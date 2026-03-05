"""Deterministic action-graph contracts for offline runtime execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ActionNode:
    id: str
    action_type: str
    payload: dict[str, Any] = field(default_factory=dict)
    depends_on: tuple[str, ...] = ()


@dataclass(frozen=True)
class ActionGraph:
    plan_id: str
    actions: tuple[ActionNode, ...] = ()


@dataclass(frozen=True)
class ExecutionResult:
    ok: bool
    node_id: str
    action_type: str
    output: str = ""
    errors: tuple[str, ...] = ()
    meta: dict[str, Any] = field(default_factory=dict)
