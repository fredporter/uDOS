from __future__ import annotations

import json

from wizard.services.sonic_schema_contract import evaluate_sonic_schema_contract


def _write_contract_files(tmp_path, *, sql_required_year: bool) -> None:
    datasets = tmp_path.parent / "uDOS-sonic" / "datasets"
    datasets.mkdir(parents=True, exist_ok=True)
    sql = f"""
CREATE TABLE devices (
  id TEXT PRIMARY KEY,
  vendor TEXT NOT NULL,
  model TEXT NOT NULL,
  year INTEGER{" NOT NULL" if sql_required_year else ""},
  usb_boot TEXT NOT NULL,
  reflash_potential TEXT NOT NULL
);
"""
    schema = {
        "type": "object",
        "required": ["id", "vendor", "model", "year", "usb_boot", "reflash_potential"],
        "properties": {
            "id": {"type": "string"},
            "vendor": {"type": "string"},
            "model": {"type": "string"},
            "year": {"type": "integer"},
            "usb_boot": {
                "type": "string",
                "enum": ["native", "uefi_only", "legacy_only", "mixed", "none"],
            },
            "reflash_potential": {
                "type": "string",
                "enum": ["high", "medium", "low", "unknown"],
            },
        },
    }
    (datasets / "sonic-devices.sql").write_text(sql, encoding="utf-8")
    (datasets / "sonic-devices.schema.json").write_text(
        json.dumps(schema),
        encoding="utf-8",
    )


def test_sonic_schema_contract_detects_required_mismatch(tmp_path) -> None:
    _write_contract_files(tmp_path, sql_required_year=False)
    result = evaluate_sonic_schema_contract(repo_root=tmp_path)

    assert result["ok"] is False
    assert "required_field_mismatch_between_sql_and_json_schema" in result["issues"]
    assert "year" in result["diff"]["required_mismatch_fields"]


def test_sonic_schema_contract_passes_when_sql_json_and_enums_align(tmp_path) -> None:
    _write_contract_files(tmp_path, sql_required_year=True)
    result = evaluate_sonic_schema_contract(repo_root=tmp_path)

    assert result["ok"] is True
    assert result["issues"] == []
    assert result["adapter"]["missing_sql_columns"] == []
    assert result["adapter"]["usb_boot_normalization"]["yes_to_native"] is True


def test_repo_sonic_schema_contract_is_in_sync() -> None:
    result = evaluate_sonic_schema_contract()
    assert result["ok"] is True, result
    assert result["adapter"]["missing_sql_columns"] == []
