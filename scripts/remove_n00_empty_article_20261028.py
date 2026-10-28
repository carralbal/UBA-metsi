"""Remove a zero-content bridge between N00 front matter and Part I."""

from pathlib import Path

file = Path(__file__).resolve().parents[1] / "N00-post-cecilia-from-current-20261027/N00/index.html"
body = file.read_text(encoding="utf-8")
needle = '<article class="reading"></article>'
if body.count(needle) != 1:
    raise SystemExit("Expected exactly one empty N00 reading wrapper; no edit made")
file.write_text(body.replace(needle, ""), encoding="utf-8")
print("Removed empty N00 article; no student-facing source ID affected")
