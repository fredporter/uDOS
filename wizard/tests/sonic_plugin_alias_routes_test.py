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
        self.bootstrap_calls = 0

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
        self.last_force = force
        return {"status": "ok", "force": force}

    def export_to_csv(self, output_path=None):
        return {"status": "ok", "output_path": str(output_path) if output_path else None}

    def bootstrap_current_machine(self, overwrite=True):
        self.bootstrap_calls += 1
        return {"status": "ok", "device_id": "local-test", "overwrite": overwrite}


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


def test_sonic_plugin_alias_routes_are_retired_by_default(monkeypatch):
    monkeypatch.delenv("UDOS_SONIC_ENABLE_LEGACY_ALIASES", raising=False)
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
    contract_res = client.get("/api/sonic/schema/contract")
    assert contract_res.status_code == 200
    assert "ok" in contract_res.json()
    assert client.get("/api/sonic/devices", params={"uefi_native": "works", "windows10_boot": "wtg", "media_mode": "htpc"}).status_code == 200
    canonical_status = client.get("/api/sonic/sync/status")
    assert canonical_status.status_code == 200
    assert canonical_status.json()["db_exists"] is True

    canonical_rebuild = client.post("/api/sonic/sync/rebuild")
    assert canonical_rebuild.status_code == 200
    assert canonical_rebuild.json()["status"] == "ok"

    alias = client.post("/api/sonic/rescan")
    assert alias.status_code == 410
    detail = alias.json()["detail"]
    assert detail["alias"] == "/api/sonic/rescan"
    assert detail["canonical"] == "/api/sonic/sync/rebuild?force=false"

    bootstrap = client.post("/api/sonic/bootstrap/current")
    assert bootstrap.status_code == 200
    assert bootstrap.json()["device_id"] == "local-test"
    assert sync.bootstrap_calls == 1

    alias_status = client.get("/api/sonic/aliases/status")
    assert alias_status.status_code == 200
    assert alias_status.json()["legacy_aliases_enabled"] is False
    assert alias_status.json()["status"] == "retired"


def test_sonic_plugin_alias_routes_can_be_reenabled(monkeypatch):
    monkeypatch.setenv("UDOS_SONIC_ENABLE_LEGACY_ALIASES", "1")
    sync = _Sync()

    monkeypatch.setattr(
        sonic_routes,
        "load_sonic_plugin",
        lambda repo_root=None: {"api": type("X", (), {"get_sonic_service": lambda self: _API()})(), "sync": type("Y", (), {"get_sync_service": lambda self: sync})(), "schemas": _Schemas},
    )
    monkeypatch.setitem(__import__("sys").modules, "library.sonic.schemas", _Enums)

    app = FastAPI()
    app.include_router(sonic_routes.create_sonic_plugin_routes(auth_guard=None))
    client = TestClient(app)

    alias = client.post("/api/sonic/rescan")
    assert alias.status_code == 200
    assert alias.json()["deprecated_alias"]["canonical"] == "/api/sonic/sync/rebuild?force=false"

    alias_status = client.get("/api/sonic/aliases/status")
    assert alias_status.status_code == 200
    assert alias_status.json()["legacy_aliases_enabled"] is True
    assert alias_status.json()["status"] == "compatibility_override"
