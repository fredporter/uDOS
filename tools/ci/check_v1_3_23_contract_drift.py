#!/usr/bin/env python3
"""v1.3.23 CI guardrails for contract drift and replay determinism."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _assert_exists(path: Path) -> None:
    if not path.exists():
        raise RuntimeError(f"missing required artifact: {path}")


def _run_pytest(paths: list[str]) -> None:
    cmd = [sys.executable, "-m", "pytest", "-q", *paths]
    proc = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True)
    if proc.returncode != 0:
        details = (proc.stdout + "\n" + proc.stderr).strip()
        raise RuntimeError(f"pytest gate failed:\n{details}")
    print(proc.stdout.strip())


def _check_event_contract_alignment() -> None:
    contract = json.loads((REPO / "core" / "config" / "world_adapter_contract_v1_3_21.json").read_text(encoding="utf-8"))
    canonical = {str(x).upper() for x in contract.get("events", {}).get("canonical_types", [])}
    required = {"MAP_ENTER", "MAP_TRAVERSE", "MAP_INSPECT", "MAP_INTERACT", "MAP_COMPLETE", "MAP_TICK"}
    missing = sorted(required - canonical)
    if missing:
        raise RuntimeError(f"contract missing canonical map events: {missing}")

    gameplay_src = (REPO / "core" / "services" / "gameplay_service.py").read_text(encoding="utf-8")
    handled = set(re.findall(r'event_type == "([A-Z0-9_]+)"', gameplay_src))
    missing_handlers = sorted(required - handled)
    if missing_handlers:
        raise RuntimeError(f"gameplay ingestion missing canonical handlers: {missing_handlers}")


def _check_mission_objective_manifest() -> None:
    path = REPO / "core" / "config" / "v1_3_23_mission_objectives.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("objectives", [])
    if not isinstance(rows, list) or not rows:
        raise RuntimeError("v1_3_23 mission objective manifest has no objectives")
    ids = {str(row.get("id", "")).strip() for row in rows if isinstance(row, dict)}
    required_ids = {
        "obj.v1_3_23.registry_contract",
        "obj.v1_3_23.adapter_lifecycle_health",
        "obj.v1_3_23.replay_determinism",
        "obj.v1_3_23.contract_drift_ci",
        "obj.v1_3_23.debug_scan_baseline",
    }
    missing = sorted(required_ids - ids)
    if missing:
        raise RuntimeError(f"missing required mission objective ids: {missing}")


def main() -> int:
    _assert_exists(REPO / "core" / "config" / "v1_3_23_mission_objectives.json")
    _assert_exists(REPO / "core" / "services" / "gameplay_replay_service.py")
    _assert_exists(REPO / "docs" / "specs" / "v1.3.23-CONTRACT-DRIFT-CI-GUARDRAILS.md")
    _check_event_contract_alignment()
    _check_mission_objective_manifest()
    _run_pytest(
        [
            "core/tests/world_adapter_contract_v1_3_21_test.py",
            "core/tests/v1_3_22_lens_parity_test.py",
            "core/tests/gameplay_replay_service_test.py",
        ]
    )
    print("[contract-drift-v1.3.23] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

