# Branch Stabilization Plan (2026-02-15)

## Snapshot

Current branch: `main` (ahead of `origin/main`)

Worktree shape at snapshot:
- `R`: archive/script relocation batch
- `A`/`D`/`AM`: docs spine cleanup batch
- `M`: core command/runtime refactor batch
- `??`: new gameplay/toybox/sonic closure artifacts
- `m`: dirty submodules (`empire`, `sonic`)

## Stabilization Goal

Split the current mixed worktree into reviewable, low-risk commits and avoid feature coupling.

## Recommended Commit Sequence

1. Sonic v1.3.17 closure
- Scope: Sonic command/help parity, Sonic release checklist closure items, Sonic boot smoke gate.
- Files: `core/commands/sonic_handler.py`, `core/commands/help_handler.py`, `core/tests/test_sonic_handler.py`, `tools/ci/sonic_boot_smoke.py`, Sonic release docs/checklist, `docs/howto/UCODE-COMMAND-REFERENCE.md`, workflow gate update.

2. Docs spine/archive migration
- Scope: `docs/.archive/2026-02-15-docs-cleanup/*`, candidate removals, docs index/spine updates.
- Validate links after move.

3. Script archive migration
- Scope: `.archive/2026-02-15-scripts/*` and paired source deletions/renames under `bin/`, `core/tools/`, `wizard/tools/`.
- Keep optional imports tolerant (already partially addressed in `wizard/tools/__init__.py`).

4. Core command/runtime refactor
- Scope: `core/commands/*`, `core/tui/*`, `core/config/*`, `core/services/*`, tests.
- Run full core pytest + TS tests.

5. Gameplay + Toybox scaffold
- Scope: `core/commands/gameplay_handler.py`, `core/services/gameplay_service.py`, `library/hethack`, `library/elite`, `wizard/services/toybox/*`, related specs/tests.

6. Submodule updates
- Scope: `sonic`, `empire` gitlinks only, each with explicit upstream SHA rationale.

## Safety Rules

- Do not mix docs-only and runtime changes in the same commit.
- Keep submodule pointer bumps isolated from code edits.
- Run required gates after each bucket:
  - `python tools/ci/check_sonic_submodule_pin.py`
  - `python tools/ci/check_sonic_route_contract_v1_3_17.py`
  - `python -m pytest` for touched areas

## Minimal Push Strategy

- Push after each bucket and open incremental PRs (or one PR with multiple ordered commits).
- Avoid rebasing in the middle of bucketization unless conflicts block progress.
