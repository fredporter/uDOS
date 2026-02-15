import json

from core.services.gameplay_service import GameplayService
from core.services.map_runtime_service import MapRuntimeService
from core.services.world_lens_service import WorldLensService


SEED = {
    "version": "1.3.22",
    "locations": [
        {
            "placeId": "subterra-relay",
            "label": "Subterra Relay",
            "placeRef": "EARTH:SUB:L340-AA22-Z-3:D4",
            "z": -3,
            "links": ["andes-pass"],
            "portals": ["deep-lift-core"],
            "hazards": ["low-oxygen"],
            "quest_ids": ["subterra.bridge.008"],
            "interaction_points": ["relay-core"],
            "npc_spawn": [],
            "metadata": {"chunk": "earth-sub-340-aa"},
        },
        {
            "placeId": "andes-pass",
            "label": "Andes Pass",
            "placeRef": "EARTH:SUR:L302-EP18",
            "z": 3,
            "links": ["subterra-relay"],
            "portals": ["cable-lift-andes-01"],
            "hazards": [],
            "quest_ids": ["ridge.crossing.004"],
            "interaction_points": ["weather-station"],
            "npc_spawn": [],
            "metadata": {"chunk": "earth-sur-302-ep"},
        },
    ],
}


def _mk_lane(tmp_path, lane: str):
    root = tmp_path / lane
    root.mkdir(parents=True, exist_ok=True)
    seed_file = root / "seed.json"
    map_state = root / "map_state.json"
    gameplay_state = root / "gameplay_state.json"
    events_file = root / "events.ndjson"
    cursor_file = root / "cursor.json"
    lens_config = root / "lens.json"
    lens_state = root / "lens_state.json"

    seed_file.write_text(json.dumps(SEED), encoding="utf-8")
    lens_config.write_text(
        json.dumps(
            {
                "version": "1.3.22",
                "feature_flag": {"env_var": "UDOS_3D_WORLD_LENS_ENABLED", "default_enabled": True},
                "single_region": {
                    "id": "earth_subterra_slice",
                    "entry_place_id": "subterra-relay",
                    "allowed_place_ids": ["subterra-relay", "andes-pass"],
                    "anchor_prefix": "EARTH:",
                },
            }
        ),
        encoding="utf-8",
    )

    map_service = MapRuntimeService(seed_file=seed_file, state_file=map_state, events_file=events_file)
    gameplay = GameplayService(state_file=gameplay_state, events_file=events_file, cursor_file=cursor_file)
    lens = WorldLensService(config_file=lens_config, state_file=lens_state, seed_file=seed_file)
    lens.set_enabled(True, actor="test")
    return map_service, gameplay, lens, events_file


def _snapshot(gameplay: GameplayService, username: str = "alice"):
    stats = gameplay.get_user_stats(username)
    progress = gameplay.get_user_progress(username)
    metrics = progress.get("metrics", {})
    achievements = set(progress.get("achievements", []))
    return {
        "xp": int(stats.get("xp", 0)),
        "gold": int(stats.get("gold", 0)),
        "map_enters": int(metrics.get("map_enters", 0)),
        "map_inspects": int(metrics.get("map_inspects", 0)),
        "map_interactions": int(metrics.get("map_interactions", 0)),
        "map_completions": int(metrics.get("map_completions", 0)),
        "missions_completed": int(metrics.get("missions_completed", 0)),
        "achievements": achievements,
    }


