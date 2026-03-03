from __future__ import annotations

import json
from pathlib import Path

from core.services.container_catalog_service import ContainerCatalogService


def test_container_catalog_discovers_library_and_extension_entries(tmp_path: Path):
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
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    thin_gui = tmp_path / "extensions" / "thin-gui"
    thin_gui.mkdir(parents=True)
    (thin_gui / "extension.json").write_text(
        json.dumps(
            {
                "description": "Thin local manifest",
                "library_refs": ["typo", "micro"],
                "standalone_capable": True,
            }
        )
        + "\n",
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
                    "type": "git",
                    "ref": "main",
                    "version": "0.9.0",
                    "source": "https://example.test/typo.git",
                },
                "metadata": {"category": "editor"},
                "policy": {"execution_model": "container-library-v1"},
                "service": {"browser_route": "/ui/typo", "port": 3001},
                "dependencies": {"integrations": ["micro"]},
                "apk_dependencies": ["git"],
                "repo_path": "memory/library/containers/typo",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    service = ContainerCatalogService(tmp_path)

    entries = service.list_entries()
    by_id = {entry.entry_id: entry for entry in entries}

    assert "typo" in by_id
    assert by_id["typo"].kind == "library"
    assert by_id["typo"].execution.runtime_owner == "shared"
    assert by_id["typo"].lens_vars["lens"] == "repo-library:typo"
    assert by_id["typo"].lens_vars["workspace_ref"] == "@memory/bank/typo-workspace"
    assert by_id["typo"].metadata["manifest_path"] == "library/typo/container.json"
    assert by_id["typo"].metadata["integration_dependencies"] == ["micro"]
    assert by_id["typo"].metadata["package_dependencies"]["apk_dependencies"] == ["git"]
    assert by_id["typo"].metadata["template_workspace"]["editor_library_ref"] == "typo"

    assert "thin-gui" in by_id
    assert by_id["thin-gui"].kind == "extension"
    assert by_id["thin-gui"].available is True
    assert "uhome" in by_id["thin-gui"].execution.callable_from
    assert by_id["thin-gui"].lens_vars["profiles"] == ["home"]
    assert by_id["thin-gui"].metadata["description"] == "Thin local manifest"
    assert by_id["thin-gui"].metadata["library_refs"] == ["typo", "micro"]
    assert by_id["thin-gui"].metadata["manifest_path"] == "extensions/thin-gui/extension.json"
    assert by_id["thin-gui"].metadata["template_workspace"]["workspace_ref"] == "@memory/bank/typo-workspace"
