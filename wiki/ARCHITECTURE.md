# uDOS Architecture

Updated: 2026-03-04
Status: v1.5 short overview

uDOS is organized around explicit runtime ownership.

## Main Layers

- `core/`
  deterministic local command/runtime layer
- `wizard/`
  networked and web-facing service layer
- `tui/`
  Bubble Tea and Lip Gloss frontend over the v1.5 JSONL TUI bridge
- `dev/`
  contributor-only `@dev` workspace, Goblin scaffold, and local-only sprawl

## Runtime Boundary

- Core stays offline-capable and deterministic.
- Wizard owns provider access, API routes, dashboards, GitHub integration, and managed orchestration.
- `@dev` is not a second user runtime. It is a permissioned contributor workspace mounted at `/dev`.
- Root `docs/` stays operator/runtime-facing. Contributor governance belongs in `dev/docs/`.

## Current v1.5 Shape

- Standard command path:
  user -> `ucode` -> core subsystems -> Wizard only when networked behavior is required
- Wizard Dev Mode path:
  Wizard GUI/API -> `@dev` workspace gates -> Goblin/docs tracked payload
- TUI path:
  Bubble Tea frontend -> JSONL protocol bridge -> core command routing

## Canonical References

- Active architecture overview:
  [../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)
- Integration reference:
  [../docs/ARCHITECTURE-INTEGRATION-REFERENCE.md](../docs/ARCHITECTURE-INTEGRATION-REFERENCE.md)
- Wizard service map:
  [../wizard/ARCHITECTURE.md](../wizard/ARCHITECTURE.md)
- Platform contract:
  [../docs/specs/PLATFORM-CONTRACT-v1.3.md](../docs/specs/PLATFORM-CONTRACT-v1.3.md)
