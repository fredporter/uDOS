from __future__ import annotations

from wizard.services.secret_store import SecretStoreError, get_secret_store


class SecretStoreAdapter:
    """Core-provider adapter for Wizard's secret store."""

    def get(self, key: str) -> str | None:
        try:
            store = get_secret_store()
            store.unlock()
            entry = store.get(key)
        except SecretStoreError:
            return None
        if not entry or not entry.value:
            return None
        return entry.value
