"""
Tests for Home Assistant bridge routes and uHOME command handlers.

Coverage:
- GET /api/ha/status   — always returns without auth; reflects enabled/disabled state
- GET /api/ha/discover — requires bridge enabled; returns entity list
- POST /api/ha/command — requires bridge enabled; validates allowlist
- uHOME command dispatch: tuner, DVR, ad-processing, playback
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from wizard.routes import home_assistant_routes as routes
from wizard.services import home_assistant_service as svc_module


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _app() -> tuple[object, TestClient]:
    app = FastAPI()
    router = routes.create_ha_routes()
    app.include_router(router)
    return app, TestClient(app)


def _monkeypatch_enabled(monkeypatch, enabled: bool) -> None:
    monkeypatch.setattr(
        svc_module.HomeAssistantService,
        "is_enabled",
        lambda self: enabled,
    )


def _mock_urlopen_hdhomerun(ip: str = "192.168.1.50") -> MagicMock:
    """Return a mock context-manager that yields HDHomeRun JSON."""
    data = json.dumps(
        {
            "DeviceID": "AABBCCDD",
            "FriendlyName": "HDHomeRun FLEX 4K",
            "ModelNumber": "HDFX-4K",
            "TunerCount": 4,
            "FirmwareVersion": "20230101",
            "BaseURL": f"http://{ip}",
        }
    ).encode()
    cm = MagicMock()
    cm.__enter__ = lambda s: s
    cm.__exit__ = MagicMock(return_value=False)
    cm.read.return_value = data
    opener = MagicMock(return_value=cm)
    return opener


# ---------------------------------------------------------------------------
# GET /api/ha/status
# ---------------------------------------------------------------------------


def test_status_when_disabled(monkeypatch):
    _monkeypatch_enabled(monkeypatch, False)
    monkeypatch.setattr(
        routes,
        "get_template_workspace_service",
        lambda repo_root=None: type(
            "_Svc",
            (),
            {
                "component_contract": lambda self, component_id: {
                    "component_id": component_id,
                    "workspace_ref": "@memory/bank/typo-workspace",
                },
                "component_snapshot": lambda self, component_id: {
                    "component_id": component_id,
                    "instructions": {"effective_source": "default"},
                },
            },
        )(),
    )
    _, client = _app()
    res = client.get("/api/ha/status")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "disabled"
    assert body["enabled"] is False
    assert body["bridge"] == "udos-ha"
    assert "version" in body
    assert body["template_workspace"]["component_id"] == "uhome"
    assert body["template_workspace_state"]["component_id"] == "uhome"


def test_status_when_enabled(monkeypatch):
    _monkeypatch_enabled(monkeypatch, True)
    _, client = _app()
    res = client.get("/api/ha/status")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["enabled"] is True


def test_status_includes_allowlist_size(monkeypatch):
    _monkeypatch_enabled(monkeypatch, True)
    _, client = _app()
    body = client.get("/api/ha/status").json()
    assert body["command_allowlist_size"] > 0


# ---------------------------------------------------------------------------
# GET /api/ha/discover
# ---------------------------------------------------------------------------


def test_discover_when_disabled_returns_503(monkeypatch):
    _monkeypatch_enabled(monkeypatch, False)
    _, client = _app()
    res = client.get("/api/ha/discover")
    assert res.status_code == 503
    assert "disabled" in res.json()["detail"].lower()


def test_discover_when_enabled_returns_entities(monkeypatch):
    _monkeypatch_enabled(monkeypatch, True)
    monkeypatch.setattr(
        routes,
        "get_template_workspace_service",
        lambda repo_root=None: type(
            "_Svc",
            (),
            {
                "component_contract": lambda self, component_id: {
                    "component_id": component_id,
                    "workspace_ref": "@memory/bank/typo-workspace",
                },
                "component_snapshot": lambda self, component_id: {
                    "component_id": component_id,
                    "instructions": {"effective_source": "default"},
                },
            },
        )(),
    )
    _, client = _app()
    res = client.get("/api/ha/discover")
    assert res.status_code == 200
    body = res.json()
    assert body["bridge"] == "udos-ha"
    assert isinstance(body["entities"], list)
    assert body["entity_count"] == len(body["entities"])
    ids = [e["id"] for e in body["entities"]]
    assert "udos.uhome.tuner" in ids
    assert "udos.uhome.dvr" in ids
    assert "udos.uhome.ad_processing" in ids
    assert "udos.uhome.playback" in ids
    assert "udos.system" in ids
    assert body["template_workspace"]["workspace_ref"] == "@memory/bank/typo-workspace"
    assert body["template_workspace_state"]["component_id"] == "uhome"


def test_discover_entity_has_required_fields(monkeypatch):
    _monkeypatch_enabled(monkeypatch, True)
    _, client = _app()
    entities = client.get("/api/ha/discover").json()["entities"]
    for entity in entities:
        assert "id" in entity
        assert "type" in entity
        assert "name" in entity
        assert "capabilities" in entity


# ---------------------------------------------------------------------------
# POST /api/ha/command — generic guards
# ---------------------------------------------------------------------------


def test_command_when_disabled_returns_503(monkeypatch):
    _monkeypatch_enabled(monkeypatch, False)
    _, client = _app()
    res = client.post("/api/ha/command", json={"command": "system.info"})
    assert res.status_code == 503


def test_command_not_in_allowlist_returns_400(monkeypatch):
    _monkeypatch_enabled(monkeypatch, True)
    _, client = _app()
    res = client.post("/api/ha/command", json={"command": "system.destroy_everything"})
    assert res.status_code == 400
    assert "allowlist" in res.json()["detail"]


def test_command_missing_command_field_returns_422():
    _, client = _app()
    res = client.post("/api/ha/command", json={"params": {}})
    assert res.status_code == 422


# ---------------------------------------------------------------------------
# POST /api/ha/command — system commands
# ---------------------------------------------------------------------------


def test_command_system_info(monkeypatch):
    _monkeypatch_enabled(monkeypatch, True)
    _, client = _app()
    res = client.post("/api/ha/command", json={"command": "system.info"})
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["result"]["command"] == "system.info"
    assert "bridge_version" in body["result"]["result"]


def test_command_system_capabilities(monkeypatch):
    _monkeypatch_enabled(monkeypatch, True)
    _, client = _app()
    res = client.post("/api/ha/command", json={"command": "system.capabilities"})
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    caps = body["result"]["result"]["allowlist"]
    assert "system.info" in caps
    assert "uhome.tuner.discover" in caps
    assert "uhome.dvr.schedule" in caps
    assert "uhome.playback.status" in caps


# ---------------------------------------------------------------------------
# uHOME tuner commands
# ---------------------------------------------------------------------------


class TestUHomeTuner:
    """uhome.tuner.* command dispatch via HA bridge."""

    def test_tuner_discover_returns_correct_shape(self, monkeypatch):
        """discover always returns the right dict shape, even with no devices."""
        _monkeypatch_enabled(monkeypatch, True)
        _, client = _app()
        # All tuner hosts unreachable in test env → devices_found == 0
        with patch("socket.gethostbyname", side_effect=OSError("unreachable")):
            res = client.post(
                "/api/ha/command",
                json={"command": "uhome.tuner.discover", "params": {}},
            )
        assert res.status_code == 200
        body = res.json()
        assert body["success"] is True
        result = body["result"]
        assert result["command"] == "uhome.tuner.discover"
        assert "devices_found" in result
        assert "devices" in result
        assert isinstance(result["devices"], list)

    def test_tuner_discover_finds_device_when_reachable(self, monkeypatch):
        """When HDHomeRun responds, device is included in results."""
        _monkeypatch_enabled(monkeypatch, True)
        _, client = _app()

        mock_opener = _mock_urlopen_hdhomerun("10.0.0.50")

        with patch("socket.gethostbyname", return_value="10.0.0.50"):
            with patch("urllib.request.urlopen", mock_opener):
                res = client.post(
                    "/api/ha/command",
                    json={
                        "command": "uhome.tuner.discover",
                        "params": {"host": "10.0.0.50"},
                    },
                )

        assert res.status_code == 200
        result = res.json()["result"]
        assert result["devices_found"] >= 1
        device = result["devices"][0]
        assert device["host"] == "10.0.0.50"
        assert device["device_id"] == "AABBCCDD"
        assert device["friendly_name"] == "HDHomeRun FLEX 4K"
        assert device["tuner_count"] == 4

    def test_tuner_status_unreachable(self, monkeypatch):
        """status returns reachable=False when tuner host is unreachable."""
        _monkeypatch_enabled(monkeypatch, True)
        _, client = _app()
        with patch("socket.gethostbyname", side_effect=OSError("unreachable")):
            res = client.post(
                "/api/ha/command",
                json={"command": "uhome.tuner.status", "params": {}},
            )
        assert res.status_code == 200
        result = res.json()["result"]
        assert result["command"] == "uhome.tuner.status"
        assert result["reachable"] is False
        assert "issue" in result

    def test_tuner_status_reachable(self, monkeypatch):
        """status returns reachable=True and model info when tuner responds."""
        _monkeypatch_enabled(monkeypatch, True)
        _, client = _app()

        mock_opener = _mock_urlopen_hdhomerun("10.0.0.50")

        with patch("socket.gethostbyname", return_value="10.0.0.50"):
            with patch("urllib.request.urlopen", mock_opener):
                res = client.post(
                    "/api/ha/command",
                    json={
                        "command": "uhome.tuner.status",
                        "params": {"host": "10.0.0.50"},
                    },
                )

        assert res.status_code == 200
        result = res.json()["result"]
        assert result["reachable"] is True
        assert result["device_id"] == "AABBCCDD"
        assert result["model"] == "HDFX-4K"
        assert result["tuner_count"] == 4


# ---------------------------------------------------------------------------
# uHOME DVR commands
# ---------------------------------------------------------------------------


class TestUHomeDVR:
    """uhome.dvr.* command dispatch with mocked file store."""

    @pytest.fixture(autouse=True)
    def _patch_dvr_path(self, tmp_path, monkeypatch):
        """Redirect DVR schedule store to a per-test tmp directory."""
        import wizard.services.uhome_command_handlers as handlers

        schedule_file = tmp_path / "dvr_schedule.json"
        monkeypatch.setattr(handlers, "_dvr_schedule_path", lambda: schedule_file)

    def _cmd(self, client, command, params=None):
        return client.post(
            "/api/ha/command",
            json={"command": command, "params": params or {}},
        )

    def test_list_rules_empty_by_default(self, monkeypatch):
        _monkeypatch_enabled(monkeypatch, True)
        _, client = _app()
        res = self._cmd(client, "uhome.dvr.list_rules")
        assert res.status_code == 200
        result = res.json()["result"]
        assert result["command"] == "uhome.dvr.list_rules"
        assert result["rule_count"] == 0
        assert result["rules"] == []

    def test_schedule_creates_rule(self, monkeypatch):
        _monkeypatch_enabled(monkeypatch, True)
        _, client = _app()
        params = {
            "title": "Jeopardy!",
            "channel": "7.1",
            "start_time": "2026-03-01T19:00:00Z",
            "duration_minutes": 30,
            "repeat": "weekly",
        }
        res = self._cmd(client, "uhome.dvr.schedule", params)
        assert res.status_code == 200
        body = res.json()
        assert body["success"] is True
        result = body["result"]
        assert result["success"] is True
        rule = result["rule"]
        assert rule["title"] == "Jeopardy!"
        assert rule["channel"] == "7.1"
        assert rule["repeat"] == "weekly"
        assert rule["duration_minutes"] == 30
        assert "id" in rule
        assert "created_at" in rule

    def test_schedule_requires_title(self, monkeypatch):
        _monkeypatch_enabled(monkeypatch, True)
        _, client = _app()
        res = self._cmd(client, "uhome.dvr.schedule", {"title": ""})
        assert res.status_code == 200
        result = res.json()["result"]
        assert result["success"] is False
        assert "title" in result["error"]

    def test_list_rules_after_schedule(self, monkeypatch):
        _monkeypatch_enabled(monkeypatch, True)
        _, client = _app()
        self._cmd(client, "uhome.dvr.schedule", {"title": "Show A"})
        self._cmd(client, "uhome.dvr.schedule", {"title": "Show B"})
        res = self._cmd(client, "uhome.dvr.list_rules")
        result = res.json()["result"]
        assert result["rule_count"] == 2
        titles = [r["title"] for r in result["rules"]]
        assert "Show A" in titles
        assert "Show B" in titles

    def test_cancel_removes_rule(self, monkeypatch):
        _monkeypatch_enabled(monkeypatch, True)
        _, client = _app()
        # Schedule a rule, grab its id
        schedule_res = self._cmd(client, "uhome.dvr.schedule", {"title": "Delete Me"})
        rule_id = schedule_res.json()["result"]["rule"]["id"]

        # Cancel it
        res = self._cmd(client, "uhome.dvr.cancel", {"id": rule_id})
        assert res.status_code == 200
        result = res.json()["result"]
        assert result["success"] is True
        assert result["removed"] == 1

        # List should be empty again
        list_res = self._cmd(client, "uhome.dvr.list_rules")
        assert list_res.json()["result"]["rule_count"] == 0

    def test_cancel_unknown_id_returns_not_found(self, monkeypatch):
        _monkeypatch_enabled(monkeypatch, True)
        _, client = _app()
        res = self._cmd(client, "uhome.dvr.cancel", {"id": "nonexistent"})
        result = res.json()["result"]
        assert result["success"] is False
        assert result["removed"] == 0

    def test_cancel_requires_id(self, monkeypatch):
        _monkeypatch_enabled(monkeypatch, True)
        _, client = _app()
        res = self._cmd(client, "uhome.dvr.cancel", {"id": ""})
        result = res.json()["result"]
        assert result["success"] is False
        assert "id" in result["error"]


# ---------------------------------------------------------------------------
# uHOME ad-processing commands
# ---------------------------------------------------------------------------


class TestUHomeAdProcessing:
    """uhome.ad_processing.* command dispatch via mocked WizardConfig."""

    @pytest.fixture(autouse=True)
    def _patch_wizard_config(self, monkeypatch):
        """Replace WizardConfig with an in-memory store."""
        store: dict[str, str] = {}
        workspace_store = {"ad_processing_mode": "disabled"}

        class FakeConfig:
            def get(self, key, default=None):
                return store.get(key, default)

            def set(self, key, value):
                store[key] = value

        class FakeWorkspaceService:
            def read_fields(self, section, component_id):
                assert section == "settings"
                assert component_id == "uhome"
                return dict(workspace_store)

            def write_user_field(self, section, component_id, field_name, value):
                assert section == "settings"
                assert component_id == "uhome"
                assert field_name == "ad-processing-mode"
                workspace_store["ad_processing_mode"] = value
                return {
                    "effective_source": "user",
                    "effective_content": f"- ad-processing-mode: {value}\n",
                }

        import wizard.services.uhome_command_handlers as handlers

        # Patch the import inside the module functions
        monkeypatch.setattr(
            "wizard.services.wizard_config.WizardConfig",
            FakeConfig,
            raising=False,
        )
        monkeypatch.setattr(
            handlers,
            "get_template_workspace_service",
            lambda repo_root=None: FakeWorkspaceService(),
        )
        self._store = store
        self._workspace_store = workspace_store

    def _cmd(self, client, command, params=None):
        return client.post(
            "/api/ha/command",
            json={"command": command, "params": params or {}},
        )

    def test_get_mode_default_is_disabled(self, monkeypatch):
        _monkeypatch_enabled(monkeypatch, True)
        _, client = _app()
        res = self._cmd(client, "uhome.ad_processing.get_mode")
        assert res.status_code == 200
        result = res.json()["result"]
        assert result["command"] == "uhome.ad_processing.get_mode"
        assert result["mode"] == "disabled"
        assert result["source"] == "template_workspace"
        assert "valid_modes" in result

    def test_get_mode_valid_modes_list(self, monkeypatch):
        _monkeypatch_enabled(monkeypatch, True)
        _, client = _app()
        result = self._cmd(client, "uhome.ad_processing.get_mode").json()["result"]
        modes = result["valid_modes"]
        assert "disabled" in modes
        assert "comskip_auto" in modes
        assert "comskip_manual" in modes
        assert "passthrough" in modes

    def test_set_mode_valid(self, monkeypatch):
        _monkeypatch_enabled(monkeypatch, True)
        _, client = _app()
        res = self._cmd(
            client, "uhome.ad_processing.set_mode", {"mode": "comskip_auto"}
        )
        assert res.status_code == 200
        result = res.json()["result"]
        assert result["success"] is True
        assert result["mode"] == "comskip_auto"
        assert result["source"] == "template_workspace"
        assert self._workspace_store["ad_processing_mode"] == "comskip_auto"

    def test_set_mode_persists(self, monkeypatch):
        _monkeypatch_enabled(monkeypatch, True)
        _, client = _app()
        self._cmd(client, "uhome.ad_processing.set_mode", {"mode": "passthrough"})
        get_res = self._cmd(client, "uhome.ad_processing.get_mode")
        assert get_res.json()["result"]["mode"] == "passthrough"

    def test_get_mode_falls_back_to_wizard_config_when_workspace_invalid(self, monkeypatch):
        self._workspace_store["ad_processing_mode"] = "invalid"
        self._store["uhome_ad_processing_mode"] = "comskip_manual"
        _monkeypatch_enabled(monkeypatch, True)
        _, client = _app()
        get_res = self._cmd(client, "uhome.ad_processing.get_mode")
        result = get_res.json()["result"]
        assert result["mode"] == "comskip_manual"
        assert result["source"] == "wizard_config"

    def test_set_mode_invalid_returns_error(self, monkeypatch):
        _monkeypatch_enabled(monkeypatch, True)
        _, client = _app()
        res = self._cmd(
            client, "uhome.ad_processing.set_mode", {"mode": "delete_all_ads"}
        )
        assert res.status_code == 200
        result = res.json()["result"]
        assert result["success"] is False
        assert "invalid mode" in result["error"]


# ---------------------------------------------------------------------------
# uHOME playback commands
# ---------------------------------------------------------------------------


class TestUHomePlayback:
    """uhome.playback.* command dispatch."""

    @pytest.fixture(autouse=True)
    def _patch_workspace_and_repo(self, monkeypatch, tmp_path):
        import wizard.services.uhome_command_handlers as handlers

        queue_root = tmp_path / "repo"
        workspace_store = {
            "presentation_mode": "thin-gui",
            "preferred_target_client": "living-room",
        }

        class FakeWorkspaceService:
            def read_fields(self, section, component_id):
                assert section == "settings"
                assert component_id == "uhome"
                return dict(workspace_store)

        monkeypatch.setattr(
            handlers,
            "get_template_workspace_service",
            lambda repo_root=None: FakeWorkspaceService(),
        )
        monkeypatch.setattr(
            "core.services.logging_api.get_repo_root",
            lambda: queue_root,
            raising=False,
        )
        self._workspace_store = workspace_store
        self._queue_file = (
            queue_root / "memory" / "bank" / "uhome" / "playback_queue.json"
        )

    def _cmd(self, client, command, params=None):
        return client.post(
            "/api/ha/command",
            json={"command": command, "params": params or {}},
        )

    def test_playback_status_no_jellyfin_configured(self, monkeypatch):
        """When JELLYFIN_URL is empty, status is returned with a helpful note."""
        _monkeypatch_enabled(monkeypatch, True)
        import wizard.services.uhome_command_handlers as handlers

        monkeypatch.setattr(handlers, "_jellyfin_base_url", lambda: "")
        _, client = _app()
        res = self._cmd(client, "uhome.playback.status")
        assert res.status_code == 200
        result = res.json()["result"]
        assert result["command"] == "uhome.playback.status"
        assert result["jellyfin_configured"] is False
        assert result["presentation_mode"] == "thin-gui"
        assert result["presentation_mode_source"] == "template_workspace"
        assert result["preferred_target_client"] == "living-room"
        assert result["preferred_target_client_source"] == "template_workspace"
        assert "note" in result

    def test_playback_status_with_jellyfin_reachable(self, monkeypatch):
        """When Jellyfin is configured and responds, active_sessions is populated."""
        _monkeypatch_enabled(monkeypatch, True)
        import wizard.services.uhome_command_handlers as handlers

        monkeypatch.setattr(
            handlers, "_jellyfin_base_url", lambda: "http://jellyfin.local:8096"
        )

        sessions_json = json.dumps(
            [
                {
                    "UserName": "alice",
                    "Client": "Jellyfin Web",
                    "NowPlayingItem": {
                        "Name": "Inception",
                        "Type": "Movie",
                    },
                }
            ]
        ).encode()
        cm = MagicMock()
        cm.__enter__ = lambda s: s
        cm.__exit__ = MagicMock(return_value=False)
        cm.read.return_value = sessions_json

        _, client = _app()
        with patch("urllib.request.urlopen", return_value=cm):
            res = self._cmd(client, "uhome.playback.status")

        assert res.status_code == 200
        result = res.json()["result"]
        assert result["jellyfin_configured"] is True
        assert result["jellyfin_reachable"] is True
        assert len(result["active_sessions"]) == 1
        session = result["active_sessions"][0]
        assert session["user"] == "alice"
        assert session["title"] == "Inception"
        assert session["media_type"] == "Movie"
        assert result["presentation_mode"] == "thin-gui"
        assert result["preferred_target_client"] == "living-room"

    def test_playback_status_jellyfin_unreachable(self, monkeypatch):
        """When Jellyfin URL is set but server is down, reachable=False."""
        _monkeypatch_enabled(monkeypatch, True)
        import wizard.services.uhome_command_handlers as handlers

        monkeypatch.setattr(
            handlers, "_jellyfin_base_url", lambda: "http://jellyfin.local:8096"
        )

        _, client = _app()
        with patch("urllib.request.urlopen", side_effect=OSError("connection refused")):
            res = self._cmd(client, "uhome.playback.status")

        result = res.json()["result"]
        assert result["jellyfin_configured"] is True
        assert result["jellyfin_reachable"] is False
        assert "issue" in result

    def test_playback_status_falls_back_when_presentation_invalid(self, monkeypatch):
        _monkeypatch_enabled(monkeypatch, True)
        import wizard.services.uhome_command_handlers as handlers

        self._workspace_store["presentation_mode"] = "invalid"
        self._workspace_store["preferred_target_client"] = ""
        monkeypatch.setattr(handlers, "_jellyfin_base_url", lambda: "")

        _, client = _app()
        res = self._cmd(client, "uhome.playback.status")

        result = res.json()["result"]
        assert result["presentation_mode"] == "thin-gui"
        assert result["presentation_mode_source"] == "template_workspace_invalid"
        assert result["preferred_target_client"] == "living-room"
        assert result["preferred_target_client_source"] == "default"

    def test_playback_handoff_queues_item(self, monkeypatch):
        """handoff queues an item and returns success."""
        _monkeypatch_enabled(monkeypatch, True)

        _, client = _app()
        res = self._cmd(
            client,
            "uhome.playback.handoff",
            {"item_id": "abc123", "target_client": "living-room-tv"},
        )

        assert res.status_code == 200
        result = res.json()["result"]
        assert result["success"] is True
        assert result["item_id"] == "abc123"
        assert result["target_client"] == "living-room-tv"
        assert result["source"] == "request"
        queue = json.loads(self._queue_file.read_text(encoding="utf-8"))
        assert queue[0]["target_client"] == "living-room-tv"

    def test_playback_handoff_uses_workspace_default_target(self, monkeypatch):
        _monkeypatch_enabled(monkeypatch, True)
        self._workspace_store["preferred_target_client"] = "theater-node"

        _, client = _app()
        res = self._cmd(client, "uhome.playback.handoff", {"item_id": "abc123"})

        result = res.json()["result"]
        assert result["success"] is True
        assert result["target_client"] == "theater-node"
        assert result["source"] == "template_workspace"
        queue = json.loads(self._queue_file.read_text(encoding="utf-8"))
        assert queue[0]["target_client"] == "theater-node"

    def test_playback_handoff_default_keyword_uses_workspace_target(self, monkeypatch):
        _monkeypatch_enabled(monkeypatch, True)
        self._workspace_store["preferred_target_client"] = "den-tv"

        _, client = _app()
        res = self._cmd(
            client,
            "uhome.playback.handoff",
            {"item_id": "abc123", "target_client": "default"},
        )

        result = res.json()["result"]
        assert result["success"] is True
        assert result["target_client"] == "den-tv"
        assert result["source"] == "template_workspace"

    def test_playback_handoff_requires_item_id(self, monkeypatch):
        """handoff returns error when item_id is missing."""
        _monkeypatch_enabled(monkeypatch, True)

        _, client = _app()
        res = self._cmd(
            client, "uhome.playback.handoff", {"item_id": "", "target_client": "tv"}
        )
        result = res.json()["result"]
        assert result["success"] is False
        assert "item_id" in result["error"]
