"""Fail-closed mechanical link update for the N12 post-Cecilia PDF release."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OLD_REV = "n12-digital-20261024"
NEW_REV = "n12-post-cecilia-20261027"
PDF_NAME = "N12-METSI-lectura-previa-v10-final.pdf"

EXPECTED = {
    "site/index.html": 11,
    "site/covers/cronicas/index.html": 1,
    "site/covers/cronicas/articles.json": 1,
}

for relative, expected in EXPECTED.items():
    path = ROOT / relative
    content = path.read_text(encoding="utf-8")
    old_link = f"{PDF_NAME}?v={OLD_REV}"
    new_link = f"{PDF_NAME}?v={NEW_REV}"
    found = content.count(old_link)
    if found != expected:
        raise SystemExit(f"{relative}: expected {expected} old links, found {found}")
    if relative == "site/index.html":
        old_page = f"{old_link}#page=38"
        if content.count(old_page) != 8:
            raise SystemExit("site/index.html: expected eight N12 reference links to page 38")
        if content.count("N12 · 39 páginas") != 1:
            raise SystemExit("site/index.html: expected one N12 39-page card")
        content = content.replace(old_page, f"{new_link}#page=40")
        content = content.replace("N12 · 39 páginas", "N12 · 41 páginas")
    content = content.replace(old_link, new_link)
    path.write_text(content, encoding="utf-8")
    print(f"{relative}: updated {found} N12 links")
