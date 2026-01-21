"""
API Routes Package
==================

Blueprint modules for uDOS API endpoints.
Each module handles a specific domain of functionality.
"""

from .system import system_bp
from .files import files_bp
from .tui import tui_bp
from .settings import settings_bp
from .dashboard import dashboard_bp
from .knowledge import knowledge_bp
from .webhooks import webhooks_bp
from .map import map_bp
from .filepicker import filepicker_bp
from .docs import docs_bp
from .debug import debug_bp
from .user import bp as user_bp
from .feed import feed_bp
from .oauth import oauth_bp
from .quota import quota_bp
from .missions import missions_bp
from .ai import ai_bp
from .teledesk import teledesk_bp
from .export import export_bp

# All blueprints to register with Flask app
ALL_BLUEPRINTS = [
    system_bp,
    files_bp,
    tui_bp,
    settings_bp,
    dashboard_bp,
    knowledge_bp,
    webhooks_bp,
    map_bp,
    filepicker_bp,
    docs_bp,
    debug_bp,
    user_bp,  # User config endpoints
    feed_bp,  # Feed system endpoints
    oauth_bp,  # OAuth connection management
    quota_bp,  # API quota tracking
    missions_bp,  # Workflow missions
    ai_bp,  # AI provider testing and generation
    teledesk_bp,  # Teletext knowledge browser
    export_bp,  # PDF export and presentations
]

__all__ = [
    "system_bp",
    "files_bp",
    "tui_bp",
    "settings_bp",
    "dashboard_bp",
    "knowledge_bp",
    "webhooks_bp",
    "map_bp",
    "filepicker_bp",
    "docs_bp",
    "debug_bp",
    "user_bp",
    "feed_bp",
    "oauth_bp",
    "quota_bp",
    "missions_bp",
    "ai_bp",
    "teledesk_bp",
    "export_bp",
    "ALL_BLUEPRINTS",
]
