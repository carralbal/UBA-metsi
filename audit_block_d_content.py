#!/usr/bin/env python3
"""Deterministic structural and integrity audit for METSI Block D canonical content."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPECTED = {
    17: "Lógicas predictivas, iterativas, incrementales, adaptativas y experimentales",
    18: "Legado, regulación y documentación como valor, restricción y evidencia",
    19: "Alternativas de realización: configurar, integrar, construir y no automatizar",
    20: "Estrategia metodológica: tailoring, hitos y condiciones de salida",
}
REQUIRED = [
    "Pregunta profesional", "Hotel Horizonte", "Tesis", "Del cierre anterior al nuevo avance",
    "Tradiciones y marcos utilizados en el argumento", "Errores frecuentes",
    "Consecuencias profesionales", "Límites y tensiones", "Síntesis",
    "Cinco píldoras para recordar", "Glosario esencial", "Preguntas de preparación",
    "Referentes", "Referencias base",
]


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]+", text)


def substantive(text: str) -> int:
    stop = text.find("## Cinco píldoras para recordar")
    return len(words(text[: stop if stop >= 0 else None]))


def main() -> None:
    results = []
    ok_all = True
    for number, title in EXPECTED.items():
        code = f"N{number:02d}"
        pkg = ROOT / f"{code}-content-canonical"
        source = next((pkg / "source").glob("*.md"))
        text = source.read_text(encoding="utf-8")
        manifest = json.loads((pkg / "source-manifest.json").read_text(encoding="utf-8"))
        report = json.loads((pkg / "provenance" / "integrity-report.json").read_text(encoding="utf-8"))
        refs = text.split("## Referencias base", 1)[1]
        ref_lines = [line[2:] for line in refs.splitlines() if line.startswith("- ")]
        body = text.split("## Referencias base", 1)[0]
        checks = {
            "title": text.startswith(f"# {code} · {title}"),
            "substantive_floor": substantive(text) >= 6000,
            "three_movements": len(re.findall(r"^## Movimiento [123]", text, re.M)) == 3,
            "required_sections": all(label in text for label in REQUIRED),
            "five_pills": len(re.findall(r"^[1-5]\. ", text.split("## Cinco píldoras para recordar", 1)[1].split("## Glosario esencial", 1)[0], re.M)) == 5,
            "six_questions": len(re.findall(r"^[1-6]\. ", text.split("## Preguntas de preparación", 1)[1].split("## Referentes", 1)[0], re.M)) == 6,
            "six_referents": len(re.findall(r"^\*\*[^\n]+\.\*\*", text.split("## Referentes", 1)[1].split("## Referencias base", 1)[0], re.M)) == 6,
            "references": len(ref_lines) >= 10,
            "reference_anchors": all(ref.split(" (", 1)[0] in body for ref in ref_lines),
            "no_placeholders": not re.search(r"\b(?:TBD|TODO|LOREM|XXX)\b|\[(?:pendiente|completar|insertar)[^\]]*\]", text),
            "no_incidental_dashes": "—" not in body and "–" not in body,
            "rioplatense_impersonal": not re.search(r"\b(?:vos|usted|ustedes|tu|tus|te)\b", text, re.I),
            "manifest_hash": manifest.get("source_sha256") == hashlib.sha256(text.encode()).hexdigest(),
            "integrity_hash": report.get("checks", {}).get("source_sha256") == hashlib.sha256(text.encode()).hexdigest(),
        }
        ok = all(checks.values())
        ok_all &= ok
        results.append({
            "document": code,
            "title": title,
            "words_total": len(words(text)),
            "words_substantive": substantive(text),
            "references": len(ref_lines),
            "checks": checks,
            "result": "PASS" if ok else "FAIL",
        })
    out = {"scope": "METSI Block D N17-N20", "result": "PASS" if ok_all else "FAIL", "documents": results}
    (ROOT / "BLOCK-D-CONTENT-AUDIT.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Auditoría de contenido · Bloque D", "", f"Resultado global: **{out['result']}**.", ""]
    for item in results:
        lines += [f"## {item['document']} · {item['title']}", "", f"Resultado: **{item['result']}**. Palabras sustantivas: {item['words_substantive']}. Referencias: {item['references']}.", ""]
        lines += [f"- {name}: {'PASS' if value else 'FAIL'}" for name, value in item["checks"].items()]
        lines.append("")
    lines += ["## Auditoría transversal", "", "La progresión quedó cerrada como N17 lógicas de intervención, N18 obligaciones y legado, N19 opciones de realización y N20 estrategia metodológica situada. Cada documento recibe un paquete HH completo del anterior y entrega otro al siguiente, sin reabrir el objeto ya cerrado.", "", "La arquitectura didáctica común se conserva deliberadamente para dar continuidad de colección. Los ejemplos, instrumentos, casos de transferencia, contraejemplos, errores, glosarios, preguntas, referentes y fuentes son específicos de cada Núcleo.", ""]
    (ROOT / "BLOCK-D-CONTENT-AUDIT.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))
    raise SystemExit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
