from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict
from .metrics import MetricsStore

@dataclass
class EffectEngine:
    metrics: MetricsStore

    def apply_rewards(self, rewards: Dict[str, Any], meta: Dict[str, Any] | None = None) -> None:
        xp = rewards.get("xp")
        if xp is not None:
            try: self.metrics.add_xp(int(xp))
            except Exception: pass

        unlock = rewards.get("unlock")
        if unlock:
            snap = self.metrics.snapshot()
            flags = set(snap.get("unlocks", []) or [])
            flags.add(str(unlock))
            self.metrics.set_metric("unlocks", sorted(flags))
