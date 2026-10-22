#!/usr/bin/env python3
"""Small, offline Markdown library. No CAT server dependency or network requests."""
import argparse
from contextlib import contextmanager
from datetime import date, datetime, timezone
import fcntl
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from uuid import uuid4
from urllib.parse import urlsplit

FOLDERS = {"evidence": "01-查证记录", "expression": "02-表达积累", "practice": "03-练习复盘"}
STATES = {"unverified", "text_read", "audio_checked"}


def root_from_config(config):
    value = json.loads(Path(config).expanduser().read_text())["path"]
    root = Path(value).expanduser()
    if not root.is_absolute() or not root.is_dir():
        raise ValueError("Configure an existing absolute library folder")
    return root.resolve()


def safe_folder(root, name):
    folder = root / name
    if folder.is_symlink():
        raise ValueError("Symlinked library folder refused")
    folder.mkdir(exist_ok=True)
    if folder.resolve().parent != root.resolve():
        raise ValueError("Folder escapes library")
    return folder


@contextmanager
def locked(root):
    lock = root / ".tiskill-library.lock"
    if lock.is_symlink():
        raise ValueError("Symlink lock refused")
    with lock.open("a") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        yield


def valid_url(value):
    try:
        p = urlsplit(value)
        valid = p.scheme in {"http", "https"} and p.hostname and not p.username and not p.password and p.port != 0
    except (ValueError, TypeError):
        valid = False
    if not valid or re.search(r"[\s\x00-\x1f\x7f\\]", value):
        raise ValueError("Source URL must be credential-free HTTP(S)")


