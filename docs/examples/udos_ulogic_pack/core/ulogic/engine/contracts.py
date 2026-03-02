from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List

@dataclass(frozen=True)
class ActorContext:
    role: str = "Operator"
    allow_destructive: bool = False

@dataclass(frozen=True)
class Gate:
    name: str
    expr: str

@dataclass
class StepSpec:
    index: int
    title: str
    action: str
    target: str
    params: Dict[str, Any] = field(default_factory=dict)
    outputs: List[str] = field(default_factory=list)
    verify: List[str] = field(default_factory=list)
    gates: List[Gate] = field(default_factory=list)

@dataclass
class MissionSpec:
    mission_id: str
    goal: str
    constraints: Dict[str, Any] = field(default_factory=dict)
    steps: List[StepSpec] = field(default_factory=list)
    rewards: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ActionNode:
    id: str
    type: str
    payload: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    gates: List[Gate] = field(default_factory=list)

@dataclass
class ActionGraph:
    plan_id: str
    actions: List[ActionNode] = field(default_factory=list)

@dataclass
class ExecutionResult:
    ok: bool
    node_id: str
    output: str = ""
    errors: List[str] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)
