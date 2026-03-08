# v1.5 Decisions, Specs, and Features Audit

Updated: 2026-03-05
Status: Completed

## Scope

Systematic audit of all docs in: `docs/decisions`, `docs/specs`, and `docs/features`.

Machine-readable inventory: `docs/specs/V1-5-DOC-COVERAGE-AUDIT.json`

## Summary

- Total docs audited: `106`
- Active v1.5 docs: `42`
- Deferred/supporting docs: `14`
- Redirect docs: `8`
- Reference/meta docs: `42`
- Active v1.5 docs with inclusion evidence or meta-governance role: `42/42`

## Release Gate Result

- no blocking inclusion gaps detected for active v1.5 docs

## Inventory (All Audited Docs)

| Doc | Group | Class | Status marker | Included/evidenced |
| --- | --- | --- | --- | --- |
| `docs/decisions/alpine-linux-spec.md` | `decisions` | `reference` | `-` | `yes` |
| `docs/decisions/data-layer-architecture.md` | `decisions` | `active-v1.5` | `active decision` | `yes` |
| `docs/decisions/formatting-spec-v1-4.md` | `decisions` | `reference` | `superseded decision-path stub` | `yes` |
| `docs/decisions/HOME-ASSISTANT-BRIDGE.md` | `decisions` | `active-v1.5` | `-` | `yes` |
| `docs/decisions/LOGGING-API-v1.3.md` | `decisions` | `deferred/supporting` | `draft` | `yes` |
| `docs/decisions/MCP-API.md` | `decisions` | `active-v1.5` | `active implementation reference` | `yes` |
| `docs/decisions/OBSIDIAN-INTEGRATION.md` | `decisions` | `reference` | `-` | `yes` |
| `docs/decisions/OK-GOVERNANCE-POLICY.md` | `decisions` | `active-v1.5` | `active decision` | `yes` |
| `docs/decisions/OK-update-v1-4-6.md` | `decisions` | `redirect` | `redirect stub` | `yes` |
| `docs/decisions/README.md` | `decisions` | `active-v1.5` | `-` | `yes` |
| `docs/decisions/SONIC-DB-SPEC-GPU-PROFILES.md` | `decisions` | `active-v1.5` | `active sonic contract` | `yes` |
| `docs/decisions/u_dos_robust_teletext_tui_brief_bubble_tea_lip_gloss.md` | `decisions` | `reference` | `-` | `yes` |
| `docs/decisions/UDOS-ALPINE-THIN-GUI-RUNTIME-SPEC.md` | `decisions` | `active-v1.5` | `active platform/runtime direction` | `yes` |
| `docs/decisions/udos-protocol-v1.md` | `decisions` | `deferred/supporting` | `active supporting protocol` | `yes` |
| `docs/decisions/UDOS-PYTHON-CORE-STDLIB-PROFILE.md` | `decisions` | `reference` | `-` | `yes` |
| `docs/decisions/UDOS-PYTHON-ENVIRONMENTS-DEV-BRIEF.md` | `decisions` | `redirect` | `-` | `yes` |
| `docs/decisions/udos-reference-implementation.md` | `decisions` | `deferred/supporting` | `active supporting reference` | `yes` |
| `docs/decisions/udos-teletext-theme.md` | `decisions` | `deferred/supporting` | `active supporting theme reference` | `yes` |
| `docs/decisions/uDOS-v1-3.md` | `decisions` | `deferred/supporting` | `historical snapshot` | `yes` |
| `docs/decisions/UDOS-VM-REMOTE-DESKTOP-ARCHITECTURE.md` | `decisions` | `deferred/supporting` | `active but non-blocking platform reference` | `yes` |
| `docs/decisions/v1-5-3-UHOME-KIOSK.md` | `decisions` | `active-v1.5.3` | `active external uHOME lane` | `yes` |
| `docs/decisions/v1-5-creator-blocker-matrix.md` | `decisions` | `redirect` | `-` | `yes` |
| `docs/decisions/v1-5-logic-assist-final-spec.md` | `decisions` | `deferred/supporting` | `active supporting narrative` | `yes` |
| `docs/decisions/v1-5-logic-input-handler.md` | `decisions` | `active-v1.5` | `active` | `yes` |
| `docs/decisions/v1-5-offline-assist.md` | `decisions` | `deferred/supporting` | `active supporting scaffold` | `yes` |
| `docs/decisions/v1-5-python-runtime-contract.md` | `decisions` | `active-v1.5` | `active` | `yes` |
| `docs/decisions/v1-5-rebaseline.md` | `decisions` | `redirect` | `-` | `yes` |
| `docs/decisions/v1-5-research-enrich-generate.md` | `decisions` | `redirect` | `-` | `yes` |
| `docs/decisions/v1-5-ucode-tui-spec.md` | `decisions` | `active-v1.5` | `active source of truth` | `yes` |
| `docs/decisions/v1-5-workflow-manager.md` | `decisions` | `active-v1.5` | `active` | `yes` |
| `docs/decisions/v1-5-workflow.md` | `decisions` | `active-v1.5` | `active` | `yes` |
| `docs/decisions/VAULT-MEMORY-CONTRACT.md` | `decisions` | `reference` | `-` | `yes` |
| `docs/decisions/WIZARD-SERVICE-SPLIT-MAP.md` | `decisions` | `reference` | `-` | `yes` |
| `docs/features/3D-WORLD.md` | `features` | `deferred/supporting` | `planned (pre-v1.5 stable)` | `yes` |
| `docs/features/alpine-core.md` | `features` | `active-v1.5` | `active feature reference` | `yes` |
| `docs/features/beacon-portal.md` | `features` | `reference` | `-` | `yes` |
| `docs/features/beacon-vpn-tunnel.md` | `features` | `reference` | `-` | `yes` |
| `docs/features/DIAGRAM-SPECS.md` | `features` | `reference` | `-` | `yes` |
| `docs/features/Emoji-Support.md` | `features` | `reference` | `-` | `yes` |
| `docs/features/MOOD-FACTORS-SPEC.md` | `features` | `reference` | `-` | `yes` |
| `docs/features/packaging-dependency-map.md` | `features` | `reference` | `-` | `yes` |
| `docs/features/PROMPT-PARSER-REFERENCE.md` | `features` | `reference` | `-` | `yes` |
| `docs/howto/SONIC-UHOME-EXTERNAL-INTEGRATION.md` | `howto` | `active` | `external companion repo integration` | `yes` |
| `docs/features/SQL-RUNNER-GUIDE.md` | `features` | `reference` | `-` | `yes` |
| `docs/features/THEME-LAYER-MAPPING.md` | `features` | `reference` | `-` | `yes` |
| `docs/features/TODO-RENDERER-REFERENCE.md` | `features` | `reference` | `-` | `yes` |
| `docs/features/wizard-networking.md` | `features` | `reference` | `-` | `yes` |
| `docs/specs/00-dev-brief.md` | `specs` | `reference` | `-` | `yes` |
| `docs/specs/01-vault-contract.md` | `specs` | `reference` | `-` | `yes` |
| `docs/specs/02-theme-pack-contract.md` | `specs` | `reference` | `-` | `yes` |
| `docs/specs/03-contributions-contract.md` | `specs` | `deferred/supporting` | `historical-but-active reference` | `yes` |
| `docs/specs/04-missions-jobs-schema.md` | `specs` | `reference` | `-` | `yes` |
| `docs/specs/05-app-references.md` | `specs` | `reference` | `-` | `yes` |
| `docs/specs/07-grid-canvas-rendering.md` | `specs` | `active-v1.5` | `active alignment spec for current ucode/tui behavior.` | `yes` |
| `docs/specs/3DWORLD-EXTENSION-SPEC-v1.5.0.md` | `specs` | `deferred/supporting` | `draft for cycle d` | `yes` |
| `docs/specs/Agnostic-World-Contract.md` | `specs` | `reference` | `-` | `yes` |
| `docs/specs/ALPINE-CORE-PLUGIN-FORMAT-v1.5.md` | `specs` | `active-v1.5` | `active` | `yes` |
| `docs/specs/BLOCK-SYSTEM-V1.3.md` | `specs` | `reference` | `-` | `yes` |
| `docs/specs/COMMAND-DISPATCH-RC-SCOPE.md` | `specs` | `active-v1.5` | `active` | `yes` |
| `docs/specs/DOCUMENTATION-CANONICAL-MAP.md` | `specs` | `active-v1.5` | `active` | `yes` |
| `docs/specs/ENV-STRUCTURE-V1.1.0.md` | `specs` | `reference` | `-` | `yes` |
| `docs/specs/FORMATTING-SPEC-v1.4.md` | `specs` | `active-v1.5` | `active formatting contract` | `yes` |
| `docs/specs/GAMEPLAY-LENS-ARCHITECTURE-v1.4.4.md` | `specs` | `reference` | `hp 50/100 / level 10 / gold: 500` | `yes` |
| `docs/specs/GAMEPLAY-LENS-SKIN-PROGRESSION-v1.4.8.md` | `specs` | `reference` | `-` | `yes` |
| `docs/specs/GHOST-MODE-POLICY.md` | `specs` | `active-v1.5` | `-` | `yes` |
| `docs/specs/INTEGRATION-READINESS.md` | `specs` | `active-v1.5` | `active readiness summary` | `yes` |
| `docs/specs/KNOWLEDGE-BANK-RUNBOOK-STANDARD-v1.5.md` | `specs` | `active-v1.5` | `active` | `yes` |
| `docs/specs/LOGIC-INPUT-HANDLER-v1.5.md` | `specs` | `active-v1.5` | `active` | `yes` |
| `docs/specs/MCP-ACTIVATION-CONTRACT.md` | `specs` | `reference` | `-` | `yes` |
| `docs/specs/MINIMUM-SPEC-DEV-MODE-UCODE.md` | `specs` | `active-v1.5` | `active contract` | `yes` |
| `docs/specs/OBSIDIAN-COMPANION-INTEGRATION-CONTRACT.md` | `specs` | `active-v1.5` | `active` | `yes` |
| `docs/specs/OFFLINE-ASSIST-STANDARD-v1.5.md` | `specs` | `active-v1.5` | `active` | `yes` |
| `docs/specs/OK-MODES-v1.3.md` | `specs` | `reference` | `-` | `yes` |
| `docs/specs/PACKAGING-RELEASE-CONTRACT-v1.5.md` | `specs` | `active-v1.5` | `active packaging contract` | `yes` |
| `docs/specs/PLATFORM-CONTRACT-v1.3.md` | `specs` | `reference` | `-` | `yes` |
| `docs/specs/PLUGIN-MANIFEST-SPEC.md` | `specs` | `reference` | `-` | `yes` |
| `docs/specs/PORT-REGISTRY.md` | `specs` | `reference` | `-` | `yes` |
| `docs/specs/publish_md_to_html_spec.md` | `specs` | `reference` | `-` | `yes` |
| `docs/specs/PYTHON-RUNTIME-OPERATIONS-v1.5.md` | `specs` | `active-v1.5` | `active` | `yes` |
| `docs/specs/README.md` | `specs` | `active-v1.5` | `-` | `yes` |
| `docs/specs/Spatial-Grid-COMPLETE.md` | `specs` | `redirect` | `redirect stub` | `yes` |
| `docs/specs/SPATIAL-GRID-CONTRACT.md` | `specs` | `active-v1.5` | `active spatial contract` | `yes` |
| `docs/specs/Spatial-Workspace-Filesystem.md` | `specs` | `reference` | `-` | `yes` |
| `docs/specs/TASK-JSON-FORMAT-OK-MODEL-INGESTION.md` | `specs` | `reference` | `-` | `yes` |
| `docs/specs/tasks-spec-v1-4.md` | `specs` | `reference` | `-` | `yes` |
| `docs/specs/TESTS-LOGS-LAYOUT.md` | `specs` | `reference` | `-` | `yes` |
| `docs/specs/TOYBOX-CONTAINER-VARIABLE-COMPARISON-v1.3.md` | `specs` | `deferred/supporting` | `drafted on 2026-02-15 against current scaffold code.` | `yes` |
| `docs/specs/TOYBOX-GAMEPLAY-SCAFFOLD-v1.3.md` | `specs` | `reference` | `scaffold implemented on 2026-02-15.` | `yes` |
| `docs/specs/TYPESCRIPT-MARKDOWN-RUNTIME-CONTRACT.md` | `specs` | `active-v1.5` | `active runtime contract` | `yes` |
| `docs/specs/typescript-markdown-runtime.md` | `specs` | `redirect` | `redirect stub` | `yes` |
| `docs/specs/UCODE-COMMAND-CONTRACT-v1.3.md` | `specs` | `reference` | `-` | `yes` |
| `docs/specs/UCODE-DISPATCH-CONTRACT.md` | `specs` | `active-v1.5` | `active command-dispatch contract` | `yes` |
| `docs/specs/UCODE-PROMPT-SPEC.md` | `specs` | `active-v1.5` | `-` | `yes` |
| `docs/specs/UCODE-SELECTOR-INTEGRATION-BRIEF.md` | `specs` | `deferred/supporting` | `active supporting brief` | `yes` |
| `docs/specs/V1-5-DECISION-IMPLEMENTATION-AUDIT.md` | `specs` | `deferred/supporting` | `release-ready with documented deferred lanes` | `yes` |
| `docs/specs/V1-5-DOCS-IMPLEMENTATION-AUDIT.md` | `specs` | `redirect` | `completed` | `yes` |
| `docs/specs/V1-5-FREEZE-SUMMARY.md` | `specs` | `active-v1.5` | `stable` | `yes` |
| `docs/specs/V1-5-SHAKEDOWN-CHECKLIST.md` | `specs` | `active-v1.5` | `active` | `yes` |
| `docs/specs/V1-5-STABLE-SIGNOFF.md` | `specs` | `active-v1.5` | `completed` | `yes` |
| `docs/specs/wiki_spec_obsidian.md` | `specs` | `active-v1.5` | `stable` | `yes` |
| `docs/specs/WIZARD-GITHUB-PAGES-PUBLISH-ARCHITECTURE-v1.4.5.md` | `specs` | `active-v1.5` | `-` | `yes` |
| `docs/specs/WIZARD-WEB-PUBLISH-SPEC-v1.3.15.md` | `specs` | `reference` | `implemented in wizard publish routes/services` | `yes` |
| `docs/specs/workflow-management.md` | `specs` | `active-v1.5` | `superseded` | `yes` |
| `docs/specs/WORKFLOW-MANAGER-CONTRACT-v1.5.md` | `specs` | `active-v1.5` | `active` | `yes` |
| `docs/specs/WORKFLOW-SCHEDULER-v1.5.md` | `specs` | `active-v1.5` | `active` | `yes` |
