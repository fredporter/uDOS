import json

from core.services.gameplay_service import GameplayService
from core.services.map_runtime_service import MapRuntimeService


SEED = {
    "version": "1.3.24",
    "locations": [
        {
            "placeId": "alpha",
            "label": "Alpha",
            "placeRef": "EARTH:SUR:L300-AA10",
            "z": 0,
            "links": [],
            "portals": [],
            "hazards": [],
            "quest_ids": [],
            "interaction_points": [],
            "npc_spawn": [],
            "metadata": {"chunk": "earth-sur-300-aa"},
        }
    ],
}


def test_gameplay_state_migration_smoke_merges_defaults_without_losing_legacy_values(tmp_path):
    state_file = tmp_path / "gameplay_state.json"
    events_file = tmp_path / "events.ndjson"
    cursor_file = tmp_path / "cursor.json"

    legacy_state = {
        "version": 1,
        "users": {
            "alice": {
                "stats": {"xp": 77, "hp": 88, "gold": 99},
                "progress": {"level": 3, "achievements": ["legacy.badge"]},
            }
        },
        "gates": {"legacy_gate": {"title": "Legacy Gate", "completed": True}},
        "toybox": {"active_profile": "elite"},
    }
    state_file.write_text(json.dumps(legacy_state), encoding="utf-8")

    svc = GameplayService(state_file=state_file, events_file=events_file, cursor_file=cursor_file)
    snapshot = svc.snapshot("alice", "user")
    stats = snapshot["stats"]
    progress = snapshot["progress"]

    assert stats == {"xp": 77, "hp": 88, "gold": 99}
    assert progress["level"] == 3
    assert "legacy.badge" in progress["achievements"]
    assert "metrics" in progress
    assert "map_completions" in progress["metrics"]
    assert snapshot["toybox"]["active_profile"] == "elite"
    assert "legacy_gate" in snapshot["gates"]


def test_map_runtime_state_migration_smoke_fills_missing_user_fields(tmp_path):
    seed_file = tmp_path / "seed.json"
    state_file = tmp_path / "map_runtime_state.json"
    events_file = tmp_path / "events.ndjson"
    seed_file.write_text(json.dumps(SEED), encoding="utf-8")

    legacy_state = {
        "version": 0,
        "users": {"alice": {"current_place_id": "alpha"}},
    }
    state_file.write_text(json.dumps(legacy_state), encoding="utf-8")

    svc = MapRuntimeService(seed_file=seed_file, state_file=state_file, events_file=events_file)
    status = svc.status("alice")

    assert status["ok"] is True
    assert status["current_place_id"] == "alpha"
    assert status["tick_counter"] == 0
    assert status["npc_phase"] == 0
    assert status["world_phase"] == 0

