"""Inventory the full rewrite without equating draft presence with completion.

This mechanical check cannot certify readability or academic fidelity. Content,
visual, and publication review remain explicit independent gates.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EDITION = ROOT / "pedagogy/plain-language-edition"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def sections(text: str) -> dict[str, str]:
    parts = re.split(r"^## (.+)$", text, flags=re.M)
    return {parts[i].strip(): parts[i + 1].strip()
            for i in range(1, len(parts), 2)}


def bibliography(text: str) -> set[str]:
    tail = sections(text).get("Referencias base", "")
    return {normalize(line) for line in tail.splitlines() if line.startswith("- ")}


def main() -> None:
    manifest = json.loads((ROOT / "course-manifest.json").read_text())
    prior_path = EDITION / "inventory.json"
    prior = {r["code"]: r for r in json.loads(prior_path.read_text())["documents"]} if prior_path.exists() else {}
    records = []
    for item in manifest["documents"]:
        code = item["code"]
        if code == "N00":
            continue
        previous = prior.get(code, {})
        source = ROOT / previous.get("baseline_source", item["canonical_source"])
        draft = EDITION / f"{code}.md"
        record = {
            "code": code,
            "baseline_source": str(source.relative_to(ROOT)),
            "baseline_sha256": digest(source),
            "baseline_public_pdf": item["public_pdf"],
            "approved_model_preserved": code == "N25",
            "draft_exists": draft.exists(),
            "full_rewrite_review_passed": False,
            "academic_and_continuity_review_passed": False,
            "pdf_visual_review_passed": False,
            "this_edition_published_and_verified": False,
        }
        if draft.exists():
            old, new = source.read_text(), draft.read_text()
            old_sections, new_sections = sections(old), sections(new)
            old_body = old.split("## Referencias base")[0]
            new_body = new.split("## Referencias base")[0]
            old_paragraphs = {normalize(p) for p in old_body.split("\n\n")
                              if len(p.split()) >= 20}
            record.update({
                "draft_path": str(draft.relative_to(ROOT)),
                "draft_sha256": digest(draft),
                "words_including_apparatus": len(new.split()),
                "body_words_including_glossary_and_questions": len(new_body.split()),
                "top_level_sections": len(new_sections),
                "baseline_sections_not_found": sorted(set(old_sections) - set(new_sections)),
                "new_sections": sorted(set(new_sections) - set(old_sections)),
                "unchanged_body_paragraphs_20_words_or_more": sum(
                    normalize(p) in old_paragraphs for p in new_body.split("\n\n")
                    if len(p.split()) >= 20),
                "bibliography_entries_missing": sorted(bibliography(old) - bibliography(new)),
                "bibliography_entries_added": sorted(bibliography(new) - bibliography(old)),
            })
        if previous.get("draft_sha256") == record.get("draft_sha256") and previous.get("baseline_sha256") == record["baseline_sha256"]:
            for gate in ("full_rewrite_review_passed", "academic_and_continuity_review_passed", "pdf_visual_review_passed", "this_edition_published_and_verified"):
                record[gate] = previous.get(gate, False)
        records.append(record)
    report = {
        "scope": "N01–N36 complete-prose rewrite; N25 approved model retained",
        "important": "Draft presence and mechanical checks do not certify any review gate.",
        "readings": len(records),
        "drafts_present": sum(r["draft_exists"] for r in records),
        "approved_models_retained": 1,
        "pending_drafts": [r["code"] for r in records
                           if not r["draft_exists"] and not r["approved_model_preserved"]],
        "documents": records,
    }
    (EDITION / "inventory.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: report[key] for key in (
        "readings", "drafts_present", "approved_models_retained", "pending_drafts")},
        ensure_ascii=False, indent=2))
    for record in records:
        if record["draft_exists"]:
            print(record["code"], "words", record["words_including_apparatus"],
                  "sections", record["top_level_sections"],
                  "missing refs", len(record["bibliography_entries_missing"]),
                  "unchanged paragraphs", record["unchanged_body_paragraphs_20_words_or_more"])


if __name__ == "__main__":
    main()
