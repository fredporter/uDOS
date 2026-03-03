"""Shared Sonic verification utilities for CLI and Wizard surfaces."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from datetime import date
from pathlib import Path
from typing import Any

from .manifest import verify_manifest_path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_detached_signature(
    payload_path: Path, signature_path: Path, pubkey: str | None = None
) -> dict[str, Any]:
    if not payload_path.exists():
        return {"present": signature_path.exists(), "verified": False, "detail": "payload missing"}
    if not signature_path.exists():
        return {"present": False, "verified": False, "detail": "signature missing"}

    resolved_pubkey = (pubkey or os.environ.get("WIZARD_SONIC_SIGN_PUBKEY", "")).strip()
    if not resolved_pubkey:
        return {"present": True, "verified": False, "detail": "WIZARD_SONIC_SIGN_PUBKEY not configured"}

    pubkey_path = Path(resolved_pubkey)
    if not pubkey_path.exists():
        return {"present": True, "verified": False, "detail": f"public key not found: {pubkey_path}"}

    verify = subprocess.run(
        [
            "openssl",
            "dgst",
            "-sha256",
            "-verify",
            str(pubkey_path),
            "-signature",
            str(signature_path),
            str(payload_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if verify.returncode == 0:
        return {"present": True, "verified": True, "detail": "signature verified via openssl"}
    detail = (verify.stderr or verify.stdout or "openssl verify failed").strip()
    return {"present": True, "verified": False, "detail": detail}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _policy_entry(policy_id: str, level: str, detail: str, **extra: Any) -> dict[str, Any]:
    return {"policy_id": policy_id, "level": level, "detail": detail, **extra}


def _validate_image_source_metadata(
    metadata_path: Path,
    *,
    expected_platform: str,
    expected_artifact: Path,
    expected_kind: str,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if not metadata_path.exists():
        return {
            "ok": False,
            "errors": [f"metadata file missing: {metadata_path}"],
            "warnings": [],
            "metadata": None,
        }

    metadata = _read_json(metadata_path)
    required_keys = {
        "source_id",
        "platform",
        "publisher",
        "channel",
        "origin_url",
        "artifact_path",
        "artifact_kind",
        "license",
        "tracked_at",
        "provenance",
    }
    missing = sorted(required_keys - set(metadata.keys()))
    if missing:
        errors.append(f"metadata missing required keys: {', '.join(missing)}")

    if str(metadata.get("platform") or "").strip() != expected_platform:
        errors.append(f"metadata platform must be '{expected_platform}'")
    if str(metadata.get("artifact_kind") or "").strip() != expected_kind:
        errors.append(f"metadata artifact_kind must be '{expected_kind}'")
    if not str(metadata.get("source_id") or "").strip():
        errors.append("metadata source_id must be non-empty")
    if not str(metadata.get("publisher") or "").strip():
        errors.append("metadata publisher must be non-empty")
    if not str(metadata.get("channel") or "").strip():
        errors.append("metadata channel must be non-empty")

    origin_url = str(metadata.get("origin_url") or "").strip()
    if not re.fullmatch(r"https://\S+", origin_url):
        errors.append("metadata origin_url must use https")

    tracked_at = str(metadata.get("tracked_at") or "").strip()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", tracked_at):
        errors.append("metadata tracked_at must use YYYY-MM-DD format")

    artifact_value = str(metadata.get("artifact_path") or "").strip()
    artifact_path = metadata_path.parents[2] / artifact_value if artifact_value else None
    if artifact_path is None:
        errors.append("metadata artifact_path must be non-empty")
    else:
        if artifact_path != expected_artifact:
            errors.append(f"metadata artifact_path must resolve to {expected_artifact}")
        if not artifact_path.exists():
            warnings.append(f"declared artifact missing: {artifact_path}")

    provenance = metadata.get("provenance")
    if not isinstance(provenance, dict):
        errors.append("metadata provenance must be an object")
        provenance = {}
    else:
        required_provenance = {"strategy", "verified_by"}
        missing_provenance = sorted(required_provenance - set(provenance.keys()))
        if missing_provenance:
            errors.append(f"metadata provenance missing keys: {', '.join(missing_provenance)}")
        if not str(provenance.get("strategy") or "").strip():
            errors.append("metadata provenance.strategy must be non-empty")
        if not str(provenance.get("verified_by") or "").strip():
            errors.append("metadata provenance.verified_by must be non-empty")
        checksum = provenance.get("checksum_sha256")
        if checksum is not None and not re.fullmatch(r"[0-9a-f]{64}", str(checksum).strip()):
            errors.append("metadata provenance.checksum_sha256 must be a 64-character lowercase sha256 digest")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "metadata": metadata,
    }


def _parse_sql_columns(sql_text: str) -> tuple[set[str], set[str]]:
    create_match = re.search(r"CREATE\s+TABLE\s+devices\s*\((.*?)\)\s*;", sql_text, re.IGNORECASE | re.DOTALL)
    if not create_match:
        return set(), set()

    block = create_match.group(1)
    columns: set[str] = set()
    required: set[str] = set()
    for raw_line in block.splitlines():
        line = raw_line.strip().rstrip(",")
        if not line or line.upper().startswith(("PRIMARY KEY", "UNIQUE", "FOREIGN KEY", "CONSTRAINT", "CHECK")):
            continue
        parts = line.split()
        if not parts:
            continue
        name = parts[0].strip('"`[]')
        columns.add(name)
        upper = line.upper()
        if "PRIMARY KEY" in upper or "NOT NULL" in upper:
            required.add(name)
    return columns, required


def _extract_schema_version_hint(schema_payload: dict[str, Any]) -> str | None:
    for key in ("description", "title"):
        value = str(schema_payload.get(key) or "").strip()
        match = re.search(r"(\d+\.\d+)", value)
        if match:
            return match.group(1)
    return None


def _split_sql_tokens(raw: str) -> list[str]:
    tokens: list[str] = []
    current: list[str] = []
    in_string = False
    i = 0
    while i < len(raw):
        ch = raw[i]
        if ch == "'":
            current.append(ch)
            if in_string and i + 1 < len(raw) and raw[i + 1] == "'":
                current.append(raw[i + 1])
                i += 2
                continue
            in_string = not in_string
            i += 1
            continue
        if ch == "," and not in_string:
            token = "".join(current).strip()
            if token:
                tokens.append(token)
            current = []
            i += 1
            continue
        current.append(ch)
        i += 1
    tail = "".join(current).strip()
    if tail:
        tokens.append(tail)
    return tokens


def _decode_sql_value(token: str) -> Any:
    value = token.strip()
    if not value:
        return ""
    if value.upper() == "NULL":
        return None
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?\d+\.\d+", value):
        return float(value)
    return value


def _parse_seed_rows(sql_text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    pattern = re.compile(
        r"INSERT\s+INTO\s+devices\s*\((.*?)\)\s*VALUES\s*\((.*?)\)\s*;",
        re.IGNORECASE | re.DOTALL,
    )
    for match in pattern.finditer(sql_text):
        columns = [item.strip().strip('"`[]') for item in _split_sql_tokens(match.group(1))]
        values = [_decode_sql_value(item) for item in _split_sql_tokens(match.group(2))]
        if len(columns) != len(values):
            rows.append({"__parse_error__": f"seed row column/value mismatch: {len(columns)} != {len(values)}"})
            continue
        rows.append(dict(zip(columns, values)))
    return rows


def _validate_seed_row_content(
    row: dict[str, Any],
    properties: dict[str, Any],
    required_fields: list[Any],
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    normalized = dict(row)

    if "__parse_error__" in row:
        return {"ok": False, "errors": [str(row["__parse_error__"])], "warnings": [], "row": row}

    for field in required_fields:
        if field not in row or row[field] in (None, ""):
            errors.append(f"seed row missing required field '{field}'")

    for field, value in list(row.items()):
        if field not in properties:
            warnings.append(f"seed row field '{field}' is not declared in schema")
            continue
        schema = properties.get(field) or {}
        expected_type = schema.get("type")
        if expected_type == "integer" and not isinstance(value, int):
            errors.append(f"seed row field '{field}' must be integer")
        elif expected_type == "string":
            if not isinstance(value, str):
                errors.append(f"seed row field '{field}' must be string")
            elif schema.get("format") == "date":
                try:
                    date.fromisoformat(value)
                except ValueError:
                    errors.append(f"seed row field '{field}' must use YYYY-MM-DD format")
        elif expected_type == "array":
            if isinstance(value, str):
                try:
                    decoded = json.loads(value)
                except json.JSONDecodeError:
                    errors.append(f"seed row field '{field}' must contain JSON array text")
                    continue
                if not isinstance(decoded, list):
                    errors.append(f"seed row field '{field}' must decode to an array")
                    continue
                normalized[field] = decoded
                value = decoded
            if not isinstance(value, list):
                errors.append(f"seed row field '{field}' must be array-like")

        enum_values = schema.get("enum")
        if enum_values and value not in enum_values:
            errors.append(f"seed row field '{field}' must be one of: {', '.join(str(item) for item in enum_values)}")

    return {"ok": not errors, "errors": errors, "warnings": warnings, "row": normalized}


def _validate_dataset_contract(dataset_root: Path) -> dict[str, Any]:
    schema_path = dataset_root / "sonic-devices.schema.json"
    version_path = dataset_root / "version.json"
    sql_path = dataset_root / "sonic-devices.sql"

    schema_payload = _read_json(schema_path)
    version_payload = _read_json(version_path)
    sql_text = sql_path.read_text(encoding="utf-8")

    errors: list[str] = []
    warnings: list[str] = []

    required_version_keys = {"component", "version", "name", "schema_version", "updated"}
    missing_version = sorted(required_version_keys - set(version_payload.keys()))
    if missing_version:
        errors.append(f"version.json missing required keys: {', '.join(missing_version)}")
    if version_payload.get("component") != "udos-sonic-datasets":
        errors.append("version.json component must be 'udos-sonic-datasets'")
    version_value = str(version_payload.get("version") or "").strip()
    if not re.fullmatch(r"v\d+\.\d+\.\d+", version_value):
        errors.append("version.json version must use vMAJOR.MINOR.PATCH format")
    schema_version = str(version_payload.get("schema_version") or "").strip()
    if not re.fullmatch(r"\d+\.\d+", schema_version):
        errors.append("version.json schema_version must use MAJOR.MINOR format")
    updated = str(version_payload.get("updated") or "").strip()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", updated):
        errors.append("version.json updated must use YYYY-MM-DD format")

    if schema_payload.get("type") != "object":
        errors.append("sonic-devices.schema.json must describe an object")
    properties = schema_payload.get("properties")
    if not isinstance(properties, dict) or not properties:
        errors.append("sonic-devices.schema.json must define properties")
        properties = {}
    required_fields = schema_payload.get("required")
    if not isinstance(required_fields, list) or not required_fields:
        errors.append("sonic-devices.schema.json must define required fields")
        required_fields = []
    additional_properties = schema_payload.get("additionalProperties")
    if additional_properties is not False:
        warnings.append("sonic-devices.schema.json should set additionalProperties=false")

    schema_columns = set(properties.keys())
    sql_columns, sql_required = _parse_sql_columns(sql_text)
    seed_rows = _parse_seed_rows(sql_text)
    if not sql_columns:
        errors.append("sonic-devices.sql must define a devices table")
    missing_sql_columns = sorted(schema_columns - sql_columns)
    missing_schema_columns = sorted(sql_columns - schema_columns)
    required_mismatch = sorted(set(required_fields).symmetric_difference(sql_required))
    if missing_sql_columns:
        errors.append(f"schema properties missing from SQL devices table: {', '.join(missing_sql_columns)}")
    if missing_schema_columns:
        warnings.append(f"SQL devices columns missing from schema properties: {', '.join(missing_schema_columns)}")
    if required_mismatch:
        errors.append(f"required field mismatch between SQL and schema: {', '.join(required_mismatch)}")

    hinted_schema_version = _extract_schema_version_hint(schema_payload)
    if hinted_schema_version and schema_version and hinted_schema_version != schema_version:
        errors.append(
            f"schema version mismatch between version.json ({schema_version}) and schema metadata ({hinted_schema_version})"
        )

    seed_validation: list[dict[str, Any]] = []
    if not seed_rows:
        errors.append("sonic-devices.sql must include at least one devices seed row")
    for index, row in enumerate(seed_rows, start=1):
        result = _validate_seed_row_content(row, properties, required_fields)
        result["index"] = index
        seed_validation.append(result)
        if not result["ok"]:
            errors.extend(f"seed row #{index}: {item}" for item in result["errors"])
        warnings.extend(f"seed row #{index}: {item}" for item in result["warnings"])

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "version": version_payload,
        "schema": {
            "required": sorted(str(item) for item in required_fields),
            "properties": sorted(schema_columns),
            "additional_properties": additional_properties,
            "schema_version_hint": hinted_schema_version,
        },
        "sql": {
            "columns": sorted(sql_columns),
            "required": sorted(sql_required),
            "seed_rows": seed_validation,
        },
        "diff": {
            "missing_sql_columns": missing_sql_columns,
            "missing_schema_columns": missing_schema_columns,
            "required_mismatch_fields": required_mismatch,
        },
    }


def verify_media_inputs(
    sonic_root: Path,
    *,
    manifest_path: Path | None = None,
    flash_pack: str | None = None,
) -> dict[str, Any]:
    payloads_root = sonic_root / "payloads"
    dataset_root = sonic_root / "datasets"
    memory_root = sonic_root.parent / "memory" / "sonic"
    legacy_db = memory_root / "sonic-devices.db"
    seed_db = memory_root / "seed" / "sonic-devices.seed.db"
    user_db = memory_root / "user" / "sonic-devices.user.db"
    local_device_db_ready = legacy_db.exists() or seed_db.exists() or user_db.exists()
    local_device_db_paths = [str(path) for path in (legacy_db, seed_db, user_db)]
    policies: list[dict[str, Any]] = []
    issues: list[str] = []
    metadata_root = sonic_root / "config" / "image-sources"

    alpine_image = payloads_root / "udos" / "udos.squashfs"
    alpine_metadata = _validate_image_source_metadata(
        metadata_root / "alpine-udos.json",
        expected_platform="alpine-udos",
        expected_artifact=alpine_image,
        expected_kind="squashfs",
    )
    if alpine_image.exists():
        policies.append(
            _policy_entry(
                "alpine-media",
                "ok" if alpine_metadata["ok"] else "error",
                "Alpine/uDOS squashfs present" if alpine_metadata["ok"] else "Alpine/uDOS image-source metadata invalid",
                path=str(alpine_image),
                metadata=alpine_metadata,
            )
        )
        if not alpine_metadata["ok"]:
            issues.append("invalid_alpine_media_metadata")
    else:
        policies.append(
            _policy_entry(
                "alpine-media",
                "warning",
                "Missing Alpine/uDOS squashfs",
                path=str(alpine_image),
                metadata=alpine_metadata,
            )
        )
        issues.append("missing_alpine_media")

    ubuntu_root = payloads_root / "wizard"
    ubuntu_candidates = sorted(
        path.name
        for pattern in ("*.iso", "*.img", "*.squashfs", "*.tar*", "*.qcow2")
        for path in ubuntu_root.glob(pattern)
    ) if ubuntu_root.exists() else []
    ubuntu_metadata = _validate_image_source_metadata(
        metadata_root / "ubuntu-wizard.json",
        expected_platform="ubuntu-wizard",
        expected_artifact=ubuntu_root / "ubuntu.iso",
        expected_kind="iso",
    )
    if ubuntu_candidates:
        policies.append(
            _policy_entry(
                "ubuntu-media",
                "ok" if ubuntu_metadata["ok"] else "error",
                "Ubuntu/Wizard media source present" if ubuntu_metadata["ok"] else "Ubuntu/Wizard image-source metadata invalid",
                root=str(ubuntu_root),
                candidates=ubuntu_candidates,
                metadata=ubuntu_metadata,
            )
        )
        if not ubuntu_metadata["ok"]:
            issues.append("invalid_ubuntu_media_metadata")
    else:
        policies.append(
            _policy_entry(
                "ubuntu-media",
                "warning",
                "Ubuntu/Wizard media source not found",
                root=str(ubuntu_root),
                metadata=ubuntu_metadata,
            )
        )
        issues.append("missing_ubuntu_media")

    windows_iso = payloads_root / "windows" / "windows10-ltsc.iso"
    windows_metadata = _validate_image_source_metadata(
        metadata_root / "windows10-ltsc.json",
        expected_platform="windows10-ltsc",
        expected_artifact=windows_iso,
        expected_kind="iso",
    )
    if windows_iso.exists():
        policies.append(
            _policy_entry(
                "windows-media",
                "ok" if windows_metadata["ok"] else "error",
                "Windows 10 media ISO present" if windows_metadata["ok"] else "Windows 10 image-source metadata invalid",
                path=str(windows_iso),
                metadata=windows_metadata,
            )
        )
        if not windows_metadata["ok"]:
            issues.append("invalid_windows_media_metadata")
    else:
        policies.append(
            _policy_entry(
                "windows-media",
                "warning",
                "Windows 10 media ISO missing",
                path=str(windows_iso),
                metadata=windows_metadata,
            )
        )
        issues.append("missing_windows_media")

    dataset_files = {
        "sql": dataset_root / "sonic-devices.sql",
        "schema": dataset_root / "sonic-devices.schema.json",
        "version": dataset_root / "version.json",
    }
    missing_dataset = [name for name, path in dataset_files.items() if not path.exists()]
    if missing_dataset:
        policies.append(
            _policy_entry(
                "device-database",
                "error",
                f"Missing Sonic dataset files: {', '.join(missing_dataset)}",
                root=str(dataset_root),
            )
        )
        issues.append("device_database_contract_missing")
    else:
        dataset_contract = _validate_dataset_contract(dataset_root)
        dataset_version = dataset_contract["version"]
        policies.append(
            _policy_entry(
                "device-database",
                "ok" if dataset_contract["ok"] else "error",
                "Sonic dataset contract validated" if dataset_contract["ok"] else "Sonic dataset contract validation failed",
                root=str(dataset_root),
                version=str(dataset_version.get("version") or "unknown"),
                schema_version=str(dataset_version.get("schema_version") or "unknown"),
                local_db_exists=local_device_db_ready,
                local_db_path=str(legacy_db),
                local_seed_db_path=str(seed_db),
                local_user_db_path=str(user_db),
                contract=dataset_contract,
            )
        )
        if not dataset_contract["ok"]:
            issues.append("device_database_contract_invalid")
        for warning in dataset_contract.get("warnings", []):
            policies.append(_policy_entry("device-database-warning", "warning", warning, root=str(dataset_root)))
        if not local_device_db_ready:
            policies.append(
                _policy_entry(
                    "device-database-local",
                    "warning",
                    "Local Sonic device database has not been synced yet",
                    paths=local_device_db_paths,
                )
            )

    pack_payload: dict[str, Any] | None = None
    if flash_pack:
        pack_path = sonic_root / "config" / "flash-packs" / f"{flash_pack}.json"
        if not pack_path.exists():
            policies.append(_policy_entry("flash-pack", "error", f"Flash pack not found: {pack_path}"))
            issues.append("flash_pack_missing")
        else:
            pack_payload = _read_json(pack_path)
            policies.append(
                _policy_entry(
                    "flash-pack",
                    "ok",
                    "Flash pack loaded",
                    flash_pack=flash_pack,
                    path=str(pack_path),
                )
            )
            windows_cfg = pack_payload.get("windows") or {}
            if windows_cfg.get("iso_path"):
                source = sonic_root / str(windows_cfg["iso_path"])
                if source.exists():
                    policies.append(_policy_entry("flash-pack-windows-iso", "ok", "Flash pack Windows ISO present", path=str(source)))
                else:
                    policies.append(_policy_entry("flash-pack-windows-iso", "warning", "Flash pack Windows ISO missing", path=str(source)))
                    issues.append("flash_pack_windows_iso_missing")
            metadata = pack_payload.get("metadata") or {}
            if metadata.get("requires_device_db") and not local_device_db_ready:
                policies.append(
                    _policy_entry(
                        "flash-pack-device-db",
                        "warning",
                        "Flash pack requires local device DB sync before deployment",
                        paths=local_device_db_paths,
                    )
                )
                issues.append("flash_pack_device_db_required")

    if manifest_path:
        manifest_result = verify_manifest_path(manifest_path)
        repo_root = Path(str(manifest_result.get("paths", {}).get("repo_root") or sonic_root))
        manifest_checks = []
        for name, rel_path in {
            "alpine": payloads_root / "udos" / "udos.squashfs",
            "ubuntu": payloads_root / "wizard",
            "windows": payloads_root / "windows",
        }.items():
            exists = rel_path.exists()
            manifest_checks.append({"source": name, "path": str(rel_path), "present": exists})
        policies.append(
            _policy_entry(
                "manifest-media-map",
                "ok" if manifest_result.get("ok") else "warning",
                "Manifest media map evaluated",
                repo_root=str(repo_root),
                checks=manifest_checks,
            )
        )

    ok = not any(item["level"] == "error" for item in policies)
    return {"ok": ok, "policies": policies, "issues": sorted(set(issues))}


def verify_release_bundle(build_dir: Path, *, pubkey: str | None = None) -> dict[str, Any]:
    manifest_path = build_dir / "build-manifest.json"
    checksums_path = build_dir / "checksums.txt"
    manifest_sig_path = build_dir / "build-manifest.json.sig"
    checksums_sig_path = build_dir / "checksums.txt.sig"

    if not manifest_path.exists():
        return {
            "build_id": build_dir.name,
            "release_ready": False,
            "checksums": {"path": str(checksums_path), "present": False, "verified": False, "entries_checked": 0},
            "signing": {"ready": False},
            "artifacts": [],
            "issues": [f"Build manifest not found: {manifest_path}"],
        }

    manifest = _read_json(manifest_path)
    issues: list[str] = []
    artifacts_status: list[dict[str, Any]] = []
    for entry in manifest.get("artifacts") or []:
        rel_path = entry.get("path")
        if not rel_path:
            continue
        artifact_path = build_dir / rel_path
        exists = artifact_path.exists()
        expected_sha = entry.get("sha256")
        actual_sha = _sha256(artifact_path) if exists else None
        sha_match = bool(exists and expected_sha and actual_sha == expected_sha)
        if not exists:
            issues.append(f"artifact missing: {rel_path}")
        elif expected_sha and not sha_match:
            issues.append(f"artifact checksum mismatch: {rel_path}")
        artifacts_status.append(
            {
                "path": rel_path,
                "exists": exists,
                "expected_sha256": expected_sha,
                "actual_sha256": actual_sha,
                "checksum_match": sha_match,
            }
        )

    checksum_file_verified = False
    checksum_entries_checked = 0
    if not checksums_path.exists():
        issues.append("checksums.txt missing")
    else:
        checksum_rows = [line.strip() for line in checksums_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        checksum_file_verified = True
        for line in checksum_rows:
            try:
                expected, name = line.split(None, 1)
                name = name.strip().lstrip("* ").strip()
            except ValueError:
                checksum_file_verified = False
                issues.append(f"invalid checksum row: {line}")
                continue
            checksum_entries_checked += 1
            target = build_dir / name
            if not target.exists():
                checksum_file_verified = False
                issues.append(f"checksum target missing: {name}")
                continue
            if _sha256(target) != expected:
                checksum_file_verified = False
                issues.append(f"checksum mismatch: {name}")

    signing = {
        "manifest": verify_detached_signature(manifest_path, manifest_sig_path, pubkey=pubkey),
        "checksums": verify_detached_signature(checksums_path, checksums_sig_path, pubkey=pubkey),
    }
    signing["manifest_signature_present"] = signing["manifest"]["present"]
    signing["checksums_signature_present"] = signing["checksums"]["present"]
    signing["manifest_signature_verified"] = signing["manifest"]["verified"]
    signing["checksums_signature_verified"] = signing["checksums"]["verified"]
    signing["ready"] = signing["manifest_signature_verified"] and signing["checksums_signature_verified"]
    if not signing["ready"]:
        issues.append("release signatures incomplete")

    release_ready = checksum_file_verified and signing["ready"] and not issues
    return {
        "build_id": manifest.get("build_id") or build_dir.name,
        "release_ready": release_ready,
        "checksums": {
            "path": str(checksums_path),
            "present": checksums_path.exists(),
            "verified": checksum_file_verified,
            "entries_checked": checksum_entries_checked,
        },
        "signing": signing,
        "artifacts": artifacts_status,
        "issues": issues,
    }


def verify_sonic_ready(
    sonic_root: Path,
    *,
    manifest_path: Path | None = None,
    build_dir: Path | None = None,
    flash_pack: str | None = None,
    pubkey: str | None = None,
) -> dict[str, Any]:
    media = verify_media_inputs(sonic_root, manifest_path=manifest_path, flash_pack=flash_pack)
    manifest = verify_manifest_path(manifest_path) if manifest_path else None
    release_bundle = verify_release_bundle(build_dir, pubkey=pubkey) if build_dir else None

    issues: list[str] = []
    if manifest and manifest.get("errors"):
        issues.extend(manifest["errors"])
    if manifest and manifest.get("warnings"):
        issues.extend(manifest["warnings"])
    issues.extend(media.get("issues", []))
    if release_bundle:
        issues.extend(release_bundle.get("issues", []))

    ok = bool((manifest is None or manifest.get("ok")) and media.get("ok") and (release_bundle is None or release_bundle.get("release_ready")))
    return {
        "ok": ok,
        "manifest": manifest,
        "media_policy": media,
        "release_bundle": release_bundle,
        "issues": issues,
    }
