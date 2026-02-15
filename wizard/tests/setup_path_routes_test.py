from fastapi import FastAPI
from fastapi.testclient import TestClient

from wizard.routes.setup_path_routes import create_setup_path_routes


def test_get_paths_returns_payload():
    app = FastAPI()
    app.include_router(
        create_setup_path_routes(
            get_paths=lambda: {"data": {"a": "/tmp/a"}, "installation": {"b": "/tmp/b"}}
        ),
        prefix="/api/setup",
    )
    client = TestClient(app)

    res = client.get("/api/setup/paths")
    assert res.status_code == 200
    payload = res.json()
    assert "data" in payload
    assert "installation" in payload


def test_initialize_paths_creates_directories(tmp_path):
    p1 = tmp_path / "data" / "main"
    p2 = tmp_path / "install" / "main"
    app = FastAPI()
    app.include_router(
        create_setup_path_routes(
            get_paths=lambda: {
                "data": {"main": str(p1)},
                "installation": {"main": str(p2)},
            }
        ),
        prefix="/api/setup",
    )
    client = TestClient(app)

    res = client.post("/api/setup/paths/initialize")
    assert res.status_code == 200
    payload = res.json()
    assert payload["status"] == "complete"
    assert str(p1) in payload["created_directories"]
    assert str(p2) in payload["created_directories"]
    assert p1.exists() is True
    assert p2.exists() is True
