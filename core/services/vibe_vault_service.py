"""
Vibe Vault Service

Manages secret/credential storage and retrieval.
Integrates with uDOS vault backend for secure key storage.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from core.services.logging_manager import get_logger
from core.services.persistence_service import get_persistence_service


class VibeVaultService:
    """Manage secrets, credentials, and sensitive data."""

    _DATA_FILE = "vault"

    def __init__(self):
        """Initialize vault service."""
        self.logger = get_logger("vibe-vault-service")
        self.persistence_service = get_persistence_service()
        self.vault_data: Dict[str, Dict[str, Any]] = {}
        self._load_vault()

    def _load_vault(self) -> None:
        """Load vault from persistent storage."""
        self.logger.debug("Loading vault data from persistence...")
        data = self.persistence_service.read_data(self._DATA_FILE)
        if data and "vault" in data:
            self.vault_data = data["vault"]
            self.logger.info(f"Loaded {len(self.vault_data)} vault keys.")
        else:
            self.logger.warning("No persistent vault data found.")

    def _save_vault(self) -> None:
        """Save vault to persistent storage."""
        self.logger.debug("Saving vault data to persistence...")
        data = {"vault": self.vault_data}
        self.persistence_service.write_data(self._DATA_FILE, data)

    def list_keys(
        self,
        pattern: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List all vault keys (without exposing values).

        Args:
            pattern: Filter keys by pattern (substring match)

        Returns:
            Dict with status and list of key metadata (without values)
        """
        keys = list(self.vault_data.keys())

        if pattern:
            keys = [k for k in keys if pattern.lower() in k.lower()]

        key_metadata = []
        for key in keys:
            metadata = {
                "key": key,
                "type": self.vault_data[key].get("type", "string"),
                "created": self.vault_data[key].get("created"),
                "last_updated": self.vault_data[key].get("last_updated"),
                "ttl": self.vault_data[key].get("ttl"),
            }
            key_metadata.append(metadata)

        return {
            "status": "success",
            "keys": key_metadata,
            "count": len(keys),
        }

    def get_secret(self, key: str) -> Dict[str, Any]:
        """
        Retrieve a secret value by key.

        Args:
            key: Secret key

        Returns:
            Dict with status and secret value (redacted in logs)
        """
        if key not in self.vault_data:
            return {
                "status": "error",
                "message": f"Secret not found: {key}",
            }

        secret_data = self.vault_data[key]

        # Log access without exposing value
        self.logger.info(f"Retrieved secret: {key}")

        return {
            "status": "success",
            "key": key,
            "value": secret_data.get("value"),  # Phase 4: Decrypt if needed
            "type": secret_data.get("type", "string"),
        }

    def set_secret(
        self,
        key: str,
        value: str,
        secret_type: str = "string",
        ttl: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Store a secret value.

        Args:
            key: Secret key
            value: Secret value
            secret_type: Type of secret (string|cert|token|connection_string)
            ttl: Time-to-live in seconds (optional)

        Returns:
            Dict with success status
        """
        now = datetime.now().isoformat()

        # Get existing created time if updating, otherwise use now
        created = now
        if key in self.vault_data:
            created = self.vault_data[key].get("created", now)

        self.vault_data[key] = {
            "value": value,
            "type": secret_type,
            "created": created,
            "last_updated": now,
            "ttl": ttl,
        }
        self._save_vault()

        self.logger.info(f"Stored secret: {key} (type: {secret_type})")

        return {
            "status": "success",
            "message": f"Secret stored: {key}",
            "key": key,
        }

    def delete_secret(self, key: str) -> Dict[str, Any]:
        """
        Remove a secret from the vault.

        Args:
            key: Secret key to delete

        Returns:
            Dict with success status
        """
        if key not in self.vault_data:
            return {
                "status": "error",
                "message": f"Secret not found: {key}",
            }

        del self.vault_data[key]
        self._save_vault()
        self.logger.info(f"Deleted secret: {key}")

        return {
            "status": "success",
            "message": f"Secret deleted: {key}",
        }


# Global singleton
_vault_service: Optional[VibeVaultService] = None


def get_vault_service() -> VibeVaultService:
    """Get or create the global vault service."""
    global _vault_service
    if _vault_service is None:
        _vault_service = VibeVaultService()
    return _vault_service
