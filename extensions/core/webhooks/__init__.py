"""
uDOS Webhook Integration System

Provides unified event processing for external platform webhooks:
- GitHub (push, PR, issues, releases)
- Slack (messages, reactions, commands)
- Notion (page updates, database changes)
- ClickUp (task updates, comments, status changes)

Components:
- EventProcessor: Normalizes platform-specific payloads
- EventRouter: Routes events to handlers and scripts
- EventSimulator: Testing and development tool
"""

from .event_processor import EventProcessor
from .event_router import EventRouter

__all__ = ['EventProcessor', 'EventRouter']
__version__ = '1.2.10'
