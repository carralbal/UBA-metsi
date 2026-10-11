#!/usr/bin/env python3
"""Block platform-rendered emoji arrows in public METSI navigation.

Run in the Pages workflow so a future regeneration cannot restore the blue
system glyphs on iOS. The active presentation bundle is checked through its
HTML entrypoint; old hashed bundles are retained but are not loaded.
"""

from html.parser import HTMLParser
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
FORBIDDEN = ("↗", "⬈", "➡", "🔗")
ARROW_PATH = 'd="M3 13 13 3M5 3h8v8"'


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.current: dict | None = None
        self.found: list[dict] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            self.current = {"text": "", "svg": False, "href": dict(attrs).get("href")}
        elif tag == "svg" and self.current is not None:
            self.current["svg"] = True

    def handle_data(self, data: str) -> None:
        if self.current is not None:
            self.current["text"] += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self.current is not None:
            self.found.append(self.current)
            self.current = None


def check_links(source: str, label: str, expected: int) -> None:
    links = Links()
    links.feed(source)
    card_links = [link for link in links.found if link["text"].strip().startswith(
        ("Leer la crónica", "Lectura N"))]
    assert len(card_links) == expected, f"{label}: expected {expected} editorial links, got {len(card_links)}"
    assert all(link["svg"] for link in card_links), f"{label}: an editorial link lacks the vector arrow"


def main() -> None:
    pages = [
        SITE / "index.html",
        SITE / "covers/cronicas/index.html",
        SITE / "covers/recorrido/index.html",
        SITE / "covers/preview-recorrido-n00/index.html",
    ]
    sources = [
        SITE / "metsi.js",
        ROOT / "scripts/build_cronicas.py",
        ROOT / "scripts/sync_learning_route.py",
        ROOT / "pedagogy/presentations-web/N01/src/main.jsx",
    ]
    for path in pages + sources:
        content = path.read_text(encoding="utf-8")
        for character in FORBIDDEN:
            assert character not in content, f"{path}: platform emoji arrow {character!r} returned"

    home = pages[0].read_text(encoding="utf-8")
    cards = home.split("<!-- BEGIN home chronicles cards -->", 1)[1].split(
        "<!-- END home chronicles cards -->", 1)[0]
    index = pages[1].read_text(encoding="utf-8")
    check_links(cards, "homepage cards", 74)
    check_links(index, "chronicle index", 74)
    assert cards.count(ARROW_PATH) == 74, "Homepage cards lost the shared monochrome vector"
    assert index.count(ARROW_PATH) >= 75, "Chronicle index lost a card or header vector"
    assert ARROW_PATH in home and ARROW_PATH in pages[2].read_text(encoding="utf-8")
    assert ARROW_PATH in pages[3].read_text(encoding="utf-8")
    assert ARROW_PATH in (SITE / "metsi.js").read_text(encoding="utf-8")

    presentation = (SITE / "pdf/presentaciones/N01/index.html").read_text(encoding="utf-8")
    bundle_match = re.search(r'src="\./(assets/index-[^"/]+\.js)"', presentation)
    assert bundle_match, "Presentation entrypoint has no active script bundle"
    bundle = SITE / "pdf/presentaciones/N01" / bundle_match.group(1)
    assert bundle.is_file(), f"Presentation bundle missing: {bundle}"
    assert all(symbol not in bundle.read_text(encoding="utf-8") for symbol in FORBIDDEN), (
        "Active presentation bundle still contains an OS arrow"
    )
    print("Editorial icon gate: 37 homepage cards, 37 index cards, active presentation, no OS arrows")


if __name__ == "__main__":
    main()
