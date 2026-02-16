# Vault Contract (v1.3)

Vault is plain files. Obsidian can open it. No hidden state required.

## Template/Seed/Runtime Split

- `vault/` — distributable markdown scaffold (tracked, no personal data)
- `core/framework/seed/vault/` — canonical starter vault seed (tracked)
- `memory/vault/` — runtime user vault (local, gitignored)

Seed installers (`bin/install-seed.py` / `REPAIR --seed`) copy starter markdown from
`core/framework/seed/vault/` into `memory/vault/`.

## Recommended layout (can map to existing repo folders later)
```txt
memory/vault/
  01_KNOWLEDGE/
  02_PROJECTS/
  03_PROMPTS/
  04_TASKS/
  05_DATA/sqlite/
  06_RUNS/
  07_LOGS/
  _templates/
```

## Write-back rules
- Runtime must not silently overwrite curated notes.
- Outputs:
  - run reports → `06_RUNS/`
  - logs → `07_LOGS/`
  - proposed edits → contributions (diff bundles)

## Links
- `[[Wiki Links]]` are allowed.
- Add stable `id:` in frontmatter where identity matters.
