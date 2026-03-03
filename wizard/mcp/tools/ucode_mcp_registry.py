"""Canonical MCP tool registry for the Vibe uCODE developer lanes."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum


class MCPToolLane(StrEnum):
    """Ownership lane for MCP tool registration."""

    GENERIC = "generic"
    PROXY = "proxy"


@dataclass(frozen=True, slots=True)
class MCPToolEntry:
    """Canonical MCP tool registration contract entry."""

    name: str
    lane: MCPToolLane
    owner_module: str
    rationale: str


UCODE_MCP_TOOL_REGISTRY: tuple[MCPToolEntry, ...] = (
    MCPToolEntry(
        name="ucode_tools_list",
        lane=MCPToolLane.GENERIC,
        owner_module="wizard.mcp.tools.ucode_tools",
        rationale="Developer lane: list the approved uCODE subset exposed to Vibe.",
    ),
    MCPToolEntry(
        name="ucode_tools_call",
        lane=MCPToolLane.GENERIC,
        owner_module="wizard.mcp.tools.ucode_tools",
        rationale="Developer lane: generic invocation for the approved uCODE subset.",
    ),
    MCPToolEntry(
        name="ucode_health",
        lane=MCPToolLane.PROXY,
        owner_module="wizard.mcp.tools.ucode_proxies",
        rationale="Latency/ergonomics path: direct proxy for high-volume health checks.",
    ),
    MCPToolEntry(
        name="ucode_token",
        lane=MCPToolLane.PROXY,
        owner_module="wizard.mcp.tools.ucode_proxies",
        rationale="Latency/ergonomics path: direct proxy for auth/token flows.",
    ),
    MCPToolEntry(
        name="ucode_help",
        lane=MCPToolLane.PROXY,
        owner_module="wizard.mcp.tools.ucode_proxies",
        rationale="Latency/ergonomics path: direct proxy for command help.",
    ),
    MCPToolEntry(
        name="ucode_verify",
        lane=MCPToolLane.PROXY,
        owner_module="wizard.mcp.tools.ucode_proxies",
        rationale="Latency/ergonomics path: direct proxy for installation verification.",
    ),
    MCPToolEntry(
        name="ucode_repair",
        lane=MCPToolLane.PROXY,
        owner_module="wizard.mcp.tools.ucode_proxies",
        rationale="Latency/ergonomics path: direct proxy for contributor repair flows.",
    ),
    MCPToolEntry(
        name="ucode_config",
        lane=MCPToolLane.PROXY,
        owner_module="wizard.mcp.tools.ucode_proxies",
        rationale="Latency/ergonomics path: direct proxy for developer config inspection.",
    ),
    MCPToolEntry(
        name="ucode_run",
        lane=MCPToolLane.PROXY,
        owner_module="wizard.mcp.tools.ucode_proxies",
        rationale="Latency/ergonomics path: direct proxy for developer script workflows.",
    ),
    MCPToolEntry(
        name="ucode_read",
        lane=MCPToolLane.PROXY,
        owner_module="wizard.mcp.tools.ucode_proxies",
        rationale="Latency/ergonomics path: direct proxy for repo and asset inspection.",
    ),
)


def tool_names(lane: MCPToolLane | None = None) -> tuple[str, ...]:
    """Return canonical tool names, optionally filtered by ownership lane."""
    if lane is None:
        return tuple(entry.name for entry in UCODE_MCP_TOOL_REGISTRY)
    return tuple(entry.name for entry in UCODE_MCP_TOOL_REGISTRY if entry.lane == lane)


def tool_registry_records() -> list[dict[str, str]]:
    """Return registry records suitable for docs/debug surfaces."""
    return [{key: str(value) for key, value in asdict(entry).items()} for entry in UCODE_MCP_TOOL_REGISTRY]
