# v1.5 Python Runtime Contract

Status: Active  
Last updated: 2026-03-03

## Decision

uDOS v1.5 standardizes Python operation on one local runtime contract:

- canonical repo-local environment path: `/.venv`
- canonical environment manager: `uv`
- canonical Python version: `3.12`
- canonical test entrypoints: root `scripts/`

## Rationale

The repository currently mixes:

- `venv/` and `.venv/`
- `uv run ...` and direct interpreter calls
- root script wrappers and scattered pytest instructions

That fragmentation causes drift across:

- `ucode`
- Wizard launchers
- editor/workspace settings
- test workflows
- recovery docs

v1.5 needs one operator rule instead of multiple near-equivalents.

## Runtime Split

### Core

- `core/` remains stdlib-only by policy for active runtime surfaces
- `core/` must remain offline-safe by default
- `core/` must not require Wizard packages for normal `ucode` operation

### Wizard

- `wizard/` owns extended/networked dependencies
- Wizard uses the same shared root `/.venv`
- Wizard does not create or own a second repo-local Python home

### Dev Extension

- the `@dev` workspace at `/dev` owns contributor governance, docs, and workflow policy
- the `@dev` workspace does not own production runtime execution
- the `@dev` workspace does not become a second Python command surface

## Allowed Invocation Styles

Preferred:

- `uv run --project . ...`
- `./bin/udos ...`
- `./bin/udos wizard ...`
- `./scripts/run_pytest.sh ...`

Allowed when a concrete interpreter path is required by an editor/debug/task integration:

- `/.venv/bin/python`

## Prohibited Styles

- committed `venv/` references in active launchers, workspace config, or docs
- per-submodule repo-local virtualenv ownership for `core/` or `wizard/`
- implicit Wizard dependency installation during normal `ucode` launch
- moving production runtime entrypoints into the `@dev` workspace

## Test Ownership

- executable pytest wrappers live in root `scripts/`
- pytest discovery defaults live in root `pyproject.toml`
- contributor test policy and workflow guidance may live in the `@dev` workspace

## Enforcement

The contract is enforced through:

- launcher normalization on `/.venv` and `uv`
- workspace/tooling normalization on `/.venv`
- active core stdlib audit via `scripts/check_core_stdlib_contract.py`
- canonical smoke lane via `scripts/run_pytest_core_stdlib.sh`
- operator-facing runtime status via `UCODE REPAIR STATUS`
