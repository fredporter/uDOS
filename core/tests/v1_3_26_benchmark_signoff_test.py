from pathlib import Path


def test_v1_3_26_benchmark_signoff_script_uses_strict_release_gate_mode():
    path = Path("tools/ci/check_v1_3_26_benchmark_signoff.py")
    text = path.read_text(encoding="utf-8")
    assert "--enforce" in text
    assert "--block-on-warn" in text
