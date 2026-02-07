-- uMarkdown SQLite Schema
-- Local-first storage for binder documents and tasks
-- Created: 2026-01-15
-- Version: 1.0.0

---
-- LOCAL DOCUMENT LAYER
---

-- binder_documents: Main document/note storage
-- Markdown content with metadata
CREATE TABLE IF NOT EXISTS binder_documents (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  title TEXT NOT NULL,
  content TEXT,
  format TEXT DEFAULT 'ucode' CHECK(format IN ('ucode', 'story', 'marp', 'guide', 'config')),
  frontmatter JSON,
  status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'published', 'archived')),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- binder_tasks: Task and mission tracking
-- Organic cron scheduler integration
CREATE TABLE IF NOT EXISTS binder_tasks (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  document_id TEXT,
  title TEXT NOT NULL,
  description TEXT,
  priority TEXT DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high', 'critical')),
  status TEXT DEFAULT 'todo' CHECK(status IN ('todo', 'in_progress', 'done', 'archived')),
  stage TEXT DEFAULT 'plant' CHECK(stage IN ('plant', 'sprout', 'prune', 'trellis', 'harvest', 'compost')),
  due_date DATE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- binder_projects: Project grouping
CREATE TABLE IF NOT EXISTS binder_projects (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT,
  color TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- binder_resources: External resources and references
-- Links, embeds, attachments
CREATE TABLE IF NOT EXISTS binder_resources (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  document_id TEXT,
  title TEXT NOT NULL,
  url TEXT,
  resource_type TEXT CHECK(resource_type IN ('link', 'image', 'pdf', 'video', 'audio', 'embed')),
  metadata JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

---
-- SYNC METADATA
---

-- sync_log: History of all sync operations
-- For debugging and audit trail
CREATE TABLE IF NOT EXISTS sync_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  operation TEXT NOT NULL,
  local_type TEXT,
  local_id TEXT,
  remote_id TEXT,
  status TEXT,
  error_message TEXT,
  duration_ms INTEGER,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- sync_conflicts: Detected conflicts requiring resolution
-- Tracks bidirectional sync conflicts
CREATE TABLE IF NOT EXISTS sync_conflicts (
  id TEXT PRIMARY KEY,
  local_id TEXT NOT NULL,
  remote_id TEXT NOT NULL,
  conflict_type TEXT CHECK(conflict_type IN ('update', 'delete', 'move')),
  local_version TIMESTAMP NOT NULL,
  remote_version TIMESTAMP NOT NULL,
  resolution_strategy TEXT DEFAULT 'manual' CHECK(resolution_strategy IN ('local', 'remote', 'manual')),
  resolved_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

---
-- INDEXES FOR COMMON QUERIES
---

-- binder_documents indexes
CREATE INDEX IF NOT EXISTS idx_docs_project_id ON binder_documents(project_id);
CREATE INDEX IF NOT EXISTS idx_docs_status ON binder_documents(status);
CREATE INDEX IF NOT EXISTS idx_docs_updated_at ON binder_documents(updated_at);
CREATE INDEX IF NOT EXISTS idx_docs_by_project_and_status ON binder_documents(project_id, status);

-- binder_tasks indexes
CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON binder_tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON binder_tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_stage ON binder_tasks(stage);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON binder_tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_by_project_and_stage ON binder_tasks(project_id, stage);

-- binder_projects indexes
CREATE INDEX IF NOT EXISTS idx_projects_created_at ON binder_projects(created_at);

-- binder_resources indexes
CREATE INDEX IF NOT EXISTS idx_resources_project_id ON binder_resources(project_id);
CREATE INDEX IF NOT EXISTS idx_resources_document_id ON binder_resources(document_id);

-- sync_log indexes
CREATE INDEX IF NOT EXISTS idx_log_status ON sync_log(status);
CREATE INDEX IF NOT EXISTS idx_log_created_at ON sync_log(created_at);

-- sync_conflicts indexes
CREATE INDEX IF NOT EXISTS idx_conflicts_resolved_at ON sync_conflicts(resolved_at);
