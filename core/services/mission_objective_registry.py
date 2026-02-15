"""Mission objective registry/status loader for release-gate checks."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from core.services.logging_api import get_repo_root

_ALLOWED_STATUS = {"pending", "pass", "fail", "error"}


class MissionObjectiveRegistry:
    """Load objective manifest and produce release-gate status snapshots."""

    def __init__(self, *, manifest_file: Optional[Path] = None, status_file: Optional[Path] = None) -> None:
        repo_root = get_repo_root()
        self.manifest_file = manifest_file or repo_root / "core" / "config" / "v1_3_23_mission_objectives.json"
        private_root = repo_root / "memory" / "bank" / "private"
        private_root.mkdir(parents=True, exist_ok=True)
        self.status_file = status_file or private_root / "mission_objective_status_v1_3_23.json"

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _load_json(path: Path) -> Dict[str, Any]:
        try:
            parsed = json.loads(path.read_text(encoding="utf-8"))
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            return {}

    def _load_manifest(self) -> Tuple[str, str, List[Dict[str, Any]]]:
        data = self._load_json(self.manifest_file)
        version = str(data.get("version") or "1.3.23")
        milestone = str(data.get("milestone") or "v1.3.23")
        raw = data.get("objectives", [])
        rows: List[Dict[str, Any]] = []
        if isinstance(raw, list):
            for item in raw:
                if not isinstance(item, dict):
                    continue
                obj_id = str(item.get("id") or "").strip()
                if not obj_id:
                    continue
                severity = str(item.get("severity") or "required")
                if severity not in {"blocker", "required", "advisory"}:
                    severity = "required"
                rows.append(
                    {
                        "id": obj_id,
                        "description": str(item.get("description") or ""),
                        "owner": str(item.get("owner") or "core"),
                        "severity": severity,
                        "checks": list(item.get("checks", [])) if isinstance(item.get("checks"), list) else [],
                        "threshold": item.get("threshold"),
                    }
                )
        return version, milestone, rows

    def _load_status_overrides(self) -> Dict[str, Dict[str, Any]]:
        data = self._load_json(self.status_file)
        raw = data.get("objectives", {})
        out: Dict[str, Dict[str, Any]] = {}
        if not isinstance(raw, dict):
            return out
        for key, value in raw.items():
            if not isinstance(value, dict):
                continue
            status = str(value.get("status") or "pending")
            if status not in _ALLOWED_STATUS:
                status = "error"
            evidence = value.get("evidence")
            out[str(key)] = {
                "status": status,
                "updated_at": value.get("updated_at"),
                "evidence": evidence if isinstance(evidence, list) else [],
            }
        return out

    def snapshot(self) -> Dict[str, Any]:
        version, milestone, manifest = self._load_manifest()
        overrides = self._load_status_overrides()
        known_ids = {row["id"] for row in manifest}
        unknown_override_ids = sorted([key for key in overrides.keys() if key not in known_ids])

        objectives: List[Dict[str, Any]] = []
        for row in manifest:
            override = overrides.get(row["id"], {})
            status = str(override.get("status") or "pending")
            if status not in _ALLOWED_STATUS:
                status = "error"
            objectives.append(
                {
                    **row,
                    "status": status,
                    "updated_at": override.get("updated_at"),
                    "evidence": list(override.get("evidence", [])),
                }
            )

        counts = {"pending": 0, "pass": 0, "fail": 0, "error": 0}
        for row in objectives:
            counts[row["status"]] = counts.get(row["status"], 0) + 1
        blocker_open = any(
            row.get("severity") == "blocker" and row.get("status") != "pass"
            for row in objectives
        )

        return {
            "version": version,
            "generated_at": self._now_iso(),
            "milestone": milestone,
            "summary": {
                "total": len(objectives),
                "pass": counts.get("pass", 0),
                "fail": counts.get("fail", 0),
                "error": counts.get("error", 0),
                "pending": counts.get("pending", 0),
                "blocker_open": blocker_open,
                "contract_drift": bool(unknown_override_ids),
            },
            "objectives": objectives,
            "contract_drift": {
                "unknown_objective_ids": unknown_override_ids,
            },
        }

