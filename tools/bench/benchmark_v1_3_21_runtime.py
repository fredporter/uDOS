#!/usr/bin/env python3
"""Benchmark budgets for v1.3.21 adapter-readiness gate."""

from __future__ import annotations

import json
import statistics
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List

import sys

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from core.locations.types import Location, Tile, TileObject
from core.services.chunking_contract import derive_chunk2d_id
from core.services.map_renderer import MapRenderer
from core.services.map_runtime_service import MapRuntimeService


def _load_seed_refs(seed_file: Path) -> List[str]:
    raw = json.loads(seed_file.read_text(encoding="utf-8"))
    out: List[str] = []
    for row in raw.get("locations", []):
        if isinstance(row, dict):
            ref = str(row.get("placeRef") or "").strip()
            if ref:
                out.append(ref)
    return out


def _seed_load_ms(seed_file: Path, runs: int = 25) -> float:
    samples = []
    with tempfile.TemporaryDirectory(prefix="udos-v1-3-21-bench-") as tmp:
        tmp_root = Path(tmp)
        events_file = tmp_root / "events.ndjson"
        for i in range(runs):
            t0 = time.perf_counter()
            _ = MapRuntimeService(
                seed_file=seed_file,
                state_file=tmp_root / f"state-{i}.json",
                events_file=events_file,
            )
            samples.append((time.perf_counter() - t0) * 1000.0)
    return float(statistics.median(samples))


def _chunk_resolve_p95_us(place_refs: List[str], rounds: int = 200) -> float:
    samples: List[float] = []
    for _ in range(rounds):
        for ref in place_refs:
            t0 = time.perf_counter()
            _ = derive_chunk2d_id(ref)
            samples.append((time.perf_counter() - t0) * 1_000_000.0)
    if not samples:
        return 0.0
    samples.sort()
    idx = int(len(samples) * 0.95)
    idx = min(max(idx, 0), len(samples) - 1)
    return float(samples[idx])


def _synthetic_location() -> Location:
    tiles: Dict[str, Tile] = {}
    for col in range(10):
        c = chr(ord("A") + col)
        for row in range(10, 30):
            cell = f"{c}{row:02d}"
            obj = TileObject(char=".", label="ground", z=0, blocks=False)
            if (col + row) % 11 == 0:
                obj = TileObject(char="#", label="wall", z=1, blocks=True)
            tiles[cell] = Tile(objects=[obj], sprites=[], markers=[])
    return Location(
        id="L300-AA10",
        name="Benchmark Grid",
        region="bench",
        description="Synthetic benchmark location",
        layer=300,
        cell="AA10",
        scale="terrestrial",
        continent="bench",
        timezone="UTC+0",
        type="benchmark",
        region_type="test",
        tiles=tiles,
    )


def _map_render_rps(rounds: int = 200) -> float:
    renderer = MapRenderer()
    loc = _synthetic_location()
    t0 = time.perf_counter()
    for _ in range(rounds):
        _ = renderer.render(loc)
    elapsed = max(time.perf_counter() - t0, 1e-9)
    return float(rounds / elapsed)


def run_benchmark() -> Dict[str, Any]:
    seed_file = REPO / "core" / "src" / "spatial" / "locations-seed.default.json"
    refs = _load_seed_refs(seed_file)
    return {
        "version": "1.3.21",
        "seed_load_median_ms": round(_seed_load_ms(seed_file), 3),
        "chunk_resolve_p95_us": round(_chunk_resolve_p95_us(refs), 3),
        "map_render_rps": round(_map_render_rps(), 3),
    }


def main() -> int:
    result = run_benchmark()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
