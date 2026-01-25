"""
Wizard Setup Manager
====================

Provides setup status, required variables, and path validation for Wizard.
"""

from __future__ import annotations

import os
import json
from pathlib import Path
from typing import Dict, Any

from wizard.services.path_utils import get_repo_root, get_memory_dir
from wizard.services.setup_state import setup_state


def validate_database_paths() -> Dict[str, Any]:
    memory_root = get_memory_dir()
    paths = {
        "memory_root": memory_root,
        "logs": memory_root / "logs",
        "wizard_data": memory_root / "wizard",
    }
    results = {}
    for name, path in paths.items():
        path.mkdir(parents=True, exist_ok=True)
        results[name] = {
            "path": str(path),
            "exists": path.exists(),
            "writable": path.is_dir() and os.access(path, os.W_OK),
        }
    return results


def get_required_variables() -> Dict[str, Dict[str, Any]]:
    config = _load_wizard_config()
    return {
        "github_token": {
            "name": "GitHub API Token",
            "description": "Personal access token for GitHub API access",
            "env_var": "GITHUB_TOKEN",
            "required": False,
            "status": "configured" if os.getenv("GITHUB_TOKEN") else "optional",
            "documentation": "https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token",
        },
        "notion_api_key": {
            "name": "Notion API Key",
            "description": "API key for Notion workspace access",
            "env_var": "NOTION_API_KEY",
            "required": config.get("notion_enabled", False),
            "status": "configured" if os.getenv("NOTION_API_KEY") else "not-configured",
            "documentation": "https://developers.notion.com/docs/getting-started",
        },
        "notion_database_id": {
            "name": "Notion Database ID",
            "description": "ID of your main Notion database",
            "env_var": "NOTION_DATABASE_ID",
            "required": config.get("notion_enabled", False),
            "status": "configured" if os.getenv("NOTION_DATABASE_ID") else "not-configured",
            "documentation": "https://developers.notion.com/docs/working-with-databases",
        },
        "mistral_api_key": {
            "name": "Mistral API Key (Optional)",
            "description": "API key for cloud AI features via Mistral",
            "env_var": "MISTRAL_API_KEY",
            "required": False,
            "status": "configured" if os.getenv("MISTRAL_API_KEY") else "optional",
            "documentation": "https://docs.mistral.ai/",
        },
        "hubspot_api_key": {
            "name": "HubSpot API Key",
            "description": "API key for HubSpot CRM integration",
            "env_var": "HUBSPOT_API_KEY",
            "required": config.get("hubspot_enabled", False),
            "status": "configured" if os.getenv("HUBSPOT_API_KEY") else "optional",
            "documentation": "https://developers.hubspot.com/docs/api/overview",
        },
    }


def get_full_config_status() -> Dict[str, Any]:
    config = _load_wizard_config()
    return {
        "server": {
            "host": config.get("host", "0.0.0.0"),
            "port": config.get("port", 8765),
            "debug": config.get("debug", False),
        },
        "services": {
            "github": {
                "configured": bool(os.getenv("GITHUB_TOKEN")),
                "status": "ready" if os.getenv("GITHUB_TOKEN") else "not-configured",
            },
            "notion": {
                "configured": bool(os.getenv("NOTION_API_KEY")),
                "status": "ready" if os.getenv("NOTION_API_KEY") else "not-configured",
            },
            "ai": {
                "configured": bool(os.getenv("MISTRAL_API_KEY")),
                "status": "ready" if os.getenv("MISTRAL_API_KEY") else "not-configured",
            },
            "hubspot": {
                "configured": bool(os.getenv("HUBSPOT_API_KEY")),
                "status": "ready" if os.getenv("HUBSPOT_API_KEY") else "not-configured",
            },
        },
        "databases": validate_database_paths(),
        "setup": setup_state.get_status(),
        "features": {
            "notion_enabled": config.get("notion_enabled", False),
            "ai_gateway_enabled": config.get("ai_gateway_enabled", False),
            "github_push_enabled": config.get("github_push_enabled", False),
            "web_proxy_enabled": config.get("web_proxy_enabled", False),
        },
        "logging": {
            "directory": str(get_memory_dir() / "logs"),
        },
    }


def get_paths() -> Dict[str, Any]:
    root = get_repo_root()
    return {
        "root": str(root),
        "installation": {
            "core": str(root / "core"),
            "extensions": str(root / "extensions"),
            "app": str(root / "app"),
            "wizard": str(root / "wizard"),
            "dev": str(root / "dev"),
        },
        "data": {
            "memory_root": str(root / "memory"),
            "logs": str(root / "memory" / "logs"),
            "wizard_data": str(root / "memory" / "wizard"),
        },
        "documentation": {
            "readme": str(root / "README.md"),
            "agents": str(root / "AGENTS.md"),
            "roadmap": str(root / "docs" / "roadmap.md"),
        },
    }


def _load_wizard_config() -> Dict[str, Any]:
    config_path = get_repo_root() / "wizard" / "config" / "wizard.json"
    if not config_path.exists():
        return {
            "notion_enabled": False,
            "ai_gateway_enabled": False,
            "github_push_enabled": False,
            "web_proxy_enabled": False,
            "hubspot_enabled": False,
        }
    try:
        return json.loads(config_path.read_text())
    except Exception:
        return {
            "notion_enabled": False,
            "ai_gateway_enabled": False,
            "github_push_enabled": False,
            "web_proxy_enabled": False,
            "hubspot_enabled": False,
        }
