"""Local terminology and explicit confirmed-segment TM. Pass server.DATA as data_dir.

No server imports. Atomic CSV replacement; serialized within one server process.
CSV uses UTF-8 BOM and FIELDS headers. Mounts are stored by stable project id.
External concurrent writers must coordinate; replacements are atomic, not cross-process locks.
TM callers must supply an authoritative segment while holding server.LOCK.
"""
from datetime import datetime, timezone
from difflib import SequenceMatcher
import csv
import io
import json
import os
from pathlib import Path
import re
import tempfile
from threading import RLock
import unicodedata
from uuid import uuid4

_LOCK = RLock()
METRIC = "normalized-character-similarity"


def normalize(text):
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def _text(value, field, maximum=20000):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ValueError(f"{field} must be nonempty text (maximum {maximum} characters)")
    return value.strip()


def _locale(value, field):
    value = _text(value, field, 64)
    if not re.fullmatch(r"[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*", value):
        raise ValueError(f"{field} must be a hyphenated language tag, e.g. zh-CN or en")
    return value


def _pair(kind, sourceLocale, targetLocale):
    if kind not in ("terms", "tm"):
        raise ValueError("kind must be terms or tm")
    return _locale(sourceLocale, "sourceLocale"), _locale(targetLocale, "targetLocale")


FIELDS = ("id", "kind", "source", "target", "sourceLocale", "targetLocale",
          "createdAt", "updatedAt", "version")


class ResourceConflict(ValueError):
    """Stale edit guard; HTTP callers should map this to 409."""


