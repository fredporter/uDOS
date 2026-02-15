#!/usr/bin/env python3
"""v1.3.25 release checklist automation for mission objectives + benchmark budgets."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from core.services.mission_objective_registry import MissionObjectiveRegistry
from tools.bench.benchmark_history_v1_3_24 import run_and_record


REPORT_PATH = REPO / "memory" / "reports" / "v1_3_25_release_checklist.json"


def evaluate_release_checklist(
    mission_snapshot: Dict[str, Any],
    benchmark_report: Dict[str, Any],
    *,
    block_on_pending: bool = False,
    block_on_blocker_open: bool = False,
    block_on_warn: bool = False,
) -> Dict[str, Any]:
    summary = mission_snapshot.get("summary", {}) if isinstance(mission_snapshot, dict) else {}
    pending = int(summary.get("pending", 0) or 0)
    fail = int(summary.get("fail", 0) or 0)
    error = int(summary.get("error", 0) or 0)
    blocker_open = bool(summary.get("blocker_open"))
    contract_drift = bool(summary.get("contract_drift"))

    mission_ok = (
        fail == 0
        and error == 0
        and (not blocker_open if block_on_blocker_open else True)
        and not contract_drift
        and (pending == 0 if block_on_pending else True)
    )

    benchmark_status = str(benchmark_report.get("regression", {}).get("status", "ok")).lower()
    benchmark_ok = benchmark_status == "ok" or (benchmark_status == "warn" and not block_on_warn)

    reasons = []
    if not mission_ok:
        reasons.append("mission objective gate not satisfied")
    if not benchmark_ok:
        reasons.append(f"benchmark budget gate blocked: status={benchmark_status}")

    return {
        "ok": mission_ok and benchmark_ok,
        "mission_gate": {
            "ok": mission_ok,
            "summary": {
                "total": int(summary.get("total", 0) or 0),
                "pass": int(summary.get("pass", 0) or 0),
                "fail": fail,
                "error": error,
                "pending": pending,
                "blocker_open": blocker_open,
                "contract_drift": contract_drift,
            },
            "policy": {
                "block_on_pending": bool(block_on_pending),
                "block_on_blocker_open": bool(block_on_blocker_open),
            },
        },
        "benchmark_gate": {
            "ok": benchmark_ok,
            "regression_status": benchmark_status,
            "policy": {
                "block_on_warn": bool(block_on_warn),
            },
            "report_path": "memory/reports/benchmarks/v1_3_24_regression_report.json",
        },
        "reasons": reasons,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run v1.3.25 release checklist automation")
    parser.add_argument("--block-on-pending", action="store_true")
    parser.add_argument("--block-on-blocker-open", action="store_true")
    parser.add_argument("--block-on-warn", action="store_true")
    parser.add_argument(
        "--enforce",
        action="store_true",
        help="Fail process when checklist result is not ok. Default is report-only.",
    )
    args = parser.parse_args()

    mission_snapshot = MissionObjectiveRegistry().snapshot()
    benchmark_report = run_and_record()
    report = {
        "version": "1.3.25",
        "milestone": "v1.3.25",
        "release_checklist": evaluate_release_checklist(
            mission_snapshot,
            benchmark_report,
            block_on_pending=args.block_on_pending,
            block_on_blocker_open=args.block_on_blocker_open,
            block_on_warn=args.block_on_warn,
        ),
        "mission_objectives": mission_snapshot,
        "benchmark": benchmark_report,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report["release_checklist"], indent=2))
    print(f"report: {REPORT_PATH.relative_to(REPO)}")

    if not report["release_checklist"]["ok"]:
        if args.enforce:
            raise RuntimeError("v1.3.25 release checklist gate failed")
        print("[release-checklist-v1.3.25] WARN (report-only mode)")
        return 0

    print("[release-checklist-v1.3.25] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