def validate(data):
    if not isinstance(data, dict) or not isinstance(data.get("type"), str) or data.get("type") not in FOLDERS:
        raise ValueError("type must be evidence, expression or practice")
    required = ["title"] + (["response", "selfReview", "kind"] if data["type"] == "practice" else ["expression", "context", "explanation"])
    for key in required:
        if not isinstance(data.get(key), str) or not data[key].strip() or len(data[key]) > 20000:
            raise ValueError("Missing/invalid " + key)
    title = data["title"]
    if len(title) > 80 or re.search(r"[/\\\x00-\x1f<>:\"|?*\[\]#]", title) or title in {".", ".."}:
        raise ValueError("Unsafe title")
    state = data.get("verification", "unverified")
    if not isinstance(state, str) or state not in STATES:
        raise ValueError("Unknown verification state")
    for key in ["quotation", "url", "timestamp", "domain", "register", "query", "accessedAt", "limitations"]:
        if key in data and (not isinstance(data[key], str) or len(data[key]) > 20000):
            raise ValueError("Invalid " + key)
    if data.get("url"):
        valid_url(data["url"])
    if state != "unverified":
        if data.get("userConfirmed") is not True or not data.get("quotation") or not (data.get("url") or data.get("localSourceId")):
            raise ValueError("Checked evidence requires actual quote, URL and explicit user confirmation")
    if data.get("localSourceId") and state == "audio_checked":
        raise ValueError("Local reading sources cannot establish audio verification")
    if data.get("localSourceSnapshot") is not None:
        raise ValueError("Local snapshots are captured, not accepted from input")
    if data.get("snapshot") is not None:
        raise ValueError("Snapshots are captured from saved sourceId, not accepted from input")
    if data["type"] == "practice" and state != "unverified":
        raise ValueError("Practice is self review, not verified evidence")
    for key in ["id", "sourceId"]:
        if key in data and (not isinstance(data[key], str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", data[key])):
            raise ValueError("Unsafe " + key)
    if not isinstance(data.get("date", ""), str):
        raise ValueError("Invalid date")
    date.fromisoformat(data.get("date", date.today().isoformat()))
    return data


def payload(note):
    text = note.read_text()
    marker = "<!-- tiskill-record -->\n"
    if marker not in text:
        return None
    return json.loads(text.split(marker, 1)[1].split("```json\n", 1)[1].rsplit("\n```", 1)[0])


def records(root):
    result = {}
    for folder in FOLDERS.values():
        directory = root / folder
        if directory.is_symlink():
            raise ValueError("Symlinked folder refused")
        for p in directory.glob("*.md"):
            if p.is_symlink():
                raise ValueError("Symlinked record refused")
            item = payload(p)
            if item:
                if item["id"] in result:
                    raise ValueError("Duplicate stored ID")
                result[item["id"]] = (p, item)
    return result


def render(item, source_link=None):
    meta = {k: item.get(k) for k in ["id", "type", "date", "verification", "verificationBy", "sourceId", "createdAt", "version", "legacy"] if item.get(k) is not None}
    lines = ["---"] + [k + ": " + json.dumps(v, ensure_ascii=False) for k, v in meta.items()] + ["---", "", "# " + item["title"], "", "[[首页]]", "", "状态：" + ("待核实" if item.get("verification", "unverified") == "unverified" else "已核对（保留核对者声明，不是自动认证）"), ""]
    if source_link:
        lines += ["来源记录：[[" + source_link + "]]", ""]
    for key in ["expression", "context", "quotation", "url", "timestamp", "domain", "register", "explanation", "kind", "response", "selfReview"]:
        if item.get(key):
            lines += ["## " + key, "", str(item[key]), ""]
    # JSON retains complete original values and immutable snapshots, including unknown metadata.
    lines += ["## 完整记录与来源快照", "", "<!-- tiskill-record -->", "```json", json.dumps(item, ensure_ascii=False, indent=2), "```", ""]
    return "\n".join(lines)


def write_record(root, item, known):
    if item["id"] in known:
        raise ValueError("ID already exists; never overwrite")
    folder = safe_folder(root, FOLDERS[item["type"]])
    title = re.sub(r"[^\w -]", "_", item["title"], flags=re.UNICODE)[:80].strip() or "记录"
    stamp = date.fromisoformat(item["date"]).strftime("%Y%m%d")
    source = known.get(item.get("sourceId"))
    link = str(source[0].relative_to(root).with_suffix("")) if source else None
    content = render(item, link)
    for version in range(1, 10000):
        path = folder / f"{stamp}_{title}_V{version:02d}.md"
        try:
            with path.open("x", encoding="utf-8") as f:
                f.write(content)
            known[item["id"]] = (path, item)
            return path
        except FileExistsError:
            continue
    raise ValueError("Filename versions exhausted")


def save(root, data, confirm=False):
    if not confirm:
        raise ValueError("Saving requires --confirm after user authorization")
    data = dict(validate(data))
    with locked(root):
        known = records(root)
        if data.get("localSourceId"):
            import importlib.util
            script = Path(__file__).resolve().parents[1]/"skills/tis-reading/scripts/reading.py"
            spec = importlib.util.spec_from_file_location("tis_reading", script)
            reading = importlib.util.module_from_spec(spec); spec.loader.exec_module(reading)
            _, local = reading.get_source(root, data["localSourceId"])
            if not data.get("quotation") or data["quotation"] not in local["content"]:
                raise ValueError("Local quotation must match canonical source")
            if data.get("verification", "unverified") != "unverified" and (local["verification"] != "text_read" or local.get("ocr_unchecked")):
                raise ValueError("Local source remains unverified")
            data["localSourceSnapshot"] = local
        source = data.get("sourceId")
        if source and source not in known:
            raise ValueError("Unknown sourceId")
        if source:
            data["snapshot"] = known[source][1]
        data.setdefault("id", uuid4().hex)
        data.setdefault("date", date.today().isoformat())
        data.setdefault("verification", "unverified")
        data["verificationBy"] = "user" if data["verification"] != "unverified" else None
        data["createdAt"] = datetime.now(timezone.utc).isoformat()
        return write_record(root, data, known)


def migrate(root, database, backup_dir, confirm=False):
    if not confirm:
        raise ValueError("Migration requires --confirm")
    database = Path(database).resolve(strict=True)
    backup_dir = Path(backup_dir).resolve()
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup = backup_dir / ("evidence-" + uuid4().hex + ".sqlite3")
    # Exact 0.7.0 application schema: cards(id,version,data), attempts(id,card_id,data).
    with sqlite3.connect(database.as_uri() + "?mode=ro", uri=True) as src:
        with sqlite3.connect(backup) as dst:
            src.backup(dst)
    with sqlite3.connect(backup.as_uri() + "?mode=ro", uri=True) as db:
        cards = db.execute("SELECT id, version, data FROM cards ORDER BY rowid").fetchall()
        attempts = db.execute("SELECT id, card_id, data FROM attempts ORDER BY rowid").fetchall()
    totals = {"cards": len(cards), "attempts": len(attempts), "saved": 0, "skipped": 0, "backup": str(backup)}
    with locked(root):
        known = records(root)
        for kind, rows in [("evidence", cards), ("practice", attempts)]:
            for ident, extra, raw in rows:
                original = json.loads(raw)
                row = {"id": ident, "version" if kind == "evidence" else "card_id": extra, "data": raw}
                key = "legacy-" + kind + "-" + hashlib.sha256(ident.encode()).hexdigest()
                if key in known:
                    if known[key][1].get("legacyRow") != row:
                        raise ValueError("Legacy record changed since migration; preserve and review")
                    totals["skipped"] += 1
                    continue
                item = dict(original)
                item.update(id=key, type=kind, legacy=True, legacyId=ident, legacyRow=row,
                            title=original.get("expression") or ("练习-" + ident),
                            date=original["createdAt"][:10], verification=original.get("verification", "unverified"))
                if kind == "practice":
                    item["sourceId"] = "legacy-evidence-" + hashlib.sha256(extra.encode()).hexdigest()
                write_record(root, item, known)
                totals["saved"] += 1
    return totals


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path.home()/".tiskill/library.json")
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("save"); s.add_argument("--input", type=Path, required=True); s.add_argument("--confirm", action="store_true")
    m = sub.add_parser("migrate"); m.add_argument("--database", type=Path, required=True); m.add_argument("--backup-dir", type=Path, required=True); m.add_argument("--confirm", action="store_true")
    args = parser.parse_args()
    try:
        root = root_from_config(args.config)
        result = save(root, json.loads(args.input.read_text()), args.confirm) if args.command == "save" else migrate(root, args.database, args.backup_dir, args.confirm)
        print(json.dumps(str(result) if isinstance(result, Path) else result, ensure_ascii=False))
    except (ValueError, KeyError, OSError, sqlite3.Error) as error:
        parser.exit(2, str(error) + "\n")

if __name__ == "__main__":
    main()
