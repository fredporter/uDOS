# Managed Wizard Operations

Updated: 2026-03-03
Status: active how-to

## Purpose

Use this guide for managed Wizard control-plane deployments.

## Managed Mode

Managed mode uses:
- `UDOS_DEPLOY_MODE=managed`
- Wizard API as the operator surface
- `web-admin/` served from `/admin`
- canonical operations routes under `/api/ops/*`
- cron-style background job entrypoints instead of the in-process loop

## Required Environment

Set the managed environment values required by your host:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_JWT_SECRET`
- `SUPABASE_JWT_ISSUER`
- `SUPABASE_JWT_AUDIENCE`
- `SUPABASE_DB_DSN`
- `BETTERSTACK_SOURCE_TOKEN`
- `BETTERSTACK_INGESTING_HOST`
- `RENDER_EXTERNAL_URL`

## Bootstrap

```bash
cp .env.managed.example .env.managed
uv run python -m wizard.tools.migrate
uv run python -m wizard.tools.bootstrap_managed_env
```

Optional bootstrap subjects:
- `UDOS_BOOTSTRAP_ADMIN_SUBJECT`
- `UDOS_BOOTSTRAP_OPERATOR_SUBJECT`

## Job Entrypoints

Run these through your managed scheduler:
- `uv run python -m wizard.jobs.run_due_tasks`
- `uv run python -m wizard.jobs.health_snapshot`
- `uv run python -m wizard.jobs.maintenance`

## Scheduler Controls

Managed scheduler settings are controlled through `POST /api/ops/settings`.

Current controls:
- `max_tasks_per_tick`
- `tick_seconds`
- `allow_network`
- `off_peak_start_hour`
- `off_peak_end_hour`
- `api_budget_daily`
- `defer_alert_threshold`
- `backoff_alert_minutes`
- `auto_retry_deferred_reasons`
- `auto_retry_deferred_limit`
- `maintenance_retry_dry_run`
- `auto_retry_deferred_policy`
- `backoff_policy`

Runtime job and budget summaries are exposed through:
- `/api/ops/summary`
- `/api/ops/jobs`

Deferred queue recovery is now part of the managed operator flow:
- deferred reason counts are exposed in the control plane
- single queued items can be retried immediately
- deferred work can be retried in bulk by reason
- the maintenance job can automatically retry safe defer classes such as `network_unavailable`

Recommended defaults:
- keep `auto_retry_deferred_reasons` limited to recoverable classes
- start with `network_unavailable`
- keep `waiting_for_workflow_state` operator-driven unless the workflow is known to be idempotent
- use queue-pressure alerts to detect work that is thrashing instead of recovering

Reason-specific maintenance retry policy supports:
- `enabled`
- `limit`
- `dry_run`

Example:

```json
{
  "network_unavailable": {
    "enabled": true,
    "limit": 10,
    "dry_run": false
  },
  "api_budget_exhausted": {
    "enabled": true,
    "limit": 5,
    "dry_run": true
  }
}
```

Use `maintenance_retry_dry_run=true` for a global preview pass that records what would be retried without changing queue state.

## Inside-Out Workflow Model

Managed operations still start from readable project artifacts:
- `tasks.md`
- `*.tasks.md`
- `*workflow*.md`
- `*schedule*.md`

The control plane indexes these files and exposes them through the managed routes.

Prompt-driven jobs should keep the core offline path intact where possible, and only use provider-backed execution where policy and budget allow.

## Task Metadata

Supported task metadata for managed scheduling includes:
- `schedule` or `cadence`
- `window`
- `priority`
- `need`
- `resource_cost`
- `budget_units`
- `provider`
- `requires_network`
- `local_only`

Window-aware tasks are deferred into the correct execution window. Network or provider work is held when budget or network policy blocks execution.

## Related Docs

- `docs/roadmap.md`
- `docs/decisions/v1-5-workflow.md`
- `docs/howto/VIBE-MCP-INTEGRATION.md`
- `docs/howto/SERVER-MANAGEMENT.md`
