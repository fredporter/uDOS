"""
Slack Web API Service
======================

Integration with Slack Web API for sending notifications, managing channels,
and thread-based communication.

Features:
  - Send messages to channels or direct messages
  - List available channels
  - Reply in threads
  - Upload files
  - Configuration validation

Security:
  - Bot token stored in environment or secret store
  - Rate limiting applied
  - Message validation
  - Webhook signature verification (future)
"""

import json
import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import asyncio

try:
    import aiohttp
except ImportError:
    aiohttp = None


@dataclass
class SlackConfig:
    """Slack configuration."""

    bot_token: Optional[str] = None
    webhook_url: Optional[str] = None
    default_channel: str = "#notifications"
    message_thread_ts: Optional[str] = None
    rate_limit_per_minute: int = 20
    timeout_seconds: int = 10

    @classmethod
    def from_env(cls) -> "SlackConfig":
        """Load config from environment variables."""
        return cls(
            bot_token=os.getenv("SLACK_BOT_TOKEN"),
            webhook_url=os.getenv("SLACK_WEBHOOK_URL"),
            default_channel=os.getenv("SLACK_DEFAULT_CHANNEL", "#notifications"),
        )

    def is_configured(self) -> bool:
        """Check if Slack is properly configured."""
        return bool(self.bot_token or self.webhook_url)


class SlackService:
    """Slack Web API client."""

    def __init__(self, config: SlackConfig):
        self.config = config
        self.base_url = "https://slack.com/api"
        self.headers = {
            "Authorization": f"Bearer {config.bot_token}",
            "Content-Type": "application/json",
        }
        self.message_count = 0
        self.last_reset = datetime.now()

    async def _check_rate_limit(self) -> bool:
        """Check if rate limit is exceeded."""
        now = datetime.now()
        if (now - self.last_reset).total_seconds() > 60:
            self.message_count = 0
            self.last_reset = now

        if self.message_count >= self.config.rate_limit_per_minute:
            return False

        self.message_count += 1
        return True

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request to Slack API."""
        if not aiohttp:
            raise RuntimeError("aiohttp not installed")

        if not await self._check_rate_limit():
            return {"ok": False, "error": "rate_limited"}

        url = f"{self.base_url}/{endpoint}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method,
                    url,
                    json=data,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(
                        total=self.config.timeout_seconds
                    ),
                ) as response:
                    result = await response.json()
                    return result
        except asyncio.TimeoutError:
            return {"ok": False, "error": "timeout"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    async def send_message(
        self,
        text: str,
        channel: Optional[str] = None,
        title: Optional[str] = None,
        blocks: Optional[List[Dict]] = None,
        thread_ts: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a message to Slack.

        Args:
            text: Plain text message
            channel: Channel ID or name (default: #notifications)
            title: Optional message title
            blocks: Rich formatting blocks
            thread_ts: Thread timestamp for threaded replies

        Returns:
            API response with ts (timestamp) if successful
        """
        if not self.config.bot_token:
            return {"ok": False, "error": "not_configured"}

        payload: Dict[str, Any] = {
            "channel": channel or self.config.default_channel,
            "text": text,
        }

        if title:
            payload["blocks"] = [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*{title}*\n{text}"},
                }
            ] + (blocks or [])
        elif blocks:
            payload["blocks"] = blocks

        if thread_ts:
            payload["thread_ts"] = thread_ts

        response = await self._make_request("POST", "chat.postMessage", payload)
        return response

    async def list_channels(self) -> Dict[str, Any]:
        """
        List all public channels.

        Returns:
            List of channels with metadata
        """
        if not self.config.bot_token:
            return {"ok": False, "error": "not_configured"}

        response = await self._make_request(
            "GET",
            "conversations.list",
            {
                "types": "public_channel,private_channel",
                "exclude_archived": True,
                "limit": 100,
            },
        )
        return response

    async def get_channel_info(self, channel: str) -> Dict[str, Any]:
        """
        Get detailed channel information.

        Args:
            channel: Channel ID or name

        Returns:
            Channel metadata
        """
        if not self.config.bot_token:
            return {"ok": False, "error": "not_configured"}

        response = await self._make_request(
            "GET",
            "conversations.info",
            {"channel": channel},
        )
        return response

    async def reply_in_thread(
        self,
        thread_ts: str,
        text: str,
        channel: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Reply to a message in a thread.

        Args:
            thread_ts: Thread timestamp
            text: Reply text
            channel: Channel ID (required for thread)

        Returns:
            API response
        """
        if not self.config.bot_token or not channel:
            return {"ok": False, "error": "missing_required_params"}

        return await self.send_message(
            text=text, channel=channel, thread_ts=thread_ts
        )

    async def upload_file(
        self,
        file_path: str,
        channel: Optional[str] = None,
        title: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Upload a file to Slack.

        Args:
            file_path: Local file path
            channel: Destination channel
            title: Optional file title

        Returns:
            API response
        """
        if not self.config.bot_token:
            return {"ok": False, "error": "not_configured"}

        if not os.path.exists(file_path):
            return {"ok": False, "error": "file_not_found"}

        payload = {
            "channels": channel or self.config.default_channel,
            "title": title or os.path.basename(file_path),
        }

        try:
            async with aiohttp.ClientSession() as session:
                with open(file_path, "rb") as f:
                    data = aiohttp.FormData()
                    data.add_field("file", f)
                    data.add_field("channels", payload["channels"])
                    if title:
                        data.add_field("title", title)

                    async with session.post(
                        f"{self.base_url}/files.upload",
                        headers={"Authorization": self.headers["Authorization"]},
                        data=data,
                        timeout=aiohttp.ClientTimeout(total=30),
                    ) as response:
                        result = await response.json()
                        return result
        except Exception as e:
            return {"ok": False, "error": str(e)}

    async def get_user_info(self, user: str) -> Dict[str, Any]:
        """
        Get user profile information.

        Args:
            user: User ID

        Returns:
            User profile data
        """
        if not self.config.bot_token:
            return {"ok": False, "error": "not_configured"}

        response = await self._make_request(
            "GET",
            "users.info",
            {"user": user},
        )
        return response

    async def check_health(self) -> Dict[str, Any]:
        """
        Check Slack API connectivity and authentication.

        Returns:
            Health status
        """
        if not self.config.bot_token:
            return {
                "ok": False,
                "error": "not_configured",
                "status": "disabled",
            }

        response = await self._make_request("GET", "auth.test", {})

        if response.get("ok"):
            return {
                "ok": True,
                "status": "healthy",
                "user_id": response.get("user_id"),
                "team_id": response.get("team_id"),
            }

        return {
            "ok": False,
            "error": response.get("error", "unknown"),
            "status": "unhealthy",
        }
