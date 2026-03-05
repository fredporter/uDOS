from __future__ import annotations

import asyncio
import json
from pathlib import Path

from core.services.release_profile_service import ReleaseProfileService
from wizard.services.extension_handler import ExtensionHandler
from wizard.services.extension_handler import GitHubCLIExtension


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
                "blockers": [],
            },
            {
                "profile_id": "dev",
                "label": "Dev",
                "summary": "Contributor tooling",
                "components": ["dev-tool"],
                "package_groups": ["dev", "utilities"],
                "extensions": ["dev-mode"],
                "blockers": [],
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


def test_extension_handler_blocks_dev_extension_without_dev_profile(tmp_path: Path, monkeypatch):
    _write_manifest(tmp_path)
    service = ReleaseProfileService(tmp_path)
    monkeypatch.setattr("wizard.services.extension_handler.get_release_profile_service", lambda: service)

    handler = ExtensionHandler()
    handler.register(GitHubCLIExtension())

    status = handler.get_status("github-cli")

    assert status["enabled"] is False
    assert status["status"] == "disabled"
    assert status["required_profiles"] == ["dev"]
    assert status["profile_policy"] == "blocked"
    assert "dev" in status["profile_reason"]

    result = asyncio.run(handler.execute("github-cli", "sync:status"))
    assert "blocked by certified profile policy" in result["error"]
    assert result["required_profiles"] == ["dev"]


def test_extension_handler_allows_dev_extension_when_dev_profile_enabled(tmp_path: Path, monkeypatch):
    _write_manifest(tmp_path)
    service = ReleaseProfileService(tmp_path)
    service.install_profiles(["dev"])
    monkeypatch.setattr("wizard.services.extension_handler.get_release_profile_service", lambda: service)

    handler = ExtensionHandler()
    extension = GitHubCLIExtension()
    handler.register(extension)
    monkeypatch.setattr(extension, "initialize", lambda: asyncio.sleep(0, result=True))

    results = asyncio.run(handler.initialize_all())
    status = handler.get_status("github-cli")

    assert results["github-cli"] is True
    assert status["enabled"] is True
    assert status["profile_policy"] == "allowed"
