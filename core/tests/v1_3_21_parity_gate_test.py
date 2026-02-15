import json

from core.services.gameplay_service import GameplayService
from core.services.map_runtime_service import MapRuntimeService


SEED = {
    "version": "1.3.21",
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
            "interaction_points": ["terminal-a"],
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
            "interaction_points": ["terminal-b"],
            "npc_spawn": [],
            "metadata": {"chunk": "earth-sur-300-ab"},
        },
    ],
}


def _mk(tmp_path):
    seed_file = tmp_path / "seed.json"
    state_file = tmp_path / "map_runtime_state.json"
    gameplay_state = tmp_path / "gameplay_state.json"
    events_file = tmp_path / "events.ndjson"
    cursor_file = tmp_path / "cursor.json"

    seed_file.write_text(json.dumps(SEED), encoding="utf-8")
    map_service = MapRuntimeService(seed_file=seed_file, state_file=state_file, events_file=events_file)
    gameplay = GameplayService(state_file=gameplay_state, events_file=events_file, cursor_file=cursor_file)
    return map_service, gameplay, events_file


def test_progression_gate_blocked_then_unlocked_from_hethack_events(tmp_path):
    _, gameplay, events_file = _mk(tmp_path)

    assert gameplay.can_proceed() is False

    events_file.write_text(
        "\n".join(
            [
                '{"ts":"2026-02-15T00:00:00Z","source":"toybox:hethack","type":"HETHACK_LEVEL_REACHED","payload":{"depth":32}}',
                '{"ts":"2026-02-15T00:00:01Z","source":"toybox:hethack","type":"HETHACK_AMULET_RETRIEVED","payload":{"line":"You pick up the Amulet of Yendor"}}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    gameplay.tick("alice")

    gate = gameplay.get_gate("dungeon_l32_amulet")
    assert gate and gate.get("completed") is True
    assert gameplay.can_proceed() is True


def test_cross_lens_mission_completion_parity_metrics(tmp_path):
    map_service, gameplay, events_file = _mk(tmp_path)

    assert map_service.complete("alice", "alpha.quest.1")["ok"] is True
    gameplay.tick("alice")

    metrics_after_map = gameplay.get_user_progress("alice")["metrics"]
    map_missions = int(metrics_after_map.get("missions_completed", 0))
    map_xp = gameplay.get_user_stats("alice")["xp"]

    with events_file.open("a", encoding="utf-8") as fh:
        fh.write(
            '{"ts":"2026-02-15T00:00:02Z","source":"toybox:elite","type":"ELITE_MISSION_COMPLETE","payload":{"line":"mission complete"}}\n'
        )

    gameplay.tick("alice")
    metrics_after_elite = gameplay.get_user_progress("alice")["metrics"]
    elite_missions = int(metrics_after_elite.get("missions_completed", 0))
    elite_xp = gameplay.get_user_stats("alice")["xp"]

    assert map_missions >= 1
    assert elite_missions == map_missions + 1
    assert elite_xp > map_xp


def test_calendar_todo_workflow_side_effect_proxy_metric(tmp_path):
    map_service, gameplay, _ = _mk(tmp_path)

    assert map_service.complete("alice", "alpha.quest.1")["ok"] is True
    gameplay.tick("alice")

    metrics = gameplay.get_user_progress("alice")["metrics"]
    # Missions completed is the canonical workflow-side effect proxy consumed by overlays.
    assert int(metrics.get("missions_completed", 0)) >= 1
