from __future__ import annotations

import importlib
import sqlite3
import sys
from pathlib import Path

from wizard.services.empire_extension_service import EmpireExtensionService


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


def test_merge_records_moves_links_and_removes_duplicate(tmp_path, monkeypatch):
    service = _seed_empire_root(tmp_path)
    extensions_root = str(Path(__file__).resolve().parents[2] / "extensions")
    if extensions_root not in sys.path:
        sys.path.insert(0, extensions_root)
    monkeypatch.setattr(service, "_import_module", lambda name: importlib.import_module(name))

    storage = importlib.import_module("empire.services.storage")
    storage.ensure_schema(service.db_path)
    with sqlite3.connect(str(service.db_path)) as conn:
        conn.execute(
            """
            INSERT INTO records (
                record_id, source, createdate, lastmodifieddate, email, firstname, lastname,
                phone, jobtitle, company, dedupe_key, raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "master-r1",
                "gmail",
                "2026-03-03T00:00:00Z",
                "2026-03-03T00:00:00Z",
                "person@example.com",
                "Person",
                "Example",
                "",
                "",
                "Empire",
                "person@example.com",
                '{"email":"person@example.com","firstname":"Person","lastname":"Example"}',
            ),
        )
        conn.execute(
            """
            INSERT INTO records (
                record_id, source, createdate, lastmodifieddate, email, firstname, lastname,
                phone, jobtitle, company, dedupe_key, raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "dup-r1",
                "hubspot",
                "2026-03-03T00:00:00Z",
                "2026-03-03T00:00:00Z",
                "person@example.com",
                "",
                "Example",
                "555-0100",
                "Lead",
                "Empire",
                "person@example.com",
                '{"phone":"555-0100","jobtitle":"Lead"}',
            ),
        )
        conn.execute(
            "INSERT INTO tasks (task_id, title, category, source, created_at, status, review_status, record_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("task-1", "Follow up", "crm", "gmail", "2026-03-03T00:00:00Z", "open", "ready", "dup-r1"),
        )
        conn.execute(
            "INSERT INTO events (event_id, record_id, event_type, occurred_at, subject, notes, metadata) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("event-1", "dup-r1", "gmail.fetch", "2026-03-03T00:00:00Z", "Fetched", "", "{}"),
        )

    candidates = service.find_record_merge_candidates("master-r1")
    assert candidates["summary"]["candidate_count"] == 1
    assert candidates["candidates"][0]["record_id"] == "dup-r1"

    result = service.merge_records(target_record_id="master-r1", source_record_id="dup-r1")
    assert result["status"] == "merged"

    with sqlite3.connect(str(service.db_path)) as conn:
        master = conn.execute(
            "SELECT phone, jobtitle FROM records WHERE record_id = ?",
            ("master-r1",),
        ).fetchone()
        duplicate = conn.execute(
            "SELECT record_id FROM records WHERE record_id = ?",
            ("dup-r1",),
        ).fetchone()
        task_owner = conn.execute(
            "SELECT record_id FROM tasks WHERE task_id = ?",
            ("task-1",),
        ).fetchone()
        event_owner = conn.execute(
            "SELECT record_id FROM events WHERE event_id = ?",
            ("event-1",),
        ).fetchone()
        merge_event = conn.execute(
            "SELECT event_type, notes FROM events WHERE event_type = 'record.merge' LIMIT 1"
        ).fetchone()

    assert master == ("555-0100", "Lead")
    assert duplicate is None
    assert task_owner[0] == "master-r1"
    assert event_owner[0] == "master-r1"
    assert merge_event == ("record.merge", "dup-r1")
