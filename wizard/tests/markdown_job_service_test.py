from wizard.services.markdown_job_service import MarkdownJobService


def test_import_markdown_tasks(tmp_path):
    vault = tmp_path / "vault"
    vault.mkdir()
    source = vault / "tasks.md"
    source.write_text(
        """
- schedule: weekday-evening
- priority: 7
        - project: release-ops
        - budget_units: 3
        - local_only: true
        - [ ] Prepare release notes
        - [x] Done task
        - [ ] Review workflow prompts
""".strip(),
        encoding="utf-8",
    )

    service = MarkdownJobService(repo_root=tmp_path, vault_root=vault)
    jobs = service.import_source("tasks.md")
    assert len(jobs) == 2
    assert jobs[0]["schedule"] == "weekday-evening"
    assert jobs[0]["priority"] == 7
    assert jobs[0]["requires_network"] is False
    assert jobs[0]["payload"]["project"] == "release-ops"
    assert jobs[0]["payload"]["budget_units"] == 3


def test_import_workflow_markdown(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    source = docs / "writing-workflow.md"
    source.write_text(
        """
# WORKFLOW: writing-article-v1

## Phases
1. Outline (writing/outline -> 01-outline.md)
2. Draft (writing/draft -> 02-draft.md)
""".strip(),
        encoding="utf-8",
    )

    service = MarkdownJobService(repo_root=tmp_path, vault_root=tmp_path / "vault")
    jobs = service.import_source(str(source))
    assert len(jobs) == 2
    assert jobs[0]["kind"] == "workflow_phase"
    assert jobs[0]["payload"]["project"] == "writing-workflow"
    assert jobs[0]["payload"]["prompt_name"] == "outline"
    assert jobs[0]["payload"]["window"] == "off_peak"
