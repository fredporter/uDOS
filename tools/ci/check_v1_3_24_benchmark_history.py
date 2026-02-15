#!/usr/bin/env python3
"""v1.3.24 benchmark history and regression-delta gate."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.bench.benchmark_history_v1_3_24 import run_and_record


def main() -> int:
    report = run_and_record()
    status = str(report.get("regression", {}).get("status", "ok"))
    print(json.dumps(report, indent=2))
    if status == "fail":
        raise RuntimeError("benchmark regression delta exceeded fail threshold(s)")
    if status == "warn":
        print("[benchmark-history-v1.3.24] WARN")
    else:
        print("[benchmark-history-v1.3.24] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

