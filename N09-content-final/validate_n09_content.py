#!/usr/bin/env python3
"""Controles deterministas para el manuscrito canónico de N09.

El validador inspecciona sólo la fuente Markdown. No compone ni revisa PDF.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source" / "N09_experiencia_accesibilidad_y_adopcion-content-final.md"
REPORT = ROOT / "provenance" / "integrity-report.json"
MANIFEST = ROOT / "source-manifest.json"


def words(text: str) -> list[str]:
    return re.findall(
        r"\b[\wÁÉÍÓÚÜÑáéíóúüñ]+(?:[-‑][\wÁÉÍÓÚÜÑáéíóúüñ]+)*\b",
        text,
        flags=re.UNICODE,
    )


def check(name: str, passed: bool, evidence: object) -> dict[str, object]:
    return {"check": name, "result": "pass" if passed else "fail", "evidence": evidence}


def main() -> int:
    text = SOURCE.read_text(encoding="utf-8")
    before_references, references = text.split("## Referencias base", 1)
    substantive = text[text.index("## Tesis") : text.index("## Cinco píldoras para recordar")]
    headings = re.findall(r"^(#{1,4}) (.+)$", text, flags=re.MULTILINE)
    heading_names = [name for _, name in headings]

    required_order = [
        "Pregunta profesional",
        "La puerta automática que sólo era automática para algunos",
        "Tesis",
        "De N08 a N09: del trabajo realizado al recorrido vivido",
        "Movimiento 1 · Seguir el recorrido completo y reconocer barreras sistémicas",
        "Movimiento 2 · Diseñar con diversidad y comprender la adopción",
        "Movimiento 3 · Medir, recuperar y gobernar la experiencia",
        "De HH-09 a N10: evidencia para construir el problema",
        "Errores frecuentes",
        "Consecuencias profesionales",
        "Límites y tensiones",
        "Síntesis",
        "Cinco píldoras para recordar",
        "Glosario esencial",
        "Preguntas de preparación",
        "Referencias base",
    ]
    positions = [heading_names.index(item) for item in required_order]

    reference_lines = [line for line in references.splitlines() if line.startswith("- ")]
    anchors = {
        "ISO 9241-11:2018": r"ISO 9241-11:2018",
        "ISO 9241-210:2019": r"ISO 9241-210:2019",
        "W3C WCAG 2.2": r"WCAG 2\.2",
        "ISO/IEC 40500:2025": r"ISO/IEC 40500:2025",
        "W3C Accessibility Principles": r"propio W3C.*accesibilidad depende",
        "Costanza-Chock (2020)": r"Sasha Costanza-Chock",
        "Lazar, Goldstein y Taylor (2015)": r"Lazar, Goldstein y Taylor",
        "Norman (2013)": r"Donald Norman",
        "Rogers (2003)": r"Everett Rogers",
        "Suchman (2007)": r"Lucy Suchman",
        "Directiva UE 2019/882": r"European Accessibility Act",
        "Reglamento UE 2024/1689": r"Reglamento europeo de IA 2024/1689",
        "Autio et al. (2024)": r"perfil de IA generativa del NIST",
        "Gmyrek et al. (2025)": r"Según la OIT",
    }
    anchor_results = {
        key: bool(re.search(pattern, before_references, flags=re.IGNORECASE | re.DOTALL))
        for key, pattern in anchors.items()
    }

    pills_block = text[text.index("## Cinco píldoras para recordar") : text.index("## Glosario esencial")]
    questions_block = text[text.index("## Preguntas de preparación") : text.index("## Referencias base")]
    pill_count = len(re.findall(r"^\d+\. \*\*", pills_block, flags=re.MULTILINE))
    question_count = len(re.findall(r"^\d+\. ¿", questions_block, flags=re.MULTILINE))
    urls = re.findall(r"https://[^\s)]+", references)
    placeholders = {
        token: len(re.findall(re.escape(token), text, flags=re.IGNORECASE))
        for token in ("TBD", "lorem", "XXX", "[TODO]")
    }
    prose_dash_lines = [
        number
        for number, line in enumerate(before_references.splitlines(), 1)
        if " — " in line or " – " in line
    ]

    quoted_removed = re.sub(r"«[^»]*»|“[^”]*”|\"[^\"]*\"", "", before_references, flags=re.DOTALL)
    second_person_hits = re.findall(
        r"\b(?:vos|tú|usted|ustedes|podés|deberías|hacé|mirá|situá|seleccioná|usarías|convertirías|querés|viste|recordás|podrías|imagine)\b",
        quoted_removed,
        flags=re.IGNORECASE,
    )
    first_person_plural_hits = re.findall(
        r"\b(?:nos|nuestro|nuestra|nuestros|nuestras|podemos|pensemos|aprendimos|veamos|recordemos|hagamos|usamos|dejamos|seguimos|modelamos|automatizamos|supongamos|sabremos|estamos)\b",
        quoted_removed,
        flags=re.IGNORECASE,
    )
    deferred_terms = re.findall(r"\boutcomes?\b", before_references, flags=re.IGNORECASE)
    english_residue = re.findall(
        r"\b(?:dashboard|chatbot|logs?|member checking|focus group|trade-off|insights?|workaround|prompt|offline|shadowing|walkthrough|handoff|takeover|end-to-end|workflow|fallback|frontstage|backstage|guardrails?)\b",
        before_references,
        flags=re.IGNORECASE,
    )

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
    repeated_ngrams = [
        {"text": " ".join(ngram), "positions": positions}
        for ngram, positions in ngram_positions.items()
        if len(positions) > 1
    ]

    hh09_fields = [
        "propósito",
        "condiciones",
        "señal visible",
        "acción requerida",
        "trabajo que sostiene la transición",
        "evidencia crítica",
        "modo de falla",
        "alternativa y reparación",
    ]
    protocol_steps = [
        "Definir la capacidad esperada",
        "Reconstruir episodios completos",
        "Representar transiciones y dependencias",
        "Probar diversidad y recuperación",
        "Evaluar distribución de carga y riesgo",
        "Decidir, monitorear y conservar salida",
    ]

    results = [
        check("canonical_heading_order", positions == sorted(positions), required_order),
        check("three_movement_architecture", sum(name.startswith("Movimiento ") for name in heading_names) == 3, [name for name in heading_names if name.startswith("Movimiento ")]),
        check("substantive_word_floor", len(words(substantive)) >= 6000, len(words(substantive))),
        check("total_word_count", 7500 <= len(words(text)) <= 9000, len(words(text))),
        check("hotel_horizonte_conductor", before_references.count("HH-09") >= 10 and before_references.count("Hotel Horizonte") >= 6, {"HH-09": before_references.count("HH-09"), "Hotel Horizonte": before_references.count("Hotel Horizonte")}),
        check("three_hh09_applications", len(re.findall(r"^### (?:Primera|Segunda|Tercera) aplicación de HH-09", before_references, flags=re.MULTILINE)) == 3, 3),
        check("n08_input_declared", all(term in before_references for term in ("N08 dejó tramos abiertos", "verificaciones repetidas", "ayudas", "canales alternativos", "excepciones localizadas")), "declared"),
        check("n10_handoff_declared", all(term in before_references for term in ("De HH-09 a N10", "N10 decidirá", "encuadre provisional")), "declared"),
        check("n10_term_not_anticipated", not deferred_terms, deferred_terms),
        check("hh09_decision_fields", all(term in before_references for term in hh09_fields), hh09_fields),
        check("six_step_protocol", all(term in before_references for term in protocol_steps), protocol_steps),
        check("three_rival_explanations", len(re.findall(r"^\*\*Explicación rival [ABC]", before_references, flags=re.MULTILINE)) == 3, 3),
        check("systemic_accessibility", all(term in before_references for term in ("atributos verificables", "alternativa efectiva", "accesibilidad es una cadena", "ISO 9241-210:2019", "WCAG 2.2")), "present"),
        check("adoption_as_relationship", all(term in before_references for term in ("La adopción es adaptación mutua", "no uso", "Everett Rogers", "uso sostenido")), "present"),
        check("distributive_metrics", all(term in before_references for term in ("tiempo", "esfuerzo", "asistencia", "error", "distribución")), "present"),
        check("current_2026_implication", all(term in before_references for term in ("ISO/IEC 40500:2025", "European Accessibility Act", "NIST", "OIT", "interfaces conversacionales")), "present"),
        check("transfer_case", any(name.startswith("Caso de transferencia: inscripción universitaria") for name in heading_names), "present"),
        check("reference_count", len(reference_lines) == len(anchors) == 14, len(reference_lines)),
        check("all_references_anchored", all(anchor_results.values()), anchor_results),
        check("five_pills", pill_count == 5, pill_count),
        check("six_questions", question_count == 6, question_count),
        check("preparation_instruction", "dos de las seis preguntas" in questions_block and "ficha breve para HH-09" in questions_block, "present"),
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
        "document": "N09",
        "stage": "content-final",
        "source": str(SOURCE.relative_to(ROOT)),
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "bytes": SOURCE.stat().st_size,
        "word_counts": {
            "total": len(words(text)),
            "substantive_from_thesis_through_synthesis": len(words(substantive)),
        },
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
        sections.append(
            {
                "order": index + 1,
                "heading": match.group(1),
                "words": len(words(section_text)),
                "sha256": hashlib.sha256(section_text.encode("utf-8")).hexdigest(),
            }
        )
    manifest = {
        "document": "N09",
        "stage": "content-final",
        "title": "Experiencia, accesibilidad y adopción no son decoración",
        "language": "es-AR",
        "format": "Markdown source only",
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": payload["sha256"],
        "source_bytes": payload["bytes"],
        "word_counts": payload["word_counts"],
        "sections": sections,
        "reference_entries": len(reference_lines),
        "urls": urls,
        "excluded_artifacts": ["PDF", "HTML", "CSS", "photography", "illustration", "layout"],
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["overall"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
