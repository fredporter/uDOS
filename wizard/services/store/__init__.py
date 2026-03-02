from __future__ import annotations

from pathlib import Path

from wizard.services.deploy_mode import is_managed_mode
from wizard.services.path_utils import get_repo_root
from wizard.services.store.base import WizardStore
from wizard.services.store.postgres_store import PostgresWizardStore
from wizard.services.store.sqlite_store import SQLiteWizardStore

_STORE: WizardStore | None = None


def get_wizard_store() -> WizardStore:
    global _STORE
    if _STORE is None:
        if is_managed_mode():
            _STORE = PostgresWizardStore()
        else:
            db_path = get_repo_root() / "memory" / "wizard" / "ops.db"
            _STORE = SQLiteWizardStore(Path(db_path))
    return _STORE
