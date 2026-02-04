# Theme Pack Contract (v1.3)

uDOS supports multiple “skins” by wrapping rendered Markdown HTML in a theme shell.

## Theme pack structure
```txt
themes/<theme-id>/
  shell.html
  theme.css
  theme.json
  assets/
```

## shell.html slots
- `{{title}}`
- `{{content}}`  (rendered Markdown HTML)
- `{{nav}}`      (optional)
- `{{meta}}`     (optional)
- `{{footer}}`   (optional)

## theme.json (v0)
```json
{
  "id": "prose",
  "name": "Tailwind Prose",
  "mode": "article",
  "contentClass": "prose",
  "notes": "Baseline theme for Markdown output."
}
```

## Special lanes
- `mode=slides`: Marp pipeline
- `mode=forms`: JSON/schema to UI (optional)
