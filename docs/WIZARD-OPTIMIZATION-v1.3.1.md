# Wizard Optimization & Hardening (v1.3.1+)

**Priority:** Critical — stabilize the Wizard server so it can safely host OAuth, plugin, and integration services without introducing drift to the Core runtime.

---

## Mission
Wizard must feel faster, more reliable, and harder to tamper with before expanding new UI and Sonic bolt-ons. This plan tracks the **optimisations**, **improvements**, and **hardening** workstreams around OAuth, workflow orchestration, integrations, and the plugin/library lifecycle so Core, Sonic, and automation runners can trust Wizard as the production services slab.

## Status Snapshot

### ✅ Completed
- Plugin/libraries now log to `memory/logs/health-training.log` and run through `wizard/services/library_manager_service.py` so automation banners reuse the same metadata that the GUI reports (`docs/WIZARD-SONIC-PLUGIN-ECOSYSTEM.md`).
- Self-healing telemetry flows expose health details to the banner and to `wizard/services/health_diagnostics.py` so every restart knows about remaining issues.
- Plugin repository metadata feed (`wizard/services/plugin_repository.py`) and LibraryManager wiring already support CLI `PLUGIN` commands, enabling the optimization story to focus on reliability rather than surface parity.

### 🔄 In Progress
- OAuth surface: `wizard/services/oauth_manager.py` with provider rotation, PKCE, and token refresh hooks plus secrets stored in `wizard/security/key_store.py`.
- Workflow + task graph: `wizard/services/workflow_manager.py`, `task_scheduler.py`, `sync_executor.py`, `quota_tracker.py`, and `cost_tracking.py` now feed the organic cron scheduler that hosts binder builds, HubSpot syncs, and file parsing jobs.
- Observability: `wizard/services/monitoring_manager.py`, `logging_manager.py`, and `health_diagnostics.py` push structured telemetry into `memory/logs/health-training.log` so automation scripts can gate `REPAIR`, `SHAKEDOWN`, and startup/reboot scripts safely.

---

## Milestones & Moves

### Milestone: Provider Gateway & Routing
**Mission:** provider routing is reliable, cost-aware, and failure-resilient.

**Moves**
- **Move: Provider fingerprints + routing balance**
  - Steps: cache provider capabilities per workspace; balance traffic across Ollama/OpenRouter/hosted APIs with `wizard/services/quota_tracker.py` and `cost_tracking.py`.
- **Move: Circuit breakers**
  - Steps: add per-provider circuit breakers via `wizard/services/monitoring_manager.py`; log to `memory/logs/provider-load.log`.

### Milestone: Workflow Throughput
**Mission:** mission containers run first, and long-running jobs stay observable.

**Moves**
- **Move: Priority scheduling**
  - Steps: prioritize mission containers in `wizard/services/workflow_manager.py`; expose ordering in `runner.status` dashboards.
- **Move: Core service reuse**
  - Steps: ensure binder/markdown parsing reuses `core/services/spatial_filesystem.py` so memory writes stay RBAC-safe.
- **Move: Automation hints**
  - Steps: extend `wizard/services/task_classifier.py` and `workflow_manager` to plumb new automation hints (F9 → `PLUGIN install`, F8 → `wizard` page).

### Milestone: Automation-Friendly APIs
**Mission:** API surfaces are validated, gated, and observable.

**Moves**
- **Move: Request validation + policy gating**
  - Steps: harden `/api/library/*` and `/api/parser/*` with `wizard/services/rate_limiter.py` and `wizard/services/policy_enforcer.py`.
- **Move: Install logging**
  - Steps: log plugin/extension installs to `memory/logs/health-training.log` and Sonic hotkey snapshots so automation can detect changes.

### Milestone: OAuth + Secrets Hygiene
**Mission:** OAuth flows are secure and auditable.

**Moves**
- **Move: PKCE + scope enforcement**
  - Steps: enforce PKCE, scope checks, and token reuse prevention in `wizard/services/oauth_manager.py`.
