#!/usr/bin/env python3
"""Audit METSI canonical content for N31 through N36."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPECTED = {
    31: "Reglas, predicción, generación y agencia: cuándo la IA es pertinente",
    32: "Evaluar tareas, cobertura, severidad, desigualdad, robustez y supervisión",
    33: "Gobierno vivo de IA: inventario, ownership, datos, proveedores, cambios, incidentes, reparación y retiro",
    34: "Reconstruir la cadena completa: del problema y la evidencia a la operación y el gobierno",
    35: "Comunicar, defender y transferir criterios sin copiar soluciones",
    36: "Práctica reflexiva: aprender de decisiones, errores, sorpresas y asistencia de IA",
}
REQUIRED = ["Pregunta profesional", "Hotel Horizonte", "Tesis", "Del cierre anterior al nuevo avance",
            "Tradiciones y marcos utilizados", "Instrumento HH", "Caso de transferencia", "Contraejemplo",
            "Errores frecuentes", "Consecuencias profesionales", "Límites y tensiones", "Síntesis",
            "Cinco píldoras para recordar", "Glosario esencial", "Preguntas de preparación", "Referentes",
            "Referencias base"]


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]+", text.lower())


def substantive(text: str) -> int:
    return len(words(text.split("## Cinco píldoras para recordar", 1)[0]))


def shingles(text: str, n: int = 12) -> set[tuple[str, ...]]:
    seq = words(text.split("## Errores frecuentes", 1)[0])
    return {tuple(seq[i:i+n]) for i in range(max(0, len(seq)-n+1))}


def main() -> None:
    records, bodies, ok_all = [], {}, True
    for number, title in EXPECTED.items():
        code = f"N{number:02d}"
        package = ROOT / f"{code}-content-canonical"
        source = next((package / "source").glob("*.md"))
        text = source.read_text(encoding="utf-8")
        body, reference_part = text.split("## Referencias base", 1)
        refs = [line[2:] for line in reference_part.splitlines() if line.startswith("- ")]
        authors = [ref.split(" (", 1)[0] for ref in refs]
        manifest = json.loads((package / "source-manifest.json").read_text(encoding="utf-8"))
        digest = hashlib.sha256(text.encode()).hexdigest()
        transition = "## Después de N36" if number == 36 else f"## De N{number:02d} a N{number+1:02d}"
        checks = {
            "title": text.startswith(f"# {code} · {title}"),
            "substantive_floor": substantive(text) >= 6000,
            "required_sections": all(item in text for item in REQUIRED),
            "transition": transition in text,
            "three_movements": len(re.findall(r"^## Movimiento [123]", text, re.M)) == 3,
            "twelve_units": len(re.findall(r"^### ", text.split("## Movimiento 1",1)[1].split("### Instrumento",1)[0], re.M)) == 12,
            "five_pills": len(re.findall(r"^[1-5]\. ", text.split("## Cinco píldoras",1)[1].split("## Glosario",1)[0], re.M)) == 5,
            "six_questions": len(re.findall(r"^[1-6]\. ", text.split("## Preguntas",1)[1].split("## Referentes",1)[0], re.M)) == 6,
            "six_referents": len(re.findall(r"^\*\*[^\n]+\.\*\*", text.split("## Referentes",1)[1].split("## Referencias",1)[0], re.M)) == 6,
            "references": len(refs) >= 10,
            "reference_anchors": all(author in body for author in authors),
            "no_placeholders": not re.search(r"\b(?:TBD|LOREM|XXX)\b|\[(?:pendiente|completar|insertar)", text, re.I),
            "no_incidental_dashes": "—" not in body and "–" not in body,
            "impersonal_register": not re.search(r"\b(?:vos|usted|ustedes|tu|tus|te)\b", body, re.I),
            "manifest_hash": manifest.get("source_sha256") == digest,
            "hotel_continuity": f"HH-{number:02d}" in text,
        }
        passed = all(checks.values())
        ok_all &= passed
        bodies[number] = body
        records.append({"document": code, "title": title, "result": "PASS" if passed else "FAIL",
                        "words_total": len(words(text)), "words_substantive": substantive(text),
                        "references": len(refs), "checks": checks})
    overlap = []
    for left in EXPECTED:
        for right in EXPECTED:
            if right <= left:
                continue
            a, b = shingles(bodies[left]), shingles(bodies[right])
            ratio = len(a & b) / max(1, min(len(a), len(b)))
            row = {"pair": f"N{left:02d}-N{right:02d}", "ratio": round(ratio, 4), "pass": ratio < 0.22}
            overlap.append(row); ok_all &= row["pass"]
    result = {"scope":"METSI Blocks G-H N31-N36", "result":"PASS" if ok_all else "FAIL",
              "documents":records, "cross_document_overlap":overlap}
    (ROOT/"BLOCKS-G-H-CONTENT-AUDIT.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines=["# Auditoría de contenido · Bloques G y H","",f"Resultado global: **{result['result']}**.",""]
    for item in records:
        lines += [f"## {item['document']} · {item['title']}","",f"Resultado: **{item['result']}**. Palabras sustantivas: {item['words_substantive']}. Referencias: {item['references']}.",""]
        lines += [f"- {k}: {'PASS' if v else 'FAIL'}" for k,v in item["checks"].items()]
        lines.append("")
    lines += ["## Solapamiento transversal",""]+[f"- {r['pair']}: {r['ratio']:.4f}, {'PASS' if r['pass'] else 'FAIL'}." for r in overlap]
    lines += ["","## Red team","",
              "- N31 no debe convertirse en catálogo de herramientas: decide pertinencia frente a alternativas sin IA.",
              "- N32 no debe reducirse a métricas: conecta cobertura, severidad, desigualdad y supervisión con autonomía.",
              "- N33 no debe quedar en principios: exige inventario vivo, autoridad, incidentes, reparación y retiro.",
              "- N34 no debe resumir el curso: reconstruye una cadena de decisiones y contradicciones verificables.",
              "- N35 no debe enseñar persuasión: conserva evidencia y permite apropiación sin copiar soluciones.",
              "- N36 no debe cerrar con autoevaluación genérica: modifica teorías de acción y prácticas observables.",""]
    (ROOT/"BLOCKS-G-H-CONTENT-AUDIT.md").write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps({"result":result["result"],"documents":{x["document"]:x["result"] for x in records},"max_overlap":max(r["ratio"] for r in overlap)},ensure_ascii=False))
    raise SystemExit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
