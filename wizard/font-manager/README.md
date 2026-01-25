# Wizard Font Manager

Canonical font bundle for Wizard UI and tooling.

## Structure

```
wizard/font-manager/
├── fonts/
│   ├── manifest.json
│   ├── font-test.md
│   ├── retro/
│   └── emoji/
└── README.md
```

## Usage

- Wizard API serves fonts from `/api/v1/fonts/*` (see `wizard/routes/font_routes.py`).
- Wizard dashboard typography is driven by CSS variables:
  - `--font-prose-title`
  - `--font-prose-body`
  - `--font-code`
  - `--scale-prose-title`
  - `--scale-prose-body`
  - `--scale-code`
  - `--font-emoji`

Bundled fonts should be added under `wizard/font-manager/fonts/` and registered
in `wizard/font-manager/fonts/manifest.json`.
