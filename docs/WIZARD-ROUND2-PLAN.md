# Wizard Round 2 Optimization & Hardening Plan

**Version:** 1.0
**Date:** 2026-01-31
**Priority:** Critical — stabilize the Wizard server so it can safely host OAuth, plugin, and integration services without introducing new drift to the Core runtime.
**Duration:** 4-8 weeks (Phase 6A-6D + follow-on tuning)

---

## Objective

Delivering Round 2 means Wizard must feel faster, more reliable, and harder to tamper with before we expand its Web UI (Round 3+) and Sonic bolt-ons. This plan tracks the **optimisations**, **improvements**, and **hardening** workstreams around OAuth, workflow orchestration, integrations, and the plugin/library lifecycle so that Core, Sonic, and automation runners can trust Wizard as the production services slab.

## Status Snapshot

### ✅ Completed
- Plugin/libraries now log to `memory/logs/health-training.log` and run through `wizard/services/library_manager_service.py` so automation banners reuse the same metadata that the GUI reports (`docs/WIZARD-SONIC-PLUGIN-ECOSYSTEM.md`).
- Self-healing telemetry flows expose health details to the banner and to `wizard/services/health_diagnostics.py` so every restart knows about remaining issues.
- Plugin repository metadata feed (`wizard/services/plugin_repository.py`) and LibraryManager wiring already support CLI `PLUGIN` commands, enabling the optimization story to focus on reliability rather than surface parity.

### 🔄 In Progress
- OAuth surface: `wizard/services/oauth_manager.py` with provider rotation, PKCE, and token refresh hooks plus secrets stored in `wizard/security/key_store.py`.
- Workflow + task graph: `wizard/services/workflow_manager.py`, `task_scheduler.py`, `sync_executor.py`, `quota_tracker.py`, and `cost_tracking.py` now feed the organic cron scheduler that hosts binder builds, HubSpot syncs, and file parsing jobs.
- Observability: `wizard/services/monitoring_manager.py`, `logging_manager.py`, and `health_diagnostics.py` push structured telemetry into `memory/logs/health-training.log` so automation scripts can gate `REPAIR`, `SHAKEDOWN`, and startup/reboot scripts safely.

## Optimization Areas

1. **Provider Gateway & Routing** (`wizard/services/ai_gateway.py`, `wizard/services/model_router.py`, `wizard/services/quota_tracker.py`)
   - Cache provider capability fingerprints per workspace so repeated prompts reuse warm models.
   - Balance traffic between Ollama, OpenRouter, and hosted APIs using `wizard/services/quota_tracker.py` + `cost_tracking.py`, ensuring the gateway never routes a burst to a single provider without logging it in `memory/logs/provider-load.log`.
   - Add per-provider circuit breakers triggered by the gateway watcher (`wizard/services/monitoring_manager.py`) when latency exceeds 500 ms.

2. **Workflow Throughput** (`wizard/services/workflow_manager.py`, `task_scheduler.py`, `sync_executor.py`, `wizard/routes/binder_routes.py`)
   - Prioritise mission containers before ad-hoc parsing jobs and reflect that order in `runner.status` dashboards.
   - Ensure binder/markdown parsing requests reuse Core services (`core/services/spatial_filesystem.py`) so memory writes stay authorized by RBAC.
   - Extend `wizard/services/task_classifier.py` and `workflow_manager` to plumb new automation hints (F9 -> `PLUGIN install`, F8 -> `wizard` page) so CLI/TUI flows share the same scheduling signals.

3. **Automation-Friendly APIs** (`wizard/routes/*`, `wizard/services/secret_store.py`, `wizard/services/extension_handler.py`)
   - Harden each `/api/v1/parser/*` endpoint with request validation and rate limiting backed by `wizard/services/rate_limiter.py` + `wizard/services/policy_enforcer.py`.
   - Log plugin/extension installs alongside `memory/logs/health-training.log` and the Sonic `/hotkeys/data` snapshot so automation knows what changed each round.

## Hardening & Security

1. **OAuth & Secrets**
   - Harden token rotation in `wizard/services/oauth_manager.py` (PKCE enforcement, scope checks, token reuse prevention).
   - Encrypt keystore artifacts with `wizard/security/key_store.py` and rotate secrets via `wizard/services/secret_store.py`, logging every rotation to `memory/logs/secret-rotation.log`.
   - Push CLI secrets visibility through the config page (`wizard/routes/config_routes.py`) but gate access with `wizard/services/policy_enforcer.py` and `AccessLevel.ADMIN` checks in `commands/config_handler.py`.

