"""Fail-closed mechanical links/manifest update for reviewed N19 acquisition case."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PDF = "N19-METSI-lectura-previa-v10-final.pdf"
OLD = f"{PDF}?v=n19-digital-20261024"
NEW = f"{PDF}?v=n19-acquisition-post-cecilia-20261027"
EXPECTED = {
    "site/index.html": 8,
    "site/covers/cronicas/index.html": 1,
    "site/covers/cronicas/articles.json": 1,
}


def replace_exact(content: str, old: str, new: str, expected: int, name: str) -> str:
    actual = content.count(old)
    if actual != expected:
        raise ValueError(f"{name}: expected {expected} occurrences, found {actual}: {old}")
    return content.replace(old, new)


for relative, expected in EXPECTED.items():
    path = ROOT / relative
    content = path.read_text(encoding="utf-8")
    if relative == "site/index.html":
        content = replace_exact(content, f"{OLD}#page=37", f"{NEW}#page=39", 5, relative)
        content = replace_exact(content, "N19, página 37", "N19, página 39", 4, relative)
        content = replace_exact(
            content,
            f'{NEW}#page=39" target="_blank" rel="noopener">N19 · ¿Comprar, construir o no automatizar?</a><small>Referencias base · pág. 37',
            f'{NEW}#page=39" target="_blank" rel="noopener">N19 · ¿Comprar, construir o no automatizar?</a><small>Referencias base · pág. 39',
            1,
            relative,
        )
        content = replace_exact(content, "N19 · 38 páginas", "N19 · 40 páginas", 1, relative)
        expected -= 5
    content = replace_exact(content, OLD, NEW, expected, relative)
    path.write_text(content, encoding="utf-8")
    print(f"{relative}: updated")

path = ROOT / "site/course-manifest.json"
manifest = json.loads(path.read_text(encoding="utf-8"))
items = [item for item in manifest["readings"] if item.get("code") == "N19"]
if len(items) != 1 or items[0].get("pages") != 38 or items[0].get("revision") != "n19-digital-20261024":
    raise ValueError("N19 manifest baseline changed")
items[0]["pages"] = 40
items[0]["pdf"] = f"pdf/publicados/{NEW}"
items[0]["revision"] = "n19-acquisition-post-cecilia-20261027"
path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("site/course-manifest.json: N19 updated to 40 pages")
