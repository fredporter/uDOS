# Thin GUI Extension Contract v1.5

Status: canonical
Updated: 2026-03-05

## Purpose

Define Thin GUI as an extension-owned GUI lane that core can call/install/build
without making GUI rendering a core ownership concern.

## Ownership Model

- Core runtime:
  - command dispatch and policy (`THINGUI` command family)
  - deterministic terminal operation
- Thin GUI extension:
  - launch intent contract client
  - fullscreen/single-window presentation surface
- Wizard GUI:
  - bundled browser/shelf GUI lane
  - operator dashboard and web publishing pathway

## Core Command Contract

`THINGUI` is the core bridge command for extension lifecycle and launch handoff.

Supported surface:

- `THINGUI STATUS`
- `THINGUI INSTALL`
- `THINGUI BUILD`
- `THINGUI LINT`
- `THINGUI OPEN [target_url]`
- `THINGUI INTENT <target_url> [title] [label]`

Launch intents are stored at:

- `memory/ucode/thin_gui_intent.json`

## Target Deployment Profiles

### Profile A: High-resource fullscreen

Use Thin GUI for focused game/3D presentation surfaces where one full-screen
window owns the runtime session.

### Profile B: Low-resource kiosk

Use Thin GUI for lightweight kiosk installs:

- bare-metal Alpine
- uDOS core runtime
- Thin GUI extension
- single-purpose kiosk mode session

## Wizard GUI Comparison

Wizard GUI is documented as:

- the GUI lane that works when a bundled system OS browser shelf is available
- the control path for web publishing and operator dashboard workflows

Thin GUI is documented as:

- the fast fullscreen/single-window extension lane
- usable for kiosk and game/3D focus scenarios

Both may coexist in one deployment.

## Non-Goals

Thin GUI does not redefine:

- core deterministic command/runtime policy
- Wizard publishing/control-plane ownership
- extension security boundaries

## Related

- `docs/decisions/UDOS-ALPINE-THIN-GUI-RUNTIME-SPEC.md`
- `docs/specs/UHOME-v1.5.md`
- `docs/specs/3DWORLD-EXTENSION-CONTRACT-v1.5.md`
- `extensions/thin-gui/README.md`
