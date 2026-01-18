"""
Wizard Dashboard Index
======================

Main dashboard index for Wizard Server. Lists all available feature pages,
API endpoints, and services.

This is the primary entry point that the TUI pokes on startup.

Endpoints:
  GET /api/v1/index           - Dashboard index (JSON)
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any, List
from datetime import datetime

from wizard.services.config_framework import get_config_framework, ConfigFramework

router = APIRouter(tags=["dashboard"])


@router.get("/api/v1/index", tags=["dashboard"])
async def get_dashboard_index(framework: ConfigFramework = Depends(get_config_framework)) -> Dict[str, Any]:
    """Get dashboard index as JSON (for TUI and API clients)."""

    features = [
        {
            "id": "config",
            "name": "⚙️ Configuration",
            "description": "Manage wizard.json, .env files, and API keys",
            "url": "/api/v1/config/dashboard",
            "category": "settings",
            "status": "active",
        },
        {
            "id": "font-manager",
            "name": "🔤 Font Manager",
            "description": "Upload, manage, and select custom fonts",
            "url": "/font-manager",
            "category": "design",
            "status": "planned",
        },
        {
            "id": "typo",
            "name": "✏️ Text Editor (Typo)",
            "description": "Rich text editor with Tailwind styling and live preview",
            "url": "/typo",
            "category": "editing",
            "status": "active",
        },
        {
            "id": "grid-editor",
            "name": "🎮 Grid Editor",
            "description": "Edit tile-based worlds and spatial layouts",
            "url": "/grid-editor",
            "category": "content",
            "status": "planned",
        },
        {
            "id": "notifications",
            "name": "🔔 Notifications",
            "description": "View and manage notification history",
            "url": "/api/v1/config/notifications/history",
            "category": "monitoring",
            "status": "active",
        },
        {
            "id": "slack",
            "name": "💬 Slack Integration",
            "description": "Connect and manage Slack notifications",
            "url": "/api/v1/slack/status",
            "category": "integrations",
            "status": "active",
        },
        {
            "id": "ai-gateway",
            "name": "🤖 AI Gateway",
            "description": "View available models and AI routing status",
            "url": "/api/v1/ai/status",
            "category": "ai",
            "status": "active",
        },
        {
            "id": "plugins",
            "name": "📦 Plugin Repository",
            "description": "Browse and install plugins",
            "url": "/api/v1/plugin/search",
            "category": "plugins",
            "status": "active",
        },
        {
            "id": "github",
            "name": "🐙 GitHub Monitor",
            "description": "View GitHub Actions status and CI/CD pipeline",
            "url": "/api/v1/github/status",
            "category": "devops",
            "status": "active",
        },
        {
            "id": "ports",
            "name": "🔌 Port Manager",
            "description": "Monitor and manage service ports",
            "url": "/api/v1/ports/status",
            "category": "infrastructure",
            "status": "active",
        },
    ]

    api_endpoints = [
        {"method": "GET", "path": "/health", "description": "Health check (no auth)"},
        {"method": "GET", "path": "/api/v1/index", "description": "This dashboard (JSON)"},
        {"method": "GET", "path": "/api/v1/status", "description": "Server status & session info"},
        {"method": "GET", "path": "/api/v1/config/dashboard", "description": "Configuration dashboard"},
        {"method": "GET", "path": "/api/v1/ai/status", "description": "AI gateway status"},
        {"method": "GET", "path": "/api/v1/ai/models", "description": "List available AI models"},
        {"method": "GET", "path": "/api/v1/rate-limits", "description": "Current rate limit status"},
    ]

    # Check configured APIs
    env_vars = framework._load_env()
    configured_apis = {
        "openai": bool(env_vars.get("OPENAI_API_KEY")),
        "anthropic": bool(env_vars.get("ANTHROPIC_API_KEY")),
        "google": bool(env_vars.get("GOOGLE_API_KEY")),
        "mistral": bool(env_vars.get("MISTRAL_API_KEY")),
        "openrouter": bool(env_vars.get("OPENROUTER_API_KEY")),
        "github": bool(env_vars.get("GITHUB_TOKEN")),
        "slack": bool(env_vars.get("SLACK_BOT_TOKEN")),
        "gmail": bool(env_vars.get("GMAIL_CREDENTIALS")),
    }

    configured_count = sum(1 for v in configured_apis.values() if v)

    return {
        "dashboard": {
            "name": "Wizard Dashboard",
            "description": "Main control center for uDOS Wizard Server",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
        "features": features,
        "api_endpoints": api_endpoints,
        "api_configured": configured_apis,
        "configured_count": configured_count,
        "categories": [
            {"id": "settings", "name": "Settings", "icon": "⚙️"},
            {"id": "design", "name": "Design", "icon": "🎨"},
            {"id": "editing", "name": "Editing", "icon": "✏️"},
            {"id": "content", "name": "Content", "icon": "📄"},
            {"id": "monitoring", "name": "Monitoring", "icon": "📊"},
            {"id": "integrations", "name": "Integrations", "icon": "🔗"},
            {"id": "ai", "name": "AI", "icon": "🤖"},
            {"id": "plugins", "name": "Plugins", "icon": "📦"},
            {"id": "devops", "name": "DevOps", "icon": "🐙"},
            {"id": "infrastructure", "name": "Infrastructure", "icon": "🔌"},
        ],
    }
