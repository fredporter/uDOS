"""Sonic schema contract validation across SQL, JSON schema, and Python enums."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from core.services.external_repo_service import resolve_sonic_repo_root

from wizard.services.path_utils import get_repo_root
from wizard.services.sonic_adapters import to_device_payload

_USB_BOOT_VALUES = ["legacy_only", "mixed", "native", "none", "uefi_only"]
_REFLASH_VALUES = ["high", "low", "medium", "unknown"]


def _sample_value_for_property(name: str, schema: dict[str, Any]) -> Any:
    enum = schema.get("enum")
    if isinstance(enum, list) and enum:
        return enum[0]
    if schema.get("type") == "integer":
        return 0
    if schema.get("type") == "array":
        return []
    if schema.get("format") == "date":
        return "2026-01-25"
    if name == "id":
        return "sample-device"
    if name == "vendor":
        return "sample-vendor"
    if name == "model":
        return "sample-model"
    return ""

_CREATE_TABLE_PATTERN = re.compile(
    r"CREATE\s+TABLE\s+devices\s*\((?P<body>.*?)\)\s*;",
    flags=re.IGNORECASE | re.DOTALL,
)
_COLUMN_PATTERN = re.compile(
    r"^\s*(?P<name>[a-zA-Z_][a-zA-Z0-9_]*)\s+(?P<type>[A-Z]+)\b(?P<rest>.*)$"
)


def _parse_sql_devices_contract(sql_text: str) -> dict[str, Any]:
    match = _CREATE_TABLE_PATTERN.search(sql_text)
    if not match:
        return {"columns": [], "required": [], "error": "devices table not found"}

    body = match.group("body")
    columns: list[str] = []
    required: list[str] = []

    for raw in body.splitlines():
        line = raw.strip().rstrip(",")
        if not line:
            continue
        if line.startswith("--"):
            continue
        if line.upper().startswith(("PRIMARY KEY", "CONSTRAINT", "UNIQUE", "CHECK", "FOREIGN KEY")):
            continue
        if (column := _COLUMN_PATTERN.match(line)) is None:
            continue
        name = column.group("name")
        rest = column.group("rest").upper()
        columns.append(name)
        if "NOT NULL" in rest or "PRIMARY KEY" in rest:
            required.append(name)

    return {
        "columns": sorted(columns),
        "required": sorted(required),
        "error": None,
    }


def _load_json_schema(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    properties = payload.get("properties", {})
    required = payload.get("required", [])
    return {
        "properties": sorted(str(name) for name in properties.keys()),
        "required": sorted(str(name) for name in required),
        "enum_usb_boot": sorted(str(v) for v in properties.get("usb_boot", {}).get("enum", [])),
        "enum_reflash_potential": sorted(
            str(v) for v in properties.get("reflash_potential", {}).get("enum", [])
        ),
        "properties_map": dict(properties),
    }


def evaluate_sonic_schema_contract(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or get_repo_root()
    datasets = resolve_sonic_repo_root(root) / "datasets"
    sql_path = datasets / "sonic-devices.sql"
    json_path = datasets / "sonic-devices.schema.json"

    issues: list[str] = []

    if not sql_path.exists():
        return {"ok": False, "issues": ["missing_sql_schema"], "paths": {"sql": str(sql_path), "json": str(json_path)}}
    if not json_path.exists():
        return {"ok": False, "issues": ["missing_json_schema"], "paths": {"sql": str(sql_path), "json": str(json_path)}}

    sql_contract = _parse_sql_devices_contract(sql_path.read_text(encoding="utf-8"))
    json_contract = _load_json_schema(json_path)

    sql_columns = set(sql_contract["columns"])
    json_properties = set(json_contract["properties"])
    sql_required = set(sql_contract["required"])
    json_required = set(json_contract["required"])

    sql_only = sorted(sql_columns - json_properties)
    json_only = sorted(json_properties - sql_columns)
    required_mismatch = sorted(sql_required ^ json_required)

    if sql_contract["error"]:
        issues.append("devices_table_parse_error")
    if sql_only:
        issues.append("sql_columns_missing_from_json_schema")
    if json_only:
        issues.append("json_schema_properties_missing_from_sql")
    if required_mismatch:
        issues.append("required_field_mismatch_between_sql_and_json_schema")

    usb_schema = json_contract["enum_usb_boot"]
    reflash_schema = json_contract["enum_reflash_potential"]
    usb_py = sorted(_USB_BOOT_VALUES)
    reflash_py = sorted(_REFLASH_VALUES)

    if usb_schema != usb_py:
        issues.append("usb_boot_enum_mismatch_between_json_schema_and_python")
    if reflash_schema != reflash_py:
        issues.append("reflash_potential_enum_mismatch_between_json_schema_and_python")

    adapter_sample = to_device_payload(
        {name: _sample_value_for_property(name, dict(schema or {})) for name, schema in json_contract.get("properties_map", {}).items()}
    )
    adapter_keys = set(adapter_sample.keys())
    missing_sql_columns_in_adapter = sorted(sql_columns - adapter_keys)
    if missing_sql_columns_in_adapter:
        issues.append("adapter_payload_missing_sql_columns")

    adapter_legacy_usb = to_device_payload({"id": "x", "vendor": "v", "model": "m", "usb_boot": "yes"})
    adapter_usb_normalized = adapter_legacy_usb.get("usb_boot") == "native"
    if not adapter_usb_normalized:
        issues.append("adapter_usb_boot_legacy_normalization_failed")

    return {
        "ok": not issues,
        "issues": issues,
        "paths": {"sql": str(sql_path), "json": str(json_path)},
        "sql": {"columns": sql_contract["columns"], "required": sql_contract["required"]},
        "json_schema": {
            "properties": json_contract["properties"],
            "required": json_contract["required"],
            "enum_usb_boot": usb_schema,
            "enum_reflash_potential": reflash_schema,
        },
        "python_schema": {
            "enum_usb_boot": usb_py,
            "enum_reflash_potential": reflash_py,
        },
        "diff": {
            "sql_only_columns": sql_only,
            "json_only_properties": json_only,
            "required_mismatch_fields": required_mismatch,
        },
        "adapter": {
            "sample_keys": sorted(adapter_keys),
            "missing_sql_columns": missing_sql_columns_in_adapter,
            "usb_boot_normalization": {
                "legacy_yes_maps_to": adapter_legacy_usb.get("usb_boot"),
                "yes_to_native": adapter_usb_normalized,
            },
        },
    }
