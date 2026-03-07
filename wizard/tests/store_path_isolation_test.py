from __future__ import annotations

from pathlib import Path

import wizard.services.store as store_module


def test_get_wizard_store_isolated_by_sqlite_path(tmp_path, monkeypatch):
    monkeypatch.setattr(store_module, "is_managed_mode", lambda: False)
    store_module._STORES.clear()

    first_path = tmp_path / "first.db"
    second_path = tmp_path / "second.db"

    first = store_module.get_wizard_store(Path(first_path))
    second = store_module.get_wizard_store(Path(second_path))

    assert first is not second

    first.update_scheduler_settings({"tick_seconds": 15})
    assert first.get_scheduler_settings()["tick_seconds"] == 15
    assert second.get_scheduler_settings()["tick_seconds"] == 60
