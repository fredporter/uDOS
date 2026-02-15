import json

from core.services.gameplay_service import GameplayService
from core.services.map_runtime_service import MapRuntimeService


SEED = {
    "version": "1.3.20",
    "locations": [
        {
            "placeId": "alpha",
            "label": "Alpha",
            "placeRef": "EARTH:SUR:L300-AA10",
            "z": 0,
            "links": ["beta", "gamma", "delta"],
            "portals": [],
            "hazards": ["fog"],
            "quest_ids": ["alpha.quest.1"],
            "interaction_points": ["terminal-a"],
            "npc_spawn": ["guide"],
            "metadata": {"chunk": "earth-sur-300-aa"},
        },
        {
            "placeId": "beta",
            "label": "Beta",
            "placeRef": "EARTH:SUR:L300-AB11",
            "z": 0,
            "links": ["alpha"],
            "portals": [],
            "hazards": [],
            "quest_ids": ["beta.quest.1"],
            "interaction_points": ["console-b"],
            "npc_spawn": [],
            "metadata": {"chunk": "earth-sur-300-ab"},
        },
        {
            "placeId": "gamma",
            "label": "Gamma",
            "placeRef": "EARTH:SUB:L340-AA22-Z-3:D4",
            "z": -3,
            "links": ["alpha"],
            "portals": ["lift-1"],
            "hazards": ["cave-in"],
            "quest_ids": ["gamma.quest.1"],
            "interaction_points": ["relay-core"],
            "npc_spawn": [],
            "metadata": {"chunk": "earth-sub-340-aa"},
        },
        {
            "placeId": "delta",
            "label": "Delta",
            "placeRef": "EARTH:SUB:L341-AB23-Z-3",
            "z": -3,
            "links": ["alpha"],
            "portals": [],
            "hazards": ["cold"],
            "quest_ids": [],
            "interaction_points": [],
            "npc_spawn": [],
            "metadata": {"chunk": "earth-sub-341-ab"},
        },
    ],
}


def _make_services(tmp_path):
    seed_file = tmp_path / "locations-seed.json"
    state_file = tmp_path / "map_runtime_state.json"
    gameplay_state = tmp_path / "gameplay_state.json"
    events_file = tmp_path / "events.ndjson"
    cursor_file = tmp_path / "cursor.json"

    seed_file.write_text(json.dumps(SEED), encoding="utf-8")
    map_service = MapRuntimeService(seed_file=seed_file, state_file=state_file, events_file=events_file)
    gameplay = GameplayService(state_file=gameplay_state, events_file=events_file, cursor_file=cursor_file)
    return map_service, gameplay


def test_map_runtime_status_and_traversal_events(tmp_path):
    map_service, gameplay = _make_services(tmp_path)

    status = map_service.status("alice")
    assert status["ok"] is True
    assert status["current_place_id"] == "alpha"
    assert status["chunk"]["chunk2d_id"] == "earth-sur-300-aa"

    moved = map_service.move("alice", "beta")
    assert moved["ok"] is True
    assert moved["mode"] == "walk"

    gameplay_tick = gameplay.tick("alice")
    assert gameplay_tick["processed"] == 1
    progress = gameplay.get_user_progress("alice")
    assert progress["metrics"]["map_moves"] == 1


def test_map_runtime_vertical_transition_requires_portal_edge(tmp_path):
    map_service, _ = _make_services(tmp_path)

    blocked = map_service.move("alice", "delta")
    assert blocked["ok"] is False
    assert blocked["blocked"] == "portal"

    entered = map_service.enter("alice", "gamma")
    assert entered["ok"] is True


def test_map_runtime_action_flow_updates_gameplay_metrics(tmp_path):
    map_service, gameplay = _make_services(tmp_path)

    assert map_service.inspect("alice")["ok"] is True
    assert map_service.interact("alice", "terminal-a")["ok"] is True
    assert map_service.complete("alice", "alpha.quest.1")["ok"] is True
    assert map_service.tick("alice", 2)["ok"] is True

    tick = gameplay.tick("alice")
    assert tick["processed"] == 4

    stats = gameplay.get_user_stats("alice")
    progress = gameplay.get_user_progress("alice")
    metrics = progress["metrics"]
    assert stats["xp"] >= 30
    assert stats["gold"] >= 11
    assert metrics["map_inspects"] == 1
    assert metrics["map_interactions"] == 1
    assert metrics["map_completions"] == 1
    assert metrics["map_ticks"] == 1
