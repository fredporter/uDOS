# Public Status

Updated: 2026-03-04

uDOS v1.5.0 is stable.

## Public Reading Order

- [README.md](../README.md)
- [INSTALLATION.md](INSTALLATION.md)
- [ALPINE-CORE-PLUGIN-FORMAT-v1.5.md](specs/ALPINE-CORE-PLUGIN-FORMAT-v1.5.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [README.md](specs/README.md)

## Current Public Contract

- `ucode` is the standard operator entry point.
- `./bin/install-udos.sh` is the stable installer entrypoint.
- `bin/ucode-tui-v1.5.command` is the stable macOS launcher.
- Wizard is the networked service layer.
- Alpine core plus plugin artifacts is the active Linux packaging story.
- `@dev` is the contributor workspace and is documented under `dev/docs/`.
- Private planning, devlogs, and milestone sequencing are kept in local `@dev` workspace paths and are not part of the public docs set.

## Current Release State

- the canonical v1.5 demo pack is certified under `docs/examples/ucode_v1_5_release_pack/`
- runtime metadata now reflects the active `v1.5.0` stable release
- all certified profiles are now installed and enabled in `memory/ucode/release-profiles.json`
- final signoff evidence now lives in `docs/specs/V1-5-STABLE-SIGNOFF.md`
- the freeze summary now lives in `docs/specs/V1-5-FREEZE-SUMMARY.md`
- the tracked v1.5 repo backlog is closed
