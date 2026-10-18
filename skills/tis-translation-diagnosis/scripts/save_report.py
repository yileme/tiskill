#!/usr/bin/env python3
"""Save one prepared Markdown report and append its confirmed issues to errors.csv."""
import argparse
import csv
import io
from pathlib import Path
import re
import sys

FIELDS = "exercise_id,exercise_date,direction,brief,coverage,issue_id,category,priority,source_span,target_span,reason,evidence_type,evidence_url,revision,review_status".split(",")


def save(report, issues, destination):
    text = report.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError("report is empty")
    with issues.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != FIELDS:
            raise ValueError("issue CSV fields differ from template")
        rows = list(reader)
    match = re.search(r"\(([A-Za-z0-9_-]{3,80})\)", text.splitlines()[0])
    if not match:
        raise ValueError("report heading must include (exercise_id)")
    exercise_id = match.group(1)
    if rows and {row["exercise_id"] for row in rows} != {exercise_id}:
        raise ValueError("issue exercise_id differs from report")
    if not re.fullmatch(r"[A-Za-z0-9_-]{3,80}", exercise_id):
        raise ValueError("exercise_id must be a safe stable identifier")
    keys = [(r["exercise_id"], r["issue_id"]) for r in rows]
    if any(not r["issue_id"].strip() or r["review_status"] != "已确认" or not r["category"].strip() for r in rows) or len(set(keys)) != len(keys):
        raise ValueError("invalid, unconfirmed or duplicate issue")
    out = destination / f"{exercise_id}.md"
    ledger = destination / "errors.csv"
    if out.exists():
        raise FileExistsError(f"report exists: {out}")
    old = []
    if ledger.exists():
        with ledger.open(encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames != FIELDS:
                raise ValueError("existing errors.csv has incompatible fields")
            old = list(reader)
    if set(keys) & {(r["exercise_id"], r["issue_id"]) for r in old}:
        raise ValueError("one or more issues already recorded; no files changed")
    # Prepare complete content before touching the destination.
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(old + rows)
    destination.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    if rows:
        ledger.write_text(buffer.getvalue(), encoding="utf-8")
    print(f"saved {out} and {len(rows)} issue(s) in {ledger}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--issues", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    try:
        save(args.report, args.issues, args.destination)
    except (ValueError, OSError) as exc:
        print(exc, file=sys.stderr)
        sys.exit(2)
