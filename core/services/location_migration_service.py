"""
Location Migration Service - JSON → SQLite Migration
Handles automatic migration when locations.json exceeds 500KB threshold.

Phase 8: SQLite Migration
- Trigger: locations.json > 500KB or > 1000 records
- Tables: locations, timezones, connections, user_additions
- Maintains backward compatibility
"""

import json
import os
import sqlite3
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime

from core.services.logging_manager import get_logger

logger = get_logger("location-migration")


class LocationMigrator:
    """Handles migration from locations.json to locations.db SQLite database."""

    # Migration thresholds (per ADR-0004)
    SIZE_THRESHOLD_KB = 500  # 500KB file size
    RECORD_THRESHOLD = 1000  # 1000 location records

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize migrator.

        Args:
            data_dir: Path to data directory (defaults to memory/bank/locations/)
        """
        if data_dir is None:
            # Default to memory/bank/locations/
            project_root = Path(__file__).parent.parent.parent
            data_dir = project_root / "memory" / "bank" / "locations"

        self.data_dir = Path(data_dir)
        self.json_path = self.data_dir / "locations.json"
        self.db_path = self.data_dir / "locations.db"
        self.timezones_path = self.data_dir / "timezones.json"
        self.user_locations_path = self.data_dir / "user-locations.json"

        logger.info(f"[LOCAL] LocationMigrator initialized (data_dir={data_dir})")

    def should_migrate(self) -> tuple[bool, str]:
        """
        Check if migration should be triggered.

        Returns:
            (should_migrate: bool, reason: str)
        """
        # If DB already exists, no need to migrate
        if self.db_path.exists():
            return False, "SQLite database already exists"

        # If JSON doesn't exist, nothing to migrate
        if not self.json_path.exists():
            return False, "No locations.json found"

        # Check file size
        file_size_kb = self.json_path.stat().st_size / 1024
        if file_size_kb >= self.SIZE_THRESHOLD_KB:
            return (
                True,
                f"File size {file_size_kb:.1f}KB exceeds {self.SIZE_THRESHOLD_KB}KB threshold",
            )

        # Check record count
        try:
            with open(self.json_path, "r") as f:
                data = json.load(f)
                record_count = len(data.get("locations", []))

                if record_count >= self.RECORD_THRESHOLD:
                    return (
                        True,
                        f"Record count {record_count} exceeds {self.RECORD_THRESHOLD} threshold",
                    )
        except Exception as e:
            logger.warning(f"[LOCAL] Could not check record count: {e}")

        return False, f"Under thresholds (size: {file_size_kb:.1f}KB)"

    def create_schema(self, conn: sqlite3.Connection):
        """Create SQLite schema for location data."""
        cursor = conn.cursor()

        # Locations table (main location data)
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
                coordinates TEXT,
                timezone TEXT,
                population INTEGER,
                area_km2 REAL,
                elevation_m REAL,
                founded_year INTEGER,
                metadata TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """
        )

        # Timezones table (timezone reference data)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS timezones (
                zone TEXT PRIMARY KEY,
                offset TEXT NOT NULL,
                name TEXT,
                dst_observed INTEGER DEFAULT 0,
                metadata TEXT
            )
        """
        )

        # Connections table (location relationships)
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
                requires TEXT,
                label TEXT,
                metadata TEXT,
                FOREIGN KEY (from_location) REFERENCES locations(id),
                FOREIGN KEY (to_location) REFERENCES locations(id),
                UNIQUE(from_location, to_location, direction)
            )
        """
        )

        # User additions table (user-contributed locations)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_additions (
                id TEXT PRIMARY KEY,
                location_data TEXT NOT NULL,
                added_at TEXT NOT NULL,
                source TEXT DEFAULT 'user',
                FOREIGN KEY (id) REFERENCES locations(id)
            )
        """
        )

        # Tiles table (tile content for locations)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tiles (
                location_id TEXT NOT NULL,
                tile_key TEXT NOT NULL,
                content TEXT,
                PRIMARY KEY (location_id, tile_key),
                FOREIGN KEY (location_id) REFERENCES locations(id)
            )
        """
        )

        # Create indexes for common queries
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_locations_type ON locations(type)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_locations_scale ON locations(scale)"
        )
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
        logger.info("[LOCAL] SQLite schema created successfully")

    def migrate_timezones(self, conn: sqlite3.Connection) -> int:
        """Migrate timezone data if available."""
        if not self.timezones_path.exists():
            logger.info("[LOCAL] No timezones.json found, skipping timezone migration")
            return 0

        cursor = conn.cursor()

        try:
            with open(self.timezones_path, "r") as f:
                timezones_data = json.load(f)

            count = 0
            for zone, data in timezones_data.get("timezones", {}).items():
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO timezones (zone, offset, name, dst_observed, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        zone,
                        data.get("offset", "UTC+0"),
                        data.get("name", zone),
                        1 if data.get("dst", False) else 0,
                        json.dumps(
                            {
                                k: v
                                for k, v in data.items()
                                if k not in ["offset", "name", "dst"]
                            }
                        ),
                    ),
                )
                count += 1

            conn.commit()
            logger.info(f"[LOCAL] Migrated {count} timezones to SQLite")
            return count

        except Exception as e:
            logger.error(f"[LOCAL] Failed to migrate timezones: {e}")
            conn.rollback()
            return 0

    def migrate_locations(self, conn: sqlite3.Connection) -> int:
        """Migrate location data from JSON to SQLite."""
        cursor = conn.cursor()

        try:
            with open(self.json_path, "r") as f:
                locations_data = json.load(f)

            locations = locations_data.get("locations", [])
            now = datetime.utcnow().isoformat()

            count = 0
            for loc in locations:
                # Extract coordinates as JSON string
                coords = loc.get("coordinates", {})
                coords_str = json.dumps(coords) if coords else None

                # Extract metadata (everything not in main fields)
                main_fields = {
                    "id",
                    "name",
                    "description",
                    "type",
                    "scale",
                    "region",
                    "continent",
                    "planet",
                    "coordinates",
                    "timezone",
                    "population",
                    "area_km2",
                    "elevation_m",
                    "founded_year",
                    "connections",
                    "tiles",
                }
                metadata = {k: v for k, v in loc.items() if k not in main_fields}

                # Insert location
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO locations (
                        id, name, description, type, scale, region, continent, planet,
                        coordinates, timezone, population, area_km2, elevation_m, 
                        founded_year, metadata, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                        coords_str,
                        loc.get("timezone"),
                        loc.get("population"),
                        loc.get("area_km2"),
                        loc.get("elevation_m"),
                        loc.get("founded_year"),
                        json.dumps(metadata) if metadata else None,
                        now,
                        now,
                    ),
                )

                # Migrate connections
                for conn_data in loc.get("connections", []):
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO connections (
                            from_location, to_location, direction, distance_km, 
                            travel_time_hours, transport_type, requires, label, metadata
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            loc.get("id"),
                            conn_data.get("to"),
                            conn_data.get("direction"),
                            conn_data.get("distance_km"),
                            conn_data.get("travel_time_hours"),
                            conn_data.get("transport"),
                            (
                                json.dumps(conn_data.get("requires"))
                                if conn_data.get("requires")
                                else None
                            ),
                            conn_data.get("label"),
                            json.dumps(
                                {
                                    k: v
                                    for k, v in conn_data.items()
                                    if k
                                    not in [
                                        "to",
                                        "direction",
                                        "distance_km",
                                        "travel_time_hours",
                                        "transport",
                                        "requires",
                                        "label",
                                    ]
                                }
                            ),
                        ),
                    )

                # Migrate tiles
                for tile_key, tile_content in loc.get("tiles", {}).items():
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO tiles (location_id, tile_key, content)
                        VALUES (?, ?, ?)
                    """,
                        (loc.get("id"), tile_key, json.dumps(tile_content)),
                    )

                count += 1

            conn.commit()
            logger.info(f"[LOCAL] Migrated {count} locations to SQLite")
            return count

        except Exception as e:
            logger.error(f"[LOCAL] Failed to migrate locations: {e}")
            conn.rollback()
            raise

    def migrate_user_locations(self, conn: sqlite3.Connection) -> int:
        """Migrate user-contributed locations if available."""
        if not self.user_locations_path.exists():
            logger.info("[LOCAL] No user-locations.json found, skipping user migration")
            return 0

        cursor = conn.cursor()

        try:
            with open(self.user_locations_path, "r") as f:
                user_data = json.load(f)

            now = datetime.utcnow().isoformat()
            count = 0

            for loc in user_data.get("locations", []):
                # Insert into user_additions table
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO user_additions (id, location_data, added_at, source)
                    VALUES (?, ?, ?, ?)
                """,
                    (loc.get("id"), json.dumps(loc), now, "user"),
                )
                count += 1

            conn.commit()
            logger.info(f"[LOCAL] Migrated {count} user locations to SQLite")
            return count

        except Exception as e:
            logger.error(f"[LOCAL] Failed to migrate user locations: {e}")
            conn.rollback()
            return 0

    def perform_migration(self, backup: bool = True) -> Dict[str, Any]:
        """
        Perform complete migration from JSON to SQLite.

        Args:
            backup: Create backup of JSON files before migration

        Returns:
            Migration statistics dictionary
        """
        logger.info("[LOCAL] Starting location data migration (JSON → SQLite)")

        stats = {
            "started_at": datetime.utcnow().isoformat(),
            "locations_migrated": 0,
            "timezones_migrated": 0,
            "user_locations_migrated": 0,
            "connections_migrated": 0,
            "backup_created": False,
            "success": False,
            "error": None,
        }

        try:
            # Check if should migrate
            should_migrate, reason = self.should_migrate()
            if not should_migrate:
                logger.info(f"[LOCAL] Migration not needed: {reason}")
                stats["error"] = f"Migration not needed: {reason}"
                return stats

            # Create backup if requested
            if backup:
                backup_dir = self.data_dir / "backups"
                backup_dir.mkdir(exist_ok=True)
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

                if self.json_path.exists():
                    backup_path = backup_dir / f"locations_{timestamp}.json"
                    import shutil

                    shutil.copy2(self.json_path, backup_path)
                    logger.info(f"[LOCAL] Backup created: {backup_path}")
                    stats["backup_created"] = True

            # Create SQLite database
            conn = sqlite3.connect(self.db_path)

            try:
                # Create schema
                self.create_schema(conn)

                # Migrate timezones
                stats["timezones_migrated"] = self.migrate_timezones(conn)

                # Migrate main locations
                stats["locations_migrated"] = self.migrate_locations(conn)

                # Migrate user additions
                stats["user_locations_migrated"] = self.migrate_user_locations(conn)

                # Count connections
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM connections")
                stats["connections_migrated"] = cursor.fetchone()[0]

                stats["success"] = True
                stats["completed_at"] = datetime.utcnow().isoformat()

                logger.info(
                    f"[LOCAL] Migration completed successfully: "
                    f"{stats['locations_migrated']} locations, "
                    f"{stats['timezones_migrated']} timezones, "
                    f"{stats['connections_migrated']} connections"
                )

            finally:
                conn.close()

        except Exception as e:
            logger.error(f"[LOCAL] Migration failed: {e}")
            stats["error"] = str(e)
            stats["success"] = False

        return stats

    def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status and statistics."""
        status = {
            "db_exists": self.db_path.exists(),
            "json_exists": self.json_path.exists(),
            "should_migrate": False,
            "reason": "",
            "file_size_kb": 0,
            "record_count": 0,
            "db_stats": {},
        }

        # Check migration criteria
        should_migrate, reason = self.should_migrate()
        status["should_migrate"] = should_migrate
        status["reason"] = reason

        # Get JSON stats
        if self.json_path.exists():
            status["file_size_kb"] = round(self.json_path.stat().st_size / 1024, 2)
            try:
                with open(self.json_path, "r") as f:
                    data = json.load(f)
                    status["record_count"] = len(data.get("locations", []))
            except Exception as e:
                logger.warning(f"[LOCAL] Could not read JSON stats: {e}")

        # Get DB stats if exists
        if self.db_path.exists():
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute("SELECT COUNT(*) FROM locations")
                status["db_stats"]["locations"] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM timezones")
                status["db_stats"]["timezones"] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM connections")
                status["db_stats"]["connections"] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM user_additions")
                status["db_stats"]["user_additions"] = cursor.fetchone()[0]

                conn.close()
            except Exception as e:
                logger.warning(f"[LOCAL] Could not read DB stats: {e}")

        return status


def main():
    """Test migration service."""
    migrator = LocationMigrator()

    print("=" * 60)
    print("Location Migration Service - Status Check")
    print("=" * 60)

    status = migrator.get_migration_status()

    print(f"\nJSON File:")
    print(f"  Exists: {status['json_exists']}")
    print(f"  Size: {status['file_size_kb']}KB")
    print(f"  Records: {status['record_count']}")

    print(f"\nSQLite Database:")
    print(f"  Exists: {status['db_exists']}")
    if status["db_stats"]:
        print(f"  Locations: {status['db_stats'].get('locations', 0)}")
        print(f"  Timezones: {status['db_stats'].get('timezones', 0)}")
        print(f"  Connections: {status['db_stats'].get('connections', 0)}")
        print(f"  User Additions: {status['db_stats'].get('user_additions', 0)}")

    print(f"\nMigration Status:")
    print(f"  Should migrate: {status['should_migrate']}")
    print(f"  Reason: {status['reason']}")

    if status["should_migrate"]:
        print("\n" + "=" * 60)
        response = input("Perform migration now? (yes/no): ")
        if response.lower() == "yes":
            stats = migrator.perform_migration(backup=True)
            print("\nMigration Results:")
            print(f"  Success: {stats['success']}")
            print(f"  Locations: {stats['locations_migrated']}")
            print(f"  Timezones: {stats['timezones_migrated']}")
            print(f"  Connections: {stats['connections_migrated']}")
            print(f"  User Locations: {stats['user_locations_migrated']}")
            print(f"  Backup: {stats['backup_created']}")
            if stats.get("error"):
                print(f"  Error: {stats['error']}")


if __name__ == "__main__":
    main()
