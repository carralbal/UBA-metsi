---
name: metsi-build-infographics
description: Create deterministic METSI-style educational diagrams and infographics as editable SVG or embeddable HTML using the measured typography, monochrome palette, card geometry, spacing, borders, and layout families of the reference Gamma documents. Use for concept grids, numbered steps, comparisons, flows, timelines, glossaries, taxonomies, checklists, process maps, and compact visual summaries that must match METSI courseware.
---

# METSI Build Infographics

Turn structured content into restrained, editorial infographics. Prefer semantic clarity over decorative complexity.

## Workflow

1. Read `references/diagram-system.md` completely.
2. Reduce the source to one claim per node. Keep node titles under 8 words and body copy under 30 words when possible.
3. Choose the relationship before the shape, then select among `grid`, `steps`, `flow`, `comparison`, `timeline`, `glossary`, `cycle`, `orbit`, `hub`, `layers`, `system-map`, `isometric-system`, `assembly`, `atlas`, `icon-field`, or `panels`.
4. For a complete HTML course document, prefer native semantic HTML/CSS so type remains one-to-one with the surrounding body and diagrams can reflow on mobile and across print pages. Use SVG only for a genuinely spatial topology that cannot be expressed cleanly in HTML.
5. For SVG output, create an input JSON following the schema in the reference and render:

   `python3 scripts/render_infographic.py input.json output.svg`

6. Inspect the finished diagram at its intended display width in desktop, mobile, and PDF—not the source canvas. Reject it if text overlaps a node, connector, border, or adjacent label.
7. Embed diagrams without additional shadows, gradients, 3D effects, or unrelated colors.
8. Audit the whole document for family repetition. Use at least four families when a document contains six or more diagrams, and never place more than two diagrams of the same family consecutively.
9. Every full `N` document with sufficient structural content must contain at least three `isometric-system` diagrams: axonometric modules, differentiated object types, ports, dotted routes, and a central construct or explicit input/output path.
10. Meet the diagram iconography quota in every full `N` document: at least eight meaningful line-icon motifs distributed through the diagrams. This does not replace the separate requirement for icon-led editorial text blocks in `$metsi-compose-document`.
11. In `isometric-system` diagrams, use complete conceptual labels of two or three words. Omit node body copy unless a separate, collision-free annotation lane exists. Central labels use one or two words and name the construct, never the source document.
12. When several documents belong to one course, load and update `course-diagram-registry.json`. Fingerprint the center plus normalized node labels and reject exact semantic repetition across documents. Shared source dossiers may repeat as prose but do not justify redrawing the same model: show a class-specific delta, comparison, evolution, application, or omit the repeated visual.
13. Derive diagrams only from the document's class-specific core, not from shared appendices or recurring editorial scaffolding. Place the visual next to the source section that generated it; fixed-position distribution is forbidden when it separates a diagram from its concept.
14. Preserve grammar in every visible label. Never create a label by deleting articles, connectors, auxiliaries, or negations from source prose. Use an exact source clause, a visibly ellipsized source prefix, or a deliberately written grammatical editorial label.
15. In icon-led or multi-item visuals, every slot must have a distinct heading and distinct explanatory copy. Never duplicate one available concept merely to fill a fixed four- or five-item layout; gather distinct adjacent concepts or reduce the item count.
16. Icon-led explanatory copy must be a substantive sentence of at least six words. Reject list stubs, headings copied as bodies, labels ending in a colon or semicolon, and fragments that require missing context.

## Fidelity rules

