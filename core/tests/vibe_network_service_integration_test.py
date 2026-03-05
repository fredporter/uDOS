"""Integration-style tests for VibeNetworkService failure/recovery paths."""

from __future__ import annotations

from core.services.dev_mode_compat.network_service import VibeNetworkService


class _DummySocket:
    def __enter__(self) -> "_DummySocket":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False


def test_connect_host_failure_then_recovery(monkeypatch) -> None:
    service = VibeNetworkService()
    results = [OSError("down"), _DummySocket()]

    def _fake_create_connection(*_args, **_kwargs):
        next_value = results.pop(0)
        if isinstance(next_value, Exception):
            raise next_value
        return next_value

    monkeypatch.setattr(
        "core.services.dev_mode_compat.network_service.socket.create_connection",
        _fake_create_connection,
    )

    first = service.connect_host("127.0.0.1", 80)
    second = service.connect_host("127.0.0.1", 80)

    assert first["status"] == "error"
    assert first["connected"] is False
    assert second["status"] == "success"
    assert second["connected"] is True


def test_check_connectivity_unreachable_then_recovery(monkeypatch) -> None:
    service = VibeNetworkService()
    results = [OSError("timeout"), _DummySocket()]

    def _fake_create_connection(*_args, **_kwargs):
        next_value = results.pop(0)
        if isinstance(next_value, Exception):
            raise next_value
        return next_value

    monkeypatch.setattr(
        "core.services.dev_mode_compat.network_service.socket.create_connection",
        _fake_create_connection,
    )

    first = service.check_connectivity("127.0.0.1")
    second = service.check_connectivity("127.0.0.1")

    assert first["status"] == "error"
    assert first["reachable"] is False
    assert second["status"] == "success"
    assert second["reachable"] is True


def test_scan_network_invalid_subnet_returns_error() -> None:
    service = VibeNetworkService()
    result = service.scan_network("not-a-subnet", timeout=1)
    assert result["status"] == "warning"
    assert result["code"] == "wizard_required"


def test_non_loopback_targets_require_wizard() -> None:
    service = VibeNetworkService()

    connect = service.connect_host("8.8.8.8", 53)
    assert connect["status"] == "warning"
    assert connect["code"] == "wizard_required"

    check = service.check_connectivity("1.1.1.1")
    assert check["status"] == "warning"
    assert check["code"] == "wizard_required"

    scan = service.scan_network("192.168.1.0/24", timeout=1)
    assert scan["status"] == "warning"
    assert scan["code"] == "wizard_required"
