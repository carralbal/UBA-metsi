"""Advance only the public N21 PDF revision references after QA."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OLD = "n21-verified-20261026"
NEW = "n21-referentes-neutral-20261028"
FILES = {
    "site/index.html": 9,
    "site/covers/atlas-data.js": 2,
    "site/covers/cronicas/articles.json": 1,
    "site/course-manifest.json": 2,
}


def main() -> None:
    for relative, count in FILES.items():
        path = ROOT / relative
        current = path.read_text(encoding="utf-8")
        if current.count(OLD) != count or NEW in current:
            raise ValueError(f"Unexpected N21 key count in {relative}")
        updated = current.replace(OLD, NEW)
        path.write_text(updated, encoding="utf-8")
        print(f"{relative}: {count} N21 revision references")


if __name__ == "__main__":
    main()