- Use Inter. Use 700 only for titles and node headings; body copy uses 400.
- Use `#272525` for primary text, `#4D4D4D` only for secondary text, white ground, `#E6E6E6` filled nodes, and `#CCCCCC` borders.
- Make labels and explanatory copy visually comparable to the surrounding paragraph text. At an 855 px display width, body labels must resolve to at least 17 px; use 27–30 px on a 1344 px canvas. Titles must resolve to at least 20 px.
- Use 6.3 px node radius, 18 px node padding at 855 px content width, and 18 px gutters. Scale proportionally for larger SVG canvases.
- Use equal-width columns only when the concepts are genuinely peers. Do not default to four boxes. Prefer cycles for feedback, radial/orbit structures for interacting dimensions, layers for nested boundaries, hub maps for systems, branching flows for scenarios, and multi-panel compositions for several related mechanisms.
- For a system boundary, socio-technical structure, evidence model, or concept with three or more interacting dimensions, a plain box grid is forbidden. Use a structural family with explicit topology.
- A structural infographic must use at least two of these devices: spatial grouping, ports/connectors, layered or isometric forms, line icons, a central construct, or a visible input/output path.
- Use `assembly` when several sources or criteria construct one outcome; `orbit` for nested or interacting scopes; `system-map` for actors, technology, structure, and tasks; `atlas` for connected micro-diagrams; and `icon-field` for four or more dimensions explained by large line icons and paragraph-scale copy.
- `orbit` and text-rich SVG `icon-field` require manual art direction when labels are longer than two words. Do not select them automatically for Spanish course text; prefer native HTML, `assembly`, or `system-map` unless desktop, mobile, and print inspection proves every label has an independent, collision-free lane.
- In `system-map`, small circles are ports or icons, never text containers. Give every multiword concept an independent exterior label or icon-led module whose width and height follow the measured wrapped text. Reserve at least 24 px horizontal and 20 px vertical clearance after wrapping; render connectors first so cards and label capsules cover their endpoints. If that lane cannot fit at paragraph-comparable size, change family instead of shrinking or clipping the label.
- Use thin neutral connectors behind nodes. Never use colorful arrows or ornamental icon packs.
- Do not turn every section into a diagram. Use diagrams when relationships, categories, order, or comparison materially improve comprehension.
- Keep line-art forms simple and editorial: circles, stacks, frames, arrows, dotted connectors, restrained outline icons, and flat neutral fills. Vary topology without changing the visual language.
- Rotate `isometric-system` variants among evidence funnels, socio-technical maps, governance assemblies, and process ecosystems. Do not repeat one central box with renamed labels.
- Keep connectors in dedicated gaps or lanes. Never draw a connector behind or through text.
- For axonometric diagrams, no object may share a bounding area with a label. Prefer a short complete label outside the object over a truncated explanatory sentence.
- Before delivery, automatically reject repeated non-empty titles or bodies within one visual, repeated node labels within the same document, and labels that are neither source-grounded grammatical fragments nor explicitly reviewed editorial rewrites.
- Calculate every step/card height from the wrapped title and body; fixed-height text boxes are forbidden. Four paragraph-scale Spanish steps use a 2×2 composition; five or more text-rich steps use a two-column serpentine sequence, vertical bands, or another reflowing composition. Never place a word in a column narrower than its rendered width, and keep connectors entirely inside dedicated gutters.
- For a five-node system map, use three wide modules above and two below a central construct; each module must provide an independent icon lane and text lane. Place the central construct label in its own opaque rounded capsule, never loose over a connector field.
- Make the infographic occupy at least 75% of the available content width unless it is intentionally paired with prose in columns.
- In stone cards, inherit the card background. Do not place a white diagram canvas or white node over gray. On `stone-dark`, do not stack medium-gray tiles over the dark parent: use white line art on a transparent surface or move the structural visual to a white/stone-light card.
- Icons use one coherent outline system: 2–2.5 px strokes at the 855 px display measure, round caps and joins, no multicolor fills, and no generic emoji.
- Prefer breakable rows, bands, pairs, and steps for print. Do not force a tall unbreakable SVG that creates a half-empty page.

## Output contract

Deliver editable HTML/JSON or SVG/JSON plus concise alt text. Do not add a visible provenance or production caption. Add a content caption only when the surrounding prose does not introduce the diagram.
