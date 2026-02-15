#!/usr/bin/env python3
"""Deterministic long-run soak for map tick loops + gameplay event ingestion."""

from __future__ import annotations

import json
import tempfile
import time
from pathlib import Path
from typing import Any, Dict

from core.services.gameplay_service import GameplayService
from core.services.map_runtime_service import MapRuntimeService


SEED_TEMPLATE = {
    "version": "1.3.25",
    "locations": [
        {
            "placeId": "alpha",
            "label": "Alpha",
            "placeRef": "EARTH:SUR:L300-AA10",
            "z": 0,
            "links": ["beta"],
            "portals": [],
            "hazards": [],
            "quest_ids": ["q.alpha"],
            "interaction_points": ["ip.alpha"],
            "npc_spawn": ["npc.a"],
            "metadata": {"chunk": "earth-sur-300-aa"},
        },
        {
            "placeId": "beta",
            "label": "Beta",
            "placeRef": "EARTH:SUR:L300-BB10",
            "z": 0,
            "links": ["alpha"],
            "portals": [],
            "hazards": [],
            "quest_ids": ["q.beta"],
            "interaction_points": ["ip.beta"],
            "npc_spawn": ["npc.b"],
            "metadata": {"chunk": "earth-sur-300-bb"},
        },
    ],
}


def run_soak(iterations: int = 1200, ingest_batch: int = 128) -> Dict[str, Any]:
    iterations = max(1, int(iterations or 1))
    ingest_batch = max(1, int(ingest_batch or 1))

    with tempfile.TemporaryDirectory(prefix="udos-v1_3_25-soak-") as tmp:
        root = Path(tmp)
        seed_file = root / "seed.json"
        map_state_file = root / "map_runtime_state.json"
        gameplay_state_file = root / "gameplay_state.json"
        events_file = root / "events.ndjson"
        cursor_file = root / "cursor.json"

        seed_file.write_text(json.dumps(SEED_TEMPLATE), encoding="utf-8")

        map_svc = MapRuntimeService(seed_file=seed_file, state_file=map_state_file, events_file=events_file)
        gameplay_svc = GameplayService(
            state_file=gameplay_state_file,
            events_file=events_file,
            cursor_file=cursor_file,
        )

        expected = {
            "MAP_ENTER": 0,
            "MAP_TRAVERSE": 0,
            "MAP_INSPECT": 0,
            "MAP_INTERACT": 0,
            "MAP_COMPLETE": 0,
            "MAP_TICK": 0,
        }

        enter = map_svc.enter("alice", "alpha")
        if not enter.get("ok"):
            raise RuntimeError(f"failed map enter: {enter}")
        expected["MAP_ENTER"] += 1

        current_place = "alpha"

        start = time.perf_counter()
        for i in range(iterations):
            tick = map_svc.tick("alice", steps=1)
            if not tick.get("ok"):
                raise RuntimeError(f"failed map tick at i={i}: {tick}")
            expected["MAP_TICK"] += 1

            if i % 2 == 0:
                inspect = map_svc.inspect("alice")
                if not inspect.get("ok"):
                    raise RuntimeError(f"failed map inspect at i={i}: {inspect}")
                expected["MAP_INSPECT"] += 1
            else:
                point = "ip.alpha" if current_place == "alpha" else "ip.beta"
                interact = map_svc.interact("alice", point)
                if not interact.get("ok"):
                    raise RuntimeError(f"failed map interact at i={i}: {interact}")
                expected["MAP_INTERACT"] += 1

            if i % 5 == 0:
                objective = "q.alpha" if current_place == "alpha" else "q.beta"
                complete = map_svc.complete("alice", objective)
                if not complete.get("ok"):
                    raise RuntimeError(f"failed map complete at i={i}: {complete}")
                expected["MAP_COMPLETE"] += 1

            target = "beta" if current_place == "alpha" else "alpha"
            move = map_svc.move("alice", target)
            if not move.get("ok"):
                raise RuntimeError(f"failed map move at i={i}: {move}")
            expected["MAP_TRAVERSE"] += 1
            current_place = target

        map_elapsed_ms = (time.perf_counter() - start) * 1000.0

        ingested = 0
        ingest_ticks = 0
        start_ingest = time.perf_counter()
        while True:
            result = gameplay_svc.tick("alice", max_events=ingest_batch)
            processed = int(result.get("processed", 0) or 0)
            ingested += processed
            ingest_ticks += 1
            if processed == 0:
                break
        ingest_elapsed_ms = (time.perf_counter() - start_ingest) * 1000.0

        progress = gameplay_svc.get_user_progress("alice")
        metrics = progress.get("metrics", {}) if isinstance(progress.get("metrics"), dict) else {}
        stats = gameplay_svc.get_user_stats("alice")

        expected_total = sum(expected.values())
        checks = {
            "ingested_matches_event_count": ingested == expected_total,
            "map_ticks_match": int(metrics.get("map_ticks", 0) or 0) == expected["MAP_TICK"],
            "map_moves_match": int(metrics.get("map_moves", 0) or 0) == expected["MAP_TRAVERSE"],
            "map_inspects_match": int(metrics.get("map_inspects", 0) or 0) == expected["MAP_INSPECT"],
            "map_interactions_match": int(metrics.get("map_interactions", 0) or 0) == expected["MAP_INTERACT"],
            "map_completions_match": int(metrics.get("map_completions", 0) or 0) == expected["MAP_COMPLETE"],
            "map_enters_match": int(metrics.get("map_enters", 0) or 0) == expected["MAP_ENTER"],
            "events_processed_match": int(metrics.get("events_processed", 0) or 0) == expected_total,
            "xp_positive": int(stats.get("xp", 0) or 0) > 0,
        }
        ok = all(checks.values())

        return {
            "ok": ok,
            "iterations": iterations,
            "ingest_batch": ingest_batch,
            "event_counts": expected,
            "expected_total_events": expected_total,
            "ingested_events": ingested,
            "ingest_tick_calls": ingest_ticks,
            "metrics": {
                "map_ticks": int(metrics.get("map_ticks", 0) or 0),
                "map_moves": int(metrics.get("map_moves", 0) or 0),
                "map_inspects": int(metrics.get("map_inspects", 0) or 0),
                "map_interactions": int(metrics.get("map_interactions", 0) or 0),
                "map_completions": int(metrics.get("map_completions", 0) or 0),
                "map_enters": int(metrics.get("map_enters", 0) or 0),
                "events_processed": int(metrics.get("events_processed", 0) or 0),
            },
            "stats": stats,
            "checks": checks,
            "timing": {
                "map_loop_ms": round(map_elapsed_ms, 3),
                "ingest_loop_ms": round(ingest_elapsed_ms, 3),
            },
        }
