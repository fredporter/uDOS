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
                "components": ["vibe"],
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
    assert summary["tinycore_tier"] == "core"


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
