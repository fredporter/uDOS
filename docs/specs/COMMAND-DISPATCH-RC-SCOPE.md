# Command Dispatch RC Scope

Date: 2026-02-22  
Status: Active

## Purpose

Freeze command syntax and fallback behavior for release-candidate scope.

## Dispatch Chain (Locked)

Route order is fixed:

1. `ucode` command match (Stage 1)
2. `shell` passthrough (Stage 2, safety-gated)
3. `dev_tool` fallback (Stage 3 skill routing)

## Canonical Alias Bridges (Locked)

- `RESTART` -> `REBOOT`
- `SCHEDULE` -> `SCHEDULER`
- `TALK` -> `SEND`
- Existing command-entry aliases retained:
  - `NEW` -> `FILE`
  - `EDIT` -> `FILE`
  - `UCLI` -> `UCODE`

## Validation Gates

The release-candidate scope is protected by tests:

- `core/tests/command_catalog_coverage_test.py`
- `core/tests/dispatch_rc_scope_contract_test.py`
- `core/tests/v1_4_4_command_dispatch_chain_test.py`

These tests lock:

- Stage 1 command catalog coverage against live dispatcher surface
- Canonical alias mappings
- Route ordering and fallback behavior
