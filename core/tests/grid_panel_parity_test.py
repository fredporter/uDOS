import json
from pathlib import Path

from core.commands.grid_handler import GridHandler

FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "grid"


def _grid_body(raw: str):
    lines = raw.splitlines()
    start = lines.index("---") + 1
    end = lines.index("--- end ---")
    body = lines[start:end]
    if body and body[0] == "":
        body = body[1:]
    if body and body[-1] == "":
        body = body[:-1]
    return body


def _normalize_raw(raw: str) -> str:
    return "\n".join(
        line for line in raw.splitlines() if not line.startswith("ts:")
    )


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_mode_fixture(mode: str) -> None:
    expected = _load_json(FIXTURE_ROOT / f"{mode}_expected.json")["lines"]

    fixture_input = FIXTURE_ROOT / f"{mode}_input.json"
    handler = GridHandler()
    result = handler.handle("GRID", [mode.upper(), "--input", str(fixture_input)], None, None)
    assert result.get("status") == "success"

    body = _grid_body(result.get("grid_raw") or "")
    assert len(body) == 30
    assert all(len(line) == 80 for line in body)
    assert body == expected


def test_grid_map_fixture_parity_80x30() -> None:
    _assert_mode_fixture("map")


def test_grid_calendar_fixture_parity_80x30() -> None:
    _assert_mode_fixture("calendar")


def test_grid_schedule_fixture_parity_80x30() -> None:
    _assert_mode_fixture("schedule")


def test_grid_workflow_fixture_parity_80x30() -> None:
    _assert_mode_fixture("workflow")


def test_grid_schedule_panel_parity(tmp_path: Path) -> None:
    payload_a = {
        "scheduleItems": [
            {"start": "13:00", "title": "Refactor", "placeRef": "EARTH:SUR:L305-DB12"},
            {"start": "09:00", "title": "Standup", "placeRef": "EARTH:SUR:L305-DA11"},
        ]
    }
    payload_b = {
        "scheduleItems": [
            {"start": "09:00", "title": "Standup", "placeRef": "EARTH:SUR:L305-DA11"},
            {"start": "13:00", "title": "Refactor", "placeRef": "EARTH:SUR:L305-DB12"},
        ]
    }

    p1 = tmp_path / "sched-a.json"
    p2 = tmp_path / "sched-b.json"
    p1.write_text(json.dumps(payload_a), encoding="utf-8")
    p2.write_text(json.dumps(payload_b), encoding="utf-8")

    handler = GridHandler()
    out_a = handler.handle("GRID", ["SCHEDULE", "--input", str(p1)], None, None)
    out_b = handler.handle("GRID", ["SCHEDULE", "--input", str(p2)], None, None)

    assert out_a.get("status") == "success"
    assert out_b.get("status") == "success"
    assert _normalize_raw(out_a.get("grid_raw") or "") == _normalize_raw(out_b.get("grid_raw") or "")
    assert "Spatial EARTH:SUR:L305-DA11, EARTH:SUR:L305-DB12" in (out_a.get("grid_raw") or "")


def test_grid_workflow_panel_rendering(tmp_path: Path) -> None:
    payload = {
        "tasks": [{"status": "[ ]", "text": "Write spec", "due": "2026-02-17"}],
        "scheduleItems": [{"start": "10:00", "title": "Design review", "placeRef": "EARTH:SUR:L305-DA11"}],
        "workflowSteps": [
            {"id": "wf-1", "title": "Draft", "state": "in_progress"},
            {"id": "wf-2", "title": "Ship", "state": "todo", "dependsOn": ["wf-1"]},
        ],
    }

    input_path = tmp_path / "workflow.json"
    input_path.write_text(json.dumps(payload), encoding="utf-8")

    handler = GridHandler()
    result = handler.handle("GRID", ["WORKFLOW", "--input", str(input_path)], None, None)
    assert result.get("status") == "success"

    raw = result.get("grid_raw") or ""
    body = _grid_body(raw)
    assert len(body) == 30
    assert all(len(line) == 80 for line in body)
    assert "Counts T:1 S:1 W:2" in raw


def test_grid_dashboard_task_schedule_workflow_summary(tmp_path: Path) -> None:
    payload = {
        "tasks": [{"status": "[ ]", "text": "A task"}],
        "scheduleItems": [{"start": "09:30", "title": "Sync"}],
        "workflowSteps": [{"id": "wf-1", "title": "Investigate", "state": "in_progress"}],
    }
    input_path = tmp_path / "dashboard.json"
    input_path.write_text(json.dumps(payload), encoding="utf-8")

    handler = GridHandler()
    result = handler.handle("GRID", ["DASHBOARD", "--input", str(input_path)], None, None)
    assert result.get("status") == "success"

    raw = result.get("grid_raw") or ""
    assert "Panels:" in raw
    assert "Tasks: 1" in raw
    assert "Schedule: 1" in raw
    assert "Workflow: 1" in raw
