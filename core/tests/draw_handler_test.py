from pathlib import Path

from core.commands.draw_handler import DrawHandler


def test_draw_py_pat_list_returns_patterns() -> None:
    handler = DrawHandler()
    result = handler.handle("DRAW", ["--py", "PAT", "LIST"])

    assert result.get("status") == "success"
    output = result.get("output", "")
    assert "DRAW PAT LIST" in output
    assert "- c64" in output
    assert "- mosaic" in output


def test_draw_md_block_wraps_in_markdown_fence() -> None:
    handler = DrawHandler()
    result = handler.handle("DRAW", ["MD", "BLOCK", "udos"])

    assert result.get("status") == "success"
    assert result.get("format") == "markdown"
    output = result.get("output", "")
    assert output.startswith("# DRAW BLOCK")
    assert "```text" in output
    assert "```" in output


def test_draw_save_markdown_to_explicit_path(tmp_path: Path) -> None:
    handler = DrawHandler()
    target = tmp_path / "diagram.md"
    result = handler.handle("DRAW", ["--md", "--save", str(target), "MAP"])

    assert result.get("status") == "success"
    assert result.get("saved_to") == str(target)
    assert target.exists()
    saved = target.read_text()
    assert saved.startswith("# DRAW MAP")
    assert "```text" in saved
