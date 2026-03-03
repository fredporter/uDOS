import hashlib
from pathlib import Path
import json

from core.commands.sonic_handler import SonicHandler
from core.services.mode_policy import RuntimeMode


class _FakeSonicHandler(SonicHandler):
    def __init__(self, repo_root: Path, sonic_root: Path):
        super().__init__()
        self._repo = repo_root
        self._sonic = sonic_root

    def _repo_root(self) -> Path:  # type: ignore[override]
        return self._repo

    def _sonic_root(self) -> Path:  # type: ignore[override]
        return self._sonic


def _seed_sonic_dataset(sonic_root: Path) -> None:
    datasets = sonic_root / "datasets"
    datasets.mkdir(parents=True, exist_ok=True)
    (datasets / "sonic-devices.sql").write_text("CREATE TABLE devices(id TEXT PRIMARY KEY);\n", encoding="utf-8")
    (datasets / "sonic-devices.schema.json").write_text(
        json.dumps({"type": "object", "properties": {"id": {"type": "string"}}, "required": ["id"]}),
        encoding="utf-8",
    )
    (datasets / "version.json").write_text(
        json.dumps({"component": "udos-sonic-datasets", "version": "v1.0.0", "schema_version": "1.1"}),
        encoding="utf-8",
    )


def _seed_full_sonic_dataset(sonic_root: Path) -> None:
    datasets = sonic_root / "datasets"
    datasets.mkdir(parents=True, exist_ok=True)
    (datasets / "sonic-devices.sql").write_text(
        (
            "CREATE TABLE devices(\n"
            "  id TEXT PRIMARY KEY,\n"
            "  vendor TEXT NOT NULL,\n"
            "  model TEXT NOT NULL,\n"
            "  year INTEGER NOT NULL,\n"
            "  bios TEXT NOT NULL,\n"
            "  secure_boot TEXT NOT NULL,\n"
            "  tpm TEXT NOT NULL,\n"
            "  usb_boot TEXT NOT NULL,\n"
            "  uefi_native TEXT NOT NULL,\n"
            "  reflash_potential TEXT NOT NULL,\n"
            "  methods TEXT NOT NULL,\n"
            "  last_seen TEXT NOT NULL,\n"
            "  windows10_boot TEXT NOT NULL,\n"
            "  media_mode TEXT NOT NULL,\n"
            "  udos_launcher TEXT NOT NULL,\n"
            "  variant TEXT,\n"
            "  cpu TEXT,\n"
            "  gpu TEXT,\n"
            "  ram_gb INTEGER,\n"
            "  storage_gb INTEGER,\n"
            "  notes TEXT,\n"
            "  sources TEXT,\n"
            "  wizard_profile TEXT,\n"
            "  media_launcher TEXT\n"
            ");\n"
            "INSERT INTO devices (\n"
            "  id, vendor, model, variant, year, cpu, gpu, ram_gb, storage_gb,\n"
            "  bios, secure_boot, tpm, usb_boot, uefi_native, reflash_potential,\n"
            "  methods, notes, sources, last_seen, windows10_boot, media_mode, udos_launcher\n"
            ") VALUES (\n"
            "  'example-device', 'Example', 'Prototype', 'Rev A', 2026, 'unknown', 'unknown', 0, 0,\n"
            "  'unknown', 'unknown', 'unknown', 'none', 'unknown', 'unknown',\n"
            "  '[\"UEFI\"]', 'Placeholder row for schema validation only.', '[]', '2026-01-25',\n"
            "  'none', 'none', 'none'\n"
            ");\n"
        ),
        encoding="utf-8",
    )
    (datasets / "sonic-devices.schema.json").write_text(
        json.dumps(
            {
                "title": "Sonic Screwdriver Device",
                "description": "Schema version 1.1",
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "id",
                    "vendor",
                    "model",
                    "year",
                    "bios",
                    "secure_boot",
                    "tpm",
                    "usb_boot",
                    "uefi_native",
                    "reflash_potential",
                    "methods",
                    "last_seen",
                    "windows10_boot",
                    "media_mode",
                    "udos_launcher",
                ],
                "properties": {
                    "id": {"type": "string"},
                    "vendor": {"type": "string"},
                    "model": {"type": "string"},
                    "variant": {"type": "string"},
                    "year": {"type": "integer"},
                    "cpu": {"type": "string"},
                    "gpu": {"type": "string"},
                    "ram_gb": {"type": "integer"},
                    "storage_gb": {"type": "integer"},
                    "bios": {"type": "string"},
                    "secure_boot": {"type": "string", "enum": ["yes", "no", "unknown"]},
                    "tpm": {"type": "string", "enum": ["yes", "no", "unknown"]},
                    "usb_boot": {"type": "string", "enum": ["native", "uefi_only", "legacy_only", "mixed", "none"]},
                    "uefi_native": {"type": "string", "enum": ["works", "issues", "unknown"]},
                    "reflash_potential": {"type": "string", "enum": ["high", "medium", "low", "unknown"]},
                    "methods": {"type": "array"},
                    "notes": {"type": "string"},
                    "sources": {"type": "array"},
                    "last_seen": {"type": "string", "format": "date"},
                    "windows10_boot": {"type": "string", "enum": ["none", "install", "wtg", "unknown"]},
                    "media_mode": {"type": "string", "enum": ["none", "htpc", "retro", "unknown"]},
                    "udos_launcher": {"type": "string", "enum": ["none", "basic", "advanced", "unknown"]},
                    "wizard_profile": {"type": "string"},
                    "media_launcher": {"type": "string"},
                },
            }
        ),
        encoding="utf-8",
    )
    (datasets / "version.json").write_text(
        json.dumps(
            {
                "component": "udos-sonic-datasets",
                "version": "v1.0.0",
                "name": "Sonic Screwdriver Device Database",
                "schema_version": "1.1",
                "updated": "2026-01-25",
            }
        ),
        encoding="utf-8",
    )


