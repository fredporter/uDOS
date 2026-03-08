# Alpine Core Plugin Format v1.5

Updated: 2026-03-04
Status: Active

## Purpose

This document defines the active Alpine packaging direction for uDOS v1.5.

It is the canonical public contract for:
- Alpine core runtime packaging
- plugin/package format expectations
- single-source packaging rules for stable release surfaces

## Core Rules

- Alpine is the active Linux packaging target for v1.5.
- `apk` is the canonical package format for Alpine plugin delivery.
- `tar.gz` and `zip` may exist as support artifacts for non-Alpine distribution flows.
- Retired legacy package formats are not part of the active release contract.
- Operator install entrypoint remains `bin/install-udos.sh`.
- Sonic and Alpine image builds remain anchored to `distribution/alpine-core/build-sonic-stick.sh`.

## Plugin Format Rules

- Plugin manifests must describe active package artifacts only.
- Alpine-targeted plugin artifacts should prefer `.apk`.
- Plugin repositories, registry scans, and download surfaces must not require retired package formats.
- Package metadata, release metadata, and public docs must point to the same active package story.

## Runtime Boundaries

- Core remains deterministic and package-format agnostic.
- Wizard owns plugin distribution, registry, build orchestration, and network-facing packaging services.
- Public docs must describe one stable Linux packaging story: Alpine core plus plugin artifacts.

## Related Docs

- `docs/INSTALLATION.md`
- `docs/howto/BARE-METAL-Alpine-Install.md`
- `docs/howto/SONIC-UHOME-EXTERNAL-INTEGRATION.md`
- `docs/specs/PACKAGING-RELEASE-CONTRACT-v1.5.md`
- `docs/features/alpine-core.md`
