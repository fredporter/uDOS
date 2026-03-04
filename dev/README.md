# Dev Mode Extension Framework

`/dev` is the v1.5 `@dev` workspace.

It is the tracked contributor framework payload for:

- Dev Mode governance
- contributor operations state and mission tracking
- contributor documentation
- extension metadata
- Goblin dev scaffold and testing-server fixtures

Rules:

- standard runtime remains `ucode`
- Wizard owns Dev Mode activation, deactivation, and GitHub integration
- `/dev` is the tracked framework payload, not a second runtime root
- `dev/ops/` is the canonical contributor operations area
- `dev/docs/` holds contributor-only documentation
- `dev/goblin/` holds the distributable dev scaffold
- `dev/goblin/tests/` holds tracked overlay tests for contributor and experimental flows
- local mutable work must stay in ignored `/dev` working paths until promoted

It must not contain production runtime logic. Wizard owns the live Dev Mode runtime and contributor control plane.
