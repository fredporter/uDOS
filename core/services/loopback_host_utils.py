"""Shared loopback host normalization and checks for v1.5 runtime surfaces."""

from __future__ import annotations

LOOPBACK_HOSTS = frozenset({"127.0.0.1", "::1", "localhost"})
WILDCARD_HOSTS = frozenset({"0.0.0.0", "::"})
DEFAULT_LOOPBACK_HOST = "127.0.0.1"


def normalize_host(host: str | None) -> str:
    """Normalize host token for membership checks."""
    return (host or "").strip().lower()


def is_loopback_host(host: str | None) -> bool:
    """Return True when host resolves to a loopback token."""
    return normalize_host(host) in LOOPBACK_HOSTS


def normalize_loopback_host(
    host: str | None,
    *,
    fallback: str = DEFAULT_LOOPBACK_HOST,
    convert_wildcard: bool = True,
) -> str:
    """Normalize host to a deterministic loopback address when needed."""
    normalized = normalize_host(host)
    if normalized in LOOPBACK_HOSTS:
        return normalized
    if convert_wildcard and normalized in WILDCARD_HOSTS:
        return fallback
    return host.strip() if isinstance(host, str) else fallback


def extract_host_from_url(raw_url: str | None) -> str | None:
    """Extract host token from a URL-like value without URL parser imports."""
    value = (raw_url or "").strip()
    if not value:
        return None
    if "://" in value:
        value = value.split("://", 1)[1]
    value = value.split("/", 1)[0]
    if "@" in value:
        value = value.rsplit("@", 1)[1]
    if value.startswith("[") and "]" in value:
        return value[1 : value.find("]")]
    if ":" in value:
        value = value.rsplit(":", 1)[0]
    return value or None
