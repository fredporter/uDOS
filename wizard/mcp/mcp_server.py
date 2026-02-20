"""
Wizard MCP Server

Exposes Wizard + uCODE tools to MCP clients (Vibe) over stdio.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict
import socket
import time
from collections import deque

# Ensure local gateway module is importable without shadowing MCP SDK package.
THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parent.parent
sys.path.insert(0, str(THIS_DIR))
# Avoid shadowing the installed MCP package with the repo's /mcp directory.
for bad in ("", str(REPO_ROOT)):
    while bad in sys.path:
        sys.path.remove(bad)

from gateway import WizardGateway
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "Wizard MCP",
    instructions=(
        "Expose Wizard service APIs and a limited uCODE dispatcher for Vibe."
    ),
    json_response=True,
)

_MCP_CALL_TIMESTAMPS: deque[float] = deque(maxlen=512)
_MCP_LAST_CALL_TS: float = 0.0


def _mcp_limits() -> tuple[int, float]:
    rpm = int(os.getenv("WIZARD_MCP_RATE_LIMIT_PER_MIN", "120"))
    min_interval = float(os.getenv("WIZARD_MCP_MIN_INTERVAL_SECONDS", "0.05"))
    return max(1, rpm), max(0.0, min_interval)


def _enforce_mcp_security() -> None:
    global _MCP_LAST_CALL_TS
    require_admin = os.getenv("WIZARD_MCP_REQUIRE_ADMIN_TOKEN", "1").strip().lower() in {"1", "true", "yes"}
    if require_admin and not os.getenv("WIZARD_ADMIN_TOKEN"):
        raise RuntimeError("MCP admin token required: set WIZARD_ADMIN_TOKEN")

    rpm, min_interval = _mcp_limits()
    now = time.time()
    if _MCP_LAST_CALL_TS and now - _MCP_LAST_CALL_TS < min_interval:
        raise RuntimeError("MCP rate limit: tool call cooldown active")
    _MCP_LAST_CALL_TS = now

    cutoff = now - 60.0
    while _MCP_CALL_TIMESTAMPS and _MCP_CALL_TIMESTAMPS[0] < cutoff:
        _MCP_CALL_TIMESTAMPS.popleft()
    if len(_MCP_CALL_TIMESTAMPS) >= rpm:
        raise RuntimeError("MCP rate limit: per-minute limit exceeded")
    _MCP_CALL_TIMESTAMPS.append(now)


def _client() -> WizardGateway:
    _enforce_mcp_security()
    return WizardGateway(
        base_url=os.getenv("WIZARD_BASE_URL", "http://localhost:8765"),
        admin_token=os.getenv("WIZARD_ADMIN_TOKEN"),
    )

def _is_port_open(host: str, port: int, timeout: float = 0.4) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False

def _status_line() -> str:
    # Role/ghost mode (simple env-based fallback)
    role = (os.getenv("UDOS_USER_ROLE") or os.getenv("USER_ROLE") or "guest").upper()
    ghost_mode = os.getenv("UDOS_GHOST_MODE", "1").strip().lower() in {"1", "true", "yes"}
    ghost_tag = " [GHOST MODE]" if ghost_mode else ""
    role_tag = "👻" if ghost_mode else "👤"

    # Wizard / Goblin status
    wiz_up = False
    try:
        _client().health()
        wiz_up = True
    except Exception:
        wiz_up = False
    gob_up = _is_port_open("127.0.0.1", 8767)

    wiz_icon = "🟢" if wiz_up else "🔴"
    gob_icon = "🟢" if gob_up else "🔴"

    # System stats (best-effort)
    mem = "?"
    cpu = "?"
    try:
        import psutil  # type: ignore
        mem = f"{int(psutil.virtual_memory().percent)}%"
        cpu = f"{int(psutil.cpu_percent(interval=0.1))}%"
    except Exception:
        pass

    return f"[{role_tag} {role}] {ghost_tag} [WIZ: {wiz_icon}] [GOB: {gob_icon}] [Mem: {mem}] [CPU: {cpu}] [F1-F8]"

def _emoji_indicator() -> str:
    frames = ["🙂", "😌", "🫧", "🤔", "🧠", "📝"]
    idx = int(time.time() / 0.6) % len(frames)
    return frames[idx]

def _toolbar_block() -> str:
    dev_state = "ON" if os.getenv("UDOS_DEV_MODE") in ("1", "true", "yes") else "OFF"
    commands = ["OK", "BINDER", "FILE", "MAP", "HELP"]
    line1 = "  ⎔ Commands: " + ", ".join(commands[:3]) + " (+2 more)"
    line2 = f"  ↳ DEV: {dev_state}  |  Tip: Use ':' or 'OK' for uCODE, '/' for shell"
    return "\n".join([line1, line2])

def _wrap_display(rendered: str) -> str:
    header = _status_line()
    prompt = f"[{_emoji_indicator()}] ▶ "
    return "\n".join([header, prompt, _toolbar_block(), "", rendered or ""])

def _extract_ucode_output(payload: Dict[str, Any]) -> str:
    if not isinstance(payload, dict):
        return str(payload)
    result = payload.get("result")
    if isinstance(result, dict):
        for key in ("output", "help", "text", "message"):
            value = result.get(key)
            if value:
                return str(value)
    rendered = payload.get("rendered")
    if rendered:
        return str(rendered)
    for key in ("output", "help", "text", "message"):
        value = payload.get(key)
        if value:
            return str(value)
    return ""

def _load_tool_index() -> list[str]:
    candidate_paths = [
        REPO_ROOT / "api" / "wizard" / "tools" / "mcp-tools.md",
        THIS_DIR.parent / "docs" / "api" / "tools" / "mcp-tools.md",
    ]
    tools_path = next((path for path in candidate_paths if path.exists()), None)
    if tools_path is None:
        return []
    tools: list[str] = []
    for line in tools_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if stripped.startswith("- `") and "`" in stripped[3:]:
            name = stripped.split("`", 2)[1].replace(".", "_")
            if name:
                tools.append(name)
    return tools


def _tool_registration_protocol() -> Dict[str, Any]:
    tools = _load_tool_index()
    server_tools = sorted(list(mcp._tool_manager._tools.keys()))
    indexed_set = set(tools)
    server_set = set(server_tools)
    return {
        "protocol_version": "1.0.0",
        "indexed_count": len(tools),
        "server_count": len(server_tools),
        "indexed_tools": tools,
        "server_tools": server_tools,
        "missing_from_server": sorted(list(indexed_set - server_set)),
        "missing_from_index": sorted(list(server_set - indexed_set)),
        "valid": indexed_set.issubset(server_set),
    }


@mcp.tool()
def wizard_health() -> Dict[str, Any]:
    """Get Wizard health status."""
    return _client().health()


@mcp.tool()
def wizard_config_get() -> Dict[str, Any]:
    """Get Wizard config."""
    return _client().config_get()


@mcp.tool()
def wizard_config_set(updates: Dict[str, Any]) -> Dict[str, Any]:
    """Patch Wizard config."""
    return _client().config_set(updates)

@mcp.tool()
def wizard_tools_list() -> Dict[str, Any]:
    """List MCP tool names."""
    tools = _load_tool_index()
    return {
        "count": len(tools),
        "tools": tools,
    }


@mcp.tool()
def wizard_tools_registration_status() -> Dict[str, Any]:
    """Return MCP tool registration protocol status."""
    return _tool_registration_protocol()

# Note: ucode_dispatch and ucode_command are defined at the end of this file
# to return string content for MCP protocol compatibility.


@mcp.tool()
def wizard_providers_list() -> Dict[str, Any]:
    """List Wizard providers."""
    return _client().providers_list()


@mcp.tool()
def wizard_plugin_command(command: str) -> Dict[str, Any]:
    """Run a plugin command via Wizard (stub)."""
    return _client().plugin_command(command)


@mcp.tool()
def wizard_plugins_registry_list(refresh: bool = False, include_manifests: bool = True) -> Dict[str, Any]:
    """List plugin registry entries."""
    return _client().plugin_registry_list(refresh=refresh, include_manifests=include_manifests)


@mcp.tool()
def wizard_plugins_registry_get(plugin_id: str, include_manifest: bool = True) -> Dict[str, Any]:
    """Get a plugin registry entry by id."""
    return _client().plugin_registry_get(plugin_id, include_manifest=include_manifest)


@mcp.tool()
def wizard_plugins_registry_refresh(write_index: bool = False) -> Dict[str, Any]:
    """Refresh plugin registry index."""
    return _client().plugin_registry_refresh(write_index=write_index)


@mcp.tool()
def wizard_plugins_registry_schema() -> Dict[str, Any]:
    """Get plugin registry schema."""
    return _client().plugin_registry_schema()

@mcp.tool()
def wizard_plugin_install(plugin_id: str) -> Dict[str, Any]:
    """Install a plugin."""
    return _client().plugin_install(plugin_id)


@mcp.tool()
def wizard_plugin_uninstall(plugin_id: str) -> Dict[str, Any]:
    """Uninstall a plugin."""
    return _client().plugin_uninstall(plugin_id)


@mcp.tool()
def wizard_plugin_enable(plugin_id: str) -> Dict[str, Any]:
    """Enable a plugin."""
    return _client().plugin_enable(plugin_id)


@mcp.tool()
def wizard_plugin_disable(plugin_id: str) -> Dict[str, Any]:
    """Disable a plugin."""
    return _client().plugin_disable(plugin_id)


@mcp.tool()
def wizard_workflow_list() -> Dict[str, Any]:
    """List workflows."""
    return _client().workflow_list()


@mcp.tool()
def wizard_workflow_get(workflow_id: str) -> Dict[str, Any]:
    """Get workflow by id."""
    return _client().workflow_get(workflow_id)


@mcp.tool()
def wizard_workflow_create(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Create a workflow."""
    return _client().workflow_create(payload)


