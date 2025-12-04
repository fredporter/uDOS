"""
Webhook Manager for uDOS v1.2.5
Handles webhook registration, validation, and event routing.

Supports:
- GitHub webhooks (push, pull_request, release)
- Slack webhooks (slash commands, events)
- Notion webhooks (page updates, database changes)
- ClickUp webhooks (task updates, comments)
"""

import json
import hmac
import hashlib
import secrets
from pathlib import Path
from typing import Dict, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class WebhookConfig:
    """Webhook configuration."""
    id: str
    platform: str  # github, slack, notion, clickup
    url: str
    secret: str
    events: List[str]
    actions: List[Dict[str, str]]  # event → workflow mappings
    created: str
    enabled: bool = True
    last_triggered: Optional[str] = None
    trigger_count: int = 0


class WebhookManager:
    """Manages webhook registrations and event routing."""

    def __init__(self, config_path: str = "memory/system/webhooks.json"):
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.webhooks: Dict[str, WebhookConfig] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.load_config()

    def load_config(self):
        """Load webhook configurations from disk."""
        if self.config_path.exists():
            try:
                data = json.loads(self.config_path.read_text())
                for wh_data in data.get('webhooks', []):
                    wh = WebhookConfig(**wh_data)
                    self.webhooks[wh.id] = wh
            except Exception as e:
                print(f"⚠️  Error loading webhooks: {e}")

    def save_config(self):
        """Save webhook configurations to disk."""
        data = {
            'webhooks': [asdict(wh) for wh in self.webhooks.values()],
            'last_updated': datetime.now().isoformat()
        }
        self.config_path.write_text(json.dumps(data, indent=2))

    def register_webhook(self, platform: str, events: List[str],
                        actions: List[Dict[str, str]]) -> WebhookConfig:
        """
        Register a new webhook.

        Args:
            platform: Platform name (github, slack, notion, clickup)
            events: List of events to listen for
            actions: List of event → workflow mappings

        Returns:
            WebhookConfig with generated ID and secret
        """
        webhook_id = f"wh_{secrets.token_hex(8)}"
        secret = secrets.token_hex(32)
        url = f"/api/webhooks/receive/{platform}"

        webhook = WebhookConfig(
            id=webhook_id,
            platform=platform,
            url=url,
            secret=secret,
            events=events,
            actions=actions,
            created=datetime.now().isoformat(),
            enabled=True
        )

        self.webhooks[webhook_id] = webhook
        self.save_config()

        return webhook

    def get_webhook(self, webhook_id: str) -> Optional[WebhookConfig]:
        """Get webhook by ID."""
        return self.webhooks.get(webhook_id)

    def list_webhooks(self, platform: Optional[str] = None) -> List[WebhookConfig]:
        """List all webhooks, optionally filtered by platform."""
        webhooks = list(self.webhooks.values())
        if platform:
            webhooks = [wh for wh in webhooks if wh.platform == platform]
        return webhooks

    def delete_webhook(self, webhook_id: str) -> bool:
        """Delete a webhook."""
        if webhook_id in self.webhooks:
            del self.webhooks[webhook_id]
            self.save_config()
            return True
        return False

    def validate_signature_github(self, payload: bytes, signature: str,
                                  secret: str) -> bool:
        """
        Validate GitHub webhook signature.

        GitHub uses HMAC-SHA256 with format: sha256=<hash>
        """
        if not signature or not signature.startswith('sha256='):
            return False

        expected_sig = signature.split('=')[1]
        computed_sig = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(computed_sig, expected_sig)

    def validate_signature_slack(self, timestamp: str, signature: str,
                                 body: str, secret: str) -> bool:
        """
        Validate Slack webhook signature.

        Slack uses HMAC-SHA256 with format: v0=<hash>
        Basestring: v0:<timestamp>:<body>
        """
        if not signature or not signature.startswith('v0='):
            return False

        # Check timestamp freshness (5 min window)
        try:
            ts = int(timestamp)
            now = int(datetime.now().timestamp())
            if abs(now - ts) > 60 * 5:
                return False
        except ValueError:
            return False

        basestring = f"v0:{timestamp}:{body}"
        expected_sig = signature.split('=')[1]
        computed_sig = hmac.new(
            secret.encode(),
            basestring.encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(computed_sig, expected_sig)

    def validate_signature_notion(self, payload: bytes, signature: str,
                                  secret: str) -> bool:
        """
        Validate Notion webhook signature.

        Notion uses HMAC-SHA256 (format varies by implementation)
        """
        if not signature:
            return False

        computed_sig = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(computed_sig, signature)

    def validate_signature_clickup(self, payload: bytes, signature: str,
                                   secret: str) -> bool:
        """
        Validate ClickUp webhook signature.

        ClickUp uses HMAC-SHA256
        """
        if not signature:
            return False

        computed_sig = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(computed_sig, signature)

    def record_trigger(self, webhook_id: str):
        """Record that a webhook was triggered."""
        if webhook_id in self.webhooks:
            wh = self.webhooks[webhook_id]
            wh.last_triggered = datetime.now().isoformat()
            wh.trigger_count += 1
            self.save_config()

    def get_actions_for_event(self, webhook_id: str, event: str) -> List[Dict[str, str]]:
        """Get workflow actions for a specific event."""
        webhook = self.get_webhook(webhook_id)
        if not webhook or not webhook.enabled:
            return []

        return [
            action for action in webhook.actions
            if action.get('event') == event
        ]

    def register_event_handler(self, event: str, handler: Callable):
        """Register a handler function for an event type."""
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)

    def trigger_event_handlers(self, event: str, data: Dict):
        """Trigger all registered handlers for an event."""
        handlers = self.event_handlers.get(event, [])
        for handler in handlers:
            try:
                handler(data)
            except Exception as e:
                print(f"⚠️  Error in event handler for {event}: {e}")


# Global webhook manager instance
_webhook_manager = None


def get_webhook_manager() -> WebhookManager:
    """Get global webhook manager instance."""
    global _webhook_manager
    if _webhook_manager is None:
        _webhook_manager = WebhookManager()
    return _webhook_manager
