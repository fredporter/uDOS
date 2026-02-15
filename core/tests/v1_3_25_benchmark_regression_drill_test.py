from tools.ci.check_v1_3_25_benchmark_regression_drill import run_drill


def test_benchmark_regression_drill_blocks_release_gate():
    result = run_drill()
    assert result["ok"] is False
    reasons = [str(x) for x in result.get("reasons", [])]
    assert any("benchmark budget gate blocked" in row for row in reasons)
