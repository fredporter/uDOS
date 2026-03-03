from __future__ import annotations

import json
from pathlib import Path

from wizard.services.enhanced_plugin_discovery import EnhancedPluginDiscovery
from wizard.services.system_info_service import SystemInfoService


def test_enhanced_plugin_discovery_uses_shared_catalog_for_library_and_extension(tmp_path: Path):
    manifest_dir = tmp_path / "distribution" / "profiles"
    manifest_dir.mkdir(parents=True)
    (manifest_dir / "certified-profiles.json").write_text(
        json.dumps(
            {
                "extensions": {
                    "thin-gui": {
                        "label": "Thin GUI",
                        "path": "extensions/thin-gui",
                        "profiles": ["home"],
                        "summary": "Shared GUI contract",
                        "category": "ui",
                        "runtime_owner": "shared",
                        "callable_from": ["core", "wizard", "uhome"],
                    }
                }
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "distribution" / "plugins").mkdir(parents=True)
    (tmp_path / "extensions" / "transport").mkdir(parents=True)
    thin_gui = tmp_path / "extensions" / "thin-gui"
    thin_gui.mkdir(parents=True)
    (thin_gui / "extension.json").write_text(
        json.dumps({"description": "Thin local manifest", "library_refs": ["typo"]}) + "\n",
        encoding="utf-8",
    )
    (thin_gui / "package.json").write_text('{"version":"1.0.0"}\n', encoding="utf-8")

    typo = tmp_path / "library" / "typo"
    typo.mkdir(parents=True)
    (typo / "container.json").write_text(
        json.dumps(
            {
                "container": {
                    "id": "typo",
                    "name": "Typo",
                    "description": "Markdown editor",
                    "version": "0.9.0",
                    "source": "https://example.test/typo.git",
                },
                "metadata": {
                    "category": "editor",
                    "license": "MIT",
                    "maintainer": "uDOS",
                    "homepage": "https://example.test/typo",
                    "documentation": "README.md",
                },
                "dependencies": {"integrations": ["micro"]},
                "service": {"health_check_url": "http://localhost:3001/health"},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    discovery = EnhancedPluginDiscovery(repo_root=tmp_path)
    plugins = discovery.discover_all()

    assert plugins["typo"].config_path == "library/typo/container.json"
    assert plugins["typo"].dependencies == ["micro"]
    assert plugins["typo"].health_check_url == "http://localhost:3001/health"
    assert plugins["thin-gui"].config_path == "extensions/thin-gui/extension.json"
    assert plugins["thin-gui"].description == "Shared GUI contract"


def test_system_info_service_uses_shared_catalog_metadata_for_library_status(tmp_path: Path):
    manifest_dir = tmp_path / "distribution" / "profiles"
    manifest_dir.mkdir(parents=True)
    (manifest_dir / "certified-profiles.json").write_text('{"extensions": {}}\n', encoding="utf-8")

    typo = tmp_path / "library" / "typo"
    typo.mkdir(parents=True)
    (typo / "container.json").write_text(
        json.dumps(
            {
                "container": {
                    "id": "typo",
                    "name": "Typo",
                    "description": "Markdown editor",
                    "type": "git",
                    "source": "https://example.test/typo.git",
                    "ref": "main",
                    "cloned_at": "2026-03-03T00:00:00Z",
                    "version": "0.9.0",
                },
                "repo_path": "memory/library/containers/typo",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    resolved = tmp_path / "memory" / "library" / "containers" / "typo"
    resolved.mkdir(parents=True)
    (resolved / "setup.sh").write_text("#!/bin/sh\n", encoding="utf-8")

    status = SystemInfoService(tmp_path).get_library_status()

    assert status.total_integrations == 1
    integration = status.integrations[0]
    assert integration.name == "typo"
    assert integration.path == str(resolved)
    assert integration.container_type == "git"
    assert integration.git_source == "https://example.test/typo.git"
    assert integration.git_ref == "main"
    assert integration.git_cloned is True
    assert integration.installed is True
