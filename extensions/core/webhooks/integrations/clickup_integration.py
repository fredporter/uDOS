"""
ClickUp Webhook Integration Helper

Provides tools for setting up ClickUp webhooks to send to uDOS.

Features:
- Webhook setup instructions
- Event subscription configuration
- Test event simulation
"""

import os
import requests
from typing import Dict, Any, Optional, List


class ClickUpIntegration:
    """Helper for ClickUp webhook integration."""

    def __init__(self, server_url: str, secret: Optional[str] = None):
        """
        Initialize ClickUp integration.

        Args:
            server_url: Base URL of webhook server
            secret: Webhook secret for verification
        """
        self.server_url = server_url.rstrip('/')
        self.secret = secret or os.getenv('CLICKUP_WEBHOOK_SECRET', '')
        self.webhook_url = f"{self.server_url}/webhooks/clickup"

    def create_webhook(
        self,
        team_id: str,
        api_token: str,
        events: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create webhook via ClickUp API.

        Args:
            team_id: ClickUp team (workspace) ID
            api_token: ClickUp personal API token
            events: Events to subscribe to

        Returns:
            Created webhook data
        """
        if events is None:
            events = [
                'taskCreated',
                'taskUpdated',
                'taskDeleted',
                'taskCommentPosted',
                'taskStatusUpdated'
            ]

        url = f"https://api.clickup.com/api/v2/team/{team_id}/webhook"

        response = requests.post(
            url,
            headers={
                'Authorization': api_token,
                'Content-Type': 'application/json'
            },
            json={
                'endpoint': self.webhook_url,
                'events': events
            }
        )
        response.raise_for_status()

        return response.json()

    def get_setup_instructions(self) -> str:
        """
        Get setup instructions for ClickUp integration.

        Returns:
            Markdown-formatted setup instructions
        """
        return f"""
# ClickUp Webhook Setup

## 1. Get API Token

Go to: https://app.clickup.com/settings/apps

Click "Generate" under "API Token"

Copy token and add to `.env`:
```bash
CLICKUP_API_TOKEN=your_api_token_here
CLICKUP_WEBHOOK_SECRET=your_webhook_secret_here
```

## 2. Get Team ID

Find your team ID:
1. Go to ClickUp workspace
2. URL format: `https://app.clickup.com/TEAM_ID/`
3. Copy the team ID from URL

## 3. Create Webhook

Use Python to create webhook:

```python
from extensions.core.webhooks.integrations import ClickUpIntegration
import os

integration = ClickUpIntegration('{self.server_url}')
team_id = 'your_team_id'
token = os.getenv('CLICKUP_API_TOKEN')

webhook = integration.create_webhook(
    team_id=team_id,
    api_token=token,
    events=[
        'taskCreated',
        'taskUpdated',
        'taskStatusUpdated',
        'taskCommentPosted'
    ]
)

print(f"Webhook created: {{webhook['id']}}")
```

Or use ClickUp API directly:

```bash
curl -X POST 'https://api.clickup.com/api/v2/team/TEAM_ID/webhook' \\
  -H 'Authorization: YOUR_API_TOKEN' \\
  -H 'Content-Type: application/json' \\
  -d '{{
    "endpoint": "{self.webhook_url}",
    "events": [
      "taskCreated",
      "taskUpdated",
      "taskStatusUpdated"
    ]
  }}'
```

## 4. Supported Events

- `taskCreated` - Task created
- `taskUpdated` - Task updated
- `taskDeleted` - Task deleted
- `taskCommentPosted` - Comment added
- `taskStatusUpdated` - Status changed
- `taskPriorityUpdated` - Priority changed
- `taskAssigneeUpdated` - Assignee changed
- `taskDueDateUpdated` - Due date changed

## 5. Filter by Space/List (Optional)

Add filters to webhook:

```python
webhook = integration.create_webhook(
    team_id=team_id,
    api_token=token,
    events=['taskCreated'],
    filters={{
        'list_id': 'your_list_id',  # Only tasks from this list
        'space_id': 'your_space_id'  # Only tasks from this space
    }}
)
```

## 6. Verify in uDOS

Check webhook events:
```bash
GET /api/events?platform=clickup&limit=10
```

Or use Python client:
```python
from extensions.core.webhooks.client import WebhookClient

client = WebhookClient('{self.server_url}')
events = client.get_events(platform='clickup', limit=10)
print(f"Received {{len(events)}} ClickUp events")
```

## 7. Manage Webhooks

**List webhooks:**
```bash
curl 'https://api.clickup.com/api/v2/team/TEAM_ID/webhook' \\
  -H 'Authorization: YOUR_API_TOKEN'
```

**Delete webhook:**
```bash
curl -X DELETE 'https://api.clickup.com/api/v2/webhook/WEBHOOK_ID' \\
  -H 'Authorization: YOUR_API_TOKEN'
```

## Troubleshooting

### Webhook Not Created

- Verify API token is valid
- Check team ID is correct
- Ensure API access is enabled for workspace

### Events Not Received

- Verify webhook URL is accessible
- Check event types are subscribed
- Review ClickUp webhook logs in settings
- Ensure tasks are in subscribed spaces/lists

### Rate Limits

ClickUp API has rate limits:
- Personal token: 100 requests/minute
- OAuth app: 100 requests/minute per app

Monitor usage and implement backoff if needed.
"""

    def list_webhooks(self, team_id: str, api_token: str) -> List[Dict[str, Any]]:
        """
        List all webhooks for team.

        Args:
            team_id: ClickUp team ID
            api_token: ClickUp API token

        Returns:
            List of webhook configurations
        """
        url = f"https://api.clickup.com/api/v2/team/{team_id}/webhook"

        response = requests.get(
            url,
            headers={'Authorization': api_token}
        )
        response.raise_for_status()

        return response.json()['webhooks']

    def delete_webhook(self, webhook_id: str, api_token: str) -> bool:
        """
        Delete webhook.

        Args:
            webhook_id: Webhook ID to delete
            api_token: ClickUp API token

        Returns:
            True if successful
        """
        url = f"https://api.clickup.com/api/v2/webhook/{webhook_id}"

        response = requests.delete(
            url,
            headers={'Authorization': api_token}
        )

        return response.status_code == 200
