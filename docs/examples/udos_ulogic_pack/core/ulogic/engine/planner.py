from __future__ import annotations
from typing import List
from .contracts import MissionSpec, ActionGraph, ActionNode

def build_plan_from_mission(mission: MissionSpec) -> ActionGraph:
    actions: List[ActionNode] = []
    prev = None
    for step in mission.steps:
        node_id = f"s{step.index}"
        payload = {"action": step.action, "target": step.target, "params": step.params, "outputs": step.outputs, "verify": step.verify}
        actions.append(ActionNode(id=node_id, type=f"mission.{step.action.lower()}", payload=payload, depends_on=[prev] if prev else [], gates=step.gates))
        prev = node_id
    return ActionGraph(plan_id=f"plan:{mission.mission_id}", actions=actions)
