"""Direct MCP tool proxies for the Vibe developer uCODE subset.

These are optimized wrappers for high-volume tools:
- health: System health check
- verify: Install and environment verification
- repair: Contributor repair workflows
- help: Command documentation
- config: Config inspection and updates
- run: Developer script execution
- read: Repo and asset inspection
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from vibe.core.tools.base import BaseToolConfig, BaseToolState
from vibe.core.types import ToolStreamEvent
from vibe.core.tools.ucode.data import UcodeConfig_
from vibe.core.tools.ucode.system import UcodeHealth
from vibe.core.tools.ucode.system import UcodeToken
from vibe.core.tools.ucode.system import UcodeHelp
from vibe.core.tools.ucode.system import UcodeVerify
from vibe.core.tools.ucode.system import UcodeRepair
from vibe.core.tools.ucode.workspace import UcodeRun
from vibe.core.tools.ucode.content import UcodeRead

from .ucode_mcp_registry import MCPToolLane, tool_names


def _get_config() -> BaseToolConfig:
    """Get tool configuration."""
    return BaseToolConfig()


def _get_state() -> BaseToolState:
    """Get tool state."""
    return BaseToolState()


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


async def proxy_health(check: Optional[str] = None) -> Dict[str, Any]:
    """Health check proxy."""
    try:
        tool = UcodeHealth(config=_get_config(), state=_get_state())
        result = await _invoke_tool(tool, check=check or "")
        return {
            "status": "success",
            "tool": "health",
            "result": result,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "tool": "health",
        }


async def proxy_token(action: str = "generate", name: Optional[str] = None) -> Dict[str, Any]:
    """Token generation proxy."""
    try:
        tool = UcodeToken(config=_get_config(), state=_get_state())
        result = await _invoke_tool(tool, action=action, name=name or "")
        return {
            "status": "success",
            "tool": "token",
            "result": result,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "tool": "token",
        }


async def proxy_help(
    command: Optional[str] = None,
    topic: Optional[str] = None,
) -> Dict[str, Any]:
    """Help documentation proxy."""
    try:
        tool = UcodeHelp(config=_get_config(), state=_get_state())
        result = await _invoke_tool(tool, command=command or "", topic=topic or "")
        return {
            "status": "success",
            "tool": "help",
            "result": result,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "tool": "help",
        }


async def proxy_verify(target: Optional[str] = None) -> Dict[str, Any]:
    """Verification proxy."""
    try:
        tool = UcodeVerify(config=_get_config(), state=_get_state())
        result = await _invoke_tool(tool, target=target or "")
        return {
            "status": "success",
            "tool": "verify",
            "result": result,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "tool": "verify",
        }


async def proxy_repair(action: Optional[str] = None) -> Dict[str, Any]:
    """Repair proxy."""
    try:
        tool = UcodeRepair(config=_get_config(), state=_get_state())
        result = await _invoke_tool(tool, action=action or "")
        return {
            "status": "success",
            "tool": "repair",
            "result": result,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "tool": "repair",
        }


async def proxy_config(action: str = "show") -> Dict[str, Any]:
    """Config proxy."""
    try:
        tool = UcodeConfig_(config=_get_config(), state=_get_state())
        result = await _invoke_tool(tool, action=action)
        return {
            "status": "success",
            "tool": "config",
            "result": result,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "tool": "config",
        }


async def proxy_run(
    script: str,
    args: Optional[str] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Script execution proxy."""
    try:
        tool = UcodeRun(config=_get_config(), state=_get_state())
        result = await _invoke_tool(
            tool,
            script=script,
            args=args or "",
            dry_run=dry_run,
        )
        return {
            "status": "success",
            "tool": "run",
            "result": result,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "tool": "run",
        }


async def proxy_read(path: str, section: Optional[str] = None) -> Dict[str, Any]:
    """File reading proxy."""
    try:
        tool = UcodeRead(config=_get_config(), state=_get_state())
        result = await _invoke_tool(tool, path=path, section=section or "")
        return {
            "status": "success",
            "tool": "read",
            "result": result,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "tool": "read",
        }


def register_ucode_proxies(mcp_server) -> None:
    """Register high-volume tool proxies with MCP server.

    Args:
        mcp_server: FastMCP server instance.
    """
    @mcp_server.tool()
    def ucode_health(check: Optional[str] = None) -> Dict[str, Any]:
        """Check uDOS system health."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return {"status": "error", "message": "Cannot run async tool in running loop"}
            return loop.run_until_complete(proxy_health(check))
        except RuntimeError:
            return asyncio.run(proxy_health(check))

    @mcp_server.tool()
    def ucode_token(action: str = "generate", name: Optional[str] = None) -> Dict[str, Any]:
        """Generate or validate authentication token."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return {"status": "error", "message": "Cannot run async tool in running loop"}
            return loop.run_until_complete(proxy_token(action, name))
        except RuntimeError:
            return asyncio.run(proxy_token(action, name))

    @mcp_server.tool()
    def ucode_help(command: Optional[str] = None, topic: Optional[str] = None) -> Dict[str, Any]:
        """Get help documentation for uDOS commands."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return {"status": "error", "message": "Cannot run async tool in running loop"}
            return loop.run_until_complete(proxy_help(command, topic))
        except RuntimeError:
            return asyncio.run(proxy_help(command, topic))

    @mcp_server.tool()
    def ucode_verify(target: Optional[str] = None) -> Dict[str, Any]:
        """Verify the local uDOS contributor environment."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return {"status": "error", "message": "Cannot run async tool in running loop"}
            return loop.run_until_complete(proxy_verify(target))
        except RuntimeError:
            return asyncio.run(proxy_verify(target))

    @mcp_server.tool()
    def ucode_repair(action: Optional[str] = None) -> Dict[str, Any]:
        """Repair common contributor environment issues."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return {"status": "error", "message": "Cannot run async tool in running loop"}
            return loop.run_until_complete(proxy_repair(action))
        except RuntimeError:
            return asyncio.run(proxy_repair(action))

    @mcp_server.tool()
    def ucode_config(action: str = "show") -> Dict[str, Any]:
        """Inspect or update contributor-facing uDOS config values."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return {"status": "error", "message": "Cannot run async tool in running loop"}
            return loop.run_until_complete(proxy_config(action))
        except RuntimeError:
            return asyncio.run(proxy_config(action))

    @mcp_server.tool()
    def ucode_run(
        script: str,
        args: Optional[str] = None,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """Execute a contributor script or maintenance command."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return {"status": "error", "message": "Cannot run async tool in running loop"}
            return loop.run_until_complete(proxy_run(script, args, dry_run))
        except RuntimeError:
            return asyncio.run(proxy_run(script, args, dry_run))

    @mcp_server.tool()
    def ucode_read(path: str, section: Optional[str] = None) -> Dict[str, Any]:
        """Read a file from the repo or contributor workspace."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return {"status": "error", "message": "Cannot run async tool in running loop"}
            return loop.run_until_complete(proxy_read(path, section))
        except RuntimeError:
            return asyncio.run(proxy_read(path, section))

    registered_names = {
        "ucode_health",
        "ucode_token",
        "ucode_help",
        "ucode_verify",
        "ucode_repair",
        "ucode_config",
        "ucode_run",
        "ucode_read",
    }
    expected_names = set(tool_names(MCPToolLane.PROXY))
    if registered_names != expected_names:
        raise RuntimeError(
            f"uCODE proxy MCP registry drift: expected {sorted(expected_names)}, got {sorted(registered_names)}"
        )
