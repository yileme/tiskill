#!/usr/bin/env python3
"""Offline URL builder. No requests, browser opening, logging or evidence claims.
Read a public/authorized phrase from stdin so it need not enter shell history.
"""
import argparse
import json
from pathlib import Path
import sys
from urllib.parse import quote, urlencode

SOURCES = json.loads((Path(__file__).resolve().parents[1] / "references/bilingual-sources.json").read_text())
HOSTS = {"yizhiyoudao.kuaizhan.com", "reciyi.com", "linguee.com"}

def build(phrase, source="reciyi"):
    if not isinstance(phrase, str) or not phrase.strip() or len(phrase) > 500 or any(ord(c) < 32 or ord(c) == 127 for c in phrase) or '"' in phrase:
        raise ValueError("Use a nonempty phrase of at most 500 characters, without controls or double quotes")
    if source == "skell":
        return {"status": "not_requested", "source": "skell", "query": phrase,
                "language": "en", "tab": "Examples", "site": "https://skell.sketchengine.eu/",
                "skell": "https://skell.sketchengine.eu/#result?f=concordance&lang=en&query=" + quote(phrase, safe="")}
    if source not in SOURCES or SOURCES[source]["host"] not in HOSTS:
        raise ValueError("Unknown source")
    query = 'site:' + SOURCES[source]["host"] + ' "' + phrase + '"'
    encoded = urlencode({"q": query}, quote_via=quote)
    return {"status": "not_requested", "google": "https://www.google.com/search?" + encoded,
            "bing": "https://www.bing.com/search?" + encoded,
            "site": SOURCES[source]["home"],
            "linguee": "https://www.linguee.com/english-chinese/search?" + urlencode({"query": phrase}, quote_via=quote)}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=(*SOURCES, "skell"), default="reciyi")
    args = parser.parse_args()
    try:
        # A single final line ending from stdin is not part of the search phrase.
        phrase = sys.stdin.read(503).removesuffix("\n").removesuffix("\r")
        print(json.dumps(build(phrase, args.source), ensure_ascii=False, indent=2))
    except ValueError as error:
        parser.exit(2, str(error) + "\n")

if __name__ == "__main__":
    main()
