#!/usr/bin/env python3
"""Bump only N02's cache key after the p. 6 semantic correction."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OLD = "n02-editorial-fix-20261026"
NEW = "n02-valija-semantic-20261028"
EXPECTED = {
    "course-manifest.json": 1,
    "site/index.html": 9,
    "site/covers/atlas-data.js": 1,
    "site/course-manifest.json": 2,
    "site/covers/cronicas/articles.json": 1,
}


def main() -> None:
    for relative, expected in EXPECTED.items():
        path = ROOT / relative
        source = path.read_text(encoding="utf-8")
        count = source.count(OLD)
        if count == 0 and source.count(NEW) == expected:
            continue
        if count != expected:
            raise ValueError(f"{relative}: expected {expected} old keys, got {count}")
        path.write_text(source.replace(OLD, NEW), encoding="utf-8")
    print("N02 cache key updated in the five exact site/manifest files")


if __name__ == "__main__":
    main()