def _atomic(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".resources-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def _record(item, kind):
    if not isinstance(item, dict):
        raise ValueError("Invalid resource record")
    _pair(item.get("kind"), item.get("sourceLocale"), item.get("targetLocale"))
    if item["kind"] != kind:
        raise ValueError("Resource kind differs from library kind")
    for key in ("id", "source", "target", "createdAt"):
        _text(item.get(key), key)
    item = dict(item)
    item.setdefault("updatedAt", item["createdAt"])
    item.setdefault("version", 1)
    _text(item["updatedAt"], "updatedAt")
    if type(item["version"]) is not int or item["version"] < 1:
        raise ValueError("Invalid resource version")
    if set(item) - set(FIELDS):
        raise ValueError("Unknown resource fields; refusing to discard data")
    return item


def _csv_bytes(items):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(items)
    return stream.getvalue().encode("utf-8-sig")


def _parse_csv(content, kind, *, importing=False):
    if isinstance(content, bytes):
        content = content.decode("utf-8-sig")
    if not isinstance(content, str):
        raise ValueError("csvContent must be UTF-8 CSV text or bytes")
    try:
        reader = csv.DictReader(io.StringIO(content.lstrip("\ufeff"), newline=""), strict=True)
        headers = reader.fieldnames
        required = {"source", "target", "sourceLocale", "targetLocale"} if importing else set(FIELDS) - {"updatedAt", "version"}
        if (not headers or len(set(headers)) != len(headers) or not required <= set(headers)
                or set(headers) - set(FIELDS)):
            raise ValueError("Invalid CSV headers; existing file was not changed")
        items, ids = [], set()
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                raise ValueError("Invalid CSV row width")
            if importing:
                now = datetime.now(timezone.utc).isoformat()
                for key, value in (("id", uuid4().hex), ("kind", kind), ("createdAt", now)):
                    row.setdefault(key, value)
            if "version" in row:
                if not re.fullmatch(r"[1-9][0-9]*", row["version"]):
                    raise ValueError("Invalid CSV version")
                row["version"] = int(row["version"])
            item = _record(row, kind)
            if item["id"] in ids:
                raise ValueError("Duplicate resource id")
            ids.add(item["id"])
            items.append(item)
        return items
    except (csv.Error, UnicodeError) as error:
        raise ValueError("Malformed CSV; existing file was not changed") from error


def _read_csv(path, kind):
    if not path.exists():
        return []
    try:
        return _parse_csv(path.read_bytes(), kind)
    except UnicodeError as error:
        raise ValueError("CSV must use UTF-8") from error


def _migrate(data_dir):
    directory = Path(data_dir)
    legacy, marker = directory / "resources.json", directory / ".resources-migrated"
    if not legacy.exists() or marker.exists():
        return
    data = json.loads(legacy.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != 1 or not isinstance(data.get("items"), list):
        raise ValueError("Invalid resources.json format; existing file was not changed")
    old = [_record(item, item.get("kind")) if isinstance(item, dict) else _record(item, None)
           for item in data["items"]]
    pending = []
    for kind in ("terms", "tm"):
        path = directory / (kind + ".csv")
        rows = _read_csv(path, kind)
        by_id = {row["id"]: row for row in rows}
        for item in old:
            if item["kind"] != kind:
                continue
            if item["id"] in by_id:
                if item != by_id[item["id"]]:
                    raise ValueError("Migration id conflict; existing files were not changed")
            else:
                rows.append(item)
                by_id[item["id"]] = item
        pending.append((path, rows))
    # Validate both before writing; retry after interruption is idempotent.
    for path, rows in pending:
        _atomic(path, _csv_bytes(rows))
    _atomic(marker, b"1\n")


def _project_id(project):
    if project is None:
        return "local"
    return _text(project.get("id") if isinstance(project, dict) else project, "project id", 200)


def _catalog(data_dir):
    path = Path(data_dir) / "libraries.json"
    if not path.exists():
        return {"version": 1, "libraries": [], "mounts": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    if (not isinstance(data, dict) or data.get("version") != 1
            or not isinstance(data.get("libraries"), list) or not isinstance(data.get("mounts"), dict)):
        raise ValueError("Invalid library catalog")
    ids = {"terms", "tm"}
    for library in data["libraries"]:
        if (not isinstance(library, dict) or not re.fullmatch(r"[a-f0-9]{32}", str(library.get("id", "")))
                or library["id"] in ids or library.get("kind") not in ("terms", "tm")):
            raise ValueError("Invalid library metadata")
        _text(library.get("name"), "name", 120)
        ids.add(library["id"])
    for ident, mounts in data["mounts"].items():
        _text(ident, "project id", 200)
        if not isinstance(mounts, list) or any(not isinstance(x, str) or x not in ids for x in mounts):
            raise ValueError("Invalid project mounts")
    return data


def _libraries(catalog):
    return [{"id": kind, "name": kind, "kind": kind} for kind in ("terms", "tm")] + catalog["libraries"]


def _mounted(catalog, project):
    return catalog["mounts"].get(_project_id(project), ["terms", "tm"])


def _path(data_dir, library):
    # Only validated catalog identifiers ever become filesystem paths.
    root = Path(data_dir)
    return root / (library["id"] + ".csv") if library["id"] in ("terms", "tm") else root / "libraries" / (library["id"] + ".csv")


def _select(data_dir, catalog, library_id, project):
    library = next((x for x in _libraries(catalog) if x["id"] == library_id), None)
    if library is None or library_id not in _mounted(catalog, project):
        raise ValueError("Library is not mounted for this project")
    return library, _path(data_dir, library)


def _read(data_dir, project=None):
    _migrate(data_dir)
    catalog = _catalog(data_dir)
    return {"items": [{**item, "libraryId": library["id"]}
                      for library in _libraries(catalog) if library["id"] in _mounted(catalog, project)
                      for item in _read_csv(_path(data_dir, library), library["kind"])]}


def list_libraries(data_dir, project=None):
    """Return {items: [{id,name,kind,mounted,count}], projectId}. All libraries listed."""
    with _LOCK:
        _migrate(data_dir)
        catalog = _catalog(data_dir)
        mounts = _mounted(catalog, project)
        return {"projectId": _project_id(project), "items": [
            {**lib, "mounted": lib["id"] in mounts,
             "count": len(_read_csv(_path(data_dir, lib), lib["kind"]))} for lib in _libraries(catalog)]}


def mount_library(data_dir, payload, project=None):
    """Import {name,kind,csvContent}, or toggle {libraryId,mounted:bool}.

    Imports accept CSV text/bytes, never paths. Minimal import headers are
    source,target,sourceLocale,targetLocale; FIELDS exports also round-trip.
    Returns {library: {id,name,kind,mounted,count}, projectId}.
    None project means legacy 'local'; otherwise use stable id string or {id}.
    """
    if not isinstance(payload, dict):
        raise ValueError("Library must be an object")
    if any(key in payload for key in ("path", "filePath", "csvPath")):
        raise ValueError("Import CSV content, not filesystem paths")
    ident = _project_id(project)
    mounted = payload.get("mounted", True)
    if type(mounted) is not bool:
        raise ValueError("mounted must be boolean")
    with _LOCK:
        _migrate(data_dir)
        catalog = _catalog(data_dir)
        if "csvContent" in payload:
            if "libraryId" in payload:
                raise ValueError("Import creates a new library; omit libraryId")
            name = _text(payload.get("name"), "name", 120)
            kind = payload.get("kind")
            if kind not in ("terms", "tm"):
                raise ValueError("kind must be terms or tm")
            rows = _parse_csv(payload["csvContent"], kind, importing=True)
            library = {"id": uuid4().hex, "name": name, "kind": kind}
            _atomic(_path(data_dir, library), _csv_bytes(rows))
            catalog["libraries"].append(library)
        else:
            library = next((x for x in _libraries(catalog) if x["id"] == payload.get("libraryId")), None)
            if library is None:
                raise ValueError("Unknown libraryId")
            rows = _read_csv(_path(data_dir, library), library["kind"])
        mounts = list(_mounted(catalog, project))
        if mounted and library["id"] not in mounts:
            mounts.append(library["id"])
        elif not mounted:
            mounts = [x for x in mounts if x != library["id"]]
        catalog["mounts"][ident] = mounts
        _atomic(Path(data_dir) / "libraries.json", json.dumps(catalog, ensure_ascii=False, indent=2).encode("utf-8"))
        return {"library": {**library, "mounted": mounted, "count": len(rows)}, "projectId": ident}


def export_library(data_dir, library_id, project=None):
    """Return validated UTF-8 BOM CSV bytes for a mounted library (text/csv)."""
    with _LOCK:
        _migrate(data_dir)
        lib, path = _select(data_dir, _catalog(data_dir), library_id, project)
        return _csv_bytes(_read_csv(path, lib["kind"]))


def update_resource(data_dir, payload, project=None):
    """Edit terms by id; optional libraryId disambiguates ids across libraries.

    Editable fields: source,target,sourceLocale,targetLocale. Require at least
    one guard: expectedVersion (int), expectedUpdatedAt, or expectedTarget.
    Every supplied guard must match. expectedTarget also detects manual CSV
    target edits that do not bump version/time. Returns {item}; stale guards
    raise ResourceConflict(ValueError). Pair fields are not selection filters.
    """
    if not isinstance(payload, dict):
        raise ValueError("Resource must be an object")
    ident = _text(payload.get("id"), "id")
    guards = {"expectedVersion": "version", "expectedUpdatedAt": "updatedAt", "expectedTarget": "target"}
    if not any(key in payload for key in guards):
        raise ValueError("An edit guard is required")
    with _LOCK:
        matches = [item for item in _read(data_dir, project)["items"]
                   if item["id"] == ident and ("libraryId" not in payload or item["libraryId"] == payload["libraryId"])]
        if len(matches) != 1 or matches[0]["kind"] != "terms":
            raise ValueError("Term not found or ambiguous; specify libraryId")
        current = matches[0]
        for key, field in guards.items():
            if key in payload and (payload[key] != current[field] or (key == "expectedVersion" and type(payload[key]) is not int)):
                raise ResourceConflict("Resource changed; reload before editing")
        item = {key: current[key] for key in FIELDS}
        for key in ("source", "target", "sourceLocale", "targetLocale"):
            if key in payload:
                item[key] = _locale(payload[key], key) if key.endswith("Locale") else _text(payload[key], key, 10000 if key == "source" else 20000)
        item["version"] += 1
        item["updatedAt"] = datetime.now(timezone.utc).isoformat()
        lib, path = _select(data_dir, _catalog(data_dir), current["libraryId"], project)
        rows = _read_csv(path, lib["kind"])
        _atomic(path, _csv_bytes([item if row["id"] == ident else row for row in rows]))
        return {"item": {**item, "libraryId": lib["id"]}}


def add_resource(data_dir, payload, *, segment=None, project=None):
    """Return {item, created}; exact bilingual duplicates are idempotent.

    TM requires segmentId/expectedVersion and matching source/target, plus the
    authoritative confirmed segment. Client status is never trusted.
    Validation raises ValueError; filesystem failures propagate as OSError.
    """
    if not isinstance(payload, dict):
        raise ValueError("Resource must be an object")
    kind = payload.get("kind")
    src_locale, tgt_locale = _pair(kind, payload.get("sourceLocale"), payload.get("targetLocale"))
    source = _text(payload.get("source"), "source", 10000)
    target = _text(payload.get("target"), "target")
    if kind == "tm":
        if not isinstance(segment, dict) or segment.get("status") != "confirmed":
            raise ValueError("TM saves require a current confirmed segment")
        if (not isinstance(payload.get("segmentId"), str) or payload["segmentId"] != segment.get("id")
                or type(payload.get("expectedVersion")) is not int
                or payload["expectedVersion"] != segment.get("version")
                or payload.get("source") != segment.get("source")
                or payload.get("target") != segment.get("target")):
            raise ValueError("Segment changed; reload the confirmed segment before saving to TM")
    with _LOCK:
        _migrate(data_dir)
        library_id = payload.get("libraryId", kind)
        library, path = _select(data_dir, _catalog(data_dir), library_id, project)
        if library["kind"] != kind:
            raise ValueError("Resource kind differs from library kind")
        rows = _read_csv(path, kind)
        for item in rows:
            if (item["sourceLocale"].lower() == src_locale.lower()
                    and item["targetLocale"].lower() == tgt_locale.lower()
                    and item["source"] == source and item["target"] == target):
                return {"item": {**item, "libraryId": library_id}, "created": False}
        now = datetime.now(timezone.utc).isoformat()
        item = {"id": uuid4().hex, "kind": kind, "source": source, "target": target,
                "sourceLocale": src_locale, "targetLocale": tgt_locale,
                "createdAt": now, "updatedAt": now, "version": 1}
        rows.append(item)
        _atomic(path, _csv_bytes(rows))
        return {"item": {**item, "libraryId": library_id}, "created": True}


def search_resources(data_dir, *, kind, sourceLocale, targetLocale, query="", limit=50, project=None):
    """Return {items, total, metric}; restrict to the requested language direction.

    Terms match source/target substrings or source term within query. TM ranks
    exact normalized sources then character similarity >= 0.5. Empty queries
    list stored entries, with no invented match score. Limit is 1..100.
    """
    src_locale, tgt_locale = _pair(kind, sourceLocale, targetLocale)
    if not isinstance(query, str) or len(query) > 20000:
        raise ValueError("query must be text of at most 20000 characters")
    if type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError("limit must be an integer from 1 to 100")
    needle = normalize(query)
    with _LOCK:
        data = _read(data_dir, project)
    hits = []
    for item in data["items"]:
        if (item["kind"] != kind or item["sourceLocale"].lower() != src_locale.lower()
                or item["targetLocale"].lower() != tgt_locale.lower()):
            continue
        source = normalize(item["source"])
        match, similarity = "stored", None
        if needle:
            if source == needle:
                match, similarity = "exact", 1.0
            elif kind == "terms":
                if needle not in source and source not in needle and needle not in normalize(item["target"]):
                    continue
                match = "substring"
            else:
                similarity = (SequenceMatcher(None, source, needle, autojunk=False).ratio()
                              + SequenceMatcher(None, needle, source, autojunk=False).ratio()) / 2
                if similarity < 0.5:
                    continue
                match = "fuzzy"
        hits.append({**item, "match": match, "similarity": similarity})
    hits.sort(key=lambda item: (-(item["similarity"] or 0), item["source"], item["id"]))
    return {"items": hits[:limit], "total": len(hits), "metric": METRIC if kind == "tm" else None}