- **Move: Keystore protection**
  - Steps: encrypt keystore artifacts with `wizard/security/key_store.py`; rotate secrets via `wizard/services/secret_store.py` and log to `memory/logs/secret-rotation.log`.
- **Move: Admin-gated visibility**
  - Steps: push CLI secrets visibility through the config page (`wizard/routes/config_routes.py`) gated by `wizard/services/policy_enforcer.py` and `AccessLevel.ADMIN` checks in `commands/config_handler.py`.

### Milestone: API Abuse Prevention
**Mission:** repeated churn surfaces in dashboards and automation gates.

**Moves**
- **Move: Rate-limit visibility**
  - Steps: gate `/api/library/*` and `/api/config/*` through `wizard/services/rate_limiter.py` and `logging_manager.py`.
- **Move: Manifest verification**
  - Steps: validate plugin manifests with `wizard/services/plugin_repository.py`, verify signatures/cert chains, reject mismatched dependencies before copying into `/library/`.
- **Move: Repair diagnostics**
  - Steps: ensure `wizard/services/repair_service.py` and `health_diagnostics.py` include failing module tags (`[WIZ]`).

### Milestone: Network & Middleware
**Mission:** external-facing surfaces are locked down and auditable.

**Moves**
- **Move: Port access controls**
  - Steps: confirm `wizard/cli_port_manager.py` respects `api_token` ACLs and log unauthorized attempts.
- **Move: Upload hygiene**
  - Steps: verify `wizard/services/device_auth.py` and `wizard/services/upload_service.py` enforce TLS and sanitize payloads.
- **Move: Provider rotation visibility**
  - Steps: surface provider rotation decisions in `wizard/services/model_router.py` and `memory/logs/provider-rotation.log`.

### Milestone: Reliability & Observability
**Mission:** telemetry is consistent across dashboards, logs, and automation.

**Moves**
- **Move: SLO/latency metrics**
  - Steps: expand `wizard/services/monitoring_manager.py` to emit SLO/latency metrics and report them alongside `monitoring_summary`, `notification_history`, and throttle history into `memory/logs/health-training.log`.
- **Move: Log parity**
  - Steps: feed `monitoring_manager` output into `wizard/services/logging_manager.py` so CLI `LOGS --wizard` mirrors the dashboard timeline.
- **Move: Automation watchers**
  - Steps: notify `wizard/services/notification_history_service.py` when `health-training.log` shows `remaining > 0`, creating PATTERN entries; snapshot `/hotkeys/data` before `REPAIR`/startup-script runs.
- **Move: Throttle history visibility**
  - Steps: log `provider-load.log` and throttle history into automation triggers so `/dev/` restarts read the same entries that get written into provisioning dashboards.

---

## Assets & Font Distribution

- The curated font binaries (Chicago FLF, PetMe64, Player2up, Teletext50, plus the resolver-friendly retro collections) are kept in a local cache at `~/uDOS/fonts` and mirrored to `https://cdn.fredporter.com/*` as documented in `docs/WIZARD-FONT-SYNC.md`. The `/fonts` directory (root level) ships the manifest, attribution, and metadata so the public repo stays light while installs pull fonts from the canonical CDN or developer cache.
- Keep the font manifest, credits, and REST endpoints aligned with the CDN copy so automation can rebuild `/fonts` bundles from the signed files stored in S3 when needed.

## References

- `docs/WIZARD-SONIC-PLUGIN-ECOSYSTEM.md` — plugin catalog + sonic blueprint
- `docs/TUI-HOTKEY-AUTOMATION.md` — hotkey snapshots + automation gating
- `wizard/services` — routing, OAuth, workflows, logging, monitoring
- `wizard/security/key_store.py` — keystore management
- `sonic/docs/specs/sonic-screwdriver-v1.1.0.md` — sonic device/media expectations