@mcp.tool()
def wizard_workflow_run(workflow_id: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Run a workflow by id."""
    return _client().workflow_run(workflow_id, payload)

@mcp.tool()
def wizard_workflows_list() -> Dict[str, Any]:
    """List workflows (current endpoint)."""
    return _client().workflow_list_current()


@mcp.tool()
def wizard_workflows_create(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Create workflow (current endpoint)."""
    return _client().workflow_create_current(payload)


@mcp.tool()
def wizard_workflows_status(workflow_id: str) -> Dict[str, Any]:
    """Get workflow status."""
    return _client().workflow_status(workflow_id)


@mcp.tool()
def wizard_workflows_tasks(workflow_id: str) -> Dict[str, Any]:
    """Get workflow tasks."""
    return _client().workflow_tasks(workflow_id)


@mcp.tool()
def wizard_workflows_dashboard() -> Dict[str, Any]:
    """Get workflow dashboard."""
    return _client().workflow_dashboard()


@mcp.tool()
def wizard_workflows_tasks_dashboard(limit: int = 20) -> Dict[str, Any]:
    """Get workflow/tasks dashboard."""
    return _client().workflows_tasks_dashboard(limit=limit)


@mcp.tool()
def wizard_tasks_list() -> Dict[str, Any]:
    """List tasks."""
    return _client().task_list()


@mcp.tool()
def wizard_tasks_get(task_id: str) -> Dict[str, Any]:
    """Get task by id."""
    return _client().task_get(task_id)


@mcp.tool()
def wizard_tasks_create(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Create a task."""
    return _client().task_create(payload)


@mcp.tool()
def wizard_tasks_run(task_id: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Run a task by id."""
    return _client().task_run(task_id, payload)

@mcp.tool()
def wizard_tasks_status(limit: int = 20) -> Dict[str, Any]:
    """Get scheduler status."""
    return _client().task_status(limit=limit)


@mcp.tool()
def wizard_tasks_queue(limit: int = 20) -> Dict[str, Any]:
    """Get scheduled queue."""
    return _client().task_queue(limit=limit)


@mcp.tool()
def wizard_tasks_runs(limit: int = 50) -> Dict[str, Any]:
    """Get execution history."""
    return _client().task_runs(limit=limit)


@mcp.tool()
def wizard_tasks_task(task_id: str) -> Dict[str, Any]:
    """Get a task by id (current endpoint)."""
    return _client().task_task(task_id)


@mcp.tool()
def wizard_tasks_schedule(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Schedule a task."""
    return _client().task_schedule(payload)


@mcp.tool()
def wizard_tasks_execute(task_id: str) -> Dict[str, Any]:
    """Execute a task."""
    return _client().task_execute(task_id)


@mcp.tool()
def wizard_tasks_calendar(
    view: str = "weekly",
    start_date: str | None = None,
    format: str = "text",
) -> Dict[str, Any]:
    """Get task calendar."""
    return _client().task_calendar(view=view, start_date=start_date, format=format)


@mcp.tool()
def wizard_tasks_gantt(window_days: int = 30, format: str = "text") -> Dict[str, Any]:
    """Get task gantt."""
    return _client().task_gantt(window_days=window_days, format=format)


@mcp.tool()
def wizard_tasks_indexer_summary() -> Dict[str, Any]:
    """Get task indexer summary."""
    return _client().task_indexer_summary()


@mcp.tool()
def wizard_tasks_indexer_search(
    status: str | None = None,
    due: str | None = None,
    tag: str | None = None,
    priority: int | None = None,
) -> Dict[str, Any]:
    """Search task indexer."""
    return _client().task_indexer_search(status=status, due=due, tag=tag, priority=priority)


@mcp.tool()
def wizard_tasks_dashboard(limit: int = 20) -> Dict[str, Any]:
    """Get tasks dashboard."""
    return _client().task_dashboard(limit=limit)


@mcp.tool()
def wizard_dev_health() -> Dict[str, Any]:
    """Dev mode health."""
    return _client().dev_health()


@mcp.tool()
def wizard_dev_status() -> Dict[str, Any]:
    """Dev mode status."""
    return _client().dev_status()


@mcp.tool()
def wizard_dev_activate() -> Dict[str, Any]:
    """Activate dev mode."""
    return _client().dev_activate()


@mcp.tool()
def wizard_dev_deactivate() -> Dict[str, Any]:
    """Deactivate dev mode."""
    return _client().dev_deactivate()


@mcp.tool()
def wizard_dev_restart() -> Dict[str, Any]:
    """Restart dev mode."""
    return _client().dev_restart()


@mcp.tool()
def wizard_dev_clear() -> Dict[str, Any]:
    """Clear dev mode state."""
    return _client().dev_clear()


@mcp.tool()
def wizard_dev_logs(lines: int = 50) -> Dict[str, Any]:
    """Fetch dev logs."""
    return _client().dev_logs(lines)


@mcp.tool()
def wizard_monitoring_summary() -> Dict[str, Any]:
    """Get monitoring health summary."""
    return _client().monitoring_summary()


@mcp.tool()
def wizard_monitoring_diagnostics() -> Dict[str, Any]:
    """Get monitoring diagnostics bundle."""
    return _client().monitoring_diagnostics()


@mcp.tool()
def wizard_monitoring_logs_list() -> Dict[str, Any]:
    """List log files."""
    return _client().monitoring_logs_list()


@mcp.tool()
def wizard_monitoring_log_tail(log_name: str, lines: int = 200) -> Dict[str, Any]:
    """Tail a log file."""
    return _client().monitoring_log_tail(log_name, lines)


@mcp.tool()
def wizard_monitoring_log_stats() -> Dict[str, Any]:
    """Get log stats summary."""
    return _client().monitoring_log_stats()


@mcp.tool()
def wizard_monitoring_alerts_list(
    severity: str | None = None,
    alert_type: str | None = None,
    service: str | None = None,
    unacknowledged_only: bool = False,
    limit: int = 100,
) -> Dict[str, Any]:
    """List monitoring alerts."""
    return _client().monitoring_alerts_list(
        severity=severity,
        alert_type=alert_type,
        service=service,
        unacknowledged_only=unacknowledged_only,
        limit=limit,
    )


@mcp.tool()
def wizard_monitoring_alert_ack(alert_id: str) -> Dict[str, Any]:
    """Acknowledge an alert."""
    return _client().monitoring_alert_ack(alert_id)


@mcp.tool()
def wizard_monitoring_alert_resolve(alert_id: str) -> Dict[str, Any]:
    """Resolve an alert."""
    return _client().monitoring_alert_resolve(alert_id)


@mcp.tool()
def wizard_datasets_list() -> Dict[str, Any]:
    """List dataset tables."""
    return _client().datasets_list_tables()


@mcp.tool()
def wizard_datasets_summary() -> Dict[str, Any]:
    """Get dataset summary."""
    return _client().datasets_summary()


@mcp.tool()
def wizard_datasets_schema() -> Dict[str, Any]:
    """Get dataset schema."""
    return _client().datasets_schema()


@mcp.tool()
def wizard_datasets_table(
    table_name: str,
    limit: int = 50,
    offset: int = 0,
    filters: list[str] | None = None,
    order_by: str | None = None,
    desc: bool = False,
) -> Dict[str, Any]:
    """Fetch rows from a dataset table."""
    return _client().datasets_table(
        table_name,
        limit=limit,
        offset=offset,
        filters=filters,
        order_by=order_by,
        desc=desc,
    )


@mcp.tool()
def wizard_datasets_query(
    table: str,
    limit: int = 50,
    offset: int = 0,
    columns: str | None = None,
    filters: list[str] | None = None,
    order_by: str | None = None,
    desc: bool = False,
) -> Dict[str, Any]:
    """Query a dataset table."""
    return _client().datasets_query(
        table,
        limit=limit,
        offset=offset,
        columns=columns,
        filters=filters,
        order_by=order_by,
        desc=desc,
    )


@mcp.tool()
def wizard_datasets_export(
    table: str,
    limit: int = 100,
    offset: int = 0,
    filters: list[str] | None = None,
    order_by: str | None = None,
    desc: bool = False,
) -> Dict[str, Any]:
    """Export a dataset table (server-side)."""
    return _client().datasets_export(
        table,
        limit=limit,
        offset=offset,
        filters=filters,
        order_by=order_by,
        desc=desc,
    )


@mcp.tool()
def wizard_datasets_import(table: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Import/parse payload into a dataset table (stub)."""
    return _client().datasets_parse(table, payload)


@mcp.tool()
def wizard_artifacts_list(kind: str | None = None) -> Dict[str, Any]:
    """List artifacts."""
    return _client().artifacts_list(kind=kind)


@mcp.tool()
def wizard_artifacts_summary() -> Dict[str, Any]:
    """Summarize artifacts."""
    return _client().artifacts_summary()


@mcp.tool()
def wizard_artifacts_add(kind: str, source_path: str, notes: str | None = None) -> Dict[str, Any]:
    """Add an artifact."""
    return _client().artifacts_add(kind=kind, source_path=source_path, notes=notes)


@mcp.tool()
def wizard_artifacts_delete(artifact_id: str) -> Dict[str, Any]:
    """Delete an artifact."""
    return _client().artifacts_delete(artifact_id)


@mcp.tool()
def wizard_library_status() -> Dict[str, Any]:
    """Get library status."""
    return _client().library_status()


@mcp.tool()
def wizard_wiki_provision() -> Dict[str, Any]:
    """Provision wiki."""
    return _client().wiki_provision()


@mcp.tool()
def wizard_wiki_structure() -> Dict[str, Any]:
    """Get wiki structure."""
    return _client().wiki_structure()


@mcp.tool()
def wizard_renderer_themes() -> Dict[str, Any]:
    """List renderer themes."""
    return _client().renderer_themes()


@mcp.tool()
def wizard_renderer_theme(theme_name: str) -> Dict[str, Any]:
    """Get renderer theme detail."""
    return _client().renderer_theme(theme_name)


@mcp.tool()
def wizard_renderer_site_exports() -> Dict[str, Any]:
    """List renderer site exports."""
    return _client().renderer_site_exports()


@mcp.tool()
def wizard_renderer_site_files(theme_name: str) -> Dict[str, Any]:
    """List renderer site files for a theme."""
    return _client().renderer_site_files(theme_name)


@mcp.tool()
def wizard_renderer_missions() -> Dict[str, Any]:
    """List renderer missions."""
    return _client().renderer_missions()


@mcp.tool()
def wizard_renderer_mission(mission_id: str) -> Dict[str, Any]:
    """Get renderer mission."""
    return _client().renderer_mission(mission_id)


@mcp.tool()
def wizard_renderer_render(payload: Dict[str, Any] | None = None, theme: str | None = None) -> Dict[str, Any]:
    """Render site output."""
    return _client().renderer_render(payload=payload, theme=theme)


@mcp.tool()
def wizard_teletext_canvas() -> Dict[str, Any]:
    """Get teletext canvas."""
    return _client().teletext_canvas()


@mcp.tool()
def wizard_teletext_nes_buttons() -> Dict[str, Any]:
    """Get NES button state."""
    return _client().teletext_nes_buttons()


@mcp.tool()
def wizard_system_os() -> Dict[str, Any]:
    """Get OS info."""
    return _client().system_os()


@mcp.tool()
def wizard_system_stats() -> Dict[str, Any]:
    """Get system stats."""
    return _client().system_stats()


@mcp.tool()
def wizard_system_info() -> Dict[str, Any]:
    """Get system info."""
    return _client().system_info()


@mcp.tool()
def wizard_system_memory() -> Dict[str, Any]:
    """Get memory stats."""
    return _client().system_memory()


@mcp.tool()
def wizard_system_storage() -> Dict[str, Any]:
    """Get storage stats."""
    return _client().system_storage()


@mcp.tool()
def wizard_system_uptime() -> Dict[str, Any]:
    """Get uptime stats."""
    return _client().system_uptime()


@mcp.tool()
def wizard_fonts_manifest() -> Dict[str, Any]:
    """Get fonts manifest."""
    return _client().fonts_manifest()


@mcp.tool()
def wizard_fonts_sample() -> Dict[str, Any]:
    """Get font samples."""
    return _client().fonts_sample()


@mcp.tool()
def wizard_fonts_file(path: str) -> Dict[str, Any]:
    """Fetch font file."""
    return _client().fonts_file(path)


@mcp.tool()
def wizard_ai_health() -> Dict[str, Any]:
    """Get AI health."""
    return _client().ai_health()


@mcp.tool()
def wizard_ai_config() -> Dict[str, Any]:
    """Get AI config."""
    return _client().ai_config()


@mcp.tool()
def wizard_ai_context() -> Dict[str, Any]:
    """Get AI context."""
    return _client().ai_context()


@mcp.tool()
def wizard_ai_suggest_next() -> Dict[str, Any]:
    """Suggest next steps."""
    return _client().ai_suggest_next()


@mcp.tool()
def wizard_ai_analyze_logs(log_type: str = "error") -> Dict[str, Any]:
    """Analyze logs with AI."""
    return _client().ai_analyze_logs(log_type=log_type)


@mcp.tool()
def wizard_ai_explain_code(
    file_path: str,
    line_start: int | None = None,
    line_end: int | None = None,
) -> Dict[str, Any]:
    """Explain code with AI."""
    return _client().ai_explain_code(file_path=file_path, line_start=line_start, line_end=line_end)


@mcp.tool()
def wizard_providers_status(provider_id: str) -> Dict[str, Any]:
    """Get provider status."""
    return _client().provider_status(provider_id)


@mcp.tool()
def wizard_providers_config(provider_id: str) -> Dict[str, Any]:
    """Get provider config."""
    return _client().provider_config(provider_id)


@mcp.tool()
def wizard_providers_enable(provider_id: str) -> Dict[str, Any]:
    """Enable a provider."""
    return _client().provider_enable(provider_id)


@mcp.tool()
def wizard_providers_disable(provider_id: str) -> Dict[str, Any]:
    """Disable a provider."""
    return _client().provider_disable(provider_id)


@mcp.tool()
def wizard_providers_setup_flags() -> Dict[str, Any]:
    """Get provider setup flags."""
    return _client().provider_setup_flags()


@mcp.tool()
def wizard_providers_models_available() -> Dict[str, Any]:
    """List available provider models."""
    return _client().provider_models_available()


@mcp.tool()
def wizard_providers_models_installed() -> Dict[str, Any]:
    """List installed provider models."""
    return _client().provider_models_installed()


@mcp.tool()
def wizard_providers_models_pull_status() -> Dict[str, Any]:
    """Get provider model pull status."""
    return _client().provider_models_pull_status()


@mcp.tool()
def wizard_providers_dashboard() -> Dict[str, Any]:
    """Get providers dashboard."""
    return _client().providers_dashboard()



@mcp.tool()
def wizard_provider_status(provider_id: str) -> Dict[str, Any]:
    """Get provider status."""
    return _client().provider_status(provider_id)

@mcp.tool()
def wizard_provider_config(provider_id: str) -> Dict[str, Any]:
    """Get provider config metadata."""
    return _client().provider_config(provider_id)


@mcp.tool()
def wizard_provider_enable(provider_id: str) -> Dict[str, Any]:
    """Enable provider."""
    return _client().provider_enable(provider_id)


@mcp.tool()
def wizard_provider_disable(provider_id: str) -> Dict[str, Any]:
    """Disable provider."""
    return _client().provider_disable(provider_id)


@mcp.tool()
def wizard_provider_setup_flags() -> Dict[str, Any]:
    """Get provider setup flags."""
    return _client().provider_setup_flags()


@mcp.tool()
def wizard_provider_models_available() -> Dict[str, Any]:
    """List available models."""
    return _client().provider_models_available()


@mcp.tool()
def wizard_provider_models_installed() -> Dict[str, Any]:
    """List installed models."""
    return _client().provider_models_installed()


@mcp.tool()
def wizard_provider_models_pull_status() -> Dict[str, Any]:
    """Get model pull status."""
    return _client().provider_models_pull_status()


@mcp.tool()
def ucode_command(raw_input: str) -> str:
    """Route raw input to uCODE (supports OK/:/ shell prefixes)."""
    resp = _client().ucode_dispatch(raw_input)
    rendered = resp.get("rendered") or resp.get("result", {}).get("output") or ""
    return _wrap_display(rendered)


@mcp.tool()
def ucode_dispatch(command: str) -> str:
    """Dispatch an allowlisted uCODE command via Wizard."""
    resp = _client().ucode_dispatch(command)
    rendered = resp.get("rendered") or resp.get("result", {}).get("output") or ""
    return _wrap_display(rendered)


# ─────────────────────────────────────────────────────────────────────────────
# Vibe Skills MCP Tools Registration
# ─────────────────────────────────────────────────────────────────────────────

try:
    from vibe_mcp_integration import register_vibe_mcp_tools
    register_vibe_mcp_tools(mcp)
except ImportError as e:
    # Vibe MCP integration is optional
    pass
except Exception as e:
    # Log but don't fail if Vibe integration has issues
    pass


if __name__ == "__main__":
    mcp.run(transport="stdio")
