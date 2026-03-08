# Sonic and uHOME External Integration

Sonic and `uHOME` are no longer implemented inside this repository.

Canonical companion repos:

- Sonic: `https://github.com/fredporter/uDOS-sonic`
- `uHOME` server: `https://github.com/fredporter/uHOME-server`

## Local layout

Install the repos beside `uDOS`, not inside it:

- `../uDOS`
- `../uDOS-sonic`
- `../uHOME-server`

Optional overrides:

- `UDOS_SONIC_ROOT`
- `UDOS_UHOME_ROOT`

## Runtime contract

- Wizard remains hosted in `uDOS`
- Wizard GUI still exposes Sonic and `uHOME` surfaces
- Sonic runtime/data/build operations are resolved from the external `uDOS-sonic` repo
- `uHOME` GUI status in Wizard is resolved against the external `uHOME-server` repo and the shared template workspace

## What stays in uDOS

- Wizard integration routes and GUI surfaces
- shared contracts
- extension/profile metadata
- local memory/state used by Wizard

## What no longer belongs in uDOS

- bundled Sonic repo contents
- in-repo Sonic datasets and build scripts
- in-repo `uHOME-server` implementation

## Notes

- If Sonic is missing locally, Wizard and `ucode` should report the external repo path they expect.
- If `uHOME-server` is missing locally, Wizard should still load but report the missing external repo in status surfaces.
