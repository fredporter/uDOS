"""Registry for the Dev Mode-facing uCODE developer subset."""

from __future__ import annotations

from typing import Any

from core.services.dev_tool_registry import get_dev_tool, list_dev_tools


def discover_ucode_tools() -> dict[str, dict[str, Any]]:
    """Return the approved Dev Mode tools with uDOS-owned metadata."""
    return list_all_tools()


def get_tool_schema(tool_meta: dict[str, Any]) -> dict[str, Any]:
    """Return a tool schema payload."""
    return dict(tool_meta.get("schema") or {"type": "object", "properties": {}})


def get_tool_description(tool_meta: dict[str, Any]) -> str:
    """Return a tool description."""
    return str(tool_meta.get("description") or "")


def list_all_tools() -> dict[str, dict[str, Any]]:
    """List all approved Dev Mode tools with metadata."""
    result: dict[str, dict[str, Any]] = {}
    for tool in list_dev_tools():
        result[tool.name] = {
            "description": tool.description,
            "schema": dict(tool.input_schema),
        }
    return result


def get_tool_by_name(name: str) -> dict[str, Any] | None:
    """Get tool metadata by name."""
    tool = get_dev_tool(name)
    if tool is None:
        return None
    return {
        "name": tool.name,
        "description": tool.description,
        "schema": dict(tool.input_schema),
    }
