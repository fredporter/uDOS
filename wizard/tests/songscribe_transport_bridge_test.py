from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

import wizard.routes.songscribe_routes as routes


class _SongscribeService:
    def to_pattern(self, text):
        return {"source": text, "tracks": []}


class _Transport:
    def handshake(self, is_initiator=True):
        _ = is_initiator
        return [0.1, 0.2]

    def success(self):
        return [0.5]

    def error(self):
        return [0.9]

    def data_stream(self, duration=2.0):
        _ = duration
        return [0.1, 0.2, 0.3]

    def save_wav(self, samples, filepath):
        _ = samples
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("wav", encoding="utf-8")
        return path


def _client(monkeypatch, tmp_path):
    monkeypatch.setattr(routes, "service", _SongscribeService())
    monkeypatch.setattr(routes, "ImperialGroovebox", lambda: _Transport())
    monkeypatch.setattr(routes, "get_memory_dir", lambda: tmp_path)
    app = FastAPI()
    app.include_router(routes.router)
    return TestClient(app)


def test_songscribe_transport_bridge_default(monkeypatch, tmp_path):
    client = _client(monkeypatch, tmp_path)
    res = client.post("/api/songscribe/transport/bridge", json={"text": "# Song"})
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["cue"] == "data"
    assert body["sample_count"] == 3
    assert body["wav_path"] is None


def test_songscribe_transport_bridge_save_wav(monkeypatch, tmp_path):
    client = _client(monkeypatch, tmp_path)
    res = client.post(
        "/api/songscribe/transport/bridge",
        json={"text": "# Song", "cue": "handshake", "save_wav": True},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["cue"] == "handshake"
    assert body["sample_count"] == 2
    assert body["wav_path"]
    assert Path(body["wav_path"]).exists()
