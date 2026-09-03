#!/usr/bin/env python3
"""Controles deterministas para el manuscrito canónico de N10.

El validador inspecciona sólo la fuente Markdown. No compone ni revisa PDF.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source" / "N10_construir_el_problema_y_outcomes-content-final.md"
REPORT = ROOT / "provenance" / "integrity-report.json"
MANIFEST = ROOT / "source-manifest.json"


def words(text: str) -> list[str]:
    return re.findall(r"\b[\wÁÉÍÓÚÜÑáéíóúüñ]+(?:[-‑][\wÁÉÍÓÚÜÑáéíóúüñ]+)*\b", text, flags=re.UNICODE)


def check(name: str, passed: bool, evidence: object) -> dict[str, object]:
    return {"check": name, "result": "pass" if passed else "fail", "evidence": evidence}


def main() -> int:
    text = SOURCE.read_text(encoding="utf-8")
    before_references, references = text.split("## Referencias base", 1)
    substantive = text[text.index("## Tesis") : text.index("## Cinco píldoras para recordar")]
    headings = re.findall(r"^(#{1,4}) (.+)$", text, flags=re.MULTILINE)
    heading_names = [name for _, name in headings]
    required_order = [
        "Pregunta profesional", "El puente que resolvía el problema equivocado",
        "Hotel Horizonte: una decisión que parece estar tomada", "Tesis",
        "De N09 a N10: del recorrido vivido al encuadre provisional",
        "Movimiento 1 · Separar pedido, síntoma, mecanismo y problema",
        "Movimiento 2 · Formular outcomes, protecciones y evidencia de revisión",
        "Movimiento 3 · Integrar evidencia y abrir una puerta de decisión",
        "Errores frecuentes", "Consecuencias profesionales",
        "Cierre del Bloque 1: un encuadre listo para ser refutado", "Síntesis",
        "Cinco píldoras para recordar", "Glosario esencial", "Preguntas de preparación",
        "Referencias base",
    ]
    positions = [heading_names.index(item) for item in required_order]
    reference_lines = [line for line in references.splitlines() if line.startswith("- ")]
    anchors = {
        "Dorst (2011)": r"Dorst explica|Kees Dorst",
        "Jackson (2001)": r"Michael Jackson",
        "Schön y Rein (1994)": r"Schön y Rein",
        "Toulmin (2003)": r"Toulmin",
        "Pawson y Tilley (1997)": r"Pawson y Tilley",
        "W. K. Kellogg Foundation (2004)": r"W\. K\. Kellogg Foundation",
        "ISO/IEC/IEEE 29148:2018": r"ISO/IEC/IEEE 29148:2018",
        "World Economic Forum (2025)": r"Future of Jobs Report 2025",
        "NIST AI 600-1": r"NIST AI RMF",
        "Reglamento UE 2024/1689": r"Reglamento de Inteligencia Artificial de la Unión Europea",
        "DORA (2025)": r"informe DORA 2025",
        "SWEBOK V4": r"SWEBOK V4",
        "ISO/IEC/IEEE 15288:2023": r"ISO/IEC/IEEE 15288:2023",
    }
    anchor_results = {key: bool(re.search(pattern, before_references, flags=re.IGNORECASE | re.DOTALL)) for key, pattern in anchors.items()}
    pills_block = text[text.index("## Cinco píldoras para recordar") : text.index("## Glosario esencial")]
    questions_block = text[text.index("## Preguntas de preparación") : text.index("## Referencias base")]
    pill_count = len(re.findall(r"^\d+\. \*\*", pills_block, flags=re.MULTILINE))
    question_count = len(re.findall(r"^\d+\. ¿", questions_block, flags=re.MULTILINE))
    urls = re.findall(r"https://[^\s)]+", references)
    placeholders = {token: len(re.findall(re.escape(token), text, flags=re.IGNORECASE)) for token in ("TBD", "lorem", "XXX", "[TODO]")}
    prose_dash_lines = [number for number, line in enumerate(before_references.splitlines(), 1) if " — " in line or " – " in line]
    quoted_removed = re.sub(r"«[^»]*»|“[^”]*”|\"[^\"]*\"", "", before_references, flags=re.DOTALL)
    second_person_hits = re.findall(r"\b(?:vos|tú|usted|ustedes|podés|deberías|hacé|mirá|situá|seleccioná|usarías|convertirías|querés|viste|recordás|podrías|imagine|formule|justifique)\b", quoted_removed, flags=re.IGNORECASE)
    first_person_plural_hits = re.findall(r"\b(?:nos|nuestro|nuestra|nuestros|nuestras|podemos|pensemos|aprendimos|veamos|recordemos|hagamos|usamos|dejamos|seguimos|modelamos|automatizamos|supongamos|sabremos|estamos|necesitamos|esperamos|observamos|incluimos|reconstruimos|preguntamos|buscamos)\b", quoted_removed, flags=re.IGNORECASE)
    english_residue = re.findall(r"\b(?:dashboard|chatbot|logs?|member checking|focus group|trade-off|insights?|workaround|prompt|offline|shadowing|walkthrough|handoff|takeover|workflow|fallback|frontstage|backstage|brief|backlog|demo)\b", before_references, flags=re.IGNORECASE)

    repeated_paragraphs = []
    paragraph_seen: dict[str, int] = {}
    for paragraph_number, paragraph in enumerate(re.split(r"\n\s*\n", before_references), 1):
        normalized = re.sub(r"\s+", " ", paragraph.strip())
        if len(words(normalized)) < 20 or normalized.startswith(("#", "|", "- ", "1. ")):
            continue
        if normalized in paragraph_seen:
            repeated_paragraphs.append((paragraph_seen[normalized], paragraph_number, normalized[:90]))
        else:
            paragraph_seen[normalized] = paragraph_number
    normalized_words = [item.lower() for item in words(before_references)]
    ngram_positions: dict[tuple[str, ...], list[int]] = defaultdict(list)
    for index in range(max(0, len(normalized_words) - 11)):
        ngram_positions[tuple(normalized_words[index : index + 12])].append(index)
    repeated_ngrams = [{"text": " ".join(ngram), "positions": found} for ngram, found in ngram_positions.items() if len(found) > 1]

    hh10_fields = ["situación", "afectados y perspectivas", "outcome", "mecanismos rivales", "evidencia y vacíos", "frontera", "restricciones y preferencias", "protecciones y reparación", "condición de revisión"]
    decision_gate = ["Aprobar el encuadre", "Devolverlo por falta de evidencia decisiva", "Dividir el problema", "Reformular la frontera o el mecanismo"]
    results = [
        check("canonical_heading_order", positions == sorted(positions), required_order),
        check("three_movement_architecture", sum(name.startswith("Movimiento ") for name in heading_names) == 3, [name for name in heading_names if name.startswith("Movimiento ")]),
        check("substantive_word_floor", len(words(substantive)) >= 6000, len(words(substantive))),
        check("total_word_count", 8000 <= len(words(text)) <= 10000, len(words(text))),
        check("hotel_horizonte_conductor", before_references.count("HH-10") >= 8 and before_references.count("Hotel Horizonte") >= 8, {"HH-10": before_references.count("HH-10"), "Hotel Horizonte": before_references.count("Hotel Horizonte")}),
        check("three_hh10_applications", len(re.findall(r"^### (?:Primera|Segunda|Tercera) aplicación de HH-10", before_references, flags=re.MULTILINE)) == 3, 3),
        check("n09_input_declared", all(term in before_references for term in ("N09 produjo HH-09", "propósito", "señal visible", "evidencia crítica", "alternativa o reparación")), "declared"),
        check("block_one_closure", all(term in before_references for term in ("Esta lectura cierra el Bloque 1", "Cierre del Bloque 1", "Así termina el Bloque 1")), "declared"),
        check("n11_boundary_declared", all(term in before_references for term in ("N11 abrirá otro bloque", "cuándo un dato puede sostener una afirmación", "no anticipa esa auditoría")), "declared"),
        check("hh10_decision_fields", all(term in before_references.lower() for term in hh10_fields), hh10_fields),
        check("decision_gate", all(term in before_references for term in decision_gate), decision_gate),
        check("four_rival_frames", len(re.findall(r"^#### [1-4]\. ", before_references, flags=re.MULTILINE)) == 4, 4),
        check("outcome_distinctions", all(term in before_references for term in ("Un **output**", "Un **outcome**", "El **impacto**", "El **valor**")), "present"),
        check("current_2026_implication", all(term in before_references for term in ("DORA 2025", "Future of Jobs Report 2025", "NIST AI RMF", "Reglamento de Inteligencia Artificial de la Unión Europea")), "present"),
        check("transfer_case", any(name.startswith("Caso de transferencia: demoras en una guardia") for name in heading_names), "present"),
        check("reference_count", len(reference_lines) == len(anchors) == 13, len(reference_lines)),
        check("all_references_anchored", all(anchor_results.values()), anchor_results),
        check("five_pills", pill_count == 5, pill_count),
        check("six_questions", question_count == 6, question_count),
        check("preparation_instruction", "dos de las seis preguntas" in questions_block and "ficha breve de HH-10" in questions_block, "present"),
        check("no_placeholders", all(value == 0 for value in placeholders.values()), placeholders),
        check("no_prose_dashes", not prose_dash_lines, prose_dash_lines),
        check("impersonal_expository_register", not second_person_hits and not first_person_plural_hits, {"second_person": second_person_hits, "first_person_plural": first_person_plural_hits}),
        check("anglicisms_normalized", not english_residue, english_residue),
        check("no_exact_duplicate_paragraphs", not repeated_paragraphs, repeated_paragraphs),
        check("no_repeated_12_word_sequences", not repeated_ngrams, repeated_ngrams[:10]),
        check("urls_unique", len(urls) == len(set(urls)), {"count": len(urls), "unique": len(set(urls))}),
        check("content_only_package", not re.search(r"\.(?:pdf|html|css|png|jpe?g)\b", before_references, flags=re.IGNORECASE), "no layout or image artifact references"),
    ]
    payload = {
        "document": "N10", "stage": "content-final", "source": str(SOURCE.relative_to(ROOT)),
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(), "bytes": SOURCE.stat().st_size,
        "word_counts": {"total": len(words(text)), "substantive_from_thesis_through_synthesis": len(words(substantive))},
        "references": {"entries": len(reference_lines), "urls": urls, "anchors": anchor_results},
        "results": results,
        "overall": "pass" if all(item["result"] == "pass" for item in results) else "fail",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    h2_matches = list(re.finditer(r"^## (.+)$", text, flags=re.MULTILINE))
    sections = []
    for index, match in enumerate(h2_matches):
        end = h2_matches[index + 1].start() if index + 1 < len(h2_matches) else len(text)
        section_text = text[match.start() : end].strip() + "\n"
        sections.append({"order": index + 1, "heading": match.group(1), "words": len(words(section_text)), "sha256": hashlib.sha256(section_text.encode("utf-8")).hexdigest()})
    manifest = {
        "document": "N10", "stage": "content-final",
        "title": "Construir el problema: de síntomas a outcomes verificables", "language": "es-AR",
        "format": "Markdown source only", "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": payload["sha256"], "source_bytes": payload["bytes"],
        "word_counts": payload["word_counts"], "sections": sections,
        "reference_entries": len(reference_lines), "urls": urls,
        "excluded_artifacts": ["PDF", "HTML", "CSS", "photography", "illustration", "layout"],
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["overall"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
