-- Gameplay Anchors Schema (v1.3)
-- Keep aligned with sonic/docs/specs/uDOS-Gameplay-Anchors-v1.3-Spec.md

PRAGMA journal_mode=WAL;

-- 1) Anchor definitions
CREATE TABLE IF NOT EXISTS anchors (
  anchor_id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT,
  version TEXT,
  capabilities_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

-- 2) Runtime instances
CREATE TABLE IF NOT EXISTS anchor_instances (
  instance_id TEXT PRIMARY KEY,
  anchor_id TEXT NOT NULL,
  profile_id TEXT,
  space_id TEXT,
  seed TEXT,
  meta_json TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(anchor_id) REFERENCES anchors(anchor_id)
);

CREATE INDEX IF NOT EXISTS idx_anchor_instances_anchor
  ON anchor_instances(anchor_id);

-- 3) LocId bindings
CREATE TABLE IF NOT EXISTS locid_bindings (
  binding_id TEXT PRIMARY KEY,
  locid TEXT NOT NULL,
  anchor_id TEXT NOT NULL,
  instance_id TEXT,
  coord_kind TEXT NOT NULL,
  coord_json TEXT NOT NULL,
  label TEXT,
  tags TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(anchor_id) REFERENCES anchors(anchor_id),
  FOREIGN KEY(instance_id) REFERENCES anchor_instances(instance_id)
);

CREATE INDEX IF NOT EXISTS idx_locid_bindings_locid
  ON locid_bindings(locid);

CREATE INDEX IF NOT EXISTS idx_locid_bindings_anchor
  ON locid_bindings(anchor_id);

-- 4) Save states
CREATE TABLE IF NOT EXISTS anchor_savestates (
  state_id TEXT PRIMARY KEY,
  instance_id TEXT NOT NULL,
  anchor_id TEXT NOT NULL,
  state_ref TEXT NOT NULL,
  size_bytes INTEGER,
  hash TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY(instance_id) REFERENCES anchor_instances(instance_id),
  FOREIGN KEY(anchor_id) REFERENCES anchors(anchor_id)
);

CREATE INDEX IF NOT EXISTS idx_savestates_instance
  ON anchor_savestates(instance_id);

-- 5) Event log
CREATE TABLE IF NOT EXISTS anchor_events (
  event_id TEXT PRIMARY KEY,
  ts INTEGER NOT NULL,
  anchor_id TEXT NOT NULL,
  instance_id TEXT NOT NULL,
  type TEXT NOT NULL,
  locid TEXT,
  coord_kind TEXT,
  coord_json TEXT,
  data_json TEXT,
  FOREIGN KEY(anchor_id) REFERENCES anchors(anchor_id),
  FOREIGN KEY(instance_id) REFERENCES anchor_instances(instance_id)
);

CREATE INDEX IF NOT EXISTS idx_anchor_events_instance_ts
  ON anchor_events(instance_id, ts);

CREATE INDEX IF NOT EXISTS idx_anchor_events_locid
  ON anchor_events(locid);

-- 6) Quest definitions (Markdown-first)
CREATE TABLE IF NOT EXISTS quests (
  quest_id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  source_uri TEXT,
  frontmatter_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

-- 7) Quest progress
CREATE TABLE IF NOT EXISTS quest_progress (
  progress_id TEXT PRIMARY KEY,
  quest_id TEXT NOT NULL,
  profile_id TEXT NOT NULL,
  status TEXT NOT NULL,
  last_event_ts INTEGER,
  state_json TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(quest_id) REFERENCES quests(quest_id)
);

CREATE INDEX IF NOT EXISTS idx_quest_progress_profile
  ON quest_progress(profile_id);
