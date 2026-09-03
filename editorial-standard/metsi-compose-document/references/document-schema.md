# Document JSON schema

```json
{
  "meta": {
    "title": "METSI Clase 3",
    "lang": "es",
    "mode": "magazine-print",
    "description": "...",
    "image_manifest": "image-manifest.json"
  },
  "cards": [
    {
      "type": "cover",
      "layout": "cover-editorial",
      "image": "images/cover.jpg",
      "focal": "50% 45%",
      "eyebrow": "METSI",
      "discipline": "Metodología de Sistemas de Información",
      "title": "Clase 3: ...",
      "lead": "..."
    },
    {
      "type": "content",
      "title": "Propósito",
      "title_source_id": "src-001",
      "layout": "article-2col",
      "spread_id": "spread-02",
      "page_side": "left",
      "kicker": "N01 · MÉTODO",
      "accent": "rust",
      "variant": "stone-light",
      "density": "compact",
      "blocks": [
        {"kind": "paragraph", "source_id": "src-002", "text": "..."},
        {"kind": "bullets", "items": [{"source_id": "src-003", "text": "..."}]},
        {"kind": "image", "src": "images/purpose.jpg", "alt": "...", "caption": "Lo que queda fuera del encuadre también modifica la decisión.", "treatment": "desaturate-soft"},
        {"kind": "infographic", "src": "diagrams/model.svg", "alt": "..."},
        {"kind": "diagram", "family": "sequence", "title": "...", "items": [{"number": "01", "title": "...", "body": "..."}]},
        {"kind": "icon-text", "title": "...", "items": [{"icon": "people", "title": "Personas", "body": "Quién conoce, decide o recibe el impacto."}]},
        {"kind": "grid", "columns": 3, "style": "filled", "items": [{"title": "...", "body": "..."}]},
        {"kind": "columns", "columns": 2, "items": [{"blocks": [{"kind": "paragraph", "text": "..."}]}]},
        {"kind": "quote", "text": "..."},
        {"kind": "subheading", "text": "..."}
      ]
    }
  ]
}
```

Supported block kinds: `paragraph`, `bullets`, `numbered`, `image`, `infographic`, `diagram`, `icon-text`, `grid`, `columns`, `quote`, `subheading`, `table`, `code`, and `links`.

Use `table` with `headers` and `rows`; every header or body cell may carry its own stable `source_id`. Use `code` with `text`, optional `language`, and a block-level `source_id`. Never flatten Markdown tables or fenced code into ordinary paragraphs: render them as semantic HTML so their content remains legible in responsive HTML and PDF.

`icon-text` is an editorial text composition, not a diagram. Use 3–6 items with large outline icons, 22.5–27 px headings, and 18 px body copy; no filled cards, borders, arrows, or connectors. Supported semantic icon names include `people`, `structure`, `technology`, `tasks`, `database`, `voice`, `repair`, `rules`, `decision`, `evidence`, and `impact`. Every full N-document requires at least two such sections outside diagrams.

High-fidelity `infographic` blocks may declare `family`: `system-map`, `isometric-system`, `assembly`, `orbit`, `atlas`, or `icon-field`, plus `source_spec` pointing to their editable JSON. These families are preferred over native box diagrams for structural models. `isometric-system` specs also declare a `variant` such as `evidence`, `sociotechnical`, `governance`, or `ecosystem`.

Native `diagram.family`: `bands`, `cycle`, `sequence`, `transfer`, `layers`, `comparison`, `hub`, `checklist`, or `panels`. Items use `number`, `title`, and optional `body`; transfer/comparison items may use `left` and `right`. Native diagrams inherit the parent card surface.

Content cards support `variant`: `white`, `stone-light`, or `stone-dark`; and `density`: `compact`, `normal`, or `airy`. Use `airy` only for a deliberate image or statement card.

For `meta.mode: "magazine-print"`, every page/card also declares:

- `layout`: `section-opener`, `article-2col`, `article-3col`, `article-rail`, `editorial-frame`, `mosaic-essay`, `portrait-profile`, `panorama-bottom`, `hero-page`, `accent-column`, `diagram-feature`, `case-dark`, or `closing-fullbleed`;
- `spread_id`: stable identifier shared by the left/right page pair;
- `page_side`: `left` or `right` when the spread plan fixes the side;
- optional `kicker`, `folio_label`, `accent`, and `running_title`.

Magazine image blocks may declare `role`: `hero`, `portrait`, `rail`, `panorama`, `mosaic-dominant`, `mosaic-secondary`, `evidence`, `texture`, or `pause`; and `span`: integer 1–6 matching the page grid. Images remain rectangular and align to the declared span.

Magazine-only block kinds:

- `kicker`: short sans-serif section label;
- `deck`: one- or two-sentence article introduction;
- `pullquote`: source-grounded quotation or editorial thesis;
- `rule`: horizontal or vertical editorial rule;
- `mosaic`: 3–6 image items with one declared `dominant: true`;
- `note`: framed definition, method test, counterexample, or worked example;
- `dropcap-paragraph`: paragraph with a four- or five-line initial.

Keep semantic text in JSON. Do not insert raw HTML.

Eligible source-bearing blocks and card titles must include a stable `source_id` or `title_source_id`. Generated visual labels and captions do not receive source IDs.

Image `treatment`: `none`, `desaturate-soft`, `restrained-color-strong`, `desaturate-strong`, or `grayscale`. The value must agree with the image manifest. Ordinary restrained-color images belong only on `white`; stone cards require neutral/grayscale photography except for the fixed Hotel Horizonte reference.

Image `caption` is optional visible editorial copy. Use a 6–18 word Spanish sentence that interprets or tensions the concept beside the image. Do not put creator, provider, license, source URL, `Foto:`, `Fuente:`, Pexels, Unsplash, Pixabay, Wikimedia, or production provenance in this field. Store all provenance in the image manifest.

Set `role: "closing-image"` on the final N-document card. Its single image block must use the canonical burned-matches asset, provide explicit `alt` and a brief conceptual `caption`, render full-page, and preserve the standard folio and footer rule. It omits the large reflective quote used on internal pauses. The two internal full-page `pause` images are separate cards and do not satisfy or replace this closing role.

`grid.style`: `filled`, `outline`, or `plain`.

`grid.columns`: 2 or 3 preferred; 4–5 only for very short content.

Use semantic text, not raw HTML. The renderer escapes all content.
