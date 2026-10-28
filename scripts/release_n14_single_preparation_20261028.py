#!/usr/bin/env python3
"""Advance only N14's public cache key after the single-assignment PDF passes QA."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD = "n14-asis-tobe-post-cecilia-20261027"
NEW = "n14-single-preparation-20261028"
FILES = {
    "site/index.html": 9,
    "site/covers/atlas-data.js": 2,
    "site/covers/cronicas/articles.json": 1,
    "site/course-manifest.json": 2,
}


def main() -> None:
    updates = {}
    for name, count in FILES.items():
        source = (ROOT / name).read_text(encoding="utf-8")
        if source.count(OLD) != count or NEW in source:
            raise ValueError(f"Unexpected N14 key count in {name}")
        updates[name] = source.replace(OLD, NEW)
    for name, revised in updates.items():
        (ROOT / name).write_text(revised, encoding="utf-8")
    print("N14 cache key advanced in exactly four public files (14 links)")


if __name__ == "__main__":
    main()
