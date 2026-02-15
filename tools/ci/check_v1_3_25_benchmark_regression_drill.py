#!/usr/bin/env python3
"""v1.3.25 benchmark regression drill: simulate failure and verify release gate blocks."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.ci.check_v1_3_25_release_checklist import evaluate_release_checklist


def run_drill() -> dict:
    mission_snapshot = {
        "summary": {
            "total": 3,
            "pass": 3,
            "fail": 0,
            "error": 0,
            "pending": 0,
            "blocker_open": False,
            "contract_drift": False,
        }
    }
    benchmark_report = {
        "regression": {
            "status": "fail",
            "metrics": {
                "seed_load_median_ms": {
                    "status": "fail",
                }
            },
        }
    }
    return evaluate_release_checklist(
        mission_snapshot,
        benchmark_report,
        block_on_pending=False,
        block_on_warn=True,
    )


def main() -> int:
    result = run_drill()
    print(json.dumps(result, indent=2))

    if result.get("ok"):
        raise RuntimeError("benchmark regression drill did not block release gate")

    reasons = [str(x) for x in result.get("reasons", [])]
    if not any("benchmark budget gate blocked" in row for row in reasons):
        raise RuntimeError("release gate block reason missing benchmark budget indicator")

    print("[benchmark-regression-drill-v1.3.25] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
