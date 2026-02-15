from core.services.chunking_contract import describe_chunk_shape, derive_chunk2d_id, parse_place_ref


def test_parse_place_ref_with_optional_depth_suffix():
    parsed = parse_place_ref("EARTH:SUB:L340-AA22-Z-3:D4")
    assert parsed is not None
    assert parsed["anchor"] == "EARTH"
    assert parsed["space"] == "SUB"
    assert parsed["layer"] == 340
    assert parsed["cell"] == "AA22"
    assert parsed["z"] == -3


def test_derive_chunk2d_id():
    assert derive_chunk2d_id("EARTH:SUR:L300-BJ10") == "earth-sur-300-bj"


def test_describe_chunk_shape_reserves_3d_fields():
    shape = describe_chunk_shape("EARTH:UDN:L306-AA10-Z2")
    assert shape is not None
    assert shape["chunk2d_id"] == "earth-udn-306-aa"
    assert shape["coord2d"] == {"layer": 306, "col": "AA"}
    assert shape["reserved3d"]["shape"] == "extruded-column"
