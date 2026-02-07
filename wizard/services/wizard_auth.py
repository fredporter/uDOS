"""Wizard authentication helpers."""

from __future__ import annotations

import hmac
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, TYPE_CHECKING

from wizard.services.secret_store import get_secret_store, SecretStoreError
from wizard.services.device_auth import get_device_auth

if TYPE_CHECKING:  # pragma: no cover
    from fastapi import Request
    from wizard.services.logging_api import Logger


@dataclass
class DeviceSession:
    """Authenticated device session."""

    device_id: str
    device_name: str
    authenticated_at: str
    last_request: str
    request_count: int = 0
    ai_cost_today: float = 0.0


class WizardAuthService:
    """Handle device/admin authentication and session tracking."""

    def __init__(self, config, logger: "Logger"):
        self.config = config
        self.logger = logger
        self.sessions: Dict[str, DeviceSession] = {}

    async def authenticate_device(self, request: "Request") -> str:
        from fastapi import HTTPException

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing authorization")

        token = auth_header[7:]
        device_id = token.split(":")[0] if ":" in token else token[:16]
        auth = get_device_auth()
        if not auth.get_device(device_id):
            raise HTTPException(status_code=401, detail="Unknown device")

        now = datetime.utcnow().isoformat() + "Z"
        if device_id not in self.sessions:
            self.sessions[device_id] = DeviceSession(
                device_id=device_id,
                device_name="Unknown",
                authenticated_at=now,
                last_request=now,
            )

        session = self.sessions[device_id]
        session.last_request = now
        session.request_count += 1
        return device_id

    async def authenticate_admin(self, request: "Request") -> None:
        from fastapi import HTTPException

        key_id = getattr(self.config, "admin_api_key_id", None)
        auth_header = request.headers.get("Authorization", "").strip()

        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=401, detail="Missing or invalid Authorization header"
            )

        token = auth_header[7:].strip()
        if not token or len(token) < 8:
            raise HTTPException(status_code=401, detail="Invalid token format")

        env_token = os.getenv("WIZARD_ADMIN_TOKEN", "").strip()
        if env_token and hmac.compare_digest(token, env_token):
            return

        if not key_id:
            raise HTTPException(
                status_code=503, detail="Admin authentication not configured"
            )

        try:
            store = get_secret_store()
            store.unlock()
            entry = store.get(key_id)
            if entry and entry.value and hmac.compare_digest(token, entry.value):
                return
        except SecretStoreError as exc:
            self.logger.warn("[WIZ] Secret store error during auth: %s", exc)
            if not env_token:
                raise HTTPException(
                    status_code=503, detail="Admin secret store locked"
                )

        raise HTTPException(status_code=403, detail="Invalid admin token")
