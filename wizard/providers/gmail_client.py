"""
Gmail OAuth Client - Google Gmail API Implementation
=====================================================

Actual Gmail API client using google-api-python-client.

Setup Required:
  1. Create project in Google Cloud Console
  2. Enable Gmail API
  3. Create OAuth 2.0 credentials (Desktop app)
  4. Download credentials.json to extensions/wizard_server/config/

Dependencies:
  pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

OAuth Scopes:
  - gmail.readonly - Read emails
  - gmail.send - Send emails
  - gmail.modify - Modify labels/archive
"""

import json
import base64
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from .base_provider import (
    BaseProvider,
    ProviderConfig,
    ProviderStatus,
    AuthenticationError,
    ProviderError,
)
from core.services.logging_api import get_logger

logger = get_logger("gmail-client")

# Check for Google API libraries
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
    logger.warning("[GMAIL] google-api-python-client not installed")

# OAuth scopes
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]

# Config paths
CONFIG_PATH = Path(__file__).parent.parent / "config"
CREDENTIALS_FILE = CONFIG_PATH / "gmail_credentials.json"
TOKEN_FILE = CONFIG_PATH / "gmail_token.json"


@dataclass
class EmailMessage:
    """Email message for sending."""

    to: List[str]
    subject: str
    body: str
    html: bool = False
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
    attachments: Optional[List[str]] = None


@dataclass
class EmailSummary:
    """Summary of received email."""

    id: str
    thread_id: str
    subject: str
    sender: str
    snippet: str
    date: str
    labels: List[str]


