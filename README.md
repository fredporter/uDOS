# uDOS v1.5

uDOS is a Python-first runtime built around `ucode`, with Wizard as the networked service layer and `@dev` as the contributor workspace.

## Runtime Contract

- `ucode` is the primary operator entry point.
- Core stays deterministic and stdlib-first.
- Wizard owns web, provider, and networked responsibilities.
- `vibe` is a contributor surface gated behind `@dev`.

## Start Here

- Install and bootstrap: [docs/INSTALLATION.md](docs/INSTALLATION.md)
- Quick operator path: [QUICK-START.md](QUICK-START.md)
- Governance and contributor docs: [dev/docs/root-governance](dev/docs/root-governance)
- Public docs front door: [docs/README.md](docs/README.md)
- Public status: [docs/STATUS.md](docs/STATUS.md)
- Contributor workspace docs: [dev/docs/README.md](dev/docs/README.md)
- Contributor operations state: [dev/ops/README.md](dev/ops/README.md)
- Short wiki map: [wiki/Home.md](wiki/Home.md)

## Stable Release Front Door

- Install with `./bin/install-udos.sh`
- Launch the macOS stable TUI with `bin/ucode-tui-v1.5.command`
- Use the active Alpine packaging path for Linux and Sonic release work
- Treat [ALPINE-CORE-PLUGIN-FORMAT-v1.5.md](docs/specs/ALPINE-CORE-PLUGIN-FORMAT-v1.5.md) as the public Linux packaging contract

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
