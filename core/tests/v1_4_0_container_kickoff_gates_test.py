from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_v1_4_0_sonic_docker_smoke_gate_exists_and_checks_cli():
    text = _read("tools/ci/check_v1_4_0_sonic_docker_smoke.py")
    assert "sonic/core/sonic_cli.py" in text
    assert "[sonic-docker-smoke-v1.4.0] PASS" in text


def test_v1_4_0_groovebox_docker_smoke_gate_exists_and_checks_validate():
    text = _read("tools/ci/check_v1_4_0_groovebox_docker_smoke.py")
    assert "library/songscribe/validate.py" in text
    assert "[groovebox-docker-smoke-v1.4.0] PASS" in text


def test_v1_4_0_compose_profile_matrix_gate_exists():
    text = _read("tools/ci/check_v1_4_0_compose_profile_matrix.py")
    assert "mission-scheduler" in text
    assert "home-assistant" in text
    assert "groovebox" in text
    assert "[compose-profile-matrix-v1.4.0] PASS" in text
