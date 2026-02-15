#!/usr/bin/env python3
"""Validate v1.3.21 adapter readiness gate artifacts and benchmark budgets."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from core.services.world_adapter_contract import load_world_adapter_contract
from tools.bench.benchmark_v1_3_21_runtime import run_benchmark


MAX_SEED_LOAD_MS = 1000.0
MAX_CHUNK_RESOLVE_P95_US = 500.0
MIN_MAP_RENDER_RPS = 80.0


def _assert_exists(path: Path) -> None:
    if not path.exists():
        raise RuntimeError(f"missing required artifact: {path}")


def _check_contract_shape() -> None:
    contract = load_world_adapter_contract()
    if contract.get("version") != "1.3.21":
        raise RuntimeError("world adapter contract version must be 1.3.21")

    canonical = set(contract.get("events", {}).get("canonical_types", []))
    required = {"MAP_ENTER", "MAP_TRAVERSE", "MAP_INSPECT", "MAP_INTERACT", "MAP_COMPLETE", "MAP_TICK"}
    missing = sorted(required - canonical)
    if missing:
        raise RuntimeError(f"world adapter contract missing canonical event types: {', '.join(missing)}")

    pattern = str(contract.get("identity", {}).get("place_ref", {}).get("pattern", ""))
    if not pattern or "L[0-9]{3}" not in pattern:
        raise RuntimeError("world adapter contract place_ref pattern missing LocId segment")
    try:
        re.compile(pattern)
    except re.error as exc:
        raise RuntimeError(f"invalid place_ref regex in world adapter contract: {exc}") from exc


def _check_benchmarks() -> None:
    result = run_benchmark()

    if float(result.get("seed_load_median_ms", 0.0)) > MAX_SEED_LOAD_MS:
        raise RuntimeError(
            f"seed load median too high: {result.get('seed_load_median_ms')}ms > {MAX_SEED_LOAD_MS}ms"
        )
    if float(result.get("chunk_resolve_p95_us", 0.0)) > MAX_CHUNK_RESOLVE_P95_US:
        raise RuntimeError(
            f"chunk resolve p95 too high: {result.get('chunk_resolve_p95_us')}us > {MAX_CHUNK_RESOLVE_P95_US}us"
        )
    if float(result.get("map_render_rps", 0.0)) < MIN_MAP_RENDER_RPS:
        raise RuntimeError(
            f"map render throughput too low: {result.get('map_render_rps')} rps < {MIN_MAP_RENDER_RPS} rps"
        )

    print(json.dumps(result, indent=2))


def main() -> int:
    _assert_exists(REPO / "core" / "config" / "world_adapter_contract_v1_3_21.json")
    _assert_exists(REPO / "docs" / "specs" / "v1.3.21-ADAPTER-READINESS-CHECKLIST.md")
    _assert_exists(REPO / "docs" / "specs" / "v1.3.21-DUAL-LENS-COMPAT-MATRIX.md")
    _check_contract_shape()
    _check_benchmarks()
    print("[adapter-readiness-v1.3.21] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
