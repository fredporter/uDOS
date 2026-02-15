import json

from tools.bench.benchmark_history_v1_3_24 import evaluate_regression, run_and_record


def test_benchmark_regression_evaluator_warn_and_fail_thresholds():
    previous = {
        "seed_load_median_ms": 10.0,
        "chunk_resolve_p95_us": 100.0,
        "map_render_rps": 1000.0,
    }
    current_warn = {
        "seed_load_median_ms": 11.6,  # +16% => warn
        "chunk_resolve_p95_us": 100.0,
        "map_render_rps": 1000.0,
    }
    warn = evaluate_regression(current_warn, previous)
    assert warn["status"] == "warn"
    assert warn["metrics"]["seed_load_median_ms"]["status"] == "warn"

    current_fail = {
        "seed_load_median_ms": 13.5,  # +35% => fail
        "chunk_resolve_p95_us": 100.0,
        "map_render_rps": 1000.0,
    }
    fail = evaluate_regression(current_fail, previous)
    assert fail["status"] == "fail"
    assert fail["metrics"]["seed_load_median_ms"]["status"] == "fail"


def test_benchmark_history_snapshot_persistence_and_delta_report(tmp_path, monkeypatch):
    first = {
        "version": "1.3.21",
        "seed_load_median_ms": 10.0,
        "chunk_resolve_p95_us": 100.0,
        "map_render_rps": 1000.0,
    }
    second = {
        "version": "1.3.21",
        "seed_load_median_ms": 14.0,
        "chunk_resolve_p95_us": 100.0,
        "map_render_rps": 1000.0,
    }
    seq = {"n": 0}

    def fake_run_benchmark():
        seq["n"] += 1
        return first if seq["n"] == 1 else second

    monkeypatch.setattr("tools.bench.benchmark_history_v1_3_24.run_benchmark", fake_run_benchmark)

    report_1 = run_and_record(snapshot_dir=tmp_path)
    assert report_1["regression"]["status"] == "ok"
    latest = json.loads((tmp_path / "v1_3_24_latest.json").read_text(encoding="utf-8"))
    assert latest["seed_load_median_ms"] == 10.0

    report_2 = run_and_record(snapshot_dir=tmp_path)
    assert report_2["regression"]["status"] == "fail"
    history_lines = (tmp_path / "v1_3_24_history.ndjson").read_text(encoding="utf-8").strip().splitlines()
    assert len(history_lines) == 2
