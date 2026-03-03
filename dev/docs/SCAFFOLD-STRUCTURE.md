# Dev Scaffold Structure

Updated: 2026-03-04

This document replaces the old submodule-era scaffold notes.

## v1.5 Layout

The tracked contributor payload is:

- `/dev` governance files
- `dev/docs/`
- `dev/goblin/`

The local-only working payload is:

- `dev/files/`
- `dev/relecs/`
- `dev/dev-work/`
- `dev/testing/`

## Intent

- `dev/docs/` is the contributor documentation tree
- `dev/goblin/` is the distributable dev scaffold and testing-server layer
- local working paths are intentionally excluded from public sync

Use `dev/docs/specs/DEV-WORKSPACE-SPEC.md` as the authoritative contract.
