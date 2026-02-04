-- Anchor registry + locid mapping (stub)
-- Keep aligned with docs/v1-3 UNIVERSE.md and docs/uDOS-Gameplay-Anchors-v1.3-Spec.md

CREATE TABLE IF NOT EXISTS anchors (
  anchor_id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  version TEXT,
  description TEXT,
  capabilities_json TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS anchor_instances (
  instance_id TEXT PRIMARY KEY,
  anchor_id TEXT NOT NULL,
  meta_json TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY(anchor_id) REFERENCES anchors(anchor_id)
);

CREATE TABLE IF NOT EXISTS locids (
  locid TEXT PRIMARY KEY,
  anchor_id TEXT NOT NULL,
  space_id TEXT NOT NULL,
  layer TEXT NOT NULL,
  cell_id TEXT NOT NULL,
  place_id TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY(anchor_id) REFERENCES anchors(anchor_id)
);

CREATE TABLE IF NOT EXISTS places (
  place_id TEXT PRIMARY KEY,
  name TEXT,
  description TEXT,
  tags_json TEXT,
  locid TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY(locid) REFERENCES locids(locid)
);

CREATE INDEX IF NOT EXISTS idx_locids_anchor ON locids(anchor_id);
CREATE INDEX IF NOT EXISTS idx_locids_place ON locids(place_id);
