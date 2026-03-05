from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

ACTIVE_RUNTIME_FILES = [
    REPO_ROOT / "core" / "tui" / "ucode.py",
    REPO_ROOT / "core" / "commands" / "binder_handler.py",
    REPO_ROOT / "core" / "commands" / "help_handler.py",
    REPO_ROOT / "core" / "commands" / "setup_handler.py",
    REPO_ROOT / "core" / "commands" / "setup_handler_helpers.py",
    REPO_ROOT / "core" / "commands" / "ucode_handler.py",
    REPO_ROOT / "core" / "commands" / "webhook_setup_handler.py",
    REPO_ROOT / "core" / "services" / "secret_vault.py",
    REPO_ROOT / "core" / "services" / "vibe_cli_handler.py",
    REPO_ROOT / "core" / "services" / "ok_router.py",
    REPO_ROOT / "wizard" / "mcp" / "mcp_server.py",
    REPO_ROOT / "wizard" / "mcp" / "gateway.py",
    REPO_ROOT / "wizard" / "mcp" / "tools" / "ucode_registry.py",
    REPO_ROOT / "wizard" / "mcp" / "tools" / "ucode_tools.py",
    REPO_ROOT / "wizard" / "mcp" / "tools" / "ucode_proxies.py",
    REPO_ROOT / "wizard" / "routes" / "ucode_routes.py",
    REPO_ROOT / "wizard" / "services" / "dev_extension_service.py",
    REPO_ROOT / "wizard" / "extensions" / "assistant" / "vibe_cli_service.py",
    REPO_ROOT / "wizard" / "services" / "provider_registry.py",
]

FORBIDDEN_RUNTIME_TOKENS = [
    "core.services.vibe_binder_service",
    "core.services.vibe_device_service",
    "core.services.vibe_network_service",
    "core.services.vibe_script_service",
    "core.services.vibe_sync_service",
    "core.services.vibe_user_service",
    "core.services.vibe_vault_service",
    "core.services.vibe_wizard_service",
    "core.services.vibe_workspace_service",
    "vibe.core.input_router",
    "vibe.core.command_engine",
    "vibe.core.response_normaliser",
    "vibe.core.tools.base",
    "vibe.core.tools.ucode",
    "vibe.core.provider_engine",
    "_tool_manager",
    "vibe-cli",
]

NORMALISED_WIZARD_DOCS = [
    REPO_ROOT / "docs" / "INSTALLATION.md",
    REPO_ROOT / "docs" / "howto" / "CONTAINER-SYSTEM-QUICK-REF.md",
    REPO_ROOT / "docs" / "howto" / "SETUP-SECRETS.md",
    REPO_ROOT / "docs" / "howto" / "WIZARD-ADMIN-SECRET-CONTRACT-RECOVERY.md",
    REPO_ROOT / "docs" / "howto" / "renderer-indexer-runbook.md",
    REPO_ROOT / "docs" / "features" / "SONIC-MODULAR-FILE-INDEX.md",
    REPO_ROOT / "docs" / "troubleshooting" / "README.md",
    REPO_ROOT / "docs" / "specs" / "ENV-STRUCTURE-V1.1.0.md",
    REPO_ROOT / "wizard" / "docs" / "SONIC-DATASETS.md",
    REPO_ROOT / "wizard" / "docs" / "PORT-MANAGER.md",
    REPO_ROOT / "wizard" / "docs" / "PEEK-COMMAND.md",
    REPO_ROOT / "wizard" / "docs" / "BEACON-IMPLEMENTATION.md",
    REPO_ROOT / "wizard" / "docs" / "api" / "tools" / "mcp-tools.md",
]

FORBIDDEN_DOC_URLS = [
    "http://localhost:8765",
    "http://127.0.0.1:8765",
]


def test_active_tui_and_mcp_runtime_files_do_not_depend_on_legacy_vibe_core_modules() -> None:
    violations: list[str] = []
    for path in ACTIVE_RUNTIME_FILES:
        source = path.read_text(encoding="utf-8")
        for token in FORBIDDEN_RUNTIME_TOKENS:
            if token in source:
                violations.append(f"{path}: {token}")
    assert violations == []


def test_normalised_wizard_docs_do_not_hardcode_localhost_endpoints() -> None:
    violations: list[str] = []
    for path in NORMALISED_WIZARD_DOCS:
        source = path.read_text(encoding="utf-8")
        for token in FORBIDDEN_DOC_URLS:
            if token in source:
                violations.append(f"{path}: {token}")
    assert violations == []
