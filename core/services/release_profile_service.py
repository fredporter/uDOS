"""Release profile registry and install-state helpers for uDOS v1.5."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from core.services.container_catalog_service import get_container_catalog_service
from core.services.logging_api import get_repo_root
from core.services.template_workspace_service import get_template_workspace_service


@dataclass(frozen=True)
class ReleaseProfile:
    profile_id: str
    label: str
    summary: str
    mandatory: bool = False
    default_enabled: bool = False
    components: list[str] = field(default_factory=list)
    extensions: list[str] = field(default_factory=list)
    package_groups: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)


DEFAULT_PROFILES: tuple[ReleaseProfile, ...] = (
    ReleaseProfile(
        profile_id="core",
        label="Core",
        summary="Mandatory base install: ucode, operator mode, offline workflows, repair and update controls.",
        mandatory=True,
        default_enabled=True,
        components=["ucode", "operator", "offline-assets", "repair", "update"],
        package_groups=["utilities"],
        blockers=[
            "ucode-single-entry",
            "operator-offline-ready",
            "repair-contract",
            "update-contract",
        ],
    ),
    ReleaseProfile(
        profile_id="home",
        label="Home",
        summary="Wizard server, home utilities, paired-device workflows, and curated household services.",
        components=["wizardd", "thin-ui-pairing", "home-services"],
        extensions=["thin-gui", "sonic"],
        package_groups=["home", "utilities"],
        blockers=["wizard-pairing", "home-service-health", "home-package-verification"],
    ),
    ReleaseProfile(
        profile_id="creator",
        label="Creator",
        summary="Groovebox, Songscribe, score workflows, transcription queueing, and sound-library management.",
        components=["music", "transcription", "sound-library"],
        extensions=["groovebox"],
        package_groups=["creator", "utilities"],
        blockers=["transcription-ga", "score-export", "library-health"],
    ),
    ReleaseProfile(
        profile_id="gaming",
        label="Gaming",
        summary="Gameplay progression, educational missions, and curated gaming/runtime packages.",
        components=["gameplay", "missions", "gaming-repos"],
        package_groups=["gaming", "utilities"],
        blockers=["mission-mapping", "gaming-package-verification"],
    ),
    ReleaseProfile(
        profile_id="dev",
        label="Dev",
        summary="Dev Mode only: dev-tool bridge, repo tooling, workflow authoring, and contributor utilities.",
        components=["dev-mode", "dev-tool", "repo-tooling"],
        extensions=["dev-mode"],
        package_groups=["dev", "utilities"],
        blockers=["dev-mode-gate", "dev-tool-dev-only"],
    ),
)


DEFAULT_PACKAGE_GROUPS: dict[str, dict[str, Any]] = {
    "utilities": {
        "label": "Utilities",
        "summary": "Base utilities and offline helper assets.",
        "repos": ["core-local", "offline-assets"],
    },
    "home": {
        "label": "Home",
        "summary": "Household services, server helpers, and companion integrations.",
        "repos": ["home-assistant", "wizard-home"],
    },
    "creator": {
        "label": "Creator",
        "summary": "Music, scoring, media workflows, and open sound libraries.",
        "repos": ["songscribe", "groovebox-library"],
    },
    "gaming": {
        "label": "Gaming",
        "summary": "Gameplay content and gaming-oriented package lanes.",
        "repos": ["gaming-bundle", "retro-runtime"],
    },
    "dev": {
        "label": "Dev",
        "summary": "Contributor utilities and development runtime dependencies.",
        "repos": ["dev-tooling", "repo-tooling"],
    },
}


DEFAULT_EXTENSIONS: dict[str, dict[str, Any]] = {
    "empire": {
        "label": "Empire",
        "path": "extensions/empire",
        "profiles": ["home"],
        "summary": "Operational business/data extension.",
        "category": "business",
        "visibility": "official",
        "runtime_owner": "wizard",
        "api_prefix": "/api/empire",
        "wizard_route": "#empire",
        "callable_from": ["core", "wizard", "extensions", "sonic", "uhome"],
        "library_refs": ["empire"],
    },
    "dev-mode": {
        "label": "Dev Mode",
        "path": "dev",
        "profiles": ["dev"],
        "summary": "Contributor scaffold and Dev Mode gate.",
        "category": "developer",
        "visibility": "public",
        "runtime_owner": "wizard",
        "api_prefix": "/api/dev",
        "wizard_route": "#dev",
        "callable_from": ["core", "wizard", "extensions"],
    },
    "groovebox": {
        "label": "Groovebox",
        "path": "extensions/groovebox",
        "profiles": ["creator"],
        "summary": "Creator-profile music workflow extension.",
        "category": "audio",
        "visibility": "official",
        "runtime_owner": "shared",
        "api_prefix": "/api/groovebox",
        "wizard_route": "#groovebox",
        "callable_from": ["core", "wizard", "extensions"],
        "library_refs": ["groovebox"],
    },
    "thin-gui": {
        "label": "Thin GUI",
        "path": "extensions/thin-gui",
        "profiles": ["home"],
        "summary": "Shared launch-intent GUI contract for direct-display and paired UI flows.",
        "category": "ui",
        "visibility": "official",
        "runtime_owner": "shared",
        "api_prefix": "/api/platform/launch",
        "wizard_route": "#thin-gui",
        "callable_from": ["core", "wizard", "extensions", "sonic", "uhome"],
        "library_refs": ["typo", "micro"],
    },
    "sonic": {
        "label": "Sonic Screwdriver",
        "path": "sonic",
        "profiles": ["home"],
        "summary": "Standalone provisioning and deployment component aligned with shared library and launch contracts.",
        "category": "utilities",
        "visibility": "official",
        "runtime_owner": "shared",
        "api_prefix": "/api/sonic",
        "wizard_route": "#sonic",
        "callable_from": ["core", "wizard", "extensions", "sonic", "uhome"],
        "library_refs": ["alpine", "distribution"],
    },
}


class ReleaseProfileService:
    """Read release profile registry and manage lightweight install state."""

    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = repo_root or get_repo_root()
        self.manifest_path = self.repo_root / "distribution" / "profiles" / "certified-profiles.json"
        self.state_path = self.repo_root / "memory" / "ucode" / "release-profiles.json"
        self.extensions_state_path = self.repo_root / "memory" / "ucode" / "extensions-state.json"

    def list_profiles(self) -> list[dict[str, Any]]:
        state = self._load_state()
        items = []
        for profile in self._profiles():
            enabled = profile.profile_id in state["enabled"]
            installed = profile.profile_id in state["installed"]
            items.append(
                {
                    **asdict(profile),
                    "installed": installed,
                    "enabled": enabled,
                }
            )
        return items

    def resolve_profile_ids(self, profile_ids: list[str] | tuple[str, ...] | set[str]) -> list[str]:
        normalized = {
            str(profile_id).strip().lower()
            for profile_id in profile_ids
            if str(profile_id).strip()
        }
        known = {profile["profile_id"] for profile in self.list_profiles()}
        resolved = [profile_id for profile_id in sorted(normalized) if profile_id in known]
        if "core" not in resolved and "core" in known:
            resolved.insert(0, "core")
        return resolved

    def get_profile(self, profile_id: str) -> dict[str, Any] | None:
        normalized = profile_id.strip().lower()
        for item in self.list_profiles():
            if item["profile_id"] == normalized:
                return item
        return None

    def install_profiles(self, profile_ids: list[str]) -> dict[str, Any]:
        profile_ids = self.resolve_profile_ids(profile_ids)
        state = self._load_state()
        changed: list[str] = []
        for profile_id in profile_ids:
            profile = self.get_profile(profile_id)
            if not profile:
                continue
            if profile["profile_id"] not in state["installed"]:
                state["installed"].append(profile["profile_id"])
                changed.append(profile["profile_id"])
            if profile["profile_id"] not in state["enabled"]:
                state["enabled"].append(profile["profile_id"])
        self._save_state(state)
        return {
            "installed": sorted(state["installed"]),
            "enabled": sorted(state["enabled"]),
            "changed": sorted(changed),
        }

    def install_summary(self, profile_ids: list[str]) -> dict[str, Any]:
        resolved = self.resolve_profile_ids(profile_ids)
        package_groups = sorted(self.package_groups_for_profiles(resolved))
        extensions = sorted(self.extensions_for_profiles(resolved))
        return {
            "profiles": resolved,
            "package_groups": package_groups,
            "extensions": extensions,
            "requires_wizard": "home" in resolved,
            "requires_dev": "dev" in resolved,
            "requires_creator": "creator" in resolved,
            "requires_gaming": "gaming" in resolved,
            "template_workspace": get_template_workspace_service(
                self.repo_root
            ).workspace_contract(),
        }

    def set_enabled(self, profile_id: str, enabled: bool) -> dict[str, Any]:
        state = self._load_state()
        profile = self.get_profile(profile_id)
        if not profile:
            raise ValueError(f"Unknown profile: {profile_id}")
        normalized = profile["profile_id"]
        if enabled:
            if normalized not in state["installed"]:
                state["installed"].append(normalized)
            if normalized not in state["enabled"]:
                state["enabled"].append(normalized)
        else:
            if profile["mandatory"]:
                raise ValueError("Mandatory profile cannot be disabled")
            state["enabled"] = [item for item in state["enabled"] if item != normalized]
        self._save_state(state)
        return self.get_profile(normalized) or {}

    def verify_profile(self, profile_id: str) -> dict[str, Any]:
        profile = self.get_profile(profile_id)
        if not profile:
            raise ValueError(f"Unknown profile: {profile_id}")
        missing_components = [
            component
            for component in profile["components"]
            if not self._component_available(component)
        ]
        missing_extensions = [
            extension
            for extension in profile["extensions"]
            if not self.extension_status(extension)["available"]
        ]
        healthy = not missing_components and not missing_extensions
        return {
            "profile_id": profile["profile_id"],
            "healthy": healthy,
            "missing_components": missing_components,
            "missing_extensions": missing_extensions,
            "blockers": profile["blockers"],
        }

    def list_package_groups(self) -> list[dict[str, Any]]:
        state = self._load_state()
        packages = self._manifest().get("package_groups", DEFAULT_PACKAGE_GROUPS)
        items = []
        for package_id, meta in packages.items():
            related_profiles = [
                profile["profile_id"]
                for profile in self.list_profiles()
                if package_id in profile["package_groups"]
            ]
            items.append(
                {
                    "package_id": package_id,
                    "label": meta.get("label", package_id.title()),
                    "summary": meta.get("summary", ""),
                    "repos": list(meta.get("repos", [])),
                    "active": any(pid in state["enabled"] for pid in related_profiles),
                    "profiles": related_profiles,
                }
            )
        return items

    def package_groups_for_profiles(self, profile_ids: list[str]) -> list[str]:
        resolved = set(self.resolve_profile_ids(profile_ids))
        groups: set[str] = set()
        for profile in self.list_profiles():
            if profile["profile_id"] in resolved:
                groups.update(profile["package_groups"])
        return sorted(groups)

    def extension_status(self, extension_id: str) -> dict[str, Any]:
        extensions = self._manifest().get("extensions", DEFAULT_EXTENSIONS)
        meta = extensions.get(extension_id)
        if not meta:
            raise ValueError(f"Unknown extension: {extension_id}")
        catalog_entry = get_container_catalog_service(self.repo_root).get_entry(extension_id)
        path = self.repo_root / str(meta.get("path", ""))
        installed = path.exists()
        enabled = self._extension_enabled(extension_id, installed)
        configured = installed
        configuration_state = "configured" if installed else "missing"
        healthy = installed and enabled
        degraded = False
        capabilities: dict[str, bool] = {}
        missing_prerequisites: list[str] = []
        wizard_route = f"#{extension_id}"
        if extension_id == "empire":
            secrets_path = path / "config" / "empire_secrets.json"
            configuration_state = "configured" if self._secret_has_key(secrets_path, "empire_api_token") else ("partial" if installed else "missing")
            configured = configuration_state == "configured"
            healthy = installed and enabled and (path / "data" / "empire.db").exists()
            degraded = installed and enabled and (not healthy or not configured)
            capabilities = {
                "gui": installed,
                "imports": (path / "scripts" / "ingest").exists(),
                "templates": (path / "templates").exists(),
                "google": self._secret_has_any(
                    secrets_path,
                    [
                        "google_gmail_credentials_path",
                        "google_gmail_token_path",
                        "google_places_api_key",
                    ],
                ),
                "hubspot": self._secret_has_key(secrets_path, "hubspot_private_app_token"),
                "webhooks": True,
            }
            if not installed:
                missing_prerequisites.append("extension-root")
            if not (path / "__init__.py").exists():
                missing_prerequisites.append("package-init")
            if not (path / "data" / "empire.db").exists():
                missing_prerequisites.append("database")
            if configuration_state != "configured":
                missing_prerequisites.append("api-token")
        return {
            "extension_id": extension_id,
            "label": meta.get("label", extension_id.title()),
            "summary": meta.get("summary", ""),
            "profiles": list(meta.get("profiles", [])),
            "path": str(path),
            "available": installed,
            "installed": installed,
            "enabled": enabled,
            "configured": configured,
            "configuration_state": configuration_state,
            "healthy": healthy,
            "degraded": degraded,
            "wizard_route": meta.get("wizard_route", wizard_route),
            "api_prefix": meta.get("api_prefix"),
            "visibility": meta.get("visibility", "official"),
            "category": meta.get("category", "general"),
            "runtime_owner": meta.get("runtime_owner", "shared"),
            "callable_from": list(meta.get("callable_from", [])),
            "library_refs": list(meta.get("library_refs", [])),
            "lens_vars": catalog_entry.lens_vars if catalog_entry else {},
            "template_workspace": (
                catalog_entry.metadata.get("template_workspace")
                if catalog_entry
                else get_template_workspace_service(self.repo_root).component_contract(
                    extension_id
                )
            ),
            "capabilities": capabilities,
            "missing_prerequisites": missing_prerequisites,
        }

    def list_extensions(self) -> list[dict[str, Any]]:
        extensions = self._manifest().get("extensions", DEFAULT_EXTENSIONS)
        return [self.extension_status(extension_id) for extension_id in sorted(extensions)]

    def extensions_for_profiles(self, profile_ids: list[str]) -> list[str]:
        resolved = set(self.resolve_profile_ids(profile_ids))
        extensions = self._manifest().get("extensions", DEFAULT_EXTENSIONS)
        selected: list[str] = []
        for extension_id, meta in sorted(extensions.items()):
            profiles = {str(item).strip().lower() for item in meta.get("profiles", [])}
            if profiles & resolved:
                selected.append(extension_id)
        return selected

    def topology_summary(self) -> dict[str, str]:
        wizard_available = (self.repo_root / "wizard" / "server.py").exists()
        thin_ui_available = (self.repo_root / "extensions" / "thin-gui").exists()
        if wizard_available and thin_ui_available:
            mode = "hybrid"
            summary = "Thin UI available with local/remote Wizard-capable topology."
        elif wizard_available:
            mode = "remote-wizard"
            summary = "Wizard service available; ucode can pair with browser GUI workflows."
        else:
            mode = "standalone"
            summary = "Core-first standalone topology; Wizard pairing unavailable."
        return {"mode": mode, "summary": summary}

    def _component_available(self, component: str) -> bool:
        component_paths = {
            "ucode": self.repo_root / "core" / "tui" / "ucode.py",
            "operator": self.repo_root / "core" / "services" / "operator_mode_service.py",
            "offline-assets": self.repo_root / "distribution",
            "repair": self.repo_root / "core" / "services" / "self_healer.py",
            "update": self.repo_root / "packaging.manifest.json",
            "wizardd": self.repo_root / "wizard" / "server.py",
            "thin-ui-pairing": self.repo_root / "extensions" / "thin-gui",
            "home-services": self.repo_root / "library" / "home-assistant",
            "music": self.repo_root / "core" / "commands" / "music_handler.py",
            "transcription": self.repo_root / "wizard" / "services" / "transcription_service.py",
            "sound-library": self.repo_root / "library",
            "gameplay": self.repo_root / "core" / "commands" / "gameplay_handler.py",
            "missions": self.repo_root / "core" / "services" / "mission_templates.py",
            "gaming-repos": self.repo_root / "distribution" / "windows10-entertainment",
            "dev-mode": self.repo_root / "dev",
            "dev-tool": self.repo_root / "vibe",
            "vibe": self.repo_root / "vibe",
            "repo-tooling": self.repo_root / "bin",
        }
        target = component_paths.get(component)
        return target.exists() if target else False

    def _profiles(self) -> list[ReleaseProfile]:
        manifest_profiles = self._manifest().get("profiles")
        if not isinstance(manifest_profiles, list) or not manifest_profiles:
            return list(DEFAULT_PROFILES)
        items: list[ReleaseProfile] = []
        for item in manifest_profiles:
            if not isinstance(item, dict):
                continue
            items.append(
                ReleaseProfile(
                    profile_id=str(item.get("profile_id", "")).strip().lower(),
                    label=str(item.get("label", "")).strip() or str(item.get("profile_id", "")).title(),
                    summary=str(item.get("summary", "")).strip(),
                    mandatory=bool(item.get("mandatory", False)),
                    default_enabled=bool(item.get("default_enabled", False)),
                    components=[str(v) for v in item.get("components", [])],
                    extensions=[str(v) for v in item.get("extensions", [])],
                    package_groups=[str(v) for v in item.get("package_groups", [])],
                    blockers=[str(v) for v in item.get("blockers", [])],
                )
            )
        return items or list(DEFAULT_PROFILES)

    def _manifest(self) -> dict[str, Any]:
        if not self.manifest_path.exists():
            return {}
        try:
            payload = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
        return payload if isinstance(payload, dict) else {}

    def _load_state(self) -> dict[str, list[str]]:
        default = {
            "installed": [profile.profile_id for profile in DEFAULT_PROFILES if profile.default_enabled],
            "enabled": [profile.profile_id for profile in DEFAULT_PROFILES if profile.default_enabled],
        }
        if not self.state_path.exists():
            self._save_state(default)
            return default
        try:
            payload = json.loads(self.state_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            self._save_state(default)
            return default
        installed = sorted({str(item).strip().lower() for item in payload.get("installed", []) if str(item).strip()})
        enabled = sorted({str(item).strip().lower() for item in payload.get("enabled", []) if str(item).strip()})
        state = {"installed": installed or default["installed"], "enabled": enabled or default["enabled"]}
        for profile in DEFAULT_PROFILES:
            if profile.mandatory and profile.profile_id not in state["installed"]:
                state["installed"].append(profile.profile_id)
            if profile.mandatory and profile.profile_id not in state["enabled"]:
                state["enabled"].append(profile.profile_id)
        state["installed"] = sorted(set(state["installed"]))
        state["enabled"] = sorted(set(state["enabled"]))
        return state

    def _save_state(self, state: dict[str, list[str]]) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(
            json.dumps(state, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def _extension_enabled(self, extension_id: str, installed: bool) -> bool:
        if not installed:
            return False
        if not self.extensions_state_path.exists():
            return True
        try:
            payload = json.loads(self.extensions_state_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return True
        extension = payload.get(extension_id, {})
        if not isinstance(extension, dict):
            return True
        return bool(extension.get("enabled", True))

    def _secret_has_key(self, path: Path, key: str) -> bool:
        if not path.exists():
            return False
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return False
        return bool(payload.get(key)) if isinstance(payload, dict) else False

    def _secret_has_any(self, path: Path, keys: list[str]) -> bool:
        return any(self._secret_has_key(path, key) for key in keys)


_service_instance: ReleaseProfileService | None = None


def get_release_profile_service() -> ReleaseProfileService:
    global _service_instance
    if _service_instance is None:
        _service_instance = ReleaseProfileService()
    return _service_instance
