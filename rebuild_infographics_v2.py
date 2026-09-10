#!/usr/bin/env python3
"""Create the METSI infographic v2 review candidates selected by the author."""

from __future__ import annotations

import importlib.util
import json
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "editorial-standard" / "infographic-rebuild-candidates-v2"
RENDERER = ROOT / "editorial-standard" / "metsi-build-infographics" / "scripts" / "render_infographic.py"

PACKAGES = {
    0: "N00-v2-candidate",
    7: "N07-v9-final",
    8: "N08-v9-final",
    9: "N09-v9-final",
    **{n: f"N{n:02d}-v6-editorial" for n in range(11, 37)},
}

FLOW_DOCS = {0, 7, 8, 9, 12, 13, 14, 17, 20, 23, 25, 29, 34, 36}

MANUAL_LABELS = {
    0: [
        "Bloque A · Ver el sistema antes de recetar",
        "Bloque B · Investigar antes de cerrar el problema",
        "Bloque C · Modelar sólo lo que ayuda a decidir",
        "Bloque D · Diseñar una estrategia situada",
        "Bloque E · Pasar de entregar cosas a gobernar capacidades",
        "Bloque F · Sostener la promesa en operación",
        "Bloque G · Incorporar IA sin delegar el juicio",
        "Bloque H · Integrar, defender, transferir y seguir aprendiendo",
    ],
    9: [
        "Propósito · Confirmar compatibilidad",
        "Condiciones · Movilidad, teclado y conectividad",
        "Señal · Etiqueta adaptada",
        "Acción · Reservar y confirmar",
        "Trabajo · Verificar atributos y disponibilidad",
        "Evidencia · Procedencia, vigencia y autoridad",
        "Modo de falla · Una promesa falsa",
        "Alternativa y reparación · Verificación, plazo y respuesta trazable",
    ],
}


def load_renderer():
    spec = importlib.util.spec_from_file_location("metsi_render_infographic", RENDERER)
    if spec is None or spec.loader is None:
        raise RuntimeError("No se pudo cargar el renderer METSI")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def xml_title(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"<title[^>]*>(.*?)</title>", raw, re.S | re.I)
    return re.sub(r"<[^>]+>", "", match.group(1)).strip() if match else ""


def source_entries(n: int) -> list[dict]:
    package = ROOT / PACKAGES[n]
    svg_files = sorted((package / "diagrams").glob("*.svg"))
    top_manifest = package / "diagrams" / "content-manifest.json"
    diagram_records: dict[str, dict] = {}
    if top_manifest.exists():
        payload = json.loads(top_manifest.read_text(encoding="utf-8"))
        for record in payload.get("diagrams", []):
            diagram_records[Path(record.get("file", "")).name] = record
    entries = []
    for svg in svg_files:
        record = diagram_records.get(svg.name, {})
        labels = record.get("labels") or []
        title = record.get("title") or xml_title(svg)
        claim = record.get("claim") or ""
        if not labels:
            metadata = svg.with_suffix(".json")
            if metadata.exists():
                data = json.loads(metadata.read_text(encoding="utf-8"))
                labels = data.get("labels", [])
                title = title or (data.get("source_headings") or [svg.stem])[0]
                claim = data.get("alt", "")
        entries.append({"source": svg, "title": title or svg.stem, "labels": labels, "claim": claim})
    return entries


def select_evenly(labels: list[str], limit: int) -> list[str]:
    if len(labels) <= limit:
        return labels
    indexes = []
    for i in range(limit):
        idx = round(i * (len(labels) - 1) / (limit - 1))
        if idx not in indexes:
            indexes.append(idx)
    return [labels[i] for i in indexes]


