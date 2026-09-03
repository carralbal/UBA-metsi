#!/usr/bin/env python3
"""Controles deterministas del contenido canónico de N02."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source" / "N02_el_sistema_no_cabe_en_una_aplicacion-content-final.md"
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
    headings = re.findall(r"^(#{2,3}) (.+)$", text, flags=re.MULTILINE)
    names = [name for _, name in headings]
    required = [
        "Pregunta profesional", "La valija que el sistema había embarcado",
        "Primera aplicación de HH-02: una reserva confirmada que no alcanza", "Tesis",
        "De HH-01 a HH-02: del pedido revisable al sistema relevante",
        "Segunda aplicación de HH-02: una autopsia del episodio",
        "Tercera aplicación de HH-02: una frontera lista para ser revisada",
        "De HH-02 a N03: un mapa con consecuencias abiertas", "Síntesis",
        "Cinco píldoras para recordar", "Glosario esencial", "Preguntas de preparación", "Referencias base",
    ]
    positions = [names.index(name) for name in required]
    reference_lines = [line for line in references.splitlines() if line.startswith("- ")]
    anchors = {
        "Alter (2002)": r"Steven Alter propuso", "Checkland y Poulter": r"Checkland y John Poulter",
        "Clegg (2000)": r"Clegg \(2000\)", "Mumford (2003)": r"Enid Mumford|Mumford insistió",
        "Trist y Bamforth (1951)": r"Trist y Bamforth", "Baxter y Sommerville (2011)": r"Baxter y Sommerville",
        "IS2020": r"modelo curricular IS2020", "NIST AI RMF 1.0": r"NIST \(Tabassi, 2023\)",
        "DORA (2025)": r"DORA, al estudiar.*2025", "DORA (2026)": r"DORA \(2026\)",
        "Alter (2024)": r"Alter \(2024\)", "Polojärvi (2023)": r"Polojärvi \(2023\)",
        "ISO/IEC/IEEE 15288:2023": r"15288:2023", "NIST AI 600-1": r"Autio y colaboradores, 2024",
        "Hofmann et al. (2024)": r"Hofmann y colaboradores \(2024\)",
        "Nguyen y Elbanna (2025)": r"Nguyen y Elbanna \(2025\)", "NIST (2026)": r"NIST \(2026\)",
    }
    anchor_results = {key: bool(re.search(pattern, body, flags=re.IGNORECASE | re.DOTALL)) for key, pattern in anchors.items()}
    pills = text[text.index("## Cinco píldoras para recordar") : text.index("## Glosario esencial")]
    questions = text[text.index("## Preguntas de preparación") : text.index("## Referencias base")]
    placeholders = {token: len(re.findall(re.escape(token), text, flags=re.IGNORECASE)) for token in ("TBD", "lorem", "XXX", "[TODO]")}
    urls = re.findall(r"https://[^\s)]+", references)
    results = [
        item("canonical_heading_order", positions == sorted(positions), required),
        item("substantive_word_floor", len(words(substantive)) >= 6000, len(words(substantive))),
        item("total_word_count", 8000 <= len(words(text)) <= 9500, len(words(text))),
        item("three_hh02_applications", len(re.findall(r"^#{2,3} (?:Primera|Segunda|Tercera) aplicación de HH-02", body, flags=re.MULTILINE)) == 3, 3),
        item("hh01_input", all(value in body for value in ("HH-01, construido en N01, dejó un memo", "acción autorizada", "decisión todavía no autorizada")), "declared"),
        item("n03_handoff", all(value in body for value in ("De HH-02 a N03", "demoras, carga o riesgo desplazado", "No desarrolla todavía bucles de retroalimentación")), "declared"),
        item("reference_count", len(reference_lines) == len(anchors) == 17, len(reference_lines)),
        item("all_references_anchored", all(anchor_results.values()), anchor_results),
        item("five_pills", len(re.findall(r"^\d+\. \*\*", pills, flags=re.MULTILINE)) == 5, len(re.findall(r"^\d+\. \*\*", pills, flags=re.MULTILINE))),
        item("six_questions", len(re.findall(r"^\d+\. ", questions, flags=re.MULTILINE)) == 6, len(re.findall(r"^\d+\. ", questions, flags=re.MULTILINE))),
        item("preparation_instruction", "dos de las seis preguntas" in questions, "present"),
        item("no_placeholders", all(value == 0 for value in placeholders.values()), placeholders),
        item("no_prose_dashes", not any(" — " in line or " – " in line for line in body.splitlines()), "none"),
        item("urls_unique", len(urls) == len(set(urls)), {"count": len(urls), "unique": len(set(urls))}),
        item("content_only", not re.search(r"\.(?:pdf|html|css|png|jpe?g)\b", body, flags=re.IGNORECASE), "source only"),
    ]
    payload = {
        "document": "N02", "stage": "content-final", "source": str(SOURCE.relative_to(ROOT)),
        "sha256": hashlib.sha256(text.encode()).hexdigest(), "bytes": SOURCE.stat().st_size,
        "word_counts": {"total": len(words(text)), "substantive_from_thesis_through_synthesis": len(words(substantive))},
        "references": {"entries": len(reference_lines), "urls": urls, "anchors": anchor_results},
        "results": results, "overall": "pass" if all(row["result"] == "pass" for row in results) else "fail",
    }
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "document": "N02", "stage": "content-final", "title": "El sistema de información no cabe en una aplicación",
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
