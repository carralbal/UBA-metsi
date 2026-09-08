#!/usr/bin/env python3
"""Publication and visual-risk audit for METSI Block F PDFs."""

from __future__ import annotations

import json
from pathlib import Path

import pdfplumber

import audit_block_d_pdfs as shared


ROOT = Path(__file__).resolve().parent


def main() -> None:
    records = []
    for number in range(26, 31):
        record = shared.audit(number)
        path = ROOT / record["pdf"]
        page_metrics = []
        page_texts = []
        with pdfplumber.open(path) as pdf:
            for index, page in enumerate(pdf.pages, 1):
                words = page.extract_words() or []
                images = page.images or []
                page_texts.append(page.extract_text() or "")
                if words:
                    top = min(float(item["top"]) for item in words)
                    bottom = max(float(item["bottom"]) for item in words)
                    vertical_fill = round((bottom - top) / float(page.height), 3)
                else:
                    vertical_fill = 1.0 if images else 0.0
                page_metrics.append({
                    "page": index, "words": len(words), "images": len(images),
                    "vertical_fill": vertical_fill,
                })
        record["page_metrics"] = page_metrics
        record["eyebrow_text_ok"] = "LECTURA PREVIA" in page_texts[0] and "EDICIÓN 2026" in page_texts[0]
        record["folios_present"] = all(f"{index:02d}" in text for index, text in enumerate(page_texts, 1))
        record["photo_plate_sequence_ok"] = record["full_page_image_plates"] == [1, 5, 22, 28]
        record["text_pages_below_half"] = [
            metric["page"] for metric in page_metrics
            if metric["page"] != 4 and metric["images"] == 0 and metric["words"] >= 20 and metric["vertical_fill"] < 0.45
        ]
        if (
            record["pages"] != 28 or not record["eyebrow_text_ok"] or not record["folios_present"]
            or not record["photo_plate_sequence_ok"] or record["text_pages_below_half"]
        ):
            record["status"] = "FAIL"
        qa = ROOT / f"N{number:02d}-v1-editorial/qa"
        qa.mkdir(parents=True, exist_ok=True)
        (qa / "qa-report.json").write_text(json.dumps(record, ensure_ascii=False, indent=2, default=dict) + "\n", encoding="utf-8")
        records.append(record)
    overall = "PASS" if all(item["status"] == "PASS" for item in records) else "FAIL"
    lines = [
        "# METSI · Auditoría de publicación del Bloque F", "", f"Resultado global: **{overall}**.", "",
        "| Documento | Estado | Páginas | Bloques | URL | Placas fotográficas | Páginas de texto bajo umbral |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for item in records:
        lines.append(
            f"| {item['document']} | {item['status']} | {item['pages']} | "
            f"{item['rendered_source_blocks']}/{item['source_blocks']} | "
            f"{item['expected_reference_urls'] - len(item['missing_reference_urls'])}/{item['expected_reference_urls']} | "
            f"{len(item['full_page_image_plates'])} | {item['text_pages_below_half'] or 'ninguna'} |"
        )
    lines += [
        "", "## Resultado transversal", "",
        f"- Correspondencia fuente a maqueta sin pérdidas: {'PASS' if all(not row['missing_canonical_token_occurrences'] and row['source_mapping'] == 'PASS' for row in records) else 'FAIL'}.",
        f"- A4, estructura etiquetada e idioma es-AR: {'PASS' if all(row['a4'] and row['tagged'] and row['language'] == 'es-AR' for row in records) else 'FAIL'}.",
        f"- URL bibliográficas y enlace de autor: {'PASS' if all(not row['missing_reference_urls'] and row['linkedin_footer_link'] for row in records) else 'FAIL'}.",
        f"- Portadas nativas en blanco y negro, dos pausas y cierre: {'PASS' if all(row['native_black_and_white_cover'] and len(row['full_page_image_plates']) >= 4 for row in records) else 'FAIL'}.",
        f"- Secuencia de placas 1, 5, 22 y 28: {'PASS' if all(row['photo_plate_sequence_ok'] for row in records) else 'FAIL'}.",
        f"- Eyebrow legible y folios 01 a 28: {'PASS' if all(row['eyebrow_text_ok'] and row['folios_present'] for row in records) else 'FAIL'}.",
        f"- Páginas vacías, casi vacías o de texto bajo umbral: {'PASS' if all(not row['blank_pages'] and not row['near_blank_pages'] and not row['text_pages_below_half'] for row in records) else 'FAIL'}.", "",
    ]
    (ROOT / "BLOCK-F-PDF-AUDIT.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"overall": overall, "documents": {row["document"]: row["status"] for row in records}}, ensure_ascii=False))
    raise SystemExit(0 if overall == "PASS" else 1)


if __name__ == "__main__":
    main()
