from tools.bench.long_run_soak_v1_3_25 import run_soak


def test_v1_3_25_long_run_soak_small_cycle_passes():
    report = run_soak(iterations=60, ingest_batch=17)

    assert report["ok"] is True
    assert report["expected_total_events"] == report["ingested_events"]

    counts = report["event_counts"]
    metrics = report["metrics"]

    assert metrics["map_ticks"] == counts["MAP_TICK"]
    assert metrics["map_moves"] == counts["MAP_TRAVERSE"]
    assert metrics["map_inspects"] == counts["MAP_INSPECT"]
    assert metrics["map_interactions"] == counts["MAP_INTERACT"]
    assert metrics["map_completions"] == counts["MAP_COMPLETE"]
    assert metrics["map_enters"] == counts["MAP_ENTER"]
    assert metrics["events_processed"] == sum(counts.values())
