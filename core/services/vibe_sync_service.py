"""Main sync service orchestrator (Phase 8)."""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from core.services.logging_manager import get_logger
from core.sync.event_queue import EventQueue
from core.sync.oauth_manager import get_oauth_manager
from core.sync.calendar_provider_factory import CalendarProviderFactory
from core.sync.email_provider_factory import EmailProviderFactory
from core.sync.project_manager_factory import ProjectManagerFactory
from core.sync.transformers import (
    CalendarEventTransformer,
    EmailMessageTransformer,
    IssueTransformer,
)

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
        self.email_providers = {}  # Keyed by provider type
        self.project_managers = {}  # Keyed by provider type (jira, linear)
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
        self, provider_type: str, mission_id: str, query: str = "", limit: int = 50,
        credentials: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Synchronize email with external provider.

        Args:
            provider_type: 'gmail', 'outlook_email', 'imap'
            mission_id: Target mission ID for created tasks
            query: Email search/filter query
            limit: Max emails to sync
            credentials: OAuth credentials (optional, uses cached if not provided)

        Returns:
            Sync result dict
        """
        logger.info(
            f"Starting email sync for {provider_type} → mission {mission_id} "
            f"(query='{query}', limit={limit})"
        )
        self.sync_status = "syncing"

        try:
            # Get or create provider
            if provider_type not in self.email_providers:
                provider = EmailProviderFactory.create_provider(provider_type)
                if not provider:
                    return {"status": "error", "error": f"Unknown provider: {provider_type}"}
                self.email_providers[provider_type] = provider

            provider = self.email_providers[provider_type]

            # Get credentials
            if not credentials:
                credentials = await self.oauth_manager.get_credentials(provider_type)
            if not credentials:
                logger.error(f"No credentials for {provider_type}")
                return {"status": "error", "error": f"No credentials for {provider_type}"}

            # Authenticate
            if not await provider.authenticate(credentials):
                return {"status": "error", "error": f"Authentication failed for {provider_type}"}

            # Fetch emails
            emails = await provider.fetch_messages(query or "", limit)
            logger.info(f"Fetched {len(emails)} emails from {provider_type}")

            # Transform to tasks
            created_tasks = []
            errors = []

            for email in emails:
                try:
                    task_item = EmailMessageTransformer.email_to_task_item(email, mission_id)
                    created_tasks.append(task_item)
                except Exception as e:
                    logger.error(f"Error transforming email {email.message_id}: {e}")
                    errors.append({"email_id": email.message_id, "error": str(e)})

            # Store sync history
            self.sync_history[provider_type] = {
                "timestamp": datetime.now().isoformat(),
                "emails_synced": len(emails),
                "tasks_created": len(created_tasks),
                "errors": len(errors),
            }

            self.sync_status = "idle"

            return {
                "status": "success",
                "provider": provider_type,
                "mission_id": mission_id,
                "timestamp": datetime.now().isoformat(),
                "emails_synced": len(emails),
                "tasks_created": len(created_tasks),
                "errors": errors,
                "tasks": created_tasks,
            }

        except Exception as e:
            logger.error(f"Email sync error: {e}")
            self.sync_status = "error"
            return {"status": "error", "error": str(e)}

    async def fetch_emails(
        self, provider_type: str, query: str = "", limit: int = 50
    ) -> List[Dict]:
        """Fetch emails from external provider.

        Args:
            provider_type: Email provider type
            query: Search/filter query
            limit: Max emails to return

        Returns:
            List of email message dicts
        """
        logger.info(
            f"Fetching emails from {provider_type} "
            f"(query='{query}', limit={limit})"
        )

        try:
            # Get or create provider
            if provider_type not in self.email_providers:
                provider = EmailProviderFactory.create_provider(provider_type)
                if not provider:
                    return []
                self.email_providers[provider_type] = provider

            provider = self.email_providers[provider_type]

            # Get credentials and authenticate
            credentials = await self.oauth_manager.get_credentials(provider_type)
            if not credentials or not await provider.authenticate(credentials):
                logger.warning(f"Cannot authenticate {provider_type}")
                return []

            # Fetch messages
            emails = await provider.fetch_messages(query or "", limit)
            logger.info(f"Retrieved {len(emails)} emails from {provider_type}")

            return [
                {
                    "id": e.message_id,
                    "subject": e.subject,
                    "from": e.from_addr,
                    "timestamp": e.timestamp.isoformat() if e.timestamp else None,
                    "provider": e.provider,
                    "is_unread": e.is_unread,
                }
                for e in emails
            ]

        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return []

    async def create_task_from_email(
        self, mission_id: str, email: Dict[str, Any]
    ) -> str:
        """Create a Binder task from email.

        Args:
            mission_id: Target mission ID
            email: Email message dict with email data

        Returns:
            Created task ID
        """
        logger.info(
            f"Creating task from email '{email.get('subject')}' in mission {mission_id}"
        )

        try:
            # Transform email to Binder task
            from core.sync.base_providers import EmailMessage

            email_msg = EmailMessage(
                message_id=email.get('id', ''),
                subject=email.get('subject', 'No subject'),
                from_addr=email.get('from', 'unknown'),
                to_addrs=email.get('to', []),
                body=email.get('body', ''),
                timestamp=datetime.fromisoformat(email.get('timestamp', '')),
                thread_id=email.get('thread_id'),
                labels=email.get('labels', []),
                provider=email.get('provider', 'unknown'),
                is_unread=email.get('is_unread', False),
            )

            task_item = EmailMessageTransformer.email_to_task_item(email_msg, mission_id)

            # TODO: Persist to Binder using VibeBinderService
            # For now, return the task ID
            return task_item['id']

        except Exception as e:
            logger.error(f"Error creating task from email: {e}")
            raise

    # ==================== Project Management ====================

    async def sync_jira(
        self, workspace_id: str, mission_id: str, jql: Optional[str] = None,
        credentials: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Synchronize with Jira instance.

        Args:
            workspace_id: Jira workspace/instance ID
            mission_id: Target mission ID for created tasks
            jql: Jira Query Language filter
            credentials: Jira credentials (instance_url, email, api_token)

        Returns:
            Sync result dict
        """
        logger.info(f"Starting Jira sync for workspace {workspace_id} to mission {mission_id}")
        self.sync_status = "syncing"

        try:
            # Initialize Jira manager if needed
            if "jira" not in self.project_managers:
                self.project_managers["jira"] = ProjectManagerFactory.create_provider("jira")

            jira_mgr = self.project_managers["jira"]
            if not jira_mgr:
                logger.error("Failed to create Jira manager")
                return {"status": "error", "error": "Failed to create Jira manager"}

            # Get credentials from OAuth manager if not provided
            if not credentials:
                credentials = await self.oauth_manager.get_credentials("jira")
                if not credentials:
                    return {"status": "error", "error": "No Jira credentials found"}

            # Authenticate
            if not await jira_mgr.authenticate(credentials):
                return {"status": "error", "error": "Jira authentication failed"}

            # Fetch issues from Jira
            jql = jql or "order by updated DESC"
            issues = await jira_mgr.fetch_issues(
                query=jql,
                filters={"max_results": 50}
            )

            logger.info(f"Fetched {len(issues)} Jira issues")

            # Transform and create tasks
            created_tasks = []
            for issue in issues:
                task_item = IssueTransformer.issue_to_task_item(issue, mission_id)
                # TODO: Persist to Binder using VibeBinderService
                created_tasks.append({"id": task_item["id"], "title": task_item["title"]})

            # Update sync history
            self.sync_history["jira"] = {
                "last_sync": datetime.now().isoformat(),
                "issues_synced": len(issues),
                "tasks_created": len(created_tasks),
            }

            self.sync_status = "idle"
            return {
                "status": "success",
                "provider": "jira",
                "workspace_id": workspace_id,
                "mission_id": mission_id,
                "issues_synced": len(issues),
                "tasks_created": len(created_tasks),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Jira sync error: {e}")
            self.sync_status = "error"
            return {"status": "error", "error": str(e)}

    async def sync_linear(
        self, team_id: str, mission_id: str, status_filter: Optional[str] = None,
        credentials: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Synchronize with Linear workspace.

        Args:
            team_id: Linear team/workspace ID
            mission_id: Target mission ID for created tasks
            status_filter: Status filter (e.g., 'active', 'completed')
            credentials: Linear credentials (api_key)

        Returns:
            Sync result dict
        """
        logger.info(f"Starting Linear sync for team {team_id} to mission {mission_id}")
        self.sync_status = "syncing"

        try:
            # Initialize Linear manager if needed
            if "linear" not in self.project_managers:
                self.project_managers["linear"] = ProjectManagerFactory.create_provider("linear")

            linear_mgr = self.project_managers["linear"]
            if not linear_mgr:
                logger.error("Failed to create Linear manager")
                return {"status": "error", "error": "Failed to create Linear manager"}

            # Get credentials from OAuth manager if not provided
            if not credentials:
                credentials = await self.oauth_manager.get_credentials("linear")
                if not credentials:
                    return {"status": "error", "error": "No Linear credentials found"}

            # Authenticate
            if not await linear_mgr.authenticate(credentials):
                return {"status": "error", "error": "Linear authentication failed"}

            # Fetch issues from Linear
            filters = {"team_id": team_id, "max_results": 50}
            if status_filter:
                filters["status"] = status_filter

            issues = await linear_mgr.fetch_issues(
                query="",
                filters=filters
            )

            logger.info(f"Fetched {len(issues)} Linear issues")

            # Transform and create tasks
            created_tasks = []
            for issue in issues:
                task_item = IssueTransformer.issue_to_task_item(issue, mission_id)
                # TODO: Persist to Binder using VibeBinderService
                created_tasks.append({"id": task_item["id"], "title": task_item["title"]})

            # Update sync history
            self.sync_history["linear"] = {
                "last_sync": datetime.now().isoformat(),
                "issues_synced": len(issues),
                "tasks_created": len(created_tasks),
            }

            self.sync_status = "idle"
            return {
                "status": "success",
                "provider": "linear",
                "team_id": team_id,
                "mission_id": mission_id,
                "issues_synced": len(issues),
                "tasks_created": len(created_tasks),
                "timestamp": datetime.now().isoformat(),
            }

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
            if provider == "jira":
                if "jira" not in self.project_managers:
                    self.project_managers["jira"] = ProjectManagerFactory.create_provider("jira")
                mgr = self.project_managers["jira"]
                if mgr:
                    return await mgr.handle_webhook(payload)

            elif provider == "linear":
                if "linear" not in self.project_managers:
                    self.project_managers["linear"] = ProjectManagerFactory.create_provider("linear")
                mgr = self.project_managers["linear"]
                if mgr:
                    return await mgr.handle_webhook(payload)

            return {
                "status": "received",
                "provider": provider,
                "message": "Webhook received but provider not configured",
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

    async def create_task_from_issue(
        self, mission_id: str, issue: Dict[str, Any]
    ) -> str:
        """Create a Binder task from a project management issue.

        Args:
            mission_id: Target mission ID
            issue: Issue dict with issue data

        Returns:
            Created task ID
        """
        logger.info(
            f"Creating task from issue '{issue.get('title')}' in mission {mission_id}"
        )

        try:
            # Transform issue to Binder task
            from core.sync.base_providers import Issue

            issue_obj = Issue(
                id=issue.get('id', ''),
                key=issue.get('key', ''),
                title=issue.get('title', 'No title'),
                description=issue.get('description', ''),
                status=issue.get('status', 'todo'),
                assignee=issue.get('assignee'),
                created_at=datetime.fromisoformat(issue.get('created_at', datetime.now().isoformat())),
                updated_at=datetime.fromisoformat(issue.get('updated_at', datetime.now().isoformat())),
                due_date=datetime.fromisoformat(issue.get('due_date')) if issue.get('due_date') else None,
                url=issue.get('url', ''),
                provider=issue.get('provider', 'unknown'),
                custom_fields=issue.get('custom_fields', {}),
            )

            task_item = IssueTransformer.issue_to_task_item(issue_obj, mission_id)

            # TODO: Persist to Binder using VibeBinderService
            # For now, return the task ID
            return task_item['id']

        except Exception as e:
            logger.error(f"Error creating task from issue: {e}")
            raise

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
