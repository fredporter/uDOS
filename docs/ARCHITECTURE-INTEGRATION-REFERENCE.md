# Architecture Integration Reference

Updated: 2026-03-05
Status: active reference

## Scope

This page defines the high-level integration boundary for uDOS v1.5:

- core runtime and command surfaces
- Wizard-managed network and control-plane surfaces
- extension/plugin boundaries
- file ownership and compatibility rules

## Integration Rules

- Keep deterministic command execution in shared runtime surfaces.
- Keep network/provider orchestration in Wizard-managed services.
- Keep extension behavior behind explicit contracts and manifests.
- Avoid duplicate control paths that fork operator behavior.

## Validation

Validate integration changes with:

- command-surface tests
- runtime boot checks
- extension contract checks
- release audit gates (`./bin/udos release-check`)

## Canonical Links

- [Architecture](ARCHITECTURE.md)
- [Wizard Service Split Map](decisions/WIZARD-SERVICE-SPLIT-MAP.md)
- [Specs Catalog](specs/README.md)
