from __future__ import annotations

import wizard.services.provider_health_service as provider_health_module
from wizard.services.provider_health_service import ProviderHealthService
from wizard.services.store.sqlite_store import SQLiteWizardStore


def test_managed_provider_health_state_persists_in_store(tmp_path, monkeypatch):
    store = SQLiteWizardStore(tmp_path / "ops.db")
    monkeypatch.setattr(provider_health_module, "is_managed_mode", lambda: True)
    monkeypatch.setattr(
        provider_health_module,
        "get_provider_definitions",
        lambda: {
            "local": {
                "name": "Local",
            }
        },
    )

    first = ProviderHealthService(repo_root=tmp_path, store=store)
    snapshot = first.run_checks()
    assert snapshot["healthy"] == 1

    second = ProviderHealthService(repo_root=tmp_path, store=store)
    summary = second.get_summary(auto_check_if_stale=False)
    assert summary["checked_at"] == snapshot["checked_at"]
    assert summary["checks"][0]["provider_id"] == "local"
