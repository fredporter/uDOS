"""Tests for typed backend error mapping in the Dev Mode tool CLI handler."""

from core.services.vibe_cli_handler import (
    BackendErrorCode,
    DevModeToolCliHandler,
    VibeCliHandler,
    _infer_error_code,
)


def test_canonical_cli_handler_alias_is_stable() -> None:
    assert DevModeToolCliHandler is VibeCliHandler


def test_infer_error_code_not_found() -> None:
    assert _infer_error_code("Workspace not found: demo") == BackendErrorCode.NOT_FOUND


def test_infer_error_code_timeout() -> None:
    assert _infer_error_code("Request timed out while contacting provider") == BackendErrorCode.TIMEOUT


def test_format_output_normalizes_error_key_and_sets_retryable() -> None:
    handler = VibeCliHandler()
    result = handler._format_output(
        {
            "status": "error",
            "error": "No credentials for github",
            "backend": "sync",
        }
    )

    assert result["status"] == "error"
    assert result["data"]["error"]["code"] == BackendErrorCode.AUTH_REQUIRED.value
    assert result["data"]["error"]["backend"] == "sync"
    assert result["data"]["error"]["retryable"] is False


def test_execute_maps_exception_to_typed_error(monkeypatch) -> None:
    handler = VibeCliHandler()

    def _raise_timeout(_action: str, _args: list[str]) -> dict[str, str]:
        raise TimeoutError("backend timeout")

    monkeypatch.setattr(handler, "_handle_device", _raise_timeout)

    result = handler.execute("DEVICE LIST")

    assert result["status"] == "error"
    assert result["data"]["error"]["code"] == BackendErrorCode.TIMEOUT.value
    assert result["data"]["error"]["backend"] == "device"
    assert result["data"]["error"]["retryable"] is True
