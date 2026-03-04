# uDOS v1.5

uDOS is a Python-first runtime built around `ucode`, with Wizard as the networked service layer and `@dev` as the contributor workspace.

## Runtime Contract

- `ucode` is the primary operator entry point.
- Core stays deterministic and stdlib-first.
- Wizard owns web, provider, and networked responsibilities.
- `vibe` is a contributor surface gated behind `@dev`.

## Start Here

- Install and bootstrap: [docs/INSTALLATION.md](/Users/fredbook/Code/uDOS/docs/INSTALLATION.md)
- Quick operator path: [QUICK-START.md](/Users/fredbook/Code/uDOS/QUICK-START.md)
- Public docs front door: [docs/README.md](/Users/fredbook/Code/uDOS/docs/README.md)
- Public status: [docs/STATUS.md](/Users/fredbook/Code/uDOS/docs/STATUS.md)
- Contributor workspace docs: [dev/docs/README.md](/Users/fredbook/Code/uDOS/dev/docs/README.md)
- Contributor operations state: [dev/ops/README.md](/Users/fredbook/Code/uDOS/dev/ops/README.md)
- Short wiki map: [wiki/Home.md](/Users/fredbook/Code/uDOS/wiki/Home.md)

## First Commands

```bash
ucode HELP
ucode SETUP
ucode STATUS
ucode UCODE PROFILE LIST
ucode UCODE OPERATOR STATUS
```

## Repository Layout

```text
uDOS/
├── core/         # Deterministic runtime and command surfaces
├── wizard/       # Networked service layer and dashboard
├── docs/         # Public operator/runtime docs
├── dev/          # `@dev` contributor workspace
├── tui/          # Go TUI client
├── vibe/         # Contributor integration layer
├── distribution/ # Packaging and release profiles
└── uDOS.py       # Root command entry point
```

## Root Policy

The repository root keeps only active entry files, governance files, packaging manifests, and runtime launch surfaces. Historical plans, devlogs, and contributor planning belong in `@dev`, not at the top level and not in public docs.
