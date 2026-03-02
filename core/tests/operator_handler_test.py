from __future__ import annotations

from core.commands.operator_handler import OperatorHandler
from core.tui.dispatcher import CommandDispatcher


def test_operator_handler_delegates_to_ucode_operator(monkeypatch):
    handler = OperatorHandler()

    monkeypatch.setattr(
        handler.ucode_handler,
        "handle",
        lambda command, params, grid=None, parser=None: {
            "status": "success",
            "command": command,
            "params": params,
        },
    )

    result = handler.handle("OPERATOR", ["STATUS"])

    assert result["command"] == "UCODE"
    assert result["params"] == ["OPERATOR", "STATUS"]


def test_dispatcher_supports_top_level_operator_command():
    dispatcher = CommandDispatcher()

    result = dispatcher.dispatch("OPERATOR STATUS")

    assert result["status"] == "success"
    assert result["operator"]["session"]["mode"] == "operator"
    assert "Operator mode:" in result["output"]