def _seed_image_source_metadata(sonic_root: Path) -> None:
    metadata_root = sonic_root / "config" / "image-sources"
    metadata_root.mkdir(parents=True, exist_ok=True)
    (metadata_root / "alpine-udos.json").write_text(
        json.dumps(
            {
                "source_id": "alpine-udos-base",
                "platform": "alpine-udos",
                "publisher": "uDOS Project",
                "channel": "stable",
                "origin_url": "https://github.com/fredporter/uDOS",
                "artifact_path": "payloads/udos/udos.squashfs",
                "artifact_kind": "squashfs",
                "license": "Project-local distribution",
                "tracked_at": "2026-03-02",
                "provenance": {"strategy": "internal-build", "verified_by": "tests"},
            }
        ),
        encoding="utf-8",
    )
    (metadata_root / "ubuntu-wizard.json").write_text(
        json.dumps(
            {
                "source_id": "ubuntu-wizard-base",
                "platform": "ubuntu-wizard",
                "publisher": "Canonical",
                "channel": "lts",
                "origin_url": "https://ubuntu.com/download",
                "artifact_path": "payloads/wizard/ubuntu.iso",
                "artifact_kind": "iso",
                "license": "Ubuntu image redistribution subject to upstream terms",
                "tracked_at": "2026-03-02",
                "provenance": {"strategy": "upstream-download", "verified_by": "tests"},
            }
        ),
        encoding="utf-8",
    )
    (metadata_root / "windows10-ltsc.json").write_text(
        json.dumps(
            {
                "source_id": "windows10-ltsc-base",
                "platform": "windows10-ltsc",
                "publisher": "Microsoft",
                "channel": "ltsc",
                "origin_url": "https://www.microsoft.com/software-download",
                "artifact_path": "payloads/windows/windows10-ltsc.iso",
                "artifact_kind": "iso",
                "license": "Windows media redistribution subject to upstream terms",
                "tracked_at": "2026-03-02",
                "provenance": {"strategy": "upstream-download", "verified_by": "tests"},
            }
        ),
        encoding="utf-8",
    )


def test_sonic_handler_fallback_when_sonic_missing(tmp_path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)

    handler = _FakeSonicHandler(repo_root=repo_root, sonic_root=repo_root / "sonic")
    result = handler.handle("SONIC", ["STATUS"])

    assert result["status"] == "error"
    assert "not installed" in result["message"].lower()


