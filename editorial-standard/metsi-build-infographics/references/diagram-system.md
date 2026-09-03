# METSI diagram system

## Measured visual tokens

At a 1280 px viewport, Gamma's central content is 855 px wide. Smart-layout cells use:

- Inter 18 px / 28.8 px, weight 400
- headings 22.5 px or 27 px, weight 700
- `#272525` text
- `#E6E6E6` fill with `#CCCCCC` 1 px border
- white outline cards with `#CCCCCC` 2 px border
- 6.3 px radius
- 18 px internal padding
- 18 px horizontal and vertical gutters

Common observed grids are 2×N and 3×N, but the reference series also uses cycles, connected system maps, radial structures, layered stacks, illustrated panels, and icon-led fields. Numbered lists may be borderless with an 18 px gap between the number and copy. Some outline-list cards use an 8 px left rule and `26px 18px` horizontal padding.

Type must be validated after embedding. For a 1344 px SVG displayed at 855 px, use 27–30 px body labels and 32–38 px node headings so the rendered text remains close to the document's 18 px body.

Prefer native HTML/CSS inside course documents. Native labels use the same 18 px body token directly and avoid scaling surprises. Reserve SVG for spatial maps that truly need a free canvas.

## Families

### grid

Use for 3–12 peer concepts, definitions, criteria, risks, or capabilities. Equal-width columns; row height follows the longest item.

### glossary

Use 3 columns for short term-definition pairs. Put a bold term above a single concise definition.

### steps

Use for 3–6 ordered actions. Place `01`, `02`, ... above or beside the text. Prefer two columns if explanations exceed one line.

Never force four paragraph-scale Spanish steps or five text-rich steps into one horizontal row. Calculate node height after wrapping. Use a 2×2 composition, a two-column serpentine path, vertical bands, or a 3+2 composition, with arrows confined to gutters rather than placed beneath text. Reject the layout if any unbroken word is wider than the available text lane.

### flow

Use for 3–7 nodes with one primary direction. Draw connectors first, then nodes. Label exceptional branches sparingly.

### comparison

Use two columns with matched rows. State the comparison axis in the section heading, not in every cell.

### timeline

Use for sequential phases or class progression. Favor horizontal for 3–5 stages and vertical for longer sequences.

### cycle

Use for 3–6 recurring states or feedback relationships. Arrange nodes on a ring and show direction with curved or tangent arrows.

### radial

Use when several dimensions orbit or qualify a central concept. Keep the center visually dominant and connect annotations with thin rules.

### hub

Use for a central system with 4–10 actors, inputs, outputs, or responsibilities around it. Allow asymmetric placement when it clarifies groups.

### layers

Use for nested boundaries, levels, stacks, or accumulated effects. Prefer concentric rings or isometric-looking flat stacks without gradients.

### system-map

Use for socio-technical structures, sources of evidence, channels, or dependencies. Combine two or three node shapes and dotted connectors; group related domains spatially.

Small circular nodes may contain an icon or a one-word identifier only. Place longer labels in independent exterior lanes or dynamically sized icon-led modules; never wrap a sentence inside a fixed-radius circle.

### assembly

Use when three to six sources, boundary choices, evidence streams, or criteria converge into one constructed outcome. Prefer quiet isometric modules, visible ports, dotted feeder paths, and one central assembled form.

### isometric-system

Use for the reference-grade structural language of the METSI evidence and socio-technical maps. Construct the scene from distinct axonometric objects—stacks, cylinders, actor rings, task panels, organization plates, open containers, ports, and small routing cubes—joined by quiet dotted paths. Keep labels horizontal and outside object faces. Use restrained stone, blue-gray, sand, and cyan accents only to distinguish roles. Each eligible full `N` document requires at least three diagrams from this family; rotate evidence funnel, socio-technical map, governance assembly, and process ecosystem variants.

