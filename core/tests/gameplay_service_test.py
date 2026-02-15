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
    progress = svc.get_user_progress("alice")
    assert progress["achievement_level"] >= 1
    tokens = {row.get("id") for row in svc.get_user_unlock_tokens("alice")}
    assert "token.toybox.xp_100" in tokens
    assert "token.toybox.achievement_l1" in tokens
    assert "token.toybox.ascension" in tokens


def test_play_option_conditions_and_start(tmp_path):
    state_file = tmp_path / "gameplay_state.json"
    events_file = tmp_path / "events.ndjson"
    cursor_file = tmp_path / "cursor.json"
    svc = GameplayService(state_file=state_file, events_file=events_file, cursor_file=cursor_file)

    blocked = svc.start_play_option("alice", "galaxy")
    assert blocked["status"] == "blocked"
    assert "xp>=100" in blocked["blocked_by"]

    svc.add_user_stat("alice", "xp", 120)
    started = svc.start_play_option("alice", "galaxy")
    assert started["status"] == "success"


def test_rule_if_then_evaluates_against_play_state(tmp_path):
    state_file = tmp_path / "gameplay_state.json"
    events_file = tmp_path / "events.ndjson"
    cursor_file = tmp_path / "cursor.json"
    svc = GameplayService(state_file=state_file, events_file=events_file, cursor_file=cursor_file)

    svc.add_user_stat("alice", "xp", 120)
    svc.set_rule(
        "rule.test.unlock",
        if_expr="xp>=100 and achievement_level>=0",
        then_expr="TOKEN token.rule.test; PLAY galaxy",
        source="test",
    )
    result = svc.run_rules("alice", "rule.test.unlock")
    fired = result.get("fired", [])
    assert len(fired) == 1
    token_ids = {row.get("id") for row in svc.get_user_unlock_tokens("alice")}
    assert "token.rule.test" in token_ids


def test_gameplay_command_is_dispatched():
    dispatcher = CommandDispatcher()

    result = dispatcher.dispatch("GPLAY STATUS")
    assert result["status"] == "success"
    assert "GPLAY STATUS" in result.get("output", "")


def test_play_command_is_dispatched():
    dispatcher = CommandDispatcher()
    result = dispatcher.dispatch("PLAY OPTIONS")
    assert result["status"] == "success"
    assert "PLAY OPTIONS" in result.get("output", "")


def test_rule_command_is_dispatched():
    dispatcher = CommandDispatcher()
    result = dispatcher.dispatch("RULE LIST")
    assert result["status"] == "success"
    assert "RULE LIST" in result.get("output", "")
