from __future__ import annotations

import sqlite3
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

import wizard.routes.empire_routes as empire_routes
import wizard.routes.extension_routes as extension_routes
from wizard.services.empire_extension_service import EmpireExtensionService
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
    (root / "templates" / "mappings" / "default.md").write_text("# Template\n", encoding="utf-8")
    (root / "workflows" / "intake-review.md").write_text("# WORKFLOW: Intake Review\n", encoding="utf-8")
    secrets = root / "config" / "empire_secrets.json"
    secrets.write_text('{"empire_api_token":"token"}\n', encoding="utf-8")

    db_path = root / "data" / "empire.db"
    with sqlite3.connect(str(db_path)) as conn:
        conn.executescript(
            """
            CREATE TABLE records (
              record_id TEXT,
              email TEXT,
              firstname TEXT,
              lastname TEXT,
              company TEXT,
              jobtitle TEXT,
              phone TEXT,
              city TEXT,
              state TEXT,
              country TEXT,
              lastmodifieddate TEXT
            );
            CREATE TABLE companies (
              company_id TEXT,
              name TEXT,
              domain TEXT,
              phone TEXT,
              city TEXT,
              state TEXT,
              country TEXT,
              source TEXT
            );
            CREATE TABLE tasks (
              task_id TEXT,
              title TEXT,
              category TEXT,
              source TEXT,
              source_ref TEXT,
              created_at TEXT,
              status TEXT,
              notes TEXT,
              record_id TEXT
            );
            CREATE TABLE events (
              event_id TEXT,
              record_id TEXT,
              event_type TEXT,
              occurred_at TEXT,
              subject TEXT,
              notes TEXT
            );
            CREATE TABLE sources (
              source_id TEXT,
              source_key TEXT,
              label TEXT,
              created_at TEXT
            );
            INSERT INTO records VALUES ('r1', 'user@example.com', 'User', 'One', 'Empire', 'Lead', '123', 'Brisbane', 'QLD', 'AU', '2026-03-03T00:00:00Z');
            INSERT INTO companies VALUES ('c1', 'Empire', 'empire.test', '123', 'Brisbane', 'QLD', 'AU', 'hubspot');
            INSERT INTO tasks VALUES ('t1', 'Follow up', 'crm', 'gmail', 'msg-1', '2026-03-03T00:00:00Z', 'open', 'Call tomorrow', 'r1');
            INSERT INTO events VALUES ('e1', 'r1', 'gmail.fetch', '2026-03-03T00:00:00Z', 'Fetched 1 record', 'gmail');
            INSERT INTO sources VALUES ('s1', 'gmail', 'Gmail', '2026-03-03T00:00:00Z');
            """
        )
    return EmpireExtensionService(repo_root=repo_root)


def test_empire_routes_expose_status_and_templates(tmp_path, monkeypatch):
    service = _seed_empire_root(tmp_path)
    monkeypatch.setattr(empire_routes, "get_empire_extension_service", lambda: service)

    app = FastAPI()
    app.include_router(empire_routes.create_empire_routes())
    client = TestClient(app)

    status = client.get("/api/empire/status")
    assert status.status_code == 200
    assert status.json()["installed"] is True
    assert status.json()["configured"] is True

    templates = client.get("/api/empire/templates")
    assert templates.status_code == 200
    names = {entry["name"] for entry in templates.json()["templates"]}
    kinds = {entry["kind"] for entry in templates.json()["templates"]}
    assert "default.md" in names
    assert "intake-review.md" in names
    assert "mapping" in kinds
    assert "workflow" in kinds

    read_res = client.get("/api/empire/templates/read", params={"path": "templates/mappings/default.md"})
    assert read_res.status_code == 200
    assert "# Template" in read_res.json()["content"]


def test_empire_document_detail_route_reads_document(tmp_path, monkeypatch):
    _seed_empire_root(tmp_path)

    class _ServiceWithDocument:
        def get_document(self, document_id: str):
            return {
                "document_id": document_id,
                "title": "Inbox Intake",
                "source_path": "@inbox/intake.pdf",
                "scope": "master",
                "binder_id": None,
                "media_type": "application/pdf",
                "metadata": {"pages": 2},
                "extracted_text": "First page summary",
            }

    monkeypatch.setattr(empire_routes, "get_empire_extension_service", lambda: _ServiceWithDocument())

    app = FastAPI()
    app.include_router(empire_routes.create_empire_routes())
    client = TestClient(app)

    response = client.get("/api/empire/documents/doc-42")
    assert response.status_code == 200
    payload = response.json()
    assert payload["document_id"] == "doc-42"
    assert payload["title"] == "Inbox Intake"
    assert payload["metadata"]["pages"] == 2


