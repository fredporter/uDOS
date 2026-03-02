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
