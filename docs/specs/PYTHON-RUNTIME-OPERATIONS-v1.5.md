# Python Runtime Operations v1.5

Status: Active  
Last updated: 2026-03-03

## Purpose

This spec defines the canonical Python operating model for uDOS v1.5.

## Canonical Runtime Contract

- repo-local environment path: `/.venv`
- environment manager: `uv`
- required Python version: `3.12`
- one root lockfile and one root environment

## Canonical Entry Points

### Runtime

- `./bin/udos`
- `./bin/udos wizard start`
- `uv run ./uDOS.py ...`

### Tests

- `./scripts/run_pytest.sh ...`
- `./scripts/run_pytest_profile.sh core|wizard|full`
- `./scripts/run_pytest_core_stdlib.sh`

## Environment Rules

### Required

- `UV_PROJECT_ENVIRONMENT=.venv`
- root tooling and workspace config must reference `/.venv`
- direct interpreter paths must use `/.venv/bin/python` only when required

### Forbidden

- committed active references to `venv/`
- separate repo-local `core/venv`
- separate repo-local `wizard/venv`
- implicit dependency installation during normal runtime startup

## Core Boundary Rules

Active core runtime surfaces must not import:

- `wizard`
- `requests`
- `httpx`
- `aiohttp`
- `fastapi`
- `flask`
- `pydantic`
- `dotenv`

Transitional exceptions must be explicit in the stdlib audit allowlist until removed.

## Wizard Dependency Rules

- Wizard dependencies are declared in the root project optional dependency groups
- Wizard execution uses the shared root `/.venv`
- Wizard-specific dependency presence is reported by runtime health checks rather than silently installed during unrelated `ucode` launches

## Pytest Rules

- root `pyproject.toml` is the source of truth for pytest defaults
- package-owned tests remain in `core/tests/` and `wizard/tests/`
- cross-cutting tests remain in `tests/`
- the `@dev` workspace may document test workflow policy but does not own the executable pytest wrappers

## Verification Surface

`UCODE REPAIR STATUS` must report:

- active Python executable
- canonical env path
- `uv` availability
- whether the active process is using `/.venv`
- core stdlib audit status
- Wizard runtime availability

## Smoke Validation

The canonical stdlib smoke lane is:

```bash
./scripts/run_pytest_core_stdlib.sh
```

It must:

- run the active core stdlib audit
- run representative deterministic core tests
- avoid depending on Wizard-only runtime paths
