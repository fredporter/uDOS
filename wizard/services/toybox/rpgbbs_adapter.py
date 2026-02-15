"""PTY adapter service for rpgbbs (social dungeon/BBS lens)."""

from __future__ import annotations

import re
from typing import Any, Dict, List

import uvicorn

from .base_adapter import PTYAdapter, create_app


def parse_rpgbbs_line(line: str) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []

    if re.search(r"(login|welcome|connected)", line, re.IGNORECASE):
        events.append({"type": "RPGBBS_SESSION_START", "payload": {"line": line}})

    if re.search(r"(post|message|board)", line, re.IGNORECASE):
        events.append({"type": "RPGBBS_MESSAGE_EVENT", "payload": {"line": line}})

    if re.search(r"(quest.*complete|victory|level up)", line, re.IGNORECASE):
        events.append({"type": "RPGBBS_QUEST_COMPLETE", "payload": {"line": line}})

    if re.search(r"(logout|disconnected|goodbye)", line, re.IGNORECASE):
        events.append({"type": "RPGBBS_SESSION_END", "payload": {"line": line}})

    return events


adapter = PTYAdapter(
    adapter_id="rpgbbs",
    env_cmd_var="TOYBOX_RPGBBS_CMD",
    command_candidates=["rpgbbs", "bbs", "door"],
    parse_fn=parse_rpgbbs_line,
)

app = create_app(adapter)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=7423)

