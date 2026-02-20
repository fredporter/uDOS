"""Tests for Phase 8.5: Slack Integration."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from core.sync.slack_client import SlackClient
from core.sync.base_providers import SlackMessage
from core.sync.transformers import SlackMessageTransformer
from core.services.vibe_sync_service import VibeSyncService


# ===================== TestSlackClient =====================


class TestSlackClient:
    """Tests for Slack client."""

    @pytest.fixture
    def slack_client(self):
        """Create Slack client instance."""
        return SlackClient()

    @pytest.mark.asyncio
    async def test_slack_authenticate_success(self, slack_client):
        """Test successful Slack authentication."""
        credentials = {"access_token": "xoxb-test-token-123"}
        result = await slack_client.authenticate(credentials)
        assert result is True
        assert slack_client.authenticated is True
        assert slack_client.access_token == "xoxb-test-token-123"

    @pytest.mark.asyncio
    async def test_slack_authenticate_missing_token(self, slack_client):
        """Test Slack authentication with missing token."""
        credentials = {}
        result = await slack_client.authenticate(credentials)
        assert result is False
        assert slack_client.authenticated is False

    @pytest.mark.asyncio
    async def test_slack_authenticate_with_bot_token(self, slack_client):
        """Test Slack authentication with separate bot token."""
        credentials = {
            "access_token": "xoxp-user-token",
            "bot_token": "xoxb-bot-token",
        }
        result = await slack_client.authenticate(credentials)
        assert result is True
        assert slack_client.bot_token == "xoxb-bot-token"

    @pytest.mark.asyncio
    async def test_slack_fetch_channel_messages(self, slack_client):
        """Test fetching messages from Slack channel."""
        credentials = {"access_token": "xoxb-test-token"}
        await slack_client.authenticate(credentials)

        messages = await slack_client.fetch_channel_messages(
            channel="C123456789",
            limit=25,
        )
        assert isinstance(messages, list)

    @pytest.mark.asyncio
    async def test_slack_fetch_messages_not_authenticated(self, slack_client):
        """Test fetching messages when not authenticated."""
        messages = await slack_client.fetch_channel_messages("C123456789")
        assert messages == []

    @pytest.mark.asyncio
    async def test_slack_post_message(self, slack_client):
        """Test posting message to Slack channel."""
        credentials = {"access_token": "xoxb-test-token"}
        await slack_client.authenticate(credentials)

        ts = await slack_client.post_message(
            channel="C123456789",
            text="Hello from uDOS!",
        )
        assert ts is not None
        assert isinstance(ts, str)

    @pytest.mark.asyncio
    async def test_slack_post_message_with_blocks(self, slack_client):
        """Test posting message with Block Kit blocks."""
        credentials = {"access_token": "xoxb-test-token"}
        await slack_client.authenticate(credentials)

        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "New task created",
                },
            }
        ]

        ts = await slack_client.post_message(
            channel="C123456789",
            text="New task",
            blocks=blocks,
        )
        assert ts is not None

    @pytest.mark.asyncio
    async def test_slack_post_message_in_thread(self, slack_client):
        """Test posting message in Slack thread."""
        credentials = {"access_token": "xoxb-test-token"}
        await slack_client.authenticate(credentials)

        ts = await slack_client.post_message(
            channel="C123456789",
            text="Reply in thread",
            thread_ts="1234567890.123456",
        )
        assert ts is not None

    @pytest.mark.asyncio
    async def test_slack_post_message_not_authenticated(self, slack_client):
        """Test posting message when not authenticated."""
        ts = await slack_client.post_message(
            channel="C123456789",
            text="Not authenticated",
        )
        assert ts is None

    @pytest.mark.asyncio
    async def test_slack_handle_event_message(self, slack_client):
        """Test handling Slack message event."""
        event = {
            "type": "message",
            "channel": "C123456789",
            "user": "U987654321",
            "text": "New task: Fix login bug",
            "ts": "1234567890.123456",
        }

        result = await slack_client.handle_event(event)
        assert result["status"] == "received"
        assert result["event_type"] == "message"
        assert result["channel"] == "C123456789"

    @pytest.mark.asyncio
    async def test_slack_handle_event_mention(self, slack_client):
        """Test handling app mention event."""
        event = {
            "type": "app_mention",
            "channel": "C123456789",
            "user": "U987654321",
            "text": "<@U123456789> create a task",
        }

        result = await slack_client.handle_event(event)
        assert result["status"] == "received"
        assert result["event_type"] == "app_mention"

    @pytest.mark.asyncio
    async def test_slack_handle_event_reaction_added(self, slack_client):
        """Test handling reaction added event."""
        event = {
            "type": "reaction_added",
            "reaction": "thumbsup",
            "item": {
                "type": "message",
                "channel": "C123456789",
                "ts": "1234567890.123456",
            },
        }

        result = await slack_client.handle_event(event)
        assert result["status"] == "received"
        assert result["event_type"] == "reaction_added"
        assert result["reaction"] == "thumbsup"

    @pytest.mark.asyncio
    async def test_slack_handle_event_reaction_removed(self, slack_client):
        """Test handling reaction removed event."""
        event = {
            "type": "reaction_removed",
            "reaction": "eyes",
            "item": {
                "type": "message",
                "channel": "C123456789",
                "ts": "1234567890.123456",
            },
        }

        result = await slack_client.handle_event(event)
        assert result["status"] == "received"
        assert result["event_type"] == "reaction_removed"

    @pytest.mark.asyncio
    async def test_slack_get_thread_messages(self, slack_client):
        """Test fetching messages from a thread."""
        credentials = {"access_token": "xoxb-test-token"}
        await slack_client.authenticate(credentials)

        messages = await slack_client.get_thread_messages(
            channel="C123456789",
            thread_ts="1234567890.123456",
            limit=10,
        )
        assert isinstance(messages, list)

    @pytest.mark.asyncio
    async def test_slack_add_reaction(self, slack_client):
        """Test adding emoji reaction."""
        credentials = {"access_token": "xoxb-test-token"}
        await slack_client.authenticate(credentials)

        result = await slack_client.add_reaction(
            channel="C123456789",
            timestamp="1234567890.123456",
            emoji="thumbsup",
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_slack_get_sync_status(self, slack_client):
        """Test getting Slack sync status."""
        credentials = {"access_token": "xoxb-test-token"}
        await slack_client.authenticate(credentials)

        status = await slack_client.get_sync_status()
        assert status["provider"] == "slack"
        assert status["authenticated"] is True
        assert "last_sync" in status


# ===================== TestSlackMessageTransformer =====================


class TestSlackMessageTransformer:
    """Tests for Slack message to task transformation."""

    def test_transform_slack_message_to_task(self):
        """Test transforming Slack message to task."""
        from datetime import datetime
        import time
        
        ts = time.time()
        message = SlackMessage(
            message_id="1234567890.123456",
            channel_id="C123456789",
            user_id="U987654321",
            text="Fix critical bug in auth system @alice",
            timestamp=ts,
            thread_ts=None,
            reactions={"tada": 1, "eyes": 1},
            metadata={"user_name": "bob", "is_bot": False},
        )

        task = SlackMessageTransformer.slack_to_task_item(message, "mission-eng")

        assert task["type"] == "task"
        assert "Fix critical bug" in task["title"]
        assert task["parent_mission"] == "mission-eng"
        assert "slack_sync" in task["tags"]
        assert task["metadata"]["channel_id"] == "C123456789"
        assert task["metadata"]["user_id"] == "U987654321"
        assert task["metadata"]["reaction_count"] == 2

    def test_transform_slack_bot_message_to_task(self):
        """Test transforming Slack bot message to task."""
        import time
        
        ts = time.time()
        message = SlackMessage(
            message_id="1234567890.654321",
            channel_id="C123456789",
            user_id="U000000000",
            text="Task completed: Deploy v2.0",
            timestamp=ts,
            thread_ts="1234567890.123456",
            reactions=None,
            metadata={"user_name": "udos-bot", "is_bot": True},
        )

        task = SlackMessageTransformer.slack_to_task_item(message, "mission-deploy")

        assert task["type"] == "task"
        assert task["parent_mission"] == "mission-deploy"
        assert task["metadata"]["thread_ts"] == "1234567890.123456"


# ===================== TestVibeSyncServiceSlack =====================


class TestVibeSyncServiceSlack:
    """Tests for sync service Slack integration."""

    @pytest.fixture
    def sync_service(self):
        """Create sync service instance."""
        return VibeSyncService()

    @pytest.mark.asyncio
    async def test_sync_slack_success(self, sync_service):
        """Test successful Slack sync."""
        with patch("core.services.vibe_sync_service.get_oauth_manager") as mock_oauth:
            mock_oauth_instance = AsyncMock()
            mock_oauth_instance.get_credentials = AsyncMock(
                return_value={"access_token": "xoxb-test-token"}
            )
            mock_oauth.return_value = mock_oauth_instance
            sync_service.oauth_manager = mock_oauth_instance

            result = await sync_service.sync_slack(
                workspace="T123456789",
                mission_id="mission-1",
                channels=["C111111111", "C222222222"],
            )

            assert result["status"] == "success"
            assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_sync_slack_all_channels(self, sync_service):
        """Test Slack sync with all channels."""
        with patch("core.services.vibe_sync_service.get_oauth_manager") as mock_oauth:
            mock_oauth_instance = AsyncMock()
            mock_oauth_instance.get_credentials = AsyncMock(
                return_value={"access_token": "xoxb-test-token"}
            )
            mock_oauth.return_value = mock_oauth_instance
            sync_service.oauth_manager = mock_oauth_instance

            result = await sync_service.sync_slack(
                workspace="T123456789",
                mission_id="mission-1",
            )

            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_post_task_update_to_slack(self, sync_service):
        """Test posting task update to Slack."""
        with patch.object(sync_service.oauth_manager, "get_credentials", new_callable=AsyncMock) as mock_creds:
            mock_creds.return_value = {"access_token": "xoxb-test-token"}
            
            result = await sync_service.post_task_update(
                task_id="task-123",
                channel="C123456789",
                update={"status": "done", "title": "Task completed"},
            )
            assert result is True

    @pytest.mark.asyncio
    async def test_handle_slack_webhook(self, sync_service):
        """Test handling Slack webhook."""
        payload = {
            "token": "Jhj5dBrHaK5OwwVQ",
            "team_id": "T123456789",
            "event": {
                "type": "message",
                "channel": "C123456789",
                "user": "U987654321",
                "text": "Create task from message",
                "ts": "1234567890.123456",
            },
        }

        result = await sync_service.handle_webhook("slack", payload)
        assert result["status"] == "received"


# ===================== Integration Tests =====================


class TestPhase8SlackIntegration:
    """Integration tests for Phase 8.5 Slack integration."""

    @pytest.mark.asyncio
    async def test_full_slack_sync_flow(self):
        """Test complete Slack sync flow."""
        service = VibeSyncService()

        with patch.object(service.oauth_manager, "get_credentials", new_callable=AsyncMock) as mock_creds:
            mock_creds.return_value = {"access_token": "xoxb-test-token"}

            result = await service.sync_slack(
                workspace="T123456789",
                mission_id="mission-1",
                channels=["C111", "C222"],
            )

            assert result["provider"] == "slack"
            assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_slack_message_to_task_flow(self):
        """Test converting Slack message to task."""
        import time
        
        ts = time.time()
        message = SlackMessage(
            message_id="ts-123",
            channel_id="C123",
            user_id="U456",
            text="Urgent: Database connection failing",
            timestamp=ts,
            thread_ts=None,
            reactions=None,
            metadata={"user_name": "alice"},
        )

        task = SlackMessageTransformer.slack_to_task_item(message, "mission-ops")

        assert task["type"] == "task"
        assert "Database connection" in task["title"]
        assert task["metadata"]["reaction_count"] == 0

    @pytest.mark.asyncio
    async def test_slack_event_handling_flow(self):
        """Test Slack event handling workflow."""
        client = SlackClient()
        await client.authenticate({"access_token": "xoxb-token"})

        # Handle message event
        message_event = {
            "type": "message",
            "channel": "C123456789",
            "user": "U987654321",
            "text": "New priority: Handle urgent issue",
            "ts": "1234567890.123456",
        }

        result = await client.handle_event(message_event)
        assert result["status"] == "received"

        # Handle reaction event
        reaction_event = {
            "type": "reaction_added",
            "reaction": "fire",
            "item": {
                "type": "message",
                "channel": "C123456789",
                "ts": "1234567890.123456",
            },
        }

        result2 = await client.handle_event(reaction_event)
        assert result2["status"] == "received"
        assert result2["reaction"] == "fire"

    @pytest.mark.asyncio
    async def test_slack_thread_workflow(self):
        """Test Slack thread message handling."""
        client = SlackClient()
        await client.authenticate({"access_token": "xoxb-token"})

        # Post parent message
        parent_ts = await client.post_message(
            channel="C123456789",
            text="New high-priority bug reported",
        )
        assert parent_ts is not None

        # Reply in thread
        reply_ts = await client.post_message(
            channel="C123456789",
            text="Assigned to alice for investigation",
            thread_ts=parent_ts,
        )
        assert reply_ts is not None

        # Fetch thread
        messages = await client.get_thread_messages(
            channel="C123456789",
            thread_ts=parent_ts,
        )
        assert isinstance(messages, list)

    @pytest.mark.asyncio
    async def test_slack_reaction_workflow(self):
        """Test Slack reaction handling."""
        client = SlackClient()
        await client.authenticate({"access_token": "xoxb-token"})

        # Add reaction to mark task complete
        result1 = await client.add_reaction(
            channel="C123456789",
            timestamp="1234567890.123456",
            emoji="white_check_mark",
        )
        assert result1 is True

        # Add reaction to flag for review
        result2 = await client.add_reaction(
            channel="C123456789",
            timestamp="1234567890.123456",
            emoji="eyes",
        )
        assert result2 is True
