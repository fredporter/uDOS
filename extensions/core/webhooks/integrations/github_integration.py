"""
GitHub Webhook Integration Helper

Provides tools for setting up GitHub webhooks to send events to uDOS.

Features:
- Webhook URL generation
- Setup instructions
- Test event simulation
- Secret management
"""

import os
import requests
from typing import Dict, Any, Optional, List


class GitHubIntegration:
    """Helper for GitHub webhook integration."""

    def __init__(self, server_url: str, secret: Optional[str] = None):
        """
        Initialize GitHub integration.

        Args:
            server_url: Base URL of webhook server (e.g., https://your-server.com)
            secret: Webhook secret for signature verification
        """
        self.server_url = server_url.rstrip('/')
        self.secret = secret or os.getenv('GITHUB_WEBHOOK_SECRET', '')
        self.webhook_url = f"{self.server_url}/webhooks/github"

    def get_webhook_config(
        self,
        events: Optional[List[str]] = None,
        active: bool = True
    ) -> Dict[str, Any]:
        """
        Get webhook configuration for GitHub repository.

        Args:
            events: List of events to subscribe to
            active: Whether webhook is active

        Returns:
            Webhook configuration dictionary
        """
        if events is None:
            events = ['push', 'pull_request', 'issues', 'release']

        return {
            'name': 'web',
            'active': active,
            'events': events,
            'config': {
                'url': self.webhook_url,
                'content_type': 'json',
                'secret': self.secret,
                'insecure_ssl': '0'  # Require SSL
            }
        }

    def create_webhook(
        self,
        owner: str,
        repo: str,
        token: str,
        events: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create webhook on GitHub repository via API.

        Args:
            owner: Repository owner
            repo: Repository name
            token: GitHub personal access token
            events: Events to subscribe to

        Returns:
            Created webhook data
        """
        url = f"https://api.github.com/repos/{owner}/{repo}/hooks"

        config = self.get_webhook_config(events=events)

        response = requests.post(
            url,
            json=config,
            headers={
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            }
        )
        response.raise_for_status()

        return response.json()

    def get_setup_instructions(self, owner: str, repo: str) -> str:
        """
        Get setup instructions for manual webhook configuration.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Markdown-formatted setup instructions
        """
        return f"""
# GitHub Webhook Setup for {owner}/{repo}

## 1. Navigate to Webhook Settings

Go to: https://github.com/{owner}/{repo}/settings/hooks

## 2. Click "Add webhook"

## 3. Configure Webhook

**Payload URL:**
```
{self.webhook_url}
```

**Content type:**
- Select: `application/json`

**Secret:**
```
{self.secret or '(Set GITHUB_WEBHOOK_SECRET in .env)'}
```

**SSL verification:**
- Enable SSL verification

## 4. Select Events

Choose which events to trigger webhook:

- [x] Push events
- [x] Pull requests
- [x] Issues
- [x] Releases

Or select "Send me everything" for all events.

## 5. Active

- [x] Active (webhook enabled)

## 6. Click "Add webhook"

GitHub will send a test ping event to verify the webhook is working.

## 7. Verify in uDOS

Check webhook events:
```bash
# In uDOS
GET /api/events?platform=github&limit=10
```

Or use the Python client:
```python
from extensions.core.webhooks.client import WebhookClient

client = WebhookClient('{self.server_url}')
events = client.get_events(platform='github', limit=10)
print(f"Received {{len(events)}} GitHub events")
```
"""

    def send_test_event(
        self,
        owner: str,
        repo: str,
        token: str,
        hook_id: int
    ) -> bool:
        """
        Send test ping event to webhook.

        Args:
            owner: Repository owner
            repo: Repository name
            token: GitHub personal access token
            hook_id: Webhook ID

        Returns:
            True if test successful
        """
        url = f"https://api.github.com/repos/{owner}/{repo}/hooks/{hook_id}/pings"

        response = requests.post(
            url,
            headers={
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            }
        )

        return response.status_code == 204
