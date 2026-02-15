"""SSE formatting helpers for uCODE stream responses."""

from __future__ import annotations

import json
from typing import Dict, Generator


def sse_event(event: str, data: Dict[str, object]) -> bytes:
    payload_text = json.dumps(data)
    return f"event: {event}\ndata: {payload_text}\n\n".encode("utf-8")


def iter_text_chunks(text: str) -> Generator[str, None, None]:
    if text is None:
        return
    if "\n" in text:
        lines = text.splitlines()
        for idx, line in enumerate(lines):
            suffix = "\n" if idx < len(lines) - 1 else ""
            yield f"{line}{suffix}"
    else:
        yield text
