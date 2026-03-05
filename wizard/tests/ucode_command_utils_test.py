from pathlib import Path

from wizard.routes.ucode_command_utils import (
    normalize_logic_command,
    parse_logic_command,
    prepare_logic_coding_request,
)


def test_normalize_logic_command_passthrough():
    assert normalize_logic_command("HELP") == "HELP"


def test_normalize_logic_command_question_prefix():
    assert normalize_logic_command("? explain file.py") == "LOGIC explain file.py"


def test_parse_logic_command_extracts_mode_and_tokens():
    parsed = parse_logic_command("LOGIC EXPLAIN sample.py 1 10 --cloud")
    assert parsed is not None
    assert parsed.command == "LOGIC EXPLAIN sample.py 1 10 --cloud"
    assert parsed.logic_mode == "EXPLAIN"
    assert parsed.logic_tokens[0] == "EXPLAIN"


def test_prepare_logic_coding_request_builds_prompt(tmp_path: Path):
    file_path = tmp_path / "sample.py"
    file_path.write_text("print('hello')\n", encoding="utf-8")

    parsed = parse_logic_command(f"LOGIC EXPLAIN {file_path}")
    assert parsed is not None
    request = prepare_logic_coding_request(
        parsed=parsed,
        is_dev_mode_active=lambda: True,
        logger=type("L", (), {"warn": lambda *args, **kwargs: None})(),
        corr_id="C1",
        rejected_log_message="rejected",
        missing_file_log_message="missing",
    )
    assert request.mode == "EXPLAIN"
    assert request.path == file_path
    assert "Explain this code from" in request.prompt
