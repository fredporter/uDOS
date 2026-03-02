# uDOS Alpine Thin GUI Runtime Decision

Status: active platform/runtime direction  
Updated: 2026-03-03

## Purpose

This decision defines the standard thin-GUI runtime for Alpine-based uDOS deployments.

## Decision

The Alpine thin-GUI runtime uses:
- Alpine Linux
- Wayland
- Cage as the single-app compositor
- Chromium as the kiosk browser/runtime shell
- a static or locally served uDOS UI bundle

This remains the standard kiosk-style GUI direction for Alpine runtime lanes.

## Working Rules

### Thinness

Thinness is achieved by minimizing the OS and session layer, not by replacing the browser engine with experimental alternatives.

### Runtime shell

The GUI stack should remain:
- reproducible
- offline-capable
- packageable for local installation
- limited to a single visible application path

### UI bundle

The UI bundle must be deployable as:
- a local static bundle, or
- a local Wizard-connected client path

Switching supported runtime modes should not require a full redesign of the thin-GUI stack.

### GPU handling

GPU and launch decisions must be driven by Sonic DB records rather than hard-coded launcher drift.

## v1.5 Relevance

For v1.5, this decision governs:
- Alpine kiosk/runtime expectations
- thin-GUI compatibility direction
- Sonic-driven launch-profile alignment

## Related Documents

- `docs/roadmap.md`
- `docs/decisions/SONIC-DB-SPEC-GPU-PROFILES.md`
- `docs/decisions/alpine-linux-spec.md`
