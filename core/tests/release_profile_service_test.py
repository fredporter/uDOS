from __future__ import annotations

import json
from pathlib import Path

from core.services.release_profile_service import ReleaseProfileService


def _write_manifest(repo_root: Path) -> None:
    manifest_dir = repo_root / "distribution" / "profiles"
    manifest_dir.mkdir(parents=True)
    payload = {
        "profiles": [
            {
                "profile_id": "core",
                "label": "Core",
                "summary": "Base runtime",
                "mandatory": True,
                "default_enabled": True,
                "components": ["ucode"],
                "package_groups": ["utilities"],
                "extensions": [],
                "blockers": ["ucode-single-entry"],
            },
            {
                "profile_id": "home",
                "label": "Home",
                "summary": "Wizard runtime",
                "components": ["wizardd"],
                "package_groups": ["home", "utilities"],
                "extensions": [],
                "blockers": ["wizard-pairing"],
            },
            {
                "profile_id": "dev",
                "label": "Dev",
                "summary": "Contributor tooling",
                "components": ["dev-tool"],
                "package_groups": ["dev", "utilities"],
                "extensions": ["dev-mode"],
                "blockers": ["dev-mode-gate"],
            },
        ],
        "extensions": {
            "dev-mode": {
                "label": "Dev Mode",
                "path": "dev",
                "profiles": ["dev"],
                "summary": "Contributor extension",
            }
        },
    }
    (manifest_dir / "certified-profiles.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )


def test_install_summary_resolves_mandatory_core_and_profile_outputs(tmp_path: Path):
    _write_manifest(tmp_path)
    service = ReleaseProfileService(tmp_path)

    summary = service.install_summary(["dev"])

    assert summary["profiles"] == ["core", "dev"]
    assert summary["package_groups"] == ["dev", "utilities"]
    assert summary["extensions"] == ["dev-mode"]
    assert summary["requires_dev"] is True
    assert summary["requires_wizard"] is False
    assert summary["template_workspace"]["editor_library_ref"] == "typo"


def test_install_profiles_persists_enabled_state(tmp_path: Path):
    _write_manifest(tmp_path)
    service = ReleaseProfileService(tmp_path)

    result = service.install_profiles(["home", "dev"])

    assert result["enabled"] == ["core", "dev", "home"]
    assert result["installed"] == ["core", "dev", "home"]
    state = json.loads((tmp_path / "memory" / "ucode" / "release-profiles.json").read_text(encoding="utf-8"))
    assert state == {
        "enabled": ["core", "dev", "home"],
        "installed": ["core", "dev", "home"],
    }


def test_set_enabled_can_disable_and_reenable_optional_profile(tmp_path: Path):
    _write_manifest(tmp_path)
    service = ReleaseProfileService(tmp_path)
    service.install_profiles(["home", "dev"])

    disabled = service.set_enabled("dev", False)
    assert disabled["profile_id"] == "dev"
    assert disabled["enabled"] is False
    state = json.loads((tmp_path / "memory" / "ucode" / "release-profiles.json").read_text(encoding="utf-8"))
    assert state["installed"] == ["core", "dev", "home"]
    assert state["enabled"] == ["core", "home"]

    enabled = service.set_enabled("dev", True)
    assert enabled["profile_id"] == "dev"
    assert enabled["enabled"] is True
    state = json.loads((tmp_path / "memory" / "ucode" / "release-profiles.json").read_text(encoding="utf-8"))
    assert state["installed"] == ["core", "dev", "home"]
    assert sorted(state["enabled"]) == ["core", "dev", "home"]


def test_set_enabled_rejects_disabling_mandatory_profile(tmp_path: Path):
    _write_manifest(tmp_path)
    service = ReleaseProfileService(tmp_path)

    try:
        service.set_enabled("core", False)
    except ValueError as exc:
        assert str(exc) == "Mandatory profile cannot be disabled"
    else:
        raise AssertionError("Expected mandatory profile disable to fail")


def test_empire_extension_status_exposes_official_contract_fields(tmp_path: Path):
    manifest_dir = tmp_path / "distribution" / "profiles"
    manifest_dir.mkdir(parents=True)
    payload = {
        "profiles": [
            {
                "profile_id": "core",
                "label": "Core",
                "summary": "Base runtime",
                "mandatory": True,
                "default_enabled": True,
                "components": ["ucode"],
                "package_groups": ["utilities"],
                "extensions": [],
                "blockers": [],
            }
        ],
        "extensions": {
            "empire": {
                "label": "Empire",
                "path": "extensions/empire",
                "profiles": ["home"],
                "summary": "Official business/data extension",
            }
        },
    }
    (manifest_dir / "certified-profiles.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )
    root = tmp_path / "extensions" / "empire"
    (root / "services").mkdir(parents=True)
    (root / "api").mkdir(parents=True)
    (root / "src").mkdir(parents=True)
    (root / "data").mkdir(parents=True)
    (root / "config").mkdir(parents=True)
    (root / "__init__.py").write_text("", encoding="utf-8")
    (root / "services" / "__init__.py").write_text("", encoding="utf-8")
    (root / "api" / "__init__.py").write_text("", encoding="utf-8")
    (root / "src" / "spine.py").write_text("", encoding="utf-8")
    (root / "data" / "empire.db").write_text("", encoding="utf-8")

    service = ReleaseProfileService(tmp_path)
    status = service.extension_status("empire")

    assert status["installed"] is True
    assert status["enabled"] is True
    assert status["configuration_state"] == "partial"
    assert status["degraded"] is True
    assert status["wizard_route"] == "#empire"
    assert "api-token" in status["missing_prerequisites"]
    assert status["template_workspace"]["workspace_ref"] == "@memory/bank/typo-workspace"
