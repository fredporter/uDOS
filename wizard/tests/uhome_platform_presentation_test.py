from fastapi import FastAPI
from fastapi.testclient import TestClient

import wizard.routes.platform_routes as platform_routes


class _BridgeSvc:
    def get_status(self):
        return {"available": True}

    def list_artifacts(self, limit=200):
        return {"available": True, "count": 0, "total_found": 0, "artifacts": []}


class _BuildSvc:
    default_profile = "alpine-core+sonic"

    def start_build(self, **_kwargs):
        return {"success": True}

    def list_builds(self, limit=50):
        return {"count": 0, "total_found": 0, "builds": []}


class _BootSvc:
    def list_profiles(self):
        return {"profiles": [], "count": 0}

    def get_route_status(self):
        return {"active_route": None}


class _DeviceSvc:
    def get_recommendations(self):
        return {"profile": {"tier": "baseline"}, "recommendations": {}, "confidence": 0.5}


class _OpsSvc:
    available = False


class _WindowsSvc:
    def get_status(self):
        return {"enabled": True}


class _LinuxSvc:
    def get_status(self):
        return {"available": True}


class _GamingSvc:
    def list_profiles(self):
        return {"profiles": [], "count": 0}


class _ThemesSvc:
    def get_extension_status(self):
        return {"available": True}


class _LaunchSessionsSvc:
    def list_sessions(self, target=None, limit=50):
        return []


class _MediaSvc:
    def list_launchers(self):
        return {"count": 0, "launchers": [], "status": self.get_status()}

    def get_status(self):
        return {"running": False}

    def stop(self):
        return {"active_launcher": None}


class _UHomeSvc:
    active_presentation = None
    preferred_presentation = "thin-gui"
    node_role = "server"

    def get_status(self):
        return {
            "supported_presentations": ["thin-gui", "steam-console"],
            "supported_node_roles": ["server", "tv-node"],
            "active_presentation": self.active_presentation,
            "running": self.active_presentation is not None,
            "preferred_presentation": self.preferred_presentation,
            "preferred_presentation_source": "template_workspace",
            "node_role": self.node_role,
            "node_role_source": "template_workspace",
        }

    def start(self, presentation):
        if not presentation:
            presentation = self.preferred_presentation
        if presentation not in {"thin-gui", "steam-console"}:
            raise ValueError("Unsupported uHOME presentation")
        self.active_presentation = presentation
        return {
            "active_presentation": presentation,
            "node_role": self.node_role,
            "last_action": "start",
        }

    def stop(self):
        self.active_presentation = None
        return {"active_presentation": None, "node_role": self.node_role, "last_action": "stop"}


def _client(monkeypatch):
    uhome = _UHomeSvc()
    monkeypatch.setattr(platform_routes, "get_sonic_bridge_service", lambda repo_root=None: _BridgeSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_build_service", lambda repo_root=None: _BuildSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_boot_profile_service", lambda repo_root=None: _BootSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_device_profile_service", lambda repo_root=None: _DeviceSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_service", lambda repo_root=None: _OpsSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_windows_launcher_service", lambda repo_root=None: _WindowsSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_media_console_service", lambda repo_root=None: _MediaSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_linux_launcher_service", lambda repo_root=None: _LinuxSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_windows_gaming_profile_service", lambda repo_root=None: _GamingSvc())
    monkeypatch.setattr(platform_routes, "get_theme_extension_service", lambda repo_root=None: _ThemesSvc())
    monkeypatch.setattr(platform_routes, "get_launch_session_service", lambda repo_root=None: _LaunchSessionsSvc())
    monkeypatch.setattr(platform_routes, "get_uhome_presentation_service", lambda repo_root=None: uhome)
    monkeypatch.setattr(
        platform_routes,
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
                    "settings": {"effective_source": "default"},
                },
            },
        )(),
    )

    app = FastAPI()
    app.include_router(platform_routes.create_platform_routes(auth_guard=None))
    return TestClient(app)


def test_uhome_presentation_routes(monkeypatch):
    client = _client(monkeypatch)

    status = client.get("/api/platform/uhome/status")
    assert status.status_code == 200
    payload = status.json()
    assert payload["presentation"]["preferred_presentation"] == "thin-gui"
    assert payload["template_workspace"]["component_id"] == "uhome"

    start = client.post("/api/platform/uhome/presentation/start", json={"presentation": ""})
    assert start.status_code == 200
    assert start.json()["state"]["active_presentation"] == "thin-gui"

    presentation_status = client.get("/api/platform/uhome/presentation/status")
    assert presentation_status.status_code == 200
    assert presentation_status.json()["running"] is True

    invalid = client.post(
        "/api/platform/uhome/presentation/start",
        json={"presentation": "bad"},
    )
    assert invalid.status_code == 400

    stop = client.post("/api/platform/uhome/presentation/stop")
    assert stop.status_code == 200
    assert stop.json()["state"]["active_presentation"] is None
