"""MCP tool handlers for the uDOS-owned Dev Mode tool subset."""

from __future__ import annotations

from typing import Any, Optional

from core.services.dev_tool_registry import build_dev_tool_command
from wizard.mcp.gateway import WizardGateway
from wizard.services.dev_extension_service import get_dev_extension_service

from .ucode_mcp_registry import MCPToolLane, tool_names
from .ucode_registry import get_tool_by_name, list_all_tools


def _dev_tool_error() -> Optional[str]:
    return get_dev_extension_service().ensure_vibe_tool_access()


def _dispatch_dev_tool(
    tool_name: str, arguments: Optional[dict[str, Any]] = None
) -> dict[str, Any]:
    """Build and dispatch a canonical ucode command for a Dev Mode tool."""
    if error := _dev_tool_error():
        return {"status": "error", "message": error, "tool": tool_name}

    try:
        command = build_dev_tool_command(tool_name, arguments or {})
    except KeyError:
        return {"status": "error", "message": f"Tool not found: {tool_name}", "tool": tool_name}

    client = WizardGateway()
    payload = client.ucode_dispatch(command)
    return {
        "status": "success",
        "tool": tool_name,
        "command": command,
        "result": payload.get("result", payload),
        "routing_contract": payload.get("routing_contract"),
    }


def ucode_tool_list() -> dict[str, Any]:
    """List the approved uDOS Dev Mode tools for MCP."""
    if error := _dev_tool_error():
        return {"status": "error", "message": error, "count": 0, "tools": []}

    tools_list = []
    for tool_name, meta in sorted(list_all_tools().items()):
        tools_list.append(
            {
                "name": tool_name,
                "description": meta["description"],
                "input_schema": meta["schema"],
            }
        )

    return {"status": "success", "count": len(tools_list), "tools": tools_list}


def ucode_tool_call(
    tool_name: str, arguments: Optional[dict[str, Any]] = None
) -> dict[str, Any]:
    """Call an approved uDOS Dev Mode tool by name with arguments."""
    if arguments is None:
        arguments = {}

    if error := _dev_tool_error():
        return {"status": "error", "message": error, "tool": tool_name}

    if get_tool_by_name(tool_name) is None:
        return {
            "status": "error",
            "message": f"Tool not found: {tool_name}",
            "available_tools": list(sorted(list_all_tools().keys())),
        }

    return _dispatch_dev_tool(tool_name, arguments)


def register_ucode_tools(mcp_server) -> None:
    """Register the approved Dev Mode subset with the MCP server."""

    @mcp_server.tool()
    def ucode_tools_list() -> dict[str, Any]:
        """List the approved uDOS Dev Mode tools."""
        return ucode_tool_list()

    @mcp_server.tool()
    def ucode_tools_call(
        tool_name: str, arguments: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Call an approved uDOS Dev Mode tool by name with arguments."""
        return ucode_tool_call(tool_name, arguments or {})

    registered_names = {"ucode_tools_list", "ucode_tools_call"}
    expected_names = set(tool_names(MCPToolLane.GENERIC))
    if registered_names != expected_names:
        raise RuntimeError(
            f"uCODE generic MCP registry drift: expected {sorted(expected_names)}, got {sorted(registered_names)}"
        )
