# uDOS Roadmap (Canonical)

Last updated: 2026-03-02

This roadmap tracks active execution and planned development.

## v1.5 Rebaseline (Active)

Status on March 2, 2026:
- the earlier v1.5 GA claim dated February 26, 2026 is now treated as stale
- v1.5 has been reopened as an active rebaseline release
- `ucode` is the primary entry point for standard users
- `vibe` is being restricted to Dev Mode only
- certified release profiles now define supported install lanes: `core`, `home`, `creator`, `gaming`, `dev`

### Active Foundation Work

- `UCODE PROFILE` command family added as the release-control surface
- `UCODE OPERATOR` command family added as the deterministic local helper surface
- `UCODE EXTENSION`, `UCODE PACKAGE`, and `UCODE REPAIR STATUS` added for profile-aware operations
- non-Dev TUI fallback now routes to local operator planning instead of defaulting to `vibe`/provider routing
- certified profile manifest introduced at `distribution/profiles/certified-profiles.json`

### Immediate Exit Criteria

- `ucode` remains the sole primary interaction surface for normal runtime
- profile install/enable/verify flows work from the TUI
- standard runtime no longer depends on `vibe`
- release/governance docs stop claiming a completed v1.5 GA state

---

## Scope Notes

- macOS Swift thin UI source is not part of this repository and is maintained as an independent commercial companion application.
- Alpine-core thin UI remained conceptual and was not developed as an active implementation lane in this repository.
- Sonic work was tracked as a dedicated pending-round stream — completed 2026-02-23 (I6 schema contract parity + alias retirement, GA3 uHOME packaging). 55 sonic tests passing at v1.5 GA.

Previous roadmap snapshot is archived at:
- `/.compost/2026-02-22/archive/docs/roadmap-pre-cycle-d-2026-02-22.md`

---

## Architecture Convergence Sprint (2026-02-26) ✅

**Primary Focus:** Pre-release parallel-stack cleanup and service consolidation.
See full details: `docs/decisions/ARCHITECTURE-DEFERRED-MILESTONES.md`

### Completed
- ✅ Entry point & call graph audit — 6 entry points mapped, 8 parallel-stack problems (P1–P8) identified
- ✅ P2: Removed dead `wizard.json` read from `UnifiedConfigLoader`
- ✅ P4: `get_ok_local_status()` delegates to `AIProviderHandler.check_local_provider()` — single AI status path
- ✅ P5: Lazy imports in `core/tui/ucode.py` — eliminates Core→Wizard circular import
- ✅ P6: `/api/self-heal/status` wired to `collect_self_heal_summary()` via `run_in_executor`
- ✅ P7: `admin_secret_contract.py` → `secret_vault.py` — naming collision resolved
- ✅ P1: `GET /health` and `GET /api/dashboard/health` merged via `health_probe()` in `wizard/version_utils.py` + `dashboard_summary_routes.py`
- ✅ P3: Notification history unified — `NotificationHistoryProtocol` in core; `NotificationHistoryAdapter` registered in `CoreProviderRegistry` at Wizard startup; core writes to SQLite backend when Wizard is running, falls back to JSONL offline

### Key Commits
| Commit | Description |
|---|---|
| `a03facd` | Dead routes wired in wizard/server.py |
| `b85406c` | Duplicate method defs + unused imports removed |
| `07ce276` | P4/P6/P7 convergence |
| `6c4c953` | P2 dead config read + deferred milestones doc |
| `4e05561` | P5 circular import fix |
| `007b042` | P1 + P3 health consolidation + notification history |

---

## v1.4.6 Development Release (Upcoming)

**Primary Focus:** Environment configuration consolidation, testing phase verification, config alignment

### Completed Features
- ✅ Centralized `UnifiedConfigLoader` for all config sources (.env → TOML → JSON)
- ✅ Centralized `AIProviderHandler` for Ollama/Mistral status checking
- ✅ Centralized `PermissionHandler` created + critical class definition bug fixed
- ⏳ Partial TUI migration to config loader (7 os.getenv() → get_config())
- ⏳ Wizard provider routes migrated to AIProviderHandler
- ✅ Unit tests for all 3 central handlers (113/113 passing)
- ✅ `admin_secret_contract.py` (SecureVault interface for cloud API keys)

### Planned Features
- Complete config loader migration (100+ remaining `os.getenv()` calls)
- Path constants handler (`core/services/paths.py`)
- Documentation: ENV-STRUCTURE spec completion

### Exit Criteria
- [x] Config loader implementation complete with type-safe accessors
- [x] **FIX:** PermissionHandler class definition (critical bug — resolved)
- [x] **CREATE:** Unit tests for 3 central handlers — **113/113 passing**
- [x] All TUI/Wizard/core `os.getenv()` calls centralized — **100% complete** (3 remaining are in test migration demos only)
- [x] Path constants handler created (`core/services/paths.py`)
- [x] User data paths aligned — wizard routes + user_service both use `get_user_manager()` → `memory/bank/private/users.json`
- [x] Secrets location documented with path constants (`paths.py`: get_vault_root, get_vault_md_root, get_private_memory_dir)
- [x] Profile matrix tests pass — 16/16 passing
- [x] `admin_secret_contract.py` created — unblocks 11 AIProviderHandler cloud tests
- [x] Devlog: v1.4.6 completion summary — `docs/devlog/2026-02-24-v1.4.6-complete.md`

---

## v1.4.7 Development Release (Upcoming)

**Primary Focus:** Remaining v1.5 blockers, stability improvements, final pre-release polish

