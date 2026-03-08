# uDOS v1.5 — Known Issues

**Date:** 2026-02-26
**Scope:** Issues identified at v1.5 GA, tracked for v1.5.1+ patch stream.

---

## Active Issues

### KI-000 — Bubble Tea home menu shipped as a partly aspirational surface (P2)

**Scope:** `tui/internal/app/model.go`, `core/tui/protocol_bridge.py`, launcher/menu UX
**Symptom:** Built-in menu items could point to invalid or incomplete commands, and
  successful command results could be obscured by protocol progress packets, making
  the shell feel log-only rather than operational.
**Impact:** The stable launcher path existed, but the operational contract of the
  Bubble Tea shell was not fully closed for launcher/controller use.
**Workaround:** Use direct typed commands instead of trusting every built-in menu
  label as a complete workflow.
**Fix target:** v1.5.1 — close out truthful menu semantics, runner result visibility,
  and explicit deferment of unfinished create/edit workflows.
**Owner:** tui-runtime

---

### KI-001 — `tui_genre_manager` imports `yaml` at module level (P3)

**Scope:** `core/services/tui_genre_manager.py:3`
**Symptom:** `test_core_modules_import_with_system_python_no_venv` fails — system Python
  without a venv cannot import `core.commands.verify_handler` because the transitive
  chain pulls in `tui_genre_manager` which does `import yaml` unconditionally.
**Impact:** Core is documented as stdlib-only for the TUI offline path. This violates
  that contract when `verify_handler` or `draw_handler` is imported.
**Workaround:** Run all commands inside the `.venv`. The production install path uses
  `uv run` which activates the venv automatically.
**Fix target:** v1.5.1 — make the `yaml` import conditional or move to a lazy import
  guarded by `TYPE_CHECKING`.
**Owner:** core-runtime

---

### KI-002 — Telemetry `send_telemetry_event` returns `''` instead of `None` (P3)

**Scope:** `tests/core/test_telemetry_send.py::test_send_telemetry_event_does_nothing_when_api_key_is_none`
**Symptom:** `assert '' is None` — when `TELEMETRY_API_KEY` is absent, the function
  returns an empty string rather than `None`.
**Impact:** Cosmetic contract mismatch; no functional regression. Telemetry is
  disabled when the key is absent.
**Workaround:** None needed; telemetry silent-fails correctly at runtime.
**Fix target:** v1.5.1 — update return to `return None` when key is absent.
**Owner:** core-telemetry

---

### KI-003 — `test_ucode_registry_warnings` fails to collect (P3)

**Scope:** `wizard/tests/test_ucode_registry_warnings.py`
**Symptom:** `ImportError: cannot import name 'ClientSession' from 'mcp'` — the local
  `wizard/mcp/__init__.py` shadows the external `mcp` package, so MCP tool imports
  cannot find `ClientSession`.
**Impact:** This test file is excluded from the default test run. No wizard functionality
  is affected; the file tests MCP tool registration warnings only.
**Workaround:** Exclude via `--ignore=wizard/tests/test_ucode_registry_warnings.py`.
**Fix target:** v1.5.1 — rename or namespace `wizard/mcp/` to avoid shadowing the
  external `mcp` package.
**Owner:** wizard-mcp

---

### KI-004 — asyncio teardown warning in core test lane (P3)

**Scope:** Core test lane (observed in GA1 burn-in, Day 2–3)
**Symptom:** `PytestUnraisableExceptionWarning` around `BaseEventLoop.__del__`
  `KeyboardInterrupt` during test teardown.
**Impact:** Non-functional; does not cause test failures. Warning noise only.
**Workaround:** None needed; does not affect production behavior.
**Fix target:** v1.5.1 — investigate asyncio loop lifecycle in test fixtures.
**Owner:** core-runtime

---

## Deferred Enhancements (v1.5.1+)

| ID | Description | Target |
|---|---|---|
| DE-000 | Complete remaining Bubble Tea launcher action flows (mission/binder/edit/setup act paths) | v1.5.1 |
| DE-001 | GitHub integration consolidation (`wizard/services/github_integration.py`) | v1.5.1 |
| DE-002 | OS keychain integration (macOS Keychain, Windows Credential Manager) | v1.6 |
| DE-003 | Secret rotation schedule + audit log | v1.6 |
| DE-004 | `wizard/mcp/` namespace collision cleanup | v1.5.1 |

---

## Resolved Issues (Closed post-GA)

| Issue | Resolution |
|---|---|
| `reset_corr_id` ContextVar cross-context ValueError (24x/day in stream dispatch) | Fixed 2026-02-27 — token moved inside `event_stream()` generator |
| P-series architecture convergence (P1–P7) | All resolved 2026-02-26 |
| `.env` secrets exposure incident | Resolved 2026-02-24 — .env removed from git, CI gate added |
| Notification history silo (core JSONL vs wizard SQLite) | Unified via Protocol + Adapter (P3) |
| `/health` endpoint schema divergence | Merged into `health_probe()` (P1) |
| Core → Wizard circular import in `ucode.py` | Fixed via lazy import (P5) |
| Workspace filepicker path consistency bug | Fixed 2026-02-26 — `get_memory_dir()` base |
| Workspace traversal guard bypass | Fixed 2026-02-26 — `relative_to()` instead of `startswith()` |
