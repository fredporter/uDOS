from wizard.routes import ucode_setup_story_utils as utils


def test_load_setup_story_from_template(monkeypatch, tmp_path):
    repo_root = tmp_path / "repo"
    memory_root = tmp_path / "memory"
    (repo_root / "core" / "tui").mkdir(parents=True, exist_ok=True)
    template = repo_root / "core" / "tui" / "setup-story.md"
    template.write_text("---\ntitle: X\ntype: story\nsubmit_endpoint: /x\n---\nBody", encoding="utf-8")

    import wizard.services.path_utils as path_utils
    monkeypatch.setattr(path_utils, "get_repo_root", lambda: repo_root)
    monkeypatch.setattr(path_utils, "get_memory_dir", lambda: memory_root)

    import core.services.story_service as story_service

    def fake_parse_story_document(raw_content, required_frontmatter_keys=None):
        assert "Body" in raw_content
        return {"frontmatter": {"title": "X"}, "sections": []}

    monkeypatch.setattr(story_service, "parse_story_document", fake_parse_story_document)

    result = utils.load_setup_story()
    assert result["frontmatter"]["title"] == "X"
    assert (memory_root / "story" / "tui-setup-story.md").exists()
