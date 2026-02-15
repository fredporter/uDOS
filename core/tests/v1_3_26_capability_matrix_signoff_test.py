from pathlib import Path


def test_v1_3_26_capability_matrix_signoff_script_targets_core_wizard_toybox():
    path = Path("tools/ci/check_v1_3_26_capability_matrix_signoff.py")
    text = path.read_text(encoding="utf-8")
    assert "core/tests/v1_3_21_parity_gate_test.py" in text
    assert "core/tests/v1_3_24_command_capability_negative_test.py" in text
    assert "wizard/tests/toybox_capability_matrix_test.py" in text
    assert "wizard/tests/toybox_adapter_lifecycle_test.py" in text
