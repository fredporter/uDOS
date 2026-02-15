# Platform Contract v1.3

## Canonical Product Surfaces

- `uCLI` is the only terminal interface.
- `uCODE` is the command surface (used by uCLI and Wizard-backed dispatch).
- `Wizard GUI` is the only GUI host for uDOS features.
- `uDOS` is the underlying TS/Python runtime.

## Dev Submodule Contract (`/dev`)

`/dev` is the private development scaffold. Goblin is not a standalone runtime product.

Required scaffold for Wizard Dev Mode:

- `/dev/goblin/scripts/` for dev scripts
- `/dev/goblin/tests/` for dev tests
- `/dev/goblin/wizard-sandbox/` for GUI-bound development outputs

Wizard Dev Mode APIs execute scripts/tests from this scaffold only.

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
