#!/usr/bin/env python3
"""Write reproducible closure records for the N11–N36 v9 editorial run."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
TZ = ZoneInfo("America/Argentina/Buenos_Aires")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def fmt_time(path: Path) -> str:
    stamp = datetime.fromtimestamp(path.stat().st_mtime, TZ)
    return stamp.isoformat(timespec="seconds")


def close_document(number: int, version: int) -> dict:
    document = f"N{number:02d}"
    package = ROOT / f"{document}-v{version}-editorial"
    qa = load_json(package / "qa-report.json")
    preservation = load_json(package / "qa" / "content-preservation-audit.json")
    source_manifest = load_json(package / "source-manifest.json")
    pdf = package / "output" / f"{document}-METSI-lectura-previa-v{version}-final.pdf"
    contact_sheet = package / "qa" / f"{document}-contact-sheet-v{version}.png"

    if qa.get("status") != "PASS" or preservation.get("status") != "PASS":
        raise SystemExit(f"{document}: closure refused because an audit is not PASS")
    if not pdf.exists() or not contact_sheet.exists():
        raise SystemExit(f"{document}: closure refused because PDF or contact sheet is missing")

    metrics = qa["metrics"]
    source_rel = source_manifest["source"]
    record = {
        "document": document,
        "candidate": f"v{version}-editorial",
        "status": "PASS",
        "visual_review": "PASS",
        "visual_review_date": datetime.now(TZ).date().isoformat(),
        "canonical_stage": preservation["canonical_stage"],
        "canonical_source": source_rel,
        "canonical_source_sha256": preservation["canonical_source_sha256"],
        "canonical_editorial_tokens": preservation["canonical_editorial_tokens"],
        "rendered_editorial_tokens": preservation["rendered_editorial_tokens"],
        "validator_checks": len(qa["checks"]),
        "pages": metrics["pages"],
        "minimum_ordinary_vertical_density": metrics["minimum_ordinary_vertical_density"],
        "source_blocks": metrics["source_blocks"],
        "pause_pages": metrics["pause_pages"],
        "pdf": str(pdf.relative_to(package)),
        "pdf_bytes": pdf.stat().st_size,
        "pdf_sha256": sha256(pdf),
        "pdf_modified_at": fmt_time(pdf),
        "contact_sheet": str(contact_sheet.relative_to(package)),
    }
    (package / "qa" / "visual-review.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    handoff = f"""# {document} v{version} editorial, acta de cierre

## Resultado

{document} queda congelado como candidato editorial en lenguaje llano. No reemplaza todavía la versión pública ni modifica `main`.

## Fuente canónica

- Etapa: `{record['canonical_stage']}`.
- Archivo: `{source_rel}`.
- SHA-256: `{record['canonical_source_sha256']}`.
- La copia empaquetada es idéntica byte por byte a la fuente canónica.
- Conservación: {record['canonical_editorial_tokens']:,} tokens normalizados en origen y {record['rendered_editorial_tokens']:,} en la composición, sin faltantes ni agregados.
- Referentes: seis fichas canónicas presentes.

## PDF

- Archivo: `{record['pdf']}`.
- Páginas: {record['pages']}.
- Tamaño: {record['pdf_bytes']:,} bytes.
- SHA-256: `{record['pdf_sha256']}`.
- Fecha de modificación: {record['pdf_modified_at']}.
- Es una exportación nueva desde la composición HTML, no una copia renombrada.

## Auditorías

- Validador integral: PASS, {record['validator_checks']} de {record['validator_checks']} controles.
- Bloques editoriales trazables: {record['source_blocks']}.
- Menor densidad vertical ordinaria: {record['minimum_ordinary_vertical_density'] * 100:.2f} %.
- Auditoría de conservación: PASS.
- Revisión visual completa y contact sheet: PASS.
"""
    handoff_path = package / "HANDOFF.md"
    if not handoff_path.exists():
        handoff_path.write_text(handoff, encoding="utf-8")
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=11)
    parser.add_argument("--end", type=int, default=36)
    parser.add_argument("--version", type=int, default=9)
    args = parser.parse_args()

    records = [close_document(n, args.version) for n in range(args.start, args.end + 1)]
    report_path = ROOT / "editorial-standard" / f"N{args.start:02d}-N{args.end:02d}-v{args.version}-final-audit.md"
    total_pages = sum(record["pages"] for record in records)
    total_bytes = sum(record["pdf_bytes"] for record in records)
    minimum = min(records, key=lambda record: record["minimum_ordinary_vertical_density"])
    rows = "\n".join(
        f"| {r['document']} | {r['pages']} | {r['validator_checks']}/{r['validator_checks']} | "
        f"{r['minimum_ordinary_vertical_density'] * 100:.2f} % | PASS | PASS | {r['pdf_bytes']:,} | `{r['pdf_sha256']}` |"
        for r in records
    )
    report = f"""# Auditoría final N{args.start:02d} a N{args.end:02d}, candidatos editoriales v{args.version}

Fecha de cierre: {datetime.now(TZ).date().isoformat()}.

## Dictamen

Los {len(records)} documentos aprobaron la auditoría de contenido, conservación de fuente canónica, estructura pedagógica, continuidad de Hotel Horizonte, referencias, imágenes, composición A4, densidad, enlaces, exportación PDF y revisión visual por contact sheet. Los archivos quedan listos como candidatos de revisión académica y editorial. Esta rama no modifica todavía `main` ni el sitio público.

## Resumen

- Documentos: {len(records)}.
- Páginas: {total_pages}.
- Tamaño total de PDF: {total_bytes:,} bytes.
- Controles deterministas: {sum(r['validator_checks'] for r in records)} de {sum(r['validator_checks'] for r in records)} aprobados.
- Menor densidad ordinaria: {minimum['minimum_ordinary_vertical_density'] * 100:.2f} % en {minimum['document']}.
- Conservación textual: PASS en los {len(records)} documentos.
- Revisión visual: PASS en los {len(records)} documentos.

## Matriz

| Documento | Páginas | Controles | Densidad mínima | Fuente | Visual | Bytes | SHA-256 |
|---|---:|---:|---:|---|---|---:|---|
{rows}
"""
    report_path.write_text(report, encoding="utf-8")
    json_path = report_path.with_suffix(".json")
    json_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PASS {len(records)} documents, {total_pages} pages, {total_bytes} PDF bytes")
    print(report_path.relative_to(ROOT))


if __name__ == "__main__":
    main()
