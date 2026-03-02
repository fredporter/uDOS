from __future__ import annotations

from types import SimpleNamespace

from core.tui.ucode import UCODE


def _make_ucode_stub() -> UCODE:
    instance = UCODE.__new__(UCODE)
    instance.prompt = None
    instance.state = None
    instance.dispatcher = SimpleNamespace(
        dispatch=lambda command, parser=None, game_state=None: {
            "status": "success",
            "command": command,
        }
    )
    instance._get_dev_mode_primary_provider = lambda: "local"
    return instance


def test_ok_route_alias_maps_to_operator_in_standard_runtime():
    ucode = _make_ucode_stub()
    ucode._dev_mode_active = lambda: False
    ucode._route_to_operator = lambda prompt: {
        "status": "operator_plan",
        "prompt": prompt,
    }

    result = ucode._handle_ok_prefix("OK ROUTE show scheduler logs")

    assert result["status"] == "operator_plan"
    assert result["prompt"] == "show scheduler logs"


def test_ok_explain_is_dev_only_in_standard_runtime():
    ucode = _make_ucode_stub()
    ucode._dev_mode_active = lambda: False
    ucode._legacy_dev_only_response = lambda text: {
        "status": "warning",
        "message": text,
    }

    result = ucode._handle_ok_prefix("OK EXPLAIN core/tui/ucode.py")

    assert result["status"] == "warning"
    assert result["message"] == "OK EXPLAIN"


def test_operator_prefix_routes_to_ucode_operator_surface():
    ucode = _make_ucode_stub()

    result = ucode._handle_operator_prefix("OPERATOR STATUS")

    assert result["status"] == "success"
    assert result["command"] == "UCODE OPERATOR STATUS"
