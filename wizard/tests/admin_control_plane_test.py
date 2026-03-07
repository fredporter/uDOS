from pathlib import Path
from types import MethodType

from fastapi.testclient import TestClient

import wizard.server as server_module
from wizard.server import WizardServer


async def _allow_admin(self, request):
    request.state.operator = {"role": "admin", "subject": "test"}
    return None


def test_admin_build_served_from_wizard():
    fake_repo_root = Path(__file__).resolve().parents[1] / ".tmp-admin-root"
    build_root = fake_repo_root / "web-admin" / "build"
    app_root = build_root / "_app" / "immutable" / "entry"
    app_root.mkdir(parents=True, exist_ok=True)
    (build_root / "index.html").write_text(
        '<!doctype html><html><body><script src="/_app/immutable/entry/start.test.js"></script></body></html>',
        encoding="utf-8",
    )
    (app_root / "start.test.js").write_text("console.log('ok');", encoding="utf-8")

    original_repo_root = server_module.REPO_ROOT
    server_module.REPO_ROOT = fake_repo_root
    server = WizardServer()
    try:
        server._authenticate_admin = MethodType(_allow_admin, server)
        app = server.create_app()
        client = TestClient(app)

        res = client.get("/admin")
        assert res.status_code == 200
        assert "/_app/immutable/entry/start." in res.text
    finally:
        server_module.REPO_ROOT = original_repo_root


def test_mesh_pair_returns_device_token(monkeypatch):
    class StubAuth:
        def complete_pairing(self, **_kwargs):
            return type(
                "_Device",
                (),
                {"id": "device-1", "to_dict": lambda self: {"id": "device-1", "name": "Phone"}},
            )()

        def rotate_device_token(self, device_id):
            assert device_id == "device-1"
            return "device-1:secret"

    monkeypatch.setattr(server_module, "get_device_auth", lambda: StubAuth())
    monkeypatch.setattr(
        server_module,
        "create_rate_limit_middleware",
        lambda _rate_limiter: (lambda request, call_next: call_next(request)),
    )

    server = WizardServer()
    server._authenticate_admin = MethodType(_allow_admin, server)
    app = server.create_app()
    client = TestClient(app)

    res = client.post(
        "/api/mesh/pair",
        json={"code": "ABCD EFGH", "device_id": "device-1", "device_name": "Phone"},
    )

    assert res.status_code == 200
    payload = res.json()
    assert payload["status"] == "success"
    assert payload["device"]["id"] == "device-1"
    assert payload["device_token"] == "device-1:secret"
