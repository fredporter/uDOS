"""Tests for the Wizard MCP Gateway HTTP client wrapper."""
import importlib
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(scope="module")
def gateway_module():
    """Load the gateway module from wizard/mcp/."""
    module_dir = Path(__file__).resolve().parents[1] / "mcp"
    sys.path.insert(0, str(module_dir))
    try:
        return importlib.import_module("gateway")
    finally:
        if str(module_dir) in sys.path:
            sys.path.remove(str(module_dir))


def test_gateway_init_defaults(gateway_module):
    """Test WizardGateway initializes with default base URL."""
    gw = gateway_module.WizardGateway()
    assert gw.base_url == "http://localhost:8765"


def test_gateway_init_custom_url(gateway_module):
    """Test WizardGateway accepts custom base URL."""
    gw = gateway_module.WizardGateway(base_url="http://custom:9000")
    assert gw.base_url == "http://custom:9000"


def test_gateway_init_strips_trailing_slash(gateway_module):
    """Test WizardGateway strips trailing slash from base URL."""
    gw = gateway_module.WizardGateway(base_url="http://localhost:8765/")
    assert gw.base_url == "http://localhost:8765"


def test_gateway_headers_includes_token(gateway_module):
    """Test _headers includes admin token when set."""
    gw = gateway_module.WizardGateway(admin_token="secret123")
    headers = gw._headers()
    assert headers["Content-Type"] == "application/json"
    assert headers["X-Admin-Token"] == "secret123"


def test_gateway_headers_no_token(gateway_module, monkeypatch):
    """Test _headers without admin token."""
    # Clear env var to ensure no token is picked up
    monkeypatch.delenv("WIZARD_ADMIN_TOKEN", raising=False)
    gw = gateway_module.WizardGateway(admin_token=None)
    headers = gw._headers()
    assert headers["Content-Type"] == "application/json"
    assert "X-Admin-Token" not in headers


@patch("requests.get")
def test_gateway_health(mock_get, gateway_module):
    """Test health() calls correct endpoint."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"status": "ok"}
    mock_get.return_value = mock_response

    gw = gateway_module.WizardGateway(base_url="http://test:8000")
    result = gw.health()

    mock_get.assert_called_once_with("http://test:8000/health", timeout=5)
    assert result == {"status": "ok"}


@patch("requests.post")
def test_gateway_ucode_dispatch(mock_post, gateway_module):
    """Test ucode_dispatch() POSTs to correct endpoint."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"result": {"output": "done"}}
    mock_post.return_value = mock_response

    gw = gateway_module.WizardGateway(base_url="http://test:8000", admin_token="tok")
    result = gw.ucode_dispatch("OK")

    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert call_args[0][0] == "http://test:8000/api/ucode/dispatch"
    assert call_args[1]["json"] == {"command": "OK"}
    assert result == {"result": {"output": "done"}}


@patch("requests.get")
def test_gateway_providers_list(mock_get, gateway_module):
    """Test providers_list() calls correct endpoint."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"providers": ["openai", "gpt4all"]}
    mock_get.return_value = mock_response

    gw = gateway_module.WizardGateway(base_url="http://test:8000")
    result = gw.providers_list()

    mock_get.assert_called_once()
    assert "/api/providers" in mock_get.call_args[0][0]
    assert result == {"providers": ["openai", "gpt4all"]}