def test_extension_routes_keep_empire_visible_as_official_extension(tmp_path, monkeypatch):
    service = _seed_empire_root(tmp_path)
    monkeypatch.setattr(extension_routes, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(extension_routes, "get_empire_extension_service", lambda: service)
    monkeypatch.setattr(
        extension_routes,
        "_official_extensions",
        lambda: [
            {
                "id": "empire",
                "name": "Empire",
                "description": "empire",
                "icon": "e",
                "path": "extensions/empire",
                "main_file": "__init__.py",
                "api_prefix": "/api/empire",
                "web_port": None,
                "category": "business",
                "visibility": "official",
                "runtime_owner": "wizard",
                "callable_from": ["core", "wizard", "uhome"],
                "library_refs": ["empire"],
                "standalone_capable": True,
                "lens_vars": {"lens": "repo-library:empire"},
                "version": "1.0.0",
                "present": True,
            }
        ],
    )

    app = FastAPI()
    app.include_router(extension_routes.router)
    client = TestClient(app)

    response = client.get("/api/extensions/list")
    assert response.status_code == 200
    payload = response.json()
    empire = next(item for item in payload["extensions"] if item["id"] == "empire")
    assert empire["visibility"] == "official"
    assert empire["enabled"] is True
    assert empire["wizard_route"] == "#empire"


def test_empire_scope_routes_resolve_master_and_binder(tmp_path, monkeypatch):
    service = _seed_empire_root(tmp_path)
    binders_root = tmp_path / "memory" / "vault" / "@binders" / "project-a"
    binders_root.mkdir(parents=True)
    monkeypatch.setattr(empire_routes, "get_empire_extension_service", lambda: service)
    scope_service = EmpireScopeService(repo_root=tmp_path)
    scope_service.vault_dir = tmp_path / "memory" / "vault"
    scope_service.binders_root = scope_service.vault_dir / "@binders"
    monkeypatch.setattr(empire_routes, "get_empire_scope_service", lambda: scope_service)

    app = FastAPI()
    app.include_router(empire_routes.create_empire_routes())
    client = TestClient(app)

    master = client.get("/api/empire/scope")
    assert master.status_code == 200
    assert master.json()["scope"] == "master"

    binders = client.get("/api/empire/scope/binders")
    assert binders.status_code == 200
    assert binders.json()["binders"][0]["binder_id"] == "project-a"

    binder = client.get("/api/empire/scope", params={"scope": "binder", "binder_id": "project-a"})
    assert binder.status_code == 200
    assert binder.json()["scope"] == "binder"
    assert binder.json()["binder_id"] == "project-a"


def test_empire_import_route_delegates_to_rebuild_service(tmp_path, monkeypatch):
    service = _seed_empire_root(tmp_path)
    monkeypatch.setattr(empire_routes, "get_empire_extension_service", lambda: service)

    class _FakeImportService:
        async def import_path(self, *, path: str, scope: str = "master", binder_id: str | None = None):
            return {
                "job_id": "job-1",
                "status": "completed",
                "records_imported": 3,
                "documents_created": 0,
                "scope": {"scope": scope, "binder_id": binder_id},
                "path": path,
            }

    monkeypatch.setattr(empire_routes, "get_empire_import_service", lambda: _FakeImportService())

    app = FastAPI()
    app.include_router(empire_routes.create_empire_routes())
    client = TestClient(app)

    response = client.post(
        "/api/empire/import/path",
        json={"path": "@inbox/contacts.csv", "scope": "master", "binder_id": None},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["job_id"] == "job-1"
    assert payload["records_imported"] == 3
    assert payload["path"] == "@inbox/contacts.csv"


def test_empire_collate_route_delegates_to_collation_service(tmp_path, monkeypatch):
    service = _seed_empire_root(tmp_path)
    monkeypatch.setattr(empire_routes, "get_empire_extension_service", lambda: service)

    class _FakeCollationService:
        def collate_document(self, document_id: str, emit_mode: str = "task_note"):
            return {
                "document_id": document_id,
                "task_count": 2,
                "artifact_path": "/tmp/task-note.md",
                "emit_mode": emit_mode,
            }

    monkeypatch.setattr(empire_routes, "get_empire_collation_service", lambda: _FakeCollationService())

    app = FastAPI()
    app.include_router(empire_routes.create_empire_routes())
    client = TestClient(app)

    response = client.post("/api/empire/process/collate", json={"document_id": "doc-1", "emit_mode": "workflow_stub"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["document_id"] == "doc-1"
    assert payload["task_count"] == 2
    assert payload["emit_mode"] == "workflow_stub"


def test_empire_connector_run_route_delegates_to_sync_service(tmp_path, monkeypatch):
    service = _seed_empire_root(tmp_path)
    monkeypatch.setattr(empire_routes, "get_empire_extension_service", lambda: service)

    class _FakeSyncService:
        async def run_connector(self, *, connector: str, action: str, scope: str = "master", binder_id: str | None = None, params=None):
            return {
                "sync_job_id": "job-sync-1",
                "status": "completed",
                "connector": connector,
                "action": action,
                "scope": {"scope": scope, "binder_id": binder_id},
                "records_imported": 7,
            }

    monkeypatch.setattr(empire_routes, "get_empire_sync_service", lambda: _FakeSyncService())

    app = FastAPI()
    app.include_router(empire_routes.create_empire_routes())
    client = TestClient(app)

    response = client.post(
        "/api/empire/connectors/run",
        json={"connector": "hubspot", "action": "sync", "scope": "master", "binder_id": None, "params": {"limit": 10}},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["sync_job_id"] == "job-sync-1"
    assert payload["connector"] == "hubspot"
    assert payload["records_imported"] == 7


def test_empire_connectors_route_exposes_catalog_and_recent_jobs(tmp_path, monkeypatch):
    service = _seed_empire_root(tmp_path)

    class _ServiceWithConnectors:
        def connector_catalog(self):
            return {
                "connectors": {
                    "google": {
                        "state": "live",
                        "actions": [{"id": "gmail_fetch", "label": "Fetch Gmail"}],
                        "recent_jobs": [
                            {
                                "sync_job_id": "job-google-1",
                                "connector": "google",
                                "action": "gmail_fetch",
                                "status": "completed",
                                "metadata": {"records_imported": 3},
                            }
                        ],
                    }
                }
            }

    monkeypatch.setattr(empire_routes, "get_empire_extension_service", lambda: _ServiceWithConnectors())

    app = FastAPI()
    app.include_router(empire_routes.create_empire_routes())
    client = TestClient(app)

    response = client.get("/api/empire/connectors")
    assert response.status_code == 200
    payload = response.json()
    assert payload["connectors"]["google"]["state"] == "live"
    assert payload["connectors"]["google"]["actions"][0]["id"] == "gmail_fetch"
    assert payload["connectors"]["google"]["recent_jobs"][0]["sync_job_id"] == "job-google-1"


def test_empire_sync_job_detail_route_reads_job(tmp_path, monkeypatch):
    service = _seed_empire_root(tmp_path)

    class _ServiceWithSyncJob:
        def get_sync_job(self, sync_job_id: str):
            return {"sync_job_id": sync_job_id, "status": "completed", "metadata": {"records_imported": 2}}

    monkeypatch.setattr(empire_routes, "get_empire_extension_service", lambda: _ServiceWithSyncJob())

    app = FastAPI()
    app.include_router(empire_routes.create_empire_routes())
    client = TestClient(app)

    response = client.get("/api/empire/sync/jobs/sync-42")
    assert response.status_code == 200
    assert response.json()["sync_job_id"] == "sync-42"


def test_empire_webhook_routes_delegate_to_webhook_service(tmp_path, monkeypatch):
    service = _seed_empire_root(tmp_path)
    monkeypatch.setattr(empire_routes, "get_empire_extension_service", lambda: service)

    class _FakeWebhookService:
        def save_mapping(self, **kwargs):
            return {**kwargs, "mapping_id": "map-1"}

        def test_mapping(self, mapping_id, payload):
            return {"mapping_id": mapping_id, "result": {"record_id": "r1"}, "payload": payload}

        def receive_inbound(self, *, mapping_id, payload, signature):
            return {"mapping_id": mapping_id, "result": {"record_id": "r2"}, "signature": signature}

    class _ServiceWithWebhooks:
        def list_webhook_mappings(self, limit=100):
            return [{"mapping_id": "map-1", "name": "HubSpot Contact"}]

        def list_webhook_deliveries(self, *, limit=100, mapping_id=None):
            return [{"delivery_id": "del-1", "mapping_id": mapping_id or "map-1", "status": "completed"}]

    monkeypatch.setattr(empire_routes, "get_empire_webhook_service", lambda: _FakeWebhookService())
    monkeypatch.setattr(empire_routes, "get_empire_extension_service", lambda: _ServiceWithWebhooks())

    app = FastAPI()
    app.include_router(empire_routes.create_empire_routes())
    client = TestClient(app)

    mappings = client.get("/api/empire/webhooks/mappings")
    assert mappings.status_code == 200
    assert mappings.json()["mappings"][0]["mapping_id"] == "map-1"

    save = client.post(
        "/api/empire/webhooks/mappings",
        json={
            "name": "HubSpot Contact",
            "source_system": "hubspot",
            "event_type": "contact.updated",
            "target_scope": "master",
            "target_entity": "contact",
            "status": "active",
            "config": {},
        },
    )
    assert save.status_code == 200
    assert save.json()["mapping_id"] == "map-1"

    deliveries = client.get("/api/empire/webhooks/deliveries")
    assert deliveries.status_code == 200
    assert deliveries.json()["deliveries"][0]["delivery_id"] == "del-1"

    test_run = client.post("/api/empire/webhooks/test/map-1", json={"email": "a@example.com"})
    assert test_run.status_code == 200
    assert test_run.json()["result"]["record_id"] == "r1"

    inbound = client.post("/api/empire/webhooks/inbound/map-1?signature=secret", json={"email": "b@example.com"})
    assert inbound.status_code == 200
    assert inbound.json()["signature"] == "secret"


def test_empire_import_job_detail_route_reads_job(tmp_path, monkeypatch):
    service = _seed_empire_root(tmp_path)
    monkeypatch.setattr(empire_routes, "get_empire_extension_service", lambda: service)

    class _ServiceWithJob:
        def status_payload(self):
            return service.status_payload()

        def get_import_job(self, job_id: str):
            return {"job_id": job_id, "status": "completed", "metadata": "{}"}

    monkeypatch.setattr(empire_routes, "get_empire_extension_service", lambda: _ServiceWithJob())

    app = FastAPI()
    app.include_router(empire_routes.create_empire_routes())
    client = TestClient(app)

    response = client.get("/api/empire/import/jobs/job-42")
    assert response.status_code == 200
    assert response.json()["job_id"] == "job-42"


def test_empire_accounts_route_exposes_wizard_managed_actions(tmp_path, monkeypatch):
    service = _seed_empire_root(tmp_path)

    monkeypatch.setattr(
        EmpireExtensionService,
        "_oauth_connection_status",
        lambda self: {
            "available": True,
            "status": "connected",
            "user": "operator@example.com",
            "provider_name": "Google",
            "scopes": ["gmail.readonly", "calendar.readonly"],
            "expires_at": 12345,
            "user_info": {"email": "operator@example.com"},
        },
    )
    monkeypatch.setattr(empire_routes, "get_empire_extension_service", lambda: service)

    app = FastAPI()
    app.include_router(empire_routes.create_empire_routes())
    client = TestClient(app)

    response = client.get("/api/empire/accounts")
    assert response.status_code == 200
    payload = response.json()
    assert payload["google"]["connected"] is True
    assert payload["google"]["actions"]["connect_url"] == "/api/oauth/connect/google"
    assert payload["google"]["user"] == "operator@example.com"


def test_empire_import_jobs_parse_metadata(tmp_path):
    service = _seed_empire_root(tmp_path)

    class _FakeStorage:
        @staticmethod
        def list_import_jobs(db_path, limit=100):
            return [
                {
                    "job_id": "job-1",
                    "status": "completed",
                    "metadata": '{"records_imported": 5, "labels": ["gmail"]}',
                }
            ]

        @staticmethod
        def get_import_job(job_id, db_path):
            return {
                "job_id": job_id,
                "status": "completed",
                "metadata": '{"records_imported": 5, "labels": ["gmail"]}',
            }

    original_import_module = service._import_module
    service._import_module = lambda name: _FakeStorage if name == "empire.services.storage" else original_import_module(name)

    jobs = service.list_import_jobs(limit=5)
    detail = service.get_import_job("job-1")

    assert isinstance(jobs[0]["metadata"], dict)
    assert jobs[0]["metadata"]["records_imported"] == 5
    assert isinstance(detail["metadata"], dict)
    assert detail["metadata"]["labels"] == ["gmail"]
