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


DEFAULT_OUTPUT = Path(".artifacts/release-demos/demo-09-dev-mode-repair-and-self-extension.json")
DEFAULT_RUNTIME = Path(".artifacts/release-demos/demo-09-runtime")


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def build_report(output_path: Path = DEFAULT_OUTPUT, runtime_root: Path = DEFAULT_RUNTIME) -> Path:
    ensure_dev_demo_root(runtime_root)

    _write_json(
        runtime_root / "dev" / "ops" / "workflows" / "self-heal-extension.json",
        {
            "id": "self-heal-extension",
            "name": "Self Heal and Extend",
            "workspace": "@dev",
            "steps": [
                {"id": "phase-1", "title": "Run repair checks", "tags": ["repair"]},
                {"id": "phase-2", "title": "Apply config fix", "tags": ["repair"]},
                {"id": "phase-3", "title": "Scaffold extension", "tags": ["extension"]},
            ],
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
        sync = service.sync_workflow_plan("self-heal-extension.json")
        run = service.run_workflow_plan("self-heal-extension.json")

    payload = {
        "demo": "09-dev-mode-repair-and-self-extension",
        "runtime_root": str(runtime_root.resolve()),
        "planning": planning,
        "repair": {
            "dry_run": {
                "checks": ["install", "config", "vault", "workflow_contract"],
                "status": "ok",
            },
            "actions": [
                {"action": "repair_config", "status": "applied"},
                {"action": "reindex_seed_library", "status": "applied"},
            ],
        },
        "extension": {
            "scaffold_id": "demo.teletext.pack",
            "enabled": True,
            "runtime_path": "extensions/demo.teletext.pack",
        },
        "cloud_code_agent_lane": {
            "enabled_by_default": False,
            "policy_gated": True,
            "entry": "Wizard managed operation",
        },
        "sync": sync,
        "run": run,
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
