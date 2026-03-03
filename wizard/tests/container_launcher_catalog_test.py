from __future__ import annotations

import json
from pathlib import Path

from wizard.routes.container_launcher_routes import ContainerLauncher


def test_container_launcher_uses_shared_catalog_for_launchable_library_entries(tmp_path: Path):
    manifest_dir = tmp_path / "distribution" / "profiles"
    manifest_dir.mkdir(parents=True)
    (manifest_dir / "certified-profiles.json").write_text('{"extensions": {}}\n', encoding="utf-8")

    elite = tmp_path / "library" / "elite"
    elite.mkdir(parents=True)
    (elite / "container.json").write_text(
        json.dumps(
            {
                "container": {
                    "id": "elite",
                    "name": "Elite",
                    "description": "Space sim adapter",
                    "type": "git",
                    "source": "https://example.test/elite.git",
                    "ref": "main",
                },
                "service": {
                    "port": 7422,
                    "browser_route": "/ui/elite",
                    "health_check_url": "http://localhost:7422/health",
                },
                "repo_path": "memory/library/containers/elite",
                "launch_config": {"command": ["python3", "-m", "wizard.services.toybox.elite_adapter"]},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    launcher = ContainerLauncher(repo_root=tmp_path)
    config = launcher.get_container_config("elite")

    assert config is not None
    assert config["port"] == 7422
    assert config["browser_route"] == "/ui/elite"
    assert config["container_path"] == str(tmp_path / "memory" / "library" / "containers" / "elite")
    assert config["manifest_path"] == str(tmp_path / "library" / "elite" / "container.json")

    meta = launcher._read_container_metadata("elite")
    assert meta is not None
    assert meta["container"]["source"] == "https://example.test/elite.git"
    assert launcher._resolve_container_runtime_path("elite") == tmp_path / "memory" / "library" / "containers" / "elite"
