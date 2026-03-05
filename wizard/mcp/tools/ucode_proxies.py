"""Direct MCP tool proxies for the uDOS-owned Dev Mode tool subset."""

from __future__ import annotations

from typing import Any, Optional

from .ucode_mcp_registry import MCPToolLane, tool_names
from .ucode_tools import ucode_tool_call


def proxy_health(check: Optional[str] = None) -> dict[str, Any]:
    return ucode_tool_call("ucode_health", {"check": check or ""})


def proxy_token(action: str = "generate", name: Optional[str] = None) -> dict[str, Any]:
    return ucode_tool_call("ucode_token", {"action": action, "name": name or ""})


def proxy_help(
    command: Optional[str] = None, topic: Optional[str] = None
) -> dict[str, Any]:
    return ucode_tool_call(
        "ucode_help", {"command": command or "", "topic": topic or ""}
    )


def proxy_verify(target: Optional[str] = None) -> dict[str, Any]:
    return ucode_tool_call("ucode_verify", {"target": target or ""})


def proxy_repair(action: Optional[str] = None) -> dict[str, Any]:
    return ucode_tool_call("ucode_repair", {"action": action or ""})


def proxy_config(action: str = "show") -> dict[str, Any]:
    return ucode_tool_call("ucode_config", {"action": action})


def proxy_run(
    script: str, args: Optional[str] = None, dry_run: bool = False
) -> dict[str, Any]:
    return ucode_tool_call(
        "ucode_run", {"script": script, "args": args or "", "dry_run": dry_run}
    )


def proxy_read(path: str, section: Optional[str] = None) -> dict[str, Any]:
    return ucode_tool_call("ucode_read", {"path": path, "section": section or ""})


def register_ucode_proxies(mcp_server) -> None:
    """Register high-volume direct proxies with the MCP server."""

    @mcp_server.tool()
    def ucode_health(check: Optional[str] = None) -> dict[str, Any]:
        """Check uDOS system health."""
        return proxy_health(check)

    @mcp_server.tool()
    def ucode_token(
        action: str = "generate", name: Optional[str] = None
    ) -> dict[str, Any]:
        """Generate or validate authentication token."""
        return proxy_token(action, name)

    @mcp_server.tool()
    def ucode_help(
        command: Optional[str] = None, topic: Optional[str] = None
    ) -> dict[str, Any]:
        """Get help documentation for uDOS commands."""
        return proxy_help(command, topic)

    @mcp_server.tool()
    def ucode_verify(target: Optional[str] = None) -> dict[str, Any]:
        """Verify the local uDOS contributor environment."""
        return proxy_verify(target)

    @mcp_server.tool()
    def ucode_repair(action: Optional[str] = None) -> dict[str, Any]:
        """Repair common contributor environment issues."""
        return proxy_repair(action)

    @mcp_server.tool()
    def ucode_config(action: str = "show") -> dict[str, Any]:
        """Inspect or update contributor-facing uDOS config values."""
        return proxy_config(action)

    @mcp_server.tool()
    def ucode_run(
        script: str, args: Optional[str] = None, dry_run: bool = False
    ) -> dict[str, Any]:
        """Run a contributor script."""
        return proxy_run(script, args, dry_run)

    @mcp_server.tool()
    def ucode_read(path: str, section: Optional[str] = None) -> dict[str, Any]:
        """Read contributor docs, code, or assets."""
        return proxy_read(path, section)

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
