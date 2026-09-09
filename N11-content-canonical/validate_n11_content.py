#!/usr/bin/env python3
"""Auditoría reproducible del contenido canónico de METSI N11."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = Path(__file__).resolve().parent
SOURCE = PACKAGE / "source" / "N11_cuando_un_dato_sostiene_una_afirmacion-content-canonical-v1.md"
REPORT = PACKAGE / "provenance" / "integrity-report.json"
SOURCE_MANIFEST = PACKAGE / "source-manifest.json"

PREDECESSORS = {
    f"N{number:02d}": ROOT / f"N{number:02d}-content-final" / "source" / filename
    for number, filename in {
        1: "N01_metodologia_sin_recetas-content-final.md",
        2: "N02_el_sistema_no_cabe_en_una_aplicacion-content-final.md",
        3: "N03_fronteras_retroalimentacion_y_efectos-content-final.md",
        4: "N04_hechos_sintomas_relatos_hipotesis_y_decisiones-content-final.md",
        5: "N05_actores_afectados_poder_y_perspectivas-content-final.md",
        6: "N06_discovery_como_reduccion_de_incertidumbre-content-final.md",
        7: "N07_entrevistar_no_es_pedir_requisitos-content-final.md",
        8: "N08_observar_el_trabajo_invisible-content-final.md",
        9: "N09_experiencia_accesibilidad_y_adopcion-content-final.md",
        10: "N10_construir_el_problema_y_outcomes-content-final.md",
    }.items()
}


def tokens(text: str) -> list[str]:
    return re.findall(r"[a-záéíóúüñ0-9]+", unicodedata.normalize("NFC", text.lower()))


def words(text: str) -> list[str]:
    return re.findall(r"\b[\wÁÉÍÓÚÜÑáéíóúüñ]+(?:[-‑][\wÁÉÍÓÚÜÑáéíóúüñ]+)*\b", text)


def check(name: str, passed: bool, evidence: object) -> dict[str, object]:
    return {"check": name, "result": "pass" if passed else "fail", "evidence": evidence}


def split_blocks(text: str) -> list[dict[str, object]]:
    lines = text.splitlines()
    blocks: list[dict[str, object]] = []
    buffer: list[str] = []
    start = 0

    def flush(end: int) -> None:
        nonlocal buffer, start
        if not buffer:
            return
        content = "\n".join(buffer).strip()
        if content:
            kind = "list_item" if re.match(r"^(?:[-*]|\d+\.)\s", content) else "paragraph"
            blocks.append({"kind": kind, "line_start": start, "line_end": end, "text": content})
        buffer = []

    for line_number, line in enumerate(lines, 1):
        if re.match(r"^#{1,6}\s", line):
            flush(line_number - 1)
            blocks.append({"kind": "heading", "line_start": line_number, "line_end": line_number, "text": line.strip()})
        elif not line.strip():
            flush(line_number - 1)
        elif re.match(r"^(?:[-*]|\d+\.)\s", line) and buffer:
            flush(line_number - 1)
            start = line_number
            buffer = [line]
        else:
            if not buffer:
                start = line_number
            buffer.append(line)
    flush(len(lines))
    for index, block in enumerate(blocks, 1):
        block["source_id"] = f"N11-S{index:03d}"
        block["sha256"] = hashlib.sha256(str(block["text"]).encode()).hexdigest()
        block["words"] = len(words(str(block["text"])))
    return blocks


def main() -> int:
    text = SOURCE.read_text(encoding="utf-8")
    source_hash = hashlib.sha256(text.encode()).hexdigest()
    substantive = text[text.index("## El noventa") : text.index("## Cinco píldoras para recordar")]
    references = text.split("## Referencias base", 1)[1]
    body_without_references = text.split("## Referencias base", 1)[0]
    blocks = split_blocks(text)

    n11_tokens = tokens(body_without_references)
    n11_ngrams = {tuple(n11_tokens[i : i + 24]) for i in range(max(0, len(n11_tokens) - 23))}
    repeated: list[dict[str, object]] = []
    for code, path in PREDECESSORS.items():
        predecessor_body = path.read_text(encoding="utf-8").split("## Referencias base", 1)[0]
        predecessor_tokens = tokens(predecessor_body)
        seen = set()
        for index in range(max(0, len(predecessor_tokens) - 23)):
            gram = tuple(predecessor_tokens[index : index + 24])
            if gram in n11_ngrams and gram not in seen:
                repeated.append({"document": code, "text": " ".join(gram)})
                seen.add(gram)

    section_titles = re.findall(r"^## (.+)$", text, flags=re.MULTILINE)
    subsection_lengths = []
    conceptual_core = substantive.split("## Errores frecuentes", 1)[0]
    for chunk in re.split(r"(?m)^### ", conceptual_core)[1:]:
        title, _, content = chunk.partition("\n")
        subsection_lengths.append({"title": title, "words": len(words(content))})

    pills = re.findall(r"^[1-5]\. ", text[text.index("## Cinco píldoras") : text.index("## Glosario")], flags=re.MULTILINE)
    questions = re.findall(r"^[1-6]\. ", text[text.index("## Preguntas de preparación") : text.index("## Referentes")], flags=re.MULTILINE)
    referents = re.findall(r"^\*\*[^*]+\.\*\*", text[text.index("## Referentes") : text.index("## Referencias base")], flags=re.MULTILINE)
    reference_entries = re.findall(r"^- ", references, flags=re.MULTILINE)
    recent_references = re.findall(r"\(202[4-6]\)", references)
    urls = re.findall(r"https://[^\s)]+", references)

    prohibited_register = re.findall(r"\b(?:tú|vos|usted|seleccioná|elegí|hacé|podés|deberías)\b", text, flags=re.IGNORECASE)
    editorial_placeholders = re.findall(r"\b(?:TBD|lorem|XXX)\b|\[[^\]]+\]", text, flags=re.IGNORECASE)
    prose_without_refs = body_without_references
    stray_dashes = re.findall(r"[—–]", prose_without_refs)
    required_terms = [
        "HH-11", "N04", "N10", "N12", "unidad de análisis", "operacionalización",
        "procedencia", "sesgo de selección", "incertidumbre", "explicaciones rivales",
        "suficiencia", "inteligencia artificial", "Hotel Horizonte",
    ]
    reference_anchors = {
        "Wang and Strong": "Wang y Strong",
        "ISO IEC 25012": "ISO/IEC 25012",
        "ISO IEC 5259": "ISO/IEC 5259",
        "W3C PROV": "W3C Provenance Working Group",
        "Moreau and Missier": "Luc Moreau y Paolo Missier",
        "Groves and Lyberg": "Robert Groves, Lars Lyberg",
        "National Academies 2019": "Academias Nacionales de Estados Unidos de 2019",
        "NIST SP 800-55v1": "NIST SP 800-55 Volumen 1",
        "NIST RDaF 2.0": "NIST RDaF 2.0",
        "NIST AI 600-1": "perfil de inteligencia artificial generativa de NIST publicado en 2024",
        "EU AI Act": "Reglamento de Inteligencia Artificial de la Unión Europea",
        "Nissenbaum": "Helen Nissenbaum",
        "ONeil": "Cathy O’Neil",
    }
    results = [
        check("source_exists", SOURCE.is_file(), str(SOURCE.relative_to(ROOT))),
        check("substantive_word_floor", len(words(substantive)) >= 6000, len(words(substantive))),
        check("total_word_count", len(words(text)) >= 7800, len(words(text))),
        check("required_architecture", all(title in section_titles for title in (
            "Pregunta profesional", "Tesis", "Errores frecuentes", "Consecuencias profesionales",
            "Límites y tensiones", "Síntesis", "Cinco píldoras para recordar",
            "Glosario esencial", "Preguntas de preparación", "Referentes", "Referencias base",
        )), section_titles),
        check("three_movements", sum(title.startswith("Movimiento ") for title in section_titles) == 3, [title for title in section_titles if title.startswith("Movimiento ")]),
        check("complete_concept_units", sum(item["words"] >= 150 for item in subsection_lengths) > len(subsection_lengths) / 2, subsection_lengths),
        check("hh11_instrument_nine_fields", len(re.findall(r"^[1-9]\. \*\*", text[text.index("### Instrumento HH-11") : text.index("### La suficiencia")], flags=re.MULTILINE)) == 9, "nine fields"),
        check("five_pills", len(pills) == 5, len(pills)),
        check("six_questions", len(questions) == 6, len(questions)),
        check("six_referents", len(referents) == 6, len(referents)),
        check("reference_depth", len(reference_entries) >= 12, len(reference_entries)),
        check("recent_literature", len(recent_references) >= 5, len(recent_references)),
        check("reference_urls", len(urls) >= 9, len(urls)),
        check("all_references_anchored_in_body", all(anchor in body_without_references for anchor in reference_anchors.values()), {name: anchor in body_without_references for name, anchor in reference_anchors.items()}),
        check("cross_document_uniqueness", not repeated, repeated[:20]),
        check("predecessor_successor_boundary", all(term in text for term in required_terms), required_terms),
        check("impersonal_register", not prohibited_register, prohibited_register),
        check("no_placeholders", not editorial_placeholders, editorial_placeholders),
        check("no_incidental_dashes_in_prose", not stray_dashes, stray_dashes),
        check("content_only_package", not list(PACKAGE.rglob("*.pdf")) and not list(PACKAGE.rglob("*.html")) and not list(PACKAGE.rglob("*.css")), "no PDF, HTML or CSS"),
    ]

    report = {
        "document": "N11",
        "title": "Cuándo un dato permite sostener una afirmación",
        "stage": "content-canonical-v1",
        "language": "es-AR",
        "source": str(SOURCE.relative_to(ROOT)),
        "sha256": source_hash,
        "bytes": SOURCE.stat().st_size,
        "words_total": len(words(text)),
        "words_substantive": len(words(substantive)),
        "source_blocks": len(blocks),
        "references": len(reference_entries),
        "urls": len(urls),
        "results": results,
        "overall": "pass" if all(item["result"] == "pass" for item in results) else "fail",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    SOURCE_MANIFEST.write_text(json.dumps({
        "document": "N11",
        "stage": "content-canonical-v1",
        "source": str(SOURCE.relative_to(PACKAGE)),
        "source_sha256": source_hash,
        "eligible_blocks": blocks,
        "block_count": len(blocks),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["overall"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
