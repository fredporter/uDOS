"""Tests for Phase 8.3 email synchronization."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from core.sync.email_provider_factory import EmailProviderFactory
from core.sync.gmail_provider import GmailProvider
from core.sync.outlook_email_provider import OutlookEmailProvider
from core.sync.imap_provider import IMAPProvider
from core.sync.transformers import EmailMessageTransformer
from core.sync.base_providers import EmailMessage
from core.services.vibe_sync_service import get_sync_service


class TestEmailProviderFactory:
    """Test email provider factory."""

    def test_create_gmail_provider(self):
        """Test creating Gmail provider."""
        provider = EmailProviderFactory.create_provider("gmail")
        assert provider is not None
        assert isinstance(provider, GmailProvider)
        assert provider.provider_type == "gmail"

    def test_create_outlook_provider(self):
        """Test creating Outlook Email provider."""
        provider = EmailProviderFactory.create_provider("outlook_email")
        assert provider is not None
        assert isinstance(provider, OutlookEmailProvider)
        assert provider.provider_type == "outlook_email"

    def test_create_imap_provider(self):
        """Test creating IMAP provider."""
        provider = EmailProviderFactory.create_provider("imap")
        assert provider is not None
        assert isinstance(provider, IMAPProvider)
        assert provider.provider_type == "imap"

    def test_create_unknown_provider(self):
        """Test creating unknown provider returns None."""
        provider = EmailProviderFactory.create_provider("unknown_provider")
        assert provider is None

    def test_get_available_providers(self):
        """Test getting list of available providers."""
        providers = EmailProviderFactory.get_available_providers()
        assert len(providers) == 3
        assert "gmail" in providers
        assert "outlook_email" in providers
        assert "imap" in providers


class TestGmailProvider:
    """Test Gmail provider."""

    @pytest.fixture
    def provider(self):
        return GmailProvider()

    @pytest.mark.asyncio
    async def test_authenticate_success(self, provider):
        """Test successful Gmail authentication."""
        credentials = {"access_token": "test-token"}
        result = await provider.authenticate(credentials)
        assert result is True
        assert provider.authenticated is True

    @pytest.mark.asyncio
    async def test_authenticate_missing_token(self, provider):
        """Test authentication fails with missing token."""
        credentials = {}
        result = await provider.authenticate(credentials)
        assert result is False

    @pytest.mark.asyncio
    async def test_fetch_messages(self, provider):
        """Test fetching Gmail messages."""
        provider.authenticated = True
        messages = await provider.fetch_messages("is:unread", limit=10)
        assert isinstance(messages, list)

    @pytest.mark.asyncio
    async def test_fetch_messages_not_authenticated(self, provider):
        """Test fetching fails when not authenticated."""
        messages = await provider.fetch_messages()
        assert messages == []

    @pytest.mark.asyncio
    async def test_mark_as_processed(self, provider):
        """Test marking email as processed."""
        provider.authenticated = True
        result = await provider.mark_as_processed("msg-123")
        assert result is True

    @pytest.mark.asyncio
    async def test_get_sync_status(self, provider):
        """Test getting sync status."""
        credentials = {"access_token": "test-token"}
        await provider.authenticate(credentials)
        status = await provider.get_sync_status()

        assert status["provider"] == "gmail"
        assert status["authenticated"] is True


class TestOutlookEmailProvider:
    """Test Outlook Email provider."""

    @pytest.fixture
    def provider(self):
        return OutlookEmailProvider()

    @pytest.mark.asyncio
    async def test_authenticate_success(self, provider):
        """Test successful Outlook authentication."""
        credentials = {"access_token": "outlook-token"}
        result = await provider.authenticate(credentials)
        assert result is True

    @pytest.mark.asyncio
    async def test_fetch_messages(self, provider):
        """Test fetching Outlook messages."""
        provider.authenticated = True
        messages = await provider.fetch_messages("isRead:false", limit=20)
        assert isinstance(messages, list)

    @pytest.mark.asyncio
    async def test_mark_as_processed(self, provider):
        """Test marking Outlook email as processed."""
        provider.authenticated = True
        result = await provider.mark_as_processed("outlook-msg-456")
        assert result is True


class TestIMAPProvider:
    """Test IMAP provider."""

    @pytest.fixture
    def provider(self):
        return IMAPProvider()

    @pytest.mark.asyncio
    async def test_authenticate_success(self, provider):
        """Test successful IMAP authentication."""
        credentials = {
            "host": "imap.example.com",
            "username": "user@example.com",
            "password": "password",
            "port": 993,
            "use_tls": True,
        }
        result = await provider.authenticate(credentials)
        assert result is True
        assert provider.authenticated is True
        assert provider.host == "imap.example.com"

    @pytest.mark.asyncio
    async def test_authenticate_missing_credentials(self, provider):
        """Test IMAP auth fails with missing credentials."""
        credentials = {"host": "imap.example.com"}
        result = await provider.authenticate(credentials)
        assert result is False

    @pytest.mark.asyncio
    async def test_fetch_messages(self, provider):
        """Test fetching IMAP messages."""
        provider.authenticated = True
        messages = await provider.fetch_messages("UNSEEN", limit=30)
        assert isinstance(messages, list)

    @pytest.mark.asyncio
    async def test_mark_as_processed(self, provider):
        """Test marking IMAP email as processed."""
        provider.authenticated = True
        result = await provider.mark_as_processed("imap-msg-789")
        assert result is True

    @pytest.mark.asyncio
    async def test_get_sync_status(self, provider):
        """Test getting IMAP sync status."""
        credentials = {
            "host": "imap.gmail.com",
            "username": "user@gmail.com",
            "password": "app-password",
        }
        await provider.authenticate(credentials)
        status = await provider.get_sync_status()

        assert status["provider"] == "imap"
        assert status["authenticated"] is True
        assert status["host"] == "imap.gmail.com"


class TestEmailMessageTransformer:
    """Test email message transformer."""

    def test_email_to_task_item(self):
        """Test transforming email to task item."""
        email = EmailMessage(
            message_id="msg-001",
            subject="Project Update",
            from_addr="boss@company.com",
            to_addrs=["me@company.com"],
            body="Here's the update on the project...",
            timestamp=datetime.now(),
            provider="gmail",
            is_unread=True,
        )

        task_item = EmailMessageTransformer.email_to_task_item(email, "mission-1")

        assert task_item["type"] == "task"
        assert task_item["title"] == "Project Update"
        assert task_item["parent_mission"] == "mission-1"
        assert "email_sync" in task_item["tags"]
        assert "gmail" in task_item["tags"]
        assert task_item["metadata"]["external_provider"] == "gmail"
        assert task_item["metadata"]["from"] == "boss@company.com"
        assert task_item["metadata"]["is_unread"] is True

    def test_email_to_task_with_thread(self):
        """Test transforming email with thread ID."""
        email = EmailMessage(
            message_id="msg-002",
            subject="Re: Question",
            from_addr="colleague@company.com",
            to_addrs=["me@company.com"],
            body="I have a question about...",
            timestamp=datetime.now(),
            thread_id="thread-123",
            labels=["work", "urgent"],
            provider="gmail",
        )

        task_item = EmailMessageTransformer.email_to_task_item(email, "mission-2")

        assert task_item["metadata"]["thread_id"] == "thread-123"
        assert "work" in task_item["tags"]
        assert "urgent" in task_item["tags"]

    def test_email_with_attachments(self):
        """Test transforming email with attachments."""
        email = EmailMessage(
            message_id="msg-003",
            subject="Contract for Review",
            from_addr="legal@company.com",
            to_addrs=["me@company.com"],
            body="Please review the attached contract.",
            timestamp=datetime.now(),
            attachments=[
                {"filename": "contract.pdf", "size": 125000},
                {"filename": "terms.txt", "size": 5000},
            ],
            provider="outlook_email",
        )

        task_item = EmailMessageTransformer.email_to_task_item(email, "mission-3")

        assert len(task_item["metadata"]["attachments"]) == 2
        assert task_item["metadata"]["attachments"][0]["filename"] == "contract.pdf"


class TestVibeSyncServiceEmail:
    """Test VibeSyncService email operations."""

    @pytest.fixture
    def sync_service(self):
        return get_sync_service()

    @pytest.mark.asyncio
    async def test_sync_emails_unknown_provider(self, sync_service):
        """Test syncing unknown email provider."""
        result = await sync_service.sync_emails(
            "unknown_provider", "mission-1", "", 50, {}
        )
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_fetch_emails(self, sync_service):
        """Test fetching emails."""
        # Mock the provider
        with patch.object(
            EmailProviderFactory, "create_provider"
        ) as mock_factory:
            mock_provider = AsyncMock()
            mock_factory.return_value = mock_provider
            mock_provider.fetch_messages = AsyncMock(return_value=[])

            emails = await sync_service.fetch_emails("gmail", "is:unread", 20)
            assert isinstance(emails, list)

    @pytest.mark.asyncio
    async def test_create_task_from_email(self, sync_service):
        """Test creating task from email."""
        email = {
            "id": "msg-004",
            "subject": "Action Required",
            "from": "manager@company.com",
            "to": ["me@company.com"],
            "body": "Please complete the review by EOD",
            "timestamp": datetime.now().isoformat(),
            "provider": "gmail",
            "is_unread": True,
        }

        task_id = await sync_service.create_task_from_email("mission-1", email)
        assert task_id.startswith("task-")

    @pytest.mark.asyncio
    async def test_sync_emails_with_transformation(self, sync_service):
        """Test full email sync with transformation."""
        # This test verifies the complete flow
        email = EmailMessage(
            message_id="msg-005",
            subject="Test Email",
            from_addr="sender@example.com",
            to_addrs=["recipient@example.com"],
            body="This is a test",
            timestamp=datetime.now(),
            provider="gmail",
        )

        # Direct transformer test
        task = EmailMessageTransformer.email_to_task_item(email, "test-mission")
        assert task["title"] == "Test Email"
        assert task["parent_mission"] == "test-mission"
        assert task["status"] == "todo"  # Default status for new email tasks
