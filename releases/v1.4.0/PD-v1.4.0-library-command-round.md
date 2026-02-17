# PD: v1.4.0 Library Command Round

## Context
Completion of v1.4.0 execution order items 5 and 6: LIBRARY command surface and residual modularization cleanup.

## Goals
- Implement `LIBRARY sync/status/info` command surfaces in core TUI.
- Wire `LibraryHandler` into dispatcher, help, ghost mode guard, and autocomplete.
- Add CI smoke gate for LIBRARY command.
- Add `library-command` lane to v1.4.0 container capability matrix.
- Rebase v1.3.25 contract freeze manifest after GPLAY→PLAY rename drift from prior round.
- All v1.4.0 preflight gates green.

## Scope Delivered
- `core/commands/library_handler.py` — STATUS, SYNC, INFO, LIST, HELP subcommands.
- `core/commands/__init__.py` — LibraryHandler lazy-loader registration.
- `core/tui/dispatcher.py` — LIBRARY route wired.
- `core/commands/help_handler.py` — LIBRARY in category and COMMANDS dict.
- `core/commands/ghost_mode_guard.py` — LIBRARY read-only subcommands allowed in ghost mode.
- `core/input/autocomplete.py` — LIBRARY autocomplete options.
- `core/tests/v1_4_0_library_command_test.py` — 14 unit tests (all pass).
- `tools/ci/check_v1_4_0_library_command_smoke.py` — 7-check smoke gate.
- `core/config/v1_4_0_container_capability_matrix.json` — library-command lane added.
- `tools/ci/check_v1_4_0_container_capability_matrix.py` — `skip_compose` flag support.
- `tools/ci/check_v1_4_0_release_preflight.py` — LIBRARY smoke gate added to preflight.
- `tools/ci/baselines/v1_3_25_contract_freeze_manifest.json` — rebased to current hashes.

## Non-Goals
- Full LIBRARY INSTALL/ENABLE/DISABLE TUI surface (wizard API handles this).
- Container runtime for library integrations.

## Acceptance Criteria
- All v1.4.0 preflight gates pass including new library-command smoke gate.
- All 14 LIBRARY command unit tests pass.
- LIBRARY appears in HELP command list and supports STATUS/SYNC/INFO in TUI.

## Validation Commands
```bash
python3 tools/ci/check_v1_4_0_library_command_smoke.py
python3 tools/ci/check_v1_4_0_container_capability_matrix.py
python3 tools/ci/check_v1_4_0_release_preflight.py
python3 -m pytest -q core/tests/v1_4_0_library_command_test.py
```

## Execution Order Status
1. ✅ TOYBOX lifecycle migration readiness gate
2. ✅ Sonic Dockerfile + smoke
3. ✅ Songscribe/Groovebox Dockerfile + smoke
4. ✅ Compose profile matrix validator
5. ✅ Library manager command completion (`LIBRARY sync/status`)
6. ✅ Residual modularization cleanup (contract freeze rebase, capability matrix lane, CI gate)
