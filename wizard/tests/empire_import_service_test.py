from __future__ import annotations

import importlib
import sqlite3
import sys
from pathlib import Path

import pytest

from wizard.services.empire_extension_service import EmpireExtensionService
from wizard.services.empire_import_service import EmpireImportService
from wizard.services.empire_scope_service import EmpireScopeService


def _seed_empire_root(repo_root: Path) -> EmpireExtensionService:
    root = repo_root / "extensions" / "empire"
    (root / "services").mkdir(parents=True)
    (root / "api").mkdir(parents=True)
    (root / "src").mkdir(parents=True)
    (root / "data").mkdir(parents=True)
    (root / "config").mkdir(parents=True)
    (root / "templates" / "mappings").mkdir(parents=True)
    (root / "workflows").mkdir(parents=True)
    (root / "__init__.py").write_text("", encoding="utf-8")
    (root / "services" / "__init__.py").write_text("", encoding="utf-8")
    (root / "api" / "__init__.py").write_text("", encoding="utf-8")
    (root / "src" / "spine.py").write_text("def initialize(): return {}\n", encoding="utf-8")
    (root / "services" / "overview_service.py").write_text(
        "def load_overview(db_path, event_limit=6):\n"
        "    return {'counts': {'records': 1, 'sources': 1, 'events': 1}, 'events': []}\n",
        encoding="utf-8",
    )
    (root / "config" / "empire_secrets.json").write_text('{"empire_api_token":"token"}\n', encoding="utf-8")
    return EmpireExtensionService(repo_root=repo_root)


@pytest.mark.asyncio
async def test_empire_import_service_parses_eml_into_contacts_and_tasks(tmp_path, monkeypatch):
    workspace_root = tmp_path / "memory"
    inbox_root = workspace_root / "vault" / "@inbox"
    inbox_root.mkdir(parents=True)
    eml_path = inbox_root / "follow-up.eml"
    eml_path.write_text(
        "\n".join(
            [
                "From: Alice Example <alice@example.com>",
                "To: Bob Builder <bob@example.com>",
                "Cc: Carol Contact <carol@example.com>",
                "Date: Tue, 03 Mar 2026 09:30:00 +1000",
                "Subject: Follow up on binder launch",
                "Content-Type: text/plain; charset=utf-8",
                "",
                "Hi team,",
                "",
                "Please review the binder draft before tomorrow.",
                "Action: Call Alice about launch timing.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    service = _seed_empire_root(tmp_path)
    monkeypatch.setattr("wizard.services.empire_import_service.get_repo_root", lambda: tmp_path)
    monkeypatch.setattr("wizard.services.empire_import_service.get_memory_dir", lambda: workspace_root)
    monkeypatch.setattr("wizard.services.empire_import_service.get_vault_dir", lambda: workspace_root / "vault")
    monkeypatch.setattr("wizard.services.empire_import_service.get_empire_extension_service", lambda: service)
    monkeypatch.setattr(
        "wizard.services.empire_import_service.get_empire_scope_service",
        lambda: EmpireScopeService(repo_root=tmp_path),
    )
    extensions_root = str(Path(__file__).resolve().parents[2] / "extensions")
    if extensions_root not in sys.path:
        sys.path.insert(0, extensions_root)
    monkeypatch.setattr(service, "_import_module", lambda name: importlib.import_module(name))

    import_service = EmpireImportService(repo_root=tmp_path)
    result = await import_service.import_path(path="vault/@inbox/follow-up.eml")

    assert result["documents_created"] == 1
    assert result["records_imported"] == 3
    assert result["metadata"]["classification"]["classification"] == "email_message"
    assert result["metadata"]["derived_tasks"] == 2

    with sqlite3.connect(str(service.db_path)) as conn:
        contacts = conn.execute("SELECT email FROM records ORDER BY email").fetchall()
        tasks = conn.execute(
            "SELECT title, task_type, review_status FROM tasks ORDER BY created_at, title"
        ).fetchall()
        events = conn.execute(
            "SELECT event_type, subject FROM events ORDER BY occurred_at, event_type"
        ).fetchall()

    assert [row[0] for row in contacts] == [
        "alice@example.com",
        "bob@example.com",
        "carol@example.com",
    ]
    assert any(row[1] == "email_follow_up" for row in tasks)
    assert any("Call Alice" in row[0] for row in tasks)
    assert any(row[0] == "email.import" for row in events)


@pytest.mark.asyncio
async def test_empire_import_service_parses_ics_into_event_and_contacts(tmp_path, monkeypatch):
    workspace_root = tmp_path / "memory"
    inbox_root = workspace_root / "vault" / "@inbox"
    inbox_root.mkdir(parents=True)
    ics_path = inbox_root / "meeting.ics"
    ics_path.write_text(
        "\n".join(
            [
                "BEGIN:VCALENDAR",
                "VERSION:2.0",
                "BEGIN:VEVENT",
                "UID:event-1",
                "DTSTART:20260303T100000Z",
                "DTEND:20260303T103000Z",
                "SUMMARY:Binder Launch Review",
                "DESCRIPTION:Review binder launch tasks\\nAction: Send recap before tomorrow",
                "LOCATION:Studio One",
                "ORGANIZER;CN=Alice Example:mailto:alice@example.com",
                "ATTENDEE;CN=Bob Builder:mailto:bob@example.com",
                "END:VEVENT",
                "END:VCALENDAR",
            ]
        ),
        encoding="utf-8",
    )

    service = _seed_empire_root(tmp_path)
    monkeypatch.setattr("wizard.services.empire_import_service.get_repo_root", lambda: tmp_path)
    monkeypatch.setattr("wizard.services.empire_import_service.get_memory_dir", lambda: workspace_root)
    monkeypatch.setattr("wizard.services.empire_import_service.get_vault_dir", lambda: workspace_root / "vault")
    monkeypatch.setattr("wizard.services.empire_import_service.get_empire_extension_service", lambda: service)
    monkeypatch.setattr(
        "wizard.services.empire_import_service.get_empire_scope_service",
        lambda: EmpireScopeService(repo_root=tmp_path),
    )
    extensions_root = str(Path(__file__).resolve().parents[2] / "extensions")
    if extensions_root not in sys.path:
        sys.path.insert(0, extensions_root)
    monkeypatch.setattr(service, "_import_module", lambda name: importlib.import_module(name))

    import_service = EmpireImportService(repo_root=tmp_path)
    result = await import_service.import_path(path="vault/@inbox/meeting.ics")

    assert result["documents_created"] == 1
    assert result["records_imported"] == 2
    assert result["metadata"]["classification"]["classification"] == "calendar_event"
    assert result["metadata"]["calendar_events"] == 1
    assert result["metadata"]["derived_tasks"] == 1

    with sqlite3.connect(str(service.db_path)) as conn:
        contacts = conn.execute("SELECT email FROM records ORDER BY email").fetchall()
        tasks = conn.execute(
            "SELECT title, task_type, due_hint FROM tasks ORDER BY created_at, title"
        ).fetchall()
        events = conn.execute(
            "SELECT event_type, subject, notes FROM events ORDER BY occurred_at, event_type"
        ).fetchall()

    assert [row[0] for row in contacts] == ["alice@example.com", "bob@example.com"]
    assert any(row[1] == "calendar.follow_up" and row[2] == "tomorrow" for row in tasks)
    assert any(row[0] == "calendar.import" and "Binder Launch Review" in (row[1] or "") for row in events)
