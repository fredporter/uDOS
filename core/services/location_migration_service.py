"""
Location Migration Service - Migrate locations.json to SQLite when needed.

Provides automatic detection and migration of location data from JSON to SQLite
when file size exceeds 500KB or record count exceeds 1000.

Thresholds (ADR-0004):
  - File size: 500KB
  - Record count: 1000 records
  - Automatic backup before migration
  - Non-destructive (original JSON preserved)
  - Rollback support (delete .db to revert)
"""

import hashlib
import json
import os
import re
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from core.services.logging_api import get_logger, get_repo_root

logger = get_logger("location_migration")

SPATIAL_SCHEMA_PATH = Path(__file__).parents[2] / "v1-3" / "core" / "src" / "spatial" / "schema.sql"
MEMORY_SPATIAL_DIR = Path("memory") / "bank" / "spatial"
DEFAULT_ANCHOR_REGISTRY = Path(__file__).parents[2] / "v1-3" / "core" / "src" / "spatial" / "anchors.default.json"
DEFAULT_PLACE_CATALOG = Path(__file__).parents[2] / "v1-3" / "core" / "src" / "spatial" / "places.default.json"

PLACE_REF_RE = re.compile(
    r"^(?P<anchor>[^:]+)"
    r"(?::(?P<subanchor>[^:]+))?"
    r":(?P<space>SUR|UDN|SUB)"
    r":(?P<loc>L\d{3}-[A-Z]{2}\d{2}(?:-Z-?\d{1,2})?)"
    r"(?::D(?P<depth>\d+))?"
    r"(?::I(?P<instance>.+))?$"
)
LOC_ID_DETAIL_RE = re.compile(r"^L(?P<layer>\d{3})-(?P<cell>[A-Z]{2}\d{2})(?:-Z(?P<z>-?\d{1,2}))?$")


def _parse_place_ref(ref: str) -> Optional[Dict[str, Any]]:
    match = PLACE_REF_RE.match(ref)
    if not match:
        return None
    anchor = match.group("anchor")
    subanchor = match.group("subanchor")
    if anchor in {"BODY", "GAME", "CATALOG"} and subanchor:
        anchor_id = f"{anchor}:{subanchor}"
    else:
        anchor_id = anchor
    space = match.group("space")
    loc_id = match.group("loc")
    depth = int(match.group("depth")) if match.group("depth") else None
    instance = match.group("instance")
    layer = int(loc_id[1:4])
    final_cell = re.match(r"^L\d{3}-([A-Z]{2}\d{2})", loc_id).group(1)
    return {
        "anchor_id": anchor_id,
        "space": space,
        "loc_id": loc_id,
        "effective_layer": layer,
        "final_cell": final_cell,
        "depth": depth,
        "instance": instance,
    }


def _cell_to_col(cell: str) -> int:
    # Two-letter base-26 column encoding: AA=0, AB=1, ..., ZZ=675
    return (ord(cell[0]) - 65) * 26 + (ord(cell[1]) - 65)


def _loc_point(loc_id: str) -> Optional[Tuple[int, int, int, int]]:
    match = LOC_ID_DETAIL_RE.match(loc_id)
    if not match:
        return None
    layer = int(match.group("layer"))
    cell = match.group("cell")
    row = int(cell[2:4])
    col = _cell_to_col(cell[:2])
    z = int(match.group("z")) if match.group("z") is not None else 0
    return (layer, col, row, z)


