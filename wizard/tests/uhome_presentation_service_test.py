from __future__ import annotations

from wizard.services.uhome_presentation_service import UHomePresentationService


def test_uhome_presentation_status_uses_template_workspace_preferences(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(
        "wizard.services.uhome_presentation_service.get_template_workspace_service",
        lambda repo_root=None: type(
            "_Svc",
            (),
            {
                "read_fields": lambda self, section, component_id: {
                    "presentation_mode": "steam-console",
                    "node_role": "tv-node",
                }
            },
        )(),
    )

    service = UHomePresentationService(repo_root=tmp_path)
    status = service.get_status()

    assert status["preferred_presentation"] == "steam-console"
    assert status["preferred_presentation_source"] == "template_workspace"
    assert status["node_role"] == "tv-node"
    assert status["node_role_source"] == "template_workspace"


def test_uhome_presentation_start_uses_workspace_preferences_when_blank(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(
        "wizard.services.uhome_presentation_service.get_template_workspace_service",
        lambda repo_root=None: type(
            "_Svc",
            (),
            {
                "read_fields": lambda self, section, component_id: {
                    "presentation_mode": "steam-console",
                    "node_role": "tv-node",
                }
            },
        )(),
    )

    service = UHomePresentationService(repo_root=tmp_path)
    payload = service.start("")

    assert payload["active_presentation"] == "steam-console"
    assert payload["node_role"] == "tv-node"
    assert payload["thin_gui"]["intent"]["target"] == "uhome-console"
    assert payload["thin_gui"]["intent"]["workspace"] == "uhome"
    assert payload["thin_gui"]["intent"]["profile_id"] == "tv-node"


def test_uhome_presentation_status_falls_back_on_invalid_workspace_values(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(
        "wizard.services.uhome_presentation_service.get_template_workspace_service",
        lambda repo_root=None: type(
            "_Svc",
            (),
            {
                "read_fields": lambda self, section, component_id: {
                    "presentation_mode": "invalid",
                    "node_role": "server-or-tv-node",
                }
            },
        )(),
    )

    service = UHomePresentationService(repo_root=tmp_path)
    status = service.get_status()

    assert status["preferred_presentation"] == "thin-gui"
    assert status["preferred_presentation_source"] == "template_workspace_invalid"
    assert status["node_role"] == "server"
    assert status["node_role_source"] == "template_workspace_invalid"