def test_v1_3_22_same_place_quest_event_flow_matches_2d_and_adapter_lenses(tmp_path):
    map_2d, gameplay_2d, lens_2d, _ = _mk_lane(tmp_path, "map_lane")
    assert map_2d.enter("alice", "subterra-relay")["ok"] is True
    assert map_2d.inspect("alice")["ok"] is True
    assert map_2d.interact("alice", "relay-core")["ok"] is True
    assert map_2d.complete("alice", "subterra.bridge.008")["ok"] is True
    gameplay_2d.tick("alice")
    map_status = map_2d.status("alice")
    lens_status = lens_2d.status(username="alice", map_status=map_status, progression_ready=True)
    assert lens_status["lens"]["ready"] is True
    two_d = _snapshot(gameplay_2d)

    _, gameplay_3d, lens_3d, events = _mk_lane(tmp_path, "adapter_lane")
    adapter_events = [
        {
            "ts": "2026-02-15T00:00:00Z",
            "source": "adapter:crawler3d-sim",
            "username": "alice",
            "type": "MAP_ENTER",
            "payload": {
                "action": "ENTER",
                "place_id": "subterra-relay",
                "place_ref": "EARTH:SUB:L340-AA22-Z-3:D4",
                "chunk2d_id": "earth-sub-340-aa",
                "location": {"grid_id": "EARTH:SUB:L340-AA22-Z-3:D4", "x": None, "y": None, "z": -3},
            },
        },
        {
            "ts": "2026-02-15T00:00:01Z",
            "source": "adapter:crawler3d-sim",
            "username": "alice",
            "type": "MAP_INSPECT",
            "payload": {
                "action": "INSPECT",
                "place_id": "subterra-relay",
                "place_ref": "EARTH:SUB:L340-AA22-Z-3:D4",
                "location": {"grid_id": "EARTH:SUB:L340-AA22-Z-3:D4", "x": None, "y": None, "z": -3},
            },
        },
        {
            "ts": "2026-02-15T00:00:02Z",
            "source": "adapter:crawler3d-sim",
            "username": "alice",
            "type": "MAP_INTERACT",
            "payload": {
                "action": "INTERACT",
                "place_id": "subterra-relay",
                "place_ref": "EARTH:SUB:L340-AA22-Z-3:D4",
                "interaction_id": "relay-core",
                "location": {"grid_id": "EARTH:SUB:L340-AA22-Z-3:D4", "x": None, "y": None, "z": -3},
            },
        },
        {
            "ts": "2026-02-15T00:00:03Z",
            "source": "adapter:crawler3d-sim",
            "username": "alice",
            "type": "MAP_COMPLETE",
            "payload": {
                "action": "COMPLETE",
                "place_id": "subterra-relay",
                "place_ref": "EARTH:SUB:L340-AA22-Z-3:D4",
                "objective_id": "subterra.bridge.008",
                "location": {"grid_id": "EARTH:SUB:L340-AA22-Z-3:D4", "x": None, "y": None, "z": -3},
            },
        },
    ]
    with events.open("a", encoding="utf-8") as fh:
        for row in adapter_events:
            fh.write(json.dumps(row) + "\n")
    gameplay_3d.tick("alice")
    lens_status_3d = lens_3d.status(
        username="alice",
        map_status={
            "ok": True,
            "current_place_id": "subterra-relay",
            "place_ref": "EARTH:SUB:L340-AA22-Z-3:D4",
        },
        progression_ready=True,
    )
    assert lens_status_3d["lens"]["ready"] is True
    adapter = _snapshot(gameplay_3d)

    for key in ("xp", "gold", "map_enters", "map_inspects", "map_interactions", "map_completions", "missions_completed"):
        assert adapter[key] == two_d[key]
    assert "map.subterra.bridge.008" in two_d["achievements"]
    assert "map.subterra.bridge.008" in adapter["achievements"]


def test_v1_3_22_adapter_payload_cannot_override_system_of_record_fields(tmp_path):
    _, gameplay, _, events = _mk_lane(tmp_path, "ownership_guard")
    with events.open("a", encoding="utf-8") as fh:
        fh.write(
            json.dumps(
                {
                    "ts": "2026-02-15T00:10:00Z",
                    "source": "adapter:crawler3d-sim",
                    "username": "alice",
                    "type": "MAP_ENTER",
                    "payload": {
                        "action": "ENTER",
                        "place_id": "subterra-relay",
                        "place_ref": "EARTH:SUB:L340-AA22-Z-3:D4",
                        "chunk2d_id": "earth-sub-340-aa",
                        "location": {"grid_id": "EARTH:SUB:L340-AA22-Z-3:D4", "x": None, "y": None, "z": -3},
                        "stats_delta": {"xp": 9999, "gold": 9999},
                        "progress": {"level": 99, "achievement_id": "adapter.owned"},
                        "permissions": {"admin": {"gameplay.gate_admin": True}},
                        "gates": {"dungeon_l32_amulet": {"completed": True}},
                    },
                }
            )
            + "\n"
        )
    result = gameplay.tick("alice")
    stats = gameplay.get_user_stats("alice")
    progress = gameplay.get_user_progress("alice")
    gates = gameplay.list_gates()

    assert result["processed"] == 1
    assert stats["xp"] == 1  # MAP_ENTER reward only; injected stats_delta ignored.
    assert stats["gold"] == 0
    assert "adapter.owned" not in set(progress.get("achievements", []))
    assert gates["dungeon_l32_amulet"]["completed"] is False
