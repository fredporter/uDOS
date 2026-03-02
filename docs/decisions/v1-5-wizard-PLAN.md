# Simplify uDOS Operations Around a Managed Wizard Control Plane

## Summary

This plan keeps `core/` local, deterministic, and stdlib-only, and simplifies the operational burden by moving the networked control plane to a managed-first model:

- Host Wizard as a managed web service.
- Replace local Wizard state SQLite files with managed Postgres.
- Replace copy/paste admin tokens and local secret-writing flows with hosted auth and platform-managed secrets.
- Replace the long-lived local scheduler loop with managed cron-triggered workers.
- Collapse the operator UI into a single control plane instead of multiple dashboards and runbooks.

This recommendation is based on the current repo shape:
- Interactive install and setup remain broad and operator-heavy in [docs/INSTALLATION.md](/Users/fredbook/Code/uDOS/docs/INSTALLATION.md).
- Secrets are still centered on starting Wizard and adding values through a local dashboard in [docs/howto/SETUP-SECRETS.md](/Users/fredbook/Code/uDOS/docs/howto/SETUP-SECRETS.md).
- Task scheduling is local SQLite plus an in-process scheduler in [wizard/services/task_scheduler.py](/Users/fredbook/Code/uDOS/wizard/services/task_scheduler.py).
- Monitoring persists to local files in [wizard/services/monitoring_manager.py](/Users/fredbook/Code/uDOS/wizard/services/monitoring_manager.py).
- The web control plane currently expects a manually copied admin token in browser localStorage in [web-admin/src/routes/+page.svelte](/Users/fredbook/Code/uDOS/web-admin/src/routes/+page.svelte).
- Wizard currently exposes a very broad server surface from [wizard/server.py](/Users/fredbook/Code/uDOS/wizard/server.py).

## Chosen Operating Model

### What stays local

- `core/` remains the offline, deterministic command/runtime layer.
- Local developer mode continues to support `.env` + local SQLite for fast setup and offline work.
- Any pure `ucode` or local vault workflows remain available without hosted dependencies.

### What moves to managed services

- **Compute**: Render
  - One managed web service for Wizard API.
  - One managed background/cron service for due-task execution and maintenance jobs.
- **Primary data plane**: Supabase
  - Managed Postgres for Wizard operational state.
  - Managed auth for operator sign-in.
  - Managed storage for exported artifacts/snapshots that need durable access.
- **Observability**: Better Stack
  - Uptime checks, log aggregation, incident routing.
- **CI/CD**: GitHub Actions
  - Tests on PRs.
  - Automatic deploy to managed environment on merge to `main`.

## Why this stack

