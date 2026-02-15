#!/usr/bin/env python3
"""v1.3.25 long-run soak gate for map loop + event ingestion."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.bench.long_run_soak_v1_3_25 import run_soak


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic long-run soak")
    parser.add_argument("--iterations", type=int, default=1200)
    parser.add_argument("--ingest-batch", type=int, default=128)
    args = parser.parse_args()

    report = run_soak(iterations=args.iterations, ingest_batch=args.ingest_batch)
    print(json.dumps(report, indent=2))
    if not report.get("ok"):
        raise RuntimeError("v1.3.25 long-run soak checks failed")
    print("[long-run-soak-v1.3.25] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
