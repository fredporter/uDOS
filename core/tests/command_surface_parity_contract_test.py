"""Parity checks for command surfaces used by core dispatch and prompt UX."""

from __future__ import annotations

import json
import re
from pathlib import Path

from core.input.command_prompt import create_default_registry
from core.services.command_catalog import CANONICAL_UCODE_COMMANDS
from core.tui.dispatcher import CommandDispatcher

_CONTRACT_PATH = Path("core/config/ucode_command_contract_v1_3_20.json")
_PROMPT_ONLY_COMMANDS = frozenset({"EXIT", "OK", "LOGIC"})


def _contract_commands() -> set[str]:
    payload = json.loads(_CONTRACT_PATH.read_text(encoding="utf-8"))
    return set(payload["ucode"]["commands"])


def test_contract_path_version_matches_payload_version() -> None:
    if not (match := re.search(r"_v(\d+)_(\d+)_(\d+)\.json$", _CONTRACT_PATH.name)):
        raise AssertionError(f"Unexpected contract file name: {_CONTRACT_PATH.name}")
    assert ".".join(match.groups()) == json.loads(_CONTRACT_PATH.read_text(encoding="utf-8"))["version"]


def test_contract_and_dispatcher_command_sets_are_identical() -> None:
    dispatcher_commands = set(CommandDispatcher().get_command_list())
    assert _contract_commands() == dispatcher_commands
    assert dispatcher_commands == set(CANONICAL_UCODE_COMMANDS)


def test_prompt_registry_only_adds_explicit_prompt_local_commands() -> None:
    prompt_commands = set(create_default_registry().commands)
    dispatcher_commands = set(CommandDispatcher().get_command_list())
    assert prompt_commands - _PROMPT_ONLY_COMMANDS == dispatcher_commands
    assert "STATUS" in prompt_commands
