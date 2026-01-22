CREATE TABLE IF NOT EXISTS sync_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    notion_block_id TEXT NOT NULL,
    database_id TEXT NOT NULL,
    block_type TEXT,
    runtime_type TEXT,
    action TEXT NOT NULL,
    payload JSON NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    processed_at DATETIME,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS sync_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    notion_block_id TEXT NOT NULL,
    local_file_path TEXT,
    action TEXT,
    status TEXT,
    synced_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS block_mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    notion_block_id TEXT UNIQUE NOT NULL,
    local_file_path TEXT,
    content_hash TEXT,
    last_synced DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sync_queue_status ON sync_queue(status);
CREATE INDEX IF NOT EXISTS idx_block_mappings_notion_id ON block_mappings(notion_block_id);
