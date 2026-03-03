from __future__ import annotations

from wizard.services.sonic_media_console_service import SonicMediaConsoleService


def test_media_console_status_uses_template_workspace_preference(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "wizard.services.sonic_media_console_service.get_template_workspace_service",
        lambda repo_root=None: type(
            "_Svc",
            (),
            {
                "read_fields": lambda self, section, component_id: {
                    "preferred_launcher": "wantmymtv"
                }
            },
        )(),
    )

    service = SonicMediaConsoleService(repo_root=tmp_path)
    status = service.get_status()

    assert status["preferred_launcher"] == "wantmymtv"
    assert status["preferred_launcher_source"] == "template_workspace"


def test_media_console_start_uses_preferred_launcher_when_blank(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "wizard.services.sonic_media_console_service.get_template_workspace_service",
        lambda repo_root=None: type(
            "_Svc",
            (),
            {
                "read_fields": lambda self, section, component_id: {
                    "preferred_launcher": "wantmymtv"
                }
            },
        )(),
    )

    service = SonicMediaConsoleService(repo_root=tmp_path)
    payload = service.start("")

    assert payload["active_launcher"] == "wantmymtv"