Every item label must be a complete two- or three-word concept, preferably 28 characters or fewer. Omit item body copy by default. Add body copy only in a dedicated annotation lane that does not intersect an object, connector, port, or neighboring label. The central construct uses one or two words. Truncated sentences and ellipses are forbidden.

### orbit

Use for nested scopes or interacting dimensions around a central construct. Rings must encode meaning, not decoration. External annotations connect to specific rings with thin rules and large labels.

### atlas

Use for six to twelve related mechanisms that each merit a micro-diagram. Compose asymmetric panels connected by shared dotted routes and ports; do not render a uniform card matrix.

### icon-field

Use for four to six dimensions where a large line icon plus heading and short paragraph makes the relationship immediately scannable. Divide the field with quiet rules instead of filled cards.

### panels

Use for 3–6 related mechanisms that deserve different micro-diagrams. Separate panels with quiet dotted rules rather than identical cards.

## JSON schema

```json
{
  "type": "grid",
  "title": "Optional title",
  "subtitle": "Optional one-line framing",
  "columns": 3,
  "style": "filled",
  "width": 1344,
  "items": [
    {"number": "01", "title": "Fuente de verdad", "body": "Quién cierra el dato si hay conflicto."}
  ]
}
```

`type`: `grid`, `glossary`, `steps`, `flow`, `comparison`, `timeline`, `cycle`, `orbit`, `radial`, `hub`, `layers`, `system-map`, `isometric-system`, `assembly`, `atlas`, `icon-field`, or `panels`.

`style`: `filled`, `outline`, or `plain`.

For `flow`, items may include `next`, an array of zero-based target indexes. Without it, nodes connect in source order.

For `comparison`, provide `left_label`, `right_label`, and item objects with `left` and `right`.

## Content limits

- Canvas title: 65 characters preferred.
- Node title: 45 characters maximum preferred.
- Node body: 180 characters maximum; 90 preferred.
- Grid: no more than 12 nodes.
- Flow: no more than 7 primary nodes.

When limits are exceeded, split the diagram. Never solve excess content by dropping below 18 px body text at 1344 px width.

## Variety gate

- Do not use a four-box grid as the universal fallback.
- In a document with 3–5 diagrams, use at least three families.
- In a document with 6 or more diagrams, use at least four families.
- Never repeat one family more than twice in sequence.
- Include at least one relational family (`cycle`, `radial`, `hub`, `layers`, or `system-map`) when the source describes a system.
- A system boundary or socio-technical model with three or more interacting dimensions may not use a plain grid, checklist, or unconnected cards.
- At least one high-complexity family (`system-map`, `assembly`, `orbit`, `atlas`, or `icon-field`) is required when a full class contains a structural model.
- Each eligible `N` document contains at least three `isometric-system` diagrams and at least eight semantic line-icon motifs inside diagrams. It also receives separate icon-and-text editorial sections during document composition.

## Collision and surface gate

- Reject any text that touches or overlaps another label, node boundary, arrow, or connector.
- In `isometric-system`, reject any item title longer than three words, any truncated label, any body copy without its own annotation lane, and any central label longer than two words.
- Reject fixed-height nodes when their title/body line count is variable; all wrapped text must remain inside its node with full padding.
- In system maps, measure title lines before choosing the node rectangle. Keep at least 24 px of horizontal clearance, 20 px of vertical clearance, and a distinct icon lane. Five-node maps use a 3+2 composition; their central label sits in an opaque capsule separated from connectors and objects.
- Place arrows and connectors in explicit grid gaps or separate lanes; never beneath text.
- Use at least 75% of the available content width.
- Use 18 px body and 22.5–27 px headings in native HTML diagrams.
- On a stone parent card, set the diagram canvas to transparent and derive nodes from the same stone surface. White canvases and white nodes are forbidden. Medium-gray cards on `stone-dark` are also forbidden; use transparent white line art or relocate the diagram.
- Let HTML rows break between nodes in print. If an SVG produces more than 30% avoidable blank page area, rebuild it as HTML.
