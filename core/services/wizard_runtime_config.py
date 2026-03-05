"""Canonical Wizard runtime URL helpers for v1.5."""

from __future__ import annotations

from urllib.parse import urlparse

from core.services.unified_config_loader import get_config, get_int_config

DEFAULT_WIZARD_HOST = "localhost"
DEFAULT_WIZARD_PORT = 8765
_LOOPBACK_HOSTS = frozenset({"127.0.0.1", "::1", "localhost"})


def get_wizard_port(default: int = DEFAULT_WIZARD_PORT) -> int:
    """Return the configured Wizard port."""
    return get_int_config("WIZARD_PORT", default)


def get_default_wizard_base_url(host: str = DEFAULT_WIZARD_HOST) -> str:
    """Return the canonical default Wizard base URL."""
    return f"http://{host}:{get_wizard_port()}"


def get_wizard_base_url(raw_base_url: str | None = None) -> str:
    """Return the configured Wizard base URL or the canonical default."""
    candidate = (raw_base_url or get_config("WIZARD_BASE_URL", "")).strip().rstrip("/")
    return candidate or get_default_wizard_base_url()


def get_loopback_wizard_base_url(
    raw_base_url: str | None = None,
    *,
    fallback_host: str = DEFAULT_WIZARD_HOST,
) -> str:
    """Return a loopback Wizard URL, falling back to the canonical default."""
    candidate = get_wizard_base_url(raw_base_url)
    parsed = urlparse(candidate)
    host = (parsed.hostname or "").strip().lower()
    if host in _LOOPBACK_HOSTS:
        return candidate
    return get_default_wizard_base_url(host=fallback_host)


def get_wizard_dashboard_url(raw_base_url: str | None = None, path: str = "/dashboard") -> str:
    """Return a Wizard dashboard/config URL."""
    base_url = get_wizard_base_url(raw_base_url)
    normalized_path = path if path.startswith("/") else f"/{path}"
    return f"{base_url}{normalized_path}"


def get_wizard_oauth_callback_url(raw_base_url: str | None = None) -> str:
    """Return the canonical Wizard OAuth callback URL."""
    return get_wizard_dashboard_url(raw_base_url, "/oauth/callback")