def test_sonic_sync_requires_sql(tmp_path):
    repo_root = tmp_path / "repo"
    sonic_root = repo_root / "sonic"
    (sonic_root / "datasets").mkdir(parents=True, exist_ok=True)

    handler = _FakeSonicHandler(repo_root=repo_root, sonic_root=sonic_root)
    result = handler.handle("SONIC", ["SYNC"])

    assert result["status"] == "error"
    assert "dataset sql missing" in result["message"].lower()


def test_sonic_sync_no_force_if_db_exists(tmp_path):
    repo_root = tmp_path / "repo"
    sonic_root = repo_root / "sonic"
    datasets = sonic_root / "datasets"
    datasets.mkdir(parents=True, exist_ok=True)
    (datasets / "sonic-devices.sql").write_text("CREATE TABLE devices(id TEXT);\n", encoding="utf-8")

    db_path = repo_root / "memory" / "sonic" / "sonic-devices.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db_path.write_bytes(b"placeholder")

    handler = _FakeSonicHandler(repo_root=repo_root, sonic_root=sonic_root)
    result = handler.handle("SONIC", ["SYNC"])

    assert result["status"] == "ok"
    assert "already exists" in result["message"].lower()
    assert result["db_path"].endswith("sonic-devices.db")


def test_sonic_bootstrap_registers_current_machine(tmp_path):
    repo_root = tmp_path / "repo"
    sonic_root = repo_root / "sonic"
    datasets = sonic_root / "datasets"
    datasets.mkdir(parents=True, exist_ok=True)
    (datasets / "sonic-devices.sql").write_text("CREATE TABLE devices(id TEXT PRIMARY KEY, vendor TEXT NOT NULL, model TEXT NOT NULL, year INTEGER NOT NULL, bios TEXT NOT NULL, secure_boot TEXT NOT NULL, tpm TEXT NOT NULL, usb_boot TEXT NOT NULL, uefi_native TEXT NOT NULL, reflash_potential TEXT NOT NULL, methods TEXT NOT NULL, last_seen TEXT NOT NULL, windows10_boot TEXT NOT NULL, media_mode TEXT NOT NULL, udos_launcher TEXT NOT NULL, variant TEXT, cpu TEXT, gpu TEXT, ram_gb INTEGER, storage_gb INTEGER, notes TEXT, sources TEXT, wizard_profile TEXT, media_launcher TEXT, settings_template_md TEXT, installers_template_md TEXT, containers_template_md TEXT, drivers_template_md TEXT);\n", encoding="utf-8")

    handler = _FakeSonicHandler(repo_root=repo_root, sonic_root=sonic_root)
    handler.handle("SONIC", ["SYNC", "--force"])
    result = handler.handle("SONIC", ["BOOTSTRAP"])

    assert result["status"] == "ok"
    assert result["result"]["device_id"].startswith("local-")


def test_sonic_plan_requires_wizard_mode_when_boundaries_enforced(tmp_path, monkeypatch):
    repo_root = tmp_path / "repo"
    sonic_root = repo_root / "sonic"
    sonic_root.mkdir(parents=True, exist_ok=True)

    handler = _FakeSonicHandler(repo_root=repo_root, sonic_root=sonic_root)
    monkeypatch.setattr("core.commands.sonic_handler.resolve_runtime_mode", lambda: RuntimeMode.USER)
    monkeypatch.setenv("UDOS_ENFORCE_MODE_BOUNDARIES", "1")

    result = handler.handle("SONIC", ["PLAN"])
    assert result["status"] == "warning"
    assert "restricted" in result["message"].lower()
    assert result["policy_flag"] == "wizard_mode_required"


