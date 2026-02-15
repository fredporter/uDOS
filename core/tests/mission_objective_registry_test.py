import json

from core.services.mission_objective_registry import MissionObjectiveRegistry


def test_registry_snapshot_has_required_summary_fields(tmp_path):
    manifest = tmp_path / "manifest.json"
    status = tmp_path / "status.json"
    manifest.write_text(
        json.dumps(
            {
                "version": "1.3.23",
                "milestone": "v1.3.23",
                "objectives": [
                    {"id": "obj.one", "description": "one", "owner": "core", "severity": "blocker"},
                    {"id": "obj.two", "description": "two", "owner": "ci", "severity": "required"},
                ],
            }
        ),
        encoding="utf-8",
    )
    status.write_text(
        json.dumps(
            {
                "objectives": {
                    "obj.one": {"status": "pass", "updated_at": "2026-02-15T00:00:00Z", "evidence": []},
                    "obj.ghost": {"status": "pass"},
                }
            }
        ),
        encoding="utf-8",
    )
    snapshot = MissionObjectiveRegistry(manifest_file=manifest, status_file=status).snapshot()

    summary = snapshot["summary"]
    assert snapshot["milestone"] == "v1.3.23"
    assert summary["total"] == 2
    assert summary["pass"] == 1
    assert summary["pending"] == 1
    assert summary["contract_drift"] is True
    assert "obj.ghost" in snapshot["contract_drift"]["unknown_objective_ids"]


def test_registry_default_pending_without_status_file(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "version": "1.3.23",
                "milestone": "v1.3.23",
                "objectives": [{"id": "obj.one", "description": "one", "owner": "core", "severity": "required"}],
            }
        ),
        encoding="utf-8",
    )
    snapshot = MissionObjectiveRegistry(manifest_file=manifest, status_file=tmp_path / "missing-status.json").snapshot()
    assert snapshot["summary"]["pending"] == 1
    assert snapshot["objectives"][0]["status"] == "pending"
