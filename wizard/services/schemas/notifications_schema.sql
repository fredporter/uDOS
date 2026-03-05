CREATE TABLE IF NOT EXISTS notifications (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    title TEXT,
    message TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    duration_ms INTEGER NOT NULL,
    sticky INTEGER NOT NULL DEFAULT 0,
    action_count INTEGER DEFAULT 0,
    dismissed_at TEXT
);

CREATE TABLE IF NOT EXISTS notification_actions (
    id TEXT PRIMARY KEY,
    notification_id TEXT NOT NULL,
    label TEXT NOT NULL,
    action_type TEXT,
    callback_data TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(notification_id) REFERENCES notifications(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notification_exports (
    id TEXT PRIMARY KEY,
    export_date TEXT NOT NULL,
    format TEXT NOT NULL,
    file_path TEXT,
    record_count INTEGER,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_notifications_timestamp ON notifications(timestamp);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type);
CREATE INDEX IF NOT EXISTS idx_actions_notification_id ON notification_actions(notification_id);
