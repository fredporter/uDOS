import json
from pathlib import Path


def test_v1_4_0_container_capability_matrix_has_required_lanes():
    payload = json.loads(Path("core/config/v1_4_0_container_capability_matrix.json").read_text(encoding="utf-8"))
    lanes = payload.get("lanes", [])
    ids = {str(row.get("id")) for row in lanes if isinstance(row, dict)}
    assert {"wizard", "sonic", "groovebox", "homeassistant"}.issubset(ids)


def test_v1_4_0_container_capability_gate_script_exists():
    text = Path("tools/ci/check_v1_4_0_container_capability_matrix.py").read_text(encoding="utf-8")
    assert "[container-capability-matrix-v1.4.0] PASS" in text
    assert "v1_4_0_container_capability_matrix.json" in text
