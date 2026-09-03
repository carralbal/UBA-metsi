---
name: metsi-find-images
description: Curate existing premium-looking, free-to-use stock photography for METSI educational documents without generating images. Use when Codex must search Unsplash, Pexels, Pixabay, Wikimedia Commons, or another verified free image bank; reproduce the METSI conceptual/editorial image language; create image briefs and search queries; rank candidates by tone, composition, brightness, saturation, negative space, and licensing; or deliver an attribution manifest for courseware.
---

# METSI Find Images

Find existing images; never generate or synthesize them.

## Workflow

1. Read `references/visual-direction.md` completely.
2. Read `references/source-and-license-policy.md` before searching or downloading.
3. Convert each section into one visual idea, not a literal list of nouns.
4. Search at least two approved banks. Prefer English queries; add Spanish only for locally specific subjects.
5. Build a shortlist of 4–8 candidates per slot. Inspect the full image, not only the thumbnail.
6. Record candidate metadata and human ratings from 0 to 1 in JSON. Run:

   `python3 scripts/rank_candidates.py candidates.json --output ranked.json`

7. Select one primary and one fallback per slot. Compare provider asset ID, source-page URL, and downloaded SHA-256 against the course-level `image-registry.json`. Every non-fixed photograph must be unique across N01–N46; only the approved Hotel Horizonte and matches-closing assets may repeat.
8. Download the chosen original or a derivative at least 1600 px on the long edge when permitted.
9. Measure or visually audit saturation at the actual crop. Record `saturation_review`, `treatment`, and `approved` in the manifest. Reject or neutralize images that read warmer or more colorful than the reference series.
10. Update the course registry and deliver `image-manifest.json` with provider asset ID, source page, creator, license/terms URL, download URL, SHA-256, crop, alt text, section ID, and saturation review. Any duplicate ID, URL, or hash is a blocking failure even when filenames differ.
11. Write one optional `editorial_caption` per selected image: a concise, forceful Spanish sentence that advances the section's concept. Keep creator, provider, source, and license only in the manifest; do not turn provenance into visible footer copy unless the license legally requires an on-page credit.

## Non-negotiable match rules

- Favor conceptual editorial photography, fine-art abstraction, systems/network metaphors, human silhouettes, scale, distance, motion traces, grids, light paths, architecture, and deliberate negative space.
- For METSI scenes of universities, students, teaching, professional work, or organizations without an explicitly foreign setting, require a credible Argentine or Latin American context. Evaluate casting together with architecture, clothing, objects, and institutional atmosphere; never infer regional fit from skin tone alone. Reject generic North American or European campus/corporate imagery even when it is visually polished.
- Keep the document-wide image set mostly monochrome or neutral. Permit restrained warm amber, cyan, or muted blue-green accents in 35–50% of ordinary images.
- Favor strong figure/ground contrast and uncluttered compositions. Reject glossy corporate stock, smiling-at-camera teams, staged handshakes, neon cyberpunk, dense dashboards, clip art, 3D icons, and generic laptop closeups.
- Match the semantic tension of the section: isolation/connection, order/complexity, evidence/ambiguity, human/technical, flow/friction, or control/change.
- Use landscape images for ordinary cards and portrait/fine-art images only when the composition earns the additional height.
- Prefer a naturally restrained source. A reversible CSS desaturation treatment is allowed only after the image is otherwise an excellent semantic and compositional match; record the exact filter in the manifest.
- Review the whole image set together. At least 50% must read neutral or near-monochrome, and no untreated image may introduce a large vivid warm or multi-color field.
- Do not force the whole document into grayscale. When a full N-document has four or more ordinary photos, curate restrained color in 35–50% of them; with four ordinary photos, select exactly two `restrained-accent` sources with a single muted dominant hue.
- Record the destination card for every image candidate. Ordinary `restrained-accent` photographs may be placed only on `white`; stock photography assigned to `stone-light` or `stone-dark` must be neutral or grayscale. The fixed Hotel Horizonte reference is the sole color-on-stone exception.
- When the course defines a recurring case image, reuse that exact asset every time a dedicated case visual is required. Label it `user_provided_reference` and confirm publication rights before public deployment.
- Across N-documents, never reuse ordinary stock photography. Visual continuity comes from art direction and treatment, not repeated files.
- For recurring fictional people, visually compare the complete portrait set and reject copies, near-duplicates, or sibling-like faces unless the narrative explicitly defines a family relationship. File IDs and hashes are insufficient identity checks.
- Never use visible captions such as `Foto: Nombre · Pexels`, `Fuente: Unsplash`, or another production credit. Visible captions are conceptual editorial sentences, not provenance labels.

## Search output contract

For every slot, return:

- `section_id`, `concept`, `query_pack`
- primary and fallback candidate with source-page URLs
- creator and license/terms evidence
- width, height, orientation, recommended crop and focal point
- concise alt text that describes content, not mood alone
- saturation assessment at the intended crop and any reversible display treatment
- match score plus one-sentence rationale
- `editorial_caption`: 6–18 words, assertive rather than descriptive, and not redundant with the alt text

Never claim an image is free merely because it appears in search results. Never use a CDN URL as the only provenance record.
