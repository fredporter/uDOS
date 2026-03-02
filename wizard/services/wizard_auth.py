"""Wizard authentication helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import base64
import hashlib
import hmac
import json
import os
from typing import TYPE_CHECKING

from core.services.unified_config_loader import get_config
from wizard.services.device_auth import get_device_auth
from wizard.services.deploy_mode import is_managed_mode
from wizard.services.secret_store import SecretStoreError, get_secret_store
from wizard.services.store import get_wizard_store

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

    def __init__(self, config, logger: Logger):
        self.config = config
        self.logger = logger
        self.sessions: dict[str, DeviceSession] = {}
        self.store = get_wizard_store()

    async def authenticate_device(self, request: Request) -> str:
        from fastapi import HTTPException

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing authorization")

        token = auth_header[7:]
        device_id = token.split(":")[0] if ":" in token else token[:16]
        auth = get_device_auth()
        if not auth.get_device(device_id):
            raise HTTPException(status_code=401, detail="Unknown device")

        now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
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

    async def authenticate_admin(self, request: Request) -> None:
        from fastapi import HTTPException

        if is_managed_mode():
            try:
                profile = self._authenticate_operator_session(request)
            except ValueError as exc:
                raise HTTPException(status_code=401, detail=str(exc)) from exc
            if profile.get("role") not in {"admin", "operator"}:
                raise HTTPException(status_code=403, detail="Operator role required")
            request.state.operator = profile
            return

        key_id = getattr(self.config, "admin_api_key_id", None)
        auth_header = request.headers.get("Authorization", "").strip()

        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=401, detail="Missing or invalid Authorization header"
            )

        token = auth_header[7:].strip()
        if not token or len(token) < 8:
            raise HTTPException(status_code=401, detail="Invalid token format")

        env_token = get_config("WIZARD_ADMIN_TOKEN", "").strip()
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
                raise HTTPException(status_code=503, detail="Admin secret store locked")

        raise HTTPException(status_code=403, detail="Invalid admin token")

    def get_operator_session(self, request: Request) -> dict[str, object]:
        profile = self._authenticate_operator_session(request)
        return {
            "subject": profile.get("subject"),
            "email": profile.get("email"),
            "display_name": profile.get("display_name"),
            "role": profile.get("role"),
            "claims": profile.get("claims", {}),
        }

    def _authenticate_operator_session(self, request: Request) -> dict[str, object]:
        from fastapi import HTTPException

        token = self._extract_bearer_or_cookie_token(request)
        if not token:
            raise HTTPException(status_code=401, detail="Missing operator session token")
        claims = self._decode_supabase_jwt(token)
        if not claims.get("sub"):
            raise HTTPException(status_code=401, detail="Invalid operator subject")
        profile = self.store.get_operator_profile(
            str(claims["sub"]),
            email=claims.get("email"),
        )
        return {
            "subject": profile.get("subject"),
            "email": profile.get("email"),
            "display_name": profile.get("display_name") or claims.get("email") or claims.get("sub"),
            "role": profile.get("role", "operator"),
            "claims": claims,
        }

    def _extract_bearer_or_cookie_token(self, request: Request) -> str:
        auth_header = request.headers.get("Authorization", "").strip()
        if auth_header.startswith("Bearer "):
            return auth_header[7:].strip()
        for cookie_name in ("udos_operator_jwt", "sb-access-token"):
            token = request.cookies.get(cookie_name, "").strip()
            if token:
                return token
        return ""

    def _decode_supabase_jwt(self, token: str) -> dict[str, object]:
        header_b64, payload_b64, signature_b64 = token.split(".")
        header = self._jwt_json(header_b64)
        claims = self._jwt_json(payload_b64)
        if header.get("alg") != "HS256":
            raise ValueError("Unsupported operator token algorithm")
        secret = (
            os.environ.get("SUPABASE_JWT_SECRET")
            or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
            or ""
        ).strip()
        if not secret:
            raise ValueError("Missing SUPABASE_JWT_SECRET for managed auth")
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        expected = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
        actual = self._jwt_b64decode(signature_b64)
        if not hmac.compare_digest(expected, actual):
            raise ValueError("Invalid operator token signature")
        issuer = (os.environ.get("SUPABASE_JWT_ISSUER") or "").strip()
        audience = (os.environ.get("SUPABASE_JWT_AUDIENCE") or "").strip()
        if issuer and claims.get("iss") != issuer:
            raise ValueError("Operator token issuer mismatch")
        aud = claims.get("aud")
        if audience:
            if isinstance(aud, list) and audience not in aud:
                raise ValueError("Operator token audience mismatch")
            if isinstance(aud, str) and aud != audience:
                raise ValueError("Operator token audience mismatch")
        exp = claims.get("exp")
        if isinstance(exp, (int, float)) and float(exp) < datetime.now(UTC).timestamp():
            raise ValueError("Operator token expired")
        return claims

    def _jwt_json(self, segment: str) -> dict[str, object]:
        return json.loads(self._jwt_b64decode(segment).decode("utf-8"))

    def _jwt_b64decode(self, value: str) -> bytes:
        padding = "=" * (-len(value) % 4)
        return base64.urlsafe_b64decode(f"{value}{padding}")
