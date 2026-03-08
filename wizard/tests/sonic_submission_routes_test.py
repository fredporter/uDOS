from __future__ import annotations

import json

from fastapi import FastAPI
from fastapi.testclient import TestClient

import wizard.routes.sonic_plugin_routes as sonic_routes


class _API:
    def health(self):
        return {"status": "ok"}

    def get_schema(self):
        return {"type": "object"}

    def query_devices(self, _query):
        return []

    def get_device(self, _device_id):
        return None

    def get_stats(self):
        class _Stats:
            total_devices = 0
            by_vendor = {}
            by_reflash_potential = {}
            usb_boot_capable = 0
            uefi_native_capable = 0
            last_updated = None

        return _Stats()

    def list_flash_packs(self):
        return []

    def get_flash_pack(self, _pack_id):
        return None


class _Sync:
    def get_status(self):
        class _Status:
            last_sync = None
            db_path = "/tmp/sonic.db"
            db_exists = True
            record_count = 1
            schema_version = "1"
            needs_rebuild = False
            errors = []
            seed_db_path = "/tmp/seed.db"
            user_db_path = "/tmp/user.db"
            seed_record_count = 1
            user_record_count = 0
            current_machine_registered = False

        return _Status()

    def rebuild_database(self, force=False):
        return {"status": "ok", "force": force}

    def export_to_csv(self, output_path=None):
        return {"status": "ok", "output_path": str(output_path) if output_path else None}

    def bootstrap_current_machine(self, overwrite=True):
        return {"status": "ok", "device_id": "local-test", "overwrite": overwrite}


class _Schemas:
    class DeviceQuery:
        def __init__(self, **kwargs):
            self.kwargs = kwargs


def _seed_sonic_dataset(repo_root) -> None:
    datasets = repo_root.parent / "uDOS-sonic" / "datasets"
    datasets.mkdir(parents=True, exist_ok=True)
    (datasets / "sonic-devices.sql").write_text(
        (
            "DROP TABLE IF EXISTS devices;\n"
            "CREATE TABLE devices (\n"
            "  id TEXT PRIMARY KEY,\n"
            "  vendor TEXT NOT NULL,\n"
            "  model TEXT NOT NULL,\n"
            "  variant TEXT,\n"
            "  year INTEGER,\n"
            "  cpu TEXT,\n"
            "  gpu TEXT,\n"
            "  ram_gb INTEGER,\n"
            "  storage_gb INTEGER,\n"
            "  bios TEXT,\n"
            "  secure_boot TEXT,\n"
            "  tpm TEXT,\n"
            "  usb_boot TEXT,\n"
            "  uefi_native TEXT,\n"
            "  reflash_potential TEXT,\n"
            "  methods TEXT,\n"
            "  notes TEXT,\n"
            "  sources TEXT,\n"
            "  last_seen TEXT,\n"
            "  windows10_boot TEXT,\n"
            "  media_mode TEXT,\n"
            "  udos_launcher TEXT,\n"
            "  wizard_profile TEXT,\n"
            "  media_launcher TEXT,\n"
            "  settings_template_md TEXT,\n"
            "  installers_template_md TEXT,\n"
            "  containers_template_md TEXT,\n"
            "  drivers_template_md TEXT\n"
            ");\n"
        ),
        encoding="utf-8",
    )
    (datasets / "sonic-devices.schema.json").write_text(
        json.dumps({"type": "object", "properties": {"id": {"type": "string"}}}),
        encoding="utf-8",
    )


def test_sonic_submission_routes_queue_and_approve(tmp_path, monkeypatch):
    repo_root = tmp_path / "repo"
    _seed_sonic_dataset(repo_root)
    monkeypatch.setattr(
        sonic_routes,
        "load_sonic_plugin",
        lambda repo_root=None: {
            "api": type("X", (), {"get_sonic_service": lambda self: _API()})(),
            "sync": type("Y", (), {"get_sync_service": lambda self: _Sync()})(),
            "schemas": _Schemas,
        },
    )
    app = FastAPI()
    app.include_router(sonic_routes.create_sonic_plugin_routes(repo_root=repo_root))
    client = TestClient(app)

    created = client.post(
        "/api/sonic/submissions",
        json={
            "submitter": "tester",
            "device": {"id": "route-device", "vendor": "RouteVendor", "model": "RouteModel"},
        },
    )
    assert created.status_code == 200
    assert created.json()["submission"]["status"] == "pending"

    listed = client.get("/api/sonic/submissions")
    assert listed.status_code == 200
    assert listed.json()["count"] == 1
    assert listed.json()["runtime_contract"]["pending_count"] == 1

    approved = client.post(
        "/api/sonic/submissions/route-device/approve",
        json={"actor": "maintainer"},
    )
    assert approved.status_code == 200
    assert approved.json()["submission"]["approved_by"] == "maintainer"
    assert approved.json()["device"]["vendor"] == "RouteVendor"

    listed = client.get("/api/sonic/submissions", params={"status": "approved"})
    assert listed.status_code == 200
    assert listed.json()["count"] == 1


def test_sonic_submission_routes_reject_pending_record(tmp_path, monkeypatch):
    repo_root = tmp_path / "repo"
    _seed_sonic_dataset(repo_root)
    monkeypatch.setattr(
        sonic_routes,
        "load_sonic_plugin",
        lambda repo_root=None: {
            "api": type("X", (), {"get_sonic_service": lambda self: _API()})(),
            "sync": type("Y", (), {"get_sync_service": lambda self: _Sync()})(),
            "schemas": _Schemas,
        },
    )
    app = FastAPI()
    app.include_router(sonic_routes.create_sonic_plugin_routes(repo_root=repo_root))
    client = TestClient(app)

    client.post(
        "/api/sonic/submissions",
        json={"device": {"id": "reject-device", "vendor": "Vendor", "model": "Model"}},
    )
    rejected = client.post(
        "/api/sonic/submissions/reject-device/reject",
        json={"actor": "maintainer", "reason": "missing fields"},
    )

    assert rejected.status_code == 200
    assert rejected.json()["submission"]["reason"] == "missing fields"
    listed = client.get("/api/sonic/submissions", params={"status": "rejected"})
    assert listed.status_code == 200
    assert listed.json()["count"] == 1
