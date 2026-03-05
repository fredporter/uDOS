"""DEV MODE command handler - Activate/deactivate development mode via Wizard Server."""
from __future__ import annotations

import json

from core.services.logging_manager import get_logger
from core.services.stdlib_http import HTTPError, http_get, http_post

logger = get_logger("core", category="dev-mode", name="dev-mode-handler")

from core.commands.base import BaseCommandHandler
from core.services.rate_limit_helpers import guard_wizard_endpoint
from core.tui.output import OutputToolkit


class DevModeHandler(BaseCommandHandler):
    """Handler for DEV MODE command - managed by Wizard Server."""

    def __init__(self):
        """Initialize dev mode handler."""
        super().__init__()
        self.wizard_host = "127.0.0.1"
        self.wizard_port = 8765

    def _admin_token(self) -> str:
        from core.services.unified_config_loader import get_config

        return get_config("WIZARD_ADMIN_TOKEN", "").strip()

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        token = self._admin_token()
        if token:
            headers["X-Admin-Token"] = token
        return headers

    def _admin_guard(self) -> dict | None:
        try:
            from core.services.permission_handler import (
                Permission,
                get_permission_handler,
            )
            permission_handler = get_permission_handler()

            if not permission_handler.require(Permission.ADMIN, action="dev_mode"):
                output = "\n".join(
                    [
                        OutputToolkit.banner("DEV MODE"),
                        "Dev mode is restricted to admin role users.",
                        "Tip: Use USER ROLE or SETUP to switch to admin.",
                    ]
                )
                return {
                    "status": "error",
                    "message": "Admin role required for dev mode",
                    "output": output,
                }
            if not permission_handler.require(Permission.DEV_MODE, action="dev_mode"):
                output = "\n".join(
                    [
                        OutputToolkit.banner("DEV MODE"),
                        "Dev mode requires explicit Dev Mode permission.",
                        "Tip: Enable the dev profile and use an admin account with dev access.",
                    ]
                )
                return {
                    "status": "error",
                    "message": "Dev Mode permission required",
                    "output": output,
                }
        except Exception as exc:
            return {
                "status": "error",
                "message": f"Failed to verify admin role: {exc}",
            }
        return None

    def _dev_templates_guard(self) -> dict | None:
        try:
            from core.services.logging_api import get_repo_root

            repo_root = get_repo_root()
            dev_root = repo_root / "dev"
            if not dev_root.exists():
                output = "\n".join(
                    [
                        OutputToolkit.banner("DEV MODE"),
                        "Dev workspace not present (`@dev` at /dev).",
                        "Hint: restore the tracked /dev framework payload.",
                    ]
                )
                return {
                    "status": "error",
                    "message": "Dev workspace missing",
                    "output": output,
                }
            marker_paths = [
                dev_root / "README.md",
                dev_root / "AGENTS.md",
                dev_root / "extension.json",
                dev_root / "ops" / "README.md",
                dev_root / "ops" / "AGENTS.md",
                dev_root / "ops" / "DEVLOG.md",
                dev_root / "ops" / "project.json",
                dev_root / "ops" / "tasks.md",
                dev_root / "ops" / "tasks.json",
                dev_root / "ops" / "completed.json",
                dev_root / "docs" / "README.md",
                dev_root / "docs" / "DEV-MODE-POLICY.md",
                dev_root / "docs" / "specs" / "DEV-WORKSPACE-SPEC.md",
                dev_root / "docs" / "howto" / "GETTING-STARTED.md",
                dev_root / "docs" / "howto" / "VIBE-Setup-Guide.md",
                dev_root / "docs" / "features" / "GITHUB-INTEGRATION.md",
                dev_root / "goblin" / "README.md",
            ]
            if not all(path.exists() for path in marker_paths):
                output = "\n".join(
                    [
                        OutputToolkit.banner("DEV MODE"),
                        "Dev extension framework is missing required files.",
                        "Hint: Update the /dev remote framework.",
                    ]
                )
                return {
                    "status": "error",
                    "message": "Dev framework missing",
                    "output": output,
                }
        except Exception as exc:
            return {
                "status": "error",
                "message": f"Failed to verify /dev templates: {exc}",
            }
        return None

    def _dev_manifest(self) -> dict:
        try:
            from core.services.logging_api import get_repo_root

            manifest_path = get_repo_root() / "dev" / "extension.json"
            if not manifest_path.exists():
                return {}
            with open(manifest_path, encoding="utf-8") as handle:
                payload = json.load(handle)
            return payload if isinstance(payload, dict) else {}
        except Exception:
            return {}

    def _resolve_action(self, raw_action: str) -> str:
        action = (raw_action or "status").strip().lower()
        if action in {"mode", "state"}:
            return "status"
        manifest = self._dev_manifest()
        actions = manifest.get("commands") or {}
        for canonical, meta in actions.items():
            aliases = [str(item).strip().lower() for item in (meta or {}).get("aliases", []) if str(item).strip()]
            if action == canonical.lower() or action in aliases:
                return canonical.lower()
        return action

    def _dev_syntax(self) -> str:
        manifest = self._dev_manifest()
        syntax = manifest.get("syntax")
        if isinstance(syntax, str) and syntax.strip():
            return syntax.strip()
        return "DEV [on|off|status|restart|logs|health|clear|plan|sync <workflow_plan>|schedule <template> <workflow_plan>|run <workflow_plan>|task <workflow_plan> <task_id> <status>]"

    def _throttle_guard(self, endpoint: str) -> dict | None:
        """Return throttle response when rate limit exceeded."""
        return guard_wizard_endpoint(endpoint)

    def handle(self, command: str, params: list[str], grid=None, parser=None) -> dict:
        """Handle DEV MODE command.

        Args:
            command: Command name (DEV MODE)
            params: [activate|deactivate|status|restart|logs] (default: status)
            grid: Optional grid context
            parser: Optional parser

        Returns:
            Dict with dev mode status
        """
        action = self._resolve_action(params[0] if params else "status")
        if action in {"on", "activate", "start"}:
            return self._activate_dev_mode()
        if action in {"off", "deactivate", "stop"}:
            return self._deactivate_dev_mode()
        if action in {"status", "stat"}:
            return self._get_dev_status()
        if action in {"restart"}:
            return self._restart_dev_mode()
        if action in {"logs", "log"}:
            return self._get_dev_logs()
        if action in {"health"}:
            return self._get_dev_health()
        if action in {"clear"}:
            return self._clear_dev_mode()
        if action in {"plan", "planning"}:
            return self._get_dev_plan()
        if action in {"sync"}:
            return self._sync_workflow_plan(params[1] if len(params) > 1 else "")
        if action in {"schedule"}:
            template = params[1] if len(params) > 1 else ""
            workflow_plan = params[2] if len(params) > 2 else ""
            return self._register_scheduler_template(template, workflow_plan)
        if action in {"run"}:
            return self._run_workflow_plan(params[1] if len(params) > 1 else "")
        if action in {"task"}:
            workflow_plan = params[1] if len(params) > 1 else ""
            task_id = params[2] if len(params) > 2 else ""
            status = params[3] if len(params) > 3 else ""
            return self._update_workflow_task(workflow_plan, task_id, status)

        output = "\n".join(
            [
                OutputToolkit.banner("DEV MODE"),
                f"Usage: {self._dev_syntax()}",
            ]
        )
        return {
            "status": "error",
            "message": "Unknown DEV action",
            "output": output,
        }

    def _activate_dev_mode(self) -> dict:
        """Activate dev mode via Wizard."""
        try:
            guard = self._admin_guard()
            if guard:
                return guard
            dev_guard = self._dev_templates_guard()
            if dev_guard:
                return dev_guard
            guard = self._throttle_guard("/api/dev/activate")
            if guard:
                return guard
            response = http_post(
                f"http://{self.wizard_host}:{self.wizard_port}/api/dev/activate",
                headers=self._headers(),
                timeout=10,
            )
            if response["status_code"] in {401, 403}:
                return self._admin_guard() or {
                    "status": "error",
                    "message": "Admin token required for dev mode",
                }
            if response["status_code"] == 412:
                return self._dev_templates_guard() or {
                    "status": "error",
                    "message": "Dev workspace missing",
                }
            if response["status_code"] == 409:
                result = response.get("json", {})
                return {
                    "status": "error",
                    "message": result.get("detail") or "Dev mode is not active",
                }
            result = response.get("json", {})
            if response["status_code"] >= 400:
                return {
                    "status": "error",
                    "message": result.get("detail") or result.get("message") or "Dev mode activation failed",
                }
            logger.info(f"[DEV] Dev mode activated: {result.get('message')}")
            framework = (result.get("extension") or {}).get("framework", {})
            output = "\n".join(
                [
                    OutputToolkit.banner("DEV MODE ACTIVATED"),
                    OutputToolkit.table(
                        ["key", "value"],
                        [
                            ["dev_root", str(result.get("dev_root"))],
                            ["framework_ready", str(framework.get("framework_ready"))],
                            ["remote_framework_only", str(framework.get("remote_framework_only"))],
                        ],
                    ),
                ]
            )
            return {
                "status": "success",
                "message": result.get("message"),
                "output": output,
                "state": "activated",
                "dev_root": result.get("dev_root"),
                "extension": result.get("extension"),
            }
        except HTTPError:
            logger.error("[DEV] Cannot connect to Wizard Server")
            return {
                "status": "error",
                "message": "Wizard Server not running on 127.0.0.1:8765",
                "hint": "Start Wizard with: uv run wizard/server.py --no-interactive",
            }
        except Exception as exc:
            logger.error(f"[DEV] Failed to activate dev mode: {exc}")
            return {
                "status": "error",
                "message": str(exc),
            }

    def _deactivate_dev_mode(self) -> dict:
        """Deactivate dev mode via Wizard."""
        try:
            guard = self._admin_guard()
            if guard:
                return guard
            guard = self._throttle_guard("/api/dev/deactivate")
            if guard:
                return guard
            response = http_post(
                f"http://{self.wizard_host}:{self.wizard_port}/api/dev/deactivate",
                headers=self._headers(),
                timeout=10,
            )
            if response["status_code"] in {401, 403}:
                return self._admin_guard() or {
                    "status": "error",
                    "message": "Admin token required for dev mode",
                }
            if response["status_code"] == 412:
                return self._dev_templates_guard() or {
                    "status": "error",
                    "message": "Dev workspace missing",
                }
            result = response.get("json", {})
            if response["status_code"] >= 400:
                return {
                    "status": "error",
                    "message": result.get("detail") or result.get("message") or "Dev mode deactivation failed",
                }
            logger.info(f"[DEV] Dev mode deactivated: {result.get('message')}")
            output = "\n".join(
                [
                    OutputToolkit.banner("DEV MODE DEACTIVATED"),
                    result.get("message", ""),
                ]
            )
            return {
                "status": "success",
                "message": result.get("message"),
                "output": output,
                "state": "deactivated",
            }
        except HTTPError:
            return {
                "status": "error",
                "message": "Wizard Server not running",
            }
        except Exception as exc:
            logger.error(f"[DEV] Failed to deactivate dev mode: {exc}")
            return {
                "status": "error",
                "message": str(exc),
            }

    def _get_dev_status(self) -> dict:
        """Get dev mode status from Wizard."""
        try:
            guard = self._admin_guard()
            if guard:
                return guard
            dev_guard = self._dev_templates_guard()
            if dev_guard:
                return dev_guard
            guard = self._throttle_guard("/api/dev/status")
            if guard:
                return guard
            response = http_get(
                f"http://{self.wizard_host}:{self.wizard_port}/api/dev/status",
                headers=self._headers(),
                timeout=5,
            )
            if response["status_code"] in {401, 403}:
                return self._admin_guard() or {
                    "status": "error",
                    "message": "Admin token required for dev mode",
                }
            if response["status_code"] == 412:
                return self._dev_templates_guard() or {
                    "status": "error",
                    "message": "Dev workspace missing",
                }
            result = response.get("json", {})
            if response["status_code"] >= 400:
                return {
                    "status": "error",
                    "message": result.get("detail") or result.get("message") or "Dev mode status failed",
                }
            services = result.get("services") or {}
            service_rows = [[name, str(active)] for name, active in services.items()]
            extension = result.get("extension") or {}
            framework = extension.get("framework") or {}
            output = "\n".join(
                [
                    OutputToolkit.banner("DEV MODE STATUS"),
                    OutputToolkit.table(
                        ["key", "value"],
                        [
                            ["active", str(result.get("active"))],
                            ["uptime_sec", str(result.get("uptime_seconds"))],
                            ["dev_root", str(result.get("dev_root"))],
                            ["scripts_root", str(result.get("scripts_root"))],
                            ["tests_root", str(result.get("tests_root"))],
                            ["framework_ready", str(framework.get("framework_ready"))],
                        ],
                    ),
                    "",
                    "Services:",
                    OutputToolkit.table(["service", "active"], service_rows)
                    if service_rows
                    else "No services reported.",
                ]
            )
            return {
                "status": "success",
                "message": "Dev mode status",
                "output": output,
                "state": "status",
                "active": result.get("active"),
                "uptime_seconds": result.get("uptime_seconds"),
                "dev_root": result.get("dev_root"),
                "scripts_root": result.get("scripts_root"),
                "tests_root": result.get("tests_root"),
                "services": result.get("services"),
                "extension": extension,
            }
        except HTTPError:
            return {
                "status": "wizard_offline",
                "message": "Wizard Server not running",
            }
        except Exception as exc:
            logger.error(f"[DEV] Failed to get dev status: {exc}")
            return {
                "status": "error",
                "message": str(exc),
            }

    def _restart_dev_mode(self) -> dict:
        """Restart dev mode via Wizard."""
        try:
            guard = self._admin_guard()
            if guard:
                return guard
            dev_guard = self._dev_templates_guard()
            if dev_guard:
                return dev_guard
            guard = self._throttle_guard("/api/dev/restart")
            if guard:
                return guard
            response = http_post(
                f"http://{self.wizard_host}:{self.wizard_port}/api/dev/restart",
                headers=self._headers(),
                timeout=15,
            )
            if response["status_code"] in {401, 403}:
                return self._admin_guard() or {
                    "status": "error",
                    "message": "Admin token required for dev mode",
                }
            if response["status_code"] == 412:
                return self._dev_templates_guard() or {
                    "status": "error",
                    "message": "Dev workspace missing",
                }
            if response["status_code"] == 409:
                result = response.get("json", {})
                return {
                    "status": "error",
                    "message": result.get("detail") or "Dev mode is not active",
                }
            result = response.get("json", {})
            if response["status_code"] >= 400:
                return {
                    "status": "error",
                    "message": result.get("detail") or result.get("message") or "Dev mode restart failed",
                }
            logger.info(f"[DEV] Dev mode restarted: {result.get('message')}")
            output = "\n".join(
                [
                    OutputToolkit.banner("DEV MODE RESTARTED"),
                    result.get("message", ""),
                ]
            )
            return {
                "status": "success",
                "message": result.get("message"),
                "output": output,
                "state": "restarted",
            }
        except HTTPError:
            return {
                "status": "error",
                "message": "Wizard Server not running",
            }
        except Exception as exc:
            logger.error(f"[DEV] Failed to restart dev mode: {exc}")
            return {
                "status": "error",
                "message": str(exc),
            }

    def _get_dev_logs(self, lines: int = 50) -> dict:
        """Get dev mode logs from Wizard."""
        try:
            guard = self._admin_guard()
            if guard:
                return guard
            dev_guard = self._dev_templates_guard()
            if dev_guard:
                return dev_guard
            guard = self._throttle_guard("/api/dev/logs")
            if guard:
                return guard
            response = http_get(
                f"http://{self.wizard_host}:{self.wizard_port}/api/dev/logs?lines={lines}",
                headers=self._headers(),
                timeout=5,
            )
            if response["status_code"] in {401, 403}:
                return self._admin_guard() or {
                    "status": "error",
                    "message": "Admin token required for dev mode",
                }
            if response["status_code"] == 412:
                return self._dev_templates_guard() or {
                    "status": "error",
                    "message": "Dev workspace missing",
                }
            if response["status_code"] == 409:
                result = response.get("json", {})
                return {
                    "status": "error",
                    "message": result.get("detail") or "Dev mode is not active",
                }
            result = response.get("json", {})
            if response["status_code"] >= 400:
                return {
                    "status": "error",
                    "message": result.get("detail") or result.get("message") or "Dev mode logs failed",
                }
            log_lines = result.get("logs", [])
            output = "\n".join(
                [
                    OutputToolkit.banner("DEV MODE LOGS"),
                    "\n".join(log_lines) if log_lines else "No logs available.",
                ]
            )
            return {
                "status": "success",
                "message": "Dev mode logs",
                "output": output,
                "state": "logs",
                "log_file": result.get("log_file"),
                "logs": result.get("logs", []),
                "total_lines": result.get("total_lines"),
            }
        except Exception as exc:
            logger.error(f"[DEV] Failed to get dev logs: {exc}")
            return {
                "status": "error",
                "message": str(exc),
            }

    def _get_dev_plan(self) -> dict:
        try:
            guard = self._admin_guard()
            if guard:
                return guard
            dev_guard = self._dev_templates_guard()
            if dev_guard:
                return dev_guard
            response = http_get(
                f"http://{self.wizard_host}:{self.wizard_port}/api/dev/ops/planning",
                headers=self._headers(),
                timeout=5,
            )
            if response["status_code"] in {401, 403}:
                return self._admin_guard() or {
                    "status": "error",
                    "message": "Admin token required for dev planning",
                }
            result = response.get("json", {})
            if response["status_code"] >= 400:
                return {
                    "status": "error",
                    "message": result.get("detail") or result.get("message") or "Dev planning status failed",
                }

            tasks_ledger = result.get("tasks_ledger") or {}
            workflow_plans = result.get("workflow_plans") or []
            scheduler_templates = result.get("scheduler_templates") or []
            runtime = result.get("runtime") or {}
            workflow_summary = (runtime.get("workflow_dashboard") or {}).get("summary") or {}
            scheduler = runtime.get("scheduler") or {}
            queue = scheduler.get("queue") or []
            handoff = result.get("ucode_handoff") or []

            plan_rows = []
            for item in workflow_plans:
                runtime_project = item.get("runtime_project") or {}
                plan_rows.append(
                    [
                        str(item.get("id") or ""),
                        str(item.get("step_count") or 0),
                        str(runtime_project.get("task_count") or 0),
                    ]
                )

            output = "\n".join(
                [
                    OutputToolkit.banner("DEV PLAN"),
                    OutputToolkit.table(
                        ["key", "value"],
                        [
                            ["missions", str(tasks_ledger.get("mission_count") or 0)],
                            ["workflow_plans", str(len(workflow_plans))],
                            ["scheduler_templates", str(len(scheduler_templates))],
                            ["runtime_runs", str(workflow_summary.get("runs") or 0)],
                            ["queued_tasks", str(len(queue))],
                        ],
                    ),
                    "",
                    "Workflow plans:",
                    OutputToolkit.table(["id", "steps", "runtime_tasks"], plan_rows)
                    if plan_rows
                    else "No tracked workflow plans.",
                    "",
                    "Handoff commands:",
                    "\n".join(f"- {item}" for item in handoff) if handoff else "- DEV STATUS",
                ]
            )
            return {
                "status": "success",
                "message": "Dev planning summary",
                "output": output,
                "planning": result,
            }
        except HTTPError:
            return {
                "status": "wizard_offline",
                "message": "Wizard Server not running",
            }
        except Exception as exc:
            logger.error(f"[DEV] Failed to get dev planning summary: {exc}")
            return {
                "status": "error",
                "message": str(exc),
            }

    def _sync_workflow_plan(self, rel_path: str) -> dict:
        normalized = (rel_path or "").strip()
        if not normalized:
            return {
                "status": "error",
                "message": "Workflow plan path required",
                "output": "\n".join(
                    [
                        OutputToolkit.banner("DEV SYNC"),
                        "Usage: DEV SYNC <workflow_plan.json>",
                    ]
                ),
            }
        try:
            guard = self._admin_guard()
            if guard:
                return guard
            dev_guard = self._dev_templates_guard()
            if dev_guard:
                return dev_guard
            response = http_post(
                f"http://{self.wizard_host}:{self.wizard_port}/api/dev/ops/workflows/sync",
                json_data={"path": normalized},
                headers=self._headers(),
                timeout=10,
            )
            if response["status_code"] in {401, 403}:
                return self._admin_guard() or {
                    "status": "error",
                    "message": "Admin token required for dev sync",
                }
            result = response.get("json", {})
            if response["status_code"] >= 400:
                return {
                    "status": "error",
                    "message": result.get("detail") or result.get("message") or "Dev workflow sync failed",
                }
            runtime_project = result.get("runtime_project") or {}
            output = "\n".join(
                [
                    OutputToolkit.banner("DEV SYNC"),
                    OutputToolkit.table(
                        ["key", "value"],
                        [
                            ["plan", str((result.get("plan") or {}).get("path") or normalized)],
                            ["runtime_project", str(runtime_project.get("name") or "")],
                            ["created_tasks", str(result.get("created_tasks") or 0)],
                        ],
                    ),
                ]
            )
            return {
                "status": "success",
                "message": "Workflow plan synced",
                "output": output,
                "result": result,
            }
        except HTTPError:
            return {
                "status": "wizard_offline",
                "message": "Wizard Server not running",
            }
        except Exception as exc:
            logger.error(f"[DEV] Failed to sync dev workflow plan: {exc}")
            return {
                "status": "error",
                "message": str(exc),
            }

    def _register_scheduler_template(self, template_path: str, workflow_plan: str) -> dict:
        template = (template_path or "").strip()
        workflow = (workflow_plan or "").strip()
        if not template or not workflow:
            return {
                "status": "error",
                "message": "Scheduler template and workflow plan path required",
                "output": "\n".join(
                    [
                        OutputToolkit.banner("DEV SCHEDULE"),
                        "Usage: DEV SCHEDULE <scheduler_template.json> <workflow_plan.json>",
                    ]
                ),
            }
        try:
            guard = self._admin_guard()
            if guard:
                return guard
            dev_guard = self._dev_templates_guard()
            if dev_guard:
                return dev_guard
            response = http_post(
                f"http://{self.wizard_host}:{self.wizard_port}/api/dev/ops/scheduler/register",
                json_data={"path": template, "workflow_path": workflow},
                headers=self._headers(),
                timeout=10,
            )
            result = response.get("json", {})
            if response["status_code"] >= 400:
                return {
                    "status": "error",
                    "message": result.get("detail") or result.get("message") or "Dev scheduler registration failed",
                }
            task = result.get("task") or {}
            output = "\n".join(
                [
                    OutputToolkit.banner("DEV SCHEDULE"),
                    OutputToolkit.table(
                        ["key", "value"],
                        [
                            ["template", str((result.get("scheduler_template") or {}).get("path") or template)],
                            ["workflow_plan", str(workflow)],
                            ["task_id", str(task.get("id") or task.get("task_id") or "")],
                            ["created", str(result.get("created"))],
                        ],
                    ),
                ]
            )
            return {
                "status": "success",
                "message": "Scheduler template registered",
                "output": output,
                "result": result,
            }
        except HTTPError:
            return {"status": "wizard_offline", "message": "Wizard Server not running"}
        except Exception as exc:
            logger.error(f"[DEV] Failed to register scheduler template: {exc}")
            return {"status": "error", "message": str(exc)}

    def _run_workflow_plan(self, rel_path: str) -> dict:
        normalized = (rel_path or "").strip()
        if not normalized:
            return {
                "status": "error",
                "message": "Workflow plan path required",
                "output": "\n".join(
                    [
                        OutputToolkit.banner("DEV RUN"),
                        "Usage: DEV RUN <workflow_plan.json>",
                    ]
                ),
            }
        try:
            guard = self._admin_guard()
            if guard:
                return guard
            dev_guard = self._dev_templates_guard()
            if dev_guard:
                return dev_guard
            response = http_post(
                f"http://{self.wizard_host}:{self.wizard_port}/api/dev/ops/workflows/run",
                json_data={"path": normalized},
                headers=self._headers(),
                timeout=10,
            )
            result = response.get("json", {})
            if response["status_code"] >= 400:
                return {
                    "status": "error",
                    "message": result.get("detail") or result.get("message") or "Dev workflow run failed",
                }
            run = result.get("run") or {}
            output = "\n".join(
                [
                    OutputToolkit.banner("DEV RUN"),
                    OutputToolkit.table(
                        ["key", "value"],
                        [
                            ["plan", str((result.get("plan") or {}).get("path") or normalized)],
                            ["task_id", str(run.get("task_id") or "")],
                            ["task_title", str(run.get("task_title") or "")],
                            ["task_status", str(run.get("task_status") or "")],
                        ],
                    ),
                ]
            )
            return {
                "status": "success",
                "message": "Workflow plan run requested",
                "output": output,
                "result": result,
            }
        except HTTPError:
            return {"status": "wizard_offline", "message": "Wizard Server not running"}
        except Exception as exc:
            logger.error(f"[DEV] Failed to run workflow plan: {exc}")
            return {"status": "error", "message": str(exc)}

    def _update_workflow_task(self, rel_path: str, task_id: str, status: str) -> dict:
        normalized = (rel_path or "").strip()
        task_value = (task_id or "").strip()
        status_value = (status or "").strip()
        if not normalized or not task_value or not status_value:
            return {
                "status": "error",
                "message": "Workflow plan path, task id, and status required",
                "output": "\n".join(
                    [
                        OutputToolkit.banner("DEV TASK"),
                        "Usage: DEV TASK <workflow_plan.json> <task_id> <status>",
                    ]
                ),
            }
        try:
            guard = self._admin_guard()
            if guard:
                return guard
            dev_guard = self._dev_templates_guard()
            if dev_guard:
                return dev_guard
            response = http_post(
                f"http://{self.wizard_host}:{self.wizard_port}/api/dev/ops/workflows/task-status",
                json_data={"path": normalized, "task_id": int(task_value), "status": status_value},
                headers=self._headers(),
                timeout=10,
            )
            result = response.get("json", {})
            if response["status_code"] >= 400:
                return {
                    "status": "error",
                    "message": result.get("detail") or result.get("message") or "Dev workflow task update failed",
                }
            task = result.get("task") or {}
            output = "\n".join(
                [
                    OutputToolkit.banner("DEV TASK"),
                    OutputToolkit.table(
                        ["key", "value"],
                        [
                            ["plan", str((result.get("plan") or {}).get("path") or normalized)],
                            ["task_id", str(task.get("id") or task_value)],
                            ["task_title", str(task.get("title") or "")],
                            ["task_status", str(task.get("status") or status_value)],
                        ],
                    ),
                ]
            )
            return {
                "status": "success",
                "message": "Workflow task updated",
                "output": output,
                "result": result,
            }
        except HTTPError:
            return {"status": "wizard_offline", "message": "Wizard Server not running"}
        except Exception as exc:
            logger.error(f"[DEV] Failed to update workflow task: {exc}")
            return {"status": "error", "message": str(exc)}

    def _get_dev_health(self) -> dict:
        """Get dev mode health from Wizard."""
        try:
            guard = self._admin_guard()
            if guard:
                return guard
            dev_guard = self._dev_templates_guard()
            if dev_guard:
                return dev_guard
            guard = self._throttle_guard("/api/dev/health")
            if guard:
                return guard
            response = http_get(
                f"http://{self.wizard_host}:{self.wizard_port}/api/dev/health",
                headers=self._headers(),
                timeout=5,
            )
            if response["status_code"] in {401, 403}:
                return self._admin_guard() or {
                    "status": "error",
                    "message": "Admin token required for dev mode",
                }
            if response["status_code"] == 412:
                return self._dev_templates_guard() or {
                    "status": "error",
                    "message": "Dev workspace missing",
                }
            if response["status_code"] == 409:
                result = response.get("json", {})
                return {
                    "status": "error",
                    "message": result.get("detail") or "Dev mode is not active",
                }
            result = response.get("json", {})
            if response["status_code"] >= 400:
                return {
                    "status": "error",
                    "message": result.get("detail") or result.get("message") or "Dev mode health failed",
                }
            services = result.get("services") or {}
            service_rows = [[name, str(active)] for name, active in services.items()]
            output = "\n".join(
                [
                    OutputToolkit.banner("DEV MODE HEALTH"),
                    OutputToolkit.table(
                        ["key", "value"],
                        [
                            ["healthy", str(result.get("healthy"))],
                            ["dev_active", str(result.get("status") == "active")],
                        ],
                    ),
                    "",
                    "Services:",
                    OutputToolkit.table(["service", "healthy"], service_rows)
                    if service_rows
                    else "No services reported.",
                ]
            )
            return {
                "status": "success",
                "message": "Dev mode health",
                "output": output,
                "state": "health",
                "healthy": result.get("healthy"),
                "dev_active": result.get("status") == "active",
                "services": result.get("services"),
            }
        except HTTPError:
            return {
                "status": "wizard_offline",
                "healthy": False,
                "dev_active": False,
            }
        except Exception as exc:
            logger.error(f"[DEV] Failed to get dev health: {exc}")
            return {
                "status": "error",
                "message": str(exc),
            }

    def _clear_dev_mode(self) -> dict:
        """Clear dev mode caches/rebuilds via Wizard."""
        try:
            guard = self._admin_guard()
            if guard:
                return guard
            dev_guard = self._dev_templates_guard()
            if dev_guard:
                return dev_guard
            guard = self._throttle_guard("/api/dev/clear")
            if guard:
                return guard
            response = http_post(
                f"http://{self.wizard_host}:{self.wizard_port}/api/dev/clear",
                headers=self._headers(),
                timeout=20,
            )
            if response["status_code"] in {401, 403}:
                return self._admin_guard() or {
                    "status": "error",
                    "message": "Admin token required for dev mode",
                }
            if response["status_code"] == 412:
                return self._dev_templates_guard() or {
                    "status": "error",
                    "message": "Dev workspace missing",
                }
            if response["status_code"] == 409:
                result = response.get("json", {})
                return {
                    "status": "error",
                    "message": result.get("detail") or "Dev mode is not active",
                }
            result = response.get("json", {})
            if response["status_code"] >= 400:
                return {
                    "status": "error",
                    "message": result.get("detail") or result.get("message") or "Dev mode clear failed",
                }
            return {
                "status": "success",
                "message": "Dev mode clear complete",
                "output": "\n".join(
                    [
                        OutputToolkit.banner("DEV MODE CLEAR"),
                        json.dumps(result, indent=2),
                    ]
                ),
                "state": "cleared",
            }
        except Exception as exc:
            logger.error(f"[DEV] Failed to clear dev mode: {exc}")
            return {
                "status": "error",
                "message": str(exc),
            }
