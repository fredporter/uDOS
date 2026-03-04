# v1.5 ucode TUI Decision

Status: active source of truth  
Updated: 2026-03-03

## Purpose

This document defines the v1.5 `ucode` TUI direction for the standard interactive runtime.

It consolidates the current TUI goals for:
- predictable fixed-width rendering
- reusable selectors and input controls
- backend-driven output contracts
- safe terminal behavior under resize, paste, and slow output

## Decision

The v1.5 `ucode` TUI is a teletext-style terminal surface with:
- fixed-width, ASCII-safe rendering by default
- a reusable library of TUI primitives
- a single output-contract layer for backend events
- a backend protocol that keeps UI rendering separate from runtime execution

This TUI is the standard interactive runtime surface for normal users.
`vibe` remains a Dev Mode contributor surface and is not the default user-facing terminal path.
Mistral-backed contributor flows are treated as Dev Mode operations rather than the baseline user runtime.
Dev Mode entry is implicit through the active `dev` extension lane and must not behave like a second default runtime.

## Architecture

### Frontend shell

The TUI frontend is a dedicated terminal UI binary that:
- owns layout
- owns input handling
- owns rendering
- does not print ad hoc backend text directly

### Backend execution

Backend tasks remain owned by the existing runtime layers:
- `core` for deterministic local execution
- `wizard` for managed and network-aware behavior where applicable

The TUI consumes structured events instead of inheriting backend formatting drift.

## Rendering Rules

### Character model

- ASCII-safe rendering is the default
- optional richer block rendering may exist, but must never be required for baseline operation
- layout must remain stable under fixed character-cell assumptions

### Layout model

- render inside a fixed canvas width by default
- use crop-then-pad behavior instead of uncontrolled wrapping
- fall back to stacked/minimal layouts on narrow terminals

### Theme direction

The standard visual language is teletext-style:
- high contrast
- minimal styling
- ASCII borders
- predictable block and column layouts

## Interaction Rules

The TUI must standardize:
- selectors
- single-line input
- multiline input
- confirmation dialogs
- picker-style flows
- consistent help/footer hints

Global behavior should remain stable across all primitives:
- accept/confirm
- cancel/back
- navigation
- search/filter
- redraw/refresh
- quit

## Terminal Safety Rules

The v1.5 TUI must be safe under:
- bracketed paste
- resize events
- partial or slow backend output
- non-ideal terminal widths

Pasted text must be handled as literal user input rather than accidental control sequences.

## Output Contract

The backend must emit structured render events rather than preformatted UI text.

The TUI renderer should own presentation of:
- blocks
- logs
- progress
- dividers
- multi-column layouts
- teletext-style graphics where supported

## Supporting Documents

- `docs/decisions/udos-protocol-v1.md`
- `docs/decisions/udos-reference-implementation.md`
- `docs/decisions/udos-teletext-theme.md`

## v1.5 Refactor Scope

The pre-release TUI refactor should cover:
- standard `ucode`-first entry behavior
- teletext-safe layout consistency
- reusable selector/input primitives
- protocol and event-contract alignment
- shakedown coverage for paste, resize, fallback, and workflow/task flows

## Related Documents

- `docs/STATUS.md`
- `dev/docs/decisions/v1-5-rebaseline.md`
- `docs/specs/RUNTIME-INTERFACE-SPEC.md`
- `docs/specs/UCODE-DISPATCH-CONTRACT.md`
