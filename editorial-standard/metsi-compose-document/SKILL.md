---
name: metsi-compose-document
description: Assemble complete METSI educational documents as premium print magazines or responsive web handouts from structured JSON, with editorial covers, spread-aware grids, serif/sans typography, varied article layouts, curated photography, compact SVG infographics, cases, summaries, assessment blocks, and references. Use when Codex must create or rebuild an N01–N46 reading PDF, reproduce the approved METSI magazine language, avoid generic Gamma cards, or package written material and media into consistent courseware.
---

# METSI Compose Document

Compose the final artifact directly as standards-based HTML and export it to PDF when requested. Do not call Gamma by default.

## Mandatory preparation

1. Read `references/visual-system.md`, `references/premium-magazine-system.md`, and `references/document-schema.md` completely.
2. Select `magazine-print` for every N01–N46 prereading PDF unless the user explicitly requests the legacy scrolling-card handout.
3. Build an eligible-source manifest. Assign a stable `source_id` to every student-facing heading, paragraph, list item, table cell, and code block.
4. Ensure every photograph passed `$metsi-find-images` or an equivalent source/license review.
5. Ensure every infographic passed `$metsi-build-reference-grade-infographics` when it represents a system, assembly, governance relation, evidence structure, or process-service map.

## Workflow

1. Create a page/spread plan before rendering. For each page declare purpose, `source_id` values, layout family, dominant visual mass, secondary mass, image role, accent, and estimated occupied area.
2. Design pairs of pages as spreads. Balance a dense page with an image-led or structurally lighter opposite page; do not optimize pages independently.
3. Use at least five layout families in a full N-document and never repeat one family more than twice consecutively.
4. Create the document JSON and render:

   `python3 scripts/render_document.py document.json output-directory`

5. Validate the plan:

   `python3 scripts/validate_magazine.py document.json`

6. Inspect HTML at 1280 px, 768 px, and 390 px. For `magazine-print`, also export A4 PDF and inspect every page plus a contact sheet.
7. Compare rendered `data-source-id` elements against the eligible-source manifest. Require equal block count, equal normalized text, and zero eligible-word delta.
8. Reject accidental blank zones, orphan headings, split paragraphs, arbitrary image widths, repeated infographics, visible provenance, and any regression against previously approved pages.
9. Deliver the output directory with `document.json`, source manifest, image manifest, editable diagrams, integrity report, PDF, contact sheet, and QA report.

## Magazine composition rules

- Treat the spread as the primary editorial unit. Use a six-column grid per page and twelve columns per spread.
- Create every METSI N-document cover photograph natively in black and white. The photographic concept, lighting ratios, wardrobe, materials, background separation, exposure, and tonal hierarchy must be designed for monochrome from the outset. Reject a cover conceived or sourced in color and later desaturated or converted with a grayscale filter. Record native monochrome intent and provenance in the image manifest, and do not apply a CSS grayscale conversion to the approved cover asset.
- Establish one dominant mass, one secondary mass, and one support zone per spread.
- Use high-contrast display serif for titles, readable serif for long body text, and sans serif for kickers, folios, labels, captions, and running matter.
- Keep body typography consistent. Use smaller text only for captions, folios, metadata, compact tables, and reviewed infographic labels.
- Use crisp rectangular photography locked to grid modules. Do not use rounded corners, shadows, gradients, floating postcards, or the same panoramic crop for every section.
- Vary image roles: full bleed, half-page hero, portrait rail, panorama, mosaic, evidence inset, or texture. Maintain one dominant image per spread.
- When a METSI scene depicts academic life, students, teaching, professional work, or organizations without an explicitly foreign setting, its people and environment must credibly read as Argentine or Latin American. Judge the whole context—casting, architecture, clothing, objects, and institutional atmosphere—not skin tone alone. Reject generic North American or European campus/corporate stock.
- Treat recurring fictional portraits as separate identities. Compare every new face against the complete character set and reject copies, near-duplicates, or sibling-like variants unless the narrative explicitly requires a family relationship; different filenames or hashes do not prove identity diversity.
- Use warm white, black, cool gray, and one restrained accent per section. Extract the accent from the dominant photograph.
- Use rules, frames, circles, signatures, accent columns, and drop caps sparingly. Each must serve a clear editorial function.
- In every complete N-document, interleave exactly two internal full-page photographic pauses, each carrying one short, source-grounded, forceful reflective phrase. Place the first immediately after the opening/front-matter transition (after page 4 in the canonical N structure) and the second at a later major conceptual transition. These are additional to the closing page.
- Every page declared full-page, full-bleed, hero-page, section background, or closing-fullbleed must cover the complete A4 canvas to all four edges. Any white paper strip, inherited text margin, gutter, footer band, or reduced background is a blocking defect.
- In METSI N documents, a stand-alone editorial photograph is always a full-page, four-edge bleed. Do not leave an autonomous photograph floating inside a white page. Portraits, documentary evidence, instructional details, diagrams, and photographs embedded in an argument may remain inset only when their informational function requires it; they are not photographic pauses.
- Exercise writing areas must read as intentional paper space: white or warm-white fill, thin neutral border, restrained volt rule, and a clear label. Never use saturated fills, debug colors, or decorative gradients.
- Integrate infographics at one-quarter to one-half page when possible. Reserve larger treatment only for a genuinely complex reference-grade model. Rotate topology and presentation.
- Keep the Hotel Horizonte dark opening when required. Every complete N-document must end with the canonical burned-matches asset as a full-page close. It carries the standard folio and footer rule, explicit alternative text, and one brief conceptual caption. It never carries the large reflective quote used by the two internal photographic pauses and is never replaced by another image.

