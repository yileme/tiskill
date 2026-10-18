#!/usr/bin/env python3
"""Verify report saving, cumulative counts and duplicate protection."""
import csv
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/tis-translation-diagnosis/scripts/save_report.py"
HEADER = (ROOT / "skills/tis-translation-diagnosis/templates/errors.csv").read_text()
FIELDS = HEADER.strip().split(",")


def issue(exercise_id, issue_id, category):
    values = [exercise_id, "2026-10-17", "zh-en", "news", "all", issue_id, category, "关键", "120户", "12 households", "数量不同", "原文对照", "", "120 households", "已确认"]
    return dict(zip(FIELDS, values))


with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    out = root / "reports"
    out.mkdir()
    report = root / "report.md"
    issues = root / "issues.csv"
    def run():
        return subprocess.run([sys.executable, str(SCRIPT), "--report", str(report), "--issues", str(issues), "--destination", str(out)], capture_output=True, text=True)
    def input_for(exercise_id, rows):
        report.write_text(f"# 笔译诊断｜测试 ({exercise_id})\n\n讲解\n")
        with issues.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS); writer.writeheader(); writer.writerows(rows)
    input_for("day01", [issue("day01", "01", "F"), issue("day01", "02", "O")])
    assert run().returncode == 0
    assert run().returncode == 2
    assert (out / "day01.md").exists()
    input_for("day02", [issue("day02", "01", "F")])
    assert run().returncode == 0
    with (out / "errors.csv").open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 3 and [x["category"] for x in rows].count("F") == 2
    input_for("day03", [])
    assert run().returncode == 0 and (out / "day03.md").exists()
    assert len(list(csv.DictReader((out / "errors.csv").open(newline="")))) == 3
    input_for("day04", [issue("day04", "01", "F")])
    assert run().returncode == 0
    before = (out / "errors.csv").read_text()
    (out / "day04.md").unlink()  # simulate a repeated issue even if report was moved
    assert run().returncode == 2 and (out / "errors.csv").read_text() == before
    input_for("day05", [issue("day05", "01", "F")])
    (out / "errors.csv").write_text("different schema\n")
    assert run().returncode == 2 and not (out / "day05.md").exists()
print("diagnosis reports, zero-error case and duplicate protection passed")
