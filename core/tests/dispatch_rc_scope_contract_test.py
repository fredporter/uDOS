"""Release-candidate scope lock for dispatch syntax and fallback behavior."""

from __future__ import annotations

from core.services.command_dispatch_service import (
    DISPATCH_ROUTE_ORDER,
    SUBCOMMAND_ALIASES,
    CommandDispatchService,
)


def test_rc_route_order_is_locked() -> None:
    assert DISPATCH_ROUTE_ORDER == ("ucode", "shell", "dev_tool")


def test_rc_legacy_command_aliases_are_locked() -> None:
    assert SUBCOMMAND_ALIASES["RESTART"] == "REBOOT"
    assert SUBCOMMAND_ALIASES["SCHEDULE"] == "SCHEDULER"
    assert SUBCOMMAND_ALIASES["TALK"] == "SEND"
    assert SUBCOMMAND_ALIASES["STAT"] == "STATUS"
    assert SUBCOMMAND_ALIASES["STATE"] == "STATUS"
    assert SUBCOMMAND_ALIASES["SEARCH"] == "FIND"


def test_status_is_first_class_command() -> None:
    service = CommandDispatchService()
    stage_1 = service.dispatch("STATUS --compact")
    assert stage_1["stage"] == 1
    assert stage_1["dispatch_to"] == "ucode"
    assert stage_1["command"] == "STATUS"


def test_rc_fallback_order_contract() -> None:
    service = CommandDispatchService()

    stage_1 = service.dispatch("MAP")
    assert stage_1["stage"] == 1
    assert stage_1["dispatch_to"] == "ucode"

    stage_2 = service.dispatch("ls")
    assert stage_2["stage"] == 2
    assert stage_2["dispatch_to"] == "shell"

    stage_3 = service.dispatch("explain this architecture")
    assert stage_3["stage"] == 3
    assert stage_3["dispatch_to"] == "dev_tool"
