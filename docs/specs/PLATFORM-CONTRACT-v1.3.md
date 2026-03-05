# Platform Contract v1.3

## Canonical Product Surfaces

- `uCODE` is the only terminal interface.
- `uCODE` is the command surface (used by uCODE and Wizard-backed dispatch).
- `Wizard GUI` is the canonical bundled web GUI host for v1.3-era features.
- `Thin GUI` is a dedicated extension lane in v1.5+ for fullscreen/single-window output (`docs/specs/THIN-GUI-EXTENSION-CONTRACT-v1.5.md`).
- `uDOS` is the underlying TS/Python runtime.

## `@dev` Workspace Contract

The `@dev` workspace lives at `/dev`. Goblin is not a standalone runtime product.

Required scaffold for Wizard Dev Mode:

- `dev/goblin/` for distributable contributor fixtures
- `dev/dev-work/` for local-only dev scripts
- `dev/testing/` for local-only dev tests
- `dev/files/` for local-only GUI-bound development outputs

Wizard Dev Mode APIs execute contributor scripts/tests from the `@dev` workspace only.

## Groovebox Contract

Groovebox outputs are hosted through Wizard:

- API surface: `/api/groovebox/*`
- GUI surface: Wizard Dashboard route `#groovebox`

No separate Groovebox GUI runtime is required.

## Sonic Contract

Sonic is independently runnable and install-first for physical provisioning.

Wizard integrates Sonic as a bridge layer:

- Sonic status/metadata exposed via `/api/platform/sonic/status`
- Sonic artifacts exposed via `/api/platform/sonic/artifacts`

This allows Sonic datasets/config/artifacts to be visible from Wizard GUI after uDOS installation.

## GUI Theme/CSS Extension Contract

Wizard GUI is the canonical home for GUI theme/CSS extension management.

- Theme/CSS inventory endpoint: `/api/platform/themes/css-extensions`
- Theme packs remain under `/themes/*` with `theme.css` + `shell.html`
- Wizard dashboard CSS extensions are tracked from `/wizard/dashboard/src/styles`
