import json

from core.tui.dispatcher import CommandDispatcher


def test_health_check_release_gates_json_surface():
    dispatcher = CommandDispatcher()
    result = dispatcher.dispatch("HEALTH CHECK release-gates --format json")
    assert result["status"] in {"success", "warning"}
    payload = json.loads(result["output"])
    assert payload["milestone"] == "v1.3.23"
    summary = payload["summary"]
    for key in ("total", "pass", "fail", "error", "pending", "blocker_open", "contract_drift"):
        assert key in summary


def test_health_check_release_gates_text_surface():
    dispatcher = CommandDispatcher()
    result = dispatcher.dispatch("HEALTH CHECK release-gates")
    assert result["status"] in {"success", "warning"}
    assert "HEALTH CHECK release-gates" in result.get("output", "")
