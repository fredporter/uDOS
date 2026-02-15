from fastapi import FastAPI
from fastapi.testclient import TestClient

from wizard.routes.ucode_meta_routes import create_ucode_meta_routes


def test_meta_routes_allowlist_and_commands():
    app = FastAPI()
    app.include_router(create_ucode_meta_routes({"HELP", "STATUS"}))
    client = TestClient(app)

    res = client.get("/allowlist")
    assert res.status_code == 200
    assert "HELP" in res.json()["allowlist"]

    res = client.get("/commands")
    assert res.status_code == 200
    assert isinstance(res.json()["commands"], list)


def test_meta_routes_hotkeys_ok():
    app = FastAPI()
    app.include_router(create_ucode_meta_routes({"HELP"}))
    client = TestClient(app)

    res = client.get("/hotkeys")
    assert res.status_code == 200
