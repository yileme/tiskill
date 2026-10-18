"""Archived 0.7.0 schema and fixture helpers. Never imported by the CAT server."""
from contextlib import contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sqlite3
from urllib.parse import urlsplit
from uuid import uuid4

FIELDS = {"expression": 300, "context": 3000, "quotation": 1200, "url": 2048,
          "timestamp": 40, "domain": 200, "register": 200, "explanation": 3000}
STATES = {"unverified", "text_read", "audio_checked"}
KINDS = {"recall", "translate", "transfer"}

class Conflict(ValueError):
    pass


def text(value, name, maximum, required=True):
    if not isinstance(value, str) or len(value) > maximum or (required and not value.strip()):
        raise ValueError(f"{name}: 请输入有效文本（最多 {maximum} 字）")
    return value.strip()


def card_fields(body):
    result = {key: text(body.get(key, ""), key, maximum,
                       key in {"expression", "context", "quotation", "url", "explanation"})
              for key, maximum in FIELDS.items()}
    url = result["url"]
    try:
        parsed = urlsplit(url)
        valid = (parsed.scheme in {"http", "https"} and parsed.hostname and
                 not parsed.username and not parsed.password and parsed.port != 0)
    except ValueError:
        valid = False
    if not valid or re.search(r"[\s\x00-\x1f\x7f\\]", url):
        raise ValueError("来源必须是无账号信息的 http(s) URL")
    stamp = result["timestamp"]
    if stamp and not re.fullmatch(r"(?:[0-9]+:)?[0-5]?[0-9]:[0-5][0-9]", stamp):
        raise ValueError("时间点使用 mm:ss 或 hh:mm:ss；没有实查就留空")
    state = body.get("verification", "unverified")
    if not isinstance(state, str) or state not in STATES:
        raise ValueError("未知核实状态")
    if state != "unverified" and body.get("userConfirmed") is not True:
        raise ValueError("请明确确认你已核对原文或听过音频")
    result.update(verification=state, verificationBy="user" if state != "unverified" else None)
    return result


@contextmanager
def database(directory):
    Path(directory).mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(Path(directory) / "evidence.sqlite3", timeout=10)
    try:
        db.execute("CREATE TABLE IF NOT EXISTS cards (id TEXT PRIMARY KEY, version INTEGER NOT NULL, data TEXT NOT NULL)")
        db.execute("CREATE TABLE IF NOT EXISTS attempts (id TEXT PRIMARY KEY, card_id TEXT NOT NULL, data TEXT NOT NULL)")
        db.commit()
        db.execute("BEGIN IMMEDIATE")
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def now():
    return datetime.now(timezone.utc).isoformat()


def current(db, body, key="id"):
    row = db.execute("SELECT data FROM cards WHERE id=?", (text(body.get(key), key, 64),)).fetchone()
    item = json.loads(row[0]) if row else None
    if not item or type(body.get("expectedVersion")) is not int or body["expectedVersion"] != item["version"]:
        raise Conflict("证据卡已变化或已删除；输入已保留，请重新打开并合并")
    return item


def cards(directory, query=""):
    query = text(query, "query", 1000, False).casefold()
    with database(directory) as db:
        items = [json.loads(row[0]) for row in db.execute("SELECT data FROM cards ORDER BY rowid DESC")]
    return {"items": [item for item in items if query in " ".join(str(item[k]) for k in FIELDS).casefold()]}


def save(directory, body, method):
    with database(directory) as db:
        old = current(db, body) if method != "POST" else None
        if method == "DELETE":
            db.execute("DELETE FROM cards WHERE id=?", (old["id"],))
            return {"deleted": old["id"]}
        if method == "POST" and "id" in body:
            raise ValueError("新建卡片不能指定 id")
        item = card_fields(body)
        item.update(id=old["id"] if old else uuid4().hex, version=old["version"] + 1 if old else 1,
                    createdAt=old["createdAt"] if old else now(), updatedAt=now())
        db.execute("INSERT OR REPLACE INTO cards VALUES (?, ?, ?)",
                   (item["id"], item["version"], json.dumps(item, ensure_ascii=False)))
        return {"item": item}


def attempts(directory, card_id=""):
    with database(directory) as db:
        rows = db.execute("SELECT data FROM attempts WHERE (?='' OR card_id=?) ORDER BY rowid DESC", (card_id, card_id))
        return {"items": [json.loads(row[0]) for row in rows]}


def practice(directory, body):
    kind = body.get("kind")
    if not isinstance(kind, str) or kind not in KINDS:
        raise ValueError("未知练习类型")
    response = text(body.get("response"), "response", 5000)
    review = text(body.get("selfReview"), "selfReview", 3000)
    with database(directory) as db:
        snapshot = current(db, body, "cardId")
        item = dict(id=uuid4().hex, cardId=snapshot["id"], snapshot=snapshot, kind=kind,
                    response=response, selfReview=review, createdAt=now(), assessment="self")
        db.execute("INSERT INTO attempts VALUES (?, ?, ?)", (item["id"], item["cardId"], json.dumps(item, ensure_ascii=False)))
        return {"item": item}
