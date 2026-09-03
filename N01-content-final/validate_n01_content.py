#!/usr/bin/env python3
"""Controles deterministas del contenido canónico de N01."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source" / "N01_metodologia_sin_recetas-content-final.md"
REPORT = ROOT / "provenance" / "integrity-report.json"
MANIFEST = ROOT / "source-manifest.json"


def words(text: str) -> list[str]:
    return re.findall(r"\b[\wÁÉÍÓÚÜÑáéíóúüñ]+(?:[-‑][\wÁÉÍÓÚÜÑáéíóúüñ]+)*\b", text)


def item(name: str, passed: bool, evidence: object) -> dict[str, object]:
    return {"check": name, "result": "pass" if passed else "fail", "evidence": evidence}


def main() -> int:
    text = SOURCE.read_text(encoding="utf-8")
    body, references = text.split("## Referencias base", 1)
    substantive = text[text.index("## Tesis") : text.index("## Cinco píldoras para recordar")]
    headings = re.findall(r"^## (.+)$", text, flags=re.MULTILINE)
    required = [
        "Pregunta profesional", "El mapa perfecto de la montaña equivocada", "Tesis",
        "Cómo leer este mapa: N01 abre el recorrido N02 a N10",
        "Aplicación a Hotel Horizonte: construir HH-01",
        "Caso de transferencia: turnos en un centro de salud",
        "Consecuencias para la práctica profesional", "Límites y tensiones", "Síntesis",
        "Cinco píldoras para recordar", "Glosario esencial", "Preguntas de preparación",
        "Referencias base",
    ]
    positions = [headings.index(name) for name in required]
    reference_lines = [line for line in references.splitlines() if line.startswith("- ")]
    anchors = {
        "Checkland y Poulter": r"Checkland y Poulter", "Schön": r"Schön describió",
        "Argyris y Schön": r"Argyris y Schön", "March": r"March formuló",
        "Suchman": r"Lucy Suchman", "Senge": r"Senge agrega",
        "ISO/IEC/IEEE 24748-1:2024": r"24748-1:2024", "PMBOK 2025": r"octava edición del PMBOK",
        "NIST AI RMF 1.0": r"AI Risk Management Framework 1\.0 de NIST",
        "NIST AI 600-1": r"perfil de NIST para inteligencia artificial generativa",
        "SWEBOK V4.0a": r"SWEBOK Guide V4\.0a", "ISO/IEC/IEEE 15288:2023": r"15288:2023",
        "Reglamento UE 2024/1689": r"Reglamento de Inteligencia Artificial de la Unión Europea",
        "DORA 2025": r"informe DORA 2025", "IS2020": r"modelo curricular IS2020",
    }
    anchor_results = {key: bool(re.search(pattern, body, flags=re.IGNORECASE)) for key, pattern in anchors.items()}
    pills = text[text.index("## Cinco píldoras para recordar") : text.index("## Glosario esencial")]
    questions = text[text.index("## Preguntas de preparación") : text.index("## Referencias base")]
    placeholders = {token: len(re.findall(re.escape(token), text, flags=re.IGNORECASE)) for token in ("TBD", "lorem", "XXX", "[TODO]")}
    urls = re.findall(r"https://[^\s)]+", references)
    fields = ["pedido", "propósito", "incertidumbre", "evidencia", "acción autorizada", "decisión todavía no autorizada", "condición de revisión"]
    results = [
        item("canonical_heading_order", positions == sorted(positions), required),
        item("substantive_word_floor", len(words(substantive)) >= 6000, len(words(substantive))),
        item("total_word_count", 7500 <= len(words(text)) <= 9000, len(words(text))),
        item("hh01_present", body.count("HH-01") >= 3, body.count("HH-01")),
        item("hh01_fields", all(value in body.lower() for value in fields), fields),
        item("n02_handoff", all(value in body for value in ("Entrega a N02", "qué sistema produce la situación", "construir el sistema relevante")), "declared"),
        item("reference_count", len(reference_lines) == len(anchors) == 15, len(reference_lines)),
        item("all_references_anchored", all(anchor_results.values()), anchor_results),
        item("five_pills", len(re.findall(r"^- ", pills, flags=re.MULTILINE)) == 5, len(re.findall(r"^- ", pills, flags=re.MULTILINE))),
        item("seven_questions", len(re.findall(r"^\d+\. ¿", questions, flags=re.MULTILINE)) == 7, len(re.findall(r"^\d+\. ¿", questions, flags=re.MULTILINE))),
        item("hh01_preparation", "ficha breve de HH-01" in questions and "dos de las siete preguntas" in questions, "present"),
        item("no_placeholders", all(value == 0 for value in placeholders.values()), placeholders),
        item("no_prose_dashes", not any(" — " in line or " – " in line for line in body.splitlines()), "none"),
        item("urls_unique", len(urls) == len(set(urls)), {"count": len(urls), "unique": len(set(urls))}),
        item("content_only", not re.search(r"\.(?:pdf|html|css|png|jpe?g)\b", body, flags=re.IGNORECASE), "source only"),
    ]
    payload = {
        "document": "N01", "stage": "content-final", "source": str(SOURCE.relative_to(ROOT)),
        "sha256": hashlib.sha256(text.encode()).hexdigest(), "bytes": SOURCE.stat().st_size,
        "word_counts": {"total": len(words(text)), "substantive_from_thesis_through_synthesis": len(words(substantive))},
        "references": {"entries": len(reference_lines), "urls": urls, "anchors": anchor_results},
        "results": results, "overall": "pass" if all(row["result"] == "pass" for row in results) else "fail",
    }
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "document": "N01", "stage": "content-final", "title": "Metodología sin recetas: intervenir cuando el problema todavía no está claro",
        "language": "es-AR", "format": "Markdown source only", "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": payload["sha256"], "source_bytes": payload["bytes"], "word_counts": payload["word_counts"],
        "reference_entries": len(reference_lines), "urls": urls,
        "excluded_artifacts": ["PDF", "HTML", "CSS", "photography", "illustration", "layout"],
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["overall"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
