"""Documentation contracts for Core/Wizard/Sonic install and update guidance."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_installation_guide_covers_core_and_wizard_profiles() -> None:
    installation_doc = (REPO_ROOT / "docs" / "INSTALLATION.md").read_text(encoding="utf-8")
    assert "./bin/udos install --core" in installation_doc
    assert "./bin/udos install --wizard" in installation_doc
    assert "bin/ucode-tui-v1.5.command" in installation_doc
    assert "ALPINE-CORE-PLUGIN-FORMAT-v1.5.md" in installation_doc
    assert "uv sync --extra udos" in installation_doc
    assert "uv sync --extra udos-wizard" in installation_doc
    assert "./scripts/demo_renderer.sh" in installation_doc
    assert "./scripts/demo_core_stdlib_py_strict.sh" in installation_doc
    assert "./scripts/demo_wizard_advanced_strict.sh" in installation_doc
    assert "./scripts/demo_story_form_tui.sh" in installation_doc


def test_sonic_release_install_guide_exists_and_contains_build_flow() -> None:
    sonic_doc = (REPO_ROOT / "docs" / "howto" / "SONIC-STANDALONE-RELEASE-AND-INSTALL.md").read_text(
        encoding="utf-8"
    )
    assert "distribution/alpine-core/build-sonic-stick.sh" in sonic_doc
    assert "release-readiness" in sonic_doc


def test_public_docs_front_door_highlights_stable_launcher_and_alpine_packaging() -> None:
    root_readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    docs_readme = (REPO_ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    status_doc = (REPO_ROOT / "docs" / "STATUS.md").read_text(encoding="utf-8")

    assert "./bin/udos install" in root_readme
    assert "bin/ucode-tui-v1.5.command" in root_readme
    assert "ALPINE-CORE-PLUGIN-FORMAT-v1.5.md" in root_readme
    assert "bin/ucode-tui-v1.5.command" in docs_readme
    assert "ALPINE-CORE-PLUGIN-FORMAT-v1.5.md" in docs_readme
    assert "bin/ucode-tui-v1.5.command" in status_doc
    assert "Alpine core plus plugin artifacts" in status_doc


def test_public_docs_front_door_avoids_machine_local_repo_paths() -> None:
    doc_paths = [
        REPO_ROOT / "docs" / "INDEX.md",
        REPO_ROOT / "docs" / "examples" / "ucode_v1_5_release_pack" / "README.md",
        REPO_ROOT / "docs" / "specs" / "V1-5-STABLE-SIGNOFF.md",
    ]
    for doc_path in doc_paths:
        content = doc_path.read_text(encoding="utf-8")
        assert "/Users/fredbook/Code/uDOS" not in content, f"machine-local path leaked in {doc_path}"
