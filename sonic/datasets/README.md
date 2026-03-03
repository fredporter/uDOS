# Sonic Screwdriver Device Database

This dataset is the public, portable device catalog used by Sonic Screwdriver.
It is designed to be human-editable and easy to redistribute.

Catalog entries may also point to open-box Obsidian-style Markdown templates for:
- configurable settings
- installers
- containers/services
- drivers/firmware

## Files

- `sonic-devices.table.md` — Primary Markdown table (human-editable)
- `sonic-devices.schema.json` — JSON Schema for validation
- `sonic-devices.sql` — SQLite schema + seed data
- `version.json` — Dataset version metadata

## Workflow

1) Edit `sonic-devices.table.md`
2) Validate against `sonic-devices.schema.json`
3) Compile SQLite:

```bash
sqlite3 memory/sonic/seed/sonic-devices.seed.db < sonic/datasets/sonic-devices.sql
```

Runtime split:
- seeded catalog: `memory/sonic/seed/sonic-devices.seed.db`
- local user overlay: `memory/sonic/user/sonic-devices.user.db`
- legacy compatibility mirror: `memory/sonic/sonic-devices.db`

The seed catalog stays read-only for normal users. Local device additions,
bootstrap records, and user-specific overrides belong in the user overlay DB.

## Notes

- Keep rows factual and reproducible.
- Use `unknown` for fields that are not yet verified.
- `windows10_boot`, `media_mode`, and `udos_launcher` are required capability fields.
  Use `unknown` when capability data is not yet verified.
- `wizard_profile` and `media_launcher` are optional planning fields used by
  Wizard/Sonic integration surfaces.
- `*_template_md` fields should point to versioned Markdown notes/templates, not hidden binary payloads.
- Template notes should stay Obsidian-style and operator-readable.
