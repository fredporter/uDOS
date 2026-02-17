# PR Draft: v1.4.0 Library Command Round

## Summary
Completes v1.4.0 execution order items 5 and 6: LIBRARY command surface implementation, capability matrix extension, and contract freeze baseline rebase.

## Changes

### LIBRARY Command (execution order item 5)
- Add `core/commands/library_handler.py` with STATUS, SYNC, INFO, LIST, HELP subcommands backed by `LibraryManagerService`.
- Register `LibraryHandler` in `core/commands/__init__.py` lazy loader and `__all__`.
- Wire `"LIBRARY"` route in `core/tui/dispatcher.py`.
- Add LIBRARY to `System & Maintenance` category and COMMANDS dict in `core/commands/help_handler.py`.
- Allow LIBRARY read-only subcommands through ghost mode guard.
- Add `LIBRARY` autocomplete entry in `core/input/autocomplete.py`.

### CI Coverage (execution order item 6)
- Add `core/tests/v1_4_0_library_command_test.py` — 14 unit tests covering all subcommands and error paths.
- Add `tools/ci/check_v1_4_0_library_command_smoke.py` — 7-check smoke gate (import, STATUS, SYNC, INFO, HELP, dispatcher registration, test file).
- Add `library-command` lane to `core/config/v1_4_0_container_capability_matrix.json` with `skip_compose: true`.
- Update `tools/ci/check_v1_4_0_container_capability_matrix.py` to support `skip_compose` for non-docker lanes.
- Add LIBRARY smoke gate to `tools/ci/check_v1_4_0_release_preflight.py`.

### Contract Freeze Rebase
- Rebase `tools/ci/baselines/v1_3_25_contract_freeze_manifest.json` to current hashes after GPLAY→PLAY rename and deprecated_aliases cleanup from prior round.

## Key Files
- `core/commands/library_handler.py`
- `core/tests/v1_4_0_library_command_test.py`
- `tools/ci/check_v1_4_0_library_command_smoke.py`
- `core/config/v1_4_0_container_capability_matrix.json`
- `tools/ci/check_v1_4_0_container_capability_matrix.py`
- `tools/ci/check_v1_4_0_release_preflight.py`
- `tools/ci/baselines/v1_3_25_contract_freeze_manifest.json`

## Validation
```bash
python3 tools/ci/check_v1_4_0_library_command_smoke.py
python3 tools/ci/check_v1_4_0_container_capability_matrix.py
python3 tools/ci/check_v1_4_0_release_preflight.py
python3 -m pytest -q core/tests/v1_4_0_library_command_test.py core/tests/v1_4_0_container_kickoff_gates_test.py core/tests/v1_4_0_toybox_lifespan_readiness_test.py
```

## Rollout Notes
- No frozen v1.3.x contract surfaces modified (freeze rebase updates manifest baseline only).
- LIBRARY command delegates to wizard `LibraryManagerService` — no new service dependencies.
- `skip_compose` support in capability matrix validator is additive/non-breaking.
