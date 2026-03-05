from __future__ import annotations

from core.services import dev_state


def _reset_dev_state_cache() -> None:
    dev_state._CACHE_ACTIVE = None
    dev_state._CACHE_TS = 0.0


def test_loopback_wizard_base_url_blocks_non_loopback() -> None:
    assert (
        dev_state._loopback_wizard_base_url("https://wizard.example.com")
        == "http://127.0.0.1:8765"
    )


def test_get_dev_active_uses_loopback_fallback(monkeypatch):
    _reset_dev_state_cache()
    monkeypatch.setenv("WIZARD_BASE_URL", "https://wizard.example.com")
    monkeypatch.setenv("WIZARD_ADMIN_TOKEN", "abc123")
    calls = {}

    def _fake_http_get(url: str, headers=None, timeout=5):
        calls["url"] = url
        calls["headers"] = headers or {}
        calls["timeout"] = timeout
        return {"status_code": 200, "json": {"active": True}}

    monkeypatch.setattr(dev_state, "http_get", _fake_http_get)
    assert dev_state.get_dev_active(force=True) is True
    assert calls["url"] == "http://127.0.0.1:8765/api/dev/status"
    assert calls["headers"]["X-Admin-Token"] == "abc123"
