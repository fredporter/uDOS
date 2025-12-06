"""
Slack Webhook Integration Helper

Provides tools for setting up Slack webhooks/events to send to uDOS.

Features:
- App configuration guidance
- Event subscription setup
- Request URL verification
- Test event simulation
"""

import os
import json
import requests
from typing import Dict, Any, Optional, List


class SlackIntegration:
    """Helper for Slack webhook integration."""

    def __init__(self, server_url: str, signing_secret: Optional[str] = None):
        """
        Initialize Slack integration.

        Args:
            server_url: Base URL of webhook server
            signing_secret: Slack signing secret for request verification
        """
        self.server_url = server_url.rstrip('/')
        self.signing_secret = signing_secret or os.getenv('SLACK_SIGNING_SECRET', '')
        self.webhook_url = f"{self.server_url}/webhooks/slack"

    def get_app_manifest(self, app_name: str = "uDOS Webhook") -> Dict[str, Any]:
        """
        Get Slack app manifest for easy setup.

        Args:
            app_name: Name of Slack app

        Returns:
            App manifest dictionary
        """
        return {
            "display_information": {
                "name": app_name,
                "description": "Send Slack events to uDOS webhook system",
                "background_color": "#2c2d30"
            },
            "features": {
                "bot_user": {
                    "display_name": app_name,
                    "always_online": True
                }
            },
            "oauth_config": {
                "scopes": {
                    "bot": [
                        "channels:history",
                        "channels:read",
                        "chat:write",
                        "reactions:read",
                        "app_mentions:read"
                    ]
                }
            },
            "settings": {
                "event_subscriptions": {
                    "request_url": self.webhook_url,
                    "bot_events": [
                        "message.channels",
                        "reaction_added",
                        "app_mention"
                    ]
                },
                "interactivity": {
                    "is_enabled": False
                },
                "org_deploy_enabled": False,
                "socket_mode_enabled": False,
                "token_rotation_enabled": False
            }
        }

    def get_setup_instructions(self, workspace: str = "your-workspace") -> str:
        """
        Get setup instructions for Slack integration.

        Args:
            workspace: Slack workspace name

        Returns:
            Markdown-formatted setup instructions
        """
        return f"""
# Slack Webhook Setup for {workspace}

## 1. Create Slack App

Go to: https://api.slack.com/apps

Click "Create New App" → "From an app manifest"

## 2. Paste App Manifest

```json
{json.dumps(self.get_app_manifest(), indent=2)}
```

Or configure manually:

## 3. Enable Event Subscriptions

**Settings > Event Subscriptions**

- Toggle "Enable Events" to ON

**Request URL:**
```
{self.webhook_url}
```

Slack will verify this URL. Ensure your webhook server is running!

## 4. Subscribe to Bot Events

Add these bot events:
- `message.channels` - Messages in public channels
- `reaction_added` - Reactions added to messages
- `app_mention` - Bot mentioned in message

## 5. Subscribe to Workspace Events (Optional)

- `channel_created` - New channel created
- `user_change` - User profile updated

## 6. Install App to Workspace

**Settings > Install App**

Click "Install to Workspace" and authorize.

## 7. Get Signing Secret

**Settings > Basic Information > App Credentials**

Copy "Signing Secret" and add to `.env`:

```bash
SLACK_SIGNING_SECRET=your_signing_secret_here
```

## 8. Invite Bot to Channels

In Slack, invite bot to channels you want to monitor:

```
/invite @uDOS Webhook
```

## 9. Verify in uDOS

Check webhook events:
```bash
# In uDOS
GET /api/events?platform=slack&limit=10
```

Or use Python client:
```python
from extensions.core.webhooks.client import WebhookClient

client = WebhookClient('{self.server_url}')
events = client.get_events(platform='slack', limit=10)
print(f"Received {{len(events)}} Slack events")
```

## Troubleshooting

### URL Verification Failed

Slack sends a challenge parameter on first setup. The webhook server automatically handles this, but ensure:
1. Server is running and accessible
2. URL is correct and uses HTTPS in production
3. No firewall blocking requests

### Events Not Received

1. Check bot is invited to channel
2. Verify event types are subscribed
3. Check signing secret matches
4. Review Slack app event logs
"""

    def verify_url_challenge(self, challenge: str) -> Dict[str, str]:
        """
        Handle Slack URL verification challenge.

        Args:
            challenge: Challenge string from Slack

        Returns:
            Challenge response
        """
        return {"challenge": challenge}
