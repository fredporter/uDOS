# uDOS Wiki Home

Updated: 2026-03-04
Status: v1.5 orientation map

This wiki is the short orientation layer for the repo.

Use it to understand the main runtime lanes and find the right canonical doc quickly.
Detailed contracts, runbooks, and release guidance live in `docs/`.
Contributor-only `@dev` workspace policy lives in `dev/docs/`.

## Start Here

- [Installation](Installation.md)
- [Onboarding Flow](Onboarding-Flow.md)
- [Architecture](ARCHITECTURE.md)
- [Core](Core.md)
- [Wizard](Wizard.md)
- [Modes and Policy](Modes-and-Policy.md)

## Canonical Entrypoints

- Docs front door: [../docs/README.md](../docs/README.md)
- Docs index: [../docs/INDEX.md](../docs/INDEX.md)
- Public status: [../docs/STATUS.md](../docs/STATUS.md)
- Specs catalog: [../docs/specs/README.md](../docs/specs/README.md)
- Decisions catalog: [../docs/decisions/README.md](../docs/decisions/README.md)
- Contributor workspace docs: [../dev/docs/README.md](../dev/docs/README.md)

## Quick Paths

- New operator:
  [Installation](Installation.md) -> [Onboarding Flow](Onboarding-Flow.md) -> [Core](Core.md) -> [Wizard](Wizard.md)
- Runtime boundaries:
  [Architecture](ARCHITECTURE.md) -> [Modes and Policy](Modes-and-Policy.md)
- Gameplay and spatial context:
  [TUI Z-Layer and TOYBOX](TUI-Z-Layer-and-TOYBOX.md)
- Contributor tools and `@dev`:
  [Dev Tools](Dev-Tools.md)

## Rules

- Wiki pages stay short.
- Root `docs/` is the source of truth for active runtime/operator documentation.
- `dev/docs/` is the source of truth for contributor-facing `@dev` material.
- Superseded docs belong in `docs/.compost/`, not beside active v1.5 pages.
