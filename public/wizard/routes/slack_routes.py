"""
Slack API Routes
================

FastAPI routes for Slack Web API integration.

Endpoints:
  POST   /api/v1/slack/send        - Send notification to Slack
  GET    /api/v1/slack/channels    - List available channels
  GET    /api/v1/slack/channels/{id} - Get channel info
  POST   /api/v1/slack/thread      - Reply in thread
  POST   /api/v1/slack/upload      - Upload file to Slack
  GET    /api/v1/slack/user/{id}   - Get user info
  GET    /api/v1/slack/health      - Check Slack connectivity
  GET    /api/v1/slack/config      - Get Slack config status
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

try:
    from fastapi import APIRouter, HTTPException, UploadFile, File, Form
except ImportError:
    APIRouter = None

from wizard.services.slack_service import SlackService, SlackConfig


# Request/Response Models
class SendMessageRequest(BaseModel):
    """Send message request."""

    text: str = Field(..., min_length=1, max_length=4000)
    channel: Optional[str] = Field(None, description="Channel ID or name")
    title: Optional[str] = Field(None, description="Optional message title")


class ThreadReplyRequest(BaseModel):
    """Thread reply request."""

    thread_ts: str = Field(..., description="Thread timestamp")
    text: str = Field(..., min_length=1, max_length=4000)
    channel: str = Field(..., description="Channel ID")


class SlackResponse(BaseModel):
    """Standard Slack API response."""

    ok: bool
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


def create_slack_routes(slack_service: SlackService) -> "APIRouter":
    """Create Slack API routes."""
    if not APIRouter:
        raise RuntimeError("FastAPI not available")

    router = APIRouter(prefix="/api/v1/slack", tags=["slack"])

    @router.post("/send", response_model=SlackResponse)
    async def send_notification(req: SendMessageRequest):
        """
        Send a notification to Slack.

        **Request:**
        ```json
        {
          "text": "Hello from uDOS!",
          "channel": "#notifications",
          "title": "uDOS Notification"
        }
        ```

        **Response:**
        ```json
        {
          "ok": true,
          "data": {
            "ts": "1234567890.123456",
            "channel": "C12345678"
          }
        }
        ```
        """
        try:
            result = await slack_service.send_message(
                text=req.text,
                channel=req.channel,
                title=req.title,
            )
            return SlackResponse(ok=result.get("ok", False), data=result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/channels", response_model=SlackResponse)
    async def list_channels():
        """
        List all available Slack channels.

        **Response:**
        ```json
        {
          "ok": true,
          "data": {
            "channels": [
              {
                "id": "C12345678",
                "name": "notifications",
                "is_member": true
              }
            ]
          }
        }
        ```
        """
        try:
            result = await slack_service.list_channels()
            return SlackResponse(ok=result.get("ok", False), data=result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/channels/{channel_id}", response_model=SlackResponse)
    async def get_channel_info(channel_id: str):
        """
        Get detailed information about a specific channel.

        **Response:**
        ```json
        {
          "ok": true,
          "data": {
            "channel": {
              "id": "C12345678",
              "name": "notifications",
              "topic": {"value": "uDOS notifications"},
              "members_count": 42
            }
          }
        }
        ```
        """
        try:
            result = await slack_service.get_channel_info(channel_id)
            return SlackResponse(ok=result.get("ok", False), data=result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/thread", response_model=SlackResponse)
    async def reply_in_thread(req: ThreadReplyRequest):
        """
        Reply to a message in a Slack thread.

        **Request:**
        ```json
        {
          "thread_ts": "1234567890.123456",
          "channel": "C12345678",
          "text": "Reply in thread"
        }
        ```

        **Response:**
        ```json
        {
          "ok": true,
          "data": {"ts": "1234567890.789012"}
        }
        ```
        """
        try:
            result = await slack_service.reply_in_thread(
                thread_ts=req.thread_ts,
                text=req.text,
                channel=req.channel,
            )
            return SlackResponse(ok=result.get("ok", False), data=result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/upload", response_model=SlackResponse)
    async def upload_file(
        file: UploadFile = File(...),
        channel: str = Form(...),
        title: Optional[str] = Form(None),
    ):
        """
        Upload a file to Slack.

        **Form Data:**
        - file: Binary file content
        - channel: Destination channel ID
        - title: Optional file title

        **Response:**
        ```json
        {
          "ok": true,
          "data": {"file": {"id": "F12345678"}}
        }
        ```
        """
        try:
            import tempfile
            import shutil

            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                content = await file.read()
                tmp.write(content)
                tmp.flush()

                result = await slack_service.upload_file(
                    file_path=tmp.name,
                    channel=channel,
                    title=title or file.filename,
                )

            return SlackResponse(ok=result.get("ok", False), data=result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/user/{user_id}", response_model=SlackResponse)
    async def get_user_info(user_id: str):
        """
        Get user profile information.

        **Response:**
        ```json
        {
          "ok": true,
          "data": {
            "user": {
              "id": "U12345678",
              "name": "username",
              "profile": {"display_name": "Display Name"}
            }
          }
        }
        ```
        """
        try:
            result = await slack_service.get_user_info(user_id)
            return SlackResponse(ok=result.get("ok", False), data=result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/health", response_model=SlackResponse)
    async def check_health():
        """
        Check Slack API connectivity and authentication status.

        **Response:**
        ```json
        {
          "ok": true,
          "data": {
            "status": "healthy",
            "user_id": "U12345678",
            "team_id": "T12345678"
          }
        }
        ```
        """
        try:
            result = await slack_service.check_health()
            return SlackResponse(
                ok=result.get("ok", False),
                error=result.get("error"),
                data=result,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/config", response_model=SlackResponse)
    async def get_config_status():
        """
        Get Slack configuration status (without exposing secrets).

        **Response:**
        ```json
        {
          "ok": true,
          "data": {
            "is_configured": true,
            "default_channel": "#notifications",
            "rate_limit_per_minute": 20
          }
        }
        ```
        """
        return SlackResponse(
            ok=True,
            data={
                "is_configured": slack_service.config.is_configured(),
                "default_channel": slack_service.config.default_channel,
                "rate_limit_per_minute": slack_service.config.rate_limit_per_minute,
            },
        )

    return router
