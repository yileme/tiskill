#!/usr/bin/env python3
"""Safely copy official skills to one Ekko Profile, preserving modified copies."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("tis", "tis-translation-practice", "tis-translation-diagnosis", "tis-real-english", "tis-usage-evidence", "tis-plain-language", "tis-speaking-practice", "tis-update", "tis-client-service")
RENAMED = {"tis-english-naturalness": "tis-real-english"}
DEFAULT_TARGET = Path.home() / ".hermes-web-ui/.ekko/skills/default/writing"
# Recognized pre-repository managed copies created during initial prototype.
LEGACY = {
    "tis/SKILL.md": "6d15206cff8fa2d768220940aa4acfaa5bc1461e15adca75031877287c5f2476",
    "tis-translation-diagnosis/SKILL.md": "65dcd4d0dd3adea5f198971aae82c22ef59dcb2e90b2ea4b4bebf1786f8ad743",
    "tis-translation-diagnosis/references/categories.md": "6a2bf64638d3eee157c8380a8abeb0bea39a30e1813a192e611b0984933bb15b",
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package_files(base):
    return {f"{name}/{p.relative_to(base / name).as_posix()}": p
            for name in NAMES for p in (base / name).rglob("*") if p.is_file() and not p.name.startswith(".ekko-") and "__pycache__" not in p.parts and p.suffix != ".pyc"}


def run(target, state, apply):
    source = package_files(ROOT / "skills")
    if any(not (ROOT / "skills" / name / "SKILL.md").is_file() for name in NAMES):
        raise ValueError("source package incomplete")
    try:
        ledger = json.loads(state.read_text())
    except FileNotFoundError:
        ledger = {}
    if not isinstance(ledger, dict):
        raise ValueError("invalid managed file ledger")
    # Plan the entire update first; never partially apply when any target file is modified.
    conflicts, actions = [], []
    retirements = []
    for old in RENAMED:
        directory = target / old
        if not directory.exists() and not directory.is_symlink():
            continue
        expected = {k: v for k, v in ledger.items() if k.startswith(old + "/")}
        if directory.is_symlink() or not directory.is_dir():
            conflicts.append(old + " (retired path)")
            continue
        entries = list(directory.rglob("*"))
        actual = {p.relative_to(target).as_posix(): p for p in entries if p.is_file()}
        # No ignored files here: retiring a whole directory requires full ownership.
        if (not expected or set(actual) != set(expected)
                or any(p.is_symlink() or not (p.is_file() or p.is_dir()) for p in entries)
                or any(digest(p) != expected.get(k) for k, p in actual.items())):
            conflicts.append(old + " (retired copy differs from manifest)")
            continue
        retirements.append(directory)
    for key, src in source.items():
        dst = target / key
        if dst.is_file():
            current = digest(dst)
            if current == digest(src):
                continue
            if current not in (ledger.get(key), LEGACY.get(key)):
                conflicts.append(key)
                continue
        elif dst.exists():
            conflicts.append(key)
            continue
        actions.append((key, src, dst))
    for name in NAMES:
        directory = target / name
        if directory.is_symlink() or (directory.exists() and not directory.is_dir()):
            conflicts.append(name)
            continue
        known = {k for k in source if k.startswith(name + "/")}
        if directory.exists():
            for f in directory.rglob("*"):
                if f.is_file() and f.name != ".ekko-skill.json" and "__pycache__" not in f.parts:
                    key = f.relative_to(target).as_posix()
                    if key not in known:
                        conflicts.append(key + " (extra file)")
    for key in sorted(set(conflicts)):
        print("SKIP modified/unknown:", key)
    if conflicts:
        return 2
    for key, _, _ in actions:
        print("COPY" if apply else "WOULD COPY", key)
    for directory in retirements:
        print("ARCHIVE" if apply else "WOULD ARCHIVE", directory.name)
    if apply:
        # Keep retired content outside Profile discovery and never overwrite an archive.
        for directory in retirements:
            archives = state.parent / "retired-skills"
            archives.mkdir(parents=True, exist_ok=True)
            batch = Path(tempfile.mkdtemp(prefix=directory.name + "-", dir=archives))
            shutil.move(str(directory), str(batch / directory.name))
            print("ARCHIVED TO", batch / directory.name)
        for key, src, dst in actions:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        updated = {k: digest(p) for k, p in source.items()}
        state.parent.mkdir(parents=True, exist_ok=True)
        state.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n")
        source_config = state.parent / "source.json"
        config = json.loads(source_config.read_text()) if source_config.exists() else {}
        config.setdefault("repo", str(ROOT))
        source_config.write_text(json.dumps(config, ensure_ascii=False) + "\n")
    if not actions and not retirements:
        print("Up to date")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--apply", action="store_true")
    parser.add_argument("--target", type=Path, default=Path(os.getenv("TIS_PROFILE_SKILLS", DEFAULT_TARGET)))
    parser.add_argument("--state", type=Path, default=Path(os.getenv("TIS_SYNC_STATE", Path.home() / ".tiskill/managed-files.json")))
    args = parser.parse_args()
    try:
        sys.exit(run(args.target, args.state, args.apply))
    except (ValueError, OSError) as error:
        print(error, file=sys.stderr)
        sys.exit(2)
