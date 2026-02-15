from core.services.gameplay_service import GameplayService
from core.tui.dispatcher import CommandDispatcher


def test_gameplay_service_stats_and_gate(tmp_path):
    state_file = tmp_path / "gameplay_state.json"
    events_file = tmp_path / "events.ndjson"
    cursor_file = tmp_path / "cursor.json"
    svc = GameplayService(state_file=state_file, events_file=events_file, cursor_file=cursor_file)

    stats = svc.get_user_stats("alice")
    assert stats == {"xp": 0, "hp": 100, "gold": 0}

    stats = svc.add_user_stat("alice", "xp", 25)
    assert stats["xp"] == 25

    assert svc.can_proceed() is False
    gate = svc.complete_gate("dungeon_l32_amulet", source="test")
    assert gate["completed"] is True
    assert svc.can_proceed() is True


def test_gameplay_tick_auto_gate_from_events(tmp_path):
    state_file = tmp_path / "gameplay_state.json"
    events_file = tmp_path / "events.ndjson"
    cursor_file = tmp_path / "cursor.json"
    svc = GameplayService(state_file=state_file, events_file=events_file, cursor_file=cursor_file)

    events_file.write_text(
        "\n".join(
            [
                '{"ts":"2026-02-15T00:00:00Z","source":"toybox:hethack","type":"HETHACK_LEVEL_REACHED","payload":{"depth":32}}',
                '{"ts":"2026-02-15T00:00:01Z","source":"toybox:hethack","type":"HETHACK_AMULET_RETRIEVED","payload":{"line":"You pick up the Amulet of Yendor"}}',
            ]
        )
        + "\n"
    )

    tick = svc.tick("alice")
    assert tick["processed"] == 2
    assert svc.can_proceed() is True
    stats = svc.get_user_stats("alice")
    assert stats["xp"] >= 510
    assert stats["gold"] >= 1000


def test_gameplay_command_is_dispatched():
    dispatcher = CommandDispatcher()

    result = dispatcher.dispatch("GAMEPLAY STATUS")
    assert result["status"] == "success"
    assert "GAMEPLAY STATUS" in result.get("output", "")
