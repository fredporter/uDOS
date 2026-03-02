from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class EscalationRule:
    """When validation fails, we can escalate tier."""
    max_escalations: int = 2
    retry_same_tier: int = 0  # retries before escalating


@dataclass
class EscalationState:
    escalations_used: int = 0
    retries_used: int = 0

    def should_retry_same_tier(self, rule: EscalationRule) -> bool:
        return self.retries_used < rule.retry_same_tier

    def should_escalate(self, rule: EscalationRule) -> bool:
        return self.escalations_used < rule.max_escalations

    def on_retry(self) -> None:
        self.retries_used += 1

    def on_escalate(self) -> None:
        self.escalations_used += 1
        self.retries_used = 0


def summarize_errors(errors: List[str]) -> str:
    if not errors:
        return "OK"
    return "; ".join(errors[:6]) + (" ..." if len(errors) > 6 else "")
