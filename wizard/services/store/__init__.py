from __future__ import annotations

from pathlib import Path

from wizard.services.deploy_mode import is_managed_mode
from wizard.services.path_utils import get_repo_root
from wizard.services.store.base import WizardStore
from wizard.services.store.postgres_store import PostgresWizardStore
from wizard.services.store.sqlite_store import SQLiteWizardStore

_STORES: dict[str, WizardStore] = {}


def get_wizard_store(db_path: Path | None = None) -> WizardStore:
    if is_managed_mode():
        key = "managed"
        if key not in _STORES:
            _STORES[key] = PostgresWizardStore()
        return _STORES[key]

    resolved_path = Path(db_path or (get_repo_root() / "memory" / "wizard" / "ops.db")).resolve()
    key = f"sqlite:{resolved_path}"
    if key not in _STORES:
        _STORES[key] = SQLiteWizardStore(resolved_path)
    return _STORES[key]
