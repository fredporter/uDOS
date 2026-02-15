from wizard.routes.ucode_command_utils import normalize_ok_command


def test_normalize_ok_command_passthrough():
    assert normalize_ok_command("HELP") == "HELP"


def test_normalize_ok_command_question_prefix():
    assert normalize_ok_command("? explain file.py") == "OK explain file.py"
