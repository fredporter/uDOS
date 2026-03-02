CREATE TABLE IF NOT EXISTS monitoring_alerts (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    severity TEXT NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    service TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    acknowledged BOOLEAN NOT NULL DEFAULT FALSE,
    resolved BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS monitoring_audit (
    id TEXT PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    operation TEXT NOT NULL,
    service TEXT NOT NULL,
    user_name TEXT NOT NULL,
    success BOOLEAN NOT NULL DEFAULT TRUE,
    duration_ms DOUBLE PRECISION,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    error TEXT
);
