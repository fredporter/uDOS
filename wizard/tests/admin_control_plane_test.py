from types import MethodType

from fastapi.testclient import TestClient

from wizard.server import WizardServer


async def _allow_admin(self, request):
    request.state.operator = {"role": "admin", "subject": "test"}
    return None


def test_admin_build_served_from_wizard():
    server = WizardServer()
    server._authenticate_admin = MethodType(_allow_admin, server)
    app = server.create_app()
    client = TestClient(app)

    res = client.get("/admin")
    assert res.status_code == 200
    assert "/_app/immutable/entry/start." in res.text
