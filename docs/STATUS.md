# Public Status

Updated: 2026-03-07

uDOS v1.5.0 is stable.

## Public Reading Order

- [README.md](../README.md)
- [INSTALLATION.md](INSTALLATION.md)
- [ALPINE-CORE-PLUGIN-FORMAT-v1.5.md](specs/ALPINE-CORE-PLUGIN-FORMAT-v1.5.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [README.md](specs/README.md)

## Current Public Contract

- `ucode` is the standard operator entry point.
- `./bin/udos install` is the stable installer entrypoint.
- `bin/ucode-tui-v1.5.command` is the stable macOS launcher.
- Wizard is the networked service layer.
- Empire is a private internal extension activated through Wizard Extensions when enabled.
- Sonic and `uHOME` are external companion repos integrated through Wizard and shared contracts.
- Alpine core plus plugin artifacts is the active Linux packaging story.
- `@dev` is the contributor workspace and is documented under `dev/docs/`.
- Private planning, devlogs, and milestone sequencing are kept in local `@dev` workspace paths and are not part of the public docs set.

## Current Release State

- the canonical v1.5 demo pack is certified under `docs/examples/ucode_v1_5_release_pack/`
- runtime metadata now reflects the active `v1.5.0` stable release
- all certified profiles are now installed and enabled in `memory/ucode/release-profiles.json`
- final signoff evidence now lives in `docs/specs/V1-5-STABLE-SIGNOFF.md`
- the freeze summary now lives in `docs/specs/V1-5-FREEZE-SUMMARY.md`
- a v1.5.1 patch stream is active for Bubble Tea TUI operational closeout before
  v1.5.2 Empire/Wizard thin-client work and v1.5.3 uHOME kiosk/controller work
- the active closeout decision is `docs/decisions/v1-5-1-TUI-OPERATIONAL-CLOSEOUT.md`
- the active patch checklist is `docs/specs/V1-5-1-TUI-CLOSEOUT-CHECKLIST.md`
- repo boundaries for Empire, Sonic, uHOME server, and private client apps are now tracked in `docs/decisions/v1-5-4-REPO-BOUNDARIES.md`
- Empire internal-extension migration closeout is recorded in `extensions/empire/docs/EMPIRE-MIGRATION-CLOSEOUT-NOTE-v1.5.2.md`
- local Empire v1.5.2 dev verification now includes strict connector preflight with repo-supported mock secrets
- Sonic and `uHOME` external-repo integration guidance now lives in `docs/howto/SONIC-UHOME-EXTERNAL-INTEGRATION.md`
