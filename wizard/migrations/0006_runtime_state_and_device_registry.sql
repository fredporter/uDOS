CREATE TABLE IF NOT EXISTS runtime_state (
    key TEXT PRIMARY KEY,
    payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS device_registry (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    device_type TEXT NOT NULL,
    trust_level TEXT NOT NULL,
    status TEXT NOT NULL,
    transport TEXT NOT NULL DEFAULT 'meshcore',
    paired_at TEXT NOT NULL,
    last_seen TEXT,
    last_sync TEXT,
    sync_version INTEGER NOT NULL DEFAULT 0,
    public_key TEXT DEFAULT '',
    token_hash TEXT DEFAULT '',
    token_last_rotated_at TEXT
);
