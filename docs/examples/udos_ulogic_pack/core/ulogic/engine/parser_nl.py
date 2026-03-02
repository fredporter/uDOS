from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List
import re

@dataclass
class IntentFrame:
    intent: str
    slots: Dict[str, Any]
    confidence: float
    source: str = "pattern"

_PATTERNS = [
    (re.compile(r"\bstatus\b", re.I), "project.status", {}),
    (re.compile(r"\brun\s+mission\s+(\S+)", re.I), "mission.run", {"mission_id": 1}),
]

def parse_intents(text: str) -> List[IntentFrame]:
    out: List[IntentFrame] = []
    t = text.strip()
    for rx, name, slotmap in _PATTERNS:
        m = rx.search(t)
        if not m: continue
        slots: Dict[str, Any] = {}
        for k, v in slotmap.items():
            slots[k] = m.group(v) if isinstance(v, int) else v
        out.append(IntentFrame(name, slots, 0.7, "pattern"))
    if not out and t:
        out.append(IntentFrame("unknown", {"text": t}, 0.2, "pattern"))
    return out