class LocationMigrator:
    """Manage migration from JSON to SQLite for location data."""

    # Migration thresholds (ADR-0004)
    SIZE_THRESHOLD_KB = 500  # 500KB
    RECORD_THRESHOLD = 1000  # 1000 records

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize migrator.

        Args:
            data_dir: Path to location data directory
                     (defaults to memory/bank/locations/)
        """
        if data_dir is None:
            # Try: memory/bank/locations/
            data_dir = Path("memory/bank/locations")
            if not data_dir.exists():
                # Fallback to absolute path from root
                root = Path(__file__).parent.parent.parent
                data_dir = root / "memory" / "bank" / "locations"

        self.data_dir = Path(data_dir)
        self.json_path = self.data_dir / "locations.json"
        self.db_path = self.data_dir / "locations.db"
        self.backup_dir = self.data_dir / "backups"
        self.timezones_path = self.data_dir / "timezones.json"
        self.user_locations_path = self.data_dir / "user-locations.json"

        logger.info(f"[LOCAL] LocationMigrator initialized (data_dir={self.data_dir})")

    def should_migrate(self) -> Tuple[bool, str]:
        """
        Check if migration should be performed.

        Returns:
            Tuple of (should_migrate: bool, reason: str)
        """
        # Already migrated
        if self.db_path.exists():
            return False, "SQLite database already exists"

        # JSON doesn't exist
        if not self.json_path.exists():
            return False, "No locations.json found"

        # Check file size
        file_size_kb = self.json_path.stat().st_size / 1024
        if file_size_kb >= self.SIZE_THRESHOLD_KB:
            reason = f"File size {file_size_kb:.1f}KB exceeds {self.SIZE_THRESHOLD_KB}KB threshold"
            return True, reason

        # Check record count
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                record_count = len(data.get("locations", []))

                if record_count >= self.RECORD_THRESHOLD:
                    reason = f"Record count {record_count} exceeds {self.RECORD_THRESHOLD} threshold"
                    return True, reason
        except (json.JSONDecodeError, IOError) as e:
            return False, f"Error reading JSON: {e}"

        return False, "Below migration thresholds"

    def get_migration_status(self) -> Dict:
        """
        Get current migration status.

        Returns:
            Dict with status information
        """
        should_migrate, reason = self.should_migrate()

        if self.json_path.exists():
            file_size_kb = self.json_path.stat().st_size / 1024
            try:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    record_count = len(data.get("locations", []))
            except (json.JSONDecodeError, IOError):
                record_count = -1
        else:
            file_size_kb = 0
            record_count = 0

        db_records = 0
        if self.db_path.exists():
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM locations")
                db_records = cursor.fetchone()[0]
                conn.close()
            except sqlite3.Error:
                pass

        return {
            "backend": "SQLite" if self.db_path.exists() else "JSON",
            "should_migrate": should_migrate,
            "reason": reason,
            "json_exists": self.json_path.exists(),
            "json_size_kb": file_size_kb,
            "json_records": record_count,
            "db_exists": self.db_path.exists(),
            "db_records": db_records,
            "size_threshold_kb": self.SIZE_THRESHOLD_KB,
            "record_threshold": self.RECORD_THRESHOLD,
        }

    def perform_migration(self, backup: bool = True) -> Dict:
        """
        Perform migration from JSON to SQLite.

        Args:
            backup: Whether to backup JSON before migration (default: True)

        Returns:
            Dict with migration statistics
        """
        # Check if migration is needed
        should_migrate, reason = self.should_migrate()
        if not should_migrate:
            logger.info(f"[LOCAL] Migration not needed: {reason}")
            return {
                "success": False,
                "message": f"Migration not needed: {reason}",
            }

        # Load JSON data
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"[LOCAL] Failed to load locations.json: {e}")
            return {
                "success": False,
                "message": f"Failed to load locations.json: {e}",
            }

        # Create backup if requested
        if backup:
            self._create_backup()

        # Create SQLite database
        try:
            self._create_database()
            logger.info("[LOCAL] SQLite schema created successfully")
        except sqlite3.Error as e:
            logger.error(f"[LOCAL] Failed to create SQLite schema: {e}")
            return {
                "success": False,
                "message": f"Failed to create SQLite schema: {e}",
            }

        # Migrate data
        try:
            stats = self._migrate_data(json_data)
            logger.info(
                f"[LOCAL] Migration completed successfully: {stats['locations_migrated']} locations, "
                f"{stats['timezones_migrated']} timezones, {stats['connections_migrated']} connections"
            )
            return {
                "success": True,
                "message": "Migration completed successfully",
                **stats,
            }
        except Exception as e:
            logger.error(f"[LOCAL] Migration failed: {e}")
            # Clean up incomplete database
            if self.db_path.exists():
                self.db_path.unlink()
            return {
                "success": False,
                "message": f"Migration failed: {e}",
            }

    def _create_backup(self):
        """Create backup of locations.json before migration."""
        self.backup_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"locations_{timestamp}.json"

        try:
            with open(self.json_path, "r", encoding="utf-8") as f_in:
                with open(backup_path, "w", encoding="utf-8") as f_out:
                    f_out.write(f_in.read())
            logger.info(f"[LOCAL] Backup created: {backup_path}")
        except IOError as e:
            logger.warning(f"[LOCAL] Failed to create backup: {e}")
            raise

    def _create_database(self):
        """Create SQLite database with schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")

        # Create locations table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS locations (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                type TEXT,
                scale TEXT,
                region TEXT,
                continent TEXT,
                planet TEXT,
                coordinates TEXT,  -- JSON stored as text
                timezone TEXT,
                population INTEGER,
                area_km2 REAL,
                elevation_m REAL,
                founded_year INTEGER,
                metadata TEXT,  -- JSON stored as text
                created_at TEXT,
                updated_at TEXT
            )
        """
        )

        # Create timezones table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS timezones (
                zone TEXT PRIMARY KEY,
                offset TEXT,
                name TEXT,
                dst_observed INTEGER,
                metadata TEXT  -- JSON stored as text
            )
        """
        )

        # Create connections table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS connections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_location TEXT NOT NULL,
                to_location TEXT NOT NULL,
                direction TEXT,
                distance_km REAL,
                travel_time_hours REAL,
                transport_type TEXT,
                requires TEXT,  -- JSON stored as text
                label TEXT,
                metadata TEXT,  -- JSON stored as text
                FOREIGN KEY (from_location) REFERENCES locations(id),
                FOREIGN KEY (to_location) REFERENCES locations(id)
            )
        """
        )

        # Create user_additions table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_additions (
                id TEXT PRIMARY KEY,
                location_data TEXT NOT NULL,  -- JSON stored as text
                added_at TEXT,
                source TEXT
            )
        """
        )

        # Create tiles table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tiles (
                location_id TEXT NOT NULL,
                tile_key TEXT NOT NULL,
                content TEXT NOT NULL,  -- JSON stored as text
                PRIMARY KEY (location_id, tile_key),
                FOREIGN KEY (location_id) REFERENCES locations(id)
            )
        """
        )

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_locations_type ON locations(type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_locations_scale ON locations(scale)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_locations_region ON locations(region)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_locations_continent ON locations(continent)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_connections_from ON connections(from_location)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_connections_to ON connections(to_location)"
        )

        conn.commit()
        conn.close()

    def _seed_spatial_index(self) -> Dict[str, int]:
        spatial_db = self._get_spatial_db_path()
        if not spatial_db:
            return {"spatial_places_seeded": 0, "spatial_place_features_seeded": 0}

        conn = sqlite3.connect(spatial_db)
        conn.execute("PRAGMA foreign_keys = ON")
        self._apply_spatial_schema(conn)
        self._seed_spatial_anchors(conn)
        places = self._load_spatial_places()
        seeded = self._insert_spatial_places(conn, places)
        conn.commit()
        conn.close()
        return seeded

    def _get_spatial_db_path(self) -> Optional[Path]:
        env_vault = os.getenv("VAULT_ROOT")
        vault_root = (
            Path(env_vault).expanduser()
            if env_vault
            else get_repo_root() / "memory" / "vault"
        )
        candidates = [
            vault_root / ".udos" / "state.db",
            vault_root / "05_DATA" / "sqlite" / "udos.db",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        if not candidates[0].parent.exists():
            candidates[0].parent.mkdir(parents=True, exist_ok=True)
        return candidates[0]

    def _apply_spatial_schema(self, conn: sqlite3.Connection):
        if SPATIAL_SCHEMA_PATH.exists():
            conn.executescript(SPATIAL_SCHEMA_PATH.read_text())

    def _seed_spatial_anchors(self, conn: sqlite3.Connection):
        registry = MEMORY_SPATIAL_DIR / "anchors.json"
        if not registry.exists():
            registry = DEFAULT_ANCHOR_REGISTRY
        if not registry.exists():
            return
        anchors = json.loads(registry.read_text()).get("anchors", [])
        now = int(time.time())
        cursor = conn.cursor()
        for anchor in anchors:
            cursor.execute(
                """
                INSERT INTO anchors(anchor_id, kind, title, status, config_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(anchor_id) DO UPDATE SET
                    kind = excluded.kind,
                    title = excluded.title,
                    status = excluded.status,
                    config_json = excluded.config_json,
                    updated_at = excluded.updated_at
                """,
                (
                    anchor.get("anchorId"),
                    anchor.get("kind"),
                    anchor.get("title"),
                    anchor.get("status", "active"),
                    json.dumps(anchor.get("config", {})),
                    now,
                    now,
                ),
            )

    def _load_spatial_places(self) -> List[Dict[str, Any]]:
        catalog = MEMORY_SPATIAL_DIR / "places.json"
        if not catalog.exists():
            catalog = DEFAULT_PLACE_CATALOG
        if not catalog.exists():
            return []
        try:
            payload = json.loads(catalog.read_text())
            return payload.get("places", [])
        except (json.JSONDecodeError, IOError):
            return []

    def _insert_spatial_places(
        self, conn: sqlite3.Connection, places: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        if not places:
            return {"spatial_places_seeded": 0, "spatial_place_features_seeded": 0}
        cursor = conn.cursor()
        now = int(time.time())
        inserted = 0
        features_seeded = 0
        records: List[Dict[str, Any]] = []
        for place in places:
            place_ref = place.get("placeRef") or ""
            parsed = _parse_place_ref(place_ref)
            if not parsed:
                continue
            place_id = place.get("placeId") or self._build_place_id(
                parsed["anchor_id"],
                parsed["space"],
                parsed["loc_id"],
                parsed.get("depth"),
                parsed.get("instance"),
            )
            records.append({"place": place, "parsed": parsed, "place_id": place_id})

        inferred_links = self._infer_seed_links(records)

        for record in records:
            place = record["place"]
            parsed = record["parsed"]
            place_id = record["place_id"]
            self._ensure_locid(conn, parsed["loc_id"], parsed["effective_layer"], parsed["final_cell"])
            cursor.execute(
                """
                INSERT INTO places(place_id, anchor_id, space, loc_id, depth, instance, label, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(place_id) DO UPDATE SET
                  anchor_id = excluded.anchor_id,
                  space = excluded.space,
                  loc_id = excluded.loc_id,
                  depth = excluded.depth,
                  instance = excluded.instance,
                  label = excluded.label,
                  updated_at = excluded.updated_at
                """,
                (
                    place_id,
                    parsed["anchor_id"],
                    parsed["space"],
                    parsed["loc_id"],
                    parsed.get("depth"),
                    parsed.get("instance"),
                    place.get("label"),
                    now,
                    now,
                ),
            )
            inserted += 1
            place_for_seed = dict(place)
            explicit_links = place_for_seed.get("links")
            if not isinstance(explicit_links, list):
                inferred = inferred_links.get(place_id, [])
                if inferred:
                    place_for_seed["links"] = inferred
                    metadata = place_for_seed.get("metadata")
                    if not isinstance(metadata, dict):
                        metadata = {}
                    metadata.setdefault("link_mode", "inferred")
                    place_for_seed["metadata"] = metadata
            if self._upsert_place_seed_features(conn, place_id, place_for_seed, now):
                features_seeded += 1
        return {
            "spatial_places_seeded": inserted,
            "spatial_place_features_seeded": features_seeded,
        }

    def _infer_seed_links(self, records: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Infer deterministic adjacency for places with no explicit links."""
        groups: Dict[Tuple[str, str, int], List[Dict[str, Any]]] = {}
        for record in records:
            parsed = record["parsed"]
            key = (parsed["anchor_id"], parsed["space"], parsed["effective_layer"])
            groups.setdefault(key, []).append(record)

        inferred: Dict[str, List[str]] = {}
        for _group_key, members in groups.items():
            if len(members) < 2:
                continue
            for record in members:
                place = record["place"]
                if isinstance(place.get("links"), list) and len(place.get("links")) > 0:
                    continue
                origin = _loc_point(record["parsed"]["loc_id"])
                if origin is None:
                    continue
                neighbors: List[Tuple[int, str]] = []
                for candidate in members:
                    if candidate["place_id"] == record["place_id"]:
                        continue
                    point = _loc_point(candidate["parsed"]["loc_id"])
                    if point is None:
                        continue
                    # Same group already guarantees anchor/space/layer; compare cell + z.
                    dist = abs(origin[1] - point[1]) + abs(origin[2] - point[2]) + abs(origin[3] - point[3])
                    neighbors.append((dist, candidate["place_id"]))
                neighbors.sort(key=lambda item: (item[0], item[1]))
                links = [pid for _dist, pid in neighbors[:2]]
                if links:
                    inferred[record["place_id"]] = links
        return inferred

    def _ensure_locid(self, conn: sqlite3.Connection, loc_id: str, layer: int, cell: str):
        now = int(time.time())
        conn.execute(
            """
            INSERT INTO locids(loc_id, effective_layer, final_cell, created_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(loc_id) DO UPDATE SET
              effective_layer = excluded.effective_layer,
              final_cell = excluded.final_cell
            """,
            (loc_id, layer, cell, now),
        )

    def _build_place_id(
        self, anchor_id: str, space: str, loc_id: str, depth: Optional[int], instance: Optional[str]
    ) -> str:
        base = [anchor_id, space, loc_id, str(depth or ""), instance or ""]
        return hashlib.sha1(":".join(base).encode("utf-8")).hexdigest()

    def _upsert_place_seed_features(
        self,
        conn: sqlite3.Connection,
        place_id: str,
        place: Dict[str, Any],
        now: int,
    ) -> bool:
        z = place.get("z")
        z_min = place.get("z_min")
        z_max = place.get("z_max")
        links = place.get("links")
        traversal = {
            "stairs": place.get("stairs", []),
            "ramps": place.get("ramps", []),
            "portals": place.get("portals", []),
        }
        gameplay = {
            "quest_ids": place.get("quest_ids", []),
            "npc_spawn": place.get("npc_spawn", []),
            "hazards": place.get("hazards", []),
            "loot_tables": place.get("loot_tables", []),
            "interaction_points": place.get("interaction_points", []),
        }
        metadata = place.get("metadata", {})

        has_seed_payload = any(
            [
                isinstance(z, int),
                isinstance(z_min, int),
                isinstance(z_max, int),
                isinstance(links, list) and len(links) > 0,
                any(isinstance(v, list) and len(v) > 0 for v in traversal.values()),
                any(isinstance(v, list) and len(v) > 0 for v in gameplay.values()),
                isinstance(metadata, dict) and len(metadata) > 0,
            ]
        )
        if not has_seed_payload:
            return False

        conn.execute(
            """
            INSERT INTO place_seed_features
            (place_id, z, z_min, z_max, links_json, traversal_json, gameplay_json, metadata_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(place_id) DO UPDATE SET
              z = excluded.z,
              z_min = excluded.z_min,
              z_max = excluded.z_max,
              links_json = excluded.links_json,
              traversal_json = excluded.traversal_json,
              gameplay_json = excluded.gameplay_json,
              metadata_json = excluded.metadata_json,
              updated_at = excluded.updated_at
            """,
            (
                place_id,
                z if isinstance(z, int) else None,
                z_min if isinstance(z_min, int) else None,
                z_max if isinstance(z_max, int) else None,
                json.dumps(links if isinstance(links, list) else []),
                json.dumps(traversal),
                json.dumps(gameplay),
                json.dumps(metadata if isinstance(metadata, dict) else {}),
                now,
                now,
            ),
        )
        return True

    def _migrate_data(self, json_data: Dict) -> Dict:
        """
        Migrate location data from JSON to SQLite.

        Args:
            json_data: Parsed JSON data

        Returns:
            Dict with migration statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {
            "locations_migrated": 0,
            "timezones_migrated": 0,
            "connections_migrated": 0,
            "tiles_migrated": 0,
            "user_additions_migrated": 0,
        }

        # Migrate timezones
        timezones_data = {}
        if self.timezones_path.exists():
            try:
                with open(self.timezones_path, "r", encoding="utf-8") as f:
                    timezones_data = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        for zone, tz_info in timezones_data.items():
            cursor.execute(
                """
                INSERT OR IGNORE INTO timezones
                (zone, offset, name, dst_observed, metadata)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    zone,
                    tz_info.get("offset"),
                    tz_info.get("name"),
                    1 if tz_info.get("dst_observed") else 0,
                    json.dumps(tz_info.get("metadata", {})),
                ),
            )
        stats["timezones_migrated"] = len(timezones_data)

        # Migrate locations and connections
        for loc in json_data.get("locations", []):
            # Insert location
            cursor.execute(
                """
                INSERT INTO locations
                (id, name, description, type, scale, region, continent, planet,
                 coordinates, timezone, population, area_km2, elevation_m,
                 founded_year, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    loc.get("id"),
                    loc.get("name"),
                    loc.get("description"),
                    loc.get("type"),
                    loc.get("scale"),
                    loc.get("region"),
                    loc.get("continent"),
                    loc.get("planet"),
                    json.dumps(loc.get("coordinates", {})),
                    loc.get("timezone"),
                    loc.get("population"),
                    loc.get("area_km2"),
                    loc.get("elevation_m"),
                    loc.get("founded_year"),
                    json.dumps(loc.get("metadata", {})),
                    loc.get("created_at", datetime.now().isoformat()),
                    loc.get("updated_at", datetime.now().isoformat()),
                ),
            )
            stats["locations_migrated"] += 1

            # Insert connections
            for conn_data in loc.get("connections", []):
                cursor.execute(
                    """
                    INSERT INTO connections
                    (from_location, to_location, direction, distance_km,
                     travel_time_hours, transport_type, requires, label, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        loc.get("id"),
                        conn_data.get("to"),
                        conn_data.get("direction"),
                        conn_data.get("distance_km"),
                        conn_data.get("travel_time_hours"),
                        conn_data.get("transport_type"),
                        json.dumps(conn_data.get("requires", {})),
                        conn_data.get("label"),
                        json.dumps(conn_data.get("metadata", {})),
                    ),
                )
                stats["connections_migrated"] += 1

            # Insert tiles
            for tile_key, tile_data in loc.get("tiles", {}).items():
                cursor.execute(
                    """
                    INSERT INTO tiles
                    (location_id, tile_key, content)
                    VALUES (?, ?, ?)
                """,
                    (loc.get("id"), tile_key, json.dumps(tile_data)),
                )
                stats["tiles_migrated"] += 1

        # Migrate user additions
        if self.user_locations_path.exists():
            try:
                with open(self.user_locations_path, "r", encoding="utf-8") as f:
                    user_data = json.load(f)
                    for user_loc in user_data.get("locations", []):
                        cursor.execute(
                            """
                            INSERT OR IGNORE INTO user_additions
                            (id, location_data, added_at, source)
                            VALUES (?, ?, ?, ?)
                        """,
                            (
                                user_loc.get("id"),
                                json.dumps(user_loc),
                                user_loc.get("added_at", datetime.now().isoformat()),
                                user_loc.get("source", "user"),
                            ),
                        )
                        stats["user_additions_migrated"] += 1
            except (json.JSONDecodeError, IOError):
                pass

        conn.commit()
        conn.close()
        spatial_stats = self._seed_spatial_index()
        stats.update(spatial_stats)

        return stats

    def delete_database(self):
        """Delete SQLite database (rollback to JSON backend)."""
        if self.db_path.exists():
            self.db_path.unlink()
            logger.info(f"[LOCAL] SQLite database deleted: {self.db_path}")
            return True
        return False
