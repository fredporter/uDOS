"""
Event Normalization Engine for uDOS Webhook System

Converts platform-specific webhook payloads into unified uDOS event format.

Supported Platforms:
- GitHub: push, pull_request, issues, release
- Slack: message, reaction_added, slash_command
- Notion: page_updated, database_item_changed
- ClickUp: task_updated, task_created, comment_posted

Event Format:
{
    "event_id": "unique-uuid",
    "platform": "github|slack|notion|clickup",
    "event_type": "normalized-type",
    "timestamp": "ISO-8601",
    "source": {
        "platform": "github",
        "repository": "owner/repo",
        "sender": "username"
    },
    "payload": {
        # Normalized platform-agnostic fields
    },
    "raw": {
        # Original webhook payload
    }
}
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class EventProcessor:
    """Normalize webhook payloads from multiple platforms."""

    # Platform-specific event type mappings
    EVENT_TYPE_MAP = {
        'github': {
            'push': 'code.pushed',
            'pull_request.opened': 'code.pull_request.opened',
            'pull_request.closed': 'code.pull_request.closed',
            'issues.opened': 'issue.created',
            'issues.closed': 'issue.closed',
            'release.published': 'release.published',
            'star.created': 'repository.starred',
        },
        'slack': {
            'message': 'message.posted',
            'reaction_added': 'message.reacted',
            'app_mention': 'message.mentioned',
            'slash_command': 'command.invoked',
        },
        'notion': {
            'page.updated': 'page.updated',
            'page.created': 'page.created',
            'database.item.created': 'database.item.created',
            'database.item.updated': 'database.item.updated',
        },
        'clickup': {
            'taskCreated': 'task.created',
            'taskUpdated': 'task.updated',
            'taskDeleted': 'task.deleted',
            'taskCommentPosted': 'task.comment.posted',
            'taskStatusUpdated': 'task.status.changed',
        }
    }

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize event processor.

        Args:
            config_path: Path to webhook configuration file
        """
        self.config = self._load_config(config_path)
        self.stats = {
            'processed': 0,
            'errors': 0,
            'by_platform': {}
        }

    def _load_config(self, config_path: Optional[Path]) -> Dict[str, Any]:
        """Load webhook configuration."""
        if config_path and config_path.exists():
            with open(config_path) as f:
                return json.load(f)

        # Default configuration
        return {
            'enabled_platforms': ['github', 'slack', 'notion', 'clickup'],
            'event_filters': {},
            'custom_mappings': {}
        }

    def process(self, platform: str, raw_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize a webhook payload.

        Args:
            platform: Platform identifier (github, slack, notion, clickup)
            raw_payload: Raw webhook payload from platform

        Returns:
            Normalized uDOS event dictionary

        Raises:
            ValueError: If platform is not supported
        """
        platform = platform.lower()
        if platform not in self.EVENT_TYPE_MAP:
            raise ValueError(f"Unsupported platform: {platform}")

        # Generate unique event ID
        event_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

        # Route to platform-specific normalizer
        normalizer = getattr(self, f'_normalize_{platform}', None)
        if not normalizer:
            raise ValueError(f"No normalizer for platform: {platform}")

        try:
            normalized = normalizer(raw_payload)

            # Build unified event
            event = {
                'event_id': event_id,
                'platform': platform,
                'event_type': normalized['event_type'],
                'timestamp': timestamp,
                'source': normalized['source'],
                'payload': normalized['payload'],
                'raw': raw_payload
            }

            # Update statistics
            self.stats['processed'] += 1
            self.stats['by_platform'][platform] = \
                self.stats['by_platform'].get(platform, 0) + 1

            logger.info(f"Processed {platform} event: {event['event_type']}")
            return event

        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Error processing {platform} event: {e}")
            raise

    def _normalize_github(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize GitHub webhook payload."""
        # Determine event type from headers (passed in payload)
        gh_event = payload.get('headers', {}).get('X-GitHub-Event', 'unknown')
        action = payload.get('action', '')

        # Map to uDOS event type
        event_key = f"{gh_event}.{action}" if action else gh_event
        event_type = self.EVENT_TYPE_MAP['github'].get(
            event_key,
            f"github.{gh_event}"
        )

        # Extract common fields
        repo = payload.get('repository', {})
        sender = payload.get('sender', {})

        return {
            'event_type': event_type,
            'source': {
                'platform': 'github',
                'repository': repo.get('full_name', 'unknown'),
                'sender': sender.get('login', 'unknown'),
                'url': repo.get('html_url', '')
            },
            'payload': {
                'title': payload.get('pull_request', {}).get('title') or
                         payload.get('issue', {}).get('title') or
                         payload.get('release', {}).get('name') or
                         payload.get('commits', [{}])[0].get('message', 'No title'),
                'description': payload.get('pull_request', {}).get('body') or
                              payload.get('issue', {}).get('body') or '',
                'url': payload.get('pull_request', {}).get('html_url') or
                       payload.get('issue', {}).get('html_url') or
                       payload.get('release', {}).get('html_url') or
                       payload.get('compare', ''),
                'state': payload.get('pull_request', {}).get('state') or
                        payload.get('issue', {}).get('state') or 'open',
                'author': sender.get('login', 'unknown')
            }
        }

    def _normalize_slack(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Slack webhook payload."""
        event_data = payload.get('event', payload)
        event_subtype = event_data.get('type', 'unknown')

        event_type = self.EVENT_TYPE_MAP['slack'].get(
            event_subtype,
            f"slack.{event_subtype}"
        )

        user = event_data.get('user', 'unknown')
        channel = event_data.get('channel', 'unknown')

        return {
            'event_type': event_type,
            'source': {
                'platform': 'slack',
                'workspace': payload.get('team_id', 'unknown'),
                'channel': channel,
                'sender': user
            },
            'payload': {
                'text': event_data.get('text', ''),
                'timestamp': event_data.get('ts', ''),
                'channel_type': event_data.get('channel_type', 'unknown'),
                'thread_ts': event_data.get('thread_ts'),
                'reaction': event_data.get('reaction')  # For reaction_added events
            }
        }

    def _normalize_notion(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Notion webhook payload."""
        event_type_raw = payload.get('type', 'unknown')
        event_type = self.EVENT_TYPE_MAP['notion'].get(
            event_type_raw,
            f"notion.{event_type_raw}"
        )

        page_data = payload.get('data', {})

        return {
            'event_type': event_type,
            'source': {
                'platform': 'notion',
                'workspace': payload.get('workspace_id', 'unknown'),
                'page_id': page_data.get('id', 'unknown'),
                'sender': payload.get('user_id', 'unknown')
            },
            'payload': {
                'title': page_data.get('properties', {}).get('title', {}).get('title', [{}])[0].get('plain_text', 'Untitled'),
                'page_type': page_data.get('object', 'page'),
                'url': page_data.get('url', ''),
                'last_edited': page_data.get('last_edited_time', ''),
                'properties': page_data.get('properties', {})
            }
        }

    def _normalize_clickup(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize ClickUp webhook payload."""
        event_type_raw = payload.get('event', 'unknown')
        event_type = self.EVENT_TYPE_MAP['clickup'].get(
            event_type_raw,
            f"clickup.{event_type_raw}"
        )

        task_data = payload.get('task_id') and payload or payload.get('history_items', [{}])[0]

        return {
            'event_type': event_type,
            'source': {
                'platform': 'clickup',
                'workspace': payload.get('webhook_id', 'unknown'),
                'task_id': task_data.get('task_id', 'unknown'),
                'sender': task_data.get('user', {}).get('username', 'unknown')
            },
            'payload': {
                'title': task_data.get('name', 'Untitled Task'),
                'status': task_data.get('status', {}).get('status', 'unknown'),
                'url': task_data.get('url', ''),
                'description': task_data.get('description', ''),
                'assignees': [a.get('username') for a in task_data.get('assignees', [])],
                'priority': task_data.get('priority', {}).get('priority', 'normal')
            }
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return self.stats.copy()

    def reset_stats(self):
        """Reset processing statistics."""
        self.stats = {
            'processed': 0,
            'errors': 0,
            'by_platform': {}
        }
