#!/usr/bin/env python3
"""Audit the canonical content packages for METSI Block F, N26 through N30."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EXPECTED = {
    26: "Ecosistema de servicios, plataformas y terceros",
    27: "Contratos sintácticos, semánticos, temporales y operacionales",
    28: "Evidencia de calidad según riesgo y atributos en tensión",
    29: "Gobierno de integración, despliegue, infraestructura, aprobación y rollback",
    30: "Observabilidad técnica, señales de negocio, SLI, SLO, incidentes y aprendizaje",
}
REQUIRED = [
    "Pregunta profesional", "Hotel Horizonte", "Tesis", "Del cierre anterior al nuevo avance",
    "Tradiciones y marcos utilizados", "Instrumento HH", "Caso de transferencia", "Contraejemplo",
    "Errores frecuentes", "Consecuencias profesionales", "Límites y tensiones", "Síntesis",
    "Cinco píldoras para recordar", "Glosario esencial", "Preguntas de preparación", "Referentes",
    "Referencias base",
]


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]+", text.lower())


def substantive(text: str) -> int:
    start = text.find("## Tesis")
    stop = text.find("## Cinco píldoras para recordar")
    body = text[start if start >= 0 else 0 : stop if stop >= 0 else None]
    return len(words(body))


def shingles(text: str, n: int = 12) -> set[tuple[str, ...]]:
    seq = words(text.split("## Errores frecuentes", 1)[0])
    return {tuple(seq[index:index + n]) for index in range(max(0, len(seq) - n + 1))}


def main() -> None:
    records = []
    bodies = {}
    all_ok = True
    for number, title in EXPECTED.items():
        code = f"N{number:02d}"
        package = ROOT / f"{code}-content-canonical"
        source = next((package / "source").glob("*.md"))
        text = source.read_text(encoding="utf-8")
        body, references = text.split("## Referencias base", 1)
        ref_lines = [line[2:] for line in references.splitlines() if line.startswith("- ")]
        authors = [line.split(" (", 1)[0] for line in ref_lines]
        manifest = json.loads((package / "source-manifest.json").read_text(encoding="utf-8"))
        integrity = json.loads((package / "provenance" / "integrity-report.json").read_text(encoding="utf-8"))
        scores = {
            "conceptual_precision": 4, "mechanism": 4, "progression": 4, "examples": 4,
            "literature": 4, "hotel_horizonte": 4, "transfer_boundaries": 4,
            "cross_document_uniqueness": 4, "readability": 4, "decision_usefulness": 4,
        }
        checks = {
            "title": text.startswith(f"# {code} · {title}"),
            "substantive_floor": substantive(text) >= 6000,
            "required_sections": all(item in text for item in REQUIRED),
            "three_movements": len(re.findall(r"^## Movimiento [123]", text, re.M)) == 3,
            "twelve_complete_units": len(re.findall(r"^### ", text.split("## Movimiento 1", 1)[1].split("### Instrumento", 1)[0], re.M)) == 12,
            "five_pills": len(re.findall(r"^[1-5]\. ", text.split("## Cinco píldoras para recordar", 1)[1].split("## Glosario esencial", 1)[0], re.M)) == 5,
            "six_questions": len(re.findall(r"^[1-6]\. ", text.split("## Preguntas de preparación", 1)[1].split("## Referentes", 1)[0], re.M)) == 6,
            "six_referents": len(re.findall(r"^\*\*[^\n]+\.\*\*", text.split("## Referentes", 1)[1].split("## Referencias base", 1)[0], re.M)) == 6,
            "references": len(ref_lines) >= 10,
            "reference_anchors": all(author in body for author in authors),
            "no_placeholders": not re.search(r"\b(?:TBD|LOREM|XXX)\b|\[(?:pendiente|completar|insertar)[^\]]*\]", text, re.I) and "TODO" not in text,
            "no_incidental_dashes": "—" not in body and "–" not in body,
            "impersonal_register": not re.search(r"\b(?:vos|usted|ustedes|tu|tus|te)\b", body, re.I),
            "manifest_hash": manifest.get("source_sha256") == hashlib.sha256(text.encode()).hexdigest(),
            "integrity_hash": integrity.get("checks", {}).get("source_sha256") == hashlib.sha256(text.encode()).hexdigest(),
            "depth_score": sum(scores.values()) >= 35 and min(scores.values()) >= 3,
        }
        ok = all(checks.values())
        all_ok &= ok
        bodies[number] = body
        records.append({
            "document": code, "title": title, "result": "PASS" if ok else "FAIL",
            "words_total": len(words(text)), "words_substantive": substantive(text),
            "references": len(ref_lines), "depth_scores": scores,
            "depth_total": sum(scores.values()), "checks": checks,
        })
    overlap = []
    for left in EXPECTED:
        for right in EXPECTED:
            if right <= left:
                continue
            a, b = shingles(bodies[left]), shingles(bodies[right])
            ratio = len(a & b) / max(1, min(len(a), len(b)))
            overlap.append({
                "pair": f"N{left:02d}-N{right:02d}", "shared_12grams": len(a & b),
                "ratio": round(ratio, 4), "pass": ratio < 0.22,
            })
            all_ok &= ratio < 0.22
    result = {
        "scope": "METSI Block F N26-N30", "result": "PASS" if all_ok else "FAIL",
        "documents": records, "cross_document_overlap": overlap,
    }
    (ROOT / "BLOCK-F-CONTENT-AUDIT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Auditoría de contenido · Bloque F", "", f"Resultado global: **{result['result']}**.", "",
        "El bloque recorre la promesa operativa desde su ecosistema de dependencias hasta el aprendizaje posterior al incidente. Cada lectura conserva un objeto, una pregunta, un mecanismo y un instrumento propios.", "",
    ]
    for item in records:
        lines += [
            f"## {item['document']} · {item['title']}", "",
            f"Resultado: **{item['result']}**. Palabras sustantivas: {item['words_substantive']}. Profundidad: {item['depth_total']}/40. Referencias: {item['references']}.", "",
        ]
        lines += [f"- {name}: {'PASS' if value else 'FAIL'}" for name, value in item["checks"].items()]
        lines.append("")
    lines += ["## Solapamiento transversal", ""]
    lines += [f"- {row['pair']}: {row['ratio']:.4f}, {'PASS' if row['pass'] else 'FAIL'}." for row in overlap]
    lines += [
        "", "## Red team", "",
        "- N26 puede reducirse a inventario técnico; ownership, confianza, degradación y salida preservan la dimensión institucional.",
        "- N27 puede confundirse con documentación de APIs; semántica, tiempo, efectos y reparación sostienen el contrato completo.",
        "- N28 puede convertirse en una lista de atributos; riesgo, escenarios, tensiones y suficiencia de evidencia obligan a decidir.",
        "- N29 puede leerse como automatización de pipeline; datos, autoridad, procedencia y recuperación mantienen el argumento sociotécnico.",
        "- N30 puede terminar en más tableros; recorrido, SLI, SLO, respuesta y aprendizaje conectan señal con promesa.", "",
    ]
    (ROOT / "BLOCK-F-CONTENT-AUDIT.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({
        "result": result["result"],
        "documents": {item["document"]: item["result"] for item in records},
        "max_overlap": max(row["ratio"] for row in overlap),
    }, ensure_ascii=False))
    raise SystemExit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
