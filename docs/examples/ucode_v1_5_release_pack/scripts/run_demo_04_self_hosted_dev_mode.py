from __future__ import annotations

import argparse
import json
from contextlib import ExitStack
from pathlib import Path
import sys
from unittest.mock import patch

SCRIPT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_ROOT.parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

import wizard.services.dev_mode_service as dev_mode_service_module
import wizard.services.store as store_module
import wizard.services.task_scheduler as task_scheduler_module
import wizard.services.workflow_manager as workflow_manager_module
from core.services.path_service import clear_repo_root_cache

from demo_runtime import ensure_dev_demo_root, write_report
from wizard.services.dev_mode_service import DevModeService


DEFAULT_OUTPUT = Path(".artifacts/release-demos/demo-04-self-hosted-dev-mode.json")
DEFAULT_RUNTIME = Path(".artifacts/release-demos/demo-04-runtime")


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def build_report(output_path: Path = DEFAULT_OUTPUT, runtime_root: Path = DEFAULT_RUNTIME) -> Path:
    ensure_dev_demo_root(runtime_root)
    _write_json(
        runtime_root / "dev" / "ops" / "tasks.json",
        {
            "updated": "2026-03-04",
            "active_missions": [
                {
                    "id": "release-demo-pack",
                    "title": "Build release demo pack",
                    "status": "in_progress",
                    "lane": "release",
                    "priority": "high",
                }
            ],
        },
    )
    _write_json(
        runtime_root / "dev" / "ops" / "workflows" / "release-program.json",
        {
            "id": "release-program",
            "name": "Release Program",
            "workspace": "@dev",
            "steps": [
                {"id": "phase-1", "title": "Close managed budget proof", "tags": ["phase-3"]},
                {"id": "phase-2", "title": "Ship release demo pack", "tags": ["phase-4"]},
            ],
        },
    )
    _write_json(
        runtime_root / "dev" / "ops" / "scheduler" / "release-demo.json",
        {
            "id": "release-demo",
            "description": "Run release demo workflow",
            "windows": ["off_peak"],
            "sources": ["release-program.json"],
        },
    )

    store_module._STORE = None
    clear_repo_root_cache()

    with ExitStack() as stack:
        stack.enter_context(patch.object(dev_mode_service_module, "get_repo_root", lambda: runtime_root))
        stack.enter_context(patch.object(task_scheduler_module, "get_repo_root", lambda: runtime_root))
        stack.enter_context(patch.object(workflow_manager_module, "get_repo_root", lambda: runtime_root))
        stack.enter_context(patch.object(store_module, "get_repo_root", lambda: runtime_root))

        service = DevModeService(repo_root=runtime_root)
        service.ensure_requirements = lambda: None

        planning = service.get_planning_summary()
        sync = service.sync_workflow_plan("release-program.json")
        schedule = service.register_scheduler_template("release-demo.json", "release-program.json")
        run = service.run_workflow_plan("release-program.json")
        task_id = int((sync["project"]["tasks"] or [])[0]["id"])
        update = service.update_workflow_plan_task_status("release-program.json", task_id, "completed")
        status = service.get_status()

    payload = {
        "demo": "04-self-hosted-dev-mode",
        "runtime_root": str(runtime_root.resolve()),
        "planning": planning,
        "sync": sync,
        "schedule": schedule,
        "run": run,
        "update": update,
        "status": status,
    }
    return write_report(output_path, payload)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--runtime-root", default=str(DEFAULT_RUNTIME))
    args = parser.parse_args()
    path = build_report(Path(args.output), Path(args.runtime_root))
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
