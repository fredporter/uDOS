from __future__ import annotations
from typing import Any, Dict, List
from .contracts import ActionGraph, ActorContext
from ..gameplay.metrics import MetricsStore
from ..gameplay.rules import GateEvaluator

def validate_plan(graph: ActionGraph, actor: ActorContext, project: Dict[str, Any], metrics: MetricsStore, gate_eval: GateEvaluator) -> List[str]:
    errors: List[str] = []
    constraints = project.get("constraints", {}) or {}
    if actor.allow_destructive and not bool(constraints.get("destructive_commands", False)):
        errors.append("actor_requested_destructive_but_project_forbids")

    snap = metrics.snapshot()
    for node in graph.actions:
        for gate in node.gates:
            ok, reason = gate_eval.evaluate(gate.expr, snap)
            if not ok:
                errors.append(f"gate_blocked:{gate.name}:{reason}")
    return errors
