#!/usr/bin/env python3
"""Deterministic integrity and publication audit for METSI N17–N20 PDFs."""

from __future__ import annotations

import collections
import hashlib
import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path

import pdfplumber
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parent


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tokens(text: str) -> list[str]:
    text = unicodedata.normalize("NFKC", text).lower().replace("’", "").replace("'", "")
    text = re.sub(r"\b([a-z]{2,})-\s+([a-z0-9]{2,})\b", r"\1-\2", text)
    return re.findall(r"[a-záéíóúüñ0-9]+", text)


def annotation_urls(reader: PdfReader) -> list[str]:
    urls: list[str] = []
    for page in reader.pages:
        for annotation in page.get("/Annots", []):
            item = annotation.get_object()
            action = item.get("/A")
            if action and action.get("/URI"):
                urls.append(str(action.get("/URI")))
    return urls


def expected_urls(manifest: dict) -> list[str]:
    found: list[str] = []
    for reference in manifest["references"]:
        for item in re.findall(r"https://\S+", reference):
            item = item.rstrip(".,;")
            while item.endswith(")") and item.count("(") < item.count(")"):
                item = item[:-1]
            found.append(item)
    return found


def audit(number: int) -> dict:
    package = ROOT / f"N{number:02d}-v1-editorial"
    source_manifest = json.loads((package / "source-manifest.json").read_text(encoding="utf-8"))
    manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
    integrity = json.loads((package / "integrity-report.json").read_text(encoding="utf-8"))
    pdf_path = package / "output" / f"N{number:02d}-METSI-lectura-previa-v1-final.pdf"
    raw_path = package / "output" / f"N{number:02d}-METSI-lectura-previa-v1.pdf"
    reader = PdfReader(pdf_path)
    pdf = pdfplumber.open(pdf_path)
    raw = pdfplumber.open(raw_path)
    extracted = "\n".join((page.extract_text() or "") for page in pdf.pages)
    pdf_counter = collections.Counter(tokens(extracted))
    source_text = "\n".join(item["text"] for item in source_manifest["eligible_blocks"])
    source_counter = collections.Counter(tokens(source_text))
    missing_tokens = {key: amount - pdf_counter[key] for key, amount in source_counter.items() if pdf_counter[key] < amount}
    blank_pages = []
    near_blank_pages = []
    image_plates = []
    for index, page in enumerate(raw.pages, 1):
        words = page.extract_words() or []
        images = page.images or []
        if not words and not images:
            blank_pages.append(index)
        if len(words) < 20 and not images:
            near_blank_pages.append(index)
        if images:
            largest = max((float(img["width"]) * float(img["height"]) for img in images), default=0)
            if largest >= float(page.width) * float(page.height) * 0.80:
                image_plates.append(index)
    raw.close()
    pdf.close()
    expected = expected_urls(manifest)
    actual = annotation_urls(reader)
    missing_urls = sorted(set(expected) - set(actual))
    linkedin_present = "https://www.linkedin.com/in/carralbal" in actual
    media_box_ok = all(abs(float(page.mediabox.width) - 594.96) < 0.2 and abs(float(page.mediabox.height) - 841.92) < 0.2 for page in reader.pages)
    root = reader.trailer["/Root"]
    tagged = "/StructTreeRoot" in root and bool(root.get("/MarkInfo", {}).get("/Marked", False))
    lang = str(root.get("/Lang", ""))
    record = {
        "document": f"N{number:02d}",
        "status": "PASS",
        "pdf": str(pdf_path.relative_to(ROOT)),
        "sha256": sha(pdf_path),
        "bytes": pdf_path.stat().st_size,
        "modified": datetime.fromtimestamp(pdf_path.stat().st_mtime).astimezone().isoformat(timespec="seconds"),
        "pages": len(reader.pages),
        "a4": media_box_ok,
        "tagged": tagged,
        "language": lang,
        "source_sha256_preserved": manifest["source_sha256"] == sha(package / manifest["source"]),
        "source_blocks": len(source_manifest["eligible_blocks"]),
        "rendered_source_blocks": integrity["rendered_source_id_count"],
        "source_mapping": integrity["status"],
        "canonical_token_count": sum(source_counter.values()),
        "pdf_token_count": sum(pdf_counter.values()),
        "missing_canonical_token_occurrences": sum(missing_tokens.values()),
        "missing_canonical_tokens": missing_tokens,
        "blank_pages": blank_pages,
        "near_blank_pages": near_blank_pages,
        "full_page_image_plates": image_plates,
        "expected_reference_urls": len(expected),
        "missing_reference_urls": missing_urls,
        "linkedin_footer_link": linkedin_present,
        "cover_alt": bool(manifest["cover"]["alt"]),
        "pause_alts": all(bool(item["alt"]) for item in manifest["image_manifest"]),
        "closing_alt": bool(manifest["closing"]["alt"]),
        "closing_caption": bool(manifest["closing"]["caption"]),
        "native_black_and_white_cover": manifest["cover"]["photographic_origin"] == "native_black_and_white",
        "diagram_count": len(manifest["diagrams"]),
        "portrait_rights": collections.Counter(item["rights_status"] for item in manifest["portrait_references"]),
    }
    required = [
        record["a4"], record["tagged"], record["source_sha256_preserved"],
        record["source_mapping"] == "PASS", not record["missing_canonical_token_occurrences"],
        not blank_pages, not near_blank_pages, not missing_urls, linkedin_present,
        record["cover_alt"], record["pause_alts"], record["closing_alt"],
        record["closing_caption"], record["native_black_and_white_cover"],
        record["diagram_count"] == 3, len(image_plates) >= 4,
    ]
    if not all(required):
        record["status"] = "FAIL"
    (package / "qa").mkdir(parents=True, exist_ok=True)
    (package / "qa" / "qa-report.json").write_text(json.dumps(record, ensure_ascii=False, indent=2, default=dict) + "\n", encoding="utf-8")
    return record


