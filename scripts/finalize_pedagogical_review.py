"""Verify the local review artifacts; never publish or alter the course catalog."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "pedagogy/pedagogical-review-20260926"

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

plan = json.loads((REVIEW / "release-plan.json").read_text())
assert len(plan) == 36
exceptions = {}
page_count = 0
for item in plan:
    package = ROOT / item["package"]
    audit = json.loads((package / "pdf-audit.json").read_text())
    render = json.loads((package / "render-report.json").read_text())
    assert digest(ROOT / item["source"]) == item["source_sha256"] == audit["source_sha256"], item["code"]
    assert digest(ROOT / item["output"]) == audit["sha256"], item["code"]
    assert not audit["empty_pages"] and not audit["out_of_bounds"] and not audit["overlap_candidates"], item["code"]
    assert not render["missingImages"] and not render["hiddenSourceBlocks"], item["code"]
    assert (REVIEW / "qa" / item["code"] / "contact.jpg").exists()
    assert audit["coverage"] >= 0.999
    if audit["missing_word_occurrences"]:
        exceptions[item["code"]] = audit["missing_meaningful"]
    page_count += len(audit["pages"])
    item.update(rendered=True, visual_review=True, published=False, pdf_sha256=audit["sha256"])
    item["visual_review_scope"] = "Vista general de todas las páginas; detalle de las tablas nuevas de N13, N29 y N30. No equivale a una prueba con estudiantes."
    (package / "edition-manifest.json").write_text(json.dumps(item, ensure_ascii=False, indent=2) + "\n")
(REVIEW / "release-plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n")
result = dict(readings=len(plan), pages=page_count, current_sources_verified=True,
              current_pdfs_verified=True, missing_images=0, hidden_source_blocks=0,
              empty_pages=0, detected_overlaps=0, detected_out_of_bounds=0,
              extraction_token_differences=exceptions, published=False)
(REVIEW / "delivery-checks.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(result, ensure_ascii=False))
