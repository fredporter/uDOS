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
| `docs/specs/MINIMUM-SPEC-DEV-MODE-UCODE.md` | `implemented` | `core/commands/ucode_handler.py`, `core/tests/ucode_min_spec_command_test.py` | Active minimum runtime pathway is implemented in the `UCODE` help and system/info flow. |
| `docs/specs/UCODE-SELECTOR-INTEGRATION-BRIEF.md` | `partial` | `core/ui/command_selector.py`, `core/ui/selector_framework.py`, `core/ui/workspace_selector.py` | Selector primitives exist; Round 5 TUI hardening still needs end-to-end proof. |

## Workflow and Offline Assist

| Spec | Status | Current anchor | Notes |
|---|---|---|---|
| `docs/specs/WORKFLOW-SCHEDULER-v1.5.md` | `implemented` | `core/workflows/`, `core/commands/workflow_handler.py`, `core/tests/workflow_handler_test.py` | Core workflow runtime is live and tested. |
| `docs/specs/OFFLINE-ASSIST-STANDARD-v1.5.md` | `implemented` | `core/ulogic/`, `docs/examples/udos_ulogic_pack/` | Core now owns the promoted deterministic parser, deliverable validation, research/enrich/generate pipeline, action-graph/runtime/state/artifact primitives, and bounded script sandbox. The example pack remains the supplemental reference surface for optional gameplay/provider scaffolds. |
| `docs/specs/LOGIC-INPUT-HANDLER-v1.5.md` | `implemented` | `core/ulogic/parser.py`, `core/tui/ucode.py`, `core/tui/dispatcher.py` | Standard parser-to-command/workflow/knowledge handoff is active in the canonical `ucode` shell. |
| `docs/specs/WORKFLOW-MANAGER-CONTRACT-v1.5.md` | `implemented` | `core/workflows/`, `core/commands/workflow_handler.py`, `wizard/routes/workflow_routes.py` | Cross-surface workflow orchestration now runs through the shared runtime contract in core and Wizard. |
| `docs/specs/KNOWLEDGE-BANK-RUNBOOK-STANDARD-v1.5.md` | `implemented` | `core/services/seed_template_service.py`, `core/services/knowledge_artifact_service.py`, `core/framework/seed/bank/templates/` | Seed/default/user template layers, local knowledge-tree persistence, Markdown template structure, and duplicate flows are now active and tested. |
| `docs/specs/wiki_spec_obsidian.md` | `partial` | `docs/decisions/OBSIDIAN-INTEGRATION.md`, `wizard/services/markdown_job_service.py` | Markdown-first and import surfaces exist, but Round 1 still needs tighter mapping from Obsidian-facing spec to shipped paths. |
| `docs/specs/FORMATTING-SPEC-v1.4.md` | `implemented` | `docs/specs/FORMATTING-SPEC-v1.4.md`, `.compost` policy docs | Canonical formatting and archival rules are already in place; use as governance during doc cleanup. |

## Platform, Packaging, and Extensions

| Spec | Status | Current anchor | Notes |
|---|---|---|---|
| `docs/specs/PLUGIN-MANIFEST-SPEC.md` | `implemented` | `distribution/plugins/`, `distribution/plugins/plugin.schema.json`, `wizard/services/plugin_manager.py` | Plugin manifests and registry surfaces are present. |
| `docs/specs/PACKAGING-RELEASE-CONTRACT-v1.5.md` | `implemented` | `distribution/`, `distribution/profiles/certified-profiles.json`, `docs/specs/V1-5-STABLE-SIGNOFF.md` | Certified profile install, verify, repair, rollback-or-recovery, and demo evidence are now checked in for the v1.5 release lane. |
| `docs/specs/INTEGRATION-READINESS.md` | `implemented` | `wizard/routes/`, `wizard/tests/`, `docs/examples/ucode_v1_5_release_pack/CERTIFICATION.md` | Managed operations, local assist, self-hosted `@dev`, and demo certification now provide integrated release evidence. |
| `dev/docs/specs/DEV-WORKSPACE-SPEC.md` | `implemented` | `dev/docs/specs/DEV-WORKSPACE-SPEC.md`, `wizard/services/dev_mode_service.py`, `wizard/services/dev_extension_service.py`, `wizard/routes/dev_routes.py` | Dev Mode is now explicitly defined as a Wizard-gated `@dev` workspace rooted at `/dev`, with a tracked sync boundary. |
| `docs/specs/3DWORLD-EXTENSION-CONTRACT-v1.5.md` | `deferred` | `extensions/3dworld/`, `wizard/services/toybox/crawler3d_adapter.py`, `core/lenses/crawler3d_lens.py` | Keep tracked as an extension lane with dedicated runtime/server ownership; do not block v1.5 mainline release. |
| `docs/specs/GAMEPLAY-COMMAND-CONTRACT-v1.5.md` | `implemented` | `core/commands/play_handler.py`, `core/commands/gameplay_handler.py`, `core/commands/skin_handler.py`, `core/services/gameplay_service.py` | Canonical gameplay/lens/skin command contract consolidated and wired into runtime handlers. |

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
  - `MINIMUM-SPEC-DEV-MODE-UCODE`
  - `WORKFLOW-SCHEDULER-v1.5`
  - `OFFLINE-ASSIST-STANDARD-v1.5`
  - `LOGIC-INPUT-HANDLER-v1.5`
  - `WORKFLOW-MANAGER-CONTRACT-v1.5`
  - `KNOWLEDGE-BANK-RUNBOOK-STANDARD-v1.5`
  - `FORMATTING-SPEC-v1.4`
  - `PLUGIN-MANIFEST-SPEC`
  - `PACKAGING-RELEASE-CONTRACT-v1.5`
  - `INTEGRATION-READINESS`
  - `SPATIAL-GRID-CONTRACT`
  - `TYPESCRIPT-MARKDOWN-RUNTIME-CONTRACT`
- `partial`
  - `RUNTIME-INTERFACE-SPEC`
  - `PORT-REGISTRY`
  - `UCODE-SELECTOR-INTEGRATION-BRIEF`
  - `wiki_spec_obsidian`
- `deferred`
  - `3DWORLD-EXTENSION-CONTRACT-v1.5.md`

## Round 1 Follow-up

1. Link each `partial` spec to one concrete acceptance pass or evidence doc.
2. Use this checklist as the source surface for Round 2 through Round 5 progress updates.
3. Add explicit evidence for:
   - global knowledge-bank seed/read-only contract
   - local user knowledge-tree writable contract
   - Sonic global seeded catalog and contributor approval path
   - cross-component Markdown template/runbook standardization