2. **API Abuse Prevention**
   - Gate `/api/v1/library/*` and `/api/v1/config/*` through `wizard/services/rate_limiter.py` and `logging_manager.py` so repeated churn surfaces in `monitoring_manager` dashboards.
   - Validate plugin manifests with `wizard/services/plugin_repository.py`, verify signatures/cert chains, and reject mismatched dependencies before copying into `/library/`.
   - Harden `wizard/services/repair_service.py` and `health_diagnostics.py` so Self-Healer events include the failing module, logged under `[WIZ]` tags.

3. **Network & Middleware**
   - Confirm `wizard/cli_port_manager.py` respects `api_token` ACLs and log unauthorized port attempts.
   - Verify `wizard/services/device_auth.py` and `wizard/services/upload_service.py` (if present) enforce TLS requirements and sanitize request payloads.
   - Ensure provider rotation (Ollama ↔ OpenRouter) is visible inside `wizard/services/model_router.py` so automation can audit switching decisions via `memory/logs/provider-rotation.log`.

## Reliability & Observability

- Expand `wizard/services/monitoring_manager.py` to emit SLO/latency metrics and report to `memory/logs/health-training.log` along with the hot reload/self-heal stats consumed by Round 3+ banners.
- Feed `monitoring_manager` output into `wizard/services/logging_manager.py` so CLI `LOGS --wizard` mirrors the dashboard timeline.
- Add `memory/logs/health-training.log` watchers that notify `wizard/services/notification_history_service.py` when a training round sees `remaining > 0`, creating a PATTERN entry for automation scripts (`startup-script.md`, `reboot-script.md`).
- Ensure `wizard/services/monitoring_manager.py` snapshots `/hotkeys/data` before each `REPAIR`/`startup-script` run so the key bindings cited in `docs/TUI-HOTKEY-AUTOMATION.md` stay consistent with the live map.

## Next Steps

1. Run `python -m wizard.server --no-interactive` with the new rate limiter/policy enforcer hooks and record baseline latency & error metrics (target < 1% 500 responses).
2. Complete OAuth Phase 6A (Google, Microsoft, GitHub, Apple) with PKCE/callback validations and refresh token cleanup scripts; log results under `[WIZ]` tags via `logging_manager`.
3. Expand workflow automation (Phase 6B-6D) to include HubSpot CRM, Notion, and iCloud syncs, ensuring each sync job is visible through `monitoring_manager` timelines and gating them via `quota_tracker` to avoid drift.
4. Harden plugin installs by wiring manifest verification code into `wizard/services/plugin_repository.py` and `LibraryManagerService`, and add automation acceptance tests that replay the Sonic catalog drive (see `sonic/docs/specs/sonic-screwdriver-v1.1.0.md`).
5. Document every optimization/hardening change in `docs/WIZARD-SONIC-PLUGIN-ECOSYSTEM.md` so later rounds inspect the same references before building UI surfaces.

## Daily Cycles (Jan 31–Feb 13)

