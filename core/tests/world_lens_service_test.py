import json

from core.services.world_lens_service import WorldLensService


def _mk(tmp_path):
    config = tmp_path / "v1_3_22_world_lens_mvp.json"
    state = tmp_path / "world_lens_state.json"
    seed = tmp_path / "locations-seed.default.json"
    config.write_text(
        json.dumps(
            {
                "version": "1.3.22",
                "feature_flag": {"env_var": "UDOS_3D_WORLD_LENS_ENABLED", "default_enabled": False},
                "single_region": {
                    "id": "earth_subterra_slice",
                    "entry_place_id": "subterra-relay",
                    "allowed_place_ids": ["andes-pass", "lunar-gateway", "subterra-relay"],
                    "anchor_prefix": "EARTH:",
                },
            }
        ),
        encoding="utf-8",
    )
    seed.write_text(
        json.dumps(
            {
                "locations": [
                    {
                        "placeId": "andes-pass",
                        "placeRef": "EARTH:SUR:L302-EP18",
                        "links": ["subterra-relay"],
                    },
                    {
                        "placeId": "lunar-gateway",
                        "placeRef": "EARTH:UDN:L320-AB12-Z5",
                        "links": ["subterra-relay"],
                    },
                    {
                        "placeId": "subterra-relay",
                        "placeRef": "EARTH:SUB:L340-AA22-Z-3:D4",
                        "links": ["andes-pass", "lunar-gateway"],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    return WorldLensService(config_file=config, state_file=state, seed_file=seed), config, seed


def test_world_lens_status_blocked_by_flag(tmp_path):
    service, _, _ = _mk(tmp_path)
    status = service.status(
        username="alice",
        map_status={
            "ok": True,
            "current_place_id": "subterra-relay",
            "place_ref": "EARTH:SUB:L340-AA22-Z-3:D4",
        },
        progression_ready=True,
    )
    assert status["lens"]["enabled"] is False
    assert status["lens"]["ready"] is False
    assert status["lens"]["blocking_reason"] == "feature_flag_disabled"


def test_world_lens_ready_when_enabled_and_in_region(tmp_path):
    service, _, _ = _mk(tmp_path)
    service.set_enabled(True, actor="test")
    status = service.status(
        username="alice",
        map_status={
            "ok": True,
            "current_place_id": "subterra-relay",
            "place_ref": "EARTH:SUB:L340-AA22-Z-3:D4",
        },
        progression_ready=True,
    )
    assert status["lens"]["enabled"] is True
    assert status["single_region"]["active"] is True
    assert status["slice_contract"]["valid"] is True
    assert status["lens"]["ready"] is True


def test_world_lens_blocked_outside_slice(tmp_path):
    service, _, _ = _mk(tmp_path)
    service.set_enabled(True, actor="test")
    status = service.status(
        username="alice",
        map_status={
            "ok": True,
            "current_place_id": "forest-clearing",
            "place_ref": "EARTH:SUR:L300-AA10",
        },
        progression_ready=True,
    )
    assert status["single_region"]["active"] is False
    assert status["lens"]["ready"] is False
    assert status["lens"]["blocking_reason"] == "outside_single_region"


def test_world_lens_contract_invalid_when_place_missing(tmp_path):
    service, config, _ = _mk(tmp_path)
    spec = json.loads(config.read_text(encoding="utf-8"))
    spec["single_region"]["allowed_place_ids"].append("missing-place")
    config.write_text(json.dumps(spec), encoding="utf-8")
    broken_service = WorldLensService(config_file=config, state_file=tmp_path / "state2.json", seed_file=tmp_path / "locations-seed.default.json")
    broken_service.set_enabled(True, actor="test")
    status = broken_service.status(
        username="alice",
        map_status={
            "ok": True,
            "current_place_id": "subterra-relay",
            "place_ref": "EARTH:SUB:L340-AA22-Z-3:D4",
        },
        progression_ready=True,
    )
    assert status["slice_contract"]["valid"] is False
    assert "missing-place" in status["slice_contract"]["missing_place_ids"]
    assert status["lens"]["blocking_reason"] == "slice_contract_invalid"
