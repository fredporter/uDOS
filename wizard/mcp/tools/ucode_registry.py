"""Registry for the Vibe-facing uCODE developer subset.

This module provides:
- discover_ucode_tools(): Find approved BaseTool subclasses in vibe.core.tools.ucode
- get_tool_schema(): Generate MCP-compatible JSON schema for a tool
- list_all_tools(): Get the approved developer tool list with descriptions and schemas
"""

from __future__ import annotations

import importlib
import inspect
import sys
from typing import Any, Dict, Optional, Type

from vibe.core.tools.base import BaseTool


# Only expose the Vibe Dev Mode subset through MCP.
UCODE_MODULES = [
    "vibe.core.tools.ucode.system",
    "vibe.core.tools.ucode.data",
    "vibe.core.tools.ucode.workspace",
    "vibe.core.tools.ucode.content",
]

ALLOWED_UCODE_TOOL_NAMES = frozenset(
    {
        "ucode_health",
        "ucode_verify",
        "ucode_repair",
        "ucode_token",
        "ucode_help",
        "ucode_config",
        "ucode_seed",
        "ucode_setup",
        "ucode_run",
        "ucode_read",
    }
)


def discover_ucode_tools() -> Dict[str, Type[BaseTool]]:
    """Auto-discover the approved developer ucode tools from UCODE_MODULES.

    Returns:
        Dict mapping tool names to tool classes.
    """
    tools: Dict[str, Type[BaseTool]] = {}

    for module_name in UCODE_MODULES:
        try:
            mod = importlib.import_module(module_name)
            for name in dir(mod):
                obj = getattr(mod, name)
                # Check if it's a BaseTool subclass (but not BaseTool itself)
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, BaseTool)
                    and obj is not BaseTool
                ):
                    # Get the tool name from the class
                    tool_name = obj.get_name() if hasattr(obj, "get_name") else name.lower()
                    if tool_name in ALLOWED_UCODE_TOOL_NAMES:
                        tools[tool_name] = obj
        except Exception as e:
            # Non-fatal: skip this module but surface the failure so operators
            # can diagnose missing dependencies or broken tool modules.
            print(
                f"[MCP WARNING] ucode_registry: skipping module '{module_name}' "
                f"({type(e).__name__}: {e})",
                file=sys.stderr,
            )

    return tools


def get_tool_schema(tool_cls: Type[BaseTool]) -> Dict[str, Any]:
    """Generate MCP-compatible JSON schema for a tool.

    Args:
        tool_cls: The tool class to generate schema for.

    Returns:
        JSON schema for the tool's input arguments.
    """
    try:
        # Get the Args model from the tool class
        # Tools typically have Args as a nested Pydantic model
        args_model = tool_cls.__dict__.get("Args")

        if not args_model:
            # Fallback: check if tool has schema() method
            if hasattr(tool_cls, "schema"):
                return tool_cls.schema()
            return {
                "type": "object",
                "properties": {},
                "required": [],
            }

        # Generate schema from Pydantic model
        schema = args_model.model_json_schema()
        return {
            "type": "object",
            "properties": schema.get("properties", {}),
            "required": schema.get("required", []),
        }
    except Exception:
        # Fallback to empty schema
        return {
            "type": "object",
            "properties": {},
            "required": [],
        }


def get_tool_description(tool_cls: Type[BaseTool]) -> str:
    """Get description for a tool.

    Args:
        tool_cls: The tool class.

    Returns:
        Description string.
    """
    # Try to get from class docstring or description attribute
    if hasattr(tool_cls, "description"):
        return tool_cls.description or ""
    return (tool_cls.__doc__ or "").strip().split("\n")[0]


def list_all_tools() -> Dict[str, Dict[str, Any]]:
    """List all Vibe-approved ucode tools with metadata.

    Returns:
        Dict mapping tool names to {"class": Type, "description": str, "schema": Dict}
    """
    tools = discover_ucode_tools()
    result: Dict[str, Dict[str, Any]] = {}

    for tool_name, tool_cls in sorted(tools.items()):
        result[tool_name] = {
            "class": tool_cls,
            "description": get_tool_description(tool_cls),
            "schema": get_tool_schema(tool_cls),
        }

    return result


def get_tool_by_name(name: str) -> Optional[Type[BaseTool]]:
    """Get a tool class by name.

    Args:
        name: Tool name (e.g., "ucode_health", "ucode_run", "ucode_read").

    Returns:
        Tool class, or None if not found.
    """
    tools = discover_ucode_tools()
    return tools.get(name)
