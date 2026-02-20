"""Main sync service orchestrator (Phase 8)."""

from typing import Dict, List, Optional, Any
from datetime import datetime
from core.services.logging_manager import get_logger
from core.sync.event_queue import EventQueue
from core.sync.oauth_manager import get_oauth_manager
from core.sync.calendar_provider_factory import CalendarProviderFactory
from core.sync.transformers import CalendarEventTransformer

logger = get_logger(__name__)


class VibeSyncService:
    """Unified external system synchronization orchestrator."""

    def __init__(self):
        """Initialize sync service."""
        self.event_queue = EventQueue(
            debounce_seconds=30, batch_size=50, max_retries=3
        )
        self.oauth_manager = get_oauth_manager()

        # Provider instances (will be initialized on demand)
        self.calendar_providers = {}  # Keyed by provider type
        self.email_provider = None
        self.project_manager = None
        self.slack_client = None

        # Sync history
        self.sync_history = {}
        self.sync_status = "idle"

        logger.info("VibeSyncService initialized")

    # ==================== Calendar Operations ====================

    async def sync_calendar(
        self, provider_type: str, mission_id: str, credentials: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Synchronize calendar with external provider.

        Args:
            provider_type: 'google_calendar', 'outlook_calendar', 'apple_calendar'
            mission_id: Target mission ID for created tasks
            credentials: OAuth credentials (optional, uses cached if not provided)

        Returns:
            Sync result dict
        """
        logger.info(f"Starting calendar sync for {provider_type} → mission {mission_id}")
        self.sync_status = "syncing"

        try:
            # Get or create provider
            if provider_type not in self.calendar_providers:
                provider = CalendarProviderFactory.create_provider(provider_type)
                if not provider:
                    return {"status": "error", "error": f"Unknown provider: {provider_type}"}
                self.calendar_providers[provider_type] = provider

            provider = self.calendar_providers[provider_type]

            # Get credentials
            if not credentials:
                credentials = await self.oauth_manager.get_credentials(provider_type)
            if not credentials:
                logger.error(f"No credentials for {provider_type}")
                return {"status": "error", "error": f"No credentials for {provider_type}"}

            # Authenticate
            if not await provider.authenticate(credentials):
                return {"status": "error", "error": f"Authentication failed for {provider_type}"}

            # Fetch events (last 7 days to next 30 days)
            from datetime import timedelta
            start_date = datetime.now() - timedelta(days=7)
            end_date = datetime.now() + timedelta(days=30)

            events = await provider.fetch_events(start_date, end_date)
            logger.info(f"Fetched {len(events)} calendar events from {provider_type}")

            # Transform to tasks
            created_tasks = []
            errors = []

            for event in events:
                try:
                    task_item = CalendarEventTransformer.event_to_task_item(
                        event, mission_id
                    )
                    created_tasks.append(task_item)
                except Exception as e:
                    logger.error(f"Error transforming event {event.id}: {e}")
                    errors.append({"event_id": event.id, "error": str(e)})

            # Store sync history
            self.sync_history[provider_type] = {
                "timestamp": datetime.now().isoformat(),
                "events_synced": len(events),
                "tasks_created": len(created_tasks),
                "errors": len(errors),
            }

            self.sync_status = "idle"

            return {
                "status": "success",
                "provider": provider_type,
                "mission_id": mission_id,
                "timestamp": datetime.now().isoformat(),
                "events_synced": len(events),
                "tasks_created": len(created_tasks),
                "errors": errors,
                "tasks": created_tasks,
            }

        except Exception as e:
            logger.error(f"Calendar sync error: {e}")
            self.sync_status = "error"
            return {"status": "error", "error": str(e)}

    async def fetch_calendar_events(
        self, provider_type: str, date_range: Dict[str, str]
    ) -> List[Dict]:
        """Fetch calendar events for date range.

        Args:
            provider_type: Calendar provider type
            date_range: Dict with 'start_date' and 'end_date' ISO strings

        Returns:
            List of calendar events
        """
        logger.info(
            f"Fetching calendar events from {provider_type} "
            f"for range {date_range.get('start_date')} to {date_range.get('end_date')}"
        )

        try:
            # Get or create provider
            if provider_type not in self.calendar_providers:
                provider = CalendarProviderFactory.create_provider(provider_type)
                if not provider:
                    return []
                self.calendar_providers[provider_type] = provider

            provider = self.calendar_providers[provider_type]

            # Get credentials and authenticate
            credentials = await self.oauth_manager.get_credentials(provider_type)
            if not credentials or not await provider.authenticate(credentials):
                logger.warning(f"Cannot authenticate {provider_type}")
                return []

            # Parse date range
            start_date = datetime.fromisoformat(date_range.get('start_date', ''))
            end_date = datetime.fromisoformat(date_range.get('end_date', ''))

            events = await provider.fetch_events(start_date, end_date)
            logger.info(f"Retrieved {len(events)} events from {provider_type}")
            return [
                {
                    "id": e.id,
                    "title": e.title,
                    "start_time": e.start_time.isoformat(),
                    "end_time": e.end_time.isoformat(),
                    "provider": e.provider,
                }
                for e in events
            ]

        except Exception as e:
            logger.error(f"Error fetching calendar events: {e}")
            return []

    async def create_task_from_event(
        self, mission_id: str, event: Dict[str, Any]
    ) -> str:
        """Create a Binder task from calendar event.

        Args:
            mission_id: Target mission ID
            event: Calendar event dict with provider and event data

        Returns:
            Created task ID
        """
        logger.info(
            f"Creating task from event '{event.get('title')}' in mission {mission_id}"
        )

        try:
            # Transform event to Binder task
            from core.sync.base_providers import CalendarEvent

            cal_event = CalendarEvent(
                id=event.get('id', ''),
                title=event.get('title', ''),
                description=event.get('description', ''),
                start_time=datetime.fromisoformat(event.get('start_time', '')),
                end_time=datetime.fromisoformat(event.get('end_time', '')),
                location=event.get('location'),
                attendees=event.get('attendees'),
                provider=event.get('provider', 'unknown'),
                is_all_day=event.get('is_all_day', False),
            )

            task_item = CalendarEventTransformer.event_to_task_item(cal_event, mission_id)

            # TODO: Persist to Binder using VibeBinderService
            # For now, return the task ID
            return task_item['id']

        except Exception as e:
            logger.error(f"Error creating task from event: {e}")
            raise

    async def update_calendar_from_task(
        self, provider_type: str, task_id: str, event_id: str, changes: Dict[str, Any] = None
    ) -> bool:
        """Update calendar event when task changes.

        Args:
            provider_type: Calendar provider type
            task_id: Binder task ID
            event_id: External calendar event ID
            changes: Optional dict of changes (title, description, due_date)

        Returns:
            True if successful
        """
        logger.info(
            f"Updating calendar event {event_id} from task {task_id} "
            f"({provider_type})"
        )

        try:
            # Get provider
            if provider_type not in self.calendar_providers:
                logger.error(f"Provider {provider_type} not initialized")
                return False

            provider = self.calendar_providers[provider_type]

            # Get credentials and authenticate
            credentials = await self.oauth_manager.get_credentials(provider_type)
            if not credentials or not await provider.authenticate(credentials):
                logger.warning(f"Cannot authenticate {provider_type}")
                return False

            # Update event
            if not changes:
                changes = {}

            success = await provider.update_event(event_id, changes)
            if success:
                logger.info(f"Updated calendar event {event_id}")
            else:
                logger.error(f"Failed to update calendar event {event_id}")

            return success

        except Exception as e:
            logger.error(f"Error updating calendar event: {e}")
            return False

    # ==================== Email Operations ====================

    async def sync_emails(
        self, provider_type: str, credentials: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Synchronize email with external provider.

        Args:
            provider_type: 'gmail', 'outlook_email', 'imap'
            credentials: OAuth credentials

        Returns:
            Sync result dict
        """
        logger.info(f"Starting email sync for {provider_type}")
        self.sync_status = "syncing"

        try:
            result = {
                "status": "pending",
                "provider": provider_type,
                "timestamp": datetime.now().isoformat(),
                "message": "Email sync not yet implemented for Phase 8.1",
            }
            return result

        except Exception as e:
            logger.error(f"Email sync error: {e}")
            self.sync_status = "error"
            return {"status": "error", "error": str(e)}

    async def fetch_emails(
        self, provider_type: str, filters: Optional[Dict] = None
    ) -> List[Dict]:
        """Fetch emails from external provider.

        Args:
            provider_type: Email provider type
            filters: Filter criteria (label, unread, etc.)

        Returns:
            List of email messages
        """
        logger.info(f"Fetching emails from {provider_type} with filters {filters}")

        try:
            # TODO: Implement actual email fetching
            return []
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            raise

    async def create_task_from_email(
        self, mission_id: str, email: Dict[str, Any]
    ) -> str:
        """Create a Binder task from email.

        Args:
            mission_id: Target mission ID
            email: Email message dict

        Returns:
            Created task ID
        """
        logger.info(
            f"Creating task from email '{email.get('subject')}' in mission {mission_id}"
        )

        try:
            # TODO: Implement task creation from email
            return f"task-{datetime.now().timestamp()}"
        except Exception as e:
            logger.error(f"Error creating task from email: {e}")
            raise

    # ==================== Project Management ====================

    async def sync_jira(
        self, workspace_id: str, jql: Optional[str] = None
    ) -> Dict[str, Any]:
        """Synchronize with Jira instance.

        Args:
            workspace_id: Jira workspace/instance ID
            jql: Jira Query Language filter

        Returns:
            Sync result dict
        """
        logger.info(f"Starting Jira sync for workspace {workspace_id}")
        self.sync_status = "syncing"

        try:
            result = {
                "status": "pending",
                "provider": "jira",
                "workspace_id": workspace_id,
                "timestamp": datetime.now().isoformat(),
                "message": "Jira sync not yet implemented for Phase 8.1",
            }
            return result

        except Exception as e:
            logger.error(f"Jira sync error: {e}")
            self.sync_status = "error"
            return {"status": "error", "error": str(e)}

    async def sync_linear(
        self, team_id: str, status_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """Synchronize with Linear workspace.

        Args:
            team_id: Linear team/workspace ID
            status_filter: Status filter (e.g., 'active', 'completed')

        Returns:
            Sync result dict
        """
        logger.info(f"Starting Linear sync for team {team_id}")
        self.sync_status = "syncing"

        try:
            result = {
                "status": "pending",
                "provider": "linear",
                "team_id": team_id,
                "timestamp": datetime.now().isoformat(),
                "message": "Linear sync not yet implemented for Phase 8.1",
            }
            return result

        except Exception as e:
            logger.error(f"Linear sync error: {e}")
            self.sync_status = "error"
            return {"status": "error", "error": str(e)}

    async def handle_webhook(self, provider: str, payload: Dict[str, Any]) -> Dict:
        """Handle incoming webhook from external system.

        Args:
            provider: Provider type (jira, linear, etc.)
            payload: Webhook payload

        Returns:
            Webhook response dict
        """
        logger.info(f"Received webhook from {provider}")

        try:
            # TODO: Implement webhook handling
            return {
                "status": "received",
                "provider": provider,
                "message": "Webhook handling not yet implemented for Phase 8.1",
            }
        except Exception as e:
            logger.error(f"Webhook handling error: {e}")
            return {"status": "error", "error": str(e)}

    # ==================== Slack Integration ====================

    async def sync_slack(
        self, workspace: str, channels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Synchronize with Slack workspace.

        Args:
            workspace: Slack workspace ID
            channels: List of channel IDs to sync

        Returns:
            Sync result dict
        """
        logger.info(f"Starting Slack sync for workspace {workspace}")
        self.sync_status = "syncing"

        try:
            result = {
                "status": "pending",
                "workspace": workspace,
                "channels": channels or [],
                "timestamp": datetime.now().isoformat(),
                "message": "Slack sync not yet implemented for Phase 8.1",
            }
            return result

        except Exception as e:
            logger.error(f"Slack sync error: {e}")
            self.sync_status = "error"
            return {"status": "error", "error": str(e)}

    async def post_task_update(
        self, task_id: str, channel: str, update: Dict[str, Any]
    ) -> bool:
        """Post a task update to Slack channel.

        Args:
            task_id: Binder task ID
            channel: Slack channel ID
            update: Update dict with status, title, etc.

        Returns:
            True if posted successfully
        """
        logger.info(f"Posting task update for {task_id} to Slack channel {channel}")

        try:
            # TODO: Implement Slack post
            return True
        except Exception as e:
            logger.error(f"Error posting to Slack: {e}")
            return False

    # ==================== Status & Control ====================

    async def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status for all systems.

        Returns:
            Status dict with provider statuses
        """
        queue_status = await self.event_queue.get_queue_status()
        auth_status = await self.oauth_manager.get_all_auth_status()

        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": self.sync_status,
            "queue": queue_status,
            "authentication": auth_status,
            "sync_history": self.sync_history,
        }

    async def trigger_full_sync(self, systems: Optional[List[str]] = None) -> Dict:
        """Trigger full synchronization across specified systems.

        Args:
            systems: List of systems to sync (None = all configured)

        Returns:
            Full sync result dict
        """
        logger.info(f"Triggering full sync for systems: {systems}")
        self.sync_status = "syncing"

        try:
            results = {}

            if not systems:
                systems = ["calendar", "email", "jira", "linear", "slack"]

            # TODO: Implement actual full sync
            # For now return placeholder
            results = {
                "status": "pending",
                "systems": systems,
                "timestamp": datetime.now().isoformat(),
                "message": "Full sync not yet implemented for Phase 8.1",
            }

            self.sync_status = "idle"
            return results

        except Exception as e:
            logger.error(f"Full sync error: {e}")
            self.sync_status = "error"
            return {"status": "error", "error": str(e)}


# Singleton instance
_sync_service = None


def get_sync_service() -> VibeSyncService:
    """Get or create sync service singleton."""
    global _sync_service
    if _sync_service is None:
        _sync_service = VibeSyncService()
    return _sync_service
