from pathlib import Path
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

import wizard.routes.diagram_routes as routes


def _client(monkeypatch):
    app = FastAPI()
    app.include_router(routes.create_diagram_routes())
    return TestClient(app)


def test_diagram_health(monkeypatch):
    monkeypatch.setattr(routes.shutil, "which", lambda name: "/usr/bin/mmdc" if name == "mmdc" else None)
    client = _client(monkeypatch)
    res = client.get("/api/diagrams/health")
    assert res.status_code == 200
    assert res.json()["engines"]["mermaid"]["available"] is True


def test_render_mermaid_inline(monkeypatch):
    monkeypatch.setattr(routes.shutil, "which", lambda _name: "/usr/bin/mmdc")

    def _fake_run(cmd, capture_output, text, timeout):
        out_index = cmd.index("-o") + 1
        out_file = Path(cmd[out_index])
        out_file.write_text("<svg>ok</svg>", encoding="utf-8")
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(routes.subprocess, "run", _fake_run)
    client = _client(monkeypatch)
    res = client.post("/api/diagrams/render", json={"source": "graph TD; A-->B;"})
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["engine"] == "mermaid"
    assert body["svg"] == "<svg>ok</svg>"


def test_render_mermaid_to_file(monkeypatch, tmp_path):
    monkeypatch.setattr(routes.shutil, "which", lambda _name: "/usr/bin/mmdc")

    def _fake_run(cmd, capture_output, text, timeout):
        out_index = cmd.index("-o") + 1
        out_file = Path(cmd[out_index])
        out_file.write_text("<svg>saved</svg>", encoding="utf-8")
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(routes.subprocess, "run", _fake_run)
    monkeypatch.setattr(routes, "get_memory_dir", lambda: tmp_path)
    client = _client(monkeypatch)

    res = client.post(
        "/api/diagrams/render",
        json={"source": "graph TD; A-->B;", "output_file": "test/out.svg"},
    )
    assert res.status_code == 200
    out_file = tmp_path / "diagrams" / "test" / "out.svg"
    assert out_file.exists()
    assert out_file.read_text(encoding="utf-8") == "<svg>saved</svg>"


def test_render_rejects_invalid_engine(monkeypatch):
    client = _client(monkeypatch)
    res = client.post("/api/diagrams/render", json={"source": "x", "engine": "unknown"})
    assert res.status_code == 400
