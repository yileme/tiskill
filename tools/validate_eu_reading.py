#!/usr/bin/env python3
"""Validate full-page record coverage and distribution integrity, not comprehension."""
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs/source-reviews"
metadata = json.loads((BASE / "metadata.json").read_text())
expected = {"EU-GARDNER": (59, r"^## T PDF (\d+)"),
            "EU-CLEAR": (16, r"^## C PDF (\d+)"),
            "EU-DGT": (138, r"^## PDF page (\d+)"),
            "EU-ISG": (306, r"^\*\*Physical page (\d+)\.\*\*"),
            "EU-TIPS": (17, r"^## PDF page (\d+)")}
assert len(metadata["sources"]) == len(expected)
assert {s["id"] for s in metadata["sources"]} == set(expected)
package = json.loads((ROOT / "skills/tis-plain-language/references/source-metadata.json").read_text())
package = {s["id"]: s for s in package["sources"]}
total = 0
for source in metadata["sources"]:
    count, pattern = expected[source["id"]]
    pages = [int(x) for x in re.findall(pattern, (BASE / source["ledger"]).read_text(), re.M)]
    assert pages == list(range(1, count + 1)), source["id"]
    assert source["pdf_pages"] == count
    assert source["read_pdf_ranges"] == package[source["id"]]["read_pdf_ranges"] == [[1, count]]
    assert all(source[k] for k in ("title", "issuer", "date", "edition", "identity_locator", "filename"))
    assert Path(source["filename"]).name == source["filename"]
    assert re.fullmatch(r"[0-9a-f]{64}", source["sha256"])
    assert source["external_current_status_checked"] is False
    total += len(pages)
assert total == metadata["unique_physical_pages"] == sum(count for count, _ in expected.values())
manifest = json.loads((BASE / "dgt-manifest.json").read_text())
assert manifest["read_pages"] == list(range(1, 139))
assert [p["pdf_page"] for p in manifest["page_records"]] == list(range(1, 139))
assert all(p["read"] and p["note_present"] for p in manifest["page_records"])
assert all(p["printed_main_page"] == (p["pdf_page"]-6 if p["pdf_page"] >= 7 else None) for p in manifest["page_records"])
assert not manifest["missing_pages"]
assert package["NEUBAUER"]["read_pdf_ranges"] == [[1, 5], [9, 13], [53, 57]]
assert package["FEDERAL"]["read_pdf_ranges"] != [[1, 115]]
paths = [*BASE.rglob("*"), *ROOT.glob("skills/*/references/eu-guides.md")]
for path in paths:
    if not path.is_file(): continue
    assert path.suffix in (".md", ".json"), path
    text = path.read_text()
    assert not re.search(r"/Users/|/home/|Nutstore Files|file://", text), path
    assert not re.search(r"^page-\d+\.txt$", path.name), path
for path in [*ROOT.glob("skills/**/*.md"), *ROOT.glob("docs/source-reviews/*.md"), ROOT / "docs/eu-guides-acceptance.md", ROOT / "docs/changes-0.9.1.md", ROOT / "docs/changes-0.9.2.md", ROOT / "docs/clear-english-acceptance.md"]:
    text = re.sub(r"`[^`\n]*`", "", path.read_text())
    for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
        if "://" not in target and not target.startswith("#"):
            assert (path.parent / target.split("#", 1)[0]).is_file(), (path, target)
tips = next(s for s in metadata["sources"] if s["id"] == "EU-TIPS")
assert all(tips[k] == package["EU-TIPS"][k] for k in tips if k != "ledger")
assert (ROOT / "skills/tis-plain-language/references/clear-english.md").read_bytes() == (ROOT / "skills/tis-translation-practice/references/clear-english.md").read_bytes()
print(f"EU records valid: {len(expected)} documents, {total} unique pages; metadata, locators, links and public-file boundaries checked")
