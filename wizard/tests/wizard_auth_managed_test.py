import base64
import hashlib
import hmac
import json
from types import SimpleNamespace

from wizard.services import wizard_auth as auth_module


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _jwt(secret: str, payload: dict) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    head = _b64(json.dumps(header).encode("utf-8"))
    body = _b64(json.dumps(payload).encode("utf-8"))
    signature = hmac.new(secret.encode("utf-8"), f"{head}.{body}".encode("utf-8"), hashlib.sha256).digest()
    return f"{head}.{body}.{_b64(signature)}"


def test_managed_operator_session_from_cookie(monkeypatch):
    class FakeStore:
        def get_operator_profile(self, subject, email=None):
            return {
                "subject": subject,
                "email": email,
                "display_name": "Ops User",
                "role": "admin",
            }

    monkeypatch.setattr(auth_module, "get_wizard_store", lambda: FakeStore())
    monkeypatch.setattr(auth_module, "is_managed_mode", lambda: True)
    monkeypatch.setenv("SUPABASE_JWT_SECRET", "secret")
    monkeypatch.setenv("SUPABASE_JWT_ISSUER", "https://example.supabase.co/auth/v1")
    monkeypatch.setenv("SUPABASE_JWT_AUDIENCE", "authenticated")

    service = auth_module.WizardAuthService(config=SimpleNamespace(admin_api_key_id=None), logger=SimpleNamespace(warn=lambda *args, **kwargs: None))
    token = _jwt(
        "secret",
        {
            "sub": "user-1",
            "email": "user@example.com",
            "iss": "https://example.supabase.co/auth/v1",
            "aud": "authenticated",
            "exp": 4102444800,
        },
    )
    request = SimpleNamespace(headers={}, cookies={"udos_operator_jwt": token}, state=SimpleNamespace())

    session = service.get_operator_session(request)
    assert session["role"] == "admin"
    assert session["email"] == "user@example.com"
