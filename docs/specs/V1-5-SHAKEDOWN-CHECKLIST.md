# v1.5 Shakedown Checklist

Updated: 2026-03-03
Status: Active
Owner: Round 1

This checklist is the canonical Round 1 audit surface for the v1.5 rebaseline.

Status values:

- `implemented`
- `partial`
- `deferred`
- `monitor-only`
- `doc-gap`

## Command and Runtime Contracts

| Spec | Status | Current anchor | Notes |
|---|---|---|---|
| `docs/specs/UCODE-COMMAND-CONTRACT-v1.3.md` | `implemented` | `core/commands/ucode_handler.py`, `core/tests/ucode_min_spec_command_test.py` | Core `UCODE` command family is live; release work is alignment and evidence, not first implementation. |
| `docs/specs/RUNTIME-INTERFACE-SPEC.md` | `partial` | `core/src/runtime/`, `core/commands/`, `wizard/routes/ucode_routes.py` | Runtime surfaces exist across core and Wizard, but Round 1 still needs explicit spec-to-surface accounting. |
| `docs/specs/PORT-REGISTRY.md` | `partial` | `wizard/routes/`, `wizard/mcp/`, `distribution/plugins/api/` | Active networked surfaces exist; Round 1 should verify port ownership and runtime docs stay aligned. |
| `docs/specs/GHOST-MODE-POLICY.md` | `implemented` | `core/commands/ghost_handler.py`, `core/commands/ghost_mode_guard.py` | Real command and guard surfaces exist. |
| `docs/specs/UCODE-DISPATCH-CONTRACT.md` | `implemented` | `core/tui/dispatcher.py`, `core/commands/ucode_handler.py`, `wizard/routes/ucode_dispatch_routes.py` | Dispatch contract is backed by both core and Wizard tests. |
| `docs/specs/MINIMUM-SPEC-VIBE-CLI-UCODE.md` | `implemented` | `core/commands/ucode_handler.py`, `core/tests/ucode_min_spec_command_test.py` | Active minimum runtime pathway is implemented in the `UCODE` help and system/info flow. |
| `docs/specs/UCODE-SELECTOR-INTEGRATION-BRIEF.md` | `partial` | `core/ui/command_selector.py`, `core/ui/selector_framework.py`, `core/ui/workspace_selector.py` | Selector primitives exist; Round 5 TUI hardening still needs end-to-end proof. |

## Workflow and Offline Assist

| Spec | Status | Current anchor | Notes |
|---|---|---|---|
| `docs/specs/WORKFLOW-SCHEDULER-v1.5.md` | `implemented` | `core/workflows/`, `core/commands/workflow_handler.py`, `core/tests/workflow_handler_test.py` | Core workflow runtime is live and tested. |
| `docs/specs/OFFLINE-ASSIST-STANDARD-v1.5.md` | `partial` | `docs/examples/udos_ulogic_pack/` | Canonical contract exists, but implementation is still mostly reference scaffold rather than promoted core runtime. |
| `docs/specs/wiki_spec_obsidian.md` | `partial` | `docs/decisions/OBSIDIAN-INTEGRATION.md`, `wizard/services/markdown_job_service.py` | Markdown-first and import surfaces exist, but Round 1 still needs tighter mapping from Obsidian-facing spec to shipped paths. |
| `docs/specs/FORMATTING-SPEC-v1.4.md` | `implemented` | `docs/specs/FORMATTING-SPEC-v1.4.md`, `.compost` policy docs | Canonical formatting and archival rules are already in place; use as governance during doc cleanup. |

## Platform, Packaging, and Extensions

| Spec | Status | Current anchor | Notes |
|---|---|---|---|
| `docs/specs/PLUGIN-MANIFEST-SPEC.md` | `implemented` | `distribution/plugins/`, `distribution/plugins/plugin.schema.json`, `wizard/services/plugin_manager.py` | Plugin manifests and registry surfaces are present. |
| `docs/specs/PACKAGING-RELEASE-CONTRACT-v1.5.md` | `partial` | `core/services/packaging_manifest_service.py`, `core/services/packaging_dependency_service.py`, `distribution/` | Packaging services and manifests exist; Round 4 still needs install, verify, repair, and rollback evidence. |
| `docs/specs/INTEGRATION-READINESS.md` | `partial` | `wizard/routes/`, `wizard/tests/`, `docs/howto/MANAGED-WIZARD-OPERATIONS.md` | Good implementation coverage exists, but release evidence is still incomplete. |
| `docs/specs/DEV-Mode-Spec.md` | `implemented` | `docs/specs/DEV-Mode-Spec.md`, `wizard/services/dev_mode_service.py`, `wizard/services/dev_extension_service.py`, `wizard/routes/dev_routes.py` | Dev Mode is now explicitly defined as a Wizard-gated `/dev/` extension lane, TUI-only, implicit, and contributor-specific. |
| `docs/specs/3DWORLD-EXTENSION-SPEC-v1.5.0.md` | `deferred` | `wizard/services/toybox/crawler3d_adapter.py`, `core/lenses/crawler3d_lens.py` | Keep tracked as an extension lane, but do not block v1.5 mainline release. |
| `docs/specs/GAMEPLAY-LENS-SKIN-PROGRESSION-v1.4.8.md` | `partial` | `core/commands/gameplay_handler.py`, `core/services/gameplay_service.py`, `core/services/gameplay_replay_service.py` | Gameplay surfaces exist; Round 4 still needs certified gaming profile acceptance proof. |

## Spatial and TypeScript Runtime

| Spec | Status | Current anchor | Notes |
|---|---|---|---|
| `docs/specs/SPATIAL-GRID-CONTRACT.md` | `implemented` | `core/src/spatial/`, `core/src/grid/`, `core/commands/grid_handler.py`, `core/commands/spatial_filesystem_handler.py` | Spatial/grid runtime and examples are present. |
| `docs/specs/TYPESCRIPT-MARKDOWN-RUNTIME-CONTRACT.md` | `implemented` | `core/src/runtime/`, `core/src/parser/markdown.ts`, `core/src/executors/`, `core/grid-runtime/` | Active TS runtime and grid-runtime support are present in-tree. |

## Release Outcome Summary

- `implemented`
  - `UCODE-COMMAND-CONTRACT-v1.3`
  - `GHOST-MODE-POLICY`
  - `UCODE-DISPATCH-CONTRACT`
  - `MINIMUM-SPEC-VIBE-CLI-UCODE`
  - `WORKFLOW-SCHEDULER-v1.5`
  - `FORMATTING-SPEC-v1.4`
  - `PLUGIN-MANIFEST-SPEC`
  - `SPATIAL-GRID-CONTRACT`
  - `TYPESCRIPT-MARKDOWN-RUNTIME-CONTRACT`
- `partial`
  - `RUNTIME-INTERFACE-SPEC`
  - `PORT-REGISTRY`
  - `UCODE-SELECTOR-INTEGRATION-BRIEF`
  - `OFFLINE-ASSIST-STANDARD-v1.5`
  - `wiki_spec_obsidian`
  - `PACKAGING-RELEASE-CONTRACT-v1.5`
  - `INTEGRATION-READINESS`
  - `GAMEPLAY-LENS-SKIN-PROGRESSION-v1.4.8`
- `deferred`
  - `3DWORLD-EXTENSION-SPEC-v1.5.0`

## Round 1 Follow-up

1. Resolve the missing `DEV-Mode-Spec` catalog entry.
2. Link each `partial` spec to one concrete acceptance pass or evidence doc.
3. Use this checklist as the source surface for Round 2 through Round 5 progress updates.