| Cycle | Date | Focus & Deliverables | Assigned Squad | Dependencies |
| --- | --- | --- | --- | --- |
| 1 | Jan 31 | Baseline gateway telemetry: enable `monitoring_manager` metrics, warm provider fingerprints, log `memory/logs/health-training.log` snapshots for next-day automation gating. | Gateway/Telemetry Squad | `wizard/services/ai_gateway.py`, `wizard/services/monitoring_manager.py` |
| 2 | Feb 1 | Add per-provider circuit breakers + quota/cost tracking instrumentation; verify `quota_tracker` emits priority distribution summaries. | Gateway/Telemetry Squad | `wizard/services/quota_tracker.py`, `wizard/services/cost_tracking.py` |
| 3 | Feb 2 | Harden the first rate limiter/policy hooks on `/api/v1/library/*` and parser endpoints; ensure `memory/logs/provider-load.log` records burst throttles. | Workflow/Policy Squad | `wizard/services/rate_limiter.py`, `wizard/services/policy_enforcer.py` |
| 4 | Feb 3 | Initiate OAuth key audits: secret rotation logging via `wizard/services/secret_store.py`, `key_store` encryption verification, CLI config route gating. | Security/OAuth Squad | `wizard/security/key_store.py`, `wizard/routes/config_routes.py` |
| 5 | Feb 4 | PKCE callback enforcement + refresh token hygiene for Google/Microsoft/GitHub/Apple; log `[WIZ]` markers for each provider handshake. | Security/OAuth Squad | `wizard/services/oauth_manager.py` |
| 6 | Feb 5 | Instrument `workflow_manager` + `sync_executor` to surface mission container priorities to automation logs; gate binder requests via `core/services/spatial_filesystem.py`. | Workflow/Policy Squad | `wizard/services/workflow_manager.py`, `core/services/spatial_filesystem.py` |
| 7 | Feb 6 | Harden binder routes: confirm mission container scheduling, uuid tracking, and RBAC validation; schedule `monitoring_manager` watchers to flag drift. | Workflow/Policy Squad | `wizard/routes/binder_routes.py`, `wizard/services/notification_history_service.py` |
| 8 | Feb 7 | Strengthen plugin manifest verification: manifest signature checks, dependency wiring, rejection logging before library copy. | Plugin/Sonic Squad | `wizard/services/plugin_repository.py`, `wizard/services/library_manager_service.py` |
| 9 | Feb 8 | Sync `memory/logs/health-training.log` with plugin installs and `sonic` hotkey snapshots; ensure the `PLUGIN` command logs to the same payload. | Plugin/Sonic Squad | `docs/TUI-HOTKEY-AUTOMATION.md`, `wizard/services/plugin_repository.py` |
| 10 | Feb 9 | Update Sonic automation docs and dashboards; highlight `sonic/docs/specs/sonic-screwdriver-v1.1.0.md` expectations plus media log gating. | Plugin/Sonic Squad | `docs/WIZARD-SONIC-PLUGIN-ECOSYSTEM.md`, `sonic/docs/specs/sonic-screwdriver-v1.1.0.md` |
| 11 | Feb 10 | Harden integration API abuse prevention: apply rate limiting to `/api/v1/library/*` and parser endpoints, log throttle events, and confirm policy enforcement on parser jobs. | Workflow/Policy Squad | `wizard/routes/library_routes.py`, `wizard/services/rate_limiter.py` |
| 12 | Feb 11 | Expand automation watchers for `startup-script.md`/`reboot-script.md`: they must read `health-training.log`, confirm hotkey snapshot match, and emit PATTERN banners. | Integration/Operations Squad | `wizard/services/monitoring_manager.py`, `wizard/services/notification_history_service.py` |
| 13 | Feb 12 | Tune `monitoring_manager`/`logging_manager` dashboards: surface remaining issues, automation logs, and provider rotation events for daily reviews. | Integration/Operations Squad | `wizard/services/logging_manager.py`, `wizard/services/monitoring_manager.py` |
| 14 | Feb 13 | Begin HubSpot/Notion/iCloud sync ramp-up with quota gating while continuing to monitor SLOs and `health-training` state; prepare language for next round. | Integration/Operations Squad | `wizard/services/task_scheduler.py`, `wizard/services/sync_executor.py` |

> **Cycle 1 snapshot:** `tools/cycle1_gateway_telemetry.py` runs the gateway telemetry health check, records the provider fingerprint, and appends the latest summary (timestamp: 2026-01-31T14:35:39Z) to `memory/logs/health-training.log` so automation has the baseline it needs before Cycle 2.

> **Dev mode config applied:** `wizard/config/init_dev_config.py` now generates `wizard/config/dev.json` (host=127.0.0.1, port=8766, debug=True, service toggles + AI routing hints) so `/dev/` mode boots with the documented developer settings from `dev/docs/howto/wizard-dev-mode.md`.

> **Cycle 2 telemetry:** `tools/cycle1_gateway_telemetry.py` now also captures quota summaries, circuit-breaker hints, recent `memory/logs/provider-load.log` entries, and the new `MonitoringManager` summary so `health-training.log` mirrors what gets logged to `logging_manager` and `notification_history` downstream.

## References

- [docs/WIZARD-SONIC-PLUGIN-ECOSYSTEM.md](WIZARD-SONIC-PLUGIN-ECOSYSTEM.md) — plugin catalog + sonic blueprint
- [docs/TUI-HOTKEY-AUTOMATION.md](TUI-HOTKEY-AUTOMATION.md) — hotkey snapshots + automation gating
- [wizard/services](wizard/services) — routing, OAuth, workflows, logging, monitoring
- [wizard/security/key_store.py](wizard/security/key_store.py) — keystore management
- [docs/STREAM1-ACTION-PLAN.md](STREAM1-ACTION-PLAN.md) — reference for Round 1 vs Round 2 boundaries
- [sonic/docs/specs/sonic-screwdriver-v1.1.0.md](sonic/docs/specs/sonic-screwdriver-v1.1.0.md) — sonic device/media expectations
