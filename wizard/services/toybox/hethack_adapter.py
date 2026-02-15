"""PTY adapter service for hethack (NetHack-class upstream runtime)."""

from __future__ import annotations

import re
from typing import Any, Dict, List

import uvicorn

from .base_adapter import PTYAdapter, create_app


def parse_hethack_line(line: str) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    if re.search(r"amulet of yendor", line, re.IGNORECASE):
        if re.search(r"pick|retrieve|obtain|wearing", line, re.IGNORECASE):
            events.append({"type": "HETHACK_AMULET_RETRIEVED", "payload": {"line": line}})
        else:
            events.append({"type": "HETHACK_AMULET_SEEN", "payload": {"line": line}})

    depth_match = re.search(r"(?:dungeon\s+level|level)\s+(\d+)", line, re.IGNORECASE)
    if depth_match:
        depth = int(depth_match.group(1))
        events.append({"type": "HETHACK_LEVEL_REACHED", "payload": {"depth": depth, "line": line}})

    if re.search(r"you die|you are dead|game over", line, re.IGNORECASE):
        events.append({"type": "HETHACK_DEATH", "payload": {"line": line}})

    return events


adapter = PTYAdapter(
    adapter_id="hethack",
    env_cmd_var="TOYBOX_HETHACK_CMD",
    command_candidates=["nethack", "hack"],
    parse_fn=parse_hethack_line,
)

app = create_app(adapter)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=7421)