def test_sonic_run_requires_wizard_mode_when_boundaries_enforced(tmp_path, monkeypatch):
    repo_root = tmp_path / "repo"
    sonic_root = repo_root / "sonic"
    sonic_root.mkdir(parents=True, exist_ok=True)

    handler = _FakeSonicHandler(repo_root=repo_root, sonic_root=sonic_root)
    monkeypatch.setattr("core.commands.sonic_handler.resolve_runtime_mode", lambda: RuntimeMode.USER)
    monkeypatch.setenv("UDOS_ENFORCE_MODE_BOUNDARIES", "1")

    result = handler.handle("SONIC", ["RUN", "--confirm"])
    assert result["status"] == "warning"
    assert "restricted" in result["message"].lower()
    assert result["policy_flag"] == "wizard_mode_required"


def test_sonic_verify_reports_valid_manifest(tmp_path):
    repo_root = tmp_path / "repo"
    sonic_root = repo_root / "sonic"
    config_dir = sonic_root / "config"
    payloads = sonic_root / "payloads"
    isos = sonic_root / "ISOS"
    config_dir.mkdir(parents=True, exist_ok=True)
    (payloads / "udos").mkdir(parents=True, exist_ok=True)
    (payloads / "windows").mkdir(parents=True, exist_ok=True)
    (payloads / "wizard").mkdir(parents=True, exist_ok=True)
    isos.mkdir(parents=True, exist_ok=True)
    (payloads / "udos" / "udos.squashfs").write_bytes(b"sqsh")
    (payloads / "windows" / "windows10-ltsc.iso").write_bytes(b"iso")
    (payloads / "wizard" / "ubuntu.iso").write_bytes(b"ubuntu")
    _seed_full_sonic_dataset(sonic_root)
    _seed_image_source_metadata(sonic_root)

    manifest = {
        "usb_device": "/dev/sdb",
        "boot_mode": "uefi-native",
        "repo_root": str(sonic_root),
        "payload_dir": str(payloads),
        "iso_dir": str(isos),
        "format_mode": "full",
        "partitions": [
            {"name": "esp", "label": "ESP", "fs": "fat32", "size_gb": 0.5, "payload_dir": "payloads/efi"},
            {"name": "udos_ro", "label": "UDOS_RO", "fs": "squashfs", "size_gb": 8, "image": "payloads/udos/udos.squashfs"},
            {"name": "cache", "label": "CACHE", "fs": "ext4", "remainder": True},
        ],
    }
    (config_dir / "sonic-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    handler = _FakeSonicHandler(repo_root=repo_root, sonic_root=sonic_root)
    result = handler.handle("SONIC", ["VERIFY"])

    assert result["status"] == "warning"
    assert result["verification"]["ok"] is True
    assert "media_policy" in result["verification"]
    policy_ids = {item["policy_id"] for item in result["verification"]["media_policy"]["policies"]}
    assert {"alpine-media", "ubuntu-media", "windows-media", "device-database"}.issubset(policy_ids)
    dataset_policy = next(item for item in result["verification"]["media_policy"]["policies"] if item["policy_id"] == "device-database")
    assert dataset_policy["contract"]["ok"] is True


def test_sonic_run_blocks_invalid_manifest(tmp_path, monkeypatch):
    repo_root = tmp_path / "repo"
    sonic_root = repo_root / "sonic"
    config_dir = sonic_root / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    _seed_full_sonic_dataset(sonic_root)
    _seed_image_source_metadata(sonic_root)

    invalid_manifest = {
        "usb_device": "/dev/sdb",
        "boot_mode": "uefi-native",
        "repo_root": str(sonic_root),
        "payload_dir": str(sonic_root / "payloads"),
        "iso_dir": str(sonic_root / "ISOS"),
        "format_mode": "full",
        "partitions": [
            {"name": "esp", "label": "ESP", "fs": "fat32", "size_gb": 0.5},
            {"name": "esp", "label": "ESP2", "fs": "fat32", "size_gb": 1},
        ],
    }
    (config_dir / "sonic-manifest.json").write_text(json.dumps(invalid_manifest), encoding="utf-8")

    handler = _FakeSonicHandler(repo_root=repo_root, sonic_root=sonic_root)
    monkeypatch.setattr("core.commands.sonic_handler.resolve_runtime_mode", lambda: RuntimeMode.DEV)

    result = handler.handle("SONIC", ["RUN", "--confirm"])

    assert result["status"] == "error"
    assert "failed verification" in result["message"].lower()
    assert any("duplicate partition name" in issue for issue in result["verification"]["manifest"]["errors"])


def test_sonic_run_requires_override_for_manifest_warnings(tmp_path, monkeypatch):
    repo_root = tmp_path / "repo"
    sonic_root = repo_root / "sonic"
    config_dir = sonic_root / "config"
    payloads = sonic_root / "payloads"
    isos = sonic_root / "ISOS"
    config_dir.mkdir(parents=True, exist_ok=True)
    payloads.mkdir(parents=True, exist_ok=True)
    isos.mkdir(parents=True, exist_ok=True)
    _seed_full_sonic_dataset(sonic_root)
    _seed_image_source_metadata(sonic_root)

    manifest = {
        "usb_device": "/dev/sdb",
        "boot_mode": "uefi-native",
        "repo_root": str(sonic_root),
        "payload_dir": str(payloads),
        "iso_dir": str(isos),
        "format_mode": "full",
        "partitions": [
            {"name": "udos_ro", "label": "UDOS_RO", "fs": "squashfs", "size_gb": 8, "image": "payloads/udos/udos.squashfs"},
            {"name": "cache", "label": "CACHE", "fs": "ext4", "remainder": True},
        ],
    }
    (config_dir / "sonic-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    handler = _FakeSonicHandler(repo_root=repo_root, sonic_root=sonic_root)
    monkeypatch.setattr("core.commands.sonic_handler.resolve_runtime_mode", lambda: RuntimeMode.DEV)

    blocked = handler.handle("SONIC", ["RUN", "--confirm"])
    assert blocked["status"] == "warning"
    assert "reviewed" in blocked["message"].lower()
    assert blocked["verification"]["ok"] is True
    assert blocked["verification"]["media_policy"]["issues"]

    monkeypatch.setattr("core.commands.sonic_handler.subprocess.call", lambda cmd: 0, raising=False)
    allowed = handler.handle("SONIC", ["RUN", "--confirm", "--no-validate-payloads"])
    assert allowed["status"] == "ok"
    assert allowed["verification"]["media_policy"]["issues"]


def test_sonic_verify_reports_signed_release_bundle_readiness(tmp_path, monkeypatch):
    repo_root = tmp_path / "repo"
    sonic_root = repo_root / "sonic"
    config_dir = sonic_root / "config"
    payloads = sonic_root / "payloads"
    isos = sonic_root / "ISOS"
    build_dir = repo_root / "distribution" / "builds" / "b1"
    config_dir.mkdir(parents=True, exist_ok=True)
    (payloads / "udos").mkdir(parents=True, exist_ok=True)
    (payloads / "windows").mkdir(parents=True, exist_ok=True)
    (payloads / "wizard").mkdir(parents=True, exist_ok=True)
    isos.mkdir(parents=True, exist_ok=True)
    build_dir.mkdir(parents=True, exist_ok=True)
    (payloads / "udos" / "udos.squashfs").write_bytes(b"sqsh")
    (payloads / "windows" / "windows10-ltsc.iso").write_bytes(b"iso")
    (payloads / "wizard" / "ubuntu.iso").write_bytes(b"ubuntu")
    _seed_full_sonic_dataset(sonic_root)
    _seed_image_source_metadata(sonic_root)

    manifest = {
        "usb_device": "/dev/sdb",
        "boot_mode": "uefi-native",
        "repo_root": str(sonic_root),
        "payload_dir": str(payloads),
        "iso_dir": str(isos),
        "format_mode": "full",
        "partitions": [
            {"name": "udos_ro", "label": "UDOS_RO", "fs": "squashfs", "size_gb": 8, "image": "payloads/udos/udos.squashfs"},
            {"name": "cache", "label": "CACHE", "fs": "ext4", "remainder": True},
        ],
    }
    (config_dir / "sonic-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    img_bytes = b"img"
    img_sha = hashlib.sha256(img_bytes).hexdigest()
    (build_dir / "sonic-stick.img").write_bytes(img_bytes)
    (build_dir / "build-manifest.json").write_text(
        json.dumps(
            {
                "build_id": "b1",
                "profile": "alpine-core+sonic",
                "artifacts": [{"name": "sonic-stick.img", "path": "sonic-stick.img", "sha256": img_sha}],
            }
        ),
        encoding="utf-8",
    )
    manifest_sha = hashlib.sha256((build_dir / "build-manifest.json").read_bytes()).hexdigest()
    (build_dir / "checksums.txt").write_text(
        f"{img_sha}  sonic-stick.img\n{manifest_sha}  build-manifest.json\n",
        encoding="utf-8",
    )
    (build_dir / "build-manifest.json.sig").write_text("sig", encoding="utf-8")
    (build_dir / "checksums.txt.sig").write_text("sig", encoding="utf-8")

    monkeypatch.setattr(
        "sonic.core.verify.verify_detached_signature",
        lambda payload_path, signature_path, pubkey=None: {
            "present": signature_path.exists(),
            "verified": True,
            "detail": "test",
        },
    )

    handler = _FakeSonicHandler(repo_root=repo_root, sonic_root=sonic_root)
    result = handler.handle("SONIC", ["VERIFY", "--build-id", "b1"])

    assert result["status"] == "ok"
    assert result["verification"]["release_bundle"]["release_ready"] is True


def test_sonic_verify_blocks_invalid_dataset_contract(tmp_path):
    repo_root = tmp_path / "repo"
    sonic_root = repo_root / "sonic"
    config_dir = sonic_root / "config"
    payloads = sonic_root / "payloads"
    isos = sonic_root / "ISOS"
    config_dir.mkdir(parents=True, exist_ok=True)
    (payloads / "udos").mkdir(parents=True, exist_ok=True)
    (payloads / "windows").mkdir(parents=True, exist_ok=True)
    (payloads / "wizard").mkdir(parents=True, exist_ok=True)
    isos.mkdir(parents=True, exist_ok=True)
    (payloads / "udos" / "udos.squashfs").write_bytes(b"sqsh")
    (payloads / "windows" / "windows10-ltsc.iso").write_bytes(b"iso")
    (payloads / "wizard" / "ubuntu.iso").write_bytes(b"ubuntu")
    _seed_full_sonic_dataset(sonic_root)
    _seed_image_source_metadata(sonic_root)
    datasets = sonic_root / "datasets"
    (datasets / "version.json").write_text(
        json.dumps(
            {
                "component": "udos-sonic-datasets",
                "version": "1.0.0",
                "name": "Sonic Screwdriver Device Database",
                "schema_version": "9.9",
                "updated": "20260125",
            }
        ),
        encoding="utf-8",
    )

    manifest = {
        "usb_device": "/dev/sdb",
        "boot_mode": "uefi-native",
        "repo_root": str(sonic_root),
        "payload_dir": str(payloads),
        "iso_dir": str(isos),
        "format_mode": "full",
        "partitions": [
            {"name": "udos_ro", "label": "UDOS_RO", "fs": "squashfs", "size_gb": 8, "image": "payloads/udos/udos.squashfs"},
            {"name": "cache", "label": "CACHE", "fs": "ext4", "remainder": True},
        ],
    }
    (config_dir / "sonic-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    handler = _FakeSonicHandler(repo_root=repo_root, sonic_root=sonic_root)
    result = handler.handle("SONIC", ["VERIFY"])

    assert result["status"] == "error"
    assert result["verification"]["ok"] is False
    dataset_policy = next(item for item in result["verification"]["media_policy"]["policies"] if item["policy_id"] == "device-database")
    assert dataset_policy["level"] == "error"
    assert "version.json version must use vMAJOR.MINOR.PATCH format" in dataset_policy["contract"]["errors"]


def test_sonic_verify_blocks_schema_sql_required_mismatch(tmp_path):
    repo_root = tmp_path / "repo"
    sonic_root = repo_root / "sonic"
    config_dir = sonic_root / "config"
    payloads = sonic_root / "payloads"
    isos = sonic_root / "ISOS"
    config_dir.mkdir(parents=True, exist_ok=True)
    (payloads / "udos").mkdir(parents=True, exist_ok=True)
    (payloads / "windows").mkdir(parents=True, exist_ok=True)
    (payloads / "wizard").mkdir(parents=True, exist_ok=True)
    isos.mkdir(parents=True, exist_ok=True)
    (payloads / "udos" / "udos.squashfs").write_bytes(b"sqsh")
    (payloads / "windows" / "windows10-ltsc.iso").write_bytes(b"iso")
    (payloads / "wizard" / "ubuntu.iso").write_bytes(b"ubuntu")
    _seed_full_sonic_dataset(sonic_root)
    _seed_image_source_metadata(sonic_root)
    datasets = sonic_root / "datasets"
    (datasets / "sonic-devices.sql").write_text(
        "CREATE TABLE devices(id TEXT PRIMARY KEY, vendor TEXT NOT NULL, model TEXT NOT NULL);\n",
        encoding="utf-8",
    )

    manifest = {
        "usb_device": "/dev/sdb",
        "boot_mode": "uefi-native",
        "repo_root": str(sonic_root),
        "payload_dir": str(payloads),
        "iso_dir": str(isos),
        "format_mode": "full",
        "partitions": [
            {"name": "udos_ro", "label": "UDOS_RO", "fs": "squashfs", "size_gb": 8, "image": "payloads/udos/udos.squashfs"},
            {"name": "cache", "label": "CACHE", "fs": "ext4", "remainder": True},
        ],
    }
    (config_dir / "sonic-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    handler = _FakeSonicHandler(repo_root=repo_root, sonic_root=sonic_root)
    result = handler.handle("SONIC", ["VERIFY"])

    assert result["status"] == "error"
    dataset_policy = next(item for item in result["verification"]["media_policy"]["policies"] if item["policy_id"] == "device-database")
    assert dataset_policy["contract"]["diff"]["missing_sql_columns"]
    assert dataset_policy["contract"]["errors"]


def test_sonic_verify_blocks_invalid_seed_row_content(tmp_path):
    repo_root = tmp_path / "repo"
    sonic_root = repo_root / "sonic"
    config_dir = sonic_root / "config"
    payloads = sonic_root / "payloads"
    isos = sonic_root / "ISOS"
    config_dir.mkdir(parents=True, exist_ok=True)
    (payloads / "udos").mkdir(parents=True, exist_ok=True)
    (payloads / "windows").mkdir(parents=True, exist_ok=True)
    (payloads / "wizard").mkdir(parents=True, exist_ok=True)
    isos.mkdir(parents=True, exist_ok=True)
    (payloads / "udos" / "udos.squashfs").write_bytes(b"sqsh")
    (payloads / "windows" / "windows10-ltsc.iso").write_bytes(b"iso")
    (payloads / "wizard" / "ubuntu.iso").write_bytes(b"ubuntu")
    _seed_full_sonic_dataset(sonic_root)
    _seed_image_source_metadata(sonic_root)
    datasets = sonic_root / "datasets"
    (datasets / "sonic-devices.sql").write_text(
        (
            "-- Sonic Screwdriver device database (schema + seed)\n"
            "DROP TABLE IF EXISTS devices;\n"
            "CREATE TABLE devices (\n"
            "  id TEXT PRIMARY KEY,\n"
            "  vendor TEXT NOT NULL,\n"
            "  model TEXT NOT NULL,\n"
            "  year INTEGER NOT NULL,\n"
            "  bios TEXT NOT NULL,\n"
            "  secure_boot TEXT NOT NULL,\n"
            "  tpm TEXT NOT NULL,\n"
            "  usb_boot TEXT NOT NULL,\n"
            "  uefi_native TEXT NOT NULL,\n"
            "  reflash_potential TEXT NOT NULL,\n"
            "  methods TEXT NOT NULL,\n"
            "  last_seen TEXT NOT NULL,\n"
            "  windows10_boot TEXT NOT NULL,\n"
            "  media_mode TEXT NOT NULL,\n"
            "  udos_launcher TEXT NOT NULL\n"
            ");\n"
            "INSERT INTO devices (\n"
            "  id, vendor, model, year, bios, secure_boot, tpm, usb_boot, uefi_native,\n"
            "  reflash_potential, methods, last_seen, windows10_boot, media_mode, udos_launcher\n"
            ") VALUES (\n"
            "  'example-device', 'Example', 'Prototype', 2026, 'unknown', 'unknown', 'unknown', 'bad-mode', 'unknown',\n"
            "  'unknown', 'not-json', '20260125', 'none', 'none', 'none'\n"
            ");\n"
        ),
        encoding="utf-8",
    )

    manifest = {
        "usb_device": "/dev/sdb",
        "boot_mode": "uefi-native",
        "repo_root": str(sonic_root),
        "payload_dir": str(payloads),
        "iso_dir": str(isos),
        "format_mode": "full",
        "partitions": [
            {"name": "udos_ro", "label": "UDOS_RO", "fs": "squashfs", "size_gb": 8, "image": "payloads/udos/udos.squashfs"},
            {"name": "cache", "label": "CACHE", "fs": "ext4", "remainder": True},
        ],
    }
    (config_dir / "sonic-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    handler = _FakeSonicHandler(repo_root=repo_root, sonic_root=sonic_root)
    result = handler.handle("SONIC", ["VERIFY"])

    assert result["status"] == "error"
    dataset_policy = next(item for item in result["verification"]["media_policy"]["policies"] if item["policy_id"] == "device-database")
    assert any("seed row #1: seed row field 'methods' must contain JSON array text" in item for item in dataset_policy["contract"]["errors"])
    assert any("seed row #1: seed row field 'usb_boot' must be one of" in item for item in dataset_policy["contract"]["errors"])


def test_sonic_verify_blocks_invalid_media_metadata(tmp_path):
    repo_root = tmp_path / "repo"
    sonic_root = repo_root / "sonic"
    config_dir = sonic_root / "config"
    payloads = sonic_root / "payloads"
    isos = sonic_root / "ISOS"
    config_dir.mkdir(parents=True, exist_ok=True)
    (payloads / "udos").mkdir(parents=True, exist_ok=True)
    (payloads / "windows").mkdir(parents=True, exist_ok=True)
    (payloads / "wizard").mkdir(parents=True, exist_ok=True)
    isos.mkdir(parents=True, exist_ok=True)
    (payloads / "udos" / "udos.squashfs").write_bytes(b"sqsh")
    (payloads / "windows" / "windows10-ltsc.iso").write_bytes(b"iso")
    (payloads / "wizard" / "ubuntu.iso").write_bytes(b"ubuntu")
    _seed_full_sonic_dataset(sonic_root)
    _seed_image_source_metadata(sonic_root)
    metadata_root = sonic_root / "config" / "image-sources"
    (metadata_root / "windows10-ltsc.json").write_text(
        json.dumps(
            {
                "source_id": "windows10-ltsc-base",
                "platform": "windows10-ltsc",
                "publisher": "Microsoft",
                "channel": "ltsc",
                "origin_url": "http://invalid.example",
                "artifact_path": "payloads/windows/wrong.iso",
                "artifact_kind": "img",
                "license": "Windows media redistribution subject to upstream terms",
                "tracked_at": "2026-03-02",
                "provenance": {"strategy": "upstream-download", "verified_by": "tests"},
            }
        ),
        encoding="utf-8",
    )

    manifest = {
        "usb_device": "/dev/sdb",
        "boot_mode": "uefi-native",
        "repo_root": str(sonic_root),
        "payload_dir": str(payloads),
        "iso_dir": str(isos),
        "format_mode": "full",
        "partitions": [
            {"name": "udos_ro", "label": "UDOS_RO", "fs": "squashfs", "size_gb": 8, "image": "payloads/udos/udos.squashfs"},
            {"name": "cache", "label": "CACHE", "fs": "ext4", "remainder": True},
        ],
    }
    (config_dir / "sonic-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    handler = _FakeSonicHandler(repo_root=repo_root, sonic_root=sonic_root)
    result = handler.handle("SONIC", ["VERIFY"])

    assert result["status"] == "error"
    windows_policy = next(item for item in result["verification"]["media_policy"]["policies"] if item["policy_id"] == "windows-media")
    assert windows_policy["level"] == "error"
    assert "metadata origin_url must use https" in windows_policy["metadata"]["errors"]
