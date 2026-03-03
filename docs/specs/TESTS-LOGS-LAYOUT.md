# Tests and Logs Layout Policy (v1.4.6)

This policy defines canonical locations for pytest artifacts, runtime logs, and cross-cutting test suites.

## Canonical Paths

- Runtime memory root: `memory/`
- Runtime logs root: `memory/logs/`
- Structured app logs: `memory/logs/udos/`
- Test artifacts root: `.artifacts/`
- Pytest cache: `.artifacts/test-runs/pytest-cache`
- Pytest temporary base: `.artifacts-pytest-tmp/`

## Test Directory Model

- Package-owned tests remain colocated:
  - `core/tests/`
  - `wizard/tests/`
- Cross-cutting repo tests live under:
  - `tests/integration/`
  - `tests/e2e/`
  - `tests/contracts/`

## Pytest Defaults

- `pyproject.toml` is the source of truth for pytest defaults (`testpaths`, `cache_dir`, `addopts`).
- root `scripts/run_pytest.sh` and `scripts/run_pytest_profile.sh` are the canonical executable entrypoints.
- `scripts/run_pytest_core_stdlib.sh` is the canonical active-core stdlib smoke lane.
- Default runs should not emit cache/temp files into package directories.

## CI and Local Consistency

- CI profile targets must reference the canonical cross-cutting paths under `tests/`.
- Local reproduction commands should mirror CI profile targets.

## Strict Logging Rule

- Wizard path helpers must resolve logs to `memory/logs/` only.
- Do not add alternate log roots in wizard config for routine runtime operation.
