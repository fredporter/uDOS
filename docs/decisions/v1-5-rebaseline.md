# uDOS v1.5 Rebaseline

Last updated: 2026-03-02
Status: Active

## Decision

uDOS v1.5 is reopened as an active rebaseline release. The earlier repository claim that v1.5 was GA on February 26, 2026 is no longer the active source of truth.

## Product Rule

- `ucode` is the sole primary user entry point
- the v1.5 `ucode` TUI is the standard interactive user experience
- Wizard is the browser/service layer subordinate to `ucode`
- `vibe` is restricted to Dev Mode
- Mistral-backed contributor flows are restricted to Dev Mode operations unless explicitly surfaced through Wizard-managed policy
- Sonic remains independently distributable, but installed-system control is routed through `ucode`

## Release Profiles

Certified profiles are now tracked in `distribution/profiles/certified-profiles.json`:

- `core`
- `home`
- `creator`
- `gaming`
- `dev`

## Initial Implementation Slice

The first implementation slice introduces:

- `UCODE PROFILE <LIST|SHOW|INSTALL|ENABLE|DISABLE|VERIFY>`
- `UCODE OPERATOR <STATUS|PLAN|QUEUE>`
- `UCODE EXTENSION <LIST|VERIFY>`
- `UCODE PACKAGE <LIST|VERIFY>`
- `UCODE REPAIR STATUS`

It also changes standard TUI fallback behavior so non-Dev runtime uses the deterministic local operator planner rather than defaulting to `vibe`/provider routing.
