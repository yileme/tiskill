#!/usr/bin/env python3
"""Check release metadata, skill layout and private-path leakage."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("tis", "tis-translation-practice", "tis-translation-diagnosis", "tis-real-english", "tis-usage-evidence", "tis-plain-language", "tis-speaking-practice", "tis-update", "tis-client-service", "tis-inclusive-language", "tis-reading", "tis-public-service-english", "tis-medical-paper")
VERSION = (ROOT / "VERSION").read_text().strip()
assert re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", VERSION)
update = json.loads((ROOT / "UPDATE.json").read_text())
market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
assert update["version"] == market["metadata"]["version"] == plugin["version"] == VERSION
assert len(NAMES) == 13
assert {p.name for p in (ROOT / "skills").iterdir() if p.is_dir()} == set(NAMES)
assert 1 <= len(update["notice"]) <= 100
assert len(market["plugins"]) == 1
assert market["plugins"][0]["name"] == plugin["name"] == "tis"
assert market["plugins"][0]["source"] == "./"
assert {x.removeprefix("./skills/") for x in plugin["skills"]} == set(NAMES)
assert all(p["version"] == VERSION for p in market["plugins"])
assert f"check-update.py {VERSION}" in (ROOT / "skills/tis/SKILL.md").read_text()
voice = (ROOT / "docs/voice-and-interaction.md").read_bytes()
for name in NAMES:
    path = ROOT / "skills" / name / "SKILL.md"
    assert (path.parent / "references/voice-and-interaction.md").read_bytes() == voice, name
    text = path.read_text()
    assert "(references/voice-and-interaction.md)" in text, name
    assert text.startswith("---\n") and f"name: {name}\n" in text.split("---", 2)[1]
    assert "description:" in text.split("---", 2)[1] and "keywords:" in text.split("---", 2)[1]
for path in (ROOT / "skills").rglob("*"):
    if path.is_file():
        assert not path.name.startswith(".ekko-"), path
        if path.suffix in (".md", ".py"):
            text = path.read_text()
            assert "01_Projects/" not in text, path
            assert "Nutstore Files" not in text, path
# Local reference integrity and source locator bounds (not prose-quality tests).
plain = ROOT / "skills/tis-plain-language"
sources = json.loads((plain / "references/source-metadata.json").read_text())["sources"]
assert len({s["id"] for s in sources}) == len(sources)
source_index = (plain / "references/sources.md").read_text()
for source in sources:
    assert all(source[k] for k in ("id", "title", "issuer", "date"))
    assert source["id"] in source_index
    assert isinstance(source["pdf_pages"], int) and source["pdf_pages"] > 0
    previous = 0
    for start, end in source["read_pdf_ranges"]:
        assert previous < start <= end <= source["pdf_pages"], source["id"]
        previous = end
for path in [*plain.rglob("*.md"), ROOT / "README.md", ROOT / "docs/changes-0.9.0.md"]:
    for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text()):
        if "://" not in target and not target.startswith("#"):
            assert (path.parent / target.split("#", 1)[0]).is_file(), (path, target)
assert not list(plain.rglob("*.pdf")), "Do not bundle source PDFs"
# Inclusive-language source identity, verified locators and standalone references.
inclusive = ROOT / "skills/tis-inclusive-language"
records = json.loads((inclusive / "references/source-metadata.json").read_text())["sources"]
assert {s["id"] for s in records} == {"UN-GENDER", "APA-ILG-2023"}
for source in records:
    assert source["id"] in (inclusive / "references/sources.md").read_text()
    assert source["url"].startswith("https://")
    for check in source["visual_checks"]:
        assert 1 <= check["pdf_page"] <= source["pdf_pages"]
        assert check["printed_page"] > 0
un, apa = records
assert un["date"] is None and un["date_status"]
assert apa["date"] == "2023" and apa["pdf_pages"] == 51
assert len({c["pdf_page"] for c in apa["visual_checks"]}) == len(apa["visual_checks"])
for path in [*inclusive.rglob("*.md"), ROOT / "docs/changes-0.11.0.md"]:
    for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text()):
        if "://" not in target and not target.startswith("#"):
            assert (path.parent / target.split("#", 1)[0]).is_file(), (path, target)
for path in inclusive.rglob("*"):
    if path.is_file():
        assert path.suffix in (".md", ".json"), path
        assert "/Users/" not in path.read_text() and "MinerU/" not in path.read_text(), path
# Medical-paper distribution is authored guidance plus a standalone lookup only.
medical = ROOT / "skills/tis-medical-paper"
for path in medical.rglob("*"):
    if not path.is_file() or "__pycache__" in path.parts:
        continue
    assert path.suffix in (".md", ".py"), path
    text = path.read_text()
    assert not any(marker in text for marker in ("/Users/", "Zotero/storage/", "Nutstore Files", "sk-")), path
    if path.suffix == ".md":
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
            if "://" not in target and not target.startswith("#"):
                assert (path.parent / target.split("#", 1)[0]).is_file(), (path, target)
assert "ti-medical-paper" in (ROOT / "skills/tis/SKILL.md").read_text()
readme = (ROOT / "README.md").read_text()
assert f"[{VERSION}](VERSION)" in readme and "全部 13 项技能" in readme
assert all(f"skills/{name}/SKILL.md" in readme for name in NAMES)
# Standalone evidence references and current terminology release navigation.
for path in [*(ROOT / "skills/tis-usage-evidence").rglob("*.md"),
             ROOT / "docs/changes-0.14.1.md", ROOT / "docs/termonline-acceptance.md"]:
    text = path.read_text()
    assert "/Users/" not in text, path
    # Inline code contains citation templates, not rendered Markdown links.
    text = re.sub(r"`[^`]*`", "", text)
    for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
        if "://" not in target and not target.startswith("#"):
            assert (path.parent / target.split("#", 1)[0]).is_file(), (path, target)
print(f"tiskill v{VERSION}: metadata, structure and source boundaries valid")
