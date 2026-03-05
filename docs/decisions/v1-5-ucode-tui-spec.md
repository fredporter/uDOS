# v1.5 ucode TUI Decision

Status: active source of truth  
Updated: 2026-03-05

## Purpose

This document defines the final pre-release v1.5 standard for the `ucode` TUI runtime.

It confirms the required feature set across rendering, onboarding, views, layer mapping, seed content, and Dev Mode repair/extension behavior.

## Final v1.5 Standard

The v1.5 `ucode` TUI is the canonical operator surface and must provide:

- fixed-width text rendering with deterministic layout
- block-graphic grid rendering with teletext-compatible fallback
- first-class support for text, columns, ASCII, teletext, calendar, task, block/grid, and container views
- gameplay-style onboarding that performs real setup work during progression
- explicit layer mapping with z-index/elevation semantics
- seed library generation/indexing for rendering and mission templates
- Dev Mode self-repair and self-extension through runtime tools and cloud-code-agent lane when enabled by policy

Mistral Vive remains an `@dev` contributor surface and not the default operator runtime.

## Architecture

### Frontend shell

The TUI frontend:

- owns layout/input/rendering
- consumes structured events
- never prints raw backend formatting as the render source of truth

### Backend ownership

- `core` owns deterministic execution and local-first behavior
- `wizard` owns managed/networked behavior and policy-gated escalation

Cross-boundary duplication is prohibited.

## Rendering and View Matrix

v1.5 standard renderer capability includes:

- plain text panels
- aligned column panels
- ASCII diagrams and box layouts
- teletext block graphics
- calendar views
- task list/kanban-style views
- block/grid/canvas views
- container/panel composition views

Rules:

- ASCII-safe baseline must remain functional on every supported terminal
- block graphics are additive, not mandatory for baseline operation
- crop-then-pad is preferred over uncontrolled soft-wrap
- narrow-width fallback must preserve command usability and critical status visibility

## Onboarding Standard

The required onboarding model is progression gameplay:

- flow: Ghost -> Apprentice -> Operator -> Alchemist -> Wizard
- every onboarding action both teaches and performs real setup/configuration
- progress is resumable and persisted
- event stream uses structured blocks (`narration`, `objective`, `challenge`, `reward`, `unlock`, `progress`)

Canonical script path:

- `docs/examples/ghost-to-wizard-script.md`

## Layer Mapping and Z-Index

TUI layer mapping is a required runtime contract:

- explicit z/elevation handling for map/render semantics
- consistent bucket mapping for dungeon/foundation/galaxy message lenses
- separate concern between spatial rendering state and message-theme vocabulary

Canonical mapping references:

- `docs/features/THEME-LAYER-MAPPING.md`
- `docs/examples/FRACTAL-GRID-IMPLEMENTATION.md`

## Seed Library Generation

v1.5 includes seed library generation/indexing for:

- teletext/ascii/block diagram seeds
- prompt/parser template seeds
- workflow/mission/story starter templates

Seed generation must emit inspectable artifacts and deterministic indexes.

## Dev Mode Repair and Self-Extension

The runtime must support repair and extension from Dev Mode through official command/tool paths:

- repair diagnostics and remediation (`ucode_repair` lanes)
- extension scaffolding/activation through runtime-owned workflows
- policy-gated cloud-code-agent escalation through Wizard-managed controls

## Output Contract

The backend emits structured render events; the TUI owns visual presentation.

Required event classes include:

- block
- progress
- result
- done

Extended classes for onboarding and grid rendering are allowed as long as the protocol envelope remains compatible.

## Demo Certification Requirement

v1.5 release proof requires the extended demo pack (`00` through `09`) under:

- `docs/examples/ucode_v1_5_release_pack/`

This pack is the canonical evidence set for the final pre-release round.

## Supporting Documents

- `docs/decisions/udos-protocol-v1.md`
- `docs/decisions/udos-reference-implementation.md`
- `docs/decisions/udos-teletext-theme.md`
- `docs/features/DIAGRAM-SPECS.md`
- `docs/features/PROMPT-PARSER-REFERENCE.md`
- `docs/features/TODO-RENDERER-REFERENCE.md`
- `docs/features/SQL-RUNNER-GUIDE.md`

## Related Documents

- `docs/specs/RUNTIME-INTERFACE-SPEC.md`
- `docs/specs/UCODE-DISPATCH-CONTRACT.md`
- `dev/docs/decisions/v1-5-rebaseline.md`
