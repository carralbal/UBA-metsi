# Sources and licensing

## Preferred sources

Use the source's own search and detail pages when possible:

- Unsplash
- Pexels
- Pixabay
- Wikimedia Commons for clearly identified public-domain or compatible Creative Commons works
- Public institutional image libraries with explicit reuse terms

Treat “free premium” as a quality goal, not a license category.

## Verification

For each selected image, verify on the source page at selection time:

1. creator identity;
2. source detail-page URL;
3. stated license or terms URL;
4. whether attribution is required or recommended;
5. whether people, trademarks, artworks, or private property introduce an additional use concern;
6. whether the downloaded derivative is permitted.

Licensing changes. Do not rely on remembered terms. Do not treat search snippets, reposts, CDN URLs, or Gamma proxy URLs as license evidence.

## Manifest schema

```json
{
  "section_id": "purpose",
  "source": "Unsplash",
  "source_page": "https://...",
  "creator": "Name",
  "license_name": "Source license",
  "license_url": "https://...",
  "download_url": "https://...",
  "local_file": "images/purpose.jpg",
  "width": 2400,
  "height": 1600,
  "crop": "3:2 center 46% 52%",
  "alt": "...",
  "saturation_review": "neutral | restrained-accent | too-saturated",
  "treatment": "none | CSS filter string",
  "approved": true,
  "selected_at": "YYYY-MM-DD"
}
```

For a user-provided fixed reference asset, use `source: "user_provided_reference"`, preserve the original local filename and hash, and set `publication_rights_confirmed` explicitly. Do not infer public reuse rights from the upload itself.
