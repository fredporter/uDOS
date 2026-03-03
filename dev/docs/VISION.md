# Dev Workspace Vision

Updated: 2026-03-04

The v1.5 contributor lane is built around one idea: keep the public repository clean while preserving a versioned contributor framework inside the main repo.

## Vision

`@dev` should give contributors a stable place for:

- governance
- onboarding
- Dev Mode policy
- Goblin fixtures
- contributor GitHub integration guidance

without mixing that material into root `docs/` or the shipping runtime tree.

## Outcome

- root `docs/` stays product and operator focused
- `dev/docs/` becomes the contributor documentation home
- `dev/goblin/` becomes the distributable dev scaffold and testing-server layer
- sprawling personal work stays ignored until promoted deliberately

## Runtime Relationship

- `ucode` is still the standard runtime
- Wizard still owns Dev Mode controls, gates, and permissions
- `vibe` remains contributor tooling inside the active Dev extension lane

The contributor lane exists to support the runtime, not compete with it.
