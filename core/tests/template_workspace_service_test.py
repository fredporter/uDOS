from __future__ import annotations

from pathlib import Path

from core.services.template_workspace_service import TemplateWorkspaceService


def test_template_workspace_service_seeds_default_workspace_and_component_contract(
    tmp_path: Path,
):
    seed_root = tmp_path / "core" / "framework" / "seed" / "bank" / "typo-workspace"
    (seed_root / "settings").mkdir(parents=True)
    (seed_root / "instructions").mkdir(parents=True)
    (seed_root / "settings" / "shared.md").write_text("# shared settings\n", encoding="utf-8")
    (seed_root / "settings" / "sonic.md").write_text("# sonic settings\n", encoding="utf-8")
    (seed_root / "instructions" / "shared.md").write_text(
        "# shared instructions\n", encoding="utf-8"
    )

    service = TemplateWorkspaceService(tmp_path)

    contract = service.component_contract("sonic")

    assert contract["editor_library_ref"] == "typo"
    assert Path(contract["settings"]["seeded"]).name == "sonic.md"
    assert Path(contract["settings"]["default"]).read_text(encoding="utf-8") == "# sonic settings\n"
    assert Path(contract["instructions"]["default"]).read_text(
        encoding="utf-8"
    ) == "# shared instructions\n"
    assert Path(contract["settings"]["user"]).parent.exists()


def test_template_workspace_service_returns_workspace_contract_for_shared_components(
    tmp_path: Path,
):
    seed_root = tmp_path / "core" / "framework" / "seed" / "bank" / "typo-workspace"
    (seed_root / "settings").mkdir(parents=True)
    (seed_root / "instructions").mkdir(parents=True)
    (seed_root / "settings" / "shared.md").write_text("# shared\n", encoding="utf-8")
    (seed_root / "instructions" / "shared.md").write_text("# shared\n", encoding="utf-8")

    service = TemplateWorkspaceService(tmp_path)
    contract = service.workspace_contract()

    assert contract["workspace_ref"] == "@memory/bank/typo-workspace"
    assert "sonic" in contract["components"]
    assert "uhome" in contract["components"]
    assert contract["components"]["shared"]["settings"]["seeded"].endswith(
        "settings/shared.md"
    )


def test_template_workspace_service_reads_and_writes_user_documents(tmp_path: Path):
    seed_root = tmp_path / "core" / "framework" / "seed" / "bank" / "typo-workspace"
    (seed_root / "settings").mkdir(parents=True)
    (seed_root / "instructions").mkdir(parents=True)
    (seed_root / "settings" / "shared.md").write_text("# shared\n", encoding="utf-8")
    (seed_root / "instructions" / "shared.md").write_text("# shared instructions\n", encoding="utf-8")

    service = TemplateWorkspaceService(tmp_path)

    before = service.read_document("settings", "uhome")
    assert before["effective_source"] == "default"
    assert before["effective_content"] == "# shared\n"

    after = service.write_user_document("settings", "uhome", "# user override\n")
    assert after["effective_source"] == "user"
    assert after["effective_content"] == "# user override\n"
    assert Path(after["paths"]["user"]).read_text(encoding="utf-8") == "# user override\n"


def test_template_workspace_service_reads_and_updates_markdown_fields(tmp_path: Path):
    seed_root = tmp_path / "core" / "framework" / "seed" / "bank" / "typo-workspace"
    (seed_root / "settings").mkdir(parents=True)
    (seed_root / "instructions").mkdir(parents=True)
    (seed_root / "settings" / "uhome.md").write_text(
        "# uHOME\n\n- ad-processing-mode: disabled\n",
        encoding="utf-8",
    )
    (seed_root / "instructions" / "shared.md").write_text("# shared\n", encoding="utf-8")

    service = TemplateWorkspaceService(tmp_path)

    assert service.read_fields("settings", "uhome")["ad_processing_mode"] == "disabled"

    snapshot = service.write_user_field(
        "settings", "uhome", "ad-processing-mode", "comskip_auto"
    )
    assert snapshot["effective_source"] == "user"
    assert "comskip_auto" in snapshot["effective_content"]
    assert service.read_fields("settings", "uhome")["ad_processing_mode"] == "comskip_auto"
