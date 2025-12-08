"""
Platform Integration Helpers for uDOS Webhook System

Utilities for setting up and configuring webhooks on external platforms:
- GitHub
- Slack
- Notion
- ClickUp

Each integration provides:
- Setup instructions
- Webhook URL generation
- Secret configuration
- Test payload sending
"""

from .github_integration import GitHubIntegration
from .slack_integration import SlackIntegration
from .notion_integration import NotionIntegration
from .clickup_integration import ClickUpIntegration

__all__ = [
    'GitHubIntegration',
    'SlackIntegration',
    'NotionIntegration',
    'ClickUpIntegration'
]
