from __future__ import annotations

import importlib
import sqlite3
import sys
from pathlib import Path

from wizard.services.empire_extension_service import EmpireExtensionService
from wizard.services.empire_scope_service import EmpireScopeService


def _seed_empire_root(repo_root: Path) -> EmpireExtensionService:
    root = repo_root / "extensions" / "empire"
    (root / "services").mkdir(parents=True)
    (root / "api").mkdir(parents=True)
    (root / "src").mkdir(parents=True)
    (root / "data").mkdir(parents=True)
    (root / "config").mkdir(parents=True)
    (root / "__init__.py").write_text("", encoding="utf-8")
    (root / "services" / "__init__.py").write_text("", encoding="utf-8")
    (root / "api" / "__init__.py").write_text("", encoding="utf-8")
    (root / "src" / "spine.py").write_text("def initialize(): return {}\n", encoding="utf-8")
    (root / "config" / "empire_secrets.json").write_text('{"empire_api_token":"token"}\n', encoding="utf-8")
    return EmpireExtensionService(repo_root=repo_root)


def test_promote_record_to_master_copies_binder_contact_and_logs_events(tmp_path, monkeypatch):
    service = _seed_empire_root(tmp_path)
    binders_root = tmp_path / "memory" / "vault" / "@binders" / "project-a"
    binders_root.mkdir(parents=True)
    scope_service = EmpireScopeService(repo_root=tmp_path)
    scope_service.vault_dir = tmp_path / "memory" / "vault"
    scope_service.binders_root = scope_service.vault_dir / "@binders"

    extensions_root = str(Path(__file__).resolve().parents[2] / "extensions")
    if extensions_root not in sys.path:
        sys.path.insert(0, extensions_root)
    monkeypatch.setattr(service, "_import_module", lambda name: importlib.import_module(name))
    binder_db_path = Path(scope_service.resolve(scope="binder", binder_id="project-a")["db_path"])
    monkeypatch.setattr(
        service,
        "_resolve_db_path",
        lambda scope="master", binder_id=None: service.db_path
        if scope == "master"
        else binder_db_path,
    )

    storage = importlib.import_module("empire.services.storage")
    storage.ensure_schema(service.db_path)
    storage.ensure_schema(binder_db_path)
    with sqlite3.connect(str(binder_db_path)) as conn:
        conn.execute(
            """
            INSERT INTO records (
                record_id, source, createdate, lastmodifieddate, email, firstname, lastname,
                phone, jobtitle, company, dedupe_key, raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "binder-r1",
                "calendar_import",
                "2026-03-03T00:00:00Z",
                "2026-03-03T00:00:00Z",
                "binder@example.com",
                "Binder",
                "User",
                "123",
                "Lead",
                "Empire Project",
                "binder@example.com",
                '{"email":"binder@example.com","name":"Binder User"}',
            ),
        )

    result = service.promote_record_to_master("binder-r1", binder_id="project-a")

    assert result["status"] == "promoted"
    assert result["binder_id"] == "project-a"
    assert result["target_record"]["email"] == "binder@example.com"

    with sqlite3.connect(str(service.db_path)) as conn:
        master_record = conn.execute(
            "SELECT email, firstname, lastname, company FROM records WHERE record_id = ?",
            (result["target_record_id"],),
        ).fetchone()
        master_event = conn.execute(
            "SELECT event_type FROM events WHERE record_id = ?",
            (result["target_record_id"],),
        ).fetchone()

    with sqlite3.connect(str(binder_db_path)) as conn:
        binder_event = conn.execute(
            "SELECT event_type FROM events WHERE record_id = ?",
            ("binder-r1",),
        ).fetchone()

    assert master_record == ("binder@example.com", "Binder", "User", "Empire Project")
    assert master_event[0] == "record.promoted_from_binder"
    assert binder_event[0] == "record.promote_to_master"
