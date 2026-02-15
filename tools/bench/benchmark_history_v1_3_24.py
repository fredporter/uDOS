#!/usr/bin/env python3
"""Benchmark history persistence and regression-delta evaluation for v1.3.24."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import sys

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.bench.benchmark_v1_3_21_runtime import run_benchmark


@dataclass(frozen=True)
class MetricPolicy:
    direction: str  # "lower" or "higher"
    warn_pct: float
    fail_pct: float


METRIC_POLICIES: Dict[str, MetricPolicy] = {
    "seed_load_median_ms": MetricPolicy(direction="lower", warn_pct=0.15, fail_pct=0.30),
    "chunk_resolve_p95_us": MetricPolicy(direction="lower", warn_pct=0.15, fail_pct=0.30),
    "map_render_rps": MetricPolicy(direction="higher", warn_pct=0.15, fail_pct=0.30),
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def evaluate_regression(current: Dict[str, Any], previous: Dict[str, Any]) -> Dict[str, Any]:
    deltas: Dict[str, Dict[str, Any]] = {}
    statuses = []
    for metric, policy in METRIC_POLICIES.items():
        cur = float(current.get(metric, 0.0))
        prev = float(previous.get(metric, 0.0))
        if prev <= 0:
            deltas[metric] = {
                "previous": prev,
                "current": cur,
                "delta": None,
                "delta_pct": None,
                "status": "unknown",
            }
            statuses.append("unknown")
            continue

        delta = cur - prev
        delta_pct = delta / prev
        if policy.direction == "lower":
            # Increase is worse.
            if delta_pct >= policy.fail_pct:
                status = "fail"
            elif delta_pct >= policy.warn_pct:
                status = "warn"
            else:
                status = "ok"
        else:
            # Decrease is worse.
            drop_pct = -delta_pct
            if drop_pct >= policy.fail_pct:
                status = "fail"
            elif drop_pct >= policy.warn_pct:
                status = "warn"
            else:
                status = "ok"

        deltas[metric] = {
            "previous": round(prev, 6),
            "current": round(cur, 6),
            "delta": round(delta, 6),
            "delta_pct": round(delta_pct, 6),
            "status": status,
            "direction": policy.direction,
            "warn_pct": policy.warn_pct,
            "fail_pct": policy.fail_pct,
        }
        statuses.append(status)

    overall = "ok"
    if "fail" in statuses:
        overall = "fail"
    elif "warn" in statuses:
        overall = "warn"
    return {"status": overall, "metrics": deltas}


def run_and_record(snapshot_dir: Optional[Path] = None) -> Dict[str, Any]:
    out_dir = snapshot_dir or (REPO / "memory" / "reports" / "benchmarks")
    out_dir.mkdir(parents=True, exist_ok=True)

    latest_path = out_dir / "v1_3_24_latest.json"
    history_path = out_dir / "v1_3_24_history.ndjson"
    report_path = out_dir / "v1_3_24_regression_report.json"

    current = run_benchmark()
    current["milestone"] = "v1.3.24"
    current["captured_at"] = _now_iso()

    previous = _read_json(latest_path)
    if previous is None:
        regression = {"status": "ok", "metrics": {}, "note": "baseline snapshot"}
    else:
        regression = evaluate_regression(current, previous)

    payload = {
        "version": "1.3.24",
        "captured_at": current["captured_at"],
        "current": current,
        "previous": previous,
        "regression": regression,
    }

    latest_path.write_text(json.dumps(current, indent=2), encoding="utf-8")
    with history_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(current) + "\n")
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> int:
    report = run_and_record()
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

