# Visual standard

The approved visual language is editorial, technical, quiet, precise, and premium. Density comes from meaningful components and relations, not ornamental clutter.

## Canvas and palette

- Prefer a wide editorial canvas such as 1800 × 1100 with a viewBox.
- Background: warm off-white or stone (`#F6F4EE`, `#F2F0E9`, `#FFFFFF`).
- Primary ink: charcoal (`#2B2B2B` to `#4A4A4A`).
- Secondary lines: neutral gray (`#8B8B87`, `#C8C6BF`).
- Sparse accents only: muted blue-gray, pale cyan, sand, or beige.
- Never use saturated corporate blue, bright gradients, neon colors, or glossy effects.

## Typography

- Use Inter, Arial, Helvetica, or a compatible grotesk sans serif.
- Visible labels should read near normal paragraph size in the target PDF.
- In a 1800 × 1100 SVG, use approximately 22–34 px for labels, 34–48 px for section headings, and 48–68 px for the principal title when present.
- Never use font sizes below 14 px; prefer 18 px or more.
- Do not use CSS hyphenation, soft hyphens, nonbreaking hyphens, `overflow-wrap:anywhere`, or artificial word breaking.
- Do not truncate with ellipses. Rewrite the label or give it more space.

## Objects

- Use clean axonometric/isometric modules, layered slabs, open containers, panels, ports, and thin-line icons.
- Keep strokes consistent, generally 1.5–3 px at 1800 × 1100.
- Use subtle fill differences to indicate role, layer, state, or boundary.
- Avoid rounded white cards floating on gray fields unless the semantic role demands a container.

## Connectors

- Draw connectors behind nodes and labels.
- Prefer dotted or fine solid orthogonal/curved routes.
- Use visible ports or endpoint dots.
- Keep at least 14 px of clearance from text bounding boxes; prefer 24 px.
- Do not run lines through text, icons, or object faces.
- Make direction explicit with arrowheads only when the relation is directional.

## Spacing and density

- Use the canvas actively without crowding it.
- Maintain a deliberate visual rhythm: dense semantic clusters separated by calm gutters.
- Reserve text lanes before placing objects.
- Keep labels close enough to their objects to avoid ambiguity.
- Do not leave a large dead region created by undersized content.
- Do not shrink the whole diagram to solve local overflow.

## Accessibility

- Include `<title>` and `<desc>` and expose them through `aria-labelledby` with `role="img"`.
- Maintain strong contrast for all text.
- Do not encode a distinction using color alone.
- Write useful alt text describing the claim, topology, major components, and reading direction.
