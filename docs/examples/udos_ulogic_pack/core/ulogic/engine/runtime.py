from __future__ import annotations
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict

from .contracts import ActorContext
from .state_store import UdosStateStore
from .parser_md import parse_mission_markdown
from .planner import build_plan_from_mission
from .validator import validate_plan
from .executor import Executor
from ..gameplay.metrics import MetricsStore
from ..gameplay.rules import GateEvaluator
from ..gameplay.effects import EffectEngine
from ..gameplay.telemetry import Telemetry

class ULogicRuntime:
    def __init__(self, project_root: Path, vault_root: Path):
        self.project_root = project_root
        self.vault_root = vault_root
        self.state = UdosStateStore(root=project_root)
        self.metrics = MetricsStore(project_root=project_root)
        self.gates = GateEvaluator()
        self.effects = EffectEngine(metrics=self.metrics)
        self.telemetry = Telemetry(project_root=project_root)
        self.executor = Executor(vault_root=vault_root, project_root=project_root)

    def run_mission_file(self, mission_path: Path, actor: ActorContext) -> Dict[str, Any]:
        mission_id = mission_path.stem
        mission = parse_mission_markdown(mission_id, mission_path.read_text(encoding="utf-8"))
        project = self.state.load_project()
        graph = build_plan_from_mission(mission)

        verrors = validate_plan(graph, actor, project, self.metrics, self.gates)
        if verrors:
            self.telemetry.emit("mission.blocked", {"mission_id": mission_id, "errors": verrors})
            return {"ok": False, "mission_id": mission_id, "errors": verrors}

        workflow_id = f"mission-{mission_id}"
        self.telemetry.emit("mission.started", {"mission_id": mission_id, "workflow_id": workflow_id})

        results = self.executor.run_graph(workflow_id, graph, actor)
        ok = all(r.ok for r in results)

        if ok and mission.rewards:
            self.effects.apply_rewards(mission.rewards, meta={"mission_id": mission_id})
            self.telemetry.emit("mission.rewards_applied", {"mission_id": mission_id, "rewards": mission.rewards})

        if ok:
            evidence = [r.output for r in results if r.output]
            self.state.append_completed({
                "id": f"mission:{mission_id}",
                "type": "mission",
                "timestamp": self.state.now_iso(),
                "evidence": evidence,
                "meta": {"rewards": mission.rewards},
            })
            self.telemetry.emit("mission.completed", {"mission_id": mission_id, "evidence": evidence})

        return {"ok": ok, "mission_id": mission_id, "workflow_id": workflow_id, "results": [asdict(r) for r in results]}
