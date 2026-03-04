"""Boundary policy tests for uCODE networking helpers."""

from __future__ import annotations

from core.tui.ucode import UCODE


class _LoggerStub:
    def warning(self, *_args, **_kwargs) -> None:
        return None


def _ucode_stub() -> UCODE:
    ucode = UCODE.__new__(UCODE)
    ucode.logger = _LoggerStub()
    ucode._env_file_cache = {}
    return ucode


def test_resolve_loopback_url_accepts_localhost() -> None:
    ucode = _ucode_stub()
    resolved = ucode._resolve_loopback_url(
        "http://localhost:8765",
        fallback="http://127.0.0.1:8765",
        context="WIZARD_BASE_URL",
    )
    assert resolved == "http://localhost:8765"


def test_resolve_loopback_url_blocks_non_loopback() -> None:
    ucode = _ucode_stub()
    resolved = ucode._resolve_loopback_url(
        "https://wizard.example.com",
        fallback="http://127.0.0.1:8765",
        context="WIZARD_BASE_URL",
    )
    assert resolved == "http://127.0.0.1:8765"


def test_wizard_base_url_falls_back_to_loopback(monkeypatch) -> None:
    ucode = _ucode_stub()
    monkeypatch.setattr(ucode, "_env_value", lambda key: "https://wizard.example.com")
    assert ucode._wizard_base_url() == "http://127.0.0.1:8765"


def test_resolve_loopback_url_sanitizes_local_model_endpoint() -> None:
    """Test that non-loopback endpoints are sanitized to localhost."""
    ucode = _ucode_stub()
    resolved = ucode._resolve_loopback_url(
        "http://local-model-host",
        fallback="http://127.0.0.1:11434",
        context="LOGIC_ASSIST_ENDPOINT",
    )
    assert resolved == "http://127.0.0.1:11434"
