# Repository contract

## Layout

```text
UBA-metsi/
├── .github/workflows/deploy-pages.yml
├── archive/
│   └── classes/<slug>-<timestamp>/
├── course/
│   └── classes/<slug>/
│       ├── index.html
│       ├── metsi.css
│       ├── document.json
│       ├── image-manifest.json
│       ├── images/
│       └── diagrams/
├── site/
│   ├── index.html
│   ├── metsi.css
│   ├── course-manifest.json
│   └── classes/<slug>/
├── course-manifest.json
└── publish-config.json
```

`course/` is the source-of-truth package for each class. `site/` is the GitHub Pages artifact. Keeping both makes the publication reproducible and prevents generated web output from replacing editable source material.

## Course manifest

```json
{
  "course": "UBA METSI",
  "repository": "UBA-metsi",
  "classes": [
    {
      "slug": "clase-03",
      "title": "Clase 3: ...",
      "path": "classes/clase-03/",
      "updated_at": "2026-08-14T12:00:00Z"
    }
  ]
}
```

Use stable lowercase slugs containing only letters, numbers, and hyphens. Update an existing manifest entry instead of adding duplicates.

## Visibility and licensing

The repository and Pages site are public. Do not include student personal data, private course administration, answer keys intended to remain restricted, proprietary readings, or third-party media without compatible permission.

Do not create a license file automatically. Ask the course owner separately whether the original course content should remain all-rights-reserved or use a specific open license.
