from __future__ import annotations

import argparse
from datetime import timedelta
from pathlib import Path
import sys

SCRIPT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_ROOT.parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from core.services.time_utils import utc_now

from demo_runtime import demo_runtime, write_report
from wizard.services.task_scheduler import TaskScheduler


DEFAULT_OUTPUT = Path(".artifacts/release-demos/demo-03-managed-scheduler-and-budget.json")
DEFAULT_RUNTIME = Path(".artifacts/release-demos/demo-03-runtime")


def build_report(output_path: Path = DEFAULT_OUTPUT, runtime_root: Path = DEFAULT_RUNTIME) -> Path:
    with demo_runtime(runtime_root, blocked_provider="openai", primary_provider="mistral") as client:
        scheduler = TaskScheduler()
        scheduler.update_settings({"api_budget_daily": 10, "off_peak_start_hour": 0, "off_peak_end_hour": 23})
        scheduler._network_available = lambda: True
        task = scheduler.create_task(
            name="Release demo quota task",
            schedule="daily",
            provider="openai",
            requires_network=True,
            resource_cost=1,
            payload={"budget_units": 1, "estimated_tokens": 500},
        )
        task_id = str(task.get("id") or task.get("task_id") or "").strip()
        if not task_id:
            raise RuntimeError(f"Task scheduler create_task did not return an id: {task}")
        scheduler.schedule_task(task_id, utc_now() - timedelta(minutes=1))
        run_result = scheduler.run_pending(max_tasks=1)
        queue = scheduler.get_scheduled_queue(limit=10)

        logic = client.get("/api/ucode/logic/status").json()
        planning = client.get("/api/ops/planning/overview").json()
        config = client.get("/api/ops/config/status").json()
        deferred = client.get("/api/ops/planning/deferred/preview?reason=api_budget_exhausted&limit=10").json()

    payload = {
        "demo": "03-managed-scheduler-and-budget",
        "runtime_root": str(runtime_root.resolve()),
        "task_id": task_id,
        "run_result": run_result,
        "queue": queue,
        "logic_status": logic,
        "planning_overview": planning,
        "ops_config": config,
        "deferred_preview": deferred,
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
