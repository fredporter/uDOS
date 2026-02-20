"""Data transformation pipeline for external events → Binder items (Phase 8.2)."""

from datetime import datetime
from typing import Dict, Any, Optional
from core.sync.base_providers import CalendarEvent, EmailMessage, Issue, SlackMessage
from core.services.logging_manager import get_logger

logger = get_logger(__name__)


class CalendarEventTransformer:
    """Transform calendar events into Binder task items."""

    @staticmethod
    def event_to_task_item(event: CalendarEvent, mission_id: str) -> Dict[str, Any]:
        """Convert calendar event to Binder task item (Phase 6 format).

        Args:
            event: CalendarEvent from external provider
            mission_id: Target mission ID in Binder

        Returns:
            Task item dict in Phase 6 unified format
        """
        try:
            task_item = {
                "id": f"task-{event.id}",
                "type": "task",
                "title": event.title,
                "description": (
                    f"Calendar event from {event.provider}\n\n{event.description}"
                    if event.description
                    else f"Calendar event from {event.provider}"
                ),
                "status": "todo",
                "parent_mission": mission_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "due_date": event.end_time.isoformat(),
                "tags": ["calendar_sync", event.provider],
                "metadata": {
                    "external_id": event.id,
                    "external_provider": event.provider,
                    "location": event.location,
                    "is_all_day": event.is_all_day,
                    "attendees": event.attendees or [],
                    "start_time": event.start_time.isoformat(),
                    "end_time": event.end_time.isoformat(),
                },
            }

            logger.info(f"Transformed calendar event to task: {task_item['id']}")
            return task_item

        except Exception as e:
            logger.error(f"Error transforming calendar event: {e}")
            raise


class EmailMessageTransformer:
    """Transform email messages into Binder task items."""

    @staticmethod
    def email_to_task_item(email: EmailMessage, mission_id: str) -> Dict[str, Any]:
        """Convert email message to Binder task item.

        Args:
            email: EmailMessage from external provider
            mission_id: Target mission ID in Binder

        Returns:
            Task item dict in Phase 6 unified format
        """
        try:
            task_item = {
                "id": f"task-{email.message_id}",
                "type": "task",
                "title": email.subject,
                "description": (
                    f"Email from {email.from_addr}\n\n{email.body[:1000]}"
                ),
                "status": "todo",
                "parent_mission": mission_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "due_date": (email.timestamp + timedelta(days=1)).isoformat()
                if email.timestamp
                else datetime.now().isoformat(),
                "tags": ["email_sync", email.provider] + (email.labels or []),
                "metadata": {
                    "external_id": email.message_id,
                    "external_provider": email.provider,
                    "from": email.from_addr,
                    "to": email.to_addrs,
                    "thread_id": email.thread_id,
                    "is_unread": email.is_unread,
                    "attachments": email.attachments or [],
                    "received_at": email.timestamp.isoformat()
                    if email.timestamp
                    else None,
                },
            }

            logger.info(f"Transformed email to task: {task_item['id']}")
            return task_item

        except Exception as e:
            logger.error(f"Error transforming email: {e}")
            raise


class IssueTransformer:
    """Transform project management issues into Binder task items."""

    @staticmethod
    def issue_to_task_item(issue: Issue, mission_id: str) -> Dict[str, Any]:
        """Convert issue to Binder task item.

        Args:
            issue: Issue from Jira/Linear
            mission_id: Target mission ID in Binder

        Returns:
            Task item dict in Phase 6 unified format
        """
        try:
            task_item = {
                "id": f"issue-{issue.id}",
                "type": "issue",
                "title": f"[{issue.key}] {issue.title}",
                "description": issue.description or "No description provided",
                "status": _map_issue_status_to_task_status(issue.status),
                "parent_mission": mission_id,
                "created_at": issue.created_at.isoformat(),
                "updated_at": issue.updated_at.isoformat(),
                "due_date": issue.due_date.isoformat() if issue.due_date else None,
                "assigned_to": issue.assignee,
                "tags": [issue.provider, issue.key.split("-")[0].upper()],
                "metadata": {
                    "external_id": issue.id,
                    "external_provider": issue.provider,
                    "issue_key": issue.key,
                    "issue_status": issue.status,
                    "issue_url": issue.url,
                    "custom_fields": issue.custom_fields or {},
                },
            }

            logger.info(f"Transformed issue to unified format: {task_item['id']}")
            return task_item

        except Exception as e:
            logger.error(f"Error transforming issue: {e}")
            raise


class SlackMessageTransformer:
    """Transform Slack messages into Binder task items."""

    @staticmethod
    def slack_to_task_item(
        message: SlackMessage, mission_id: str
    ) -> Dict[str, Any]:
        """Convert Slack message to Binder task item.

        Args:
            message: SlackMessage from Slack API
            mission_id: Target mission ID in Binder

        Returns:
            Task item dict in Phase 6 unified format
        """
        try:
            task_item = {
                "id": f"task-{message.message_id}",
                "type": "task",
                "title": (
                    message.text[:80].split("\n")[0]
                    if message.text
                    else "Slack message"
                ),
                "description": (
                    f"Slack message from <@{message.user_id}>\n\n{message.text[:500]}"
                ),
                "status": "todo",
                "parent_mission": mission_id,
                "created_at": datetime.fromtimestamp(message.timestamp).isoformat(),
                "updated_at": datetime.now().isoformat(),
                "due_date": (
                    datetime.fromtimestamp(message.timestamp)
                    .replace(hour=17, minute=0, second=0)
                    .isoformat()
                ),
                "tags": ["slack_sync", f"channel-{message.channel_id}"],
                "metadata": {
                    "external_id": message.message_id,
                    "external_provider": "slack",
                    "channel_id": message.channel_id,
                    "user_id": message.user_id,
                    "thread_ts": message.thread_ts,
                    "reaction_count": sum(message.reactions.values())
                    if message.reactions
                    else 0,
                    "attachments": message.attachments or [],
                },
            }

            logger.info(f"Transformed Slack message to task: {task_item['id']}")
            return task_item

        except Exception as e:
            logger.error(f"Error transforming Slack message: {e}")
            raise


def _map_issue_status_to_task_status(issue_status: str) -> str:
    """Map project management issue status to Binder task status.

    Args:
        issue_status: Status from Jira/Linear (e.g., 'In Progress', 'Done')

    Returns:
        Binder task status (todo, in-progress, done, blocked)
    """
    status_map = {
        "todo": "todo",
        "to do": "todo",
        "backlog": "todo",
        "open": "todo",
        "new": "todo",
        "in progress": "in-progress",
        "in_progress": "in-progress",
        "doing": "in-progress",
        "in development": "in-progress",
        "developing": "in-progress",
        "done": "done",
        "completed": "done",
        "closed": "done",
        "resolved": "done",
        "blocked": "blocked",
        "on hold": "blocked",
        "paused": "blocked",
    }

    normalized = issue_status.lower().strip()
    return status_map.get(normalized, "todo")


from datetime import timedelta  # Import at end to handle circular deps

__all__ = [
    "CalendarEventTransformer",
    "EmailMessageTransformer",
    "IssueTransformer",
    "SlackMessageTransformer",
]
