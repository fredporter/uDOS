from __future__ import annotations

import argparse
from pathlib import Path
import sys

SCRIPT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_ROOT.parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from core.workflows.contracts import PhaseResult
from core.workflows.scheduler import WorkflowScheduler

from demo_runtime import ensure_runtime_root, write_report


DEFAULT_OUTPUT = Path(".artifacts/release-demos/demo-02-workflow-and-task-planning.json")
DEFAULT_RUNTIME = Path(".artifacts/release-demos/demo-02-runtime")


def build_report(output_path: Path = DEFAULT_OUTPUT, runtime_root: Path = DEFAULT_RUNTIME) -> Path:
    ensure_runtime_root(runtime_root)
    source = runtime_root / "workflow-demo.md"
    source.write_text(
        "\n".join(
            [
                "# WORKFLOW: release-demo-workflow",
                "",
                "## Goal",
                "Prepare release workflow evidence",
                "",
                "## Phases",
                "1. Outline (writing/outline -> 01-outline.md)",
                "2. Draft (writing/draft -> 02-draft.md)",
            ]
        ),
        encoding="utf-8",
    )

    scheduler = WorkflowScheduler(runtime_root)
    scheduler.create_workflow_from_markdown(
        "release-demo-workflow",
        source.read_text(encoding="utf-8"),
        source_path=source,
        project="release-demo",
    )

    scheduler.engine.run_phase = lambda workflow, phase, tier: PhaseResult(
        ok=True,
        provider_id="local-demo",
        tier=tier,
        cost_usd=0.0,
        tokens=42,
        artifact_text=f"{phase.name} artifact",
    )

    first_state = scheduler.run_workflow("release-demo-workflow")
    first_status = scheduler.status("release-demo-workflow")
    approved_state = scheduler.approve_phase("release-demo-workflow")
    second_state = scheduler.run_workflow("release-demo-workflow")
    second_status = scheduler.status("release-demo-workflow")
    workflow_root = runtime_root / "memory" / "vault" / "workflows" / "release-demo-workflow"

    payload = {
        "demo": "02-workflow-and-task-planning",
        "runtime_root": str(runtime_root.resolve()),
        "first_state": first_state.status,
        "approved_state": approved_state.status,
        "second_state": second_state.status,
        "first_status": first_status,
        "second_status": second_status,
        "artifacts": sorted(str(path.relative_to(workflow_root)) for path in workflow_root.rglob("*") if path.is_file()),
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
