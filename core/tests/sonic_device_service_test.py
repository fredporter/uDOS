from pathlib import Path
import sqlite3

from core.services.sonic_device_service import get_sonic_device_service


def _seed_sql(repo_root: Path) -> None:
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
            "  year INTEGER NOT NULL,\n"
            "  cpu TEXT,\n"
            "  gpu TEXT,\n"
            "  ram_gb INTEGER,\n"
            "  storage_gb INTEGER,\n"
            "  bios TEXT NOT NULL,\n"
            "  secure_boot TEXT NOT NULL,\n"
            "  tpm TEXT NOT NULL,\n"
            "  usb_boot TEXT NOT NULL,\n"
            "  uefi_native TEXT NOT NULL,\n"
            "  reflash_potential TEXT NOT NULL,\n"
            "  methods TEXT NOT NULL,\n"
            "  notes TEXT,\n"
            "  sources TEXT,\n"
            "  last_seen TEXT NOT NULL,\n"
            "  windows10_boot TEXT NOT NULL,\n"
            "  media_mode TEXT NOT NULL,\n"
            "  udos_launcher TEXT NOT NULL,\n"
            "  wizard_profile TEXT,\n"
            "  media_launcher TEXT,\n"
            "  settings_template_md TEXT,\n"
            "  installers_template_md TEXT,\n"
            "  containers_template_md TEXT,\n"
            "  drivers_template_md TEXT\n"
            ");\n"
            "INSERT INTO devices (\n"
            "  id, vendor, model, variant, year, cpu, gpu, ram_gb, storage_gb,\n"
            "  bios, secure_boot, tpm, usb_boot, uefi_native, reflash_potential,\n"
            "  methods, notes, sources, last_seen, windows10_boot, media_mode, udos_launcher,\n"
            "  settings_template_md, installers_template_md, containers_template_md, drivers_template_md\n"
            ") VALUES (\n"
            "  'seed-device', 'SeedVendor', 'SeedModel', 'Mk1', 2025, 'cpu', 'gpu', 8, 64,\n"
            "  'uefi', 'unknown', 'unknown', 'native', 'works', 'medium',\n"
            "  '[\"seed\"]', 'seed record', '[\"seed\"]', '2026-03-03', 'install', 'htpc', 'basic',\n"
            "  'core/framework/seed/bank/templates/submissions/SONIC-DEVICE-SETTINGS-template.md',\n"
            "  'core/framework/seed/bank/templates/submissions/SONIC-DEVICE-INSTALLERS-template.md',\n"
            "  'core/framework/seed/bank/templates/submissions/SONIC-DEVICE-CONTAINERS-template.md',\n"
            "  'core/framework/seed/bank/templates/submissions/SONIC-DEVICE-DRIVERS-template.md'\n"
            ");\n"
        ),
        encoding="utf-8",
    )


def test_sonic_device_service_splits_seed_and_user_runtime(tmp_path):
    repo_root = tmp_path / "repo"
    _seed_sql(repo_root)
    service = get_sonic_device_service(repo_root)

    rebuild = service.ensure_seed_runtime(force=True)
    assert rebuild["status"] == "ok"

    runtime = service.runtime_contract()
    assert runtime["seed_catalog"]["record_count"] == 1
    assert runtime["user_catalog"]["record_count"] == 0

    bootstrap = service.register_current_machine()
    assert bootstrap["status"] == "ok"

    runtime = service.runtime_contract()
    assert runtime["user_catalog"]["record_count"] == 1
    assert runtime["user_catalog"]["current_machine_registered"] is True

    devices = service.list_devices(limit=20)
    assert len(devices) == 2
    local = next(item for item in devices if item["catalog_source"] == "user")
    assert local["settings_template_md"].endswith("SONIC-DEVICE-SETTINGS-template.md")
    assert local["installers_template_md"].endswith("SONIC-DEVICE-INSTALLERS-template.md")
    with sqlite3.connect(runtime["paths"]["legacy_db_path"]) as conn:
        legacy_count = conn.execute("SELECT COUNT(*) FROM devices").fetchone()[0]
    assert legacy_count == 2


def test_sonic_device_service_user_overlay_overrides_seed(tmp_path):
    repo_root = tmp_path / "repo"
    _seed_sql(repo_root)
    service = get_sonic_device_service(repo_root)
    service.ensure_seed_runtime(force=True)
    service.ensure_user_runtime()

    user_csv = repo_root / "overlay.csv"
    user_csv.write_text(
        (
            "id,vendor,model,year,bios,secure_boot,tpm,usb_boot,uefi_native,reflash_potential,methods,last_seen,windows10_boot,media_mode,udos_launcher,settings_template_md,installers_template_md,containers_template_md,drivers_template_md\n"
            "seed-device,LocalVendor,LocalModel,2026,uefi,unknown,unknown,native,works,high,\"[\\\"local\\\"]\",2026-03-03,install,htpc,advanced,settings.md,installers.md,containers.md,drivers.md\n"
        ),
        encoding="utf-8",
    )

    result = service.import_user_csv(user_csv)
    assert result["status"] == "ok"

    device = service.get_device("seed-device")
    assert device is not None
    assert device["vendor"] == "LocalVendor"
    assert device["catalog_source"] == "user"
    assert device["drivers_template_md"] == "drivers.md"


def test_sonic_device_service_submission_approval_merges_into_user_catalog(tmp_path):
    repo_root = tmp_path / "repo"
    _seed_sql(repo_root)
    service = get_sonic_device_service(repo_root)
    service.ensure_seed_runtime(force=True)

    queued = service.submit_device_submission(
        {
            "id": "submitted-device",
            "vendor": "SubmitVendor",
            "model": "SubmitModel",
            "methods": ["usb"],
            "sources": ["local-note"],
            "year": 2026,
        },
        submitter="tester",
    )
    assert queued["status"] == "ok"
    assert service.submission_runtime_contract()["pending_count"] == 1

    approved = service.approve_submission("submitted-device", approved_by="maintainer")
    assert approved["status"] == "ok"
    assert approved["submission"]["approved_by"] == "maintainer"
    assert service.submission_runtime_contract()["pending_count"] == 0
    assert service.submission_runtime_contract()["approved_count"] == 1

    device = service.get_device("submitted-device")
    assert device is not None
    assert device["catalog_source"] == "user"
    assert device["vendor"] == "SubmitVendor"
    assert device["methods"] == ["usb"]


def test_sonic_device_service_submission_rejects_pending_record(tmp_path):
    repo_root = tmp_path / "repo"
    _seed_sql(repo_root)
    service = get_sonic_device_service(repo_root)
    service.ensure_seed_runtime(force=True)

    service.submit_device_submission(
        {"id": "reject-me", "vendor": "RejectVendor", "model": "RejectModel"},
        submitter="tester",
    )
    rejected = service.reject_submission(
        "reject-me", rejected_by="maintainer", reason="missing verification"
    )

    assert rejected["status"] == "ok"
    assert rejected["submission"]["reason"] == "missing verification"
    assert service.submission_runtime_contract()["pending_count"] == 0
    assert service.submission_runtime_contract()["rejected_count"] == 1
