---
name: metsi-build-reference-grade-infographics
description: Create source-grounded, dense, editorial METSI infographics as editable SVG and review assets at the visual quality of approved axonometric references. Use when converting class prose or structured content into premium system maps, evidence assemblies, governance atlases, process-service maps, layered architectures, or multi-panel visual summaries; when a diagram must avoid overlap, truncation, generic repeated boxes, and semantically meaningless decoration; or when validating infographic SVGs before inclusion in METSI PDFs or HTML.
---

# METSI Reference-Grade Infographics

Create deterministic, source-grounded infographics at or above the quality of the approved Hotel Horizonte reference. Treat each infographic as an explanatory model, not as decoration.

## Mandatory preparation

Read these references completely before designing:

- `references/content-contract.md`
- `references/semantic-topologies.md`
- `references/visual-standard.md`
- `references/qa-checklist.md`

Use `assets/golden/hotel-horizonte-system.png` as the minimum visual-quality benchmark and `assets/golden/hotel-horizonte-system.svg` as the structural reference. Do not copy its content into unrelated diagrams.

## Workflow

1. Extract the semantic contract from the supplied text.
   - State the central claim in one sentence.
   - Identify the source sections supporting every visible label.
   - Define nodes, groups, relations, direction, boundary, and decision consequence.
   - Remove decorative concepts that cannot be traced to the source.
2. Choose the topology that best explains the claim.
   - Do not default to a four-box grid or a radial hub.
   - Select from the families in `references/semantic-topologies.md` or compose a justified hybrid.
3. Build the diagram as editable SVG.
   - Put connectors behind objects.
   - Reserve independent text lanes.
   - Keep labels outside object silhouettes unless the object explicitly contains the label.
   - Use ports and dotted routes to make endpoints unambiguous.
4. Create the complete review package.
   - Editable SVG.
   - High-resolution PNG preview.
   - HTML review page.
   - `alt-text.md`.
   - `content-manifest.json`.
   - QA report.
5. Run the deterministic validator:

   `python3 scripts/validate_infographic.py output.svg --manifest content-manifest.json`

6. Compare the rendered PNG with the golden benchmark for density, legibility, hierarchy, precision, and editorial finish.
7. Stop for visual approval before integrating the infographic into a PDF or replicating it across the course.

## Non-negotiable gates

Reject and revise any output with:

- overlapping text, connectors, ports, or objects;
- clipped, truncated, hyphenated, or mechanically broken words;
- duplicated or generic labels;
- ambiguous connector endpoints;
- labels not grounded in the source;
- decorative topology that does not encode the stated claim;
- four identical boxes used by habit rather than meaning;
- typography too small for normal paragraph-level reading;
- density or finish below the golden benchmark.

Never compensate for poor layout by shrinking text below the limits in the visual standard. Redesign the topology, split the infographic, or shorten labels without changing their meaning.

## Semantic fidelity

The visible diagram and `content-manifest.json` must agree. Every node and edge must have a unique identifier, a source-grounded label, and an explicit explanatory purpose. Connectors must represent a declared relation such as flow, dependency, authority, evidence, feedback, transformation, or boundary crossing.

Do not invent curricular claims. Preserve distinctions in the source even when visual simplification is necessary.

## Integration rule

This skill produces and validates infographic assets only. Do not rebuild or modify a complete course PDF unless the user separately approves the infographic set and asks for integration.
