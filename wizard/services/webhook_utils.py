"""Webhook helper utilities."""

from __future__ import annotations

import hmac
import hashlib
from typing import Optional

from wizard.services.secret_store import get_secret_store, SecretStoreError


def get_base_url(host: str, port: int) -> str:
    if host == "0.0.0.0":
        host = "localhost"
    return f"http://{host}:{port}"


def resolve_github_webhook_secret(key_id: Optional[str]) -> Optional[str]:
    if not key_id:
        return None
    try:
        store = get_secret_store()
        store.unlock()
        entry = store.get(key_id)
        return entry.value if entry and entry.value else None
    except SecretStoreError:
        return None


def verify_signature(
    body: bytes, signature_header: Optional[str], secret: Optional[str]
) -> bool:
    if not secret:
        return False
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    expected = f"sha256={digest}"
    return hmac.compare_digest(expected, signature_header)
