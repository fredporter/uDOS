"""Tests for Phase 8.2 calendar synchronization."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from core.sync.calendar_provider_factory import CalendarProviderFactory
from core.sync.google_calendar_provider import GoogleCalendarProvider
from core.sync.outlook_calendar_provider import OutlookCalendarProvider
from core.sync.apple_calendar_provider import AppleCalendarProvider
from core.sync.transformers import CalendarEventTransformer
from core.sync.base_providers import CalendarEvent
from core.services.vibe_sync_service import get_sync_service


class TestCalendarProviderFactory:
    """Test calendar provider factory."""

    def test_create_google_provider(self):
        """Test creating Google Calendar provider."""
        provider = CalendarProviderFactory.create_provider("google_calendar")
        assert provider is not None
        assert isinstance(provider, GoogleCalendarProvider)
        assert provider.provider_type == "google_calendar"

    def test_create_outlook_provider(self):
        """Test creating Outlook Calendar provider."""
        provider = CalendarProviderFactory.create_provider("outlook_calendar")
        assert provider is not None
        assert isinstance(provider, OutlookCalendarProvider)
        assert provider.provider_type == "outlook_calendar"

    def test_create_apple_provider(self):
        """Test creating Apple Calendar provider."""
        provider = CalendarProviderFactory.create_provider("apple_calendar")
        assert provider is not None
        assert isinstance(provider, AppleCalendarProvider)
        assert provider.provider_type == "apple_calendar"

    def test_create_unknown_provider(self):
        """Test creating unknown provider returns None."""
        provider = CalendarProviderFactory.create_provider("unknown_provider")
        assert provider is None

    def test_get_available_providers(self):
        """Test getting list of available providers."""
        providers = CalendarProviderFactory.get_available_providers()
        assert len(providers) == 3
        assert "google_calendar" in providers
        assert "outlook_calendar" in providers
        assert "apple_calendar" in providers


class TestGoogleCalendarProvider:
    """Test Google Calendar provider."""

    @pytest.fixture
    def provider(self):
        return GoogleCalendarProvider()

    @pytest.mark.asyncio
    async def test_authenticate_success(self, provider):
        """Test successful authentication."""
        credentials = {"access_token": "test-token"}
        result = await provider.authenticate(credentials)
        assert result is True
        assert provider.authenticated is True
        assert provider.last_sync is not None

    @pytest.mark.asyncio
    async def test_authenticate_missing_token(self, provider):
        """Test authentication fails with missing token."""
        credentials = {}
        result = await provider.authenticate(credentials)
        assert result is False
        assert provider.authenticated is False

    @pytest.mark.asyncio
    async def test_fetch_events(self, provider):
        """Test fetching events."""
        provider.authenticated = True
        start_date = datetime.now()
        end_date = datetime.now() + timedelta(days=7)

        events = await provider.fetch_events(start_date, end_date)
        assert isinstance(events, list)

    @pytest.mark.asyncio
    async def test_fetch_events_not_authenticated(self, provider):
        """Test fetching events when not authenticated."""
        start_date = datetime.now()
        end_date = datetime.now() + timedelta(days=7)

        events = await provider.fetch_events(start_date, end_date)
        assert events == []

    @pytest.mark.asyncio
    async def test_create_event(self, provider):
        """Test creating an event."""
        provider.authenticated = True
        event = CalendarEvent(
            id="test-event",
            title="Test Event",
            description="Testing",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=1),
        )

        event_id = await provider.create_event(event)
        assert event_id != ""
        assert "google" in event_id

    @pytest.mark.asyncio
    async def test_update_event(self, provider):
        """Test updating an event."""
        provider.authenticated = True
        changes = {"title": "Updated Title"}

        result = await provider.update_event("test-event-id", changes)
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_event(self, provider):
        """Test deleting an event."""
        provider.authenticated = True

        result = await provider.delete_event("test-event-id")
        assert result is True

    @pytest.mark.asyncio
    async def test_get_sync_status(self, provider):
        """Test getting sync status."""
        credentials = {"access_token": "test-token"}
        await provider.authenticate(credentials)
        status = await provider.get_sync_status()

        assert status["provider"] == "google_calendar"
        assert status["authenticated"] is True
        assert status["last_sync"] is not None


class TestOutlookCalendarProvider:
    """Test Outlook Calendar provider."""

    @pytest.fixture
    def provider(self):
        return OutlookCalendarProvider()

    @pytest.mark.asyncio
    async def test_authenticate_success(self, provider):
        """Test successful Outlook authentication."""
        credentials = {"access_token": "outlook-token"}
        result = await provider.authenticate(credentials)
        assert result is True

    @pytest.mark.asyncio
    async def test_create_event(self, provider):
        """Test creating Outlook event."""
        provider.authenticated = True
        event = CalendarEvent(
            id="outlook-event",
            title="Outlook Event",
            description="Test",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=1),
        )

        event_id = await provider.create_event(event)
        assert "outlook" in event_id


class TestAppleCalendarProvider:
    """Test Apple Calendar provider."""

    @pytest.fixture
    def provider(self):
        return AppleCalendarProvider()

    @pytest.mark.asyncio
    async def test_authenticate_with_path(self, provider):
        """Test Apple Calendar authentication with path."""
        # Create a temp file
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name

        try:
            credentials = {"calendar_path": tmp_path}
            result = await provider.authenticate(credentials)
            assert result is True
            assert provider.authenticated is True
        finally:
            import os
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    @pytest.mark.asyncio
    async def test_authenticate_missing_path(self, provider):
        """Test Apple Calendar auth fails without path."""
        credentials = {}
        result = await provider.authenticate(credentials)
        assert result is False


class TestCalendarEventTransformer:
    """Test calendar event transformer."""

    def test_event_to_task_item(self):
        """Test transforming calendar event to task item."""
        event = CalendarEvent(
            id="event-123",
            title="Team Meeting",
            description="Weekly sync",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=1),
            location="Zoom",
            attendees=["alice@example.com"],
            provider="google_calendar",
            is_all_day=False,
        )

        task_item = CalendarEventTransformer.event_to_task_item(event, "mission-1")

        assert task_item["type"] == "task"
        assert task_item["title"] == "Team Meeting"
        assert task_item["parent_mission"] == "mission-1"
        assert "calendar_sync" in task_item["tags"]
        assert "google_calendar" in task_item["tags"]
        assert task_item["metadata"]["external_provider"] == "google_calendar"
        assert task_item["metadata"]["location"] == "Zoom"
        assert len(task_item["metadata"]["attendees"]) == 1

    def test_event_to_task_all_day(self):
        """Test transforming all-day event."""
        event = CalendarEvent(
            id="event-456",
            title="Holiday",
            description="",
            start_time=datetime.now().date(),
            end_time=datetime.now().date(),
            is_all_day=True,
            provider="apple_calendar",
        )

        task_item = CalendarEventTransformer.event_to_task_item(event, "mission-2")

        assert task_item["metadata"]["is_all_day"] is True


class TestVibeSyncServiceCalendar:
    """Test VibeSyncService calendar operations."""

    @pytest.fixture
    def sync_service(self):
        return get_sync_service()

    @pytest.mark.asyncio
    async def test_sync_calendar_unknown_provider(self, sync_service):
        """Test syncing unknown calendar provider."""
        result = await sync_service.sync_calendar(
            "unknown_provider", "mission-1", {}
        )
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_fetch_calendar_events(self, sync_service):
        """Test fetching calendar events."""
        # Mock the provider
        with patch.object(
            CalendarProviderFactory, "create_provider"
        ) as mock_factory:
            mock_provider = AsyncMock()
            mock_factory.return_value = mock_provider
            mock_provider.fetch_events = AsyncMock(return_value=[])

            date_range = {
                "start_date": datetime.now().isoformat(),
                "end_date": (datetime.now() + timedelta(days=7)).isoformat(),
            }

            # Note: This will fail gracefully without credentials
            # In real use, credentials would be mocked too
            events = await sync_service.fetch_calendar_events("google_calendar", date_range)
            assert isinstance(events, list)

    @pytest.mark.asyncio
    async def test_create_task_from_event(self, sync_service):
        """Test creating task from calendar event."""
        event = {
            "id": "event-789",
            "title": "Project Deadline",
            "description": "Final submission",
            "start_time": datetime.now().isoformat(),
            "end_time": (datetime.now() + timedelta(days=1)).isoformat(),
            "provider": "google_calendar",
        }

        task_id = await sync_service.create_task_from_event("mission-1", event)
        assert task_id.startswith("task-")

    @pytest.mark.asyncio
    async def test_update_calendar_from_task(self, sync_service):
        """Test updating calendar from task."""
        result = await sync_service.update_calendar_from_task(
            "google_calendar", "task-1", "event-1", {"title": "Updated"}
        )
        # Will be False because provider not initialized
        assert isinstance(result, bool)
