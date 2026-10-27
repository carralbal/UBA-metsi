"""Correct stale accessible labels after N12/N36 bibliography pagination changes."""

from pathlib import Path


path = Path(__file__).resolve().parents[1] / "site/index.html"
text = path.read_text(encoding="utf-8")
for old, new, expected in (
    ("Bibliografía de N12, página 38", "Bibliografía de N12, página 40", 7),
    ("Bibliografía de N36, página 42", "Bibliografía de N36, página 40", 6),
):
    if text.count(old) != expected:
        raise ValueError(f"Expected {expected} instances of {old!r}, found {text.count(old)}")
    text = text.replace(old, new)
path.write_text(text, encoding="utf-8")
print("Corrected 13 stale bibliography accessibility labels")
