-- Grid canvas render snapshots (stub)
-- Keep aligned with docs/specs/07-grid-canvas-rendering.md

CREATE TABLE IF NOT EXISTS grid_canvases (
  canvas_id TEXT PRIMARY KEY,
  width INTEGER NOT NULL,
  height INTEGER NOT NULL,
  title TEXT,
  theme TEXT,
  mode TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS grid_canvas_renders (
  render_id TEXT PRIMARY KEY,
  canvas_id TEXT NOT NULL,
  header_json TEXT,
  lines_text TEXT,
  raw_text TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY(canvas_id) REFERENCES grid_canvases(canvas_id)
);

CREATE INDEX IF NOT EXISTS idx_grid_canvas_renders_canvas
  ON grid_canvas_renders(canvas_id);
