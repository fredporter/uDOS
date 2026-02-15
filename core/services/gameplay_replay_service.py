"""Deterministic replay harness for gameplay event streams."""

from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.services.gameplay_service import GameplayService


KNOWN_EVENT_TYPES = {
    "HETHACK_LEVEL_REACHED",
    "HETHACK_AMULET_RETRIEVED",
    "HETHACK_DEATH",
    "ELITE_HYPERSPACE_JUMP",
    "ELITE_DOCKED",
    "ELITE_MISSION_COMPLETE",
    "ELITE_TRADE_PROFIT",
    "RPGBBS_SESSION_START",
    "RPGBBS_MESSAGE_EVENT",
    "RPGBBS_QUEST_COMPLETE",
    "CRAWLER3D_FLOOR_REACHED",
    "CRAWLER3D_LOOT_FOUND",
    "CRAWLER3D_OBJECTIVE_COMPLETE",
    "MAP_ENTER",
    "MAP_TRAVERSE",
    "MAP_INSPECT",
    "MAP_INTERACT",
    "MAP_COMPLETE",
    "MAP_TICK",
}


class GameplayReplayService:
    """Replay a fixed NDJSON event stream and emit deterministic artifacts."""

    @staticmethod
    def _stable_json_obj(obj: Any) -> Any:
        if isinstance(obj, dict):
            out = {}
            for key in sorted(obj.keys()):
                value = obj[key]
                if key in {"updated_at", "completed_at", "created_at", "generated_at", "ts", "unlocked_at"}:
                    continue
                out[key] = GameplayReplayService._stable_json_obj(value)
            return out
        if isinstance(obj, list):
            return [GameplayReplayService._stable_json_obj(x) for x in obj]
        return obj

    @staticmethod
    def _checksum_json(path: Path) -> str:
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
            stable = GameplayReplayService._stable_json_obj(obj)
            payload = json.dumps(stable, sort_keys=True, separators=(",", ":")).encode("utf-8")
        except Exception:
            payload = path.read_bytes() if path.exists() else b""
        return hashlib.sha256(payload).hexdigest()

    @staticmethod
    def _load_events(path: Path) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        if not path.exists():
            return rows
        for line in path.read_text(encoding="utf-8").splitlines():
            text = line.strip()
            if not text:
                continue
            try:
                parsed = json.loads(text)
            except Exception:
                continue
            if isinstance(parsed, dict):
                rows.append(parsed)
        return rows

    def replay(
        self,
        *,
        input_events_file: Path,
        output_state_file: Path,
        output_report_file: Optional[Path] = None,
        initial_state_file: Optional[Path] = None,
        max_events_per_tick: int = 1024,
    ) -> Dict[str, Any]:
        with tempfile.TemporaryDirectory(prefix="udos-replay-") as tmp:
            work = Path(tmp)
            state_file = work / "gameplay_state.json"
            events_file = work / "events.ndjson"
            cursor_file = work / "cursor.json"

            if initial_state_file and initial_state_file.exists():
                state_file.write_text(initial_state_file.read_text(encoding="utf-8"), encoding="utf-8")

            svc = GameplayService(state_file=state_file, events_file=events_file, cursor_file=cursor_file)
            checksum_before = self._checksum_json(state_file)

            rows = self._load_events(input_events_file)
            with events_file.open("w", encoding="utf-8") as fh:
                for row in rows:
                    fh.write(json.dumps(row) + "\n")

            # Ensure deterministic user rows exist even if input events are unknown/no-op.
            usernames = sorted({str(row.get("username", "")).strip() for row in rows if str(row.get("username", "")).strip()})
            for username in usernames:
                svc.get_user_stats(username)
            if usernames:
                svc._save()  # Persist bootstrap rows for deterministic replay artifacts.

            all_results: List[Dict[str, Any]] = []
            processed_total = 0
            while True:
                tick = svc.tick("replay", max_events=max_events_per_tick)
                processed = int(tick.get("processed", 0) or 0)
                processed_total += processed
                all_results.extend(list(tick.get("events", [])))
                if processed == 0:
                    break

            state_json = json.loads(state_file.read_text(encoding="utf-8"))
            output_state_file.parent.mkdir(parents=True, exist_ok=True)
            output_state_file.write_text(json.dumps(state_json, indent=2), encoding="utf-8")

            checksum_after = self._checksum_json(state_file)

            input_types = [str(row.get("type", "")).upper() for row in rows]
            unknown_types = sorted({t for t in input_types if t not in KNOWN_EVENT_TYPES})
            events_applied = sum(1 for row in all_results if bool(row.get("changed")))
            events_skipped = max(0, processed_total - events_applied)

            unknown_changed = 0
            for idx, event_type in enumerate(input_types):
                if idx >= len(all_results):
                    break
                if event_type in KNOWN_EVENT_TYPES:
                    continue
                if bool(all_results[idx].get("changed")):
                    unknown_changed += 1

            report = {
                "events_total": len(rows),
                "events_processed": processed_total,
                "events_applied": events_applied,
                "events_skipped": events_skipped,
                "unknown_event_types": unknown_types,
                "unknown_events_changed": unknown_changed,
                "checksum_before": checksum_before,
                "checksum_after": checksum_after,
            }
            if output_report_file:
                output_report_file.parent.mkdir(parents=True, exist_ok=True)
                output_report_file.write_text(json.dumps(report, indent=2), encoding="utf-8")
            return report
