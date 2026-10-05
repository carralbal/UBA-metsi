"""Publish the program page through the already-deployed covers/ tree.

The editable source is site/programa.html. The Pages workflow copies
site/covers/ recursively, so its generated program/index.html is public.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "site/programa.html"
TARGET = ROOT / "site/covers/programa/index.html"


def replace_once(document: str, old: str, new: str) -> str:
    count = document.count(old)
    if count != 1:
        raise ValueError(f"Expected one occurrence of {old!r}, found {count}")
    return document.replace(old, new, 1)


def build() -> None:
    document = SOURCE.read_text(encoding="utf-8")
    document = replace_once(
        document,
        'content="https://carralbal.github.io/UBA-metsi/programa.html"',
        'content="https://carralbal.github.io/UBA-metsi/covers/programa/"',
    )
    document = document.replace('href="index.html', 'href="../../index.html')
    document = document.replace('href="covers/programa/programa-metsi-2026.pdf"', 'href="programa-metsi-2026.pdf"')
    document = replace_once(document, 'href="favicon.svg"', 'href="../../favicon.svg"')
    document = replace_once(document, 'href="metsi.css', 'href="../../metsi.css')
    document = replace_once(document, 'src="metsi.js"', 'src="../../metsi.js"')
    document = document.replace(
        '<!doctype html>',
        '<!doctype html>\n<!-- Generated from site/programa.html by scripts/build_program_public_page.py. -->',
        1,
    )
    TARGET.write_text(document, encoding="utf-8")
    print(TARGET.relative_to(ROOT))


if __name__ == "__main__":
    build()
