CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    schedule TEXT NOT NULL,
    provider TEXT,
    enabled INTEGER DEFAULT 1,
    priority INTEGER DEFAULT 5,
    need INTEGER DEFAULT 5,
    mission TEXT,
    objective TEXT,
    resource_cost INTEGER DEFAULT 1,
    requires_network INTEGER DEFAULT 0,
    kind TEXT,
    payload TEXT,
    state TEXT DEFAULT 'plant',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS task_runs (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL REFERENCES tasks(id),
    state TEXT DEFAULT 'sprout',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    result TEXT,
    output TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS task_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL REFERENCES tasks(id),
    run_id TEXT REFERENCES task_runs(id),
    state TEXT DEFAULT 'pending',
    scheduled_for TIMESTAMP,
    processed_at TIMESTAMP,
    priority INTEGER DEFAULT 5,
    need INTEGER DEFAULT 5,
    resource_cost INTEGER DEFAULT 1,
    requires_network INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS scheduler_settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE INDEX IF NOT EXISTS idx_tasks_state ON tasks(state);
CREATE INDEX IF NOT EXISTS idx_task_runs_task_id ON task_runs(task_id);
CREATE INDEX IF NOT EXISTS idx_task_runs_state ON task_runs(state);
CREATE INDEX IF NOT EXISTS idx_task_queue_state ON task_queue(state);
CREATE INDEX IF NOT EXISTS idx_task_queue_task_id ON task_queue(task_id);
