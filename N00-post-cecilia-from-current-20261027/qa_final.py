#!/usr/bin/env python3
"""Validate the source-faithful N00 post-Cecilia PDF before publication."""

from pathlib import Path
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
import re

from PIL import ImageChops
from pypdf import PdfReader
import pypdfium2 as pdfium
from baseline import ensure_baseline


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
FINAL = HERE / "proper-assembly-v4/N00-post-cecilia-full-v3.pdf"
REPORT = HERE / "QA-POST-CECILIA-20261028.json"
ASSEMBLY_REPORT = HERE / "proper-assembly-v4/assembled/validation/N00-assembly.json"


def compact(text: str) -> str:
    text = text.replace("ﬁ", "fi").replace("ﬂ", "fl").lower()
    return re.sub(r"\s+", "", text)


def pixel_equal(a: pdfium.PdfDocument, b: pdfium.PdfDocument, index: int) -> bool:
    left = a[index].render(scale=1).to_pil().convert("RGB")
    right = b[index].render(scale=1).to_pil().convert("RGB")
    return left.size == right.size and ImageChops.difference(left, right).getbbox() is None


def main() -> None:
    public_path = ensure_baseline()
    source = PdfReader(FINAL, strict=True)
    published = PdfReader(public_path, strict=True)
    assembly = json.loads(ASSEMBLY_REPORT.read_text())
    spec = spec_from_file_location("metsi_n00_qa", HERE / "assemble_pdf_patched.py")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    nav = module.navigation(source)
    document = " ".join(page.extract_text() or "" for page in source.pages)
    logical = compact(document)
    questions = [
        "Qué diferencia existe entre leer para recordar",
        "Qué sección de una N creés que te resultará más útil",
        "Qué función cumple una historia",
        "Qué deberías registrar para que el caso Hotel Horizonte",
        "Qué uso de IA apoyaría tu aprendizaje",
        "Volvé a la pregunta profesional",
        "El huésped todavía no tiene una ficha propia",
    ]
    questions_text = compact(" ".join((source.pages[index].extract_text() or "")
                                      for index in (45, 46)))
    positions = [questions_text.find(compact(question)) for question in questions]
    page2 = compact(source.pages[1].extract_text() or "")
    toc = {
        "section_04": ("metsi:delpedidoolaseñalaunaintervencióndefendible", "p.9"),
        "section_18": ("18síntesis", "p.37"),
        "section_25": ("25cómosabersilalecturaprodujoaprendizaje", "p.44"),
        "section_27": ("27cómoseconectanteoría,prácticayevaluación", "p.45"),
    }
    toc_ok = {}
    for name, (title, page) in toc.items():
        at = page2.find(title)
        toc_ok[name] = at >= 0 and page in page2[at:at + len(title) + 70]
    render_a = pdfium.PdfDocument(str(FINAL))
    render_b = pdfium.PdfDocument(str(public_path))
    preserved_pages = [1, 14, 15, 16, 17, 18, 19]
    pixels = {str(index): pixel_equal(render_a, render_b, index - 1) for index in preserved_pages}
    checks = {
        "55_A4_pages": len(source.pages) == len(published.pages) == 55 and all(
            abs(float(page.mediabox.width) - 595.276) < 2 and
            abs(float(page.mediabox.height) - 841.89) < 2 for page in source.pages),
        "original_cover_and_route_pixels": all(pixels.values()),
        "original_page_labels": source.page_labels == published.page_labels,
        "semantic_structure_and_language": bool(source.trailer["/Root"].get("/StructTreeRoot")) and
            bool(source.trailer["/Root"].get("/MarkInfo")) and
            str(source.trailer["/Root"].get("/Lang")) == "es-AR",
        "navigation_complete": not nav["errors"] and len(nav["outlines"]) == 98 and
            len(nav["named_destinations"]) == 36 and len(nav["links"]) == 120,
        "questions_in_reading_order": -1 not in positions and positions == sorted(positions),
        "toc_repagination": all(toc_ok.values()),
        "two_entrances_explained": all(compact(phrase) in logical for phrase in (
            "Hay dos formas frecuentes de entrar en una situación",
            "Una es reactiva",
            "Otra es proactiva",
            "Ni el pedido ni la señal definen por sí solos el problema")),
        "assembly_machine_gate": assembly["status"] == "PASS_MACHINE_CHECKS_PENDING_VISUAL_REVIEW" and
            assembly["structure"]["interior_role_counts_identical"] and
            not assembly["navigation"]["errors"] and not assembly["errors"],
        "no_unexpected_empty_interior_pages": all((page.extract_text() or "").strip()
            for page in source.pages[1:]),
    }
    record = {
        "document": "N00",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "candidate": str(FINAL),
        "candidate_sha256": sha256(FINAL.read_bytes()).hexdigest(),
        "published_baseline_sha256": sha256(public_path.read_bytes()).hexdigest(),
        "checks": checks,
        "preserved_page_pixel_identity": pixels,
        "toc_checks": toc_ok,
        "question_positions": positions,
        "navigation_errors": nav["errors"],
        "publication_state": "private_candidate_not_yet_published",
    }
    REPORT.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": record["status"], "sha256": record["candidate_sha256"],
                      "failed": [key for key, passed in checks.items() if not passed]}, ensure_ascii=False))
    if record["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
