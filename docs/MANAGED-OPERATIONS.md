# Managed Wizard Operations

uDOS now supports a managed Wizard control plane mode:

- `UDOS_DEPLOY_MODE=managed`
- Wizard API served as the canonical operator surface
- `web-admin/` served at `/admin`
- canonical operations routes under `/api/ops/*`
- background jobs run through cron entrypoints instead of the in-process loop

## Required managed environment

Set these in the hosting platform:

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

Run:

```bash
cp .env.managed.example .env.managed
uv run python -m wizard.tools.migrate
uv run python -m wizard.tools.bootstrap_managed_env
```

Optional bootstrap subjects:

- `UDOS_BOOTSTRAP_ADMIN_SUBJECT`
- `UDOS_BOOTSTRAP_OPERATOR_SUBJECT`

## Job entrypoints

- `uv run python -m wizard.jobs.run_due_tasks`
- `uv run python -m wizard.jobs.health_snapshot`
- `uv run python -m wizard.jobs.maintenance`

## Inside-out workflow model

Operational work should start from human-readable sources in the vault:

- `tasks.md`
- `*.tasks.md`
- `*workflow*.md`
- `*schedule*.md`

The control plane indexes these files and exposes them through `/api/ops/summary` and `/api/ops/jobs`.
Prompt-driven jobs use the existing core prompt parser so task expansion still works offline from core.
