import json
import sqlite3
from pathlib import Path

import core.services.location_migration_service as location_migration
from core.services.location_migration_service import LocationMigrator


def _schema_sql() -> str:
    root = Path(__file__).resolve().parents[2]
    return (root / "core" / "src" / "spatial" / "schema.sql").read_text(encoding="utf-8")


def test_insert_spatial_places_persists_seed_features(tmp_path):
    migrator = LocationMigrator(data_dir=tmp_path)
    conn = sqlite3.connect(tmp_path / "state.db")
    conn.executescript(_schema_sql())
    now = 1739580000
    conn.execute(
        """
        INSERT INTO anchors(anchor_id, kind, title, status, config_json, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        ("EARTH", "earth", "Earth", "active", "{}", now, now),
    )

    stats = migrator._insert_spatial_places(
        conn,
        [
            {
                "placeId": "seed-feature-place",
                "label": "Seed Feature Place",
                "placeRef": "EARTH:SUR:L300-AA10-Z2",
                "z": 2,
                "z_min": 0,
                "z_max": 9,
                "links": ["tokyo-shibuya"],
                "portals": ["lift-a"],
                "quest_ids": ["q.seed.001"],
            }
        ],
    )
    conn.commit()

    assert stats["spatial_places_seeded"] == 1
    assert stats["spatial_place_features_seeded"] == 1

    row = conn.execute(
        """
        SELECT z, z_min, z_max, links_json, traversal_json, gameplay_json
        FROM place_seed_features WHERE place_id = ?
        """,
        ("seed-feature-place",),
    ).fetchone()
    assert row is not None
    assert row[0] == 2
    assert row[1] == 0
    assert row[2] == 9
    assert "tokyo-shibuya" in json.loads(row[3])
    assert "lift-a" in json.loads(row[4])["portals"]
    assert "q.seed.001" in json.loads(row[5])["quest_ids"]
    conn.close()


def test_load_spatial_places_falls_back_to_tracked_default(tmp_path, monkeypatch):
    migrator = LocationMigrator(data_dir=tmp_path)
    missing_memory_dir = tmp_path / "no-memory-seed"
    missing_memory_dir.mkdir(parents=True, exist_ok=True)

    default_catalog = Path(__file__).resolve().parents[2] / "core" / "src" / "spatial" / "places.default.json"
    monkeypatch.setattr(location_migration, "MEMORY_SPATIAL_DIR", missing_memory_dir)
    monkeypatch.setattr(location_migration, "DEFAULT_PLACE_CATALOG", default_catalog)

    places = migrator._load_spatial_places()
    assert len(places) >= 1
    assert any("z" in place for place in places)


def test_load_spatial_places_merges_locations_seed_overrides(tmp_path, monkeypatch):
    migrator = LocationMigrator(data_dir=tmp_path)
    missing_memory_dir = tmp_path / "no-memory-seed"
    missing_memory_dir.mkdir(parents=True, exist_ok=True)

    places_catalog = tmp_path / "places.default.json"
    places_catalog.write_text(
        json.dumps(
            {
                "places": [
                    {
                        "placeId": "forest-clearing",
                        "label": "Forest Clearing",
                        "placeRef": "EARTH:SUR:L300-AA10",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    locations_seed = tmp_path / "locations-seed.default.json"
    locations_seed.write_text(
        json.dumps(
            {
                "locations": [
                    {
                        "placeId": "forest-clearing",
                        "placeRef": "EARTH:SUR:L300-AA10",
                        "links": ["tokyo-shibuya"],
                        "quest_ids": ["intro.welcome"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(location_migration, "MEMORY_SPATIAL_DIR", missing_memory_dir)
    monkeypatch.setattr(location_migration, "DEFAULT_PLACE_CATALOG", places_catalog)
    monkeypatch.setattr(location_migration, "DEFAULT_LOCATIONS_SEED", locations_seed)

    places = migrator._load_spatial_places()
    assert len(places) == 1
    assert places[0]["placeId"] == "forest-clearing"
    assert places[0]["links"] == ["tokyo-shibuya"]
    assert places[0]["quest_ids"] == ["intro.welcome"]


def test_insert_spatial_places_infers_links_when_missing(tmp_path):
    migrator = LocationMigrator(data_dir=tmp_path)
    conn = sqlite3.connect(tmp_path / "state.db")
    conn.executescript(_schema_sql())
    now = 1739580000
    conn.execute(
        """
        INSERT INTO anchors(anchor_id, kind, title, status, config_json, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        ("EARTH", "earth", "Earth", "active", "{}", now, now),
    )

    stats = migrator._insert_spatial_places(
        conn,
        [
            {"placeId": "a", "label": "A", "placeRef": "EARTH:SUR:L300-AA10"},
            {"placeId": "b", "label": "B", "placeRef": "EARTH:SUR:L300-AA11"},
            {"placeId": "c", "label": "C", "placeRef": "EARTH:SUR:L300-AA12"},
        ],
    )
    conn.commit()

    assert stats["spatial_places_seeded"] == 3
    assert stats["spatial_place_features_seeded"] == 3

    rows = conn.execute(
        """
        SELECT place_id, links_json, metadata_json
        FROM place_seed_features
        ORDER BY place_id
        """
    ).fetchall()
    assert len(rows) == 3
    for place_id, links_json, metadata_json in rows:
        links = json.loads(links_json)
        assert len(links) >= 1, place_id
        metadata = json.loads(metadata_json)
        assert metadata.get("link_mode") == "inferred"
    conn.close()
