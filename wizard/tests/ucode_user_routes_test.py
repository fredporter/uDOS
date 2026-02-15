from fastapi import FastAPI
from fastapi.testclient import TestClient

from wizard.routes.ucode_user_routes import create_ucode_user_routes


class _User:
    def __init__(self, username="alice"):
        self.username = username

    def to_dict(self):
        return {"username": self.username}


class _UserMgr:
    def __init__(self):
        self._user = _User()

    def current(self):
        return self._user

    def list_users(self):
        return [{"username": "alice"}]

    def switch_user(self, username):
        return (True, f"switched to {username}")

    def has_permission(self, _perm):
        return True

    def set_role(self, username, role):
        return (True, f"set {username} -> {role}")


def _build_client(monkeypatch):
    import core.services.user_service as user_service

    monkeypatch.setattr(user_service, "get_user_manager", lambda: _UserMgr())
    monkeypatch.setattr(user_service, "is_ghost_mode", lambda: False)
    app = FastAPI()
    app.include_router(create_ucode_user_routes())
    return TestClient(app)


def test_user_routes_basic(monkeypatch):
    client = _build_client(monkeypatch)

    res = client.get("/user")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

    res = client.get("/users")
    assert res.status_code == 200
    assert isinstance(res.json()["users"], list)

    res = client.post("/user/switch", json={"username": "bob"})
    assert res.status_code == 200
    assert "switched" in res.json()["message"]


def test_user_role_route(monkeypatch):
    client = _build_client(monkeypatch)
    res = client.post("/user/role", json={"username": "bob", "role": "admin"})
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
