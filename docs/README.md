# uDOS Documentation Index

Updated: 2026-03-03

This is the canonical entry point for repository documentation.

## Start Here

- Product roadmap: `docs/roadmap.md`
- Workflow architecture decision: `docs/decisions/v1-5-workflow.md`
- Workflow archive redirect: `docs/v1-4-workflow-PLAN.md`
- Consolidated release notes: `docs/releases/v1.4.4-release-notes.md`
- Specs catalog (main + detailed): `docs/specs/README.md`
- Integration readiness: `docs/specs/INTEGRATION-READINESS.md`
- Sonic standalone release/install: `docs/howto/SONIC-STANDALONE-RELEASE-AND-INSTALL.md`
- Command reference (canonical): `docs/howto/UCODE-COMMAND-REFERENCE.md`
- Offline operator runbook: `docs/howto/UCODE-OFFLINE-OPERATOR-RUNBOOK.md`
- Commands index: `docs/howto/commands/README.md`
- Wizard command ownership: `docs/howto/commands/wizard.md`
- Decisions index: `docs/decisions/README.md`
- Specs index: `docs/specs/`

## Documentation Flow

1. Root orientation: `README.md`, `QUICKSTART.md`, `INSTALLATION.md`, `wiki/Home.md`
2. Runtime command surface: `docs/howto/UCODE-COMMAND-REFERENCE.md`
3. System boundaries and contracts: `docs/specs/`, `docs/decisions/`
4. Workflow execution direction: `docs/decisions/v1-5-workflow.md`, `docs/roadmap.md`
5. Component docs:
- Core: `core/README.md`
- Wizard: `wizard/README.md`
- Sonic: `sonic/README.md`
- Library: `library/README.md`
- Extensions: `extensions/README.md`
- Empire: `empire/README.md`

## Archive Policy

Historical and superseded docs are moved under `/.compost` with dated folders.

Current archive updates:
- `/.compost/<date>/archive/docs/.archive/2026-02-11-roadmap-consolidation/`
- `/.compost/<date>/archive/docs/.archive/2026-02-15-docs-cleanup/`
- `/.compost/<date>/archive/docs/.archive/2026-02-17-archived-docs/`

Legacy command pages in `docs/howto/commands/` now contain redirect stubs.
Archived full content lives under `/.compost/<date>/archive/docs/.archive/2026-02-17-archived-docs/howto/commands/`.

`docs/.archive/` itself is local-only and untracked.

Compost runtime policy reference: `docs/COMPOST-POLICY.md`.
