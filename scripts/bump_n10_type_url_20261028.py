"""Bump exactly the N10 PDF cache key in the four public site references."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OLD = "n10-post-cecilia-20261027"
NEW = "n10-type-20261028"
EXPECTED = {
    "site/index.html": 7,
    "site/covers/cronicas/articles.json": 1,
    "site/covers/cronicas/index.html": 1,
    "site/course-manifest.json": 2,
}


def main() -> None:
    for relative, expected in EXPECTED.items():
        path = ROOT / relative
        value = path.read_text(encoding="utf-8")
        if value.count(OLD) != expected or NEW in value:
            raise ValueError(f"Unexpected N10 link state: {relative}")
    for relative in EXPECTED:
        path = ROOT / relative
        value = path.read_text(encoding="utf-8")
        path.write_text(value.replace(OLD, NEW), encoding="utf-8")
    print({"files": len(EXPECTED), "replacements": sum(EXPECTED.values()), "cache_key": NEW})


if __name__ == "__main__":
    main()
