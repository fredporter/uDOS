"""
Gmail Relay - Email Service for User Devices
=============================================

Provides email send/receive capabilities for user devices
through the Wizard Server's OAuth-authenticated Gmail API.

Features:
  - Send emails on behalf of devices
  - Receive and forward emails to devices
  - Email-to-knowledge pipeline
  - Rate limiting per device
  - Audit logging

Security:
  - OAuth 2.0 authentication (Wizard holds tokens)
  - User devices never see credentials
  - Allowlist for recipient domains
  - Content scanning for safety

Note: This is WIZARD-ONLY functionality.
User devices request email operations via private transport.
"""

import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

from wizard.services.logging_manager import get_logger

logger = get_logger("gmail-relay")

# Configuration paths
CONFIG_PATH = Path(__file__).parent / "config"
CREDENTIALS_PATH = CONFIG_PATH / "gmail_credentials.json"
TOKEN_PATH = CONFIG_PATH / "gmail_token.json"


class GmailStatus(Enum):
    """Gmail relay status."""

    NOT_CONFIGURED = "not_configured"
    AUTHENTICATED = "authenticated"
    TOKEN_EXPIRED = "token_expired"
    ERROR = "error"


@dataclass
class EmailMessage:
    """Email message structure."""

    to: List[str]
    subject: str
    body: str
    from_name: str = "uDOS Wizard"
    cc: List[str] = None
    bcc: List[str] = None
    html: bool = False
    attachments: List[str] = None

    def __post_init__(self):
        if self.cc is None:
            self.cc = []
        if self.bcc is None:
            self.bcc = []
        if self.attachments is None:
            self.attachments = []


@dataclass
class EmailResult:
    """Result of email operation."""

    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class GmailRelay:
    """
    Gmail relay service for uDOS.

    Handles email operations through Google OAuth API.
    Only runs on Wizard Server (has web access).
    """

    # Rate limits
    MAX_EMAILS_PER_DAY = 100
    MAX_RECIPIENTS_PER_EMAIL = 10

    # Allowlisted domains (empty = allow all)
    ALLOWED_DOMAINS: List[str] = []

    def __init__(self):
        """Initialize Gmail relay."""
        self.status = GmailStatus.NOT_CONFIGURED
        self.credentials_path = CREDENTIALS_PATH
        self.token_path = TOKEN_PATH
        self.service = None

        # Stats
        self.emails_sent_today = 0
        self.last_reset = datetime.now().date()

        # Check configuration
        self._check_config()

    def _check_config(self):
        """Check if Gmail is configured."""
        if not self.credentials_path.exists():
            logger.info("[GMAIL] Not configured - credentials.json missing")
            self.status = GmailStatus.NOT_CONFIGURED
            return

        if not self.token_path.exists():
            logger.info("[GMAIL] Not authenticated - need OAuth flow")
            self.status = GmailStatus.NOT_CONFIGURED
            return

        # TODO: Validate token
        self.status = GmailStatus.AUTHENTICATED
        logger.info("[GMAIL] Relay configured and ready")

    def is_available(self) -> bool:
        """Check if Gmail relay is available."""
        return self.status == GmailStatus.AUTHENTICATED

    def get_status(self) -> Dict[str, Any]:
        """Get relay status."""
        return {
            "status": self.status.value,
            "configured": self.credentials_path.exists(),
            "authenticated": self.status == GmailStatus.AUTHENTICATED,
            "emails_sent_today": self.emails_sent_today,
            "daily_limit": self.MAX_EMAILS_PER_DAY,
            "remaining": self.MAX_EMAILS_PER_DAY - self.emails_sent_today,
        }

    async def send_email(self, message: EmailMessage, device_id: str) -> EmailResult:
        """
        Send email on behalf of a device.

        Args:
            message: Email message to send
            device_id: ID of requesting device

        Returns:
            EmailResult with status
        """
        # Check availability
        if not self.is_available():
            return EmailResult(
                success=False, error=f"Gmail relay not available: {self.status.value}"
            )

        # Check rate limit
        self._check_rate_limit()
        if self.emails_sent_today >= self.MAX_EMAILS_PER_DAY:
            return EmailResult(
                success=False,
                error=f"Daily email limit reached ({self.MAX_EMAILS_PER_DAY})",
            )

        # Validate recipients
        if len(message.to) > self.MAX_RECIPIENTS_PER_EMAIL:
            return EmailResult(
                success=False,
                error=f"Too many recipients (max {self.MAX_RECIPIENTS_PER_EMAIL})",
            )

        # Check domain allowlist
        if self.ALLOWED_DOMAINS:
            for recipient in message.to + message.cc + message.bcc:
                domain = recipient.split("@")[-1] if "@" in recipient else ""
                if domain not in self.ALLOWED_DOMAINS:
                    return EmailResult(
                        success=False, error=f"Recipient domain not allowed: {domain}"
                    )

        # TODO: Actually send via Gmail API
        logger.info(f"[GMAIL] Would send email to {message.to} from device {device_id}")

        # Placeholder - actual implementation needs google-api-python-client
        return EmailResult(
            success=False,
            error="Gmail API not yet implemented - install google-api-python-client",
        )

    def _check_rate_limit(self):
        """Reset daily counter if needed."""
        today = datetime.now().date()
        if today != self.last_reset:
            self.emails_sent_today = 0
            self.last_reset = today

    async def check_inbox(self, device_id: str, max_results: int = 10) -> List[Dict]:
        """
        Check inbox for new messages.

        Args:
            device_id: Requesting device
            max_results: Maximum messages to return

        Returns:
            List of message summaries
        """
        if not self.is_available():
            return []

        # TODO: Implement inbox checking
        logger.info(f"[GMAIL] Would check inbox for device {device_id}")
        return []

    def setup_oauth(self) -> str:
        """
        Start OAuth setup flow.

        Returns:
            Authorization URL to visit
        """
        # TODO: Generate OAuth URL
        return "https://accounts.google.com/o/oauth2/v2/auth?..."


# Singleton instance
_relay: Optional[GmailRelay] = None


def get_gmail_relay() -> GmailRelay:
    """Get Gmail relay singleton."""
    global _relay
    if _relay is None:
        _relay = GmailRelay()
    return _relay
