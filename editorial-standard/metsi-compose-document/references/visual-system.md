# METSI visual system

This file defines the legacy `web-cards` mode measured from the three Gamma documents. For N01–N46 print readings, use `magazine-print` and read `premium-magazine-system.md`; do not mix rounded Gamma cards into the print magazine.

## Evidence base

Measured from three reference Gamma documents at a 1280×720 viewport:

- 19, 18, and 18 document cards;
- page heights approximately 21,201 px, 28,694 px, and 23,237 px;
- card inner body width 981 px and primary content width 855 px;
- 63 px inner horizontal inset and 32 px top/bottom inset inside the 981 px card body;
- 10.8 px card radius;
- Inter for visible document content; `PPMori` appears on the application shell but is not the content face.

## Tokens

| Role | Value |
|---|---|
| canvas | `#FFFFFF` |
| cover | `#000000` |
| primary ink | `#272525` |
| pure black heading | `#000000` |
| secondary ink | `#4D4D4D` |
| tile | `#E6E6E6` |
| stone light | `#D0D0CE` |
| stone dark | `#2F2F2D` |
| border | `#CCCCCC` |
| quiet border | `#DFDFE0` |
| content face | `Inter, Arial, sans-serif` |
| body | `18px / 1.6`, weight 400 |
| cover title | `62.1px / 1.25`, weight 700 |
| major heading | `45px / 1.25`, weight 700 |
| section heading | `36px / 1.25`, weight 700 |
| subheading | `27px / 1.25`, weight 700 |
| small heading | `22.5px / 1.25`, weight 700 |
| card radius | `10.8px` |
| tile radius | `6.3px` |
| editorial photo ratio | `16:5` desktop/print; `16:7` mobile |
| tile padding/gap | `18px` |

## Layout

- Page background is white.
- Each card spans the page flow; its visible body is `min(981px, calc(100vw - 48px))`.
- Card content is `min(855px, calc(100% - 126px))` on desktop.
- Separate cards with a 32 px outer section gap. Use 32 px internal vertical padding for compact cards and 46 px for ordinary cards; reserve 64 px for deliberate airy cover or image cards.
- Keep heading-to-body gaps from 18–28 px and major block gaps from 32–48 px.
- Ordinary photographs use the full 855 px content measure, a panoramic `16:5` crop, `object-fit: cover`, focal-point-aware positioning, and a 10.8 px radius. On mobile, use `16:7` to preserve enough visual information. Infographics preserve their native aspect ratio and do not inherit the photographic crop.
- Use stone backgrounds on 15–30% of substantive cards. Confirm black or white foreground contrast at 4.5:1 or better.
- At desktop and print, an ordinary card should contain meaningful content through at least 45% of its internal height. Group short related sections instead of leaving accidental blank zones.

## Image rhythm

Use roughly one image in every 1.5–2 substantive cards, not in every card. Alternate pale negative-space images with dark high-contrast conceptual images. Keep the document-wide set cohesive rather than forcing identical exposure.

Audit saturation after final crop and rendering. Apply only manifest-declared treatments. Dedicated Hotel Horizonte case visuals use `assets/hotel-horizonte-reference.png`; every N-document ends with `assets/n-document-closing-matches.png`.

The set is mostly neutral but not entirely monochrome. When an N-document contains at least four ordinary photographs, target restrained color in 35–50% of them; with four ordinary photographs, use exactly two restrained-color images. Favor a single desaturated blue-green, cyan, sand, or amber family per image; use a recorded filter around `saturate(.28–.50) contrast(1.03–1.06)` when needed.

Surface pairing is mandatory: every ordinary restrained-color photograph belongs on a `white` card. Photography placed on `stone-light` or `stone-dark` must read neutral or grayscale. The fixed Hotel Horizonte reference is the only color photograph permitted on stone.

Do not display provenance notes for user-provided fixed assets. Keep rights and source fields in `image-manifest.json` only.

Ordinary photographs may carry one visible conceptual caption below the crop. Write it as a brief editorial assertion that deepens the adjacent section; never as a descriptive alt-text duplicate or a provider/photographer credit. Render it at 12.6px, weight 300, line-height 1.45—visually quieter than body copy and never bold. Keep stock-bank and creator attribution in the manifest unless a selected license explicitly requires another presentation.

Native diagrams inherit the parent background. On stone cards use transparent canvases and darker/lighter stone-derived nodes; never white panels or white objects. The closing matches image uses a dedicated full-page card with alternative text, one brief conceptual caption, and the standard folio and footer rule, but no large reflective quote.

Do not place medium-gray tiles over `stone-dark`; this produces a muddy gray-on-gray field. Use transparent white line art, or put high-information structural diagrams on white/stone-light. Large line-icon fields use black strokes on light surfaces and white strokes on dark surfaces.

Icon-led editorial text is a separate document rhythm from diagrams. Arrange 3–6 large outline icons beside headings and paragraph-scale copy on an open surface, with no surrounding tiles or connector lines. Every full N-document uses at least two such sections; diagram icons do not satisfy this requirement.

## Responsive rules

- At 900 px: reduce card/content insets and scale titles with `clamp()`.
- At 720 px: all grids become one column; card radius may reduce slightly; body remains at least 17 px.
- Complex fixed-topology SVGs may become horizontally scrollable below 720 px with a 760 px minimum canvas, so labels remain paragraph-scale. The scroll container must not widen the document viewport.
- Print: allow native diagram rows to break between nodes, keep each node intact, prevent isolated headings, and reject ordinary pages with more than 40% avoidable white area. When a card fragments, clone its vertical box decoration and restore at least 7 mm of top inset on every continuation page. Keep each paragraph and list item intact unless it cannot fit on a fresh page. The final closing image occupies one complete page.
