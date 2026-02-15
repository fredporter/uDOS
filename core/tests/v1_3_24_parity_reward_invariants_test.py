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
            "links": ["beta"],
            "portals": [],
            "hazards": [],
            "quest_ids": ["alpha.quest.1"],
            "interaction_points": [],
            "npc_spawn": [],
            "metadata": {"chunk": "earth-sur-300-aa"},
        },
        {
            "placeId": "beta",
            "label": "Beta",
            "placeRef": "EARTH:SUR:L300-AB10",
            "z": 0,
            "links": ["alpha"],
            "portals": [],
            "hazards": [],
            "quest_ids": ["beta.quest.1"],
            "interaction_points": [],
            "npc_spawn": [],
            "metadata": {"chunk": "earth-sur-300-ab"},
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
    seed_file.write_text(json.dumps(SEED), encoding="utf-8")
    map_service = MapRuntimeService(seed_file=seed_file, state_file=map_state, events_file=events_file)
    gameplay = GameplayService(state_file=gameplay_state, events_file=events_file, cursor_file=cursor_file)
    return map_service, gameplay, events_file


def _snapshot(gameplay: GameplayService, username: str = "alice"):
    stats = gameplay.get_user_stats(username)
    progress = gameplay.get_user_progress(username)
    metrics = progress.get("metrics", {})
    return {
        "xp": int(stats.get("xp", 0)),
        "gold": int(stats.get("gold", 0)),
        "map_moves": int(metrics.get("map_moves", 0)),
        "map_completions": int(metrics.get("map_completions", 0)),
        "missions_completed": int(metrics.get("missions_completed", 0)),
        "achievements": sorted(progress.get("achievements", [])),
    }


def test_v1_3_24_quest_chain_state_and_reward_invariants_between_lenses(tmp_path):
    map_2d, gameplay_2d, _ = _mk_lane(tmp_path, "map_lane")
    assert map_2d.enter("alice", "alpha")["ok"] is True
    assert map_2d.complete("alice", "alpha.quest.1")["ok"] is True
    assert map_2d.move("alice", "beta")["ok"] is True
    assert map_2d.complete("alice", "beta.quest.1")["ok"] is True
    gameplay_2d.tick("alice")
    two_d = _snapshot(gameplay_2d)

    _, gameplay_3d, events = _mk_lane(tmp_path, "adapter_lane")
    adapter_events = [
        {
            "ts": "2026-02-15T00:00:00Z",
            "source": "adapter:roundb-sim",
            "username": "alice",
            "type": "MAP_ENTER",
            "payload": {
                "action": "ENTER",
                "place_id": "alpha",
                "place_ref": "EARTH:SUR:L300-AA10",
                "chunk2d_id": "earth-sur-300-aa",
                "location": {"grid_id": "EARTH:SUR:L300-AA10", "x": None, "y": None, "z": 0},
            },
        },
        {
            "ts": "2026-02-15T00:00:01Z",
            "source": "adapter:roundb-sim",
            "username": "alice",
            "type": "MAP_COMPLETE",
            "payload": {
                "action": "COMPLETE",
                "place_id": "alpha",
                "place_ref": "EARTH:SUR:L300-AA10",
                "objective_id": "alpha.quest.1",
                "location": {"grid_id": "EARTH:SUR:L300-AA10", "x": None, "y": None, "z": 0},
            },
        },
        {
            "ts": "2026-02-15T00:00:02Z",
            "source": "adapter:roundb-sim",
            "username": "alice",
            "type": "MAP_TRAVERSE",
            "payload": {
                "action": "ENTER",
                "from_place_id": "alpha",
                "to_place_id": "beta",
                "to_place_ref": "EARTH:SUR:L300-AB10",
                "terrain_cost": 1,
                "mode": "walk",
                "chunk2d_id": "earth-sur-300-ab",
                "location": {"grid_id": "EARTH:SUR:L300-AB10", "x": None, "y": None, "z": 0},
            },
        },
        {
            "ts": "2026-02-15T00:00:03Z",
            "source": "adapter:roundb-sim",
            "username": "alice",
            "type": "MAP_COMPLETE",
            "payload": {
                "action": "COMPLETE",
                "place_id": "beta",
                "place_ref": "EARTH:SUR:L300-AB10",
                "objective_id": "beta.quest.1",
                "location": {"grid_id": "EARTH:SUR:L300-AB10", "x": None, "y": None, "z": 0},
            },
        },
    ]
    with events.open("a", encoding="utf-8") as fh:
        for row in adapter_events:
            fh.write(json.dumps(row) + "\n")
    gameplay_3d.tick("alice")
    adapter = _snapshot(gameplay_3d)

    for key in ("xp", "gold", "map_moves", "map_completions", "missions_completed"):
        assert adapter[key] == two_d[key], f"parity mismatch on {key}"

    assert adapter["achievements"] == two_d["achievements"]
    assert "map.alpha.quest.1" in adapter["achievements"]
    assert "map.beta.quest.1" in adapter["achievements"]
