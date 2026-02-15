import json
from pathlib import Path

from core.services.gameplay_service import GameplayService
from core.services.map_runtime_service import MapRuntimeService
from core.services.world_adapter_contract import (
    load_world_adapter_contract,
    validate_canonical_event,
)


SEED = {
    "version": "1.3.21",
    "locations": [
        {
            "placeId": "alpha",
            "label": "Alpha",
            "placeRef": "EARTH:SUR:L300-AA10",
            "z": 0,
            "links": ["beta"],
            "portals": [],
            "hazards": [],
            "quest_ids": ["alpha.quest.1"],
            "interaction_points": ["terminal-a"],
            "npc_spawn": [],
            "metadata": {"chunk": "earth-sur-300-aa"},
        },
        {
            "placeId": "beta",
            "label": "Beta",
            "placeRef": "EARTH:SUR:L300-AB10",
            "z": 0,
            "links": ["alpha"],
            "portals": [],
            "hazards": ["rain"],
            "quest_ids": ["beta.quest.1"],
            "interaction_points": ["terminal-b"],
            "npc_spawn": [],
            "metadata": {"chunk": "earth-sur-300-ab"},
        },
    ],
}


def _mk(tmp_path):
    seed_file = tmp_path / "seed.json"
    map_state = tmp_path / "map_runtime_state.json"
    gameplay_state = tmp_path / "gameplay_state.json"
    events_file = tmp_path / "events.ndjson"
    cursor_file = tmp_path / "cursor.json"

    seed_file.write_text(json.dumps(SEED), encoding="utf-8")
    map_service = MapRuntimeService(seed_file=seed_file, state_file=map_state, events_file=events_file)
    gameplay = GameplayService(state_file=gameplay_state, events_file=events_file, cursor_file=cursor_file)
    return map_service, gameplay, events_file


def _read_events(path: Path):
    rows = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def test_world_adapter_contract_file_loads():
    contract = load_world_adapter_contract()
    assert contract["version"] == "1.3.21"
    assert "MAP_TRAVERSE" in contract["events"]["canonical_types"]


def test_tui_lens_events_match_contract(tmp_path):
    map_service, gameplay, events_file = _mk(tmp_path)
    assert map_service.enter("alice", "alpha")["ok"] is True
    assert map_service.move("alice", "beta")["ok"] is True
    assert map_service.inspect("alice")["ok"] is True
    assert map_service.interact("alice", "terminal-b")["ok"] is True
    assert map_service.complete("alice", "beta.quest.1")["ok"] is True
    assert map_service.tick("alice", 1)["ok"] is True

    gameplay.tick("alice")

    contract = load_world_adapter_contract()
    rows = _read_events(events_file)
    checked = 0
    for row in rows:
        if str(row.get("source", "")).startswith("core:map-runtime"):
            ok, errors = validate_canonical_event(row, contract)
            assert ok, f"contract mismatch: {errors}"
            checked += 1
    assert checked >= 6


def test_external_adapter_emits_same_canonical_types(tmp_path):
    _, gameplay, events_file = _mk(tmp_path)

    synthetic = [
        {
            "ts": "2026-02-15T00:00:00Z",
            "source": "adapter:elite-sim",
            "username": "alice",
            "type": "MAP_ENTER",
            "payload": {
                "action": "ENTER",
                "place_id": "alpha",
                "place_ref": "EARTH:SUR:L300-AA10",
                "chunk2d_id": "earth-sur-300-aa",
                "location": {"grid_id": "EARTH:SUR:L300-AA10", "x": None, "y": None, "z": 0},
            },
        },
        {
            "ts": "2026-02-15T00:00:01Z",
            "source": "adapter:elite-sim",
            "username": "alice",
            "type": "MAP_TRAVERSE",
            "payload": {
                "action": "ENTER",
                "from_place_id": "alpha",
                "to_place_id": "beta",
                "to_place_ref": "EARTH:SUR:L300-AB10",
                "terrain_cost": 2,
                "mode": "walk",
                "chunk2d_id": "earth-sur-300-ab",
                "location": {"grid_id": "EARTH:SUR:L300-AB10", "x": None, "y": None, "z": 0},
            },
        },
    ]

    with events_file.open("a", encoding="utf-8") as fh:
        for row in synthetic:
            fh.write(json.dumps(row) + "\n")

    tick = gameplay.tick("alice")
    assert tick["processed"] == 2

    metrics = gameplay.get_user_progress("alice")["metrics"]
    assert metrics["map_enters"] == 1
    assert metrics["map_moves"] == 1
