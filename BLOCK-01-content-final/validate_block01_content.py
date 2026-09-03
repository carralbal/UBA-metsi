#!/usr/bin/env python3
"""Auditoría transversal del contenido canónico N01 a N10."""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
REPORT = OUT / "provenance" / "block-integrity-report.json"
MANIFEST = OUT / "block-manifest.json"

DOCS = {
    "N01": "N01-content-final/source/N01_metodologia_sin_recetas-content-final.md",
    "N02": "N02-content-final/source/N02_el_sistema_no_cabe_en_una_aplicacion-content-final.md",
    "N03": "N03-content-final/source/N03_fronteras_retroalimentacion_y_efectos-content-final.md",
    "N04": "N04-content-final/source/N04_hechos_sintomas_relatos_hipotesis_y_decisiones-content-final.md",
    "N05": "N05-content-final/source/N05_actores_afectados_poder_y_perspectivas-content-final.md",
    "N06": "N06-content-final/source/N06_discovery_como_reduccion_de_incertidumbre-content-final.md",
    "N07": "N07-content-final/source/N07_entrevistar_no_es_pedir_requisitos-content-final.md",
    "N08": "N08-content-final/source/N08_observar_el_trabajo_invisible-content-final.md",
    "N09": "N09-content-final/source/N09_experiencia_accesibilidad_y_adopcion-content-final.md",
    "N10": "N10-content-final/source/N10_construir_el_problema_y_outcomes-content-final.md",
}

FUNCTIONS = {
    "N01": "Sitúa para qué sirve una metodología cuando no puede garantizar el resultado.",
    "N02": "Muestra que un sistema de información no cabe en una aplicación.",
    "N03": "Convierte la frontera en una hipótesis con consecuencias y examina retroalimentación y efectos no intencionales.",
    "N04": "Separa hechos, señales, relatos, hipótesis, supuestos y decisiones para reconstruir la evidencia.",
    "N05": "Reemplaza al interesado genérico por actores con poder, exposición, voz y capacidad de reparación.",
    "N06": "Diseña discovery como una inversión proporcional para reducir incertidumbre.",
    "N07": "Transforma la entrevista en reconstrucción de episodios y contraste de explicaciones.",
    "N08": "Observa trabajo prescripto, real, adaptativo e invisible.",
    "N09": "Estudia experiencia de principio a fin, accesibilidad, fricción y adopción.",
    "N10": "Integra el bloque en un encuadre con mecanismos rivales, outcomes, restricciones y condiciones de revisión.",
}


def words(text: str) -> list[str]:
    return re.findall(r"\b[\wÁÉÍÓÚÜÑáéíóúüñ]+(?:[-‑][\wÁÉÍÓÚÜÑáéíóúüñ]+)*\b", text)


def check(name: str, passed: bool, evidence: object) -> dict[str, object]:
    return {"check": name, "result": "pass" if passed else "fail", "evidence": evidence}


