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


def test_ok_prefix_handler_removed_in_v1_5_surface():
    ucode = _make_ucode_stub()
    assert not hasattr(ucode, "_handle_ok_prefix")


def test_operator_prefix_routes_to_ucode_operator_surface():
    ucode = _make_ucode_stub()

    result = ucode._handle_operator_prefix("OPERATOR STATUS")

    assert result["status"] == "success"
    assert result["command"] == "UCODE OPERATOR STATUS"