## Required layout families

Support and rotate among:

- `cover-editorial`
- `section-opener`
- `article-2col`
- `article-3col`
- `article-rail`
- `editorial-frame`
- `mosaic-essay`
- `portrait-profile`
- `panorama-bottom`
- `hero-page`
- `accent-column`
- `diagram-feature`
- `case-dark`
- `closing-fullbleed`

Do not use every family mechanically. Select the family from content, image geometry, and its role in the spread.

## Content integrity

- Preserve every eligible source block and word unless the user authorizes rewriting.
- Write prompts, calls to action, and direct instructions in Argentine River Plate Spanish. When addressing the student with `vos`, use consistent voseo and its imperative forms (`situá`, `mostrá`, `convertí`, `seleccioná`, `compará`), never mix them with tuteo imperatives. Titles or index entries that describe what a Núcleo does use third person (`sitúa`, `muestra`, `convierte`, `selecciona`); do not convert a description into an order merely because it is student facing.
- Add captions, folios, kickers, pull quotes, diagram labels, and transitions as separate editorial microcopy.
- Do not shorten academic nuance to make a page fit. Recompose the spread, change the layout family, or continue the article.
- Do not add decorative examples merely to fill a hole. When more content is needed, use a source-grounded worked example, counterexample, decision test, or application.

## Non-negotiable quality gate

Reject the output if any of these are true:

- the document reads as a vertical sequence of identical cards;
- fewer than five layout families appear in a full N-document;
- one layout family repeats on more than two consecutive pages;
- a photograph is centered at an arbitrary width instead of aligned to the grid;
- ordinary editorial photography uses rounded corners or shadows;
- title, body, metadata, and caption use an undifferentiated typographic voice;
- a page has more than 40% avoidable empty area;
- a visual-pause page is not intentionally full-page or structurally composed;
- an infographic exceeds half a page without documented conceptual need;
- two infographics repeat the same topology without comparative purpose;
- a paragraph, list item, title, label, or caption is clipped or split awkwardly;
- visible captions expose stock-bank, creator, license, file, or production metadata;
- source block count, normalized text, or eligible-word count differs from the manifest;
- previously approved images, page families, or visual decisions changed without an explicit reason recorded in the regression checklist.
- any content, image, crop, layout, typography, or page outside the user's explicit revision scope changed opportunistically; approved elements remain locked until the user names them again.

## Legacy web-card mode

Use `web-cards` only when the user requests a scrolling Gamma-like handout. Apply the earlier 981/855 px card system from `references/visual-system.md`; do not mix its rounded card grammar into `magazine-print`.
