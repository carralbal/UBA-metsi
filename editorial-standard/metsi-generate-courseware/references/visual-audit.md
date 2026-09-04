# METSI magazine reference audit

## Reference finding

The four supplied premium references behave as publications, not as collections of cards. Their consistency comes from stable grid, typography, folios, rules, palette, and photographic direction while the page compositions rotate according to the article.

## Page and spread grammar

- A4 portrait pages are designed in facing pairs.
- Six columns per page and twelve per spread provide the alignment system.
- Every spread has one dominant visual mass, one secondary mass, and one support zone.
- Outside margins and folios remain stable. Inner gutters are respected; images may bleed only when their role is hero or visual pause.
- Dense pages use two or three narrow reading columns rather than oversized body text.
- White space is shaped by alignment and hierarchy. Large unused lower halves are defects unless the entire page is an intentional hero composition.

## Recurring composition families

- editorial cover with full-bleed image and typographic masthead;
- section opener with folio, kicker, title, deck, and multi-column article;
- article with narrow image/evidence rail;
- framed editorial letter or methodological test;
- modular image mosaic with a short analytic block;
- tall portrait profile with side article and small-image rail;
- upper article plus lower panorama;
- full-page or full-spread hero image;
- real accent column carrying substantive text;
- compact diagram feature integrated into the article;
- dark case opener;
- image-only full-bleed close.

## Typography

- High-contrast serif: cover, article title, section number, pull quote, drop cap.
- Reading serif: long-form paragraphs and substantial captions.
- Editorial sans: kickers, metadata, folios, labels, tables, running matter, and compact diagram text.
- Body size does not jump between neighboring narrative pages. Variation comes from column width, role, scale, case, and weight.

## Photography

- Photographs form a series and carry semantic roles.
- Crops are rectangular and locked to the column grid.
- One photograph dominates the spread; secondary images are smaller or monochrome.
- Hero, portrait, rail, panorama, mosaic, inset, texture, and pause are distinct roles.
- Rounded corners, drop shadows, floating postcard frames, and one repeated panoramic band are absent.
- Text overlays occur only on verified quiet zones with sufficient contrast.

## Cover audit

- Verify that the source photograph was conceived natively in black and white and that its manifest records that origin. A grayscale rendering filter is a blocking defect, not a substitute for monochrome art direction.
- Inspect the source photograph and the composed PDF cover as separate artifacts. Confirm that mid-grays, highlights, textured shadows and local subject separation survive composition.
- Use a scrim only as a local contrast correction behind specific copy. Reject a uniform dark veil and any combination of low source exposure plus overlay that crushes the image.
- Measure contrast on every independent text zone, including masthead, both metadata blocks, kicker, title and thesis. Prefer changing light text to dark ink on a naturally light quiet zone over darkening the entire photograph.
- Rasterize the final PDF page and verify full bleed at all four media-box edges. A CSS declaration alone does not prove the absence of a paper-colored halo.
- Compare all covers in the current block on one contact sheet so an isolated acceptable image cannot create an excessively dark or repetitive sequence.
- Inspect the tagged PDF, not only the HTML `alt` attribute. Chromium may omit a cover image from the structure tree when a CSS image filter is active. Require an actual page-one `/Figure` with the approved `/Alt`; if a tonal adjustment is needed, use a native tonal asset or a neutral substrate plus controlled opacity and repeat the semantic audit.

## Color and detail

- White or warm paper, black ink, cool gray fields, and one controlled section accent.
- Saturated color is concentrated in one event rather than scattered.
- Thin rules, frames, circles, signatures, or drop caps are editorial devices, not decoration quotas.
- Infographics are mostly monochrome and compact. Their topology changes with the concept.

## Rhythm

The references alternate dense article, mixed article/image, rail or mosaic, and visual pause. The successful pattern is controlled asymmetry: facing pages differ, but their masses, baselines, rules, and accent create one spread.

## Legacy note

The earlier 981/855 px Gamma-card system remains available only for explicit `web-cards` requests. It must not determine the print-magazine composition.
