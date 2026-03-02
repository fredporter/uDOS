"""Sonic Screwdriver manifest utilities."""

import json
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, List, Optional, Any

ALLOWED_BOOT_MODES = {"uefi-native"}
ALLOWED_FORMAT_MODES = {"full", "skip"}


@dataclass
class PartitionSpec:
    name: str
    label: str
    fs: str
    size_gb: Optional[float] = None
    remainder: bool = False
    mount: Optional[str] = None
    format: bool = True
    flags: List[str] = field(default_factory=list)
    role: Optional[str] = None
    scalable: bool = False
    min_size_gb: Optional[float] = None
    max_size_gb: Optional[float] = None
    image: Optional[str] = None
    payload_dir: Optional[str] = None


@dataclass
class SonicManifest:
    usb_device: str
    boot_mode: str
    repo_root: str
    payload_dir: str
    iso_dir: str
    flash_label: str = "FLASH"
    sonic_label: str = "SONIC"
    esp_label: str = "ESP"
    dry_run: bool = False
    format_mode: str = "full"
    auto_scale: bool = False
    partitions: List[PartitionSpec] = field(default_factory=list)

    def to_dict(self) -> Dict:
        data = asdict(self)
        return data


def write_manifest(path: Path, manifest: SonicManifest) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest.to_dict(), indent=2))


def read_manifest(path: Path) -> Optional[Dict]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return None