### Completed Features
- ✅ Sonic schema parity (SQL/JSON/Python) — 3/3 tests passing, contract validator in place
- ✅ Cloud provider expansion — `cloud_provider_executor.py` fallback chain (Mistral→OpenRouter→OpenAI→Anthropic→Gemini), 12 tests
- ✅ Ollama tier baselines — `ollama_tier_service.py` with explicit tier1/tier2/tier3 definitions, 22 tests
- ✅ Wizard secret sync drift repair — fixed `collect_admin_secret_contract` isolation, all 9 sync tests passing
- ✅ Sonic uHOME bundle contract — 21/21 tests passing
- ✅ uHOME HA bridge fully wired — real tuner/DVR/ad-processing/playback handlers, 32 integration tests

### Exit Criteria
- [x] Wizard secret store sync contract fully implemented — drift detection + repair tested
- [x] Sonic schema drift eliminated across all layers — 3/3 contract tests pass
- [x] Cloud provider fallback chain deterministic and tested — all 5 providers + 12 executor tests
- [x] Ollama tier-aware pulling stabilized — tier1/2/3 baselines + detect_missing_models
- [x] uHOME HA bridge routes live with integration tests — **32/32 passing** (tuner, DVR, ad-processing, playback)
- [x] Extended integration test coverage — 56 new tests this milestone (executor×12, tier×22, HA bridge×32 – net +22 with overlap reduction)
- [x] Devlog: v1.4.7 completion summary — `docs/devlog/2026-02-24-v1.4.7-complete.md`

---

## Flexible Development Buffer (Optional Enhancements)

**Placeholder rounds for additional development if needed** — no committed features.

If the v1.4.6 and v1.4.7 timelines accelerate, we can add:
- Additional cloud providers
- Extended Wizard dashboard consolidation
- 3DWORLD extension packaging
- Stub remediation (Git actions, plugin stubs, dataset parsing)
- Docs normalization work

Or slot this time for burn-in, stabilization, and user validation before RC phase.

---

## v1.5 Complete Tested Working Release ✅ (Superseded snapshot from 2026-02-26)

This section is retained as historical evidence only. It is no longer the active release truth for the repository after the March 2, 2026 rebaseline.

**Primary Focus:** Release candidate hardening → General Availability

### Release Scope (All v1.4.6 + v1.4.7 Features Plus)
- Offline/online parity validation
- Capability-tier installer gates with deterministic fallback
- Full cloud provider support matrix
- Ollama baseline with self-heal diagnostics
- Wizard config/secret sync contract verified
- Sonic drift cleanup complete
- uHOME + Home Assistant bridge live
- Sonic Screwdriver uHOME standalone packaging
- Wizard networking + beacon services stabilized

### Milestone Exit Criteria
- [x] RC1 burn-in cycle: multi-day reliability run completed
- [x] Extended integration test suite: core/wizard/full profiles passing — **2280/6 skipped** (2026-02-26)
- [x] GA1: Release-candidate burn-in cycle (multi-day reliability run + failure triage)
- [x] GA2: Post-RC stabilization sweep and doc finalization
- [x] GA3: Release readiness validation (operator runbooks tested end-to-end)
- [x] GA4: Final security audit and dependency scan — `.env` not in git, CI gate active, secrets.tomb in place
- [x] All freeze-blocker lanes closed and evidence captured
- [x] Operator readiness confirmed: deployment guides, troubleshooting, recovery paths documented

### v1.5 Launch Readiness Checklist
- [x] Documentation: Full operator runbooks for all deployment tiers
- [x] Minimum spec verified: Linux/macOS/Windows 10+ with explicit offline paths
- [x] Provider fallback tested under network failures, rate limits, auth errors
- [x] Ollama baseline proven stable across tier2/tier3 hardware profiles
- [x] Sonic Screwdriver uHOME installer tested on compatible hardware
- [x] Wizard networking beacon services stable under degraded conditions
- [x] Support: Known issues list with workarounds and tracking issues filed for v1.5.x patches — `docs/known-issues.md`

---

## v1.5.1+ Patch Stream (After v1.5 GA)

Will include:
- Security fixes and dependency updates
- Stability improvements from post-GA feedback
- Non-blocking feature enhancements
- Performance optimizations

---

---

## Cycle D Completion Summary

All work from Cycle D has been completed and moved into v1.4.6 and v1.4.7 milestones above.

For detailed completion evidence and status, see:
- `docs/devlog/2026-02-23-roadmap-completed-rollup.md` - Comprehensive completion summary
- `docs/devlog/2026-02-24-testing-phase-verification.md` - Testing phase validation
- `docs/devlog/2026-02-24-env-alignment-audit.md` - Configuration system audit

### Completed Cycle D Tracks
- ✅ Minimum spec parity validation
- ✅ Installer capability gates (I1, I2)
- ✅ Cloud provider schema and fallback chain (I3)
- ✅ Ollama baseline tier pulls and self-heal (I4)
- ✅ Wizard config/secret sync drift repair (I5)
- ✅ Sonic schema contract cleanup (I6)
- ✅ RC1 validation sweep (I7)
- ✅ GA1: Release-candidate burn-in cycle
- ✅ GA2: uHOME + Home Assistant bridge
- ✅ GA3: Sonic uHOME packaging

All evidence captured in devlog/ directory.

---

## Quality Gate Rules

- [x] Runtime logs remain under memory/logs and test artifacts remain under .artifacts paths.
- [x] All v1.4.6 and v1.4.7 development work captured with evidence in `docs/devlog/`
- [x] v1.5 release readiness validated through full test matrix before GA — **2280 passed** (2026-02-26)
- [x] Known issues and patch assignments prepared for v1.5.1+ stream before launch — `docs/known-issues.md`
