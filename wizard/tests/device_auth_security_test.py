from __future__ import annotations

import wizard.services.device_auth as device_auth_module
from wizard.services.device_auth import DeviceAuthService
from wizard.services.store.sqlite_store import SQLiteWizardStore


def test_device_tokens_are_issued_and_validated(tmp_path, monkeypatch):
    monkeypatch.setattr(device_auth_module, "WIZARD_DATA", tmp_path / "wizard")
    monkeypatch.setattr(device_auth_module, "DEVICES_FILE", tmp_path / "wizard" / "devices.json")
    monkeypatch.setattr(device_auth_module, "SESSIONS_FILE", tmp_path / "wizard" / "sessions.json")
    monkeypatch.setattr(device_auth_module, "is_managed_mode", lambda: False)

    auth = DeviceAuthService()
    pairing = auth.create_pairing_request()
    device = auth.complete_pairing(
        code=pairing.code,
        device_id="device-1",
        device_name="Phone",
    )
    assert device is not None

    token = auth.rotate_device_token("device-1")
    assert token
    assert auth.authenticate_bearer_token(token).id == "device-1"
    assert auth.authenticate_bearer_token(f"{token}-tampered") is None
    assert "token_hash" not in auth.get_device("device-1").to_dict()


def test_managed_mode_device_registry_survives_restart(tmp_path, monkeypatch):
    store = SQLiteWizardStore(tmp_path / "ops.db")
    monkeypatch.setattr(device_auth_module, "is_managed_mode", lambda: True)

    auth = DeviceAuthService(store=store)
    pairing = auth.create_pairing_request()
    device = auth.complete_pairing(
        code=pairing.code,
        device_id="device-2",
        device_name="Tablet",
    )
    assert device is not None
    token = auth.rotate_device_token("device-2")

    reloaded = DeviceAuthService(store=store)
    assert reloaded.get_device("device-2") is not None
    assert reloaded.authenticate_bearer_token(token).id == "device-2"
