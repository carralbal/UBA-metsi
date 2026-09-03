---
name: metsi-generate-courseware
description: Orchestrate source-faithful METSI courseware as premium print magazines or responsive web handouts, including content analysis, spread planning, licensed image curation, source-grounded infographics, composition, PDF and responsive QA, preservation, and optional publication. Use for complete N01–N46 prereading documents and rebuilds that must match the approved METSI editorial system without reverting to generic Gamma cards.
---

# METSI Generate Courseware

Transform source material into complete METSI courseware through the specialist skills. For N01–N46 prereading documents, the default product is an A4 premium magazine PDF with companion HTML source, not a vertical Gamma-card stack.

## Required preparation

1. Read `references/content-architecture.md`, `references/content-depth-standard.md`, `references/visual-audit.md`, and `references/qa-rubric.md` completely.
2. Read the selected specialist skills completely before invoking them.
3. Record the last approved artifact and its locked invariants before revising an existing class.

## Pipeline

1. Analyze the source. Extract claims, objectives, definitions, examples, procedures, evidence, risks, activities, evaluation material, and references. Flag unsupported gaps.
2. Run the conceptual-depth gate in `references/content-depth-standard.md`. Reject and rewrite the source before design if it fails any blocker. Word count alone never passes this gate.
3. Create an eligible-source manifest with one `source_id` for every student-facing heading, paragraph, list item, table cell, and code block.
4. Build a page-and-spread plan from source density. For each page declare source IDs, layout family, dominant and secondary masses, image role, infographic need, accent, and estimated occupancy.
5. Invoke `$metsi-find-images` for each photographic role. Preserve the course image registry and previously approved selections.
6. Invoke `$metsi-build-reference-grade-infographics` for system maps, evidence assemblies, governance atlases, layered architectures, and complex processes. Use `$metsi-build-infographics` for compact comparisons, glossaries, steps, and taxonomies.
7. Invoke `$metsi-compose-document` in `magazine-print` mode for N-documents. Use `web-cards` only when the user explicitly requests the legacy scrolling handout.
8. Export A4 PDF and render every page. Inspect the contact sheet first, then each page at full resolution.
9. Run the complete rubric, conceptual-depth audit, and source-integrity comparison. Iterate until every blocker passes.
10. Invoke `$metsi-publish-course` only when publication is requested or already in scope. A local design test does not imply publication.

## Editorial architecture

- Plan the spread before the individual page: six columns per page, twelve per spread.
- Use at least five composition families in a full N-document. Never repeat one family on more than two consecutive pages.
- Balance dense article pages with image-led, mosaic, rail, portrait, accent-column, diagram-feature, or full-bleed pages.
- Schedule an intentional visual pause every four to six pages. A pause must be compositionally full; accidental underfill is a defect.
- Preserve the complete academic text. Recompose, continue the article, or add a source-grounded example instead of shrinking the narrative body or deleting nuance.
- Keep the editorial system stable while layouts vary: display serif, reading serif, sans metadata, rectangular grid-locked photography, thin rules, disciplined accent color, outside folios, and consistent running matter.

## Infographic selection

- Visualize only relationships for which spatial structure improves understanding.
- Select topology from meaning: flow for transformation, assembly for evidence, system-map for interaction, atlas for governance, comparison for alternatives, timeline for change, and glossary/grid only for genuinely parallel items.
- Do not impose quotas for isometric views, icons, diagrams, or page positions.
- In a document with four or more diagrams, use at least three semantic topologies unless the source supports fewer.
- Keep most infographics between one quarter and one half page. A larger feature requires a documented complexity reason.
- Keep labels complete, grammatical, source-grounded, and collision-free at final PDF size.

## Photography and recurring assets

- Treat photographs as a coherent editorial series. Assign every image a role: hero, portrait, evidence, sequence, comparison, texture, or pause.
- For every N-document cover, source or generate a photograph conceived natively in black and white. Require monochrome-specific art direction and verify that the final composition does not depend on post hoc desaturation or a grayscale rendering filter.
- Use one dominant image per spread. Subordinate the rest through scale, crop, or monochrome treatment.
- Do not use rounded corners, shadows, arbitrary centered widths, or the same panoramic band repeatedly.
- Keep provenance in the manifest, never in visible captions.
- Maintain the course image registry; non-fixed images may not repeat across N01–N46 by provider ID, URL, or SHA-256.
- Reuse the approved Hotel Horizonte and burned-matches assets when the class architecture calls for them. The matches closing is image-only and full bleed.

## Content integrity and regression control

- Preserve 100% of eligible source blocks and words unless the user authorizes rewriting.
- Add kickers, decks, captions, pull quotes, transitions, and diagram labels as separately identified editorial microcopy.
- Compare the new contact sheet against the approved contact sheet. Do not change a locked image, crop family, page family, palette, footer, case treatment, close, or diagram topology without an explicit recorded reason.
- Reject any version that fixes one request by silently undoing earlier positive feedback.

## Conceptual depth and pedagogical progression

- Treat the approved N02 standard and `references/content-depth-standard.md` as blocking, not aspirational.
- Measure the requested 6,000-word minimum on substantive conceptual body only. Exclude front matter, contents, referents, captions, Hotel Horizonte character cards, pills, glossary, preparation questions, references, and visual instructions.
- Never manufacture length through many shallow headings, duplicated explanations, enlarged glossaries, repeated summaries, or list-heavy restatement.
- Every major concept must form a complete explanatory unit: precise definition, distinction from neighboring concepts, mechanism or causal logic, worked example, counterexample or boundary condition, and decision consequence.
- Progress from an accessible situation to intermediate distinctions and then to technical or academic depth. Assume readers are 18–20 years old with limited systems background and prior Software Engineering exposure.
- Integrate foundational literature with current sources from 2022 onward, preferably 2024 onward where available. Use sources in the reasoning; do not merely append them to the bibliography.
- Include contemporary implications such as generative AI, automation, platforms, data governance, security, work redesign, or regulation only when they materially change the concept under study.
- Compare the N-document with its immediate prerequisites and successors. Remove accidental repetition and state what conceptual advance this N uniquely contributes.

## Rendering decision

Default to direct HTML/CSS/SVG and PDF. Use Gamma only when the user explicitly requires a Gamma-native editable artifact. Treat the validated direct package as source of truth because Gamma import can introduce layout drift.

## Completion standard

The task is complete only when the document reads as one premium publication; every page and spread passes visual inspection; typography, photography, layouts, and infographics show controlled variety; source integrity has zero unexplained delta; the artifact regenerates from editable sources; and any requested publication is verified at its live URL.
