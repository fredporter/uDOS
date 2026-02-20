"""Base classes for external system providers (Phase 8)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Any


class ProviderType(str, Enum):
    """External system provider types."""
    GOOGLE_CALENDAR = "google_calendar"
    OUTLOOK_CALENDAR = "outlook_calendar"
    APPLE_CALENDAR = "apple_calendar"
    GMAIL = "gmail"
    OUTLOOK_EMAIL = "outlook_email"
    IMAP = "imap"
    JIRA = "jira"
    LINEAR = "linear"
    SLACK = "slack"


class SyncStatus(str, Enum):
    """Synchronization status."""
    IDLE = "idle"
    SYNCING = "syncing"
    SUCCESS = "success"
    ERROR = "error"
    PAUSED = "paused"


@dataclass
class SyncEvent:
    """Represents a synchronization event."""
    id: str
    provider: str
    event_type: str  # "create", "update", "delete"
    payload: Dict[str, Any]
    timestamp: datetime
    processed: bool = False
    retry_count: int = 0


@dataclass
class CalendarEvent:
    """Represents a calendar event from any provider."""
    id: str
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    attendees: Optional[List[str]] = None
    provider: str = "unknown"
    is_all_day: bool = False
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class EmailMessage:
    """Represents an email message from any provider."""
    message_id: str
    subject: str
    from_addr: str
    to_addrs: List[str]
    body: str
    html_body: Optional[str] = None
    timestamp: datetime = datetime.now()
    thread_id: Optional[str] = None
    labels: Optional[List[str]] = None
    attachments: Optional[List[Dict[str, str]]] = None
    provider: str = "unknown"
    is_unread: bool = False
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Issue:
    """Represents an issue from project management system."""
    id: str
    key: str
    title: str
    description: Optional[str] = None
    status: str = "todo"
    assignee: Optional[str] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    due_date: Optional[datetime] = None
    url: Optional[str] = None
    provider: str = "unknown"
    custom_fields: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class SlackMessage:
    """Represents a Slack message."""
    message_id: str
    channel_id: str
    user_id: str
    text: str
    timestamp: float
    thread_ts: Optional[float] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    reactions: Optional[Dict[str, int]] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseCalendarProvider(ABC):
    """Base class for calendar provider implementations."""

    def __init__(self, provider_type: str):
        self.provider_type = provider_type
        self.authenticated = False
        self.last_sync = None

    @abstractmethod
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with the calendar service."""
        pass

    @abstractmethod
    async def fetch_events(
        self, start_date: datetime, end_date: datetime
    ) -> List[CalendarEvent]:
        """Fetch calendar events within date range."""
        pass

    @abstractmethod
    async def create_event(self, event: CalendarEvent) -> str:
        """Create a new calendar event. Returns event ID."""
        pass

    @abstractmethod
    async def update_event(self, event_id: str, changes: Dict[str, Any]) -> bool:
        """Update an existing calendar event."""
        pass

    @abstractmethod
    async def delete_event(self, event_id: str) -> bool:
        """Delete a calendar event."""
        pass

    @abstractmethod
    async def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status."""
        pass


class BaseEmailProvider(ABC):
    """Base class for email provider implementations."""

    def __init__(self, provider_type: str):
        self.provider_type = provider_type
        self.authenticated = False
        self.last_sync = None

    @abstractmethod
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with the email service."""
        pass

    @abstractmethod
    async def fetch_messages(
        self, query: str = "", limit: int = 50
    ) -> List[EmailMessage]:
        """Fetch email messages matching query."""
        pass

    @abstractmethod
    async def get_message(self, message_id: str) -> Optional[EmailMessage]:
        """Get a specific message by ID."""
        pass

    @abstractmethod
    async def mark_as_processed(self, message_id: str) -> bool:
        """Mark a message as processed (e.g., archived)."""
        pass

    @abstractmethod
    async def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status."""
        pass


class BaseProjectManager(ABC):
    """Base class for project management system implementations."""

    def __init__(self, manager_type: str):
        self.manager_type = manager_type
        self.authenticated = False
        self.last_sync = None

    @abstractmethod
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with the project management service."""
        pass

    @abstractmethod
    async def fetch_issues(
        self, query: str = "", filters: Optional[Dict[str, Any]] = None
    ) -> List[Issue]:
        """Fetch issues matching query/filters."""
        pass

    @abstractmethod
    async def get_issue(self, issue_id: str) -> Optional[Issue]:
        """Get a specific issue by ID."""
        pass

    @abstractmethod
    async def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming webhook from project management system."""
        pass

    @abstractmethod
    async def update_issue(self, issue_id: str, changes: Dict[str, Any]) -> bool:
        """Update an issue."""
        pass

    @abstractmethod
    async def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status."""
        pass


class BaseSlackClient(ABC):
    """Base class for Slack integration."""

    def __init__(self):
        self.authenticated = False
        self.last_sync = None
        self.workspace_id = None

    @abstractmethod
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with Slack."""
        pass

    @abstractmethod
    async def fetch_channel_messages(
        self, channel_id: str, ts_from: float = 0
    ) -> List[SlackMessage]:
        """Fetch messages from a channel."""
        pass

    @abstractmethod
    async def get_thread_messages(
        self, channel_id: str, thread_ts: str
    ) -> List[SlackMessage]:
        """Get messages from a thread."""
        pass

    @abstractmethod
    async def post_message(
        self, channel: str, blocks: List[Dict[str, Any]]
    ) -> str:
        """Post a message with blocks."""
        pass

    @abstractmethod
    async def handle_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming Slack event."""
        pass

    @abstractmethod
    async def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status."""
        pass
