from wizard.extensions.assistant import vibe_cli_service


class _DevAccess:
    def __init__(self, error=None):
        self._error = error

    def ensure_vibe_tool_access(self):
        return self._error


def test_vibe_cli_service_blocks_when_dev_mode_lane_is_unavailable(monkeypatch):
    monkeypatch.setattr(vibe_cli_service, "get_dev_extension_service", lambda: _DevAccess("Dev Mode inactive"))
    monkeypatch.setattr(vibe_cli_service, "get_wizard_key", lambda _key: "secret")
    monkeypatch.setattr(vibe_cli_service.shutil, "which", lambda _name: "/usr/local/bin/vibe")

    service = vibe_cli_service.VibeCliService()

    assert service.is_available is False
    assert service.status["dev_mode_error"] == "Dev Mode inactive"


def test_vibe_cli_service_reports_ready_when_dev_mode_tool_is_available(monkeypatch):
    monkeypatch.setattr(vibe_cli_service, "get_dev_extension_service", lambda: _DevAccess(None))
    monkeypatch.setattr(vibe_cli_service, "get_wizard_key", lambda _key: "secret")
    monkeypatch.setattr(vibe_cli_service.shutil, "which", lambda _name: "/usr/local/bin/vibe")

    service = vibe_cli_service.VibeCliService()

    assert service.is_available is True
    assert service.status["installed"] is True
    assert service.status["api_key_configured"] is True
