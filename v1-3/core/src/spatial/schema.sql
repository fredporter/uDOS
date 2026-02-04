PRAGMA foreign_keys = ON;

-- uDOS v1.3 Spatial Schema
-- Canonical LocId is compressed: L{EffectiveLayer}-{FinalCell}
-- Place = Anchor + Space + LocId (+ optional depth/instance)

-- 1) Anchors: coordinate frames / adapters
CREATE TABLE IF NOT EXISTS anchors (
  anchor_id     TEXT PRIMARY KEY,     -- "EARTH", "BODY:MOON", "GAME:skyrim"
  kind          TEXT NOT NULL,         -- "earth" | "body" | "game" | "catalog"
  title         TEXT NOT NULL,
  status        TEXT NOT NULL DEFAULT 'active',  -- active|deprecated
  config_json   TEXT NOT NULL,         -- JSON config (projection params, transforms, refs)
  created_at    INTEGER NOT NULL,
  updated_at    INTEGER NOT NULL
);

-- 2) LocIds: canonical compressed IDs (stable across anchors/spaces)
CREATE TABLE IF NOT EXISTS locids (
  loc_id            TEXT PRIMARY KEY,  -- "L305-DA11"
  effective_layer   INTEGER NOT NULL,
  final_cell        TEXT NOT NULL,      -- "DA11"
  created_at        INTEGER NOT NULL
);

-- 3) Places: user-facing “place keys” (anchor+space+locid)
CREATE TABLE IF NOT EXISTS places (
  place_id      TEXT PRIMARY KEY,      -- uuid or deterministic hash
  anchor_id     TEXT NOT NULL,
  space         TEXT NOT NULL,          -- SUR|UDN|SUB
  loc_id        TEXT NOT NULL,
  depth         INTEGER,                -- SUB depth (D0..Dn) stored as int
  instance      TEXT,                   -- optional shard/instance id
  label         TEXT,                   -- optional human label
  created_at    INTEGER NOT NULL,
  updated_at    INTEGER NOT NULL,
  FOREIGN KEY(anchor_id) REFERENCES anchors(anchor_id),
  FOREIGN KEY(loc_id) REFERENCES locids(loc_id)
);

CREATE INDEX IF NOT EXISTS idx_places_anchor_space_loc
  ON places(anchor_id, space, loc_id);

-- 4) Vault files + tags (frontmatter/grid_locations integration)
CREATE TABLE IF NOT EXISTS files (
  file_path     TEXT PRIMARY KEY,
  mtime         INTEGER NOT NULL,
  hash          TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS file_place_tags (
  file_path     TEXT NOT NULL,
  place_id      TEXT NOT NULL,
  source        TEXT NOT NULL DEFAULT 'frontmatter',  -- frontmatter|inferred|import
  created_at    INTEGER NOT NULL,
  PRIMARY KEY(file_path, place_id),
  FOREIGN KEY(file_path) REFERENCES files(file_path) ON DELETE CASCADE,
  FOREIGN KEY(place_id) REFERENCES places(place_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_file_place_tags_place
  ON file_place_tags(place_id);

-- 5) Optional earth bounds (internal only; users never see lat/long)
CREATE TABLE IF NOT EXISTS earth_cell_bounds (
  anchor_id      TEXT NOT NULL DEFAULT 'EARTH',
  loc_id         TEXT NOT NULL,
  min_lat        REAL NOT NULL,
  min_lon        REAL NOT NULL,
  max_lat        REAL NOT NULL,
  max_lon        REAL NOT NULL,
  projection     TEXT NOT NULL DEFAULT 'web_mercator',
  computed_at    INTEGER NOT NULL,
  PRIMARY KEY(anchor_id, loc_id),
  FOREIGN KEY(anchor_id) REFERENCES anchors(anchor_id),
  FOREIGN KEY(loc_id) REFERENCES locids(loc_id)
);

-- 6) Optional external refs (POIs, game coords, star catalogue ids)
CREATE TABLE IF NOT EXISTS external_refs (
  ref_id        TEXT PRIMARY KEY,
  anchor_id     TEXT NOT NULL,
  place_id      TEXT NOT NULL,
  provider      TEXT NOT NULL,          -- "osm" | "foursquare" | "steam" | "hipparcos" | etc.
  provider_key  TEXT NOT NULL,
  payload_json  TEXT,
  created_at    INTEGER NOT NULL,
  FOREIGN KEY(anchor_id) REFERENCES anchors(anchor_id),
  FOREIGN KEY(place_id) REFERENCES places(place_id)
);

CREATE INDEX IF NOT EXISTS idx_external_refs_place
  ON external_refs(place_id);