def _resolve_manifest_path(base: Path, value: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    return base / candidate


def _default_partitions() -> List[PartitionSpec]:
    return [
        PartitionSpec(name="esp", label="ESP", fs="fat32", size_gb=0.5, flags=["boot", "esp"], role="efi"),
        PartitionSpec(name="udos_ro", label="UDOS_RO", fs="squashfs", size_gb=8, role="udos"),
        PartitionSpec(name="udos_rw", label="UDOS_RW", fs="ext4", size_gb=8, mount="/mnt/udos", role="udos"),
        PartitionSpec(name="swap", label="SWAP", fs="swap", size_gb=8, role="swap"),
        PartitionSpec(name="wizard", label="WIZARD", fs="ext4", size_gb=20, mount="/mnt/wizard", role="wizard"),
        PartitionSpec(name="win10", label="WIN10", fs="ntfs", size_gb=48, role="windows"),
        PartitionSpec(name="media", label="MEDIA", fs="exfat", size_gb=28, mount="/mnt/media", role="media"),
        PartitionSpec(name="cache", label="CACHE", fs="ext4", remainder=True, mount="/mnt/cache", role="cache"),
    ]

def validate_partitions(partitions: List[PartitionSpec]) -> None:
    remainder_count = sum(1 for p in partitions if p.remainder)
    if remainder_count > 1:
        raise ValueError("Only one remainder partition is allowed.")
    for p in partitions:
        if p.remainder:
            continue
        if p.size_gb is None or p.size_gb <= 0:
            raise ValueError(f"Partition '{p.name}' must define a positive size_gb.")

def _load_partitions(layout_path: Optional[Path]) -> List[PartitionSpec]:
    if not layout_path:
        return _default_partitions()
    if not layout_path.exists():
        return _default_partitions()
    try:
        data = json.loads(layout_path.read_text())
    except json.JSONDecodeError:
        return _default_partitions()
    partitions = []
    for item in data.get("partitions", []):
        partitions.append(
            PartitionSpec(
                name=item.get("name", ""),
                label=item.get("label", ""),
                fs=item.get("fs", ""),
                size_gb=item.get("size_gb"),
                remainder=item.get("remainder", False),
                mount=item.get("mount"),
                format=item.get("format", True),
                flags=item.get("flags", []),
                role=item.get("role"),
                scalable=item.get("scalable", False),
                min_size_gb=item.get("min_size_gb"),
                max_size_gb=item.get("max_size_gb"),
                image=item.get("image"),
                payload_dir=item.get("payload_dir"),
            )
        )
    return partitions or _default_partitions()


def _load_format_mode(layout_path: Optional[Path]) -> Optional[str]:
    if not layout_path or not layout_path.exists():
        return None
    try:
        data = json.loads(layout_path.read_text())
    except json.JSONDecodeError:
        return None
    mode = data.get("format_mode")
    if mode in {"full", "skip"}:
        return mode
    return None


def _load_auto_scale(layout_path: Optional[Path]) -> Optional[bool]:
    if not layout_path or not layout_path.exists():
        return None
    try:
        data = json.loads(layout_path.read_text())
    except json.JSONDecodeError:
        return None
    if "auto_scale" in data:
        return bool(data.get("auto_scale"))
    return None


def default_manifest(
    repo_root: Path,
    usb_device: str,
    dry_run: bool,
    layout_path: Optional[Path] = None,
    format_mode: Optional[str] = None,
    payload_dir: Optional[Path] = None,
) -> SonicManifest:
    resolved_payload_dir = payload_dir or (repo_root / "payloads")
    iso_dir = repo_root / "ISOS"
    resolved_format = format_mode or _load_format_mode(layout_path) or "full"
    resolved_auto_scale = _load_auto_scale(layout_path) or False
    partitions = _load_partitions(layout_path)
    validate_partitions(partitions)
    return SonicManifest(
        usb_device=usb_device,
        boot_mode="uefi-native",
        repo_root=str(repo_root),
        payload_dir=str(resolved_payload_dir),
        iso_dir=str(iso_dir),
        dry_run=dry_run,
        format_mode=resolved_format,
        auto_scale=resolved_auto_scale,
        partitions=partitions,
    )


def validate_manifest_data(manifest: Dict[str, Any], manifest_path: Optional[Path] = None) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []
    required_keys = ["usb_device", "boot_mode", "repo_root", "payload_dir", "iso_dir", "partitions"]
    missing_keys = [key for key in required_keys if key not in manifest]
    if missing_keys:
        errors.append(f"missing required manifest keys: {', '.join(sorted(missing_keys))}")

    partitions_raw = manifest.get("partitions")
    partition_summaries: List[Dict[str, Any]] = []
    if not isinstance(partitions_raw, list) or not partitions_raw:
        errors.append("manifest must define at least one partition")
        partitions_raw = []

    boot_mode = manifest.get("boot_mode")
    if boot_mode and boot_mode not in ALLOWED_BOOT_MODES:
        errors.append(f"unsupported boot_mode '{boot_mode}'")

    format_mode = manifest.get("format_mode", "full")
    if format_mode not in ALLOWED_FORMAT_MODES:
        errors.append(f"unsupported format_mode '{format_mode}'")

    usb_device = str(manifest.get("usb_device", "")).strip()
    if usb_device and not usb_device.startswith("/dev/"):
        warnings.append(f"usb_device '{usb_device}' is not a Linux block-device path")

    repo_root_raw = str(manifest.get("repo_root", "")).strip()
    manifest_base = manifest_path.parent if manifest_path else Path.cwd()
    repo_root = _resolve_manifest_path(manifest_base, repo_root_raw) if repo_root_raw else None
    if repo_root is None:
        errors.append("manifest repo_root is required")
    elif not repo_root.exists():
        warnings.append(f"repo_root does not exist: {repo_root}")

    payload_dir_raw = str(manifest.get("payload_dir", "")).strip()
    iso_dir_raw = str(manifest.get("iso_dir", "")).strip()
    payload_dir = None
    iso_dir = None
    if repo_root is not None:
        if payload_dir_raw:
            payload_dir = _resolve_manifest_path(repo_root, payload_dir_raw)
            if not payload_dir.exists():
                warnings.append(f"payload_dir does not exist: {payload_dir}")
        else:
            errors.append("manifest payload_dir is required")
        if iso_dir_raw:
            iso_dir = _resolve_manifest_path(repo_root, iso_dir_raw)
            if not iso_dir.exists():
                warnings.append(f"iso_dir does not exist: {iso_dir}")
        else:
            errors.append("manifest iso_dir is required")

    seen_names: set[str] = set()
    seen_labels: set[str] = set()
    remainder_count = 0
    missing_payload_refs: List[str] = []

    for index, item in enumerate(partitions_raw):
        if not isinstance(item, dict):
            errors.append(f"partition #{index + 1} must be an object")
            continue
        name = str(item.get("name", "")).strip()
        label = str(item.get("label", "")).strip()
        fs = str(item.get("fs", "")).strip()
        remainder = bool(item.get("remainder", False))
        size_gb = item.get("size_gb")

        if not name:
            errors.append(f"partition #{index + 1} is missing name")
        elif name in seen_names:
            errors.append(f"duplicate partition name '{name}'")
        else:
            seen_names.add(name)

        if not label:
            errors.append(f"partition '{name or index + 1}' is missing label")
        elif label in seen_labels:
            errors.append(f"duplicate partition label '{label}'")
        else:
            seen_labels.add(label)

        if not fs:
            errors.append(f"partition '{name or index + 1}' is missing fs")
        if remainder:
            remainder_count += 1
        elif not isinstance(size_gb, (int, float)) or float(size_gb) <= 0:
            errors.append(f"partition '{name or index + 1}' must define a positive size_gb")

        partition_summary = {
            "name": name,
            "label": label,
            "fs": fs,
            "remainder": remainder,
            "size_gb": size_gb,
            "role": item.get("role"),
        }

        for key in ("image", "payload_dir"):
            raw_ref = item.get(key)
            if not raw_ref:
                continue
            resolved_ref = None
            if repo_root is not None:
                resolved_ref = _resolve_manifest_path(repo_root, str(raw_ref))
                if not resolved_ref.exists():
                    missing_payload_refs.append(f"{name}:{key}:{resolved_ref}")
            partition_summary[f"{key}_path"] = str(resolved_ref) if resolved_ref else str(raw_ref)

        partition_summaries.append(partition_summary)

    if remainder_count > 1:
        errors.append("only one remainder partition is allowed")
    for ref in missing_payload_refs:
        warnings.append(f"missing payload reference: {ref}")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "required_keys": required_keys,
        "paths": {
            "manifest": str(manifest_path) if manifest_path else None,
            "repo_root": str(repo_root) if repo_root else repo_root_raw,
            "payload_dir": str(payload_dir) if payload_dir else payload_dir_raw,
            "iso_dir": str(iso_dir) if iso_dir else iso_dir_raw,
        },
        "summary": {
            "partition_count": len(partition_summaries),
            "remainder_partitions": remainder_count,
            "missing_payload_references": len(missing_payload_refs),
        },
        "partitions": partition_summaries,
    }


def verify_manifest_path(path: Path) -> Dict[str, Any]:
    payload = read_manifest(path)
    if payload is None:
        return {
            "ok": False,
            "errors": [f"unable to read manifest: {path}"],
            "warnings": [],
            "paths": {"manifest": str(path)},
            "summary": {"partition_count": 0, "remainder_partitions": 0, "missing_payload_references": 0},
            "partitions": [],
        }
    return validate_manifest_data(payload, manifest_path=path)
