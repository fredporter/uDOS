# Contributions Contract (v1.3)

Wiki-style updates are handled as **contribution bundles** (patches), not direct edits to curated notes.

## Bundle layout
```txt
_contributions/contrib_<id>/
  manifest.yml
  patch.diff
  notes.md
  signatures/   (optional)
```

## AI as contributor
AI must produce:
- patch.diff
- notes explaining changes
- run report referencing the contribution id
