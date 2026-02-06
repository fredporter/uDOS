"""
Wizard Secret Store
===================

Encrypted secret storage for the Wizard server using a tomb-style blob.
- Encrypted at rest (Fernet / cryptography). If cryptography is missing, the
  store refuses to load.
- Keys provided via env (`WIZARD_KEY`) or explicit argument.
- Decrypts into memory-only structures; no plaintext persisted.

This module intentionally avoids OS keychain/keyring. Unlock failures keep
sensitive routes disabled until the operator provides a valid key.
"""

from __future__ import annotations

import base64
import json
import os
import hashlib
from datetime import datetime
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, Optional, List, Any

from wizard.services.logging_manager import get_logger

logger = get_logger("secret-store")

try:
    from cryptography.fernet import Fernet, InvalidToken

    CRYPTO_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    Fernet = None
    InvalidToken = Exception
    CRYPTO_AVAILABLE = False


class SecretStoreError(Exception):
    """Raised for secret store failures."""


@dataclass
class SecretEntry:
    """Single secret entry (kept in memory only once decrypted)."""

    key_id: str
    provider: str
    value: str
    version: int = 1
    created_at: str = ""
    rotated_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecretStoreConfig:
    """Config for locating and unlocking the tomb."""

    tomb_path: Path = Path(__file__).parent.parent / "secrets.tomb"
    key_env: str = "WIZARD_KEY"
    secondary_key_env: Optional[str] = "WIZARD_KEY_PEER"
    key_file_path: Path = (
        Path(__file__).resolve().parents[2]
        / "memory"
        / "private"
        / "wizard_secret_store.key"
    )


class SecretStore:
    """Encrypted secret store with in-memory cache."""

    def __init__(self, config: Optional[SecretStoreConfig] = None):
        self.config = config or SecretStoreConfig()
        self._fernet: Optional[Fernet] = None
        self._cache: Dict[str, SecretEntry] = {}
        self._loaded = False

    def _derive_key(self, raw: str) -> bytes:
        """Derive a Fernet-compatible key from arbitrary text."""
        digest = hashlib.sha256(raw.encode("utf-8")).digest()
        return base64.urlsafe_b64encode(digest)

    def _get_fernet(self, key_material: Optional[str]) -> Fernet:
        if not CRYPTO_AVAILABLE:
            raise SecretStoreError(
                "cryptography is required. Install with: pip install cryptography"
            )
        if not key_material:
            raise SecretStoreError("No key material provided to unlock tomb")
        return Fernet(self._derive_key(key_material))

    def unlock(self, key_material: Optional[str] = None):
        """Unlock the tomb and load secrets into memory."""
        if self._loaded:
            return
        env_key = key_material or os.getenv(self.config.key_env)
        fallback_key = os.getenv(self.config.secondary_key_env) if not env_key else None
        file_key = None
        if self.config.key_file_path.exists():
            try:
                file_key = self.config.key_file_path.read_text().strip()
            except Exception:
                file_key = None

        tomb = self.config.tomb_path
        if not tomb.exists():
            logger.warning("[WIZ] secret tomb not found; starting empty store")
            # Still need to set up _fernet for persistence even if tomb doesn't exist
            # Use the provided key or env key
            if env_key:
                self._fernet = self._get_fernet(env_key)
            elif fallback_key:
                self._fernet = self._get_fernet(fallback_key)
            elif file_key:
                self._fernet = self._get_fernet(file_key)
            else:
                raise SecretStoreError("No key material provided to unlock tomb")
            self._cache = {}
            self._loaded = True
            return

        data = tomb.read_bytes()
        decrypted = None
        last_error: Optional[Exception] = None
        for candidate in (env_key, fallback_key, file_key):
            if not candidate:
                continue
            try:
                self._fernet = self._get_fernet(candidate)
                decrypted = self._fernet.decrypt(data)
                break
            except InvalidToken as exc:
                last_error = exc
            except SecretStoreError as exc:
                last_error = exc

        if decrypted is None:
            raise SecretStoreError("Unable to decrypt tomb with provided key") from last_error

        payload = json.loads(decrypted.decode("utf-8"))
        secrets = payload.get("secrets", [])
        cache: Dict[str, SecretEntry] = {}
        for entry in secrets:
            se = SecretEntry(**entry)
            cache[se.key_id] = se
        self._cache = cache
        self._loaded = True
        logger.info("[WIZ] secret tomb unlocked", extra={"entries": len(self._cache)})

    def _persist(self):
        if not self._fernet:
            raise SecretStoreError("Store is locked; cannot persist")
        tomb = self.config.tomb_path
        payload = {"version": 1, "secrets": [asdict(v) for v in self._cache.values()]}
        encrypted = self._fernet.encrypt(json.dumps(payload).encode("utf-8"))
        tomb.parent.mkdir(parents=True, exist_ok=True)
        with open(tomb, "wb") as fh:
            fh.write(encrypted)

    def list(self) -> List[SecretEntry]:
        self._ensure_loaded()
        return list(self._cache.values())

    def get_entry(self, key_id: str) -> Optional[SecretEntry]:
        self._ensure_loaded()
        return self._cache.get(key_id)

    def get(self, key_id: str) -> Optional[SecretEntry]:
        self._ensure_loaded()
        return self._cache.get(key_id)

    def set_entry(
        self,
        key_id: str,
        value: str,
        metadata: Optional[Dict[str, Any]] = None,
        provider: str = "manual",
    ):
        self._ensure_loaded()
        entry = SecretEntry(
            key_id=key_id,
            provider=provider,
            value=value,
            created_at=datetime.utcnow().isoformat(),
            metadata=metadata or {},
        )
        self._cache[key_id] = entry
        self._persist()

    def set(self, entry: SecretEntry):
        self._ensure_loaded()
        self._cache[entry.key_id] = entry
        self._persist()

    def rotate(self, key_id: str, new_value: str, rotated_at: str):
        self._ensure_loaded()
        current = self._cache.get(key_id)
        if not current:
            raise SecretStoreError(f"Unknown key_id: {key_id}")
        updated = SecretEntry(
            key_id=key_id,
            provider=current.provider,
            value=new_value,
            version=current.version + 1,
            created_at=current.created_at,
            rotated_at=rotated_at,
            metadata=current.metadata,
        )
        self._cache[key_id] = updated
        self._persist()

    def _ensure_loaded(self):
        if not self._loaded:
            raise SecretStoreError("Secret store is locked or not initialized")


def get_secret_store(config: Optional[SecretStoreConfig] = None) -> SecretStore:
    """Singleton-ish accessor for the secret store."""
    if not hasattr(get_secret_store, "_instance"):
        setattr(get_secret_store, "_instance", SecretStore(config))
    return getattr(get_secret_store, "_instance")
