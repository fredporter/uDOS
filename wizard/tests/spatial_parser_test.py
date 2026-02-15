from wizard.services.spatial_parser import (
    normalise_frontmatter_places,
    parse_locid,
    parse_place_ref,
)


def test_parse_locid_accepts_optional_z_axis():
    assert parse_locid("L305-DA11") == "L305-DA11"
    assert parse_locid("L305-DA11-Z0") == "L305-DA11-Z0"
    assert parse_locid("L305-DA11-Z-5") == "L305-DA11-Z-5"


def test_parse_locid_rejects_invalid_z_axis_or_bounds():
    assert parse_locid("L305-DA11-Z") is None
    assert parse_locid("L305-DA11-Z100") is None
    assert parse_locid("L305-DA09") is None


def test_parse_place_ref_accepts_z_axis_locid():
    parsed = parse_place_ref("EARTH:SUR:L305-DA11-Z3")
    assert parsed is not None
    assert parsed["loc_id"] == "L305-DA11-Z3"


def test_normalise_frontmatter_places_keeps_z_axis_legacy_grid_locations():
    places = normalise_frontmatter_places(
        {
            "places": ["EARTH:SUR:L305-DA11-Z2"],
            "grid_locations": ["L305-DA11-Z2", "L305-DA11"],
        }
    )
    assert "EARTH:SUR:L305-DA11-Z2" in places
    assert "EARTH:SUR:L305-DA11" in places