def build_spec(n: int, entry: dict, index: int, total: int) -> dict:
    is_flow = n in FLOW_DOCS or (n == 30 and index == 2)
    if n in MANUAL_LABELS:
        labels = MANUAL_LABELS[n]
    elif n in {7, 8, 9}:
        labels = select_evenly(entry["labels"], 8)
    else:
        labels = select_evenly(entry["labels"], 6)
    items = [{"number": f"{i:02d}", "title": label} for i, label in enumerate(labels, 1)]
    title = "El recorrido completo: ocho bloques, una capacidad acumulativa" if n == 0 else entry["title"]
    title = re.sub(rf"^N{n:02d}\s*[·,:-]\s*", "", title, flags=re.I)
    if n == 30 and total > 1:
        title = f"{title} · pieza {index}"
    spec = {
        "type": "flow" if is_flow else "layers",
        "model": 1 if is_flow else 5,
        "title": title,
        "width": 1344,
        "style": "outline",
        "items": items,
        "alt": entry["claim"] or f"Infografía de {title} con {len(items)} conceptos relacionados.",
    }
    if is_flow:
        spec["orientation"] = "matrix" if n == 0 else "zigzag"
    return spec


def add_volt_signature(svg: str) -> str:
    signature = '<path d="M121 32 H211 L200 47 H110 Z" fill="#CFFF00"/>'
    return svg.replace("</defs>", "</defs>" + signature, 1)


def validate_svg(svg: str, expected_items: int) -> list[str]:
    warnings = []
    fonts = set(re.findall(r'font-family="([^"]+)"', svg))
    if fonts != {"Inter, Arial, sans-serif"}:
        warnings.append(f"font-family inesperada: {sorted(fonts)}")
    allowed = {"#272525", "#4D4D4D", "#FFFFFF", "#E6E6E6", "#CCCCCC", "#CFFF00"}
    colors = {c.upper() for c in re.findall(r"#[0-9A-Fa-f]{6}", svg)}
    foreign = sorted(colors - {c.upper() for c in allowed})
    if foreign:
        warnings.append(f"colores fuera de paleta: {foreign}")
    if svg.count('font-weight="700"') < expected_items:
        warnings.append("faltan encabezados de nodos")
    if any(token in svg for token in ['fill="#272525"/>', 'fill="#272525">']):
        warnings.append("posible bloque oscuro")
    return warnings


def main() -> None:
    renderer = load_renderer()
    summary = []
    for n in sorted(PACKAGES):
        entries = source_entries(n)
        target_dir = OUT / f"N{n:02d}"
        target_dir.mkdir(parents=True, exist_ok=True)
        records = []
        for index, entry in enumerate(entries, 1):
            source = entry["source"]
            spec = build_spec(n, entry, index, len(entries))
            spec_name = source.stem + "-v2.spec.json"
            svg_name = source.stem + "-v2.svg"
            spec_path = target_dir / spec_name
            svg_path = target_dir / svg_name
            spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
            svg = add_volt_signature(renderer.render(spec))
            svg_path.write_text(svg, encoding="utf-8")
            warnings = validate_svg(svg, len(spec["items"]))
            record = {
                "code": f"N{n:02d}" + (chr(64 + index) if len(entries) > 1 else ""),
                "model": spec["model"],
                "title": spec["title"],
                "source": source.relative_to(ROOT).as_posix(),
                "spec": spec_path.relative_to(ROOT).as_posix(),
                "svg": svg_path.relative_to(ROOT).as_posix(),
                "item_count": len(spec["items"]),
                "warnings": warnings,
            }
            records.append(record)
            summary.append(record)
            alt_name = source.stem + "-v2-alt-text.md"
            (target_dir / alt_name).write_text(spec["alt"].strip() + "\n", encoding="utf-8")
        (target_dir / "manifest.json").write_text(json.dumps({"document": f"N{n:02d}", "status": "candidate-for-author-review", "pieces": records}, ensure_ascii=False, indent=2), encoding="utf-8")
    warnings = [w for item in summary for w in item["warnings"]]
    report = {
        "status": "PASS" if not warnings else "FAIL",
        "documents": len(PACKAGES),
        "pieces": len(summary),
        "model_1": sum(1 for item in summary if item["model"] == 1),
        "model_5": sum(1 for item in summary if item["model"] == 5),
        "warnings": warnings,
        "items": summary,
    }
    (OUT / "QA.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ["status", "documents", "pieces", "model_1", "model_5", "warnings"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
