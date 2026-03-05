CREATE TABLE IF NOT EXISTS scheduler_settings (
    key TEXT PRIMARY KEY,
    value JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    schedule TEXT NOT NULL DEFAULT 'daily',
    state TEXT NOT NULL DEFAULT 'plant',
    provider TEXT,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    priority INTEGER NOT NULL DEFAULT 5,
    need INTEGER NOT NULL DEFAULT 5,
    mission TEXT,
    objective TEXT,
    resource_cost INTEGER NOT NULL DEFAULT 1,
    requires_network BOOLEAN NOT NULL DEFAULT FALSE,
    kind TEXT,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS task_runs (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL REFERENCES tasks(id),
    state TEXT NOT NULL,
    result TEXT,
    output TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS task_queue (
    id BIGSERIAL PRIMARY KEY,
    task_id TEXT NOT NULL REFERENCES tasks(id),
    run_id TEXT NOT NULL REFERENCES task_runs(id),
    state TEXT NOT NULL,
    scheduled_for TIMESTAMPTZ NOT NULL,
    processed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    priority INTEGER NOT NULL DEFAULT 5,
    need INTEGER NOT NULL DEFAULT 5,
    resource_cost INTEGER NOT NULL DEFAULT 1,
    requires_network BOOLEAN NOT NULL DEFAULT FALSE,
    defer_reason TEXT,
    defer_count INTEGER NOT NULL DEFAULT 0,
    backoff_seconds INTEGER NOT NULL DEFAULT 0,
    last_deferred_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS notifications (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    title TEXT,
    message TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    duration_ms INTEGER NOT NULL DEFAULT 5000,
    sticky BOOLEAN NOT NULL DEFAULT FALSE,
    action_count INTEGER NOT NULL DEFAULT 0,
    dismissed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS notification_actions (
    id TEXT PRIMARY KEY,
    notification_id TEXT NOT NULL REFERENCES notifications(id) ON DELETE CASCADE,
    label TEXT NOT NULL,
    action_type TEXT,
    callback_data TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS notification_exports (
    id TEXT PRIMARY KEY,
    export_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    format TEXT NOT NULL,
    file_path TEXT,
    record_count INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS operator_accounts (
    subject TEXT PRIMARY KEY,
    email TEXT,
    display_name TEXT,
    role TEXT NOT NULL DEFAULT 'operator',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
