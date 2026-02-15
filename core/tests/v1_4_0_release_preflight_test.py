from pathlib import Path


def test_v1_4_0_release_preflight_includes_docker_and_capability_gates():
    text = Path("tools/ci/check_v1_4_0_release_preflight.py").read_text(encoding="utf-8")
    assert "check_v1_4_0_toybox_lifespan_readiness.py" in text
    assert "check_v1_4_0_sonic_docker_smoke.py" in text
    assert "check_v1_4_0_groovebox_docker_smoke.py" in text
    assert "check_v1_4_0_compose_profile_matrix.py" in text
    assert "check_v1_4_0_container_capability_matrix.py" in text
    assert "[release-preflight-v1.4.0] PASS" in text
