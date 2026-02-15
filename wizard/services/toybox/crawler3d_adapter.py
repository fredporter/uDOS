"""PTY adapter service for 3D crawler lens runtime."""

from __future__ import annotations

import re
from typing import Any, Dict, List

import uvicorn

from .base_adapter import PTYAdapter, create_app


def parse_crawler3d_line(line: str) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []

    floor_match = re.search(r"(?:floor|depth|level)\s+(\d+)", line, re.IGNORECASE)
    if floor_match:
        events.append(
            {
                "type": "CRAWLER3D_FLOOR_REACHED",
                "payload": {"floor": int(floor_match.group(1)), "line": line},
            }
        )

    if re.search(r"(loot|treasure|found)", line, re.IGNORECASE):
        events.append({"type": "CRAWLER3D_LOOT_FOUND", "payload": {"line": line}})

    if re.search(r"(portal|stairs|exit)", line, re.IGNORECASE):
        events.append({"type": "CRAWLER3D_TRANSITION", "payload": {"line": line}})

    if re.search(r"(boss.*defeated|objective complete|quest complete)", line, re.IGNORECASE):
        events.append({"type": "CRAWLER3D_OBJECTIVE_COMPLETE", "payload": {"line": line}})

    return events


adapter = PTYAdapter(
    adapter_id="crawler3d",
    env_cmd_var="TOYBOX_CRAWLER3D_CMD",
    command_candidates=["crawler3d", "crawl3d", "dungeon3d"],
    parse_fn=parse_crawler3d_line,
)

app = create_app(adapter)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=7424)

