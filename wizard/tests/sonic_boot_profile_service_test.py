from __future__ import annotations

import json

from wizard.services.sonic_boot_profile_service import SonicBootProfileService


def _write_boot_selector(tmp_path):
    selector_path = tmp_path / "sonic" / "config" / "boot-selector.json"
    selector_path.parent.mkdir(parents=True, exist_ok=True)
    selector_path.write_text(
        json.dumps(
            {
                "name": "Sonic Boot Selector",
                "targets": [
                    {"id": "udos-alpine", "name": "uDOS Alpine Core"},
                    {"id": "udos-windows-entertainment", "name": "Windows Media"},
                ],
            }
        ),
        encoding="utf-8",
    )


def test_boot_route_status_uses_template_workspace_preference(tmp_path, monkeypatch):
    _write_boot_selector(tmp_path)
    monkeypatch.setattr(
        "wizard.services.sonic_boot_profile_service.get_template_workspace_service",
        lambda repo_root=None: type(
            "_Svc",
            (),
            {
                "read_fields": lambda self, section, component_id: {
                    "preferred_boot_profile": "udos-windows-entertainment"
                }
            },
        )(),
    )

    service = SonicBootProfileService(repo_root=tmp_path)
    status = service.get_route_status()

    assert status["preferred_route_profile_id"] == "udos-windows-entertainment"
    assert status["preferred_route_source"] == "template_workspace"
    assert status["preferred_route"]["id"] == "udos-windows-entertainment"


def test_apply_default_route_uses_workspace_profile(tmp_path, monkeypatch):
    _write_boot_selector(tmp_path)
    monkeypatch.setattr(
        "wizard.services.sonic_boot_profile_service.get_template_workspace_service",
        lambda repo_root=None: type(
            "_Svc",
            (),
            {
                "read_fields": lambda self, section, component_id: {
                    "preferred_boot_profile": "udos-alpine"
                }
            },
        )(),
    )

    service = SonicBootProfileService(repo_root=tmp_path)
    route = service.apply_default_route()

    assert route["profile_id"] == "udos-alpine"
    assert route["source"] == "template_workspace"
    assert route["reason"] == "template workspace default route"


def test_boot_route_status_falls_back_when_workspace_preference_missing(tmp_path, monkeypatch):
    _write_boot_selector(tmp_path)
    monkeypatch.setattr(
        "wizard.services.sonic_boot_profile_service.get_template_workspace_service",
        lambda repo_root=None: type(
            "_Svc",
            (),
            {"read_fields": lambda self, section, component_id: {}},
        )(),
    )

    service = SonicBootProfileService(repo_root=tmp_path)
    status = service.get_route_status()

    assert status["preferred_route_profile_id"] is None
    assert status["preferred_route"] is None
    assert status["preferred_route_source"] == "default"
