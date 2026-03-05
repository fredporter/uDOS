"""Deterministic offline runtime for promoted uLogic action graphs."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable

from .action_graph import ActionGraph, ExecutionResult
from .artifact_store import ArtifactStore
from .script_sandbox import SandboxError, ScriptSandbox
from .state_store import ULogicStateStore


CommandDispatcher = Callable[[str], dict[str, Any]]


class ULogicRuntime:
    """Execute a bounded deterministic action graph against local state."""

    def __init__(
        self,
        project_root: Path,
        vault_root: Path,
        *,
        command_dispatcher: CommandDispatcher | None = None,
        state_store: ULogicStateStore | None = None,
        artifact_store: ArtifactStore | None = None,
        sandbox: ScriptSandbox | None = None,
    ) -> None:
        self.project_root = Path(project_root)
        self.vault_root = Path(vault_root)
        self.command_dispatcher = command_dispatcher
        self.state_store = state_store or ULogicStateStore(self.project_root)
        self.artifact_store = artifact_store or ArtifactStore(self.vault_root)
        self.sandbox = sandbox or ScriptSandbox(self.project_root)

    def run_graph(self, workflow_id: str, graph: ActionGraph) -> dict[str, Any]:
        completed: set[str] = set()
        results: list[ExecutionResult] = []

        for node in graph.actions:
            missing = [dependency for dependency in node.depends_on if dependency not in completed]
            if missing:
                results.append(
                    ExecutionResult(
                        ok=False,
                        node_id=node.id,
                        action_type=node.action_type,
                        errors=(f"Missing dependencies: {', '.join(missing)}",),
                    )
                )
                continue

            result = self._execute_node(workflow_id, node.id, node.action_type, node.payload)
            results.append(result)
            if result.ok:
                completed.add(node.id)

        overall_ok = all(result.ok for result in results)
        self.state_store.append_completed(
            {
                "id": f"workflow:{workflow_id}",
                "type": "workflow",
                "timestamp": self.state_store.now_iso(),
                "ok": overall_ok,
                "plan_id": graph.plan_id,
                "evidence": [result.output for result in results if result.output],
                "results": [asdict(result) for result in results],
            }
        )
        return {
            "ok": overall_ok,
            "workflow_id": workflow_id,
            "plan_id": graph.plan_id,
            "results": [asdict(result) for result in results],
        }

    def _execute_node(
        self,
        workflow_id: str,
        node_id: str,
        action_type: str,
        payload: dict[str, Any],
    ) -> ExecutionResult:
        try:
            if action_type == "write_text":
                path = self.artifact_store.write_text(
                    workflow_id,
                    str(payload["relpath"]),
                    str(payload.get("text", "")),
                )
                return ExecutionResult(
                    ok=True,
                    node_id=node_id,
                    action_type=action_type,
                    output=str(path),
                )
            if action_type == "write_json":
                path = self.artifact_store.write_json(
                    workflow_id,
                    str(payload["relpath"]),
                    dict(payload.get("obj") or {}),
                )
                return ExecutionResult(
                    ok=True,
                    node_id=node_id,
                    action_type=action_type,
                    output=str(path),
                )
            if action_type == "run_script":
                output = self.sandbox.run_script(
                    str(payload["path"]),
                    timeout_seconds=int(payload.get("timeout_seconds") or 60),
                )
                return ExecutionResult(
                    ok=True,
                    node_id=node_id,
                    action_type=action_type,
                    output=output,
                )
            if action_type == "ucode_command":
                if self.command_dispatcher is None:
                    raise ValueError("ucode_command action requires a command_dispatcher")
                command_text = str(payload["command_text"])
                command_result = self.command_dispatcher(command_text)
                return ExecutionResult(
                    ok=True,
                    node_id=node_id,
                    action_type=action_type,
                    output=str(command_result.get("output") or command_result.get("message") or command_result),
                    meta={"command_result": command_result},
                )
            raise ValueError(f"Unsupported action type: {action_type}")
        except (KeyError, SandboxError, ValueError) as exc:
            return ExecutionResult(
                ok=False,
                node_id=node_id,
                action_type=action_type,
                errors=(str(exc),),
            )
