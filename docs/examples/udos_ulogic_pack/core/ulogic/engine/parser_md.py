from __future__ import annotations
from typing import Any, Dict, List
import re
from .contracts import MissionSpec, StepSpec

_STEP_RE = re.compile(r"^\s*(\d+)\.\s+(\w+)\s+(.+?)\s*$")

def parse_mission_markdown(mission_id: str, text: str) -> MissionSpec:
    goal = ""
    constraints: Dict[str, Any] = {}
    rewards: Dict[str, Any] = {}
    steps: List[StepSpec] = []
    section = None
    current: StepSpec | None = None

    for raw in text.splitlines():
        line = raw.rstrip("\n")
        if line.startswith("## "):
            section = line[3:].strip().lower()
            current = None
            continue

        if section == "goal":
            if line.strip():
                goal += line.strip() + " "
            continue

        if section == "constraints":
            m = re.match(r"^\s*-\s*([^:]+)\s*:\s*(.+)\s*$", line)
            if m:
                constraints[m.group(1).strip()] = m.group(2).strip()
            continue

        if section == "rewards":
            m = re.match(r"^\s*-\s*([^:]+)\s*:\s*(.+)\s*$", line)
            if m:
                k, v = m.group(1).strip(), m.group(2).strip()
                rewards[k] = int(v) if re.fullmatch(r"\d+", v) else v
            continue

        if section == "steps":
            m = _STEP_RE.match(line)
            if m:
                idx = int(m.group(1))
                action = m.group(2).strip().upper()
                target = m.group(3).strip()
                current = StepSpec(index=idx, title=f"{action} {target}", action=action, target=target)
                steps.append(current)
                continue
            if current is not None:
                m2 = re.match(r"^\s*-\s*output\s*:\s*(.+)\s*$", line)
                if m2: current.outputs.append(m2.group(1).strip())
                m3 = re.match(r"^\s*-\s*verify\s*:\s*(.+)\s*$", line)
                if m3: current.verify.append(m3.group(1).strip())

    return MissionSpec(mission_id=mission_id, goal=goal.strip(), constraints=constraints, steps=steps, rewards=rewards)
