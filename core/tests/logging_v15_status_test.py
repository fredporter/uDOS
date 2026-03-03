from __future__ import annotations

import importlib


def test_core_logging_v15_health_and_stats(tmp_path, monkeypatch):
    monkeypatch.setenv("UDOS_LOG_ROOT", str(tmp_path))
    logging_api = importlib.import_module("core.services.logging_api")
    logging_api._LOG_MANAGER = None

    logger = logging_api.get_logger("core", category="test", name="core")
    logger.info("health-check", ctx={"topic": "logging"})

    health = logging_api.get_logging_health()
    stats = logging_api.get_log_stats()

    assert health["schema"] == "udos-log-v1.5"
    assert health["runtime_version"] == "v1.5"
    assert stats["schema"] == "udos-log-v1.5"
    assert stats["runtime_version"] == "v1.5"
    assert stats["total_files"] >= 1
    assert stats["by_component"]["core"]["count"] >= 1


def test_wizard_logging_wrapper_exposes_v15_stats(tmp_path, monkeypatch):
    monkeypatch.setenv("UDOS_LOG_ROOT", str(tmp_path))

    core_logging = importlib.import_module("core.services.logging_api")
    core_logging._LOG_MANAGER = None

    wizard_logging = importlib.import_module("wizard.services.logging_api")
    logger = wizard_logging.get_logger("wizard", category="status", name="wizard-status")
    logger.info("wizard-health")

    health = wizard_logging.get_logging_health()
    stats = wizard_logging.get_log_stats()

    assert health["schema"] == "udos-log-v1.5"
    assert stats["schema"] == "udos-log-v1.5"
    assert stats["by_component"]["wizard"]["count"] >= 1
