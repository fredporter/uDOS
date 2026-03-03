# Contributing to uDOS v1.5

uDOS v1.5 is in active restructure. Contributions should follow the runtime split and the new `@dev` workspace boundary.

## Before You Start

- read `AGENTS.md`
- read `dev/AGENTS.md` for contributor workspace rules
- use root `docs/` for runtime, operator, and public product docs
- use `dev/docs/` for contributor-only Dev Mode, Goblin, `vibe`, and GitHub integration docs

## Environment

```bash
git clone <repository-url>
cd uDOS
UV_PROJECT_ENVIRONMENT=.venv uv sync --extra udos-wizard --dev
```

Open the contributor workspace:

```bash
code ucode-dev.code-workspace
```

Workspace folders:

- `uDOS`: runtime root
- `@dev`: contributor framework root
- `@docs`: contributor documentation
- `@goblin`: distributable dev scaffold and testing-server layer

## Workspace Rules

- `ucode` is the standard runtime
- `vibe` is contributor tooling only inside the active Dev Mode lane
- Wizard owns Dev Mode activation, permissions, and GitHub integration
- tracked `@dev` payload is limited to `/dev` governance files, `dev/docs/`, and `dev/goblin/`
- local-only work belongs in `dev/files/`, `dev/relecs/`, `dev/dev-work/`, and `dev/testing/`

## Documentation Rules

- do not add contributor-only docs to root `docs/`
- promote mature contributor decisions into `dev/docs/specs/`, `dev/docs/features/`, or `dev/docs/howto/`
- compost superseded docs instead of leaving duplicate active copies

## Verification

Run the relevant checks for the area you changed:

```bash
./scripts/run_pytest.sh
uv run ruff check .
uv run ruff format --check .
```

For Dev Mode work, also verify the Wizard control plane and `@dev` workspace docs stay aligned.

## GitHub and Dev Mode

- use Wizard-managed Dev Mode controls and `/api/dev/*` for contributor lifecycle checks
- keep GitHub tokens and webhook secrets in Wizard-managed secrets, not in `/dev`
- sync only the tracked `@dev` payload

## Pull Requests

- keep changes scoped to one lane when possible
- call out any architecture boundary you touched
- include tests or a concrete reason tests were not run
- mention any follow-up compost or migration work that remains