def main() -> int:
    documents = []
    bodies: dict[str, str] = {}
    all_paragraphs: dict[str, list[dict[str, object]]] = defaultdict(list)
    all_ngrams: dict[tuple[str, ...], list[tuple[str, int]]] = defaultdict(list)
    for index, (code, relative) in enumerate(DOCS.items(), 1):
        source = ROOT / relative
        text = source.read_text(encoding="utf-8")
        body, references = text.split("## Referencias base", 1)
        substantive = text[text.index("## Tesis") : text.index("## Cinco píldoras para recordar")]
        integrity_path = ROOT / f"{code}-content-final/provenance/integrity-report.json"
        audit_path = ROOT / f"{code}-content-final/CONTENT-AUDIT.md"
        integrity = json.loads(integrity_path.read_text(encoding="utf-8"))
        audit = audit_path.read_text(encoding="utf-8")
        score_match = re.findall(r"\*\*([0-4][0-9])/40\*\*", audit)
        score = int(score_match[-1]) if score_match else 0
        current_hash = hashlib.sha256(text.encode()).hexdigest()
        bodies[code] = body
        reference_count = len(re.findall(r"^- ", references, flags=re.MULTILINE))
        url_count = len(re.findall(r"https://[^\s)]+", references))
        own_hh = f"HH-{index:02d}"
        documents.append({
            "order": index, "document": code, "block": "A" if index <= 4 else "B",
            "canonical_function": FUNCTIONS[code], "source": relative,
            "sha256": current_hash, "bytes": source.stat().st_size,
            "words_total": len(words(text)), "words_substantive": len(words(substantive)),
            "references": reference_count, "urls": url_count, "own_artifact": own_hh,
            "own_artifact_mentions": body.count(own_hh), "individual_validator": integrity["overall"],
            "integrity_hash_matches": current_hash == integrity["sha256"], "human_score": score,
        })
        for paragraph_number, paragraph in enumerate(re.split(r"\n\s*\n", body), 1):
            normalized = " ".join(word.lower() for word in words(paragraph))
            if len(normalized.split()) >= 30 and not paragraph.startswith(("#", "- ", "|")):
                all_paragraphs[normalized].append({"document": code, "paragraph": paragraph_number})
        normalized_words = [word.lower() for word in words(body)]
        for position in range(max(0, len(normalized_words) - 23)):
            all_ngrams[tuple(normalized_words[position : position + 24])].append((code, position))

    duplicate_paragraphs = [{"text": text[:160], "locations": locations} for text, locations in all_paragraphs.items() if len({location["document"] for location in locations}) > 1]
    duplicate_ngrams = [{"text": " ".join(ngram), "locations": locations} for ngram, locations in all_ngrams.items() if len({location[0] for location in locations}) > 1]
    adjacency = {}
    for index in range(1, 10):
        code = f"N{index:02d}"
        next_code = f"N{index + 1:02d}"
        adjacency[f"{code}_to_{next_code}"] = next_code in bodies[code] and code in bodies[next_code]
    own_artifacts = {row["document"]: row["own_artifact_mentions"] > 0 for row in documents}
    results = [
        check("ten_canonical_documents", len(documents) == 10, len(documents)),
        check("all_individual_validators_pass", all(row["individual_validator"] == "pass" for row in documents), {row["document"]: row["individual_validator"] for row in documents}),
        check("all_integrity_hashes_match", all(row["integrity_hash_matches"] for row in documents), {row["document"]: row["integrity_hash_matches"] for row in documents}),
        check("all_substantive_word_floors_pass", all(row["words_substantive"] >= 6000 for row in documents), {row["document"]: row["words_substantive"] for row in documents}),
        check("human_depth_gate", all(row["human_score"] >= 35 for row in documents), {row["document"]: row["human_score"] for row in documents}),
        check("complete_hh01_hh10_sequence", all(own_artifacts.values()), own_artifacts),
        check("bidirectional_adjacent_handoffs", all(adjacency.values()), adjacency),
        check("block_a_n01_n04", [row["document"] for row in documents if row["block"] == "A"] == ["N01", "N02", "N03", "N04"], "N01-N04"),
        check("block_b_n05_n10", [row["document"] for row in documents if row["block"] == "B"] == ["N05", "N06", "N07", "N08", "N09", "N10"], "N05-N10"),
        check("n10_closes_block_one", all(term in bodies["N10"] for term in ("cierra el Bloque 1", "Así termina el Bloque 1", "HH-10")), "declared"),
        check("n04_n11_distinction", all(term in bodies["N10"] for term in ("N04 ya enseñó", "N11 retomará esa exigencia desde otra unidad", "dato como representación")), "declared"),
        check("no_cross_document_duplicate_paragraphs", not duplicate_paragraphs, duplicate_paragraphs),
        check("no_cross_document_repeated_24_word_sequences", not duplicate_ngrams, duplicate_ngrams[:20]),
        check("reference_apparatus_present", all(row["references"] >= 10 for row in documents), {row["document"]: row["references"] for row in documents}),
        check("content_only_block_package", not list(OUT.rglob("*.pdf")) and not list(OUT.rglob("*.html")) and not list(OUT.rglob("*.css")), "no composition artifacts"),
    ]
    totals = {
        "words_total": sum(row["words_total"] for row in documents),
        "words_substantive": sum(row["words_substantive"] for row in documents),
        "reference_entries": sum(row["references"] for row in documents),
        "urls": sum(row["urls"] for row in documents),
    }
    report = {"scope": "METSI Block 1, N01-N10", "stage": "content-final", "documents": documents, "totals": totals, "results": results, "overall": "pass" if all(row["result"] == "pass" for row in results) else "fail"}
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = {"scope": "METSI Block 1", "stage": "content-final", "language": "es-AR", "documents": documents, "totals": totals, "next_document": "N11", "next_block": "Block C · Modelar sólo lo que ayuda a decidir", "excluded_artifacts": ["PDF", "HTML", "CSS", "photography", "illustration", "layout"]}
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["overall"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
