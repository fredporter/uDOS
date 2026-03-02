CREATE TABLE IF NOT EXISTS launch_sessions (
    session_id TEXT PRIMARY KEY,
    target TEXT NOT NULL,
    mode TEXT NOT NULL,
    launcher TEXT,
    workspace TEXT,
    profile_id TEXT,
    auth_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    state TEXT NOT NULL,
    payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
