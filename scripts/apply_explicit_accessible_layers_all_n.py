#!/usr/bin/env python3
"""Hace explícitas las capas llanas y los ejemplos en cada concepto N00–N36.

La intervención no duplica ni reemplaza el desarrollo académico. Identifica la
frase de entrada y el ejemplo ya aprobados, los rotula de modo consistente y
mantiene la fuente canónica, el paquete editorial y el HTML sincronizados.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
from pathlib import Path

from audit_pedagogical_accessibility_n00_n36 import (
    CONCRETE_MARKERS,
    EXAMPLE_MARKERS,
    is_concept,
    normalize_heading,
    parse_sections,
    source_for,
    words,
)

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = {
    0: "N00-v3-final", 1: "N01-v18-final", 2: "N02-v15-final",
    3: "N03-v10-final", 4: "N04-v9-final", 5: "N05-v10-final",
    6: "N06-v10-final", 7: "N07-v10-final", 8: "N08-v10-final",
    9: "N09-v10-final", 10: "N10-v9-final",
}
PREFIX_SIMPLE = "En simple: "
PREFIX_EXAMPLE = "Ejemplo cercano: "
PREFIX_COMBINED = "En simple, con un ejemplo: "
ANY_PREFIX = (PREFIX_SIMPLE, PREFIX_EXAMPLE, PREFIX_COMBINED)
HEADING_KIND = re.compile(r"heading(?:-(\d+))?$")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package_for(number: int) -> Path:
    name = PACKAGES.get(number, f"N{number:02d}-v9-editorial")
    return ROOT / name


def manifest_and_source(folder: Path) -> tuple[Path, dict, Path]:
    manifest_path = folder / "source-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return manifest_path, manifest, folder / manifest["source"]


def heading_level(entry: dict) -> int | None:
    kind = str(entry.get("kind", ""))
    match = HEADING_KIND.fullmatch(kind)
    if match and match.group(1):
        return int(match.group(1))
    if kind == "heading":
        marks = re.match(r"^(#+)\s+", str(entry.get("text", "")))
        return len(marks.group(1)) if marks else None
    return None


def heading_text(entry: dict) -> str:
    return re.sub(r"^#+\s+", "", str(entry.get("text", ""))).strip()


def example_paragraph(text: str) -> bool:
    value = text.casefold()
    return (
        any(marker in value for marker in EXAMPLE_MARKERS)
        or any(marker in value for marker in CONCRETE_MARKERS)
        or bool(re.search(r"[«“\"]|\b\d+[\s%:.]", value))
    )


def concept_sections(code: str) -> list[dict]:
    sections = parse_sections(source_for(code).read_text(encoding="utf-8"))
    previous_h2 = ""
    error_level = 99
    result: list[dict] = []
    for section in sections:
        normalized = normalize_heading(section["title"])
        if section["level"] <= error_level and normalized != "errores frecuentes":
            error_level = 99
        if normalized == "errores frecuentes":
            error_level = section["level"]
        if section["level"] == 2:
            previous_h2 = normalized
        if section["level"] > error_level:
            continue
        if is_concept(section, previous_h2):
            result.append(section)
    return result


def updates_for(code: str, manifest: dict) -> dict[str, str]:
    entries = manifest.get("eligible_blocks", [])
    cursor = 0
    updates: dict[str, str] = {}
    for section in concept_sections(code):
        found = None
        for index in range(cursor, len(entries)):
            level = heading_level(entries[index])
            # Editorial composition may demote a canonical H2 to H3 so it fits
            # within a larger visual section.  The stable identity is the
            # normalized heading text and its order, not the rendered level.
            if level is not None and normalize_heading(heading_text(entries[index])) == normalize_heading(section["title"]):
                found = index
                break
        if found is None:
            raise RuntimeError(f"{code}: no se encontró el bloque para {section['title']!r}")
        cursor = found + 1
        paragraphs: list[dict] = []
        for entry in entries[cursor:]:
            if heading_level(entry) is not None:
                break
            if entry.get("kind") == "paragraph":
                paragraphs.append(entry)
                if len(paragraphs) == 4:
                    break
        if not paragraphs:
            raise RuntimeError(f"{code}: {section['title']!r} no tiene párrafo de entrada")
        example = next((item for item in paragraphs if example_paragraph(str(item.get("text", "")))), None)
        if example is None:
            raise RuntimeError(f"{code}: {section['title']!r} no tiene ejemplo cercano identificable")
        first_id = str(paragraphs[0]["source_id"])
        example_id = str(example["source_id"])
        if first_id == example_id:
            updates[first_id] = PREFIX_COMBINED
        else:
            updates[first_id] = PREFIX_SIMPLE
            updates[example_id] = PREFIX_EXAMPLE
    return updates


def flexible_prepend(text: str, old: str, prefix: str, label: str) -> str:
    if old.startswith(ANY_PREFIX):
        return text
    pieces = re.split(r"(\s+)", old)
    pattern = "".join(r"\s+" if piece.isspace() else re.escape(piece) for piece in pieces)
    match = re.search(pattern, text)
    if not match:
        raise RuntimeError(f"{label}: no se encontró el párrafo fuente")
    return text[:match.start()] + prefix + match.group(0) + text[match.end():]


def update_html(package: Path, updates: dict[str, str]) -> None:
    path = package / "index.html"
    source = path.read_text(encoding="utf-8")
    # Repair a partially completed earlier run before applying the idempotent
    # update. This only removes immediately repeated editorial labels.
    for marker in ANY_PREFIX:
        escaped = html.escape(marker)
        while escaped + escaped in source:
            source = source.replace(escaped + escaped, escaped)
    for source_id, prefix in updates.items():
        pattern = re.compile(rf'(<[^>]+\bdata-source-id="{re.escape(source_id)}"[^>]*>)(.*?)((?:</p>|</li>))', re.S)
        match = pattern.search(source)
        if not match:
            raise RuntimeError(f"{package.name}: no se pudo rotular {source_id}")
        body = match.group(2)
        if not any(body.startswith(html.escape(marker)) for marker in ANY_PREFIX):
            body = html.escape(prefix) + body
            source = source[:match.start(2)] + body + source[match.end(2):]
    path.write_text(source, encoding="utf-8")


def update_manifest_entries(manifest: dict, updates: dict[str, str]) -> None:
    by_id = {str(entry.get("source_id")): entry for entry in manifest.get("eligible_blocks", [])}
    for source_id, prefix in updates.items():
        entry = by_id.get(source_id)
        if entry is None:
            raise RuntimeError(f"Falta {source_id} en source-manifest")
        if not str(entry.get("text", "")).startswith(ANY_PREFIX):
            entry["text"] = prefix + str(entry.get("text", ""))
    if "eligible_block_count" in manifest:
        manifest["eligible_block_count"] = len(manifest.get("eligible_blocks", []))
    if "eligible_word_count" in manifest:
        manifest["eligible_word_count"] = sum(len(str(entry.get("text", "")).split()) for entry in manifest.get("eligible_blocks", []))


def update_source_manifest(path: Path, manifest: dict, source: Path, stage: str) -> None:
    text = source.read_text(encoding="utf-8")
    manifest["source_sha256"] = digest(source)
    manifest["stage"] = stage
    if "source_bytes" in manifest:
        manifest["source_bytes"] = source.stat().st_size
    if isinstance(manifest.get("word_counts"), dict):
        manifest["word_counts"]["total"] = len(words(text))
        start = text.find("## Tesis")
        end = text.find("## Cinco píldoras para recordar")
        if start >= 0 and end > start:
            manifest["word_counts"]["substantive_from_thesis_through_synthesis"] = len(words(text[start:end]))
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_package_records(package: Path, source: Path) -> None:
    source_words = len(words(source.read_text(encoding="utf-8")))
    for name in ("document.json", "manifest.json"):
        path = package / name
        if not path.is_file():
            continue
        record = json.loads(path.read_text(encoding="utf-8"))
        record["source_sha256"] = digest(source)
        record["source_words"] = source_words
        record["content_audit"] = "explicit-accessible-layers-all-concepts-pass"
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    report_documents = []
    total_concepts = 0
    total_labels = 0
    for number in range(37):
        code = f"N{number:02d}"
        package = package_for(number)
        package_manifest_path, package_manifest, package_source = manifest_and_source(package)
        updates = updates_for(code, package_manifest)

        authority_source = source_for(code)
        authority_manifest_path = authority_source.parent.parent / "source-manifest.json"
        authority_manifest = json.loads(authority_manifest_path.read_text(encoding="utf-8"))
        original_entries = {str(entry.get("source_id")): str(entry.get("text", "")) for entry in package_manifest.get("eligible_blocks", [])}

        source_text = authority_source.read_text(encoding="utf-8")
        for source_id, prefix in updates.items():
            source_text = flexible_prepend(source_text, original_entries[source_id], prefix, f"{code}.{source_id}")
        authority_source.write_text(source_text, encoding="utf-8")

        if package_source.resolve() != authority_source.resolve():
            shutil.copy2(authority_source, package_source)

        update_manifest_entries(package_manifest, updates)
        update_source_manifest(
            package_manifest_path,
            package_manifest,
            package_source,
            "explicit-accessible-layers-all-concepts",
        )
        if authority_manifest_path.resolve() != package_manifest_path.resolve():
            authority_manifest["source"] = str(authority_source.relative_to(authority_manifest_path.parent))
            if authority_manifest.get("eligible_blocks"):
                authority_by_text = {str(entry.get("text", "")): entry for entry in authority_manifest["eligible_blocks"]}
                for source_id, prefix in updates.items():
                    old = original_entries[source_id]
                    entry = authority_by_text.get(old)
                    if entry is not None and not str(entry.get("text", "")).startswith(ANY_PREFIX):
                        entry["text"] = prefix + str(entry.get("text", ""))
            update_source_manifest(
                authority_manifest_path,
                authority_manifest,
                authority_source,
                "explicit-accessible-layers-all-concepts",
            )

        update_html(package, updates)
        update_package_records(package, package_source)
        concepts = len(concept_sections(code))
        report_documents.append({"document": code, "concept_units": concepts, "labels": len(updates)})
        total_concepts += concepts
        total_labels += len(updates)

    report = {
        "status": "APPLIED",
        "scope": "N00-N36",
        "documents": 37,
        "concept_units": total_concepts,
        "labels_inserted": total_labels,
        "policy": "Every audited concept has an explicit plain-language entry and nearby concrete example label.",
        "per_document": report_documents,
    }
    output = ROOT / "editorial-standard" / "explicit-accessible-layers-application-n00-n36.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("status", "documents", "concept_units", "labels_inserted")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
