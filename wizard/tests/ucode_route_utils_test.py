from pathlib import Path

from fastapi import HTTPException

from wizard.routes import ucode_route_utils as utils


def test_shell_safe_blocks_destructive_patterns():
    assert utils.shell_safe("echo hello") is True
    assert utils.shell_safe("rm -rf /tmp/x") is False


def test_parse_ok_file_args_with_lines_and_cloud():
    parsed = utils.parse_ok_file_args("foo.py 10:20 --cloud")
    assert parsed["path"].name == "foo.py"
    assert parsed["line_start"] == 10
    assert parsed["line_end"] == 20
    assert parsed["use_cloud"] is True


def test_load_ok_file_content_with_range(tmp_path):
    file_path = tmp_path / "sample.py"
    file_path.write_text("a\nb\nc\nd\n", encoding="utf-8")

    content = utils.load_ok_file_content(file_path, line_start=2, line_end=3)
    assert content == "b\nc"


def test_load_ok_file_content_missing_raises(tmp_path):
    missing = tmp_path / "missing.py"
    try:
        utils.load_ok_file_content(missing)
        assert False, "Expected HTTPException"
    except HTTPException as exc:
        assert exc.status_code == 404


def test_build_ok_file_prompt_modes(tmp_path):
    file_path = Path(tmp_path / "x.py")
    text = "print('x')"

    explain = utils.build_ok_file_prompt("EXPLAIN", file_path, text)
    diff = utils.build_ok_file_prompt("DIFF", file_path, text)
    patch = utils.build_ok_file_prompt("PATCH", file_path, text)

    assert "Explain this code" in explain
    assert "unified diff" in diff
    assert "Draft a patch" in patch
