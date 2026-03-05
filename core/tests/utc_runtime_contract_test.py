from __future__ import annotations

from pathlib import Path
import re

REPO_ROOT = Path(__file__).resolve().parents[2]

UTC_CRITICAL_FILES = [
    REPO_ROOT / "core/services/maintenance_utils.py",
    REPO_ROOT / "core/services/knowledge_artifact_service.py",
    REPO_ROOT / "core/services/mission_templates.py",
    REPO_ROOT / "core/services/vibe_binder_service.py",
    REPO_ROOT / "core/services/logging_api.py",
    REPO_ROOT / "core/commands/destroy_handler_helpers.py",
    REPO_ROOT / "core/services/vibe_wizard_service.py",
    REPO_ROOT / "wizard/services/monitoring_manager.py",
    REPO_ROOT / "wizard/services/feed_sync.py",
    REPO_ROOT / "wizard/services/quota_tracker.py",
    REPO_ROOT / "wizard/services/task_scheduler.py",
]

UTC_SECONDARY_FILES = [
    REPO_ROOT / "wizard/services/pdf_ocr_service.py",
    REPO_ROOT / "wizard/services/extension_handler.py",
    REPO_ROOT / "wizard/services/plugin_repository.py",
    REPO_ROOT / "wizard/services/enhanced_plugin_discovery.py",
    REPO_ROOT / "wizard/services/oauth_manager.py",
    REPO_ROOT / "wizard/services/mesh_sync.py",
    REPO_ROOT / "wizard/services/beacon_service.py",
    REPO_ROOT / "wizard/routes/beacon_routes.py",
    REPO_ROOT / "wizard/routes/settings_unified.py",
    REPO_ROOT / "wizard/services/home_assistant/api/rest.py",
    REPO_ROOT / "wizard/services/home_assistant/api/websocket.py",
    REPO_ROOT / "wizard/services/port_manager.py",
    REPO_ROOT / "wizard/routes/renderer_routes.py",
    REPO_ROOT / "wizard/routes/config_admin_routes.py",
    REPO_ROOT / "wizard/routes/config_routes.py",
    REPO_ROOT / "wizard/routes/log_routes.py",
    REPO_ROOT / "wizard/services/device_auth.py",
    REPO_ROOT / "wizard/services/url_to_markdown_service.py",
]

FORBIDDEN_PATTERNS = [
    re.compile(r"datetime\.now\("),
    re.compile(r"datetime\.utcnow\("),
    re.compile(r"datetime\.fromtimestamp\("),
]


def test_utc_critical_runtime_files_do_not_use_naive_datetime_calls() -> None:
    violations: list[str] = []
    for path in UTC_CRITICAL_FILES:
        source = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_PATTERNS:
            for match in pattern.finditer(source):
                line = source.count("\n", 0, match.start()) + 1
                violations.append(f"{path}:{line}: {pattern.pattern}")
    assert violations == []


def test_utc_secondary_runtime_files_do_not_use_naive_datetime_calls() -> None:
    violations: list[str] = []
    for path in UTC_SECONDARY_FILES:
        source = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_PATTERNS:
            for match in pattern.finditer(source):
                line = source.count("\n", 0, match.start()) + 1
                violations.append(f"{path}:{line}: {pattern.pattern}")
    assert violations == []
