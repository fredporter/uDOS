from __future__ import annotations

from pathlib import Path
import re


UTC_CRITICAL_FILES = [
    Path("/Users/fredbook/Code/uDOS/core/services/maintenance_utils.py"),
    Path("/Users/fredbook/Code/uDOS/core/services/knowledge_artifact_service.py"),
    Path("/Users/fredbook/Code/uDOS/core/services/mission_templates.py"),
    Path("/Users/fredbook/Code/uDOS/core/services/vibe_binder_service.py"),
    Path("/Users/fredbook/Code/uDOS/core/services/logging_api.py"),
    Path("/Users/fredbook/Code/uDOS/core/commands/destroy_handler_helpers.py"),
    Path("/Users/fredbook/Code/uDOS/core/services/vibe_wizard_service.py"),
    Path("/Users/fredbook/Code/uDOS/wizard/services/monitoring_manager.py"),
    Path("/Users/fredbook/Code/uDOS/wizard/services/feed_sync.py"),
    Path("/Users/fredbook/Code/uDOS/wizard/services/quota_tracker.py"),
    Path("/Users/fredbook/Code/uDOS/wizard/services/task_scheduler.py"),
]

UTC_SECONDARY_FILES = [
    Path("/Users/fredbook/Code/uDOS/wizard/services/pdf_ocr_service.py"),
    Path("/Users/fredbook/Code/uDOS/wizard/services/extension_handler.py"),
    Path("/Users/fredbook/Code/uDOS/wizard/services/plugin_repository.py"),
    Path("/Users/fredbook/Code/uDOS/wizard/services/enhanced_plugin_discovery.py"),
    Path("/Users/fredbook/Code/uDOS/wizard/services/oauth_manager.py"),
    Path("/Users/fredbook/Code/uDOS/wizard/services/mesh_sync.py"),
    Path("/Users/fredbook/Code/uDOS/wizard/services/beacon_service.py"),
    Path("/Users/fredbook/Code/uDOS/wizard/routes/beacon_routes.py"),
    Path("/Users/fredbook/Code/uDOS/wizard/routes/settings_unified.py"),
    Path("/Users/fredbook/Code/uDOS/wizard/services/home_assistant/api/rest.py"),
    Path("/Users/fredbook/Code/uDOS/wizard/services/home_assistant/api/websocket.py"),
    Path("/Users/fredbook/Code/uDOS/wizard/services/port_manager.py"),
    Path("/Users/fredbook/Code/uDOS/wizard/routes/renderer_routes.py"),
    Path("/Users/fredbook/Code/uDOS/wizard/routes/config_admin_routes.py"),
    Path("/Users/fredbook/Code/uDOS/wizard/routes/config_routes.py"),
    Path("/Users/fredbook/Code/uDOS/wizard/routes/log_routes.py"),
    Path("/Users/fredbook/Code/uDOS/wizard/services/device_auth.py"),
    Path("/Users/fredbook/Code/uDOS/wizard/services/url_to_markdown_service.py"),
    Path("/Users/fredbook/Code/uDOS/wizard/services/ok_gateway.py"),
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
