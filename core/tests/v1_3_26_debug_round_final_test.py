from pathlib import Path


def test_v1_3_26_debug_round_final_script_contains_unused_review_approval():
    path = Path("tools/ci/check_v1_3_26_debug_round_final.py")
    text = path.read_text(encoding="utf-8")
    assert "unused_function_review" in text
    assert '"status": "approved"' in text
