"""Log reader utilities for Wizard dashboard/TUI."""

from __future__ import annotations

import json
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from wizard.services.logging_api import get_log_stats, get_logs_root


class LogReader:
    """Read and parse Wizard JSONL logs for UI consumption."""

    def read_logs(
        self, category: str = "all", limit: int = 200, level: Optional[str] = None
    ) -> Dict[str, Any]:
        log_dir = get_logs_root()
        if not log_dir.exists():
            return {
                "logs": [],
                "category": category,
                "limit": limit,
                "categories": [],
                "stats": {},
            }

        files = sorted(
            log_dir.rglob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True
        )
        categories = sorted({p.parent.name for p in files})

        selected = (category or "all").lower()
        entries: List[Dict[str, Any]] = []

        for log_file in files:
            if selected not in ("all", ""):
                if (
                    log_file.parent.name != selected
                    and log_file.stem.split("-")[0] != selected
                ):
                    continue

            for line in self._tail_file(log_file, max(limit * 3, 200)):
                parsed = self._parse_log_json(line, log_file.name)
                if not parsed:
                    continue
                if level and parsed["level"].lower() != level.lower():
                    continue
                entries.append(parsed)

        entries.sort(key=lambda e: e["timestamp_sort"], reverse=True)
        trimmed = entries[:limit]
        for entry in trimmed:
            entry.pop("timestamp_sort", None)

        return {
            "logs": trimmed,
            "category": selected,
            "limit": limit,
            "categories": categories,
            "stats": get_log_stats(),
        }

    def _tail_file(self, path: Path, max_lines: int) -> List[str]:
        buf: deque = deque(maxlen=max_lines)
        try:
            with path.open("r", encoding="utf-8", errors="ignore") as handle:
                for line in handle:
                    buf.append(line.rstrip("\n"))
        except OSError:
            return []
        return list(buf)

    def _parse_log_json(self, line: str, filename: str) -> Optional[Dict[str, Any]]:
        try:
            payload = json.loads(line)
        except Exception:
            return None

        ts_raw = payload.get("ts") or payload.get("timestamp")
        try:
            ts_dt = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
            ts_iso = ts_dt.isoformat()
        except Exception:
            ts_dt = datetime.min
            ts_iso = ts_raw or ""

        return {
            "timestamp": ts_iso,
            "timestamp_sort": ts_dt,
            "level": payload.get("level", ""),
            "category": payload.get("category", ""),
            "component": payload.get("component", ""),
            "event": payload.get("event", ""),
            "message": payload.get("msg", ""),
            "file": filename,
        }