class GmailClient(BaseProvider):
    """
    Gmail API client for uDOS Wizard Server.

    Handles OAuth authentication and email operations.
    """

    def __init__(self, config: Optional[ProviderConfig] = None):
        """Initialize Gmail client."""
        if config is None:
            config = ProviderConfig(
                name="gmail",
                rate_limit_rpm=60,  # Gmail API default
            )
        super().__init__(config)

        self.credentials: Optional[Credentials] = None
        self.service = None

        # Ensure config directory exists
        CONFIG_PATH.mkdir(parents=True, exist_ok=True)

    async def authenticate(self) -> bool:
        """
        Authenticate with Gmail OAuth.

        First run requires interactive browser auth.
        Subsequent runs use stored token.
        """
        if not GOOGLE_API_AVAILABLE:
            raise AuthenticationError(
                "Google API not installed. Run: pip install google-api-python-client google-auth-oauthlib"
            )

        try:
            # Check for existing token
            if TOKEN_FILE.exists():
                self.credentials = Credentials.from_authorized_user_file(
                    str(TOKEN_FILE), SCOPES
                )

            # Refresh or get new credentials
            if not self.credentials or not self.credentials.valid:
                if (
                    self.credentials
                    and self.credentials.expired
                    and self.credentials.refresh_token
                ):
                    logger.info("[GMAIL] Refreshing expired token")
                    self.credentials.refresh(Request())
                else:
                    # Need new auth flow
                    if not CREDENTIALS_FILE.exists():
                        raise AuthenticationError(
                            f"OAuth credentials not found at {CREDENTIALS_FILE}. "
                            "Download from Google Cloud Console."
                        )

                    logger.info("[GMAIL] Starting OAuth flow")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(CREDENTIALS_FILE), SCOPES
                    )
                    # Note: run_local_server requires user interaction
                    self.credentials = flow.run_local_server(port=0)

                # Save token
                TOKEN_FILE.write_text(self.credentials.to_json())
                logger.info("[GMAIL] Token saved")

            # Build service
            self.service = build("gmail", "v1", credentials=self.credentials)
            self.status = ProviderStatus.READY

            logger.info("[GMAIL] Authentication successful")
            return True

        except Exception as e:
            logger.error(f"[GMAIL] Authentication failed: {e}")
            self.status = ProviderStatus.AUTH_REQUIRED
            raise AuthenticationError(str(e))

    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Gmail API request."""
        if not self.is_available():
            raise ProviderError("Gmail not authenticated")

        action = request.get("action", "")

        if action == "send":
            return await self._send_email(request)
        elif action == "list":
            return await self._list_messages(request)
        elif action == "get":
            return await self._get_message(request)
        elif action == "labels":
            return await self._list_labels()
        else:
            raise ProviderError(f"Unknown action: {action}")

    async def _send_email(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send an email."""
        try:
            message = self._create_message(
                to=request["to"],
                subject=request["subject"],
                body=request["body"],
                html=request.get("html", False),
            )

            result = (
                self.service.users()
                .messages()
                .send(userId="me", body=message)
                .execute()
            )

            logger.info(f"[GMAIL] Email sent: {result['id']}")
            return {
                "success": True,
                "message_id": result["id"],
                "thread_id": result.get("threadId"),
            }

        except HttpError as e:
            logger.error(f"[GMAIL] Send failed: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def _list_messages(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """List messages in mailbox."""
        try:
            query = request.get("query", "")
            max_results = request.get("max_results", 10)

            results = (
                self.service.users()
                .messages()
                .list(userId="me", q=query, maxResults=max_results)
                .execute()
            )

            messages = results.get("messages", [])
            summaries = []

            for msg in messages:
                full = (
                    self.service.users()
                    .messages()
                    .get(
                        userId="me",
                        id=msg["id"],
                        format="metadata",
                        metadataHeaders=["Subject", "From", "Date"],
                    )
                    .execute()
                )

                headers = {
                    h["name"]: h["value"]
                    for h in full.get("payload", {}).get("headers", [])
                }

                summaries.append(
                    {
                        "id": msg["id"],
                        "thread_id": full.get("threadId"),
                        "subject": headers.get("Subject", ""),
                        "sender": headers.get("From", ""),
                        "date": headers.get("Date", ""),
                        "snippet": full.get("snippet", ""),
                        "labels": full.get("labelIds", []),
                    }
                )

            return {
                "success": True,
                "count": len(summaries),
                "messages": summaries,
            }

        except HttpError as e:
            return {
                "success": False,
                "error": str(e),
            }

    async def _get_message(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get full message content."""
        try:
            msg_id = request["message_id"]

            result = (
                self.service.users()
                .messages()
                .get(userId="me", id=msg_id, format="full")
                .execute()
            )

            # Extract body
            body = self._extract_body(result.get("payload", {}))
            headers = {
                h["name"]: h["value"]
                for h in result.get("payload", {}).get("headers", [])
            }

            return {
                "success": True,
                "id": msg_id,
                "subject": headers.get("Subject", ""),
                "sender": headers.get("From", ""),
                "date": headers.get("Date", ""),
                "body": body,
                "labels": result.get("labelIds", []),
            }

        except HttpError as e:
            return {
                "success": False,
                "error": str(e),
            }

    async def _list_labels(self) -> Dict[str, Any]:
        """List Gmail labels."""
        try:
            results = self.service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])

            return {
                "success": True,
                "labels": [{"id": l["id"], "name": l["name"]} for l in labels],
            }
        except HttpError as e:
            return {
                "success": False,
                "error": str(e),
            }

    def _create_message(
        self, to: List[str], subject: str, body: str, html: bool = False
    ) -> Dict:
        """Create email message."""
        if html:
            message = MIMEMultipart("alternative")
            message.attach(MIMEText(body, "html"))
        else:
            message = MIMEText(body)

        message["to"] = ", ".join(to) if isinstance(to, list) else to
        message["subject"] = subject

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return {"raw": raw}

    def _extract_body(self, payload: Dict) -> str:
        """Extract body from message payload."""
        if "body" in payload and payload["body"].get("data"):
            return base64.urlsafe_b64decode(payload["body"]["data"]).decode()

        if "parts" in payload:
            for part in payload["parts"]:
                if part.get("mimeType") == "text/plain":
                    if part.get("body", {}).get("data"):
                        return base64.urlsafe_b64decode(part["body"]["data"]).decode()

        return ""

    def get_status(self) -> Dict[str, Any]:
        """Get Gmail client status."""
        return {
            "provider": "gmail",
            "status": self.status.value,
            "available": self.is_available(),
            "credentials_exist": CREDENTIALS_FILE.exists(),
            "token_exists": TOKEN_FILE.exists(),
            "scopes": SCOPES,
        }

    def get_oauth_url(self) -> Optional[str]:
        """Get OAuth authorization URL for manual flow."""
        if not GOOGLE_API_AVAILABLE or not CREDENTIALS_FILE.exists():
            return None

        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES, redirect_uri="urn:ietf:wg:oauth:2.0:oob"
            )
            auth_url, _ = flow.authorization_url(prompt="consent")
            return auth_url
        except Exception:
            return None


# Singleton
_client: Optional[GmailClient] = None


def get_gmail_client() -> GmailClient:
    """Get Gmail client singleton."""
    global _client
    if _client is None:
        _client = GmailClient()
    return _client


if __name__ == "__main__":
    print("Gmail OAuth Client")
    print("=" * 40)
    print(f"Google API available: {GOOGLE_API_AVAILABLE}")
    print(f"Credentials file: {CREDENTIALS_FILE}")
    print(f"Token file: {TOKEN_FILE}")
    print()
    print("Setup steps:")
    print("1. Go to console.cloud.google.com")
    print("2. Create project and enable Gmail API")
    print("3. Create OAuth credentials (Desktop app)")
    print("4. Download to extensions/wizard_server/config/gmail_credentials.json")
