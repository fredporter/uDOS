from pathlib import Path


def test_v1_4_0_toybox_lifespan_gate_targets_adapter_lifecycle_contract():
    path = Path("tools/ci/check_v1_4_0_toybox_lifespan_readiness.py")
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "deprecated @app.on_event hooks" in text
    assert "lifespan=lifespan" in text
    assert "wizard/tests/toybox_adapter_lifecycle_test.py" in text
