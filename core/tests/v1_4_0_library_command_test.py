"""Tests for v1.4.0 LIBRARY command - sync/status surfaces."""

from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def handler():
    from core.commands.library_handler import LibraryHandler
    return LibraryHandler()


def _mock_integration(name: str, enabled: bool = False, installed: bool = False):
    m = MagicMock()
    m.name = name
    m.path = f"/repo/library/{name}"
    m.source = "library"
    m.enabled = enabled
    m.installed = installed
    m.cloned = installed
    return m


def _mock_status(names=("sonic", "groovebox"), enabled=()):
    status = MagicMock()
    status.integrations = [_mock_integration(n, n in enabled) for n in names]
    return status


class TestLibraryHandlerStatus:
    def test_status_returns_success(self, handler):
        with patch.object(handler, "_get_manager") as mock_mgr:
            mock_mgr.return_value.get_library_status.return_value = _mock_status()
            result = handler.handle("LIBRARY", [], None, None)
        assert result["status"] == "success"
        assert result["total"] == 2
        assert "sonic" in result["integrations"]

    def test_status_subcommand(self, handler):
        with patch.object(handler, "_get_manager") as mock_mgr:
            mock_mgr.return_value.get_library_status.return_value = _mock_status()
            result = handler.handle("LIBRARY", ["STATUS"], None, None)
        assert result["status"] == "success"

    def test_list_alias(self, handler):
        with patch.object(handler, "_get_manager") as mock_mgr:
            mock_mgr.return_value.get_library_status.return_value = _mock_status()
            result = handler.handle("LIBRARY", ["LIST"], None, None)
        assert result["status"] == "success"

    def test_enabled_count(self, handler):
        with patch.object(handler, "_get_manager") as mock_mgr:
            mock_mgr.return_value.get_library_status.return_value = _mock_status(
                names=("sonic", "groovebox"), enabled=("sonic",)
            )
            result = handler.handle("LIBRARY", [], None, None)
        assert result["enabled"] == 1

    def test_output_contains_integrations(self, handler):
        with patch.object(handler, "_get_manager") as mock_mgr:
            mock_mgr.return_value.get_library_status.return_value = _mock_status()
            result = handler.handle("LIBRARY", [], None, None)
        assert "sonic" in result["output"]
        assert "groovebox" in result["output"]

    def test_status_error_path(self, handler):
        with patch.object(handler, "_get_manager", side_effect=RuntimeError("fail")):
            result = handler.handle("LIBRARY", ["STATUS"], None, None)
        assert result["status"] == "error"


class TestLibraryHandlerSync:
    def test_sync_returns_success(self, handler):
        with patch.object(handler, "_get_manager") as mock_mgr:
            mock_mgr.return_value.get_library_status.return_value = _mock_status()
            result = handler.handle("LIBRARY", ["SYNC"], None, None)
        assert result["status"] == "success"
        assert "sync complete" in result["message"].lower()

    def test_sync_reports_count(self, handler):
        with patch.object(handler, "_get_manager") as mock_mgr:
            mock_mgr.return_value.get_library_status.return_value = _mock_status(
                names=("sonic", "groovebox", "nethack")
            )
            result = handler.handle("LIBRARY", ["SYNC"], None, None)
        assert result["total"] == 3

    def test_sync_error_path(self, handler):
        with patch.object(handler, "_get_manager", side_effect=RuntimeError("db error")):
            result = handler.handle("LIBRARY", ["SYNC"], None, None)
        assert result["status"] == "error"


class TestLibraryHandlerInfo:
    def test_info_found(self, handler):
        intg = _mock_integration("sonic")
        with patch.object(handler, "_get_manager") as mock_mgr:
            mock_mgr.return_value.get_integration.return_value = intg
            result = handler.handle("LIBRARY", ["INFO", "sonic"], None, None)
        assert result["status"] == "success"
        assert result["name"] == "sonic"
        assert "sonic" in result["output"]

    def test_info_not_found(self, handler):
        with patch.object(handler, "_get_manager") as mock_mgr:
            mock_mgr.return_value.get_integration.return_value = None
            result = handler.handle("LIBRARY", ["INFO", "nosuchlib"], None, None)
        assert result["status"] == "error"
        assert "not found" in result["message"]

    def test_info_missing_name(self, handler):
        result = handler.handle("LIBRARY", ["INFO"], None, None)
        assert result["status"] == "error"
        assert "Usage" in result["message"]


class TestLibraryHandlerHelp:
    def test_help_subcommand(self, handler):
        result = handler.handle("LIBRARY", ["HELP"], None, None)
        assert result["status"] == "success"
        assert "LIBRARY" in result["output"]
        assert "STATUS" in result["output"]
        assert "SYNC" in result["output"]

    def test_unknown_action(self, handler):
        result = handler.handle("LIBRARY", ["BOGUS"], None, None)
        assert result["status"] == "error"
        assert "LIBRARY HELP" in result["message"]
