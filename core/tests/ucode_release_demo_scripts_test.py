from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_ROOT = REPO_ROOT / "docs" / "examples" / "ucode_v1_5_release_pack" / "scripts"


def _load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_demo_00_script_builds_status_report(tmp_path):
    module = _load_module(SCRIPTS_ROOT / "run_demo_00_setup_and_status.py")
    output_path = tmp_path / "demo-00.json"
    runtime_root = tmp_path / "demo-00-runtime"

    report_path = module.build_report(output_path=output_path, runtime_root=runtime_root)
    payload = json.loads(report_path.read_text(encoding="utf-8"))

    assert payload["demo"] == "00-setup-and-status"
    assert payload["logic_status"]["logic"]["network"]["blocked_by_quota"] == ["mistral"]
    assert "managed_operations" in payload["ops_config"]
    assert "managed_operations" in payload["ops_jobs"]["runtime"]


def test_demo_03_script_builds_managed_operations_report(tmp_path):
    module = _load_module(SCRIPTS_ROOT / "run_demo_03_managed_scheduler_and_budget.py")
    output_path = tmp_path / "demo-03.json"
    runtime_root = tmp_path / "demo-03-runtime"

    report_path = module.build_report(output_path=output_path, runtime_root=runtime_root)
    payload = json.loads(report_path.read_text(encoding="utf-8"))

    assert payload["demo"] == "03-managed-scheduler-and-budget"
    assert payload["run_result"]["deferred"] == 1
    assert payload["queue"][0]["defer_reason"] == "api_budget_exhausted"
    assert payload["logic_status"]["logic"]["network"]["blocked_by_quota"] == ["openai"]
    assert payload["planning_overview"]["runtime"]["managed_operations"]["cloud_execution"]["blocked_by_quota"] == [
        "openai"
    ]


def test_demo_01_script_builds_local_assist_report(tmp_path):
    module = _load_module(SCRIPTS_ROOT / "run_demo_01_local_assist_and_knowledge.py")
    output_path = tmp_path / "demo-01.json"
    runtime_root = tmp_path / "demo-01-runtime"

    report_path = module.build_report(output_path=output_path, runtime_root=runtime_root)
    payload = json.loads(report_path.read_text(encoding="utf-8"))

    assert payload["demo"] == "01-local-assist-and-knowledge"
    assert payload["status"]["local"]["ready"] is True
    assert payload["response"]["route"]["source"] == "local"
    assert payload["conversation_exists"] is True
    assert "Prefer OK Assistant terminology" in payload["local_calls"][0]["system"]


def test_demo_02_script_builds_workflow_report(tmp_path):
    module = _load_module(SCRIPTS_ROOT / "run_demo_02_workflow_and_task_planning.py")
    output_path = tmp_path / "demo-02.json"
    runtime_root = tmp_path / "demo-02-runtime"

    report_path = module.build_report(output_path=output_path, runtime_root=runtime_root)
    payload = json.loads(report_path.read_text(encoding="utf-8"))

    assert payload["demo"] == "02-workflow-and-task-planning"
    assert payload["first_state"] == "awaiting_approval"
    assert "01-outline.md" in payload["artifacts"]
    assert payload["second_status"]["state"]["current_phase_index"] >= 1


def test_demo_04_script_builds_self_hosted_dev_report(tmp_path):
    module = _load_module(SCRIPTS_ROOT / "run_demo_04_self_hosted_dev_mode.py")
    output_path = tmp_path / "demo-04.json"
    runtime_root = tmp_path / "demo-04-runtime"

    report_path = module.build_report(output_path=output_path, runtime_root=runtime_root)
    payload = json.loads(report_path.read_text(encoding="utf-8"))

    assert payload["demo"] == "04-self-hosted-dev-mode"
    assert payload["planning"]["status"] == "ok"
    assert payload["sync"]["status"] == "ok"
    assert payload["schedule"]["status"] == "ok"
    assert payload["run"]["status"] == "ok"
    assert payload["update"]["task"]["status"] == "completed"


def test_demo_05_script_builds_grid_rendering_report(tmp_path):
    module = _load_module(SCRIPTS_ROOT / "run_demo_05_grid_and_view_rendering.py")
    output_path = tmp_path / "demo-05.json"
    runtime_root = tmp_path / "demo-05-runtime"

    report_path = module.build_report(output_path=output_path, runtime_root=runtime_root)
    payload = json.loads(report_path.read_text(encoding="utf-8"))

    assert payload["demo"] == "05-grid-and-view-rendering"
    assert payload["character_model"]["ascii_safe_default"] is True
    views = {item["view"] for item in payload["view_matrix"]}
    assert {"text", "columns", "ascii", "teletext", "calendar", "task", "grid", "container"}.issubset(views)


