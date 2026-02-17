"""
Generate a sample overlays JSON file for UGRID map demos.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Dict, Any


def generate_sample_overlays(path: Path, focus_locid: Optional[str] = None) -> Path:
    focus = focus_locid or "EARTH:SUR:L305-DA11"
    payload = build_sample_overlays(focus)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def build_sample_overlays(focus_locid: str) -> Dict[str, Any]:
    return {
        "focusLocId": focus_locid,
        "overlays": [
            {"locId": "EARTH:SUR:L305-DA11", "icon": "T", "label": "Tasks: 3"},
            {"locId": "EARTH:SUR:L305-DA12", "icon": "N", "label": "Notes: 1"},
            {"locId": "EARTH:SUR:L305-DB11", "icon": "!", "label": "Alert"},
            {"locId": "EARTH:SUR:L305-DB12", "icon": "E", "label": "Event"},
            {"locId": "EARTH:SUR:L305-DC11", "icon": "*", "label": "Marker"},
        ],
    }


def build_sample_calendar() -> Dict[str, Any]:
    return {
        "events": [
            {"time": "09:00", "title": "Standup"},
            {"time": "11:00", "title": "UGRID review"},
            {"time": "14:30", "title": "Wizard sync"},
        ],
        "tasks": [
            {"status": "[ ]", "text": "Ship GRID demos"},
            {"status": "[x]", "text": "Wire overlays"},
            {"status": "[ ]", "text": "Log review"},
        ],
    }


def build_sample_table() -> Dict[str, Any]:
    return {
        "query": "SELECT id, name, status FROM anchors",
        "columns": [
            {"key": "id", "title": "ID", "width": 10},
            {"key": "name", "title": "Name", "width": 30},
            {"key": "status", "title": "Status", "width": 36},
        ],
        "rows": [
            {"id": "EARTH", "name": "Earth", "status": "active"},
            {"id": "GAME:NETHACK", "name": "NetHack", "status": "stub"},
            {"id": "BODY:MOON", "name": "Moon", "status": "active"},
        ],
        "page": 1,
        "perPage": 20,
    }


def build_sample_schedule() -> Dict[str, Any]:
    return {
        "events": [
            {"time": "08:00", "item": "Coffee + notes", "location": "HOME"},
            {"time": "10:00", "item": "Map review", "location": "EARTH:SUR:L305-DA11"},
            {"time": "15:00", "item": "Sonic sync", "location": "WIZARD"},
        ],
        "filters": {"mode": "today", "owner": "local"},
    }


def build_sample_workflow() -> Dict[str, Any]:
    return {
        "tasks": [
            {"id": "task-1", "status": "[ ]", "text": "Finalize command contract", "due": "2026-02-18"},
            {"id": "task-2", "status": "[x]", "text": "Ship stdout lock", "due": "2026-02-17"},
            {"id": "task-3", "status": "[ ]", "text": "Add parity fixtures", "due": "2026-02-19"},
        ],
        "scheduleItems": [
            {"id": "sched-1", "start": "09:30", "item": "TUI parity standup", "locId": "EARTH:SUR:L305-DA11"},
            {"id": "sched-2", "start": "13:00", "item": "Workflow fixture review", "locId": "EARTH:SUR:L305-DA12"},
            {"id": "sched-3", "start": "16:15", "item": "Release note update", "location": "WIZARD"},
        ],
        "workflowSteps": [
            {"id": "wf-io", "title": "I/O contract", "state": "done"},
            {"id": "wf-grid", "title": "GRID workflow docs", "state": "in_progress", "dependsOn": ["wf-io"]},
            {"id": "wf-parity", "title": "Panel parity fixtures", "state": "todo", "dependsOn": ["wf-grid"]},
        ],
    }


def generate_sample_grid_inputs(root: Path) -> Dict[str, Path]:
    root.mkdir(parents=True, exist_ok=True)
    outputs = {
        "map": root / "grid-overlays-sample.json",
        "calendar": root / "grid-calendar-sample.json",
        "table": root / "grid-table-sample.json",
        "schedule": root / "grid-schedule-sample.json",
        "workflow": root / "grid-workflow-sample.json",
    }

    outputs["map"].write_text(
        json.dumps(build_sample_overlays("EARTH:SUR:L305-DA11"), indent=2),
        encoding="utf-8",
    )
    outputs["calendar"].write_text(
        json.dumps(build_sample_calendar(), indent=2),
        encoding="utf-8",
    )
    outputs["table"].write_text(
        json.dumps(build_sample_table(), indent=2),
        encoding="utf-8",
    )
    outputs["schedule"].write_text(
        json.dumps(build_sample_schedule(), indent=2),
        encoding="utf-8",
    )
    outputs["workflow"].write_text(
        json.dumps(build_sample_workflow(), indent=2),
        encoding="utf-8",
    )

    return outputs
