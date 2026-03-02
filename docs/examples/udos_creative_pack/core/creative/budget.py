from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class BudgetLedger:
    """Tracks spend for a workflow."""
    max_total_usd: float = 0.0
    spent_usd: float = 0.0

    def can_spend(self, amount: float) -> bool:
        return (self.spent_usd + amount) <= self.max_total_usd

    def add(self, amount: float) -> None:
        self.spent_usd += amount


@dataclass(frozen=True)
class PhaseBudgetPolicy:
    max_cost_usd: float
    max_tokens: Optional[int] = None

    def enforce_max_tokens(self, suggested: int) -> Optional[int]:
        if self.max_tokens is None:
            return None
        return min(self.max_tokens, suggested)

    def within_cost(self, cost: float) -> bool:
        return cost <= self.max_cost_usd
