# uDOS Specs Catalog

Updated: 2026-03-05
Release baseline: v1.5 rebaseline

This index organizes main specs and detailed specs under `docs/specs/`.

## Main Specs (Canonical)

- `docs/specs/wiki_spec_obsidian.md` — Wiki authoring/profile spec
- `docs/specs/UCODE-COMMAND-CONTRACT-v1.3.md` — command contract baseline
- `docs/specs/GAMEPLAY-COMMAND-CONTRACT-v1.5.md` — canonical gameplay/lens/skin command contract
- `docs/specs/RUNTIME-INTERFACE-SPEC.md` — runtime interface
- `docs/specs/PORT-REGISTRY.md` — shared port ownership
- `docs/specs/PLUGIN-MANIFEST-SPEC.md` — extension/plugin manifest
- `docs/specs/GHOST-MODE-POLICY.md` — ghost mode policy
- `dev/docs/specs/DEV-WORKSPACE-SPEC.md` — `@dev` workspace and Dev Mode behavior
- `docs/specs/3DWORLD-EXTENSION-CONTRACT-v1.5.md` — canonical 3D extension boundary and integration contract
- `docs/specs/WORKFLOW-SCHEDULER-v1.5.md` — core workflow scheduler contract for v1.5
- `docs/specs/OFFLINE-ASSIST-STANDARD-v1.5.md` — canonical offline assist and `uLogic` standard for v1.5, grounded in the `udos_ulogic_pack` reference scaffold
- `docs/specs/LOGIC-INPUT-HANDLER-v1.5.md` — canonical smart logic input handler contract for the refactored v1.5 `ucode` shell
- `docs/specs/WORKFLOW-MANAGER-CONTRACT-v1.5.md` — canonical cross-surface workflow manager contract for core, Wizard, and offline logic
- `docs/specs/KNOWLEDGE-BANK-RUNBOOK-STANDARD-v1.5.md` — canonical librarian content, seed/local split, and Markdown runbook/template standard
- `docs/specs/PYTHON-RUNTIME-OPERATIONS-v1.5.md` — canonical `.venv`/`uv`/pytest operating contract for v1.5
- `docs/specs/UHOME-v1.5.md` — canonical v1.5 home profile runtime and Sonic install contract
- `docs/specs/FORMATTING-SPEC-v1.4.md` — canonical formatting and `.compost` archival contract
- `docs/specs/TYPESCRIPT-MARKDOWN-RUNTIME-CONTRACT.md` — active TypeScript markdown runtime contract
- `docs/specs/PACKAGING-RELEASE-CONTRACT-v1.5.md` — active packaging and release contract
- `docs/specs/ALPINE-CORE-PLUGIN-FORMAT-v1.5.md` — canonical Alpine core and plugin packaging contract for v1.5
- `docs/specs/THIN-GUI-EXTENSION-CONTRACT-v1.5.md` — canonical Thin GUI extension boundary and core bridge command contract
- `docs/specs/SPATIAL-GRID-CONTRACT.md` — active spatial grid and text-graphics contract
- `docs/specs/UCODE-DISPATCH-CONTRACT.md` — active input-dispatch and routing contract
- `docs/specs/INTEGRATION-READINESS.md` — active integration readiness summary
- `docs/specs/MINIMUM-SPEC-DEV-MODE-UCODE.md` — active minimum runtime pathway contract
- `docs/specs/UCODE-SELECTOR-INTEGRATION-BRIEF.md` — supporting selector brief for the v1.5 `ucode` TUI
- `docs/specs/DOCUMENTATION-CANONICAL-MAP.md` — current docs assessment and canonical ownership map

## Detailed / Historical Execution Specs

- `docs/specs/v1.3.*.md` — stabilization rounds and bridge contracts
- `docs/specs/v1.4.0-*.md` — v1.4 execution artifacts consolidated by v1.4.3 notes
- `docs/specs/03-contributions-contract.md` — historical contribution-bundle contract snapshot
- `docs/specs/WIZARD-WEB-PUBLISH-SPEC-v1.3.15.md` — wizard publish contract
- `docs/specs/TOYBOX-*.md` and legacy gameplay/lens specs — historical scaffolds and migration references
- `docs/specs/Spatial-*.md` and numbered specs (`01-*`, `02-*`, etc.) — architecture and schema details

## Release Context

- `docs/releases/v1.4.3-release-notes.md` — consolidated v1.4+ release notes
- `docs/STATUS.md` — public status page
- `docs/specs/V1-5-SHAKEDOWN-CHECKLIST.md` — consolidated v1.5 spec-to-runtime shakedown tracker
- `docs/decisions/v1-5-workflow.md` — workflow architecture decision
- `docs/decisions/v1-5-offline-assist.md` — offline assist architecture decision
- `docs/howto/WORKFLOW-SCHEDULER-QUICKSTART.md` — operator workflow quickstart

## Usage Guidance

- Add/maintain stable platform contracts in **Main Specs**.
- Keep round-by-round or migration-specific documents in **Detailed / Historical Execution Specs**.
- Keep release audit state in `docs/specs/V1-5-SHAKEDOWN-CHECKLIST.md` rather than duplicating checklist fragments across public status and local devlog files.
- When in doubt, update this index and `docs/README.md` together.
