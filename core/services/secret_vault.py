"""
Admin Secret Contract

Provides a stable interface for accessing admin/cloud provider secrets
from the uDOS vault. Used by OK provider handlers to check for API keys.
"""

from __future__ import annotations

from typing import Optional

from core.services.logging_manager import get_logger

_logger = get_logger("admin-secret-contract")


class SecureVault:
    """Thin contract interface for reading secrets from the vault.

    Returns raw secret values (not the dict envelope from VibeVaultService).
    Failures are silenced so callers can treat missing secrets as unconfigured.
    """

    def get_secret(self, key: str) -> Optional[str]:
        """Retrieve a secret value by key.

        Args:
            key: Secret identifier (e.g. "mistral_api_key")

        Returns:
            The secret string value, or None if not found / vault unavailable.
        """
        try:
            from core.services.vibe_vault_service import VibeVaultService

            vault = VibeVaultService()
            result = vault.get_secret(key)
            if isinstance(result, dict) and result.get("status") == "success":
                return result.get("value") or result.get("data", {}).get("value")
            return None
        except Exception as exc:
            _logger.debug("SecureVault.get_secret(%r) unavailable: %s", key, exc)
            return None
