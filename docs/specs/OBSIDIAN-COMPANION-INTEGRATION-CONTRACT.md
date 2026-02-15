# Obsidian Companion Integration Contract (Draft)

Status: under development
Updated: 2026-02-15

## Scope

This contract defines how uDOS Wizard will integrate with the external Obsidian Companion app hosted in the private pre-release repository `fredporter/oc-app`.

The uDOS monorepo does not host or build the app directly.

## Boundaries

- `oc-app` owns app UX, release cadence, and app-specific TODOs.
- uDOS owns Wizard-side web view/rendering interfaces.
- Integration is API and artifact based, not source-tree based.

## Planned Interfaces

1. Wizard Web View Host
- Wizard provides a stable host surface for external app-rendered views.
- Host feature flags and compatibility version are exposed by Wizard.

2. Rendering API
- Input: markdown/content payload + render options.
- Output: deterministic HTML + referenced assets manifest.
- Contract versioning is explicit (`render_contract_version`).

3. Asset Handoff
- Wizard accepts or pulls generated assets using a declared manifest.
- Asset IDs are content-hash based for cache safety.

4. Auth and Session Boundary
- Wizard validates caller/session before render or publish actions.
- Tokens/secrets remain outside the app payload contract.

## Compatibility Rules

- Backward compatibility is guaranteed for one minor contract version.
- Breaking changes require:
  - new contract version
  - migration notes
  - compatibility test updates in uDOS

## uDOS TODOs

- Add Wizard contract validators for request/response schema.
- Add integration tests covering render, asset handoff, and auth boundaries.
- Add compatibility matrix tracking `wizard_version` <-> `contract_version`.
