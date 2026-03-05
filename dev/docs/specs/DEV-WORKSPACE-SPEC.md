# Dev Workspace Spec

Updated: 2026-03-04
Status: Active

## Purpose

This spec defines the v1.5 `@dev` workspace contract.

`@dev` is the contributor framework lane inside the main repository. It exists to hold the tracked dev scaffold, contributor governance, Dev Mode policy, Goblin fixtures, and GitHub integration guidance without polluting root `docs/` or the production runtime tree.

## Canonical Layout

```text
dev/
├── AGENTS.md
├── README.md
├── extension.json
├── ops/
│   ├── README.md
│   ├── AGENTS.md
│   ├── DEVLOG.md
│   ├── project.json
│   ├── tasks.md
│   ├── tasks.json
│   ├── completed.json
│   ├── scheduler/
│   ├── templates/
│   ├── utils/
│   ├── workflows/
│   └── workspace/
├── docs/
│   ├── README.md
│   ├── DEV-MODE-POLICY.md
│   ├── decisions/
│   ├── devlog/
│   ├── features/
│   ├── howto/
│   ├── roadmap/
│   ├── contributors/
│   ├── tasks/
│   └── specs/
└── goblin/
    ├── README.md
    ├── scenarios/
    ├── seed/
    ├── server/
    ├── tests/
    └── test-vault/
```

## Sync Boundary

Tracked and distributable:

- `/dev` governance files
- `dev/ops/`
- `dev/docs/`
- `dev/goblin/`

Ignored and local-only:

- `dev/files/`
- `dev/relecs/`
- `dev/dev-work/`
- `dev/testing/`

## Goblin Contract

`dev/goblin/` is the distributable dev structure and testing-server layer.

It is used for:

- repeatable Wizard-side dev scenarios
- scaffolded seed content
- test vault fixtures
- server-layer examples and config stubs
- tracked overlay tests for contributor and experimental feature work

It must not become a second runtime root or a private scratch area.

## Documentation Boundary

Contributor-facing Dev Mode documentation belongs in `dev/docs/`.
Contributor mission state, workspace templates, and shared contributor tool config belong in `dev/ops/`.
Contributor submission drafts belong in `dev/docs/contributors/` before promotion into canonical `dev/docs/` tracks.

Root `docs/` must not host:

- Dev Mode onboarding
- `vibe` contributor setup
- `@dev` workspace rules
- Goblin framework instructions

Those documents must live under `dev/docs/howto/`, `dev/docs/specs/`, or `dev/docs/features/`.
