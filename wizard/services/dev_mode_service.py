"""Dev Mode Service for Wizard Server.

Dev Mode is a contributor extension lane rooted at /dev.
Wizard owns the runtime logic; /dev provides the versioned framework,
governance files, and templates that gate contributor workflows.
"""

from __future__ import annotations

import json
import re
import subprocess
import time
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

from core.services.path_service import get_repo_root
from core.ulogic import describe_json_format_profile, format_json_text
from wizard.services.logging_api import get_logger
from wizard.services.workflow_manager import TaskStatus, WorkflowManager
from wizard.services.task_scheduler import TaskScheduler
from wizard.services.vibe_service import DevModeToolService
from wizard.services.ok_context_store import write_ok_context_bundle


class DevModeService:
    """Manages Wizard dev workspace mode (/dev scripts/tests)."""

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = Path(repo_root).resolve() if repo_root else get_repo_root().resolve()
        # Keep the legacy attribute name for compatibility with existing call sites.
        self.wizard_root = self.repo_root
        self.logger = get_logger("dev-mode-service")

        self.active = False
        self.start_time: Optional[float] = None
        self.services_status = {
            "dev_extension_framework": False,
            "workflow_manager": False,
            "github_service": False,
            "dashboard_watch": False,
        }

        self._dev_requirements_cache: Optional[Dict[str, Any]] = None
        self._dev_requirements_checked_at: Optional[float] = None
        self.dashboard_watch_process: Optional[subprocess.Popen] = None

    def _dev_root(self) -> Path:
        return self.wizard_root / "dev"

    def _scripts_root(self) -> Path:
        return self._dev_root() / "dev-work" / "scripts"

    def _tests_root(self) -> Path:
        return self._dev_root() / "goblin" / "tests"

    def _ops_root(self) -> Path:
        return self._dev_root() / "ops"

    def _local_tests_root(self) -> Path:
        return self._dev_root() / "testing" / "tests"

    def _sandbox_root(self) -> Path:
        return self._dev_root() / "files" / "wizard-sandbox"

    def _goblin_root(self) -> Path:
        return self._dev_root() / "goblin"

    def _docs_root(self) -> Path:
        return self._dev_root() / "docs"

    def _ops_devlog_path(self) -> Path:
        return self._ops_root() / "DEVLOG.md"

    def _ops_project_path(self) -> Path:
        return self._ops_root() / "project.json"

    def _ops_tasks_path(self) -> Path:
        return self._ops_root() / "tasks.md"

    def _ops_tasks_json_path(self) -> Path:
        return self._ops_root() / "tasks.json"

    def _ops_completed_path(self) -> Path:
        return self._ops_root() / "completed.json"

    def _roadmap_path(self) -> Path:
        return self._docs_root() / "roadmap" / "ROADMAP.md"

    def _ops_workflows_root(self) -> Path:
        return self._ops_root() / "workflows"

    def _ops_scheduler_root(self) -> Path:
        return self._ops_root() / "scheduler"

    def _decisions_root(self) -> Path:
        return self._docs_root() / "decisions"

    def _devlog_index_path(self) -> Path:
        return self._docs_root() / "devlog" / "README.md"

    def _task_index_path(self) -> Path:
        return self._docs_root() / "tasks" / "README.md"

    def get_ops_summary(self) -> Dict[str, Any]:
        requirements = self.check_requirements(force=False)
        ops_paths = {
            "root": str(self._ops_root()),
            "devlog": str(self._ops_devlog_path()),
            "project": str(self._ops_project_path()),
            "tasks": str(self._ops_tasks_path()),
            "tasks_json": str(self._ops_tasks_json_path()),
            "completed": str(self._ops_completed_path()),
            "workspace": str(self._ops_root() / "templates" / "uDOS-dev.code-workspace"),
            "copilot": str(self._ops_root() / "templates" / "copilot-instructions.md"),
            "scheduler": str(self._ops_root() / "scheduler"),
            "workflows": str(self._ops_root() / "workflows"),
            "utils": str(self._ops_root() / "utils"),
        }
        files = {
            name: {"path": path, "present": Path(path).exists()}
            for name, path in ops_paths.items()
        }
        return {
            "workspace_alias": "@dev",
            "active": self.active,
            "ops": {
                "root": ops_paths["root"],
                "files": files,
            },
            "requirements_ready": bool(requirements.get("framework_ready")),
            "tracked_sync_paths": requirements.get("tracked_sync_paths", {}),
        }

    def _framework_manifest(self) -> Path:
        return self._dev_root() / "extension.json"

    def _dev_commands_manifest(self) -> Path:
        return self._dev_root() / "docs" / "templates" / "extensions.json"

    def get_dev_commands_manifest(self) -> Dict[str, Any]:
        path = self._dev_commands_manifest()
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            return payload if isinstance(payload, dict) else {}
        except Exception:
            return {}

    def _allowed_script(self, path: Path) -> bool:
        return path.suffix.lower() in {".sh", ".py"}

    def _allowed_test(self, path: Path) -> bool:
        suffix = path.suffix.lower()
        return suffix in {".py", ".sh"} and path.name.startswith("test_")

    def _editable_text_suffixes(self) -> set[str]:
        return {
            ".md",
            ".json",
            ".txt",
            ".py",
            ".sh",
            ".yaml",
            ".yml",
            ".toml",
            ".code-workspace",
        }

    def _json_like_suffixes(self) -> set[str]:
        return {".json", ".code-workspace"}

    def _toml_like_suffixes(self) -> set[str]:
        return {".toml"}

    def _yaml_like_suffixes(self) -> set[str]:
        return {".yaml", ".yml"}

    def _python_like_suffixes(self) -> set[str]:
        return {".py"}

    def _shell_like_suffixes(self) -> set[str]:
        return {".sh"}

    def _markdown_like_suffixes(self) -> set[str]:
        return {".md"}

    def _validate_markdown_content(self, content: str) -> Optional[str]:
        fence_lines = 0
        for line in content.splitlines():
            if line.lstrip().startswith("```"):
                fence_lines += 1
        if fence_lines % 2 != 0:
            return "Markdown fenced code blocks are unbalanced"
        return None

    def _validate_shell_content(self, content: str) -> Optional[str]:
        with tempfile.NamedTemporaryFile("w", suffix=".sh", encoding="utf-8", delete=False) as handle:
            handle.write(content)
            temp_path = Path(handle.name)
        try:
            proc = subprocess.run(
                ["bash", "-n", str(temp_path)],
                capture_output=True,
                text=True,
            )
            if proc.returncode != 0:
                detail = proc.stderr.strip() or proc.stdout.strip() or "shell syntax error"
                return f"Invalid shell syntax: {detail}"
            return None
        finally:
            temp_path.unlink(missing_ok=True)

    def _validate_tracked_content(self, target: Path, content: str) -> Optional[str]:
        suffix = target.suffix.lower()

        if suffix in self._json_like_suffixes():
            try:
                result = format_json_text(content, source_path=target)
            except ValueError as exc:
                return str(exc)
            if result.errors:
                return "; ".join(result.errors)

        if suffix in self._toml_like_suffixes():
            try:
                import tomllib  # type: ignore[attr-defined]
            except ModuleNotFoundError:
                import tomli as tomllib  # type: ignore[import-not-found]
            try:
                tomllib.loads(content)
            except Exception as exc:
                return f"Invalid TOML: {exc}"

        if suffix in self._yaml_like_suffixes():
            try:
                import yaml
            except ModuleNotFoundError:
                return "YAML validation unavailable in this runtime"
            try:
                yaml.safe_load(content)
            except Exception as exc:
                return f"Invalid YAML: {exc}"

        if suffix in self._python_like_suffixes():
            try:
                compile(content, str(target), "exec")
            except SyntaxError as exc:
                return f"Invalid Python syntax at line {exc.lineno}, column {exc.offset}: {exc.msg}"

        if suffix in self._shell_like_suffixes():
            return self._validate_shell_content(content)

        if suffix in self._markdown_like_suffixes():
            return self._validate_markdown_content(content)

        return None

    def _normalize_plain_text(self, content: str) -> str:
        normalized = "\n".join(line.rstrip() for line in content.splitlines())
        if content.endswith("\n") or normalized:
            normalized += "\n"
        return normalized

    def _normalize_markdown(self, content: str) -> str:
        normalized = self._normalize_plain_text(content)
        return re.sub(r"\n{3,}", "\n\n", normalized)

    def _normalize_tracked_content(self, target: Path, content: str) -> str:
        suffix = target.suffix.lower()

        if suffix in self._json_like_suffixes():
            return format_json_text(content, source_path=target).content

        if suffix in self._toml_like_suffixes():
            try:
                import tomllib  # type: ignore[attr-defined]
            except ModuleNotFoundError:
                import tomli as tomllib  # type: ignore[import-not-found]
            try:
                import tomli_w  # type: ignore[import-not-found]
            except ModuleNotFoundError as exc:
                raise RuntimeError("TOML normalization unavailable in this runtime") from exc
            payload = tomllib.loads(content)
            normalized = tomli_w.dumps(payload)
            return normalized if normalized.endswith("\n") else normalized + "\n"

        if suffix in self._yaml_like_suffixes():
            try:
                import yaml
            except ModuleNotFoundError as exc:
                raise RuntimeError("YAML normalization unavailable in this runtime") from exc
            payload = yaml.safe_load(content)
            normalized = yaml.safe_dump(
                payload,
                sort_keys=False,
                allow_unicode=False,
                default_flow_style=False,
            )
            return normalized if normalized.endswith("\n") else normalized + "\n"

        if suffix in self._markdown_like_suffixes():
            return self._normalize_markdown(content)

        return self._normalize_plain_text(content)

    def _format_helper_metadata(self, target: Path) -> Dict[str, Any]:
        suffix = target.suffix.lower()
        format_id = "text"
        format_label = "Text"
        validation_label = "Text safety"
        helper_action = "cleanup"
        helper_action_label = "Clean up"
        helper_result_label = "cleaned"
        helper_profile = None
        helper_profile_label = None

        if suffix in self._json_like_suffixes():
            profile = describe_json_format_profile(source_path=target)
            format_id = "json"
            format_label = profile["format_label"]
            validation_label = profile["validation_label"]
            helper_action = "format"
            helper_action_label = "Format"
            helper_result_label = "formatted"
            helper_profile = profile["profile"]
            helper_profile_label = profile["profile_label"]
        elif suffix in self._toml_like_suffixes():
            format_id = "toml"
            format_label = "TOML"
            validation_label = "TOML syntax"
            helper_action = "format"
            helper_action_label = "Format"
            helper_result_label = "formatted"
        elif suffix in self._yaml_like_suffixes():
            format_id = "yaml"
            format_label = "YAML"
            validation_label = "YAML syntax"
            helper_action = "format"
            helper_action_label = "Format"
            helper_result_label = "formatted"
        elif suffix in self._python_like_suffixes():
            format_id = "python"
            format_label = "Python"
            validation_label = "Python syntax"
        elif suffix in self._shell_like_suffixes():
            format_id = "shell"
            format_label = "Shell"
            validation_label = "Shell syntax"
        elif suffix in self._markdown_like_suffixes():
            format_id = "markdown"
            format_label = "Markdown"
            validation_label = "Fence balance"
            helper_action = "normalize"
            helper_action_label = "Normalize"
            helper_result_label = "normalized"

        can_normalize = suffix in self._editable_text_suffixes()
        return {
            "format": format_id,
            "format_label": format_label,
            "validation_label": validation_label,
            "profile": helper_profile,
            "profile_label": helper_profile_label,
            "editable": suffix in self._editable_text_suffixes(),
            "can_normalize": can_normalize,
            "helper_action": helper_action if can_normalize else None,
            "helper_action_label": helper_action_label if can_normalize else None,
            "helper_result_label": helper_result_label if can_normalize else None,
            "normalize_label": f"{helper_action_label} {format_label}" if can_normalize else None,
            "save_normalized_label": f"Save {helper_result_label} {format_label}" if can_normalize else None,
        }

    def _safe_resolve(self, root: Path, rel_path: str) -> Optional[Path]:
        if not rel_path:
            return None
        candidate = (root / rel_path).resolve()
        if not str(candidate).startswith(str(root.resolve())):
            return None
        return candidate

    def _browser_roots(self) -> Dict[str, Path]:
        return {
            "ops": self._ops_root(),
            "docs": self._docs_root(),
            "goblin": self._goblin_root(),
        }

    def _read_json_file(self, path: Path) -> Dict[str, Any] | None:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None
        return payload if isinstance(payload, dict) else None

    def _runtime_project_name(self, plan_id: str, name: str) -> str:
        label = name.strip() or plan_id.strip() or "contributor-workflow"
        return f"@dev workflow:{plan_id.strip() or 'workflow'}:{label}"

    def _coerce_workflow_plan_step(self, item: Any, index: int) -> Dict[str, Any]:
        if isinstance(item, str):
            title = item.strip()
            return {
                "step_id": title or f"step-{index + 1}",
                "title": title or f"Step {index + 1}",
                "description": "",
                "tags": [],
            }

        if isinstance(item, dict):
            step_id = str(
                item.get("step_id")
                or item.get("id")
                or item.get("name")
                or item.get("title")
                or item.get("action")
                or f"step-{index + 1}"
            ).strip()
            title = str(
                item.get("title")
                or item.get("name")
                or item.get("action")
                or step_id
                or f"Step {index + 1}"
            ).strip()
            description = str(item.get("description") or "").strip()
            tags_raw = item.get("tags") or []
            tags = [
                str(tag).strip()
                for tag in tags_raw
                if str(tag).strip()
            ] if isinstance(tags_raw, list) else []
            return {
                "step_id": step_id or f"step-{index + 1}",
                "title": title or f"Step {index + 1}",
                "description": description,
                "tags": tags,
            }

        return {
            "step_id": f"step-{index + 1}",
            "title": f"Step {index + 1}",
            "description": "",
            "tags": [],
        }

    def _load_workflow_plan(self, path: Path) -> Dict[str, Any]:
        payload = self._read_json_file(path) or {}
        steps_raw = payload.get("steps") or []
        if not isinstance(steps_raw, list):
            steps_raw = []
        steps = [
            self._coerce_workflow_plan_step(item, index)
            for index, item in enumerate(steps_raw)
        ]
        plan_id = str(payload.get("id") or path.stem.replace(".workflow", "")).strip()
        name = str(payload.get("name") or plan_id or path.stem).strip()
        artifacts = payload.get("artifacts") or []
        if not isinstance(artifacts, list):
            artifacts = []
        return {
            "id": plan_id or path.stem,
            "name": name or path.stem,
            "workspace": str(payload.get("workspace") or "@dev"),
            "artifacts": [str(item) for item in artifacts if str(item).strip()],
            "steps": steps,
            "path": path.relative_to(self._ops_root()).as_posix(),
            "source_path": str(path),
            "valid": bool(steps),
        }

    def _load_scheduler_template(self, path: Path) -> Dict[str, Any]:
        payload = self._read_json_file(path) or {}
        windows = payload.get("windows") or []
        sources = payload.get("sources") or []
        return {
            "id": str(payload.get("id") or path.stem).strip() or path.stem,
            "workspace": str(payload.get("workspace") or "@dev"),
            "description": str(payload.get("description") or "").strip(),
            "windows": [str(item) for item in windows if str(item).strip()] if isinstance(windows, list) else [],
            "sources": [str(item) for item in sources if str(item).strip()] if isinstance(sources, list) else [],
            "path": path.relative_to(self._ops_root()).as_posix(),
            "source_path": str(path),
        }

    def _load_tasks_ledger(self) -> Dict[str, Any]:
        path = self._ops_tasks_json_path()
        payload = self._read_json_file(path) or {}
        missions = payload.get("active_missions") or []
        if not isinstance(missions, list):
            missions = []
        status_counts: Dict[str, int] = {}
        normalized_missions: List[Dict[str, Any]] = []
        for item in missions:
            if not isinstance(item, dict):
                continue
            status = str(item.get("status") or "unknown").strip().lower()
            status_counts[status] = status_counts.get(status, 0) + 1
            normalized_missions.append(
                {
                    "id": str(item.get("id") or "").strip(),
                    "title": str(item.get("title") or "").strip(),
                    "status": status,
                    "lane": str(item.get("lane") or "").strip(),
                    "priority": str(item.get("priority") or "").strip(),
                }
            )
        return {
            "path": str(path),
            "updated": str(payload.get("updated") or ""),
            "mission_count": len(normalized_missions),
            "status_counts": status_counts,
            "missions": normalized_missions,
        }

    def _runtime_project_lookup(self, manager: WorkflowManager) -> Dict[str, Dict[str, Any]]:
        lookup: Dict[str, Dict[str, Any]] = {}
        for project in manager.list_projects():
            name = str(project.get("name") or "")
            if not name.startswith("@dev workflow:"):
                continue
            parts = name.split(":", 2)
            if len(parts) < 3:
                continue
            lookup[parts[1]] = project
        return lookup

    def _find_runtime_project_for_plan(
        self,
        manager: WorkflowManager,
        plan: Dict[str, Any],
    ) -> Dict[str, Any] | None:
        return self._runtime_project_lookup(manager).get(plan["id"])

    def get_planning_summary(self) -> Dict[str, Any]:
        requirements_error = self.ensure_requirements()
        if requirements_error:
            return {"status": "error", "message": requirements_error}

        manager = WorkflowManager()
        scheduler = TaskScheduler()
        project_lookup = self._runtime_project_lookup(manager)

        workflow_plans: List[Dict[str, Any]] = []
        workflows_root = self._ops_workflows_root()
        if workflows_root.exists():
            for path in sorted(workflows_root.glob("*.json")):
                plan = self._load_workflow_plan(path)
                runtime_project = project_lookup.get(plan["id"])
                runtime_summary = None
                if runtime_project:
                    project_detail = manager.get_workflow(runtime_project["id"])["workflow"]
                    runtime_summary = {
                        "id": str(runtime_project.get("id")),
                        "name": str(runtime_project.get("name") or ""),
                        "status": str(runtime_project.get("status") or "active"),
                        "task_count": len(project_detail.get("tasks") or []),
                        "tasks": project_detail.get("tasks") or [],
                    }
                workflow_plans.append(
                    {
                        **plan,
                        "step_count": len(plan["steps"]),
                        "runtime_project": runtime_summary,
                    }
                )

        scheduler_templates: List[Dict[str, Any]] = []
        scheduler_root = self._ops_scheduler_root()
        if scheduler_root.exists():
            for path in sorted(scheduler_root.glob("*.json")):
                scheduler_templates.append(self._load_scheduler_template(path))

        runtime_dashboard = manager.get_runtime_dashboard()
        scheduler_stats = scheduler.get_stats()
        scheduler_queue = scheduler.get_scheduled_queue(limit=10)

        return {
            "status": "ok",
            "workspace_alias": "@dev",
            "tasks_ledger": self._load_tasks_ledger(),
            "workflow_plans": workflow_plans,
            "scheduler_templates": scheduler_templates,
            "runtime": {
                "workflow_dashboard": runtime_dashboard,
                "scheduler": {
                    "stats": scheduler_stats,
                    "queue": scheduler_queue,
                    "settings": scheduler.get_settings(),
                },
            },
            "ucode_handoff": [
                "DEV STATUS",
                "DEV PLAN",
                "DEV SCHEDULE <template> <workflow_plan>",
                "DEV RUN <workflow_plan>",
                "DEV TASK <workflow_plan> <task_id> <status>",
                "WORKFLOW LIST",
                "WORKFLOW STATUS <workflow_id>",
            ],
        }

    def sync_workflow_plan(self, rel_path: str) -> Dict[str, Any]:
        requirements_error = self.ensure_requirements()
        if requirements_error:
            return {"status": "error", "message": requirements_error}

        target = self._safe_resolve(self._ops_workflows_root(), rel_path)
        if target is None:
            return {"status": "error", "message": f"Path not allowed: {rel_path}"}
        if not target.exists() or not target.is_file():
            return {"status": "error", "message": "Workflow plan not found"}

        plan = self._load_workflow_plan(target)
        if not plan["valid"]:
            return {"status": "error", "message": "Workflow plan has no usable steps"}

        manager = WorkflowManager()
        project_name = self._runtime_project_name(plan["id"], plan["name"])
        project_description = (
            f"Synced from @dev workflow plan {plan['path']} via Wizard Dev Mode."
        )
        project_id = manager.get_or_create_project(project_name, description=project_description)
        existing_tasks = manager.get_project_tasks(project_id)
        existing_titles = {
            str(item.get("title") or "").strip().lower()
            for item in existing_tasks
        }

        created = 0
        for index, step in enumerate(plan["steps"]):
            title = str(step.get("title") or "").strip()
            if not title or title.lower() in existing_titles:
                continue
            description_lines = [step.get("description") or ""]
            description_lines.append(f"source_plan={plan['path']}")
            description_lines.append(f"step_id={step['step_id']}")
            manager.create_task(
                project_id=project_id,
                title=title,
                description="\n".join(line for line in description_lines if line).strip(),
                priority=index + 1,
                tags=["@dev", plan["id"], *step.get("tags", [])],
            )
            existing_titles.add(title.lower())
            created += 1

        project = manager.get_workflow(project_id)["workflow"]
        self._append_dev_log(f"SYNC WORKFLOW PLAN: {plan['path']} -> project:{project_id}")
        return {
            "status": "ok",
            "workspace_alias": "@dev",
            "plan": {
                "id": plan["id"],
                "name": plan["name"],
                "path": plan["path"],
                "step_count": len(plan["steps"]),
            },
            "runtime_project": {
                "id": str(project.get("id")),
                "name": str(project.get("name") or ""),
                "status": str(project.get("status") or ""),
                "task_count": len(project.get("tasks") or []),
            },
            "created_tasks": created,
            "project": project,
        }

    def register_scheduler_template(
        self,
        rel_path: str,
        workflow_plan_path: str,
    ) -> Dict[str, Any]:
        requirements_error = self.ensure_requirements()
        if requirements_error:
            return {"status": "error", "message": requirements_error}

        template_target = self._safe_resolve(self._ops_scheduler_root(), rel_path)
        if template_target is None:
            return {"status": "error", "message": f"Path not allowed: {rel_path}"}
        if not template_target.exists() or not template_target.is_file():
            return {"status": "error", "message": "Scheduler template not found"}

        workflow_target = self._safe_resolve(self._ops_workflows_root(), workflow_plan_path)
        if workflow_target is None:
            return {"status": "error", "message": f"Path not allowed: {workflow_plan_path}"}
        if not workflow_target.exists() or not workflow_target.is_file():
            return {"status": "error", "message": "Workflow plan not found"}

        template = self._load_scheduler_template(template_target)
        plan = self._load_workflow_plan(workflow_target)
        if not plan["valid"]:
            return {"status": "error", "message": "Workflow plan has no usable steps"}

        manager = WorkflowManager()
        runtime_project = self._find_runtime_project_for_plan(manager, plan)
        if runtime_project is None:
            sync_result = self.sync_workflow_plan(workflow_plan_path)
            if sync_result.get("status") != "ok":
                return sync_result
            runtime_project = dict(sync_result["runtime_project"])

        scheduler = TaskScheduler()
        task_kind = f"dev_scheduler:{template['id']}:{runtime_project['id']}"
        existing = scheduler.get_task_by_kind(task_kind)
        if existing:
            return {
                "status": "ok",
                "workspace_alias": "@dev",
                "scheduler_template": template,
                "runtime_project": runtime_project,
                "task": existing,
                "created": False,
            }

        created = scheduler.create_task(
            name=f"@dev scheduler {template['id']}",
            description=template["description"] or f"Scheduler template {template['id']} for {plan['name']}",
            schedule="daily",
            mission=template["id"],
            objective=plan["name"],
            priority=7,
            need=7,
            resource_cost=1,
            requires_network=False,
            kind=task_kind,
            payload={
                "template_id": template["id"],
                "template_path": template["path"],
                "workflow_plan_path": plan["path"],
                "workflow_plan_id": plan["id"],
                "workflow_project_id": str(runtime_project["id"]),
                "windows": template["windows"],
                "sources": template["sources"],
                "window": "off_peak",
            },
        )
        if created.get("id"):
            scheduler.schedule_task(created["id"])
        self._append_dev_log(
            f"REGISTER SCHEDULER TEMPLATE: {template['path']} -> project:{runtime_project['id']}"
        )
        return {
            "status": "ok",
            "workspace_alias": "@dev",
            "scheduler_template": template,
            "runtime_project": runtime_project,
            "task": created,
            "created": True,
        }

    def run_workflow_plan(self, workflow_plan_path: str) -> Dict[str, Any]:
        requirements_error = self.ensure_requirements()
        if requirements_error:
            return {"status": "error", "message": requirements_error}

        workflow_target = self._safe_resolve(self._ops_workflows_root(), workflow_plan_path)
        if workflow_target is None:
            return {"status": "error", "message": f"Path not allowed: {workflow_plan_path}"}
        if not workflow_target.exists() or not workflow_target.is_file():
            return {"status": "error", "message": "Workflow plan not found"}

        plan = self._load_workflow_plan(workflow_target)
        manager = WorkflowManager()
        runtime_project = self._find_runtime_project_for_plan(manager, plan)
        if runtime_project is None:
            sync_result = self.sync_workflow_plan(workflow_plan_path)
            if sync_result.get("status") != "ok":
                return sync_result
            runtime_project = dict(sync_result["runtime_project"])

        result = manager.run_workflow(runtime_project["id"])
        project = manager.get_workflow(runtime_project["id"])["workflow"]
        self._append_dev_log(f"RUN WORKFLOW PLAN: {plan['path']} -> project:{runtime_project['id']}")
        return {
            "status": "ok",
            "workspace_alias": "@dev",
            "plan": {
                "id": plan["id"],
                "name": plan["name"],
                "path": plan["path"],
            },
            "runtime_project": {
                "id": str(project.get("id")),
                "name": str(project.get("name") or ""),
                "status": str(project.get("status") or ""),
                "task_count": len(project.get("tasks") or []),
            },
            "run": result.get("run"),
            "project": project,
        }

    def update_workflow_plan_task_status(
        self,
        workflow_plan_path: str,
        task_id: int,
        status: str,
    ) -> Dict[str, Any]:
        requirements_error = self.ensure_requirements()
        if requirements_error:
            return {"status": "error", "message": requirements_error}

        workflow_target = self._safe_resolve(self._ops_workflows_root(), workflow_plan_path)
        if workflow_target is None:
            return {"status": "error", "message": f"Path not allowed: {workflow_plan_path}"}
        if not workflow_target.exists() or not workflow_target.is_file():
            return {"status": "error", "message": "Workflow plan not found"}

        normalized = str(status or "").strip().lower().replace("_", "-")
        status_map = {
            "not-started": TaskStatus.NOT_STARTED,
            "in-progress": TaskStatus.IN_PROGRESS,
            "completed": TaskStatus.COMPLETED,
            "blocked": TaskStatus.BLOCKED,
            "deferred": TaskStatus.DEFERRED,
        }
        mapped = status_map.get(normalized)
        if mapped is None:
            return {"status": "error", "message": f"Unsupported task status: {status}"}

        plan = self._load_workflow_plan(workflow_target)
        manager = WorkflowManager()
        runtime_project = self._find_runtime_project_for_plan(manager, plan)
        if runtime_project is None:
            return {"status": "error", "message": "Workflow plan is not yet synced into runtime"}

        project = manager.get_workflow(runtime_project["id"])["workflow"]
        tasks = project.get("tasks") or []
        if not any(int(item.get("id")) == int(task_id) for item in tasks):
            return {"status": "error", "message": f"Task {task_id} not found in synced runtime project"}

        manager.update_task_status(int(task_id), mapped)
        project = manager.get_workflow(runtime_project["id"])["workflow"]
        updated_task = next(
            (item for item in (project.get("tasks") or []) if int(item.get("id")) == int(task_id)),
            None,
        )
        self._append_dev_log(
            f"UPDATE WORKFLOW TASK: {plan['path']} task:{task_id} status:{mapped.value}"
        )
        return {
            "status": "ok",
            "workspace_alias": "@dev",
            "plan": {
                "id": plan["id"],
                "name": plan["name"],
                "path": plan["path"],
            },
            "runtime_project": {
                "id": str(project.get("id")),
                "name": str(project.get("name") or ""),
                "status": str(project.get("status") or ""),
                "task_count": len(project.get("tasks") or []),
            },
            "task": updated_task,
            "project": project,
        }

    def _append_dev_log(self, message: str) -> None:
        try:
            log_dir = self.wizard_root / "memory" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_path = log_dir / "dev-mode.log"
            ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            with open(log_path, "a", encoding="utf-8") as handle:
                handle.write(f"[{ts}] {message}\n")
        except Exception:
            pass

    def check_requirements(self, force: bool = False) -> Dict[str, Any]:
        from wizard.services.dev_extension_service import get_dev_extension_service

        now = time.time()
        if (
            not force
            and self._dev_requirements_cache
            and self._dev_requirements_checked_at
            and now - self._dev_requirements_checked_at < 10
        ):
            return self._dev_requirements_cache

        dev_root = self._dev_root()
        scripts_root = self._scripts_root()
        tests_root = self._tests_root()
        local_tests_root = self._local_tests_root()
        sandbox_root = self._sandbox_root()
        framework_status = get_dev_extension_service(repo_root=self.repo_root).framework_status()
        script_count = (
            sum(1 for path in scripts_root.rglob("*") if path.is_file() and self._allowed_script(path))
            if scripts_root.exists()
            else 0
        )
        test_count = (
            sum(1 for path in tests_root.rglob("*") if path.is_file() and self._allowed_test(path))
            if tests_root.exists()
            else 0
        )

        self._dev_requirements_cache = {
            "workspace_alias": framework_status["workspace_alias"],
            "dev_root": framework_status["dev_root"],
            "dev_root_present": framework_status["dev_root_present"],
            "dev_template_present": framework_status["framework_ready"],
            "scripts_root": str(scripts_root),
            "tests_root": str(tests_root),
            "local_tests_root": str(local_tests_root),
            "sandbox_root": str(sandbox_root),
            "framework_manifest": framework_status["framework_manifest_path"],
            "framework_manifest_present": framework_status["framework_manifest_present"],
            "dev_commands_manifest": str(self._dev_commands_manifest()),
            "dev_commands_manifest_present": self._dev_commands_manifest().exists(),
            "ops_root": str(self._ops_root()),
            "script_count": script_count,
            "test_count": test_count,
            "framework_ready": framework_status["framework_ready"],
            "required_files": framework_status["required_files"],
            "missing_files": framework_status["missing_files"],
            "tracked_sync_paths": {
                "ops": str(self._ops_root()),
                "docs": str(self._docs_root()),
                "decisions": str(self._decisions_root()),
                "devlog": str(self._ops_devlog_path()),
                "project": str(self._ops_project_path()),
                "roadmap": str(self._roadmap_path()),
                "tasks": str(self._ops_tasks_path()),
                "tasks_json": str(self._ops_tasks_json_path()),
                "completed": str(self._ops_completed_path()),
                "workspace": str(self._ops_root() / "templates" / "uDOS-dev.code-workspace"),
                "copilot": str(self._ops_root() / "templates" / "copilot-instructions.md"),
                "goblin": str(self._goblin_root()),
                "goblin_tests": str(self._tests_root()),
            },
            "goblin_layers": {
                "root": str(self._goblin_root()),
                **framework_status["goblin_layers"],
                "tests": str(self._tests_root()),
            },
            "remote_framework_only": True,
            "ignored_local_paths": framework_status["local_only_dirs"],
        }
        self._dev_requirements_checked_at = now
        return self._dev_requirements_cache

    def ensure_requirements(self) -> Optional[str]:
        req = self.check_requirements(force=True)
        if not req.get("dev_root_present"):
            return "Dev extension workspace not present at /dev (`@dev`)."
        if not req.get("dev_template_present"):
            return "Dev extension workspace is missing required framework files. Update /dev from the remote dev framework."
        if not req.get("framework_manifest_present"):
            return "Dev extension manifest missing (/dev/extension.json)."
        return None

    def ensure_active(self) -> Optional[str]:
        if not self.active:
            return "Dev extension lane is inactive. Enable Dev Mode from Wizard GUI before using contributor tooling."
        return None

    def activate(self) -> Dict[str, Any]:
        requirements_error = self.ensure_requirements()
        if requirements_error:
            return {"status": "error", "message": requirements_error}

        if self.active:
            return {
                "status": "already_active",
                "message": "Dev extension lane is already active",
                "uptime_seconds": int(time.time() - self.start_time) if self.start_time else 0,
            }

        self.active = True
        self.start_time = time.time()
        self.services_status["dev_extension_framework"] = True
        self.services_status["github_service"] = True

        self._start_dashboard_watch()

        workflow = WorkflowManager()
        round_name = f"Dev Milestone {datetime.now().strftime('%Y-%m-%d')}"
        workflow.get_or_create_project(
            round_name,
            description="Auto-created when the Dev extension lane is enabled.",
        )
        self.services_status["workflow_manager"] = True

        self._append_dev_log("Dev extension lane enabled")

        return {
            "status": "activated",
            "message": "Dev extension lane enabled: /dev framework available in Wizard",
            "dev_root": str(self._dev_root()),
            "timestamp": datetime.now().isoformat(),
        }

    def clear(self) -> Dict[str, Any]:
        requirements_error = self.ensure_requirements()
        if requirements_error:
            return {"status": "error", "message": requirements_error}
        active_error = self.ensure_active()
        if active_error:
            return {"status": "error", "message": active_error}

        self.logger.info("[WIZ-DEV] Clearing dev mode caches/rebuilds...")
        results: Dict[str, Any] = {"status": "cleared", "actions": []}

        try:
            write_ok_context_bundle()
            results["actions"].append({"context": "refreshed"})
        except Exception as exc:
            results["actions"].append({"context": f"error: {exc}"})

        dashboard_dir = self.wizard_root / "wizard" / "dashboard"
        dist_path = dashboard_dir / "dist" / "index.html"
        rebuild = False
        if not dist_path.exists():
            rebuild = True
        else:
            try:
                for path in (dashboard_dir / "src").rglob("*"):
                    if path.is_file() and path.stat().st_mtime > dist_path.stat().st_mtime:
                        rebuild = True
                        break
            except Exception:
                rebuild = True

        if rebuild:
            try:
                subprocess.run(
                    ["npm", "install", "--no-fund", "--no-audit"],
                    cwd=str(dashboard_dir),
                    check=True,
                )
                subprocess.run(["npm", "run", "build"], cwd=str(dashboard_dir), check=True)
                results["actions"].append({"dashboard": "rebuilt"})
            except Exception as exc:
                results["actions"].append({"dashboard": f"error: {exc}"})

        self._append_dev_log("Dev mode clear completed")
        return results

    def _start_dashboard_watch(self) -> None:
        if self.dashboard_watch_process and self.dashboard_watch_process.poll() is None:
            return

        dashboard_dir = self.wizard_root / "wizard" / "dashboard"
        package_json = dashboard_dir / "package.json"
        if not package_json.exists():
            return

        try:
            self.dashboard_watch_process = subprocess.Popen(
                ["npm", "run", "build", "--", "--watch"],
                cwd=str(dashboard_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.services_status["dashboard_watch"] = True
            self.logger.info("[WIZ-DEV] Dashboard build watcher started")
        except Exception as exc:
            self.services_status["dashboard_watch"] = False
            self.logger.warning(f"[WIZ-DEV] Failed to start dashboard watch: {exc}")

    def suggest_next_steps(self) -> str:
        try:
            contributor_tool = DevModeToolService()
            context = contributor_tool.load_default_context()
            prompt = (
                "Suggest the next 3-5 development steps for uDOS. "
                "Consider devlog, roadmap, and recent logs."
            )
            return contributor_tool.generate(prompt=prompt, system=context)
        except Exception as exc:
            return f"Failed to generate suggestions: {exc}"

    def deactivate(self) -> Dict[str, Any]:
        if not self.active:
            return {"status": "not_active", "message": "Dev extension lane is not active"}

        try:
            if self.dashboard_watch_process:
                self.logger.info("[WIZ-DEV] Stopping dashboard watcher")
                self.dashboard_watch_process.terminate()
                try:
                    self.dashboard_watch_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.dashboard_watch_process.kill()
                    self.dashboard_watch_process.wait()

            self.active = False
            self.start_time = None
            self.dashboard_watch_process = None
            self.services_status = {k: False for k in self.services_status}
            self._append_dev_log("Dev mode deactivated")

            return {
                "status": "deactivated",
                "message": "Dev mode deactivated successfully",
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as exc:
            self.logger.error(f"[WIZ-DEV] Failed to deactivate dev mode: {exc}")
            return {"status": "error", "message": str(exc)}

    def get_status(self) -> Dict[str, Any]:
        uptime_seconds = int(time.time() - self.start_time) if self.active and self.start_time else 0
        if self.dashboard_watch_process and self.dashboard_watch_process.poll() is not None:
            self.logger.warning("[WIZ-DEV] Dashboard watch process has exited unexpectedly")
            self.dashboard_watch_process = None
            self.services_status["dashboard_watch"] = False

        requirements = self.check_requirements(force=False)

        return {
            "active": self.active,
            "uptime_seconds": uptime_seconds,
            "dev_root": str(self._dev_root()),
            "ops_root": str(self._ops_root()),
            "scripts_root": str(self._scripts_root()),
            "tests_root": str(self._tests_root()),
            "local_tests_root": str(self._local_tests_root()),
            "sandbox_root": str(self._sandbox_root()),
            "services": self.services_status,
            "requirements": requirements,
            "dev_commands": self.get_dev_commands_manifest(),
            "timestamp": datetime.now().isoformat(),
        }

    def get_logs(self, lines: int = 50) -> Dict[str, Any]:
        requirements_error = self.ensure_requirements()
        if requirements_error:
            return {"status": "error", "message": requirements_error}
        active_error = self.ensure_active()
        if active_error:
            return {"status": "error", "message": active_error}

        log_file = self.wizard_root / "memory" / "logs" / "dev-mode.log"
        logs: List[str] = []
        if log_file.exists():
            try:
                with open(log_file, "r", encoding="utf-8") as handle:
                    all_lines = handle.readlines()
                    logs = [line.rstrip() for line in all_lines[-max(0, lines):]]
            except Exception as exc:
                logs = [f"Error reading logs: {exc}"]

        return {
            "status": "running" if self.active else "inactive",
            "log_file": str(log_file),
            "logs": logs,
            "total_lines": len(logs),
        }

    def list_browser_entries(self, area: str = "ops", rel_path: str = "") -> Dict[str, Any]:
        requirements_error = self.ensure_requirements()
        if requirements_error:
            return {"status": "error", "message": requirements_error}

        root = self._browser_roots().get(area)
        if root is None:
            return {"status": "error", "message": f"Unknown area: {area}"}

        target = root if not rel_path else self._safe_resolve(root, rel_path)
        if target is None:
            return {"status": "error", "message": f"Path not allowed: {rel_path}"}
        if not target.exists():
            return {"status": "error", "message": "Path not found"}
        if not target.is_dir():
            return {"status": "error", "message": "Path is not a directory"}

        entries: List[Dict[str, Any]] = []
        for entry in sorted(target.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
            rel = entry.relative_to(root).as_posix()
            entries.append(
                {
                    "name": entry.name,
                    "path": rel,
                    "type": "dir" if entry.is_dir() else "file",
                    "size": entry.stat().st_size,
                }
            )

        return {
            "status": "ok",
            "workspace_alias": "@dev",
            "area": area,
            "root": str(root),
            "path": rel_path,
            "entries": entries,
        }

    def read_browser_file(self, area: str = "ops", rel_path: str = "") -> Dict[str, Any]:
        requirements_error = self.ensure_requirements()
        if requirements_error:
            return {"status": "error", "message": requirements_error}

        root = self._browser_roots().get(area)
        if root is None:
            return {"status": "error", "message": f"Unknown area: {area}"}

        target = self._safe_resolve(root, rel_path)
        if target is None:
            return {"status": "error", "message": f"Path not allowed: {rel_path}"}
        if not target.exists() or not target.is_file():
            return {"status": "error", "message": "File not found"}
        try:
            content = target.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return {"status": "error", "message": "File is not valid text"}

        return {
            "status": "ok",
            "workspace_alias": "@dev",
            "area": area,
            "root": str(root),
            "path": rel_path,
            "content": content,
            "format_helper": self._format_helper_metadata(target),
        }

    def write_browser_file(
        self,
        area: str = "ops",
        rel_path: str = "",
        content: str = "",
        normalize: bool = False,
    ) -> Dict[str, Any]:
        requirements_error = self.ensure_requirements()
        if requirements_error:
            return {"status": "error", "message": requirements_error}

        root = self._browser_roots().get(area)
        if root is None:
            return {"status": "error", "message": f"Unknown area: {area}"}

        target = self._safe_resolve(root, rel_path)
        if target is None:
            return {"status": "error", "message": f"Path not allowed: {rel_path}"}
        if not target.exists() or not target.is_file():
            return {"status": "error", "message": "File not found"}
        if target.suffix.lower() not in self._editable_text_suffixes():
            return {"status": "error", "message": "File type is not editable from Dev Mode"}
        if len(content.encode("utf-8")) > 1_000_000:
            return {"status": "error", "message": "File too large to edit from Dev Mode"}

        try:
            target.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return {"status": "error", "message": "File is not valid text"}

        validation_error = self._validate_tracked_content(target, content)
        if validation_error:
            return {"status": "error", "message": validation_error}

        final_content = content
        if normalize:
            try:
                final_content = self._normalize_tracked_content(target, content)
            except RuntimeError as exc:
                return {"status": "error", "message": str(exc)}

        target.write_text(final_content, encoding="utf-8")
        log_action = "FORMAT+EDIT FILE" if normalize else "EDIT FILE"
        self._append_dev_log(f"{log_action}: {area}/{rel_path}")

        return {
            "status": "ok",
            "workspace_alias": "@dev",
            "area": area,
            "root": str(root),
            "path": rel_path,
            "content": final_content,
            "saved": True,
            "normalized": normalize,
            "changed": final_content != content,
            "format_helper": self._format_helper_metadata(target),
        }

    def normalize_browser_file(
        self,
        area: str = "ops",
        rel_path: str = "",
        content: str = "",
    ) -> Dict[str, Any]:
        requirements_error = self.ensure_requirements()
        if requirements_error:
            return {"status": "error", "message": requirements_error}

        root = self._browser_roots().get(area)
        if root is None:
            return {"status": "error", "message": f"Unknown area: {area}"}

        target = self._safe_resolve(root, rel_path)
        if target is None:
            return {"status": "error", "message": f"Path not allowed: {rel_path}"}
        if not target.exists() or not target.is_file():
            return {"status": "error", "message": "File not found"}
        if target.suffix.lower() not in self._editable_text_suffixes():
            return {"status": "error", "message": "File type is not editable from Dev Mode"}

        validation_error = self._validate_tracked_content(target, content)
        if validation_error:
            return {"status": "error", "message": validation_error}

        try:
            normalized = self._normalize_tracked_content(target, content)
        except RuntimeError as exc:
            return {"status": "error", "message": str(exc)}

        return {
            "status": "ok",
            "workspace_alias": "@dev",
            "area": area,
            "root": str(root),
            "path": rel_path,
            "content": normalized,
            "changed": normalized != content,
            "format_helper": self._format_helper_metadata(target),
        }

    def restart(self) -> Dict[str, Any]:
        deactivate_result = self.deactivate()
        if deactivate_result["status"] == "error":
            return deactivate_result
        time.sleep(1)
        return self.activate()

    def get_health(self) -> Dict[str, Any]:
        requirements_error = self.ensure_requirements()
        if requirements_error:
            return {"status": "error", "healthy": False, "message": requirements_error}

        if not self.active:
            return {
                "status": "inactive",
                "healthy": False,
                "message": "Dev mode inactive. Activate to run /dev operations.",
            }

        scripts_ok = self._scripts_root().exists()
        tests_ok = self._tests_root().exists() or self._local_tests_root().exists()
        healthy = scripts_ok or tests_ok

        return {
            "status": "active",
            "healthy": healthy,
            "services": {
                "dev_workspace": {
                "status": "healthy" if healthy else "unhealthy",
                "scripts_root": str(self._scripts_root()),
                "tests_root": str(self._tests_root()),
                "local_tests_root": str(self._local_tests_root()),
                "sandbox_root": str(self._sandbox_root()),
                "framework_manifest": str(self._framework_manifest()),
            }
            },
        }

    def list_scripts(self) -> List[str]:
        if self.ensure_requirements() or self.ensure_active():
            return []
        root = self._scripts_root()
        if not root.exists():
            return []
        out: List[str] = []
        for path in sorted(root.rglob("*")):
            if path.is_file() and self._allowed_script(path):
                out.append(str(path.relative_to(root)))
        return out

    def list_tests(self) -> List[str]:
        if self.ensure_requirements() or self.ensure_active():
            return []
        root = self._tests_root()
        out: List[str] = []
        for label, base in (("goblin", self._tests_root()), ("local", self._local_tests_root())):
            if not base.exists():
                continue
            for path in sorted(base.rglob("*")):
                if path.is_file() and self._allowed_test(path):
                    rel = str(path.relative_to(base))
                    out.append(f"{label}/{rel}")
        return out

    def _resolve_test_path(self, rel_path: str) -> Optional[Path]:
        if rel_path.startswith("goblin/"):
            return self._safe_resolve(self._tests_root(), rel_path[len("goblin/"):])
        if rel_path.startswith("local/"):
            return self._safe_resolve(self._local_tests_root(), rel_path[len("local/"):])
        path = self._safe_resolve(self._tests_root(), rel_path)
        if path and path.exists():
            return path
        return self._safe_resolve(self._local_tests_root(), rel_path)

    def run_script(self, rel_path: str, args: Optional[List[str]] = None, timeout: int = 300) -> Dict[str, Any]:
        requirements_error = self.ensure_requirements()
        if requirements_error:
            return {"status": "error", "message": requirements_error}
        active_error = self.ensure_active()
        if active_error:
            return {"status": "error", "message": active_error}

        script = self._safe_resolve(self._scripts_root(), rel_path)
        if not script or not script.exists() or not script.is_file() or not self._allowed_script(script):
            return {"status": "error", "message": f"Script not allowed: {rel_path}"}

        cmd = ["python", str(script)] if script.suffix.lower() == ".py" else ["bash", str(script)]
        if args:
            cmd.extend(args)

        self._append_dev_log(f"RUN SCRIPT: {' '.join(cmd)}")
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(self.wizard_root),
                capture_output=True,
                text=True,
                timeout=max(10, timeout),
            )
            return {
                "status": "success" if proc.returncode == 0 else "error",
                "command": cmd,
                "exit_code": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
            }
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def run_tests(self, rel_path: Optional[str] = None, args: Optional[List[str]] = None, timeout: int = 600) -> Dict[str, Any]:
        requirements_error = self.ensure_requirements()
        if requirements_error:
            return {"status": "error", "message": requirements_error}
        active_error = self.ensure_active()
        if active_error:
            return {"status": "error", "message": active_error}

        args = args or []
        if rel_path:
            test_path = self._resolve_test_path(rel_path)
            if not test_path or not test_path.exists() or not test_path.is_file() or not self._allowed_test(test_path):
                return {"status": "error", "message": f"Test not allowed: {rel_path}"}

            if test_path.suffix.lower() == ".sh":
                cmd = ["bash", str(test_path)] + args
            else:
                cmd = ["python", "-m", "pytest", str(test_path)] + args
        else:
            targets: List[str] = []
            if self._tests_root().exists():
                targets.append(str(self._tests_root()))
            if self._local_tests_root().exists():
                targets.append(str(self._local_tests_root()))
            if not targets:
                return {"status": "error", "message": "No contributor tests available"}
            cmd = ["python", "-m", "pytest", *targets] + args

        self._append_dev_log(f"RUN TESTS: {' '.join(cmd)}")
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(self.wizard_root),
                capture_output=True,
                text=True,
                timeout=max(30, timeout),
            )
            return {
                "status": "success" if proc.returncode == 0 else "error",
                "command": cmd,
                "exit_code": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
            }
        except Exception as exc:
            return {"status": "error", "message": str(exc)}


_dev_mode_service: Optional[DevModeService] = None


def get_dev_mode_service(repo_root: Optional[Path] = None) -> DevModeService:
    global _dev_mode_service
    resolved_root = Path(repo_root) if repo_root else get_repo_root()
    if _dev_mode_service is None or _dev_mode_service.repo_root != resolved_root:
        _dev_mode_service = DevModeService(repo_root=resolved_root)
    return _dev_mode_service
