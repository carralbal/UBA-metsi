#!/usr/bin/env python3
"""Sincroniza hashes y bloques trazables después de una edición canónica autorizada."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from validate_block_c_content import blocks_for, words


ROOT = Path(__file__).resolve().parent


def simple_blocks(text: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for index, raw in enumerate(re.split(r"\n\s*\n", text.strip()), 1):
        kind = "heading" if raw.startswith("#") else "list-item" if re.match(r"^(?:\d+\.|- )", raw) else "paragraph"
        entries.append({"source_id": f"src-{index:04d}", "kind": kind, "text": raw})
    return entries


def refresh(number: int) -> dict[str, object]:
    code = f"N{number:02d}"
    package = ROOT / f"{code}-content-canonical"
    sources = sorted((package / "source").glob("*.md"))
    if len(sources) != 1:
        raise RuntimeError(f"{code}: se esperaba una fuente y se encontraron {len(sources)}")
    source = sources[0]
    text = source.read_text(encoding="utf-8")
    digest = hashlib.sha256(text.encode()).hexdigest()
    manifest_path = package / "source-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    current_entries = manifest.get("eligible_blocks") or []
    simple_schema = bool(current_entries and str(current_entries[0].get("source_id", "")).startswith("src-"))
    entries = simple_blocks(text) if simple_schema else blocks_for(code, text)
    manifest.update({
        "document": code,
        "stage": "content-canonical-v1",
        "source": f"source/{source.name}",
        "source_sha256": digest,
        "eligible_blocks": entries,
        "block_count": len(entries),
        "word_count": len(words(text)),
    })
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    integrity_path = package / "provenance" / "integrity-report.json"
    if integrity_path.exists():
        integrity = json.loads(integrity_path.read_text(encoding="utf-8"))
        references = len(re.findall(r"^- ", text.split("## Referencias base", 1)[1], re.MULTILINE)) if "## Referencias base" in text else 0
        substantive = text[text.find("## Tesis") : text.find("## Cinco píldoras para recordar")]
        integrity.update({
            "document": code,
            "word_count": len(words(text)),
            "block_count": len(entries),
        })
        if "sha256" in integrity:
            integrity.update({
                "sha256": digest,
                "bytes": source.stat().st_size,
                "words_total": len(words(text)),
                "words_substantive": len(words(substantive)),
                "source_blocks": len(entries),
                "references": references,
                "urls": len(re.findall(r"https://[^\s)]+", text.split("## Referencias base", 1)[-1])),
            })
        checks = integrity.setdefault("checks", {})
        checks["source_sha256"] = digest
        checks["references"] = references
        integrity_path.write_text(json.dumps(integrity, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"document": code, "sha256": digest, "blocks": len(entries), "words": len(words(text))}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=11)
    parser.add_argument("--end", type=int, default=36)
    args = parser.parse_args()
    print(json.dumps([refresh(number) for number in range(args.start, args.end + 1)], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
