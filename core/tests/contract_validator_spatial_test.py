from core.services.anchor_validation import is_valid_locid
from core.tools.contract_validator import validate_world_contract


def test_anchor_validation_accepts_z_axis_locid():
    assert is_valid_locid("EARTH:SUR:L305-DA11")
    assert is_valid_locid("EARTH:SUR:L305-DA11-Z0")
    assert is_valid_locid("EARTH:SUR:L305-DA11-Z-9")
    assert not is_valid_locid("EARTH:SUR:L305-DA11-Z100")


def test_world_contract_validation_accepts_z_axis_tokens(tmp_path):
    note = tmp_path / "valid.md"
    note.write_text(
        "\n".join(
            [
                "---",
                "places:",
                "  - EARTH:SUR:L305-DA11-Z2",
                "grid_locations:",
                "  - L305-DA11-Z-2",
                "---",
            ]
        ),
        encoding="utf-8",
    )

    report = validate_world_contract(tmp_path)
    assert report.valid, report.errors


def test_world_contract_validation_rejects_bad_z_axis_tokens(tmp_path):
    note = tmp_path / "invalid.md"
    note.write_text("grid_locations: [L305-DA11-Z100]\n", encoding="utf-8")

    report = validate_world_contract(tmp_path)
    assert not report.valid
    assert "L305-DA11-Z100" in (report.details or {}).get("invalid_locids", [])
