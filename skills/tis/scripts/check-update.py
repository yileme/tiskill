#!/usr/bin/env python3
"""Print one update notice at most once per 24h; fail silently offline."""
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.request import urlopen

SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")


def notice(local, remote):
    if not SEMVER.fullmatch(local) or not isinstance(remote, dict):
        return ""
    version, text = remote.get("version"), remote.get("notice")
    if not isinstance(version, str) or not SEMVER.fullmatch(version):
        return ""
    if not isinstance(text, str) or not 1 <= len(text.strip()) <= 100 or any(c in text for c in "\r\n\t"):
        return ""
    if tuple(map(int, version.split("."))) <= tuple(map(int, local.split("."))):
        return ""
    return f"tiskill v{version}：{text.strip()} 回复 1，我现在帮你更新。"


def main():
    local = sys.argv[1] if len(sys.argv) == 2 else ""
    if not SEMVER.fullmatch(local):
        return
    url = os.getenv("TIS_UPDATE_URL", "")
    repo = Path(os.environ["TIS_REPO_DIR"]).expanduser() if os.getenv("TIS_REPO_DIR") else None
    if not url and repo is None:
        try:
            config = json.loads((Path.home() / ".tiskill/source.json").read_text())
            repo = Path(config["repo"]).expanduser()
        except (OSError, ValueError, TypeError, KeyError):
            return
    if not url and repo is None:
        return
    source = url or str(repo / "UPDATE.json")
    cache = Path(os.getenv("TIS_CACHE_DIR", str(Path.home() / ".tiskill"))) / "update_check.json"
    try:
        record = json.loads(cache.read_text())
        if record.get("source") == source and time.time() - record.get("checked_at", 0) < 86400:
            return
    except (OSError, ValueError, TypeError):
        pass
    try:
        if url:
            if not re.match(r"^https://", url):
                return
            with urlopen(url, timeout=5) as response:
                payload = json.loads(response.read(4096))
        else:
            payload = json.loads((repo / "UPDATE.json").read_text())
        result = notice(local, payload)
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps({"source": source, "checked_at": time.time()}))
        if result:
            print(result)
    except (OSError, ValueError, TypeError):
        pass


if __name__ == "__main__":
    main()
