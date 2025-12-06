"""
Webhook Event Simulator

Generates realistic webhook payloads for testing the webhook system without
needing actual external platform events.

Supports:
- GitHub: push, pull_request, issues, release
- Slack: message, reaction_added, app_mention
- Notion: page_created, page_updated, database_updated
- ClickUp: task_created, task_updated, task_status_changed

Usage:
    from extensions.core.webhooks.simulator import WebhookSimulator

    simulator = WebhookSimulator()
    payload = simulator.generate('github', 'push')
    signature = simulator.sign_payload(payload, 'github')
"""

import hashlib
import hmac
import json
import secrets
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class SimulatedEvent:
    """Simulated webhook event with payload and signature."""
    platform: str
    event_type: str
    payload: Dict[str, Any]
    signature: str
    headers: Dict[str, str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class WebhookSimulator:
    """Generate realistic webhook payloads for testing."""

    # Default webhook secrets for testing
    DEFAULT_SECRETS = {
        'github': 'test_github_secret_12345',
        'slack': 'test_slack_secret_67890',
        'notion': 'test_notion_secret_abcde',
        'clickup': 'test_clickup_secret_fghij'
    }

    def __init__(self, secrets: Optional[Dict[str, str]] = None):
        """
        Initialize webhook simulator.

        Args:
            secrets: Custom webhook secrets by platform (uses defaults if not provided)
        """
        self.secrets = secrets or self.DEFAULT_SECRETS.copy()

    def generate(self, platform: str, event_type: str, **kwargs) -> Dict[str, Any]:
        """
        Generate webhook payload for specified platform and event type.

        Args:
            platform: Platform name (github, slack, notion, clickup)
            event_type: Event type (push, pull_request, message, etc.)
            **kwargs: Additional parameters for payload customization

        Returns:
            Simulated webhook payload dictionary

        Raises:
            ValueError: If platform or event_type is not supported
        """
        platform = platform.lower()
        generator_method = f"_generate_{platform}_{event_type}"

        if not hasattr(self, generator_method):
            raise ValueError(
                f"Unsupported event: {platform}.{event_type}. "
                f"Available: {', '.join(self.get_supported_events(platform))}"
            )

        return getattr(self, generator_method)(**kwargs)

    def generate_with_signature(self, platform: str, event_type: str, **kwargs) -> SimulatedEvent:
        """
        Generate webhook payload with valid signature and headers.

        Args:
            platform: Platform name
            event_type: Event type
            **kwargs: Additional parameters for payload customization

        Returns:
            SimulatedEvent with payload, signature, and headers
        """
        payload = self.generate(platform, event_type, **kwargs)
        signature = self.sign_payload(payload, platform)
        headers = self._get_headers(platform, event_type, signature)

        return SimulatedEvent(
            platform=platform,
            event_type=event_type,
            payload=payload,
            signature=signature,
            headers=headers
        )

    def sign_payload(self, payload: Dict[str, Any], platform: str) -> str:
        """
        Generate HMAC signature for payload.

        Args:
            payload: Webhook payload dictionary
            platform: Platform name

        Returns:
            HMAC signature string (format varies by platform)
        """
        secret = self.secrets.get(platform, '')
        payload_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')

        if platform == 'github':
            signature = hmac.new(secret.encode(), payload_bytes, hashlib.sha256).hexdigest()
            return f"sha256={signature}"
        elif platform == 'slack':
            # Slack uses timestamp + payload for signature
            timestamp = str(int(datetime.now(timezone.utc).timestamp()))
            sig_base = f"v0:{timestamp}:{payload_bytes.decode()}"
            signature = hmac.new(secret.encode(), sig_base.encode(), hashlib.sha256).hexdigest()
            return f"v0={signature}"
        else:
            # Generic HMAC-SHA256
            signature = hmac.new(secret.encode(), payload_bytes, hashlib.sha256).hexdigest()
            return signature

    def _get_headers(self, platform: str, event_type: str, signature: str) -> Dict[str, str]:
        """Get platform-specific headers for webhook request."""
        headers = {'Content-Type': 'application/json'}

        if platform == 'github':
            headers['X-GitHub-Event'] = event_type
            headers['X-Hub-Signature-256'] = signature
            headers['X-GitHub-Delivery'] = secrets.token_hex(20)
        elif platform == 'slack':
            headers['X-Slack-Signature'] = signature
            headers['X-Slack-Request-Timestamp'] = str(int(datetime.now(timezone.utc).timestamp()))
        elif platform == 'notion':
            headers['Notion-Webhook-Signature'] = signature
        elif platform == 'clickup':
            headers['X-ClickUp-Signature'] = signature

        return headers

    def get_supported_events(self, platform: Optional[str] = None) -> List[str]:
        """
        Get list of supported event types.

        Args:
            platform: Platform name (returns all if None)

        Returns:
            List of supported event type strings
        """
        all_events = {
            'github': ['push', 'pull_request', 'issues', 'release'],
            'slack': ['message', 'reaction_added', 'app_mention'],
            'notion': ['page_created', 'page_updated', 'database_updated'],
            'clickup': ['task_created', 'task_updated', 'task_status_changed']
        }

        if platform:
            return all_events.get(platform.lower(), [])

        return [f"{plat}.{evt}" for plat, events in all_events.items() for evt in events]

    # GitHub Event Generators

    def _generate_github_push(self, ref: str = "refs/heads/main", **kwargs) -> Dict[str, Any]:
        """Generate GitHub push event payload."""
        return {
            "ref": ref,
            "before": secrets.token_hex(20),
            "after": secrets.token_hex(20),
            "repository": {
                "id": 123456789,
                "name": kwargs.get('repo_name', 'test-repo'),
                "full_name": f"{kwargs.get('owner', 'testuser')}/{kwargs.get('repo_name', 'test-repo')}",
                "owner": {
                    "name": kwargs.get('owner', 'testuser'),
                    "email": kwargs.get('email', 'test@example.com')
                }
            },
            "pusher": {
                "name": kwargs.get('pusher', 'testuser'),
                "email": kwargs.get('email', 'test@example.com')
            },
            "commits": [
                {
                    "id": secrets.token_hex(20),
                    "message": kwargs.get('commit_message', 'Test commit'),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "author": {
                        "name": kwargs.get('author', 'Test User'),
                        "email": kwargs.get('email', 'test@example.com')
                    }
                }
            ]
        }

    def _generate_github_pull_request(self, action: str = "opened", **kwargs) -> Dict[str, Any]:
        """Generate GitHub pull_request event payload."""
        return {
            "action": action,
            "number": kwargs.get('pr_number', 42),
            "pull_request": {
                "id": 987654321,
                "number": kwargs.get('pr_number', 42),
                "state": "open",
                "title": kwargs.get('pr_title', 'Test Pull Request'),
                "body": kwargs.get('pr_body', 'This is a test PR'),
                "user": {
                    "login": kwargs.get('user', 'testuser'),
                    "id": 12345
                },
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "head": {
                    "ref": kwargs.get('head_ref', 'feature-branch'),
                    "sha": secrets.token_hex(20)
                },
                "base": {
                    "ref": kwargs.get('base_ref', 'main'),
                    "sha": secrets.token_hex(20)
                }
            },
            "repository": {
                "id": 123456789,
                "name": kwargs.get('repo_name', 'test-repo'),
                "full_name": f"{kwargs.get('owner', 'testuser')}/{kwargs.get('repo_name', 'test-repo')}"
            }
        }

    def _generate_github_issues(self, action: str = "opened", **kwargs) -> Dict[str, Any]:
        """Generate GitHub issues event payload."""
        return {
            "action": action,
            "issue": {
                "id": 111222333,
                "number": kwargs.get('issue_number', 123),
                "title": kwargs.get('issue_title', 'Test Issue'),
                "body": kwargs.get('issue_body', 'This is a test issue'),
                "state": "open",
                "user": {
                    "login": kwargs.get('user', 'testuser'),
                    "id": 12345
                },
                "labels": kwargs.get('labels', []),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            "repository": {
                "id": 123456789,
                "name": kwargs.get('repo_name', 'test-repo'),
                "full_name": f"{kwargs.get('owner', 'testuser')}/{kwargs.get('repo_name', 'test-repo')}"
            }
        }

    def _generate_github_release(self, action: str = "published", **kwargs) -> Dict[str, Any]:
        """Generate GitHub release event payload."""
        return {
            "action": action,
            "release": {
                "id": 444555666,
                "tag_name": kwargs.get('tag', 'v1.0.0'),
                "name": kwargs.get('release_name', 'Release v1.0.0'),
                "body": kwargs.get('release_notes', 'Test release notes'),
                "draft": False,
                "prerelease": kwargs.get('prerelease', False),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "published_at": datetime.now(timezone.utc).isoformat()
            },
            "repository": {
                "id": 123456789,
                "name": kwargs.get('repo_name', 'test-repo'),
                "full_name": f"{kwargs.get('owner', 'testuser')}/{kwargs.get('repo_name', 'test-repo')}"
            }
        }

    # Slack Event Generators

    def _generate_slack_message(self, **kwargs) -> Dict[str, Any]:
        """Generate Slack message event payload."""
        return {
            "token": "test_verification_token",
            "team_id": "T12345678",
            "event": {
                "type": "message",
                "channel": kwargs.get('channel', 'C12345678'),
                "user": kwargs.get('user', 'U12345678'),
                "text": kwargs.get('text', 'Test message'),
                "ts": str(datetime.now(timezone.utc).timestamp())
            },
            "type": "event_callback",
            "event_id": secrets.token_hex(16),
            "event_time": int(datetime.now(timezone.utc).timestamp())
        }

    def _generate_slack_reaction_added(self, **kwargs) -> Dict[str, Any]:
        """Generate Slack reaction_added event payload."""
        return {
            "token": "test_verification_token",
            "team_id": "T12345678",
            "event": {
                "type": "reaction_added",
                "user": kwargs.get('user', 'U12345678'),
                "reaction": kwargs.get('reaction', 'thumbsup'),
                "item": {
                    "type": "message",
                    "channel": kwargs.get('channel', 'C12345678'),
                    "ts": str(datetime.now(timezone.utc).timestamp())
                },
                "event_ts": str(datetime.now(timezone.utc).timestamp())
            },
            "type": "event_callback",
            "event_id": secrets.token_hex(16),
            "event_time": int(datetime.now(timezone.utc).timestamp())
        }

    def _generate_slack_app_mention(self, **kwargs) -> Dict[str, Any]:
        """Generate Slack app_mention event payload."""
        return {
            "token": "test_verification_token",
            "team_id": "T12345678",
            "event": {
                "type": "app_mention",
                "user": kwargs.get('user', 'U12345678'),
                "text": kwargs.get('text', '<@U87654321> test mention'),
                "channel": kwargs.get('channel', 'C12345678'),
                "ts": str(datetime.now(timezone.utc).timestamp())
            },
            "type": "event_callback",
            "event_id": secrets.token_hex(16),
            "event_time": int(datetime.now(timezone.utc).timestamp())
        }

    # Notion Event Generators

    def _generate_notion_page_created(self, **kwargs) -> Dict[str, Any]:
        """Generate Notion page_created event payload."""
        return {
            "object": "event",
            "type": "page.created",
            "page": {
                "id": kwargs.get('page_id', secrets.token_hex(16)),
                "created_time": datetime.now(timezone.utc).isoformat(),
                "last_edited_time": datetime.now(timezone.utc).isoformat(),
                "properties": {
                    "title": {
                        "title": [{"text": {"content": kwargs.get('title', 'Test Page')}}]
                    }
                }
            }
        }

    def _generate_notion_page_updated(self, **kwargs) -> Dict[str, Any]:
        """Generate Notion page_updated event payload."""
        return {
            "object": "event",
            "type": "page.updated",
            "page": {
                "id": kwargs.get('page_id', secrets.token_hex(16)),
                "created_time": datetime.now(timezone.utc).isoformat(),
                "last_edited_time": datetime.now(timezone.utc).isoformat(),
                "properties": {
                    "title": {
                        "title": [{"text": {"content": kwargs.get('title', 'Updated Page')}}]
                    }
                }
            }
        }

    def _generate_notion_database_updated(self, **kwargs) -> Dict[str, Any]:
        """Generate Notion database_updated event payload."""
        return {
            "object": "event",
            "type": "database.updated",
            "database": {
                "id": kwargs.get('database_id', secrets.token_hex(16)),
                "created_time": datetime.now(timezone.utc).isoformat(),
                "last_edited_time": datetime.now(timezone.utc).isoformat(),
                "title": [{"text": {"content": kwargs.get('title', 'Test Database')}}]
            }
        }

    # ClickUp Event Generators

    def _generate_clickup_task_created(self, **kwargs) -> Dict[str, Any]:
        """Generate ClickUp task_created event payload."""
        return {
            "event": "taskCreated",
            "task_id": kwargs.get('task_id', secrets.token_hex(12)),
            "webhook_id": secrets.token_hex(16),
            "history_items": [
                {
                    "id": secrets.token_hex(16),
                    "type": 1,
                    "date": str(int(datetime.now(timezone.utc).timestamp() * 1000)),
                    "field": "status",
                    "parent_id": kwargs.get('task_id', secrets.token_hex(12)),
                    "data": {
                        "status_type": "custom"
                    },
                    "source": None,
                    "user": {
                        "id": 12345,
                        "username": kwargs.get('user', 'testuser'),
                        "email": kwargs.get('email', 'test@example.com')
                    }
                }
            ]
        }

    def _generate_clickup_task_updated(self, **kwargs) -> Dict[str, Any]:
        """Generate ClickUp task_updated event payload."""
        return {
            "event": "taskUpdated",
            "task_id": kwargs.get('task_id', secrets.token_hex(12)),
            "webhook_id": secrets.token_hex(16),
            "history_items": [
                {
                    "id": secrets.token_hex(16),
                    "type": 1,
                    "date": str(int(datetime.now(timezone.utc).timestamp() * 1000)),
                    "field": kwargs.get('field', 'name'),
                    "parent_id": kwargs.get('task_id', secrets.token_hex(12)),
                    "data": {
                        "old": kwargs.get('old_value', 'Old Task Name'),
                        "new": kwargs.get('new_value', 'Updated Task Name')
                    },
                    "user": {
                        "id": 12345,
                        "username": kwargs.get('user', 'testuser'),
                        "email": kwargs.get('email', 'test@example.com')
                    }
                }
            ]
        }

    def _generate_clickup_task_status_changed(self, **kwargs) -> Dict[str, Any]:
        """Generate ClickUp task_status_changed event payload."""
        return {
            "event": "taskStatusUpdated",
            "task_id": kwargs.get('task_id', secrets.token_hex(12)),
            "webhook_id": secrets.token_hex(16),
            "history_items": [
                {
                    "id": secrets.token_hex(16),
                    "type": 1,
                    "date": str(int(datetime.now(timezone.utc).timestamp() * 1000)),
                    "field": "status",
                    "parent_id": kwargs.get('task_id', secrets.token_hex(12)),
                    "data": {
                        "status_type": kwargs.get('status_type', 'custom'),
                        "old_status": kwargs.get('old_status', 'to do'),
                        "new_status": kwargs.get('new_status', 'in progress')
                    },
                    "user": {
                        "id": 12345,
                        "username": kwargs.get('user', 'testuser'),
                        "email": kwargs.get('email', 'test@example.com')
                    }
                }
            ]
        }