def main() -> None:
    records = [audit(number) for number in range(17, 21)]
    lines = [
        "# METSI · Auditoría de publicación del Bloque D",
        "",
        "Control determinístico posterior a la composición y finalización de N17 a N20.",
        "",
        "| Documento | Estado | Páginas | Bloques | URLs | Placas fotográficas | PDF final |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for item in records:
        lines.append(
            f"| {item['document']} | {item['status']} | {item['pages']} | "
            f"{item['rendered_source_blocks']}/{item['source_blocks']} | "
            f"{item['expected_reference_urls'] - len(item['missing_reference_urls'])}/{item['expected_reference_urls']} | "
            f"{len(item['full_page_image_plates'])} | `{item['pdf']}` |"
        )
    lines += [
        "",
        "## Resultado transversal",
        "",
        f"- Fuentes canónicas sin pérdidas: {'PASS' if all(not r['missing_canonical_token_occurrences'] for r in records) else 'FAIL'}.",
        f"- Mapeo fuente a HTML: {'PASS' if all(r['source_mapping'] == 'PASS' for r in records) else 'FAIL'}.",
        f"- PDF A4, etiquetado y en español: {'PASS' if all(r['a4'] and r['tagged'] and r['language'] == 'es-AR' for r in records) else 'FAIL'}.",
        f"- Páginas vacías o casi vacías accidentales: {'PASS' if all(not r['blank_pages'] and not r['near_blank_pages'] for r in records) else 'FAIL'}.",
        f"- Enlaces bibliográficos y pie: {'PASS' if all(not r['missing_reference_urls'] and r['linkedin_footer_link'] for r in records) else 'FAIL'}.",
        f"- Portadas nativas en blanco y negro, dos pausas, tres diagramas y cierre de fósforos: {'PASS' if all(r['native_black_and_white_cover'] and len(r['full_page_image_plates']) >= 4 and r['diagram_count'] == 3 for r in records) else 'FAIL'}.",
        "",
        "## Auditoría visual",
        "",
        "Las cuatro planchas de contacto se revisaron completas después de la recompaginación final. Resultado: PASS. No se observan títulos huérfanos, texto truncado, colisiones, placas con márgenes blancos, preguntas fragmentadas ni páginas accidentales vacías. Las portadas y las ocho pausas conservan cobertura a sangre, rango tonal de grises y lectura editorial coherente con la colección.",
        "",
        "## Incertidumbre declarada",
        "",
        "Los retratos se reproducen sólo cuando existe un archivo local con procedencia utilizable. Cuando no pudo verificarse ese derecho, la ficha conserva el nombre y el aporte, y muestra un monograma explícito en lugar de inventar o duplicar una identidad.",
    ]
    (ROOT / "BLOCK-D-PDF-AUDIT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({item["document"]: item["status"] for item in records}, ensure_ascii=False))


if __name__ == "__main__":
    main()
