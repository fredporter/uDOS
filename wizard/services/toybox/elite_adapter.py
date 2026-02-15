"""PTY adapter service for elite (galaxy runtime)."""

from __future__ import annotations

import re
from typing import Any, Dict, List

import uvicorn

from .base_adapter import PTYAdapter, create_app


def parse_elite_line(line: str) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []

    if re.search(r"hyperspace|jump complete|arrived at", line, re.IGNORECASE):
        events.append({"type": "ELITE_HYPERSPACE_JUMP", "payload": {"line": line}})

    if re.search(r"docked|docking complete", line, re.IGNORECASE):
        events.append({"type": "ELITE_DOCKED", "payload": {"line": line}})

    mission_match = re.search(r"mission.*complete", line, re.IGNORECASE)
    if mission_match:
        events.append({"type": "ELITE_MISSION_COMPLETE", "payload": {"line": line}})

    profit_match = re.search(r"profit[:\s]+(-?\d+)", line, re.IGNORECASE)
    if profit_match:
        profit = int(profit_match.group(1))
        events.append({"type": "ELITE_TRADE_PROFIT", "payload": {"profit": profit, "line": line}})

    return events


adapter = PTYAdapter(
    adapter_id="elite",
    env_cmd_var="TOYBOX_ELITE_CMD",
    command_candidates=["elite", "newkind", "oolite"],
    parse_fn=parse_elite_line,
)

app = create_app(adapter)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=7422)

