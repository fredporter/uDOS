"""
Task scheduling routes for Wizard Server.
"""

import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Callable, Awaitable, Optional, Dict, Any, List, Tuple

from fastapi import APIRouter, HTTPException, Request, Query, Body
from pydantic import BaseModel

from core.services.prompt_parser_service import get_prompt_parser_service
from core.services.todo_reminder_service import get_reminder_service
from core.services.todo_service import (
    CalendarGridRenderer,
    GanttGridRenderer,
    get_service,
)
from wizard.services.task_scheduler import TaskScheduler
from wizard.services.path_utils import get_repo_root, get_vault_md_root

AuthGuard = Optional[Callable[[Request], Awaitable[str]]]


def create_task_routes(auth_guard: AuthGuard = None) -> APIRouter:
    router = APIRouter(prefix="/api/tasks", tags=["task-scheduler"])
    scheduler = TaskScheduler()
    todo_manager = get_service()
    calendar_renderer = CalendarGridRenderer()
    gantt_renderer = GanttGridRenderer()
    prompt_parser = get_prompt_parser_service()
    reminder_service = get_reminder_service(todo_manager)

    def _vault_root() -> Path:
        return get_vault_md_root()

    def _tasks_db_path() -> Path:
        return _vault_root() / ".udos" / "state.db"

    def _task_indexer_cli() -> Path:
        return get_repo_root() / "core" / "dist" / "tasks" / "cli.js"

    indexer_cache: Dict[str, Tuple[float, Any]] = {}
    search_cache: Dict[Tuple[Optional[str], Optional[str], Optional[str], Optional[int]], Tuple[float, Any]] = {}
    cache_ttl_seconds = 5.0

    def _cache_get(cache_key: str) -> Optional[Any]:
        entry = indexer_cache.get(cache_key)
        if not entry:
            return None
        timestamp, payload = entry
        if (time.time() - timestamp) > cache_ttl_seconds:
            indexer_cache.pop(cache_key, None)
            return None
        return payload

    def _cache_set(cache_key: str, payload: Any) -> None:
        indexer_cache[cache_key] = (time.time(), payload)

    def _search_cache_get(
        key: Tuple[Optional[str], Optional[str], Optional[str], Optional[int]]
    ) -> Optional[Any]:
        entry = search_cache.get(key)
        if not entry:
            return None
        timestamp, payload = entry
        if (time.time() - timestamp) > cache_ttl_seconds:
            search_cache.pop(key, None)
            return None
        return payload

    def _search_cache_set(
        key: Tuple[Optional[str], Optional[str], Optional[str], Optional[int]],
        payload: Any,
    ) -> None:
        search_cache[key] = (time.time(), payload)

    def _parse_json_lines(stdout: str) -> List[Dict[str, Any]]:
        payloads: List[Dict[str, Any]] = []
        for line in stdout.splitlines():
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                payloads.append(json.loads(line))
            except Exception:
                continue
        return payloads

    def _run_task_indexer(args: List[str], env: Dict[str, str]) -> Dict[str, Any]:
        cli_path = _task_indexer_cli()
        if not cli_path.exists():
            raise HTTPException(
                status_code=500,
                detail="Task indexer binary missing; run npm run build under core.",
            )

        result = subprocess.run(
            ["node", str(cli_path), *args],
            capture_output=True,
            text=True,
            env=env,
        )
        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Task indexer failed: {result.stderr.strip()}",
            )

        payloads = _parse_json_lines(result.stdout)
        return {
            "payloads": payloads,
            "stdout": result.stdout.strip(),
        }

    class TaskCreate(BaseModel):
        name: str
        description: Optional[str] = None
        cron_expression: str
        provider: Optional[str] = None
        enabled: bool = True
        priority: int = 5
        need: int = 5
        mission: Optional[str] = None
        objective: Optional[str] = None
        resource_cost: int = 1
        requires_network: bool = False
        kind: Optional[str] = None
        payload: Optional[dict] = None

    @router.get("/health")
    async def health_check(request: Request):
        if auth_guard:
            await auth_guard(request)
        return {"status": "ok", "scheduler": "ready"}

    @router.post("/schedule")
    async def schedule_task(request: Request, task: TaskCreate):
        if auth_guard:
            await auth_guard(request)
        try:
            return scheduler.create_task(
                name=task.name,
                description=task.description,
                schedule=task.cron_expression,
                provider=task.provider,
                enabled=task.enabled,
                priority=task.priority,
                need=task.need,
                mission=task.mission,
                objective=task.objective,
                resource_cost=task.resource_cost,
                requires_network=task.requires_network,
                kind=task.kind,
                payload=task.payload,
            )
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @router.get("/queue")
    async def get_queue(request: Request):
        if auth_guard:
            await auth_guard(request)
        try:
            return scheduler.get_scheduled_queue()
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/status")
    async def get_status(request: Request, limit: int = 20):
        if auth_guard:
            await auth_guard(request)
        try:
            return {
                "stats": scheduler.get_stats(),
                "queue": scheduler.get_scheduled_queue(limit=limit),
                "settings": scheduler.get_settings(),
            }
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    class SchedulerSettings(BaseModel):
        max_tasks_per_tick: Optional[int] = None
        tick_seconds: Optional[int] = None
        allow_network: Optional[bool] = None

    class PromptPayload(BaseModel):
        text: str
        calendar_view: Optional[str] = "weekly"
        start_date: Optional[str] = None
        calendar_format: Optional[str] = "text"
        gantt_window_days: Optional[int] = 30
        gantt_format: Optional[str] = "text"

    class IndexerRunPayload(BaseModel):
        mission_id: Optional[str] = None

    @router.post("/settings")
    async def update_settings(request: Request, payload: SchedulerSettings):
        if auth_guard:
            await auth_guard(request)
        try:
            updates = payload.dict(exclude_unset=True)
            return {"success": True, "settings": scheduler.update_settings(updates)}
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/runs")
    async def get_runs(request: Request, limit: int = 50):
        if auth_guard:
            await auth_guard(request)
        try:
            return scheduler.get_execution_history(limit)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/runs/{task_id}")
    async def get_task_runs(request: Request, task_id: str, limit: int = 20):
        if auth_guard:
            await auth_guard(request)
        try:
            return scheduler.get_task_runs(task_id, limit)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/task/{task_id}")
    async def get_task(request: Request, task_id: str):
        if auth_guard:
            await auth_guard(request)
        task = scheduler.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

    @router.post("/execute/{task_id}")
    async def execute_task(request: Request, task_id: str):
        if auth_guard:
            await auth_guard(request)
        try:
            return scheduler.execute_task(task_id)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/calendar")
    async def get_calendar(
        request: Request,
        view: str = "weekly",
        start_date: Optional[str] = None,
        format: str = "text",
    ):
        if auth_guard:
            await auth_guard(request)
        try:
            parsed = (
                datetime.fromisoformat(start_date)
                if start_date
                else None
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format")

        lines = calendar_renderer.render_calendar(
            todo_manager.list_pending(), view=view, start_date=parsed
        )
        if format == "json":
            return {"view": view, "lines": lines}
        return {"view": view, "output": "\n".join(lines)}

    @router.get("/gantt")
    async def get_gantt(
        request: Request,
        window_days: int = 30,
        format: str = "text",
    ):
        if auth_guard:
            await auth_guard(request)
        lines = gantt_renderer.render_gantt(
            todo_manager.list_pending(), window_days=window_days
        )
        if format == "json":
            return {"window_days": window_days, "lines": lines}
        return {"window_days": window_days, "output": "\n".join(lines)}

    @router.post("/prompt")
    async def parse_prompt(request: Request, payload: PromptPayload):
        if auth_guard:
            await auth_guard(request)
        if not payload.text.strip():
            raise HTTPException(status_code=400, detail="Provide instruction text")

        parse_result = prompt_parser.parse(payload.text)
        tasks = parse_result.get("tasks", [])
        for task in tasks:
            todo_manager.add(task)

        try:
            parsed_date = (
                datetime.fromisoformat(payload.start_date)
                if payload.start_date
                else None
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format")

        calendar_lines = calendar_renderer.render_calendar(
            todo_manager.list_pending(),
            view=payload.calendar_view,
            start_date=parsed_date,
        )
        gantt_lines = gantt_renderer.render_gantt(
            todo_manager.list_pending(),
            window_days=payload.gantt_window_days or 30,
        )
        reminder_payload = reminder_service.log_reminder(
            horizon_hours=parse_result.get("reminder", {}).get("horizon_hours")
        )

        response = {
            "instruction": {
                "id": parse_result["instruction_id"],
                "label": parse_result["instruction_label"],
                "description": parse_result["instruction_description"],
                "story_guidance": parse_result.get("story_guidance"),
                "reference_links": parse_result.get("reference_links", []),
            },
            "tasks": [task.to_notion_block() for task in tasks],
            "calendar": {
                "view": payload.calendar_view,
                "format": payload.calendar_format,
                "lines": calendar_lines,
            },
            "gantt": {
                "window_days": payload.gantt_window_days or 30,
                "format": payload.gantt_format,
                "lines": gantt_lines,
            },
            "reminder": reminder_payload,
        }

        if payload.calendar_format != "json":
            response["calendar"]["output"] = "\n".join(calendar_lines)
        if payload.gantt_format != "json":
            response["gantt"]["output"] = "\n".join(gantt_lines)

        return response

    @router.post("/indexer/run")
    async def run_task_indexer(
        request: Request,
        payload: IndexerRunPayload = Body(default=IndexerRunPayload()),
    ):
        if auth_guard:
            await auth_guard(request)

        env = os.environ.copy()
        env["VAULT_ROOT"] = str(_vault_root())
        env["DB_PATH"] = str(_tasks_db_path())
        env["RUNS_ROOT"] = str(_vault_root() / "06_RUNS")
        if payload.mission_id:
            env["MISSION_ID"] = payload.mission_id

        result = _run_task_indexer([], env)
        payloads = result["payloads"]
        report = next(
            (item for item in reversed(payloads) if item.get("runner") == "task-indexer-cli"),
            None,
        )

        return {
            "status": "completed",
            "output": report or result["stdout"],
        }

    @router.get("/indexer/summary")
    async def task_indexer_summary(request: Request):
        if auth_guard:
            await auth_guard(request)

        cached = _cache_get("summary")
        if cached is not None:
            return cached

        env = os.environ.copy()
        env["VAULT_ROOT"] = str(_vault_root())
        env["DB_PATH"] = str(_tasks_db_path())

        result = _run_task_indexer(["--summary"], env)
        payloads = result["payloads"]
        summary = next((item.get("summary") for item in payloads if "summary" in item), None)
        if not summary:
            raise HTTPException(status_code=500, detail="Task indexer summary missing")

        _cache_set("summary", summary)
        return summary

    @router.get("/indexer/search")
    async def task_indexer_search(
        request: Request,
        status: Optional[str] = Query(None),
        due: Optional[str] = Query(None),
        tag: Optional[str] = Query(None),
        priority: Optional[int] = Query(None),
    ):
        if auth_guard:
            await auth_guard(request)

        cache_key = (status, due, tag, priority)
        cached = _search_cache_get(cache_key)
        if cached is not None:
            return {"results": cached}

        env = os.environ.copy()
        env["VAULT_ROOT"] = str(_vault_root())
        env["DB_PATH"] = str(_tasks_db_path())

        args: List[str] = ["--search"]
        if status:
            args.extend(["--status", status])
        if due:
            args.extend(["--due", due])
        if tag:
            args.extend(["--tag", tag])
        if priority is not None:
            args.extend(["--priority", str(priority)])

        result = _run_task_indexer(args, env)
        payloads = result["payloads"]
        results_payload = next(
            (item.get("results") for item in payloads if "results" in item),
            None,
        )
        if results_payload is None:
            raise HTTPException(status_code=500, detail="Task indexer search missing")

        _search_cache_set(cache_key, results_payload)
        return {"results": results_payload}

    return router
