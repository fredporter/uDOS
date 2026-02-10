"""
Wizard MCP Gateway (scaffold)

This module provides a thin wrapper around Wizard HTTP APIs.
The MCP protocol integration will be implemented in server.py.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

import requests


class WizardGateway:
    """HTTP client wrapper for Wizard services."""

    def __init__(self, base_url: Optional[str] = None, admin_token: Optional[str] = None):
        self.base_url = (base_url or os.getenv("WIZARD_BASE_URL", "http://localhost:8765")).rstrip("/")
        self.admin_token = admin_token or os.getenv("WIZARD_ADMIN_TOKEN")

    def _headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {"Content-Type": "application/json"}
        if self.admin_token:
            headers["X-Admin-Token"] = self.admin_token
        return headers

    def health(self) -> Dict[str, Any]:
        resp = requests.get(f"{self.base_url}/health", timeout=5)
        resp.raise_for_status()
        return resp.json()

    def config_get(self) -> Dict[str, Any]:
        resp = requests.get(f"{self.base_url}/api/config", headers=self._headers(), timeout=10)
        resp.raise_for_status()
        return resp.json()

    def config_set(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        payload = {"updates": updates}
        resp = requests.patch(
            f"{self.base_url}/api/config",
            json=payload,
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def providers_list(self) -> Dict[str, Any]:
        resp = requests.get(f"{self.base_url}/api/providers", headers=self._headers(), timeout=10)
        resp.raise_for_status()
        return resp.json()

    def plugin_command(self, command: str) -> Dict[str, Any]:
        payload = {"command": command}
        resp = requests.post(
            f"{self.base_url}/api/plugin/command",
            json=payload,
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def ucode_dispatch(self, command: str) -> Dict[str, Any]:
        payload = {"command": command}
        resp = requests.post(
            f"{self.base_url}/api/ucode/dispatch",
            json=payload,
            headers=self._headers(),
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    # Plugins
    def plugin_registry_list(self, refresh: bool = False, include_manifests: bool = True) -> Dict[str, Any]:
        params = {"refresh": str(refresh).lower(), "include_manifests": str(include_manifests).lower()}
        resp = requests.get(
            f"{self.base_url}/api/plugins/registry",
            params=params,
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def plugin_registry_get(self, plugin_id: str, include_manifest: bool = True) -> Dict[str, Any]:
        params = {"include_manifest": str(include_manifest).lower()}
        resp = requests.get(
            f"{self.base_url}/api/plugins/registry/{plugin_id}",
            params=params,
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def plugin_registry_refresh(self, write_index: bool = False) -> Dict[str, Any]:
        payload = {"write_index": write_index}
        resp = requests.post(
            f"{self.base_url}/api/plugins/registry/refresh",
            json=payload,
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def plugin_registry_schema(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/plugins/registry/schema",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def plugin_install(self, plugin_id: str) -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/api/plugins/{plugin_id}/install",
            headers=self._headers(),
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def plugin_uninstall(self, plugin_id: str) -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/api/plugins/{plugin_id}/uninstall",
            headers=self._headers(),
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def plugin_enable(self, plugin_id: str) -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/api/catalog/plugins/{plugin_id}/enable",
            headers=self._headers(),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()

    def plugin_disable(self, plugin_id: str) -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/api/catalog/plugins/{plugin_id}/disable",
            headers=self._headers(),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()

    # Workflow
    def workflow_list(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/workflows",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def workflow_get(self, workflow_id: str) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/workflows/{workflow_id}",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def workflow_create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/api/workflows",
            json=payload,
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def workflow_run(self, workflow_id: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/api/workflows/{workflow_id}/run",
            json=payload or {},
            headers=self._headers(),
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    # Workflow (current endpoints)
    def workflow_list_current(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/workflows/list",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def workflow_create_current(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/api/workflows/create",
            json=payload,
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/workflows/{workflow_id}/status",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def workflow_tasks(self, workflow_id: str) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/workflows/{workflow_id}/tasks",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def workflow_dashboard(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/workflows/dashboard",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def workflows_tasks_dashboard(self, limit: int = 20) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/workflows/tasks-dashboard",
            params={"limit": limit},
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    # Tasks
    def task_list(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/tasks",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def task_get(self, task_id: str) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/tasks/{task_id}",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def task_create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/api/tasks",
            json=payload,
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def task_run(self, task_id: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/api/tasks/{task_id}/run",
            json=payload or {},
            headers=self._headers(),
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    # Tasks (current endpoints)
    def task_status(self, limit: int = 20) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/tasks/status",
            params={"limit": limit},
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def task_queue(self, limit: int = 20) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/tasks/queue",
            params={"limit": limit},
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def task_runs(self, limit: int = 50) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/tasks/runs",
            params={"limit": limit},
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def task_task(self, task_id: str) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/tasks/task/{task_id}",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def task_schedule(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/api/tasks/schedule",
            json=payload,
            headers=self._headers(),
            timeout=20,
        )
        resp.raise_for_status()
        return resp.json()

    def task_execute(self, task_id: str) -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/api/tasks/execute/{task_id}",
            headers=self._headers(),
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def task_calendar(
        self,
        view: str = "weekly",
        start_date: Optional[str] = None,
        format: str = "text",
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {"view": view, "format": format}
        if start_date:
            params["start_date"] = start_date
        resp = requests.get(
            f"{self.base_url}/api/tasks/calendar",
            params=params,
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def task_gantt(self, window_days: int = 30, format: str = "text") -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/tasks/gantt",
            params={"window_days": window_days, "format": format},
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def task_indexer_summary(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/tasks/indexer/summary",
            headers=self._headers(),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()

    def task_indexer_search(
        self,
        status: Optional[str] = None,
        due: Optional[str] = None,
        tag: Optional[str] = None,
        priority: Optional[int] = None,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        if status:
            params["status"] = status
        if due:
            params["due"] = due
        if tag:
            params["tag"] = tag
        if priority is not None:
            params["priority"] = priority
        resp = requests.get(
            f"{self.base_url}/api/tasks/indexer/search",
            params=params,
            headers=self._headers(),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()

    def task_dashboard(self, limit: int = 20) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/tasks/dashboard",
            params={"limit": limit},
            headers=self._headers(),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()

    # Dev mode
    def dev_health(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/dev/health",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def dev_status(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/dev/status",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def dev_activate(self) -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/api/dev/activate",
            headers=self._headers(),
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def dev_deactivate(self) -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/api/dev/deactivate",
            headers=self._headers(),
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def dev_restart(self) -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/api/dev/restart",
            headers=self._headers(),
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def dev_clear(self) -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/api/dev/clear",
            headers=self._headers(),
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def dev_logs(self, lines: int = 50) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/dev/logs",
            params={"lines": lines},
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    # Monitoring + Logs
    def monitoring_summary(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/monitoring/summary",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def monitoring_diagnostics(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/monitoring/diagnostics",
            headers=self._headers(),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()

    def monitoring_logs_list(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/monitoring/logs",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def monitoring_log_tail(self, log_name: str, lines: int = 200) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/monitoring/logs/{log_name}",
            params={"lines": lines},
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def monitoring_log_stats(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/monitoring/logs/stats",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def monitoring_alerts_list(
        self,
        severity: Optional[str] = None,
        alert_type: Optional[str] = None,
        service: Optional[str] = None,
        unacknowledged_only: bool = False,
        limit: int = 100,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {"unacknowledged_only": str(unacknowledged_only).lower(), "limit": limit}
        if severity:
            params["severity"] = severity
        if alert_type:
            params["type"] = alert_type
        if service:
            params["service"] = service
        resp = requests.get(
            f"{self.base_url}/api/monitoring/alerts",
            params=params,
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def monitoring_alert_ack(self, alert_id: str) -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/api/monitoring/alerts/{alert_id}/ack",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def monitoring_alert_resolve(self, alert_id: str) -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/api/monitoring/alerts/{alert_id}/resolve",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    # Datasets
    def datasets_list_tables(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/data/tables",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def datasets_summary(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/data/summary",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def datasets_schema(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/data/schema",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def datasets_table(
        self,
        table_name: str,
        limit: int = 50,
        offset: int = 0,
        filters: Optional[list[str]] = None,
        order_by: Optional[str] = None,
        desc: bool = False,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
            "desc": str(desc).lower(),
        }
        if filters:
            params["filter"] = filters
        if order_by:
            params["order_by"] = order_by
        resp = requests.get(
            f"{self.base_url}/api/data/tables/{table_name}",
            params=params,
            headers=self._headers(),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()

    def datasets_query(
        self,
        table: str,
        limit: int = 50,
        offset: int = 0,
        columns: Optional[str] = None,
        filters: Optional[list[str]] = None,
        order_by: Optional[str] = None,
        desc: bool = False,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "table": table,
            "limit": limit,
            "offset": offset,
            "desc": str(desc).lower(),
        }
        if columns:
            params["columns"] = columns
        if filters:
            params["filter"] = filters
        if order_by:
            params["order_by"] = order_by
        resp = requests.get(
            f"{self.base_url}/api/data/query",
            params=params,
            headers=self._headers(),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()

    def datasets_export(
        self,
        table: str,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[list[str]] = None,
        order_by: Optional[str] = None,
        desc: bool = False,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
            "desc": str(desc).lower(),
        }
        if filters:
            params["filter"] = filters
        if order_by:
            params["order_by"] = order_by
        resp = requests.post(
            f"{self.base_url}/api/data/export/{table}",
            params=params,
            headers=self._headers(),
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def datasets_parse(self, table: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/api/data/parse/{table}",
            json=payload,
            headers=self._headers(),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()

    # Artifacts
    def artifacts_list(self, kind: Optional[str] = None) -> Dict[str, Any]:
        params = {"kind": kind} if kind else None
        resp = requests.get(
            f"{self.base_url}/api/artifacts",
            params=params,
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def artifacts_summary(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/artifacts/summary",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def artifacts_add(self, kind: str, source_path: str, notes: Optional[str] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"kind": kind, "source_path": source_path}
        if notes:
            payload["notes"] = notes
        resp = requests.post(
            f"{self.base_url}/api/artifacts/add",
            json=payload,
            headers=self._headers(),
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def artifacts_delete(self, artifact_id: str) -> Dict[str, Any]:
        resp = requests.delete(
            f"{self.base_url}/api/artifacts/{artifact_id}",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    # Library
    def library_status(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/library/status",
            headers=self._headers(),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()

    # Wiki
    def wiki_provision(self) -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/api/wiki/provision",
            headers=self._headers(),
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def wiki_structure(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/wiki/structure",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    # Renderer
    def renderer_themes(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/renderer/themes",
            headers=self._headers(),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()

    def renderer_theme(self, theme_name: str) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/renderer/themes/{theme_name}",
            headers=self._headers(),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()

    def renderer_site_exports(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/renderer/site",
            headers=self._headers(),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()

    def renderer_site_files(self, theme_name: str) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/renderer/site/{theme_name}/files",
            headers=self._headers(),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()

    def renderer_missions(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/renderer/missions",
            headers=self._headers(),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()

    def renderer_mission(self, mission_id: str) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/renderer/missions/{mission_id}",
            headers=self._headers(),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()

    def renderer_render(self, payload: Dict[str, Any] | None = None, theme: str | None = None) -> Dict[str, Any]:
        params = {"theme": theme} if theme else None
        resp = requests.post(
            f"{self.base_url}/api/renderer/render",
            params=params,
            json=payload or {},
            headers=self._headers(),
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()

    # Teletext
    def teletext_canvas(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/teletext/canvas",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def teletext_nes_buttons(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/teletext/nes-buttons",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    # System info
    def system_os(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/system/os",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def system_stats(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/system/stats",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def system_info(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/system/info",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def system_memory(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/system/memory",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def system_storage(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/system/storage",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def system_uptime(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/system/uptime",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    # Fonts
    def fonts_manifest(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/fonts/manifest",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def fonts_sample(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/fonts/sample",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def fonts_file(self, path: str) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/fonts/file",
            params={"path": path},
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    # AI
    def ai_health(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/ai/health",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def ai_config(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/ai/config",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def ai_context(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/ai/context",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def ai_suggest_next(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/ai/suggest-next",
            headers=self._headers(),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()

    def ai_analyze_logs(self, log_type: str = "error") -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/api/ai/analyze-logs",
            params={"log_type": log_type},
            headers=self._headers(),
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def ai_explain_code(
        self,
        file_path: str,
        line_start: int | None = None,
        line_end: int | None = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"file_path": file_path}
        if line_start is not None:
            payload["line_start"] = line_start
        if line_end is not None:
            payload["line_end"] = line_end
        resp = requests.post(
            f"{self.base_url}/api/ai/explain-code",
            json=payload,
            headers=self._headers(),
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()

    # Providers
    def providers_list(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/providers/list",
            headers=self._headers(),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()

    def provider_status(self, provider_id: str) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/providers/{provider_id}/status",
            headers=self._headers(),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()

    def provider_config(self, provider_id: str) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/providers/{provider_id}/config",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def provider_enable(self, provider_id: str) -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/api/providers/{provider_id}/enable",
            headers=self._headers(),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()

    def provider_disable(self, provider_id: str) -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/api/providers/{provider_id}/disable",
            headers=self._headers(),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()

    def provider_setup_flags(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/providers/setup/flags",
            headers=self._headers(),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()

    def provider_models_available(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/providers/models/available",
            headers=self._headers(),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()

    def provider_models_installed(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/providers/models/installed",
            headers=self._headers(),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()

    def provider_models_pull_status(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/providers/models/pull/status",
            headers=self._headers(),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()

    def providers_dashboard(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/providers/dashboard",
            headers=self._headers(),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()
