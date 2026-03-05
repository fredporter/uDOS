"""uDOS-owned Dev Mode tool registry for MCP and contributor tooling."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


ToolBuilder = Callable[[dict[str, Any]], str]


@dataclass(frozen=True, slots=True)
class DevToolSpec:
    """Canonical Dev Mode tool metadata and command builder."""

    name: str
    description: str
    input_schema: dict[str, Any]
    command_builder: ToolBuilder


def _string_arg(arguments: dict[str, Any], key: str) -> str:
    value = arguments.get(key, "")
    return str(value).strip() if value is not None else ""


def _bool_arg(arguments: dict[str, Any], key: str) -> bool:
    return bool(arguments.get(key, False))


def _join_command(*parts: str) -> str:
    return " ".join(part for part in parts if part).strip()


def _build_health(arguments: dict[str, Any]) -> str:
    return _join_command("HEALTH", _string_arg(arguments, "check"))


def _build_verify(arguments: dict[str, Any]) -> str:
    return _join_command("VERIFY", _string_arg(arguments, "target"))


def _build_repair(arguments: dict[str, Any]) -> str:
    return _join_command("REPAIR", _string_arg(arguments, "action"))


def _build_token(arguments: dict[str, Any]) -> str:
    action = _string_arg(arguments, "action").upper()
    name = _string_arg(arguments, "name")
    if action in {"", "GEN", "GENERATE"}:
        return "TOKEN"
    return _join_command("TOKEN", action, name)


def _build_help(arguments: dict[str, Any]) -> str:
    return _join_command("HELP", _string_arg(arguments, "command") or _string_arg(arguments, "topic"))


def _build_config(arguments: dict[str, Any]) -> str:
    return _join_command("CONFIG", _string_arg(arguments, "action"))


def _build_seed(arguments: dict[str, Any]) -> str:
    return _join_command("SEED", _string_arg(arguments, "action"))


def _build_setup(arguments: dict[str, Any]) -> str:
    return _join_command("SETUP", _string_arg(arguments, "action"))


def _build_run(arguments: dict[str, Any]) -> str:
    script = _string_arg(arguments, "script")
    args = _string_arg(arguments, "args")
    dry_run = "--dry-run" if _bool_arg(arguments, "dry_run") else ""
    return _join_command("RUN", script, args, dry_run)


def _build_read(arguments: dict[str, Any]) -> str:
    return _join_command("READ", _string_arg(arguments, "path"), _string_arg(arguments, "section"))


_STRING_SCHEMA = {"type": "string"}

DEV_TOOL_REGISTRY: dict[str, DevToolSpec] = {
    "ucode_health": DevToolSpec(
        "ucode_health",
        "Check local uDOS health surfaces.",
        {"type": "object", "properties": {"check": _STRING_SCHEMA}},
        _build_health,
    ),
    "ucode_verify": DevToolSpec(
        "ucode_verify",
        "Verify the contributor environment.",
        {"type": "object", "properties": {"target": _STRING_SCHEMA}},
        _build_verify,
    ),
    "ucode_repair": DevToolSpec(
        "ucode_repair",
        "Run contributor repair flows.",
        {"type": "object", "properties": {"action": _STRING_SCHEMA}},
        _build_repair,
    ),
    "ucode_token": DevToolSpec(
        "ucode_token",
        "Generate or inspect local tokens.",
        {"type": "object", "properties": {"action": _STRING_SCHEMA, "name": _STRING_SCHEMA}},
        _build_token,
    ),
    "ucode_help": DevToolSpec(
        "ucode_help",
        "Show command help.",
        {"type": "object", "properties": {"command": _STRING_SCHEMA, "topic": _STRING_SCHEMA}},
        _build_help,
    ),
    "ucode_config": DevToolSpec(
        "ucode_config",
        "Inspect contributor-facing config values.",
        {"type": "object", "properties": {"action": _STRING_SCHEMA}},
        _build_config,
    ),
    "ucode_seed": DevToolSpec(
        "ucode_seed",
        "Trigger seed-related contributor setup.",
        {"type": "object", "properties": {"action": _STRING_SCHEMA}},
        _build_seed,
    ),
    "ucode_setup": DevToolSpec(
        "ucode_setup",
        "Run setup flows from the Dev Mode lane.",
        {"type": "object", "properties": {"action": _STRING_SCHEMA}},
        _build_setup,
    ),
    "ucode_run": DevToolSpec(
        "ucode_run",
        "Run a tracked script or helper.",
        {
            "type": "object",
            "properties": {"script": _STRING_SCHEMA, "args": _STRING_SCHEMA, "dry_run": {"type": "boolean"}},
            "required": ["script"],
        },
        _build_run,
    ),
    "ucode_read": DevToolSpec(
        "ucode_read",
        "Read repo or workspace content through the command layer.",
        {
            "type": "object",
            "properties": {"path": _STRING_SCHEMA, "section": _STRING_SCHEMA},
            "required": ["path"],
        },
        _build_read,
    ),
}


def get_dev_tool(name: str) -> DevToolSpec | None:
    """Return a tool spec by name."""
    return DEV_TOOL_REGISTRY.get(name)


def list_dev_tools() -> list[DevToolSpec]:
    """Return the Dev Mode tool subset in stable order."""
    return [DEV_TOOL_REGISTRY[name] for name in sorted(DEV_TOOL_REGISTRY)]


def build_dev_tool_command(name: str, arguments: dict[str, Any] | None = None) -> str:
    """Build a canonical command for a Dev Mode tool invocation."""
    tool = get_dev_tool(name)
    if tool is None:
        raise KeyError(name)
    return tool.command_builder(arguments or {})
