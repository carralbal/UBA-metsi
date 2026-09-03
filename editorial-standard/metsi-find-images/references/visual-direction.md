# METSI image direction

## Target impression

Academic, contemporary, conceptual, restrained, intelligent, slightly cinematic. Images carry emotional and conceptual depth while the surrounding document stays monochrome and systematic.

## Observed image families

1. **Human scale and negative space** — small or silhouetted people in large architectural, gallery, landscape, or abstract environments.
2. **Networks and systems** — nodes, lines, paths, grids, traces, cables, constellations, maps, swarms, or repeated modules.
3. **Order versus complexity** — tangled lines, particles, intersecting paths, dense marks, light trails, or controlled chaos against a simple ground.
4. **Socio-technical tension** — people observing, collaborating around, or being contrasted with technological or mechanical forms.
5. **Operational context** — hotels, workspaces, whiteboards, service environments, or evaluation scenes photographed with an editorial rather than advertising sensibility.

## Color and tonal profile

- Document-wide target for ordinary photography: 50–65% neutral/near-monochrome and 35–50% restrained accent.
- Saturation: low to moderate; reject broad areas of vivid multi-color.
- Contrast: medium-high or high; black/white figure-ground images are common.
- Brightness may alternate: pale high-key negative-space images and black-background fine-art images both fit.
- Accent allowance: one dominant amber, cyan, or desaturated blue-green hue; do not mix several saturated hues.
- Texture: photographic grain, natural shadow, real materials, light drawing, paper, concrete, glass, or projection.

## Saturation gate

Inspect every final crop at its display size, not only the source thumbnail. Record one of `neutral`, `restrained-accent`, or `too-saturated`. A final set passes only when:

- at least 50% of ordinary images are `neutral` or visually monochrome;
- no untreated image contains a dominant vivid orange, red, green, or multicolor field;
- any `restrained-accent` image uses one subdued hue and still belongs beside the neutral set;
- an otherwise excellent source that is slightly too warm may receive a documented CSS treatment such as `saturate(.35) contrast(1.04)`, but filters never rescue a weak concept or composition.
- a full N-document with four or more ordinary photos uses restrained color in 35–50% of ordinary photos; with four ordinary photos, exactly two are `restrained-accent` and the remainder read neutral or near-monochrome;
- every ordinary `restrained-accent` photo is assigned to a `white` card; ordinary photos on `stone-light` or `stone-dark` are neutral or grayscale. The fixed Hotel Horizonte reference is the sole exception.

Review contact sheets for set-level consistency. Recheck images after HTML and PDF rendering because browser color and crop can change the perceived saturation.

## Composition

- Prefer one dominant idea and a clear focal hierarchy.
- Preserve 25–60% negative space when possible.
- Favor asymmetry, aerial viewpoints, silhouettes, long shadows, cropped scale, or centered abstract systems.
- Avoid text baked into the image, visible brands, watermarks, UI screenshots, and busy backgrounds.
- Ensure the intended crop works at a content width of 855 px. Common display ratios are 3:2, 16:9, 4:3, and occasional 2:3 portrait.

## Query construction

Build each English query as:

`[conceptual subject] + [visual metaphor] + [composition] + [tone/style]`

Useful modifiers:

- `conceptual editorial`, `fine art photography`, `minimal`, `negative space`
- `silhouette`, `aerial`, `long shadow`, `gallery installation`
- `interconnected lines`, `nodes`, `data flow abstract`, `light trails`
- `black background`, `monochrome`, `neutral tones`, `muted cyan`
- `human observing`, `team abstract cinematic`, `system complexity`

Do not over-constrain a single query. Create 3–5 variants that change the metaphor, not just synonyms.

## Candidate rating fields

Rate each 0–1:

- `concept_match`: expresses the section's core tension.
- `editorial_quality`: feels authored, not commodity stock.
- `negative_space`: supports calm composition and cropping.
- `contrast_match`: clear figure/ground and tonal structure.
- `palette_match`: neutral or a single restrained accent.
- `saturation_control`: remains neutral at the final crop and display treatment.
- `crop_flexibility`: survives the requested aspect ratio.
- `series_cohesion`: belongs beside the already selected images.
- `literalness_penalty`: 1 means overly literal/clichéd.
- `stock_cliche_penalty`: 1 means staged corporate-stock behavior.
- `license_risk_penalty`: 1 means unclear or incompatible rights.
