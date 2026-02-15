import subprocess

from fastapi import FastAPI
from fastapi.testclient import TestClient

from wizard.routes import config_ssh_routes as routes


def _app_with_router() -> FastAPI:
    app = FastAPI()
    app.include_router(routes.create_config_ssh_routes(), prefix="/api/config")
    return app


def test_ssh_status_parses_fingerprint(monkeypatch, tmp_path):
    ssh_dir = tmp_path / ".ssh"
    ssh_dir.mkdir(parents=True, exist_ok=True)
    (ssh_dir / routes.DEFAULT_SSH_KEY_NAME).write_text("private", encoding="utf-8")
    monkeypatch.setattr(routes, "SSH_DIR", ssh_dir)

    class Result:
        returncode = 0
        stdout = "4096 SHA256:abc user@host (RSA)\n"

    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: Result())

    app = _app_with_router()
    client = TestClient(app)
    res = client.get("/api/config/ssh/status")
    assert res.status_code == 200
    payload = res.json()
    assert payload["key_exists"] is True
    assert payload["fingerprint"] == "SHA256:abc"
    assert payload["key_type"] == "RSA"


def test_ssh_public_key_returns_content(monkeypatch, tmp_path):
    ssh_dir = tmp_path / ".ssh"
    ssh_dir.mkdir(parents=True, exist_ok=True)
    pub_path = ssh_dir / f"{routes.DEFAULT_SSH_KEY_NAME}.pub"
    pub_path.write_text("ssh-ed25519 AAAATEST user@test", encoding="utf-8")
    monkeypatch.setattr(routes, "SSH_DIR", ssh_dir)

    app = _app_with_router()
    client = TestClient(app)
    res = client.get("/api/config/ssh/public-key")
    assert res.status_code == 200
    payload = res.json()
    assert payload["public_key"].startswith("ssh-ed25519")


def test_ssh_test_connection_success(monkeypatch, tmp_path):
    ssh_dir = tmp_path / ".ssh"
    ssh_dir.mkdir(parents=True, exist_ok=True)
    (ssh_dir / routes.DEFAULT_SSH_KEY_NAME).write_text("private", encoding="utf-8")
    monkeypatch.setattr(routes, "SSH_DIR", ssh_dir)

    class Result:
        returncode = 1
        stdout = "Hi user! You've successfully authenticated."
        stderr = ""

    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: Result())

    app = _app_with_router()
    client = TestClient(app)
    res = client.post("/api/config/ssh/test-connection")
    assert res.status_code == 200
    payload = res.json()
    assert payload["success"] is True
    assert payload["status"] == "connected"


def test_ssh_test_connection_timeout(monkeypatch, tmp_path):
    ssh_dir = tmp_path / ".ssh"
    ssh_dir.mkdir(parents=True, exist_ok=True)
    (ssh_dir / routes.DEFAULT_SSH_KEY_NAME).write_text("private", encoding="utf-8")
    monkeypatch.setattr(routes, "SSH_DIR", ssh_dir)

    def _raise_timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="ssh", timeout=10)

    monkeypatch.setattr(subprocess, "run", _raise_timeout)

    app = _app_with_router()
    client = TestClient(app)
    res = client.post("/api/config/ssh/test-connection")
    assert res.status_code == 408
