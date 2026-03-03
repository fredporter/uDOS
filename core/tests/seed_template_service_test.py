from __future__ import annotations

from pathlib import Path

from core.services.seed_template_service import SeedTemplateService


def test_seed_template_service_seeds_default_workspace_and_lists_families(
    tmp_path: Path,
):
    seed_root = tmp_path / "core" / "framework" / "seed" / "bank" / "templates"
    (seed_root / "workflows").mkdir(parents=True)
    (seed_root / "missions").mkdir(parents=True)
    (seed_root / "workflows" / "WRITING-article.md").write_text(
        "# WORKFLOW: writing-article-v1\n", encoding="utf-8"
    )
    (seed_root / "missions" / "MISSION-template.md").write_text(
        "# MISSION: template-v1\n", encoding="utf-8"
    )

    service = SeedTemplateService(tmp_path)
    contract = service.ensure_workspace()

    assert Path(contract["default_root"]).exists()
    assert service.list_families() == ["missions", "workflows"]
    assert Path(contract["default_root"], "workflows", "WRITING-article.md").exists()


def test_seed_template_service_reads_seeded_template_content(tmp_path: Path):
    seed_root = tmp_path / "core" / "framework" / "seed" / "bank" / "templates"
    (seed_root / "captures").mkdir(parents=True)
    content = "# CAPTURE: topic-template-v1\n\n## Purpose\nCapture a topic\n"
    (seed_root / "captures" / "CAPTURE-template.md").write_text(
        content, encoding="utf-8"
    )

    service = SeedTemplateService(tmp_path)

    snapshot = service.read_template("captures", "CAPTURE-template")

    assert snapshot["effective_source"] == "default"
    assert snapshot["content"] == content
    assert snapshot["family"] == "captures"


def test_seed_template_service_duplicates_template_to_user(tmp_path: Path):
    seed_root = tmp_path / "core" / "framework" / "seed" / "bank" / "templates"
    (seed_root / "submissions").mkdir(parents=True)
    content = "# SUBMISSION: sonic-device-template-v1\n"
    (seed_root / "submissions" / "DEVICE-SUBMISSION-template.md").write_text(
        content, encoding="utf-8"
    )

    service = SeedTemplateService(tmp_path)

    result = service.duplicate_to_user(
        "submissions",
        "DEVICE-SUBMISSION-template",
        target_name="my-device-draft",
    )

    target_path = Path(result["target_path"])
    assert target_path.exists()
    assert target_path.read_text(encoding="utf-8") == content

    snapshot = service.read_template("submissions", "my-device-draft")
    assert snapshot["effective_source"] == "user"
    assert snapshot["content"] == content


def test_seed_template_service_workspace_contract_includes_template_inventory(
    tmp_path: Path,
):
    seed_root = tmp_path / "core" / "framework" / "seed" / "bank" / "templates"
    (seed_root / "workflows").mkdir(parents=True)
    (seed_root / "workflows" / "WRITING-article.md").write_text(
        "# WORKFLOW: writing-article-v1\n", encoding="utf-8"
    )

    service = SeedTemplateService(tmp_path)
    contract = service.workspace_contract()

    assert "workflows" in contract["families"]
    assert contract["families"]["workflows"]["templates"] == ["WRITING-article"]
