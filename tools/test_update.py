#!/usr/bin/env python3
"""Focused tests for version alerts and safe installed-copy synchronization."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
script = ROOT / "skills/tis/scripts/check-update.py"
spec = importlib.util.spec_from_file_location("update_check", script)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
assert module.notice("0.2.0", {"version": "0.3.0", "notice": "新功能"})
assert module.notice("0.2.0", {"version": "0.1.9", "notice": "过期"}) == ""
assert module.notice("0.2.0", {"version": "oops", "notice": "无效"}) == ""
assert module.notice("0.2.0", {"version": "0.2.0", "notice": "\nmalformed"}) == ""
with tempfile.TemporaryDirectory() as temp:
    root = Path(temp)
    fake = root / "remote.json"
    fake.write_text(json.dumps({"version": "0.3.0", "notice": "新增训练反馈"}))
    env = {**os.environ, "TIS_REPO_DIR": str(root), "TIS_CACHE_DIR": str(root / "cache")}
    first = subprocess.run([sys.executable, str(script), "0.2.0"], env=env, text=True, capture_output=True, check=True)
    assert first.stdout == "", first.stdout
    (root / "UPDATE.json").write_text(fake.read_text())
    first = subprocess.run([sys.executable, str(script), "0.2.0"], env=env, text=True, capture_output=True, check=True)
    second = subprocess.run([sys.executable, str(script), "0.2.0"], env=env, text=True, capture_output=True, check=True)
    assert "0.3.0" in first.stdout and not second.stdout
    target, state = root / "installed", root / "ledger.json"
    sync = ROOT / "tools/sync_installed.py"
    args = [sys.executable, str(sync), "--target", str(target), "--state", str(state)]
    subprocess.run(args + ["--apply"], check=True, capture_output=True)
    subprocess.run(args + ["--check"], check=True, capture_output=True)
    # The newly registered skill is installed and protected like existing skills.
    new_skill = target / "tis-inclusive-language/SKILL.md"
    assert new_skill.read_bytes() == (ROOT / "skills/tis-inclusive-language/SKILL.md").read_bytes()
    original = new_skill.read_bytes()
    new_skill.write_text(new_skill.read_text() + "\n# local inclusive preference\n")
    before = {str(p.relative_to(target)): p.read_bytes() for p in target.rglob("*") if p.is_file()}
    blocked_new = subprocess.run(args + ["--apply"], text=True, capture_output=True)
    assert blocked_new.returncode == 2 and "tis-inclusive-language/SKILL.md" in blocked_new.stdout
    assert before == {str(p.relative_to(target)): p.read_bytes() for p in target.rglob("*") if p.is_file()}
    new_skill.write_bytes(original)
    modified = target / "tis/SKILL.md"
    modified.write_text(modified.read_text() + "\n# user change\n")
    blocked = subprocess.run(args + ["--apply"], text=True, capture_output=True)
    assert blocked.returncode == 2 and "SKIP modified/unknown" in blocked.stdout
    assert modified.read_text().endswith("# user change\n")
# Retired-name migration: exercise the actual CLI with disposable installs.
for case in ("clean", "modified", "unknown", "extra", "missing", "symlink", "new-conflict"):
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        target, state = root / "installed", root / "ledger.json"
        args = [sys.executable, str(ROOT / "tools/sync_installed.py"), "--target", str(target), "--state", str(state)]
        subprocess.run(args + ["--apply"], check=True, capture_output=True)
        old, new = "tis-english-naturalness", "tis-real-english"
        (target / new).rename(target / old)
        ledger = json.loads(state.read_text())
        ledger = {k.replace(new + "/", old + "/"): v for k, v in ledger.items()}
        if case == "unknown": ledger = {k:v for k,v in ledger.items() if not k.startswith(old + "/")}
        state.write_text(json.dumps(ledger))
        skill = target / old / "SKILL.md"
        if case == "modified": skill.write_text(skill.read_text() + "user edit")
        if case == "extra": (target / old / "notes.txt").write_text("user notes")
        if case == "missing": skill.unlink()
        if case == "symlink":
            saved = root / "external.md"
            skill.rename(saved)
            skill.symlink_to(saved)
        if case == "new-conflict":
            (target / new).mkdir()
            (target / new / "SKILL.md").write_text("user skill")
        def snapshot():
            return {str(p.relative_to(root)): ("link:" + str(p.readlink()) if p.is_symlink() else p.read_bytes())
                    for p in root.rglob("*") if p.is_file() or p.is_symlink()}
        before = snapshot()
        dry = subprocess.run(args + ["--check"], text=True, capture_output=True)
        assert snapshot() == before, case
        applied = subprocess.run(args + ["--apply"], text=True, capture_output=True)
        if case == "clean":
            assert dry.returncode == applied.returncode == 0, applied.stdout
            assert "WOULD ARCHIVE" in dry.stdout
            assert not (target / old).exists() and (target / new / "SKILL.md").is_file()
            archived = list((root / "retired-skills").glob("*/" + old + "/SKILL.md"))
            assert len(archived) == 1 and archived[0].read_bytes() == before[f"installed/{old}/SKILL.md"]
            assert not any(k.startswith(old + "/") for k in json.loads(state.read_text()))
            repeat = subprocess.run(args + ["--apply"], text=True, capture_output=True, check=True)
            assert "Up to date" in repeat.stdout
            assert len(list((root / "retired-skills").iterdir())) == 1
        else:
            assert dry.returncode == applied.returncode == 2, case
            assert "SKIP modified/unknown" in applied.stdout, case
            assert snapshot() == before, case
print("update notices, modified-copy guard and 7 rename migration scenarios passed")
