"""Advance only N11 public links after the p. 3 legibility QA."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD = "n11-editorial-20261028"
NEW = "n11-referentes-legibles-20261028"
FILES = {
    "site/index.html": 8,
    "site/covers/cronicas/articles.json": 1,
    "site/course-manifest.json": 2,
}


def main() -> None:
    for relative, count in FILES.items():
        path = ROOT / relative
        current = path.read_text(encoding="utf-8")
        if current.count(OLD) != count or NEW in current:
            raise ValueError(f"Unexpected N11 revision count in {relative}")
        path.write_text(current.replace(OLD, NEW), encoding="utf-8")
        print(f"{relative}: {count} N11 references updated")


if __name__ == "__main__":
    main()
