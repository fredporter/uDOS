"""
Notion Webhook Integration Helper

Provides tools for setting up Notion webhooks to send to uDOS.

Note: Notion webhook support is still in beta. Check official docs:
https://developers.notion.com/docs/webhooks
"""

import os
from typing import Dict, Any, Optional


class NotionIntegration:
    """Helper for Notion webhook integration."""

    def __init__(self, server_url: str, secret: Optional[str] = None):
        """
        Initialize Notion integration.

        Args:
            server_url: Base URL of webhook server
            secret: Webhook secret for verification
        """
        self.server_url = server_url.rstrip('/')
        self.secret = secret or os.getenv('NOTION_WEBHOOK_SECRET', '')
        self.webhook_url = f"{self.server_url}/webhooks/notion"

    def get_setup_instructions(self) -> str:
        """
        Get setup instructions for Notion integration.

        Returns:
            Markdown-formatted setup instructions
        """
        return f"""
# Notion Webhook Setup

## Prerequisites

- Notion workspace with admin access
- Notion integration created
- Notion API access (beta feature)

## 1. Create Notion Integration

Go to: https://www.notion.so/my-integrations

Click "New integration" and configure:
- **Name:** uDOS Webhook
- **Associated workspace:** Your workspace
- **Capabilities:**
  - [x] Read content
  - [x] Update content (optional)
  - [ ] Insert content (optional)

## 2. Get Integration Token

Copy the "Internal Integration Token" from integration settings.

Add to `.env`:
```bash
NOTION_INTEGRATION_TOKEN=your_integration_token_here
NOTION_WEBHOOK_SECRET=your_webhook_secret_here
```

## 3. Share Pages/Databases with Integration

For each page or database you want to monitor:

1. Click "..." (more menu)
2. Click "Add connections"
3. Select "uDOS Webhook"
4. Click "Confirm"

## 4. Configure Webhook (via API)

**Webhook URL:**
```
{self.webhook_url}
```

**Secret:**
```
{self.secret or '(Set NOTION_WEBHOOK_SECRET in .env)'}
```

Use Notion API to create webhook subscription:

```python
import requests

# Get integration token
token = os.getenv('NOTION_INTEGRATION_TOKEN')

# Create webhook
response = requests.post(
    'https://api.notion.com/v1/webhooks',
    headers={{
        'Authorization': f'Bearer {{token}}',
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
    }},
    json={{
        'url': '{self.webhook_url}',
        'events': [
            'page.updated',
            'page.created',
            'database.item.created',
            'database.item.updated'
        ]
    }}
)

webhook_id = response.json()['id']
print(f"Webhook created: {{webhook_id}}")
```

## 5. Supported Events

- `page.updated` - Page content changed
- `page.created` - New page created
- `database.item.created` - New database row
- `database.item.updated` - Database row updated

## 6. Verify in uDOS

Check webhook events:
```bash
GET /api/events?platform=notion&limit=10
```

Or use Python client:
```python
from extensions.core.webhooks.client import WebhookClient

client = WebhookClient('{self.server_url}')
events = client.get_events(platform='notion', limit=10)
print(f"Received {{len(events)}} Notion events")
```

## Limitations

- Notion webhooks are in beta
- Limited to pages/databases shared with integration
- Rate limits apply (check Notion API docs)

## Troubleshooting

### Webhook Not Created

- Verify integration token is valid
- Check Notion API version compatibility
- Ensure workspace has webhook beta access

### Events Not Received

- Verify pages/databases are shared with integration
- Check webhook secret matches
- Review Notion API logs
"""
