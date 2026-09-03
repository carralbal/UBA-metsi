# QA checklist

## Semantic QA

- [ ] One clear central claim.
- [ ] Every visible label maps to the manifest and source.
- [ ] Every connector has a declared relation and meaning.
- [ ] Node roles are visually distinguishable.
- [ ] No invented, repeated, or filler concepts.
- [ ] Topology explains the source rather than decorating it.
- [ ] Removal of any major element would change the explanation.

## Layout QA

- [ ] No text overlaps lines, ports, icons, or objects.
- [ ] No connectors cross labels.
- [ ] No clipping at the SVG viewBox boundary.
- [ ] No ellipses, truncated labels, or mechanically hyphenated words.
- [ ] Labels remain readable at the final PDF size.
- [ ] Endpoints and direction are unambiguous.
- [ ] Connectors render behind nodes.
- [ ] No unused large dead zones.
- [ ] No repeated four-box or radial pattern without semantic justification.

## Visual QA

- [ ] Warm neutral background and restrained accent palette.
- [ ] Consistent line weight and corner geometry.
- [ ] Axonometric shapes have coherent perspective.
- [ ] Density and finish meet or exceed the golden PNG.
- [ ] The diagram feels editorial and technical, not like a generic slide template.
- [ ] No highly saturated, glossy, or decorative styling.

## Output QA

- [ ] SVG is editable and contains title/description accessibility metadata.
- [ ] PNG preview is high resolution and visually inspected.
- [ ] HTML review page renders without overflow.
- [ ] `content-manifest.json` validates.
- [ ] `alt-text.md` is complete.
- [ ] Validator exits successfully.
- [ ] User approved the infographic set before PDF integration.