def test_demo_06_script_builds_onboarding_report(tmp_path):
    module = _load_module(SCRIPTS_ROOT / "run_demo_06_ghost_to_wizard_onboarding.py")
    output_path = tmp_path / "demo-06.json"
    runtime_root = tmp_path / "demo-06-runtime"

    report_path = module.build_report(output_path=output_path, runtime_root=runtime_root)
    payload = json.loads(report_path.read_text(encoding="utf-8"))

    assert payload["demo"] == "06-ghost-to-wizard-onboarding"
    assert payload["mission_script_exists"] is True
    assert payload["final_state"]["role"] == "wizard"
    assert payload["level_sequence"][0] == "awakening_chamber"
    assert payload["level_sequence"][-1] == "surface"


def test_demo_07_script_builds_layer_mapping_report(tmp_path):
    module = _load_module(SCRIPTS_ROOT / "run_demo_07_layer_mapping_and_z_index.py")
    output_path = tmp_path / "demo-07.json"
    runtime_root = tmp_path / "demo-07-runtime"

    report_path = module.build_report(output_path=output_path, runtime_root=runtime_root)
    payload = json.loads(report_path.read_text(encoding="utf-8"))

    assert payload["demo"] == "07-layer-mapping-and-z-index"
    assert payload["z_policy"]["dungeon"] == "z < 0"
    assert any(item["lane"] == "galaxy" for item in payload["sample_mapping"])


def test_demo_08_script_builds_seed_library_report(tmp_path):
    module = _load_module(SCRIPTS_ROOT / "run_demo_08_seed_library_generation.py")
    output_path = tmp_path / "demo-08.json"
    runtime_root = tmp_path / "demo-08-runtime"

    report_path = module.build_report(output_path=output_path, runtime_root=runtime_root)
    payload = json.loads(report_path.read_text(encoding="utf-8"))

    assert payload["demo"] == "08-seed-library-generation"
    assert payload["paths_exist"]["seed_root"] is True
    assert payload["counts"]["themes"] > 0
    assert payload["counts"]["diagrams_ascii"] > 0


def test_demo_09_script_builds_repair_and_extension_report(tmp_path):
    module = _load_module(SCRIPTS_ROOT / "run_demo_09_dev_mode_repair_and_self_extension.py")
    output_path = tmp_path / "demo-09.json"
    runtime_root = tmp_path / "demo-09-runtime"

    report_path = module.build_report(output_path=output_path, runtime_root=runtime_root)
    payload = json.loads(report_path.read_text(encoding="utf-8"))

    assert payload["demo"] == "09-dev-mode-repair-and-self-extension"
    assert payload["repair"]["dry_run"]["status"] == "ok"
    assert payload["extension"]["enabled"] is True
    assert payload["cloud_code_agent_lane"]["policy_gated"] is True


def test_demo_scripts_run_from_cli_entrypoints(tmp_path):
    scripts = [
        ("run_demo_00_setup_and_status.py", "00-setup-and-status"),
        ("run_demo_01_local_assist_and_knowledge.py", "01-local-assist-and-knowledge"),
        ("run_demo_02_workflow_and_task_planning.py", "02-workflow-and-task-planning"),
        ("run_demo_03_managed_scheduler_and_budget.py", "03-managed-scheduler-and-budget"),
        ("run_demo_04_self_hosted_dev_mode.py", "04-self-hosted-dev-mode"),
        ("run_demo_05_grid_and_view_rendering.py", "05-grid-and-view-rendering"),
        ("run_demo_06_ghost_to_wizard_onboarding.py", "06-ghost-to-wizard-onboarding"),
        ("run_demo_07_layer_mapping_and_z_index.py", "07-layer-mapping-and-z-index"),
        ("run_demo_08_seed_library_generation.py", "08-seed-library-generation"),
        ("run_demo_09_dev_mode_repair_and_self_extension.py", "09-dev-mode-repair-and-self-extension"),
    ]

    for script_name, demo_id in scripts:
        output_path = tmp_path / f"{demo_id}.json"
        runtime_root = tmp_path / f"{demo_id}-runtime"
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_ROOT / script_name),
                "--output",
                str(output_path),
                "--runtime-root",
                str(runtime_root),
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        payload = json.loads(output_path.read_text(encoding="utf-8"))
        assert payload["demo"] == demo_id
        assert result.stdout.strip() == str(output_path)
