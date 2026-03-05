from __future__ import annotations

import json

from core.ulogic import (
    ActionGraph,
    ActionNode,
    ScriptSandbox,
    ULogicRuntime,
    ULogicStateStore,
)


def test_ulogic_runtime_writes_artifacts_and_records_completion(tmp_path) -> None:
    runtime = ULogicRuntime(
        project_root=tmp_path / "project",
        vault_root=tmp_path / "vault",
    )

    result = runtime.run_graph(
        "wf-001",
        ActionGraph(
            plan_id="plan-001",
            actions=(
                ActionNode(
                    id="write-note",
                    action_type="write_text",
                    payload={"relpath": "notes/summary.md", "text": "# Summary"},
                ),
                ActionNode(
                    id="write-json",
                    action_type="write_json",
                    payload={"relpath": "data/state.json", "obj": {"ready": True}},
                    depends_on=("write-note",),
                ),
            ),
        ),
    )

    assert result["ok"] is True
    assert (tmp_path / "vault" / "workflows" / "wf-001" / "notes" / "summary.md").read_text(encoding="utf-8") == "# Summary"
    payload = json.loads(
        (tmp_path / "vault" / "workflows" / "wf-001" / "data" / "state.json").read_text(encoding="utf-8")
    )
    assert payload == {"ready": True}
    completed = ULogicStateStore(tmp_path / "project").load_completed()
    assert completed["completed"][0]["plan_id"] == "plan-001"


def test_ulogic_runtime_runs_script_with_bounded_sandbox(tmp_path) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir(parents=True, exist_ok=True)
    (project_root / "hello.py").write_text("print('hello runtime')\n", encoding="utf-8")

    sandbox = ScriptSandbox(project_root)
    output = sandbox.run_script("hello.py")

    assert "[SANDBOX EXIT 0]" in output
    assert "hello runtime" in output


def test_ulogic_runtime_dispatches_ucode_command(tmp_path) -> None:
    calls: list[str] = []

    def _dispatch(command_text: str) -> dict[str, str]:
        calls.append(command_text)
        return {"status": "success", "output": "WORKFLOW STATUS wf-001"}

    runtime = ULogicRuntime(
        project_root=tmp_path / "project",
        vault_root=tmp_path / "vault",
        command_dispatcher=_dispatch,
    )
    result = runtime.run_graph(
        "wf-001",
        ActionGraph(
            plan_id="plan-command",
            actions=(
                ActionNode(
                    id="command",
                    action_type="ucode_command",
                    payload={"command_text": "WORKFLOW STATUS wf-001"},
                ),
            ),
        ),
    )

    assert result["ok"] is True
    assert calls == ["WORKFLOW STATUS wf-001"]
    assert result["results"][0]["meta"]["command_result"]["status"] == "success"


def test_ulogic_runtime_blocks_missing_dependencies(tmp_path) -> None:
    runtime = ULogicRuntime(
        project_root=tmp_path / "project",
        vault_root=tmp_path / "vault",
    )

    result = runtime.run_graph(
        "wf-002",
        ActionGraph(
            plan_id="plan-002",
            actions=(
                ActionNode(
                    id="dependent",
                    action_type="write_text",
                    payload={"relpath": "notes/blocked.md", "text": "blocked"},
                    depends_on=("missing-step",),
                ),
            ),
        ),
    )

    assert result["ok"] is False
    assert "Missing dependencies" in result["results"][0]["errors"][0]
