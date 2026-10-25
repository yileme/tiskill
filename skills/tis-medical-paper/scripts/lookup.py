#!/usr/bin/env python3
"""Read-only bounded search of a separately configured private page catalog."""
import argparse
import json
from pathlib import Path


def inside(root, relative):
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("unsafe source pointer")
    current = root
    for part in path.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("symlink source pointer")
    resolved = current.resolve()
    if not resolved.is_relative_to(root):
        raise ValueError("source pointer outside root")
    return resolved


def search(root, query, limit=3):
    root = root.expanduser().resolve(strict=True)
    if not query.strip() or not 1 <= limit <= 10:
        raise ValueError("query required; limit must be 1..10")
    manifest = json.loads(inside(root, "manifest.json").read_text())
    pages = json.loads(inside(root, "page-map.json").read_text())
    results = []
    for page in pages:
        pointer = page.get("text_file")
        if not pointer:
            continue
        text = inside(root, pointer).read_text()
        at = text.casefold().find(query.casefold())
        if at < 0:
            continue
        results.append({"physical_page": page["physical_page"],
                        "printed_page": page.get("printed_page"),
                        "chapter": page.get("chapter"),
                        "batch": page["batch"], "batch_page": page["batch_page"],
                        "excerpt": text[max(0, at-120):at+380],
                        "status": "extraction_candidate",
                        "source_sha256": manifest["source_sha256"],
                        "source_edition": manifest["edition"],
                        "extraction_status": page.get("extraction_status"),
                        "qa_status": page.get("qa_status"),
                        "source_text_supplement_available": bool(page.get("source_text_supplement"))})
        if len(results) >= limit:
            break
    return {"status": "candidates" if results else "no_match", "results": results,
            "notice": "Check source PDF; extraction is not source verification."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True)
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--config", type=Path, default=Path.home()/".tiskill/medical-paper.json")
    args = parser.parse_args()
    try:
        config = json.loads(args.config.read_text())
        result = search(Path(config["sourceRoot"]), args.query, args.limit)
    except FileNotFoundError:
        result = {"status": "source_unavailable", "results": []}
    except (ValueError, KeyError, OSError) as error:
        result = {"status": "invalid_source", "error_type": type(error).__name__, "results": []}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
