# uDOS Documentation Index

Updated: 2026-02-15

This is the canonical entry point for repository documentation.

## Start Here

- Product roadmap: `docs/roadmap.md`
- Sonic standalone release/install: `docs/howto/SONIC-STANDALONE-RELEASE-AND-INSTALL.md`
- Command reference (canonical): `docs/howto/UCODE-COMMAND-REFERENCE.md`
- Commands index: `docs/howto/commands/README.md`
- Wizard command ownership: `docs/howto/commands/wizard.md`
- Decisions index: `docs/decisions/`
- Specs index: `docs/specs/`

## Documentation Flow

1. Root orientation: `README.md`, `QUICKSTART.md`, `INSTALLATION.md`
2. Runtime command surface: `docs/howto/UCODE-COMMAND-REFERENCE.md`
3. System boundaries and contracts: `docs/specs/`, `docs/decisions/`
4. Component docs:
- Core: `core/README.md`
- Wizard: `wizard/README.md`
- Sonic: `sonic/README.md`
- Library: `library/README.md`
- Extensions: `extensions/README.md`
- Empire: `empire/README.md`

## Archive Policy

Historical and superseded docs are moved under `docs/.archive/` with dated folders.

Current archive updates:
- `docs/.archive/2026-02-11-roadmap-consolidation/`
- `docs/.archive/2026-02-15-docs-cleanup/`
- `docs/.archive/2026-02-17-legacy-docs/`

Legacy command pages in `docs/howto/commands/` now contain redirect stubs.
Archived full content lives under `docs/.archive/2026-02-17-legacy-docs/howto/commands/`.