- Render supports managed web services and cron jobs suitable for FastAPI/Python deployments: [Web Services](https://render.com/docs/web-services), [Cron Jobs](https://render.com/docs/cronjobs), [Render Postgres](https://render.com/docs/postgresql).
- Supabase gives managed Postgres, auth, storage, and realtime in one platform: [Supabase Overview](https://supabase.com/docs), [Auth](https://supabase.com/docs/guides/auth), [Architecture](https://supabase.com/docs/architecture).
- Better Stack provides managed uptime, incidenting, and log management: [Getting Started](https://direct.betterstack.com/docs/getting-started/welcome/), [Logs collector](https://direct.betterstack.com/docs/logs/collector/).

## Target Architecture

### Runtime split

- `core/`
  - unchanged boundary
  - never depends on managed services directly
- `wizard/`
  - becomes the sole hosted control plane
  - owns auth, operational APIs, scheduling, monitoring, and integrations
- `web-admin/`
  - becomes the canonical operator UI
  - built once and served by Wizard at `/admin`
- `wizard/dashboard/`
  - removed from the hosted path and deprecated
  - only retained temporarily if something in `web-admin/` is not yet ported

### Data split

- **Postgres in Supabase**
  - tasks
  - task runs
  - scheduler settings
  - launch sessions
  - monitoring alerts
  - audit entries
  - notification history
  - control-plane config metadata
- **Supabase Storage**
  - config exports
  - generated artifacts the operator needs to download
- **Platform secrets**
  - provider/API credentials stored in Render environment groups and Supabase auth provider config
  - no production secret values stored in repo `.env` or app-managed local tombs
- **Local only**
  - local `.env` and local secret tomb remain dev-only fallback

## Public API / Interface Changes

### New canonical API surface

Create a single operations namespace:

- `GET /api/ops/summary`
- `GET /api/ops/health`
- `GET /api/ops/jobs`
- `POST /api/ops/jobs`
- `POST /api/ops/jobs/{job_id}/run`
- `GET /api/ops/alerts`
- `POST /api/ops/alerts/{alert_id}/ack`
- `POST /api/ops/alerts/{alert_id}/resolve`
- `GET /api/ops/logs`
- `GET /api/ops/config-status`
- `GET /api/ops/releases`

### Authentication change

- Remove manual admin-token entry from the operator UI.
- Require Supabase session auth for `/admin`.
- Require bearer JWT validation for all `/api/ops/*` routes.
- Add role model:
  - `operator`
  - `admin`

### Compatibility policy

For one release:

- keep `/api/tasks/*` as wrappers over `/api/ops/jobs*`
- keep `/api/monitoring/*` as wrappers over `/api/ops/health|alerts|logs`
- keep `/api/admin-token/*` read-only with deprecation responses
- remove write/generate flows after the deprecation window

## Internal Interface Changes

### New store abstraction

Introduce a Wizard-only persistence boundary:

- `wizard/services/store/base.py`
  - `WizardStore`
- `wizard/services/store/sqlite_store.py`
  - local dev implementation
- `wizard/services/store/postgres_store.py`
  - hosted implementation

`WizardStore` must own methods for:

- task CRUD and due-task claiming
- task run history
- launch session persistence
- alert and audit persistence
- notification history
- config export metadata

This avoids scattering raw `sqlite3` usage across services and keeps local-dev fallback.

### New configuration contract

Add environment mode:

- `UDOS_DEPLOY_MODE=local|managed`

Add required managed env vars:

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_JWT_ISSUER`
- `SUPABASE_JWT_AUDIENCE`
- `SUPABASE_DB_DSN`
- `BETTERSTACK_SOURCE_TOKEN`
- `BETTERSTACK_INGESTING_HOST`
- `RENDER_EXTERNAL_URL`

## Implementation Plan

### Phase 1: Collapse the operator entrypoint

1. Make `web-admin/` the only hosted operator UI.
2. Serve built `web-admin` assets from Wizard at `/admin`.
3. Remove the localStorage token UX from [web-admin/src/routes/+page.svelte](/Users/fredbook/Code/uDOS/web-admin/src/routes/+page.svelte).
4. Add session bootstrap endpoint:
   - `GET /api/ops/session`
   - returns current operator profile and role from validated JWT.
5. Mark `wizard/dashboard/` as non-canonical in docs and stop adding new operator features there.

### Phase 2: Move Wizard state to managed Postgres

1. Add the `WizardStore` abstraction.
2. Migrate these services first:
   - task scheduler
   - monitoring manager
   - launch session service
   - notification history
3. Keep SQLite implementation for local mode.
4. Add SQL migrations under:
   - `wizard/migrations/0001_ops_core.sql`
   - `wizard/migrations/0002_monitoring.sql`
   - `wizard/migrations/0003_launch_sessions.sql`
5. Add a migration runner:
   - `python -m wizard.tools.migrate`
6. Stop creating production state under `memory/wizard/*.db`.

### Phase 3: Replace in-process scheduler with managed cron workers

1. Remove the assumption that a long-lived `TaskSchedulerRunner` owns due-task execution in production.
2. Add a worker command:
   - `python -m wizard.jobs.run_due_tasks`
3. The worker must:
   - claim due jobs in Postgres with row locking
   - execute up to configured concurrency
   - write runs and failure status back to Postgres
4. Create Render cron jobs:
   - every minute: due-task executor
   - every 5 minutes: health snapshot job
   - hourly: maintenance/cleanup
5. Keep the existing in-process scheduler only for `UDOS_DEPLOY_MODE=local`.

### Phase 4: Replace app-managed production secrets with platform-managed secrets

1. Production:
   - secrets come from Render environment groups and Supabase auth/provider config
   - secret values are never written by the app
2. Local:
   - current secret tomb remains supported
3. Change the control plane UX:
   - Settings page becomes status/validation only
   - show “configured / missing / invalid” per integration
   - no “paste secret into app” flow in production mode
4. Deprecate write-heavy admin secret routes in [wizard/routes/config_admin_routes.py](/Users/fredbook/Code/uDOS/wizard/routes/config_admin_routes.py) for managed mode.

### Phase 5: Replace manual admin auth with hosted auth

1. Use Supabase Auth with GitHub sign-in for operator access.
2. Add JWT verification middleware in Wizard.
3. Add role lookup table in Postgres:
   - `operator_accounts`
   - `operator_roles`
4. Protect:
   - `/admin`
   - `/api/ops/*`
5. Remove:
   - manual admin token generation
   - browser localStorage bearer token entry
   - any docs telling the operator to copy tokens into the dashboard

### Phase 6: Centralize observability

1. Emit structured JSON logs to stdout from Wizard.
2. Ship logs to Better Stack.
3. Create monitors for:
   - `/health`
   - `/api/ops/summary`
   - cron heartbeat
4. Send alert destinations to email/Slack.
5. Keep local JSONL logs only in local mode and as short-lived fallback.

### Phase 7: Automate deploys and bootstrap

1. Add `render.yaml` to provision:
   - `wizard-api`
   - `wizard-jobs`
   - `wizard-maintenance`
2. Add GitHub Actions deployment workflow:
   - PR: test only
   - `main`: test, build, migrate, deploy
3. Add seed/bootstrap command:
   - `python -m wizard.tools.bootstrap_managed_env`
   - creates base rows, roles, scheduler defaults, and health records
4. Update installer docs:
   - local mode instructions
   - managed mode instructions
   - remove production guidance that depends on local dashboard setup

## Test Cases and Scenarios

### Unit tests

- `WizardStore` contract parity between SQLite and Postgres implementations.
- JWT verification and role enforcement.
- Due-task claiming logic prevents double execution.
- Managed mode forbids production secret writes through app routes.
- Deprecated route wrappers map exactly to new `/api/ops/*` handlers.

### Integration tests

- Sign in through Supabase-authenticated operator flow and load `/admin`.
- Schedule a job through `/api/ops/jobs`; cron worker picks it up and writes a run record.
- Alert lifecycle: create, acknowledge, resolve.
- Config-status endpoint correctly reports missing platform secrets without exposing values.
- Migrations run clean on empty database and upgrade from previous schema.

### End-to-end acceptance

- A new operator can reach a working control plane with:
  - one Render deploy
  - one Supabase project
  - no local dashboard secret entry
  - no copied admin token
- A deploy to `main` updates Wizard automatically.
- A failed scheduled job creates an alert visible in `/admin` and in Better Stack.
- Local mode still works offline with SQLite and existing `ucode` flows.

## Acceptance Criteria

- No production runbook requires “start Wizard locally, open dashboard, paste token, paste secrets”.
- No production-critical Wizard service depends on local SQLite files in `memory/wizard/`.
- Operator auth is session-based, not manual token-based.
- Scheduled jobs run via managed cron, not a permanently running local loop.
- There is one canonical hosted operator UI.
- Existing `core/` boundaries remain intact.

## Assumptions and Defaults

- Scope is the networked Wizard/control-plane side first, not a full rewrite of local `core/`.
- Managed-first is preferred over self-hosted operational tooling.
- Internal operator access is the initial audience; public multi-tenant product auth is out of scope.
- `web-admin/` is the canonical UI to keep, and `wizard/dashboard/` is the one to retire from hosted use.
- Backward compatibility lasts one release for the main task/monitoring/admin-token routes.
- Postgres migration is limited to Wizard/networked operational state; `core/` local data remains local unless separately justified.

## Risks to manage

- The repo currently mixes documented and actual operational paths; documentation cleanup must ship with code.
- A few Wizard services currently write local files directly; those must move behind the new store/config abstraction before hosted rollout.
- Extension-specific runbooks such as Empire should be migrated after the shared control-plane foundation, not before.

## Deliverables

- `render.yaml`
- managed-mode env contract and docs
- `WizardStore` abstraction with SQLite + Postgres implementations
- new `/api/ops/*` routes
- Supabase-authenticated `/admin`
- worker jobs for cron execution
- Better Stack logging/monitoring integration
- updated local vs managed installation/runbook documentation
