from pathlib import Path


def test_v1_3_26_final_stabilization_script_exists():
    path = Path("tools/ci/check_v1_3_26_final_stabilization.py")
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "final stabilization pass" in text.lower()
    assert "check_v1_3_25_contract_freeze.py" in text
    assert "check_v1_3_23_contract_drift.py" in text
