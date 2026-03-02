from __future__ import annotations
from pathlib import Path
from typing import List
from .contracts import ActionGraph, ActionNode, ExecutionResult, ActorContext
from .artifacts import ArtifactStore
from ..ucode.dispatcher import UcodeDispatcher
from ..ucode.sandbox import ScriptSandbox
from ..providers.queue import DeferredQueue
from ..providers.mcp_client import McpClient
from ..providers.ok_api import OkApiClient

class Executor:
    def __init__(self, vault_root: Path, project_root: Path):
        self.artifacts = ArtifactStore(vault_root=vault_root)
        self.ucode = UcodeDispatcher(project_root=project_root)
        self.sandbox = ScriptSandbox(project_root=project_root)
        self.queue = DeferredQueue(project_root=project_root)
        self.mcp = McpClient(queue=self.queue)
        self.ok = OkApiClient(queue=self.queue)

    def run_node(self, workflow_id: str, node: ActionNode, actor: ActorContext) -> ExecutionResult:
        payload = node.payload
        action = (payload.get("action") or "").upper()
        target = payload.get("target") or ""
        outputs = payload.get("outputs") or []

        def outpath(default):
            return outputs[0] if outputs else default

        if action in ("CREATE", "UPDATE"):
            text = f"# {action} {target}\n\nWrite the required change for `{target}`.\n"
            p = outpath(f"artifacts/{node.id}-{action.lower()}.md")
            self.artifacts.write_text(workflow_id, p, text)
            return ExecutionResult(ok=True, node_id=node.id, output=p)

        if action == "RUN":
            # RUN UCODE STATUS  OR RUN scripts/x.py
            if target.strip().upper().startswith("UCODE "):
                cmd = target.strip()[6:]
                res = self.ucode.run(cmd=cmd, actor=actor)
                p = outpath(f"logs/{node.id}-ucode.md")
                self.artifacts.write_text(workflow_id, p, res)
                return ExecutionResult(ok=True, node_id=node.id, output=p)
            res = self.sandbox.run_script(target, timeout_seconds=60)
            p = outpath(f"logs/{node.id}-script.md")
            self.artifacts.write_text(workflow_id, p, res)
            return ExecutionResult(ok=True, node_id=node.id, output=p)

        if action == "CALL":
            if target.startswith("mcp:"):
                tool = target[4:]
                rr = self.mcp.call_tool(tool, payload.get("params", {}))
                p = outpath(f"logs/{node.id}-mcp.json")
                self.artifacts.write_text(workflow_id, p, rr)
                return ExecutionResult(ok=True, node_id=node.id, output=p)
            if target.startswith("ok:"):
                endpoint = target[3:]
                rr = self.ok.call(endpoint, payload.get("params", {}))
                p = outpath(f"logs/{node.id}-ok.json")
                self.artifacts.write_text(workflow_id, p, rr)
                return ExecutionResult(ok=True, node_id=node.id, output=p)

        p = outpath(f"logs/{node.id}.md")
        self.artifacts.write_text(workflow_id, p, f"Unimplemented action: {action} {target}\n")
        return ExecutionResult(ok=False, node_id=node.id, output=p, errors=["unimplemented_action"])

    def run_graph(self, workflow_id: str, graph: ActionGraph, actor: ActorContext) -> List[ExecutionResult]:
        results: List[ExecutionResult] = []
        done = set()
        for node in graph.actions:
            for dep in node.depends_on:
                if dep and dep not in done:
                    results.append(ExecutionResult(ok=False, node_id=node.id, errors=[f"missing_dep:{dep}"]))
                    break
            else:
                r = self.run_node(workflow_id, node, actor)
                results.append(r)
                if r.ok:
                    done.add(node.id)
        return results
