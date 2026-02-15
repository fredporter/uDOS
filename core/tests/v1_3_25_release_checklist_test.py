from tools.ci.check_v1_3_25_release_checklist import evaluate_release_checklist


def test_release_checklist_passes_with_clean_mission_and_ok_benchmark():
    mission_snapshot = {
        "summary": {
            "total": 2,
            "pass": 2,
            "fail": 0,
            "error": 0,
            "pending": 0,
            "blocker_open": False,
            "contract_drift": False,
        }
    }
    benchmark_report = {"regression": {"status": "ok"}}

    result = evaluate_release_checklist(mission_snapshot, benchmark_report)
    assert result["ok"] is True
    assert result["mission_gate"]["ok"] is True
    assert result["benchmark_gate"]["ok"] is True


def test_release_checklist_blocks_on_benchmark_fail():
    mission_snapshot = {
        "summary": {
            "total": 2,
            "pass": 2,
            "fail": 0,
            "error": 0,
            "pending": 0,
            "blocker_open": False,
            "contract_drift": False,
        }
    }
    benchmark_report = {"regression": {"status": "fail"}}

    result = evaluate_release_checklist(mission_snapshot, benchmark_report)
    assert result["ok"] is False
    assert result["benchmark_gate"]["ok"] is False
