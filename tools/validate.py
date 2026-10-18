#!/usr/bin/env python3
"""Check release metadata, skill layout and private-path leakage."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("tis", "tis-translation-practice", "tis-translation-diagnosis", "tis-real-english", "tis-usage-evidence", "tis-plain-language", "tis-speaking-practice", "tis-update", "tis-client-service")
VERSION = (ROOT / "VERSION").read_text().strip()
assert re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", VERSION)
update = json.loads((ROOT / "UPDATE.json").read_text())
market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
assert update["version"] == market["metadata"]["version"] == VERSION
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
print(f"tiskill v{VERSION}: metadata, structure and source boundaries valid")
