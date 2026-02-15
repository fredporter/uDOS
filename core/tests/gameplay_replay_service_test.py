import json

from core.services.gameplay_replay_service import GameplayReplayService


def test_replay_is_deterministic_for_same_input(tmp_path):
    events = tmp_path / "events.ndjson"
    initial = tmp_path / "initial_state.json"
    out_state_1 = tmp_path / "out_state_1.json"
    out_state_2 = tmp_path / "out_state_2.json"
    out_report_1 = tmp_path / "out_report_1.json"
    out_report_2 = tmp_path / "out_report_2.json"

    initial.write_text(
        json.dumps(
            {
                "version": 2,
                "users": {
                    "alice": {
                        "stats": {"xp": 0, "hp": 100, "gold": 0},
                        "progress": {"level": 1, "achievement_level": 0, "achievements": [], "location": {"grid_id": "unknown", "x": None, "y": None, "z": 0}, "metrics": {}},
                        "flags": {},
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    rows = [
        {
            "ts": "2026-02-15T00:00:00Z",
            "source": "core:map-runtime",
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
            "source": "core:map-runtime",
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
    ]
    with events.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")

    replay = GameplayReplayService()
    report_1 = replay.replay(
        input_events_file=events,
        output_state_file=out_state_1,
        output_report_file=out_report_1,
        initial_state_file=initial,
    )
    report_2 = replay.replay(
        input_events_file=events,
        output_state_file=out_state_2,
        output_report_file=out_report_2,
        initial_state_file=initial,
    )

    assert report_1["checksum_after"] == report_2["checksum_after"]
    stable_1 = replay._stable_json_obj(json.loads(out_state_1.read_text(encoding="utf-8")))
    stable_2 = replay._stable_json_obj(json.loads(out_state_2.read_text(encoding="utf-8")))
    assert stable_1 == stable_2


def test_replay_reports_unknown_events_without_state_mutation(tmp_path):
    events = tmp_path / "events.ndjson"
    out_state = tmp_path / "out_state.json"
    out_report = tmp_path / "out_report.json"
    rows = [
        {
            "ts": "2026-02-15T00:00:00Z",
            "source": "adapter:test-lane",
            "username": "alice",
            "type": "UNKNOWN_EVENT",
            "payload": {
                "stats_delta": {"xp": 9999, "gold": 9999},
                "progress": {"level": 99, "achievement_id": "unknown.inject"},
            },
        }
    ]
    with events.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")

    report = GameplayReplayService().replay(
        input_events_file=events,
        output_state_file=out_state,
        output_report_file=out_report,
    )
    state = json.loads(out_state.read_text(encoding="utf-8"))
    stats = state["users"]["alice"]["stats"]
    progress = state["users"]["alice"]["progress"]

    assert report["unknown_event_types"] == ["UNKNOWN_EVENT"]
    assert report["unknown_events_changed"] == 0
    assert stats["xp"] == 0
    assert stats["gold"] == 0
    assert "unknown.inject" not in progress["achievements"]
