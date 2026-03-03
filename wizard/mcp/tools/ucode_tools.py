"""MCP tool handlers for the Vibe-approved uCODE developer subset.

This module provides:
- register_ucode_tools(): Main function to register the developer subset with MCP
- ucode_tool_list(): List all available developer tools
- ucode_tool_call(): Call a tool by name with arguments
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional

from vibe.core.tools.base import BaseToolConfig, BaseToolState
from vibe.core.types import ToolStreamEvent

from .ucode_mcp_registry import MCPToolLane, tool_names
from .ucode_registry import (
    discover_ucode_tools,
    get_tool_by_name,
    list_all_tools,
)


def get_vibe_config() -> BaseToolConfig:
    """Get or create default Vibe tool configuration."""
    try:
        # Try to get from environment/config
        return BaseToolConfig()
    except Exception:
        # Fallback
        return BaseToolConfig()


def _run_async(coro):
    """Run async function in a new event loop if needed."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # We're in an async context, create a task
            import asyncio
            return asyncio.create_task(coro)
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        # No event loop, create one
        return asyncio.run(coro)


async def _invoke_tool(tool, **arguments: Any) -> Dict[str, Any]:
    """Collect the terminal result from a streaming BaseTool invocation."""
    result: Dict[str, Any] | None = None
    async for item in tool.invoke(**arguments):
        if isinstance(item, ToolStreamEvent):
            continue
        if hasattr(item, "model_dump"):
            result = item.model_dump()
        else:
            result = dict(item)
    if result is None:
        raise RuntimeError("Tool returned no terminal result")
    return result


async def ucode_tool_list() -> Dict[str, Any]:
    """List the Vibe-approved ucode developer tools for MCP.

    Returns:
        Dict with list of tools and their metadata.
    """
    tools_meta = list_all_tools()
    tools_list = []

    for tool_name, meta in sorted(tools_meta.items()):
        tools_list.append({
            "name": tool_name,
            "description": meta["description"],
            "input_schema": meta["schema"],
        })

    return {
        "status": "success",
        "count": len(tools_list),
        "tools": tools_list,
    }


async def ucode_tool_call(
    tool_name: str,
    arguments: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Call an approved ucode developer tool by name with arguments.

    Args:
        tool_name: Name of the tool (e.g., "ucode_health", "ucode_run").
        arguments: Input arguments for the tool.

    Returns:
        Result from the tool.
    """
    if arguments is None:
        arguments = {}

    # Find the tool within the approved developer subset.
    tool_cls = get_tool_by_name(tool_name)
    if not tool_cls:
        tools = discover_ucode_tools()
        return {
            "status": "error",
            "message": f"Tool not found: {tool_name}",
            "available_tools": list(sorted(tools.keys())),
        }

    try:
        # Instantiate the tool
        config = get_vibe_config()
        state = BaseToolState()
        tool = tool_cls(config=config, state=state)

        # Call the tool
        result = await _invoke_tool(tool, **arguments)

        return {
            "status": "success",
            "tool": tool_name,
            "result": result,
        }
    except TypeError as e:
        # Invalid arguments
        return {
            "status": "error",
            "message": f"Invalid arguments: {str(e)}",
            "tool": tool_name,
        }
    except Exception as e:
        # Tool execution error
        return {
            "status": "error",
            "message": f"Tool error: {str(e)}",
            "tool": tool_name,
        }


def register_ucode_tools(mcp_server) -> None:
    """Register the approved ucode developer subset with MCP server.

    Args:
        mcp_server: FastMCP server instance.
    """
    @mcp_server.tool()
    def ucode_tools_list() -> Dict[str, Any]:
        """List the Vibe-approved uCODE developer tools."""
        return _run_async(ucode_tool_list())

    @mcp_server.tool()
    def ucode_tools_call(tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Call an approved uCODE developer tool by name with arguments."""
        return _run_async(ucode_tool_call(tool_name, arguments or {}))

    registered_names = {"ucode_tools_list", "ucode_tools_call"}
    expected_names = set(tool_names(MCPToolLane.GENERIC))
    if registered_names != expected_names:
        raise RuntimeError(
            f"uCODE generic MCP registry drift: expected {sorted(expected_names)}, got {sorted(registered_names)}"
        )

    # Also register individual high-volume tools directly for convenience
    # (see ucode_proxies.py for these)
