from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RoutingOutcome:
    route: str
    input_class: str


@dataclass(frozen=True)
class IntentFrame:
    input_class: str
    intent: str
    slots: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    source: str = "deterministic-pattern"
    requires_confirmation: bool = False

    def routing_outcome(self) -> RoutingOutcome:
        route_map = {
            "command": "dispatch.command",
            "workflow": "dispatch.workflow",
            "knowledge": "dispatch.knowledge",
            "guidance": "dispatch.guidance",
        }
        return RoutingOutcome(
            route=route_map.get(self.input_class, "dispatch.reject"),
            input_class=self.input_class,
        )
