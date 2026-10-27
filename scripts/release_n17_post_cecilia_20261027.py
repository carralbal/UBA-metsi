"""Fail-closed link and manifest update for N17's reviewed additive lesson."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PDF = "N17-METSI-lectura-previa-v10-final.pdf"
OLD = f"{PDF}?v=n17-digital-20261024"
NEW = f"{PDF}?v=n17-prefact-post-cecilia-20261027"
EXPECTED = {
    "site/index.html": 11,
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
        content = replace_exact(content, f"{OLD}#page=43", f"{NEW}#page=44", 8, relative)
        content = replace_exact(content, "N17, página 43", "N17, página 44", 7, relative)
        content = replace_exact(
            content,
            f'{NEW}#page=44" target="_blank" rel="noopener">N17 · No todos los cambios se hacen igual</a><small>Referencias base · pág. 43',
            f'{NEW}#page=44" target="_blank" rel="noopener">N17 · No todos los cambios se hacen igual</a><small>Referencias base · pág. 44',
            1,
            relative,
        )
        content = replace_exact(content, "N17 · 44 páginas", "N17 · 45 páginas", 1, relative)
        expected -= 8
    content = replace_exact(content, OLD, NEW, expected, relative)
    path.write_text(content, encoding="utf-8")
    print(f"{relative}: updated")

path = ROOT / "site/course-manifest.json"
manifest = json.loads(path.read_text(encoding="utf-8"))
items = [item for item in manifest["readings"] if item.get("code") == "N17"]
if len(items) != 1 or items[0].get("pages") != 44 or items[0].get("revision") != "n17-digital-20261024":
    raise ValueError("N17 manifest baseline changed")
items[0]["pages"] = 45
items[0]["pdf"] = f"pdf/publicados/{NEW}"
items[0]["revision"] = "n17-prefact-post-cecilia-20261027"
path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("site/course-manifest.json: N17 updated to 45 pages")
