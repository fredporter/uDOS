from core.services.gameplay_service import GameplayService
from core.services.user_service import UserManager, UserRole
from core.tui.dispatcher import CommandDispatcher


def _setup_isolated_runtime(monkeypatch, tmp_path):
    import core.services.gameplay_service as gameplay_mod
    import core.services.user_service as user_mod

    user_mgr = UserManager(state_dir=tmp_path / "users")
    if "admin" not in user_mgr.users:
        user_mgr.create_user("admin", UserRole.ADMIN)
    if "user" not in user_mgr.users:
        user_mgr.create_user("user", UserRole.USER)
    if "guest" not in user_mgr.users:
        user_mgr.create_user("guest", UserRole.GUEST)
    user_mgr.switch_user("admin")
    monkeypatch.setattr(user_mod, "_user_manager", user_mgr)

    gameplay = GameplayService(
        state_file=tmp_path / "gameplay_state.json",
        events_file=tmp_path / "events.ndjson",
        cursor_file=tmp_path / "cursor.json",
    )
    monkeypatch.setattr(gameplay_mod, "_gameplay_service", gameplay)
    return user_mgr


def test_command_capability_matrix_denials_and_negative_paths(monkeypatch, tmp_path):
    user_mgr = _setup_isolated_runtime(monkeypatch, tmp_path)
    dispatcher = CommandDispatcher()

    user_mgr.switch_user("guest")
    denied_stats = dispatcher.dispatch("PLAY STATS ADD xp 1")
    assert denied_stats["status"] == "error"
    assert denied_stats["message"] == "Permission denied: gameplay.mutate"

    denied_rule = dispatcher.dispatch("RULE ADD r1 IF xp>=1 THEN TOKEN token.r1")
    assert denied_rule["status"] == "error"
    assert denied_rule["message"] == "Permission denied: gameplay.rule_admin"

    user_mgr.switch_user("user")
    denied_toybox = dispatcher.dispatch("PLAY TOYBOX SET elite")
    assert denied_toybox["status"] == "error"
    assert denied_toybox["message"] == "Permission denied: toybox.admin"

    user_mgr.switch_user("admin")
    blocked_play = dispatcher.dispatch("PLAY START galaxy")
    assert blocked_play["status"] == "blocked"
    assert "xp>=100" in ",".join(blocked_play.get("blocked_by", []))

    bad_rule_syntax = dispatcher.dispatch("RULE ADD r2 IF xp>=1")
    assert bad_rule_syntax["status"] == "error"
    assert bad_rule_syntax["message"] == "Syntax: RULE ADD <rule_id> IF <condition> THEN <actions>"

    bad_play_syntax = dispatcher.dispatch("PLAY START")
    assert bad_play_syntax["status"] == "error"
    assert bad_play_syntax["message"] == "Syntax: PLAY START <option_id>"

    bad_lens_syntax = dispatcher.dispatch("PLAY LENS nonsense")
    assert bad_lens_syntax["status"] == "error"
    assert bad_lens_syntax["message"] == "Syntax: PLAY LENS <STATUS|ENABLE|DISABLE>"

    unknown_play_subcommand = dispatcher.dispatch("PLAY BOGUS")
    assert unknown_play_subcommand["status"] == "error"
    assert unknown_play_subcommand["message"] == "Unknown PLAY subcommand: bogus"
