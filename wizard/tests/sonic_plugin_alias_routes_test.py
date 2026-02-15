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
    def __init__(self):
        self.last_force = None

    def get_status(self):
        class _Status:
            last_sync = None
            db_path = "/tmp/sonic.db"
            db_exists = True
            record_count = 1
            schema_version = "1"
            needs_rebuild = False
            errors = []

        return _Status()

    def rebuild_database(self, force=False):
        self.last_force = force
        return {"status": "ok", "force": force}

    def export_to_csv(self, output_path=None):
        return {"status": "ok", "output_path": str(output_path) if output_path else None}


class _Schemas:
    class DeviceQuery:
        def __init__(self, **kwargs):
            self.kwargs = kwargs


class _Enums:
    class ReflashPotential:
        def __new__(cls, value):
            return value

    class USBBootSupport:
        def __new__(cls, value):
            return value


def test_sonic_plugin_alias_routes(monkeypatch):
    sync = _Sync()

    monkeypatch.setattr(
        sonic_routes,
        "load_sonic_plugin",
        lambda repo_root=None: {"api": type("X", (), {"get_sonic_service": lambda self: _API()})(), "sync": type("Y", (), {"get_sync_service": lambda self: sync})(), "schemas": _Schemas},
    )

    # Route module imports enums from library.sonic.schemas in /devices handler.
    monkeypatch.setitem(__import__("sys").modules, "library.sonic.schemas", _Enums)

    app = FastAPI()
    app.include_router(sonic_routes.create_sonic_plugin_routes(auth_guard=None))
    client = TestClient(app)

    assert client.get("/api/sonic/health").status_code == 200
    assert client.get("/api/sonic/devices", params={"uefi_native": "works", "windows10_boot": "wtg", "media_mode": "htpc"}).status_code == 200
    assert client.post("/api/sonic/rescan").status_code == 200
    assert sync.last_force is False

    assert client.post("/api/sonic/rebuild").status_code == 200
    assert sync.last_force is True

    assert client.post("/api/sonic/sync").status_code == 200
    assert sync.last_force is False

    export_res = client.get("/api/sonic/export")
    assert export_res.status_code == 200
    assert export_res.json()["status"] == "ok"

    db_status = client.get("/api/sonic/db/status")
    assert db_status.status_code == 200
    assert db_status.json()["db_exists"] is True

    db_rebuild = client.post("/api/sonic/db/rebuild")
    assert db_rebuild.status_code == 200

    db_export = client.get("/api/sonic/db/export")
    assert db_export.status_code == 200
