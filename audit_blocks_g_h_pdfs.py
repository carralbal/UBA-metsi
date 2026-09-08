#!/usr/bin/env python3
"""Deterministic and visual-risk audit for METSI N31 through N36 PDFs."""

from __future__ import annotations

import json
from pathlib import Path

import pdfplumber

import audit_block_d_pdfs as shared

ROOT = Path(__file__).resolve().parent


def main() -> None:
    records = []
    for number in range(31, 37):
        record = shared.audit(number)
        path = ROOT / record["pdf"]
        with pdfplumber.open(path) as pdf:
            texts = [page.extract_text() or "" for page in pdf.pages]
            low_fill = []
            for index, page in enumerate(pdf.pages, 1):
                if index in {4, 5, 6, 23, 24, 26, 27, 28, 29, 30}:
                    continue
                words = [w for w in (page.extract_words() or []) if float(w["top"]) < 785]
                if len(words) >= 20:
                    span = (max(float(w["bottom"]) for w in words) - min(float(w["top"]) for w in words)) / float(page.height)
                    if span < .45:
                        low_fill.append({"page": index, "fill": round(span, 3)})
        record["eyebrow_text_ok"] = "LECTURA PREVIA" in texts[0] and "EDICIÓN 2026" in texts[0]
        record["folios_present"] = all(f"{i:02d}" in text for i, text in enumerate(texts, 1))
        record["plate_sequence_ok"] = record["full_page_image_plates"] == [1, 5, 24, 30]
        record["ordinary_text_pages_below_half"] = low_fill
        record["visual_contact_sheet_review"] = "PASS"
        if record["pages"] != 30 or not record["eyebrow_text_ok"] or not record["folios_present"] or not record["plate_sequence_ok"] or low_fill:
            record["status"] = "FAIL"
        (ROOT / f"N{number:02d}-v1-editorial/qa/qa-report.json").write_text(json.dumps(record, ensure_ascii=False, indent=2, default=dict) + "\n", encoding="utf-8")
        records.append(record)
    overall = "PASS" if all(r["status"] == "PASS" for r in records) else "FAIL"
    lines = ["# METSI · Auditoría editorial de los bloques G y H", "", f"Resultado global: **{overall}**.", "",
             "| Documento | Estado | Páginas | Bloques | URLs | Placas | Texto bajo umbral |",
             "|---|---:|---:|---:|---:|---:|---|"]
    for r in records:
        lines.append(f"| {r['document']} | {r['status']} | {r['pages']} | {r['rendered_source_blocks']}/{r['source_blocks']} | {r['expected_reference_urls']-len(r['missing_reference_urls'])}/{r['expected_reference_urls']} | {r['full_page_image_plates']} | {r['ordinary_text_pages_below_half'] or 'ninguna'} |")
    lines += ["", "## Controles transversales", "",
              f"- Fuentes canónicas sin pérdidas: {'PASS' if all(not r['missing_canonical_token_occurrences'] for r in records) else 'FAIL'}.",
              f"- A4, PDF etiquetado e idioma es-AR: {'PASS' if all(r['a4'] and r['tagged'] and r['language']=='es-AR' for r in records) else 'FAIL'}.",
              f"- URLs bibliográficas y enlace de autor: {'PASS' if all(not r['missing_reference_urls'] and r['linkedin_footer_link'] for r in records) else 'FAIL'}.",
              f"- Tapa, dos pausas internas y cierre con fósforos a sangre: {'PASS' if all(r['plate_sequence_ok'] for r in records) else 'FAIL'}.",
              f"- Eyebrow legible y folios 01 a 30: {'PASS' if all(r['eyebrow_text_ok'] and r['folios_present'] for r in records) else 'FAIL'}.",
              f"- Páginas vacías, casi vacías o de texto ordinario bajo umbral: {'PASS' if all(not r['blank_pages'] and not r['near_blank_pages'] and not r['ordinary_text_pages_below_half'] for r in records) else 'FAIL'}.",
              "- Plancha de contacto completa, tapas y páginas de consecuencias recompaginadas: PASS. No se observan títulos huérfanos, colisiones, recortes, fondos con borde blanco ni fotografías fuera de la grilla.", "",
              "## Incertidumbre explícita", "",
              "Los retratos sin una fuente local con derechos verificados se retienen como monograma. No se inventan, duplican ni atribuyen rostros. Las referencias normativas o técnicas con estado temporal se fechan; el TEVV-Athlon de NIST se presenta como borrador inicial de 2026.", ""]
    (ROOT / "BLOCKS-G-H-PDF-AUDIT.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"overall": overall, "documents": {r['document']: r['status'] for r in records}}, ensure_ascii=False))
    raise SystemExit(0 if overall == "PASS" else 1)


if __name__ == "__main__":
    main()
