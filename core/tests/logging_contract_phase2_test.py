from __future__ import annotations

from pathlib import Path


def test_server_modular_source_uses_core_logging_contract():
    path = Path("distribution/plugins/api/server_modular.py")
    text = path.read_text(encoding="utf-8")
    assert "from core.services.logging_api import get_logger" in text
    assert "api_logger = get_logger(" in text
    assert "RotatingFileHandler" not in text
    assert "logging.basicConfig" not in text


def test_dev_mode_vibe_cli_service_uses_shared_logging_contract():
    path = Path("wizard/extensions/assistant/vibe_cli_service.py")
    text = path.read_text(encoding="utf-8")
    assert "from wizard.services.logging_api import get_logger" in text
    assert 'logger = get_logger("dev-mode-tool-service")' in text
    assert "RotatingFileHandler" not in text
    assert "logging.basicConfig" not in text


def test_input_command_prompt_uses_core_logging_contract_only():
    path = Path("core/input/command_prompt.py")
    text = path.read_text(encoding="utf-8")
    assert "logging.getLogger(" not in text
    assert "StreamHandler(" not in text
    assert "logging.basicConfig" not in text


def test_input_keypad_handler_uses_core_logging_contract_only():
    path = Path("core/input/keypad_handler.py")
    text = path.read_text(encoding="utf-8")
    assert "logging.getLogger(" not in text
    assert "StreamHandler(" not in text
    assert "logging.basicConfig" not in text
