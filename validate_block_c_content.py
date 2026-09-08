#!/usr/bin/env python3
"""Auditoría reproducible de contenidos canónicos del Bloque C de METSI."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def tokens(text: str) -> list[str]:
    return re.findall(r"[a-záéíóúüñ0-9]+", unicodedata.normalize("NFC", text.lower()))


def words(text: str) -> list[str]:
    return re.findall(r"\b[\wÁÉÍÓÚÜÑáéíóúüñ]+(?:[-‑][\wÁÉÍÓÚÜÑáéíóúüñ]+)*\b", text)


def result(name: str, passed: bool, evidence: object) -> dict[str, object]:
    return {"check": name, "result": "pass" if passed else "fail", "evidence": evidence}


def blocks_for(code: str, text: str) -> list[dict[str, object]]:
    blocks: list[dict[str, object]] = []
    buffer: list[str] = []
    start = 0

    def flush(end: int) -> None:
        nonlocal buffer
        if not buffer:
            return
        content = "\n".join(buffer).strip()
        if content:
            kind = "list_item" if re.match(r"^(?:[-*]|\d+\.)\s", content) else "paragraph"
            blocks.append({"kind": kind, "line_start": start, "line_end": end, "text": content})
        buffer = []

    lines = text.splitlines()
    for number, line in enumerate(lines, 1):
        if re.match(r"^#{1,6}\s", line):
            flush(number - 1)
            blocks.append({"kind": "heading", "line_start": number, "line_end": number, "text": line.strip()})
        elif not line.strip():
            flush(number - 1)
        elif re.match(r"^(?:[-*]|\d+\.)\s", line) and buffer:
            flush(number - 1)
            start = number
            buffer = [line]
        else:
            if not buffer:
                start = number
            buffer.append(line)
    flush(len(lines))
    for index, block in enumerate(blocks, 1):
        block["source_id"] = f"{code}-S{index:03d}"
        block["sha256"] = hashlib.sha256(str(block["text"]).encode()).hexdigest()
        block["words"] = len(words(str(block["text"])))
    return blocks


def prior_sources(number: int) -> dict[str, Path]:
    names = {
        1: "N01-content-final/source/N01_metodologia_sin_recetas-content-final.md",
        2: "N02-content-final/source/N02_el_sistema_no_cabe_en_una_aplicacion-content-final.md",
        3: "N03-content-final/source/N03_fronteras_retroalimentacion_y_efectos-content-final.md",
        4: "N04-content-final/source/N04_hechos_sintomas_relatos_hipotesis_y_decisiones-content-final.md",
        5: "N05-content-final/source/N05_actores_afectados_poder_y_perspectivas-content-final.md",
        6: "N06-content-final/source/N06_discovery_como_reduccion_de_incertidumbre-content-final.md",
        7: "N07-content-final/source/N07_entrevistar_no_es_pedir_requisitos-content-final.md",
        8: "N08-content-final/source/N08_observar_el_trabajo_invisible-content-final.md",
        9: "N09-content-final/source/N09_experiencia_accesibilidad_y_adopcion-content-final.md",
        10: "N10-content-final/source/N10_construir_el_problema_y_outcomes-content-final.md",
        11: "N11-content-canonical/source/N11_cuando_un_dato_sostiene_una_afirmacion-content-canonical-v1.md",
        12: "N12-content-canonical/source/N12_eventos_estados_comandos_evidencia_y_autoridad-content-canonical-v1.md",
        13: "N13-content-canonical/source/N13_demoras_concurrencia_consistencia_idempotencia_y_reconciliacion-content-canonical-v1.md",
        14: "N14-content-canonical/source/N14_procesos_end_to_end_handoffs_colas_y_excepciones-content-canonical-v1.md",
        15: "N15-content-canonical/source/N15_seleccionar_modelos_segun_pregunta_audiencia_y_costo-content-canonical-v1.md",
    }
    return {f"N{n:02d}": ROOT / names[n] for n in range(1, number) if n in names and (ROOT / names[n]).is_file()}


def audit(package: Path) -> dict[str, object]:
    config = json.loads((package / "content-config.json").read_text())
    code = config["document"]
    number = int(code[1:])
    source = package / config["source"]
    text = source.read_text()
    body = text.split("## Referencias base", 1)[0]
    references = text.split("## Referencias base", 1)[1]
    substantive = text[text.index(config["opening_heading"]):text.index("## Cinco píldoras para recordar")]
    source_blocks = blocks_for(code, text)

    current = tokens(body)
    ngrams = {tuple(current[i:i + 24]) for i in range(max(0, len(current) - 23))}
    repeated: list[dict[str, str]] = []
    for prior_code, path in prior_sources(number).items():
        prior = tokens(path.read_text().split("## Referencias base", 1)[0])
        seen: set[tuple[str, ...]] = set()
        for index in range(max(0, len(prior) - 23)):
            gram = tuple(prior[index:index + 24])
            if gram in ngrams and gram not in seen:
                repeated.append({"document": prior_code, "text": " ".join(gram)})
                seen.add(gram)

    sections = re.findall(r"^## (.+)$", text, flags=re.MULTILINE)
    core = substantive.split("## Errores frecuentes", 1)[0]
    unit_lengths = []
    for chunk in re.split(r"(?m)^### ", core)[1:]:
        title, _, content = chunk.partition("\n")
        unit_lengths.append({"title": title, "words": len(words(content))})
    instrument = text[text.index(config["instrument_heading"]):text.index(config["instrument_end_heading"])]
    pills = re.findall(r"^[1-5]\. ", text[text.index("## Cinco píldoras"):text.index("## Glosario")], flags=re.MULTILINE)
    questions = re.findall(r"^[1-6]\. ", text[text.index("## Preguntas de preparación"):text.index("## Referentes")], flags=re.MULTILINE)
    referents = re.findall(r"^\*\*[^*]+\.\*\*", text[text.index("## Referentes"):text.index("## Referencias base")], flags=re.MULTILINE)
    reference_entries = re.findall(r"^- ", references, flags=re.MULTILINE)
    urls = re.findall(r"https://[^\s)]+", references)
    recent = re.findall(r"\(202[2-6]\)", references)
    prohibited = re.findall(r"\b(?:tú|vos|usted|seleccioná|elegí|hacé|podés|deberías)\b", text, flags=re.IGNORECASE)
    placeholders = re.findall(r"\b(?:TBD|XXX|TODO)\b|\blorem\b|\[[^\]]+\]", text)
    dashes = re.findall(r"[—–]", body)

    checks = [
        result("source_exists", source.is_file(), str(source.relative_to(ROOT))),
        result("substantive_word_floor", len(words(substantive)) >= 6000, len(words(substantive))),
        result("total_word_count", len(words(text)) >= 6500, len(words(text))),
        result("required_architecture", all(x in sections for x in config["required_sections"]), sections),
        result("three_movements", sum(x.startswith("Movimiento ") for x in sections) == 3, [x for x in sections if x.startswith("Movimiento ")]),
        result("complete_concept_units", sum(x["words"] >= 150 for x in unit_lengths) > len(unit_lengths) / 2, unit_lengths),
        result("instrument_fields", len(re.findall(r"^\d+\. \*\*", instrument, flags=re.MULTILINE)) == config["instrument_fields"], config["instrument_fields"]),
        result("five_pills", len(pills) == 5, len(pills)),
        result("six_questions", len(questions) == 6, len(questions)),
        result("six_referents", len(referents) == 6, len(referents)),
        result("reference_depth", len(reference_entries) >= 12, len(reference_entries)),
        result("recent_literature", len(recent) >= config.get("recent_reference_floor", 3), len(recent)),
        result("reference_urls", len(urls) >= 8, len(urls)),
        result("all_references_anchored_in_body", all(anchor in body for anchor in config["reference_anchors"].values()), {k: v in body for k, v in config["reference_anchors"].items()}),
        result("cross_document_uniqueness", not repeated, repeated[:20]),
        result("boundary_terms", all(term in text for term in config["required_terms"]), config["required_terms"]),
        result("impersonal_register", not prohibited, prohibited),
        result("no_placeholders", not placeholders, placeholders),
        result("no_incidental_dashes_in_prose", not dashes, dashes),
        result("content_only_package", not list(package.rglob("*.pdf")) and not list(package.rglob("*.html")) and not list(package.rglob("*.css")), "no PDF, HTML or CSS"),
    ]
    source_hash = hashlib.sha256(text.encode()).hexdigest()
    report = {
        "document": code,
        "title": config["title"],
        "stage": "content-canonical-v1",
        "language": "es-AR",
        "source": str(source.relative_to(ROOT)),
        "sha256": source_hash,
        "bytes": source.stat().st_size,
        "words_total": len(words(text)),
        "words_substantive": len(words(substantive)),
        "source_blocks": len(source_blocks),
        "references": len(reference_entries),
        "urls": len(urls),
        "results": checks,
        "overall": "pass" if all(x["result"] == "pass" for x in checks) else "fail",
    }
    (package / "provenance").mkdir(exist_ok=True)
    (package / "provenance" / "integrity-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    (package / "source-manifest.json").write_text(json.dumps({
        "document": code,
        "stage": "content-canonical-v1",
        "source": config["source"],
        "source_sha256": source_hash,
        "eligible_blocks": source_blocks,
        "block_count": len(source_blocks),
    }, ensure_ascii=False, indent=2) + "\n")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packages", nargs="+", type=Path)
    args = parser.parse_args()
    reports = [audit(ROOT / p if not p.is_absolute() else p) for p in args.packages]
    print(json.dumps(reports, ensure_ascii=False, indent=2))
    return 0 if all(r["overall"] == "pass" for r in reports) else 1


if __name__ == "__main__":
    raise SystemExit(main())
