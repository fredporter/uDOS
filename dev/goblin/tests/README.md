# Goblin Tests

Updated: 2026-03-04

`dev/goblin/tests/` is the tracked overlay test layer for contributor and experimental flows.

Rules:

- Goblin tests may exercise Wizard services and Dev Mode service contracts.
- Goblin tests must not introduce a second runtime root.
- Keep runtime-owned tests in `wizard/tests/` or `core/tests/` when they validate primary subsystem behavior.
- Use this tree for contributor overlays, framework contract tests, and experimental feature coverage that layers over Wizard.
- Typical candidates include `@dev` workspace selection, tracked payload browser/read contracts, extension hot-reload against the contributor scaffold, certified-profile Dev extension gate policy, and dev scaffold status checks.
- Keep dispatch/router behavior that merely branches on Dev Mode state in `wizard/tests` when the runtime contract itself is what is under test.
