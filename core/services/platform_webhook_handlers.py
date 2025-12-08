"""
Platform-Specific Webhook Handlers for uDOS v1.2.5

Slack: Slash commands, event subscriptions, interactive messages
Notion: Page updates, database changes
ClickUp: Task updates, comments, status changes
"""

from typing import Dict, List, Optional


class SlackWebhookHandler:
    """Process Slack webhook events."""

    def __init__(self):
        self.command_handlers = {
            '/udos': self.handle_udos_command,
            '/knowledge': self.handle_knowledge_command,
            '/map': self.handle_map_command
        }

    def process_event(self, event_type: str, payload: Dict) -> Dict:
        """Process Slack event."""
        if event_type == 'url_verification':
            # Slack URL verification challenge
            return {
                'status': 'verification',
                'challenge': payload.get('challenge')
            }

        if event_type == 'event_callback':
            return self.handle_event_callback(payload)

        if event_type == 'slash_command':
            return self.handle_slash_command(payload)

        return {'status': 'ignored', 'reason': f'Unknown event type: {event_type}'}

    def handle_event_callback(self, payload: Dict) -> Dict:
        """Handle Slack event callbacks."""
        event = payload.get('event', {})
        event_type = event.get('type', '')

        if event_type == 'message':
            return self.handle_message(event)

        return {'status': 'ignored', 'reason': f'Unhandled event: {event_type}'}

    def handle_message(self, event: Dict) -> Dict:
        """Handle Slack messages."""
        text = event.get('text', '')
        user = event.get('user', '')
        channel = event.get('channel', '')

        # Check for knowledge requests
        if 'knowledge' in text.lower():
            return {
                'status': 'processed',
                'event': 'message',
                'actions': [{
                    'type': 'command',
                    'command': 'KNOWLEDGE SEARCH',
                    'args': {'query': text}
                }]
            }

        return {'status': 'ignored', 'reason': 'No trigger words'}

    def handle_slash_command(self, payload: Dict) -> Dict:
        """Handle Slack slash commands."""
        command = payload.get('command', '')
        text = payload.get('text', '')
        user_id = payload.get('user_id', '')

        handler = self.command_handlers.get(command)
        if handler:
            return handler(text, user_id, payload)

        return {'status': 'ignored', 'reason': f'Unknown command: {command}'}

    def handle_udos_command(self, text: str, user_id: str, payload: Dict) -> Dict:
        """Handle /udos command."""
        return {
            'status': 'processed',
            'event': 'slash_command',
            'command': '/udos',
            'actions': [{
                'type': 'command',
                'command': text.upper(),
                'args': {'slack_user': user_id}
            }]
        }

    def handle_knowledge_command(self, text: str, user_id: str, payload: Dict) -> Dict:
        """Handle /knowledge command."""
        return {
            'status': 'processed',
            'event': 'slash_command',
            'command': '/knowledge',
            'actions': [{
                'type': 'workflow',
                'name': 'knowledge-search',
                'args': {'query': text, 'slack_user': user_id}
            }]
        }

    def handle_map_command(self, text: str, user_id: str, payload: Dict) -> Dict:
        """Handle /map command."""
        return {
            'status': 'processed',
            'event': 'slash_command',
            'command': '/map',
            'actions': [{
                'type': 'command',
                'command': f'MAP {text.upper()}',
                'args': {'slack_user': user_id}
            }]
        }


class NotionWebhookHandler:
    """Process Notion webhook events."""

    def process_event(self, event_type: str, payload: Dict) -> Dict:
        """Process Notion event."""
        # Notion sends all events as 'page' or 'database' updates
        object_type = payload.get('type', '')

        if object_type == 'page':
            return self.handle_page_update(payload)
        elif object_type == 'database':
            return self.handle_database_update(payload)

        return {'status': 'ignored', 'reason': f'Unknown object type: {object_type}'}

    def handle_page_update(self, payload: Dict) -> Dict:
        """Handle Notion page updates."""
        page = payload.get('page', {})
        properties = page.get('properties', {})

        # Check if knowledge-related page
        title = self.extract_title(properties)
        if 'knowledge' in title.lower():
            return {
                'status': 'processed',
                'event': 'page_update',
                'title': title,
                'actions': [{
                    'type': 'workflow',
                    'name': 'notion-sync',
                    'args': {'page_id': page.get('id'), 'title': title}
                }]
            }

        return {'status': 'ignored', 'reason': 'Not a knowledge page'}

    def handle_database_update(self, payload: Dict) -> Dict:
        """Handle Notion database updates."""
        database = payload.get('database', {})
        database_id = database.get('id', '')

        return {
            'status': 'processed',
            'event': 'database_update',
            'database_id': database_id,
            'actions': [{
                'type': 'notification',
                'message': f'Notion database updated: {database_id}'
            }]
        }

    def extract_title(self, properties: Dict) -> str:
        """Extract title from Notion page properties."""
        title_prop = properties.get('title', {})
        if isinstance(title_prop, dict):
            title_content = title_prop.get('title', [])
            if title_content and len(title_content) > 0:
                return title_content[0].get('plain_text', '')
        return ''


class ClickUpWebhookHandler:
    """Process ClickUp webhook events."""

    def process_event(self, event_type: str, payload: Dict) -> Dict:
        """Process ClickUp event."""
        event = payload.get('event', '')

        handlers = {
            'taskCreated': self.handle_task_created,
            'taskUpdated': self.handle_task_updated,
            'taskDeleted': self.handle_task_deleted,
            'taskCommentPosted': self.handle_task_comment
        }

        handler = handlers.get(event)
        if handler:
            return handler(payload)

        return {'status': 'ignored', 'reason': f'Unhandled event: {event}'}

    def handle_task_created(self, payload: Dict) -> Dict:
        """Handle task creation."""
        task_id = payload.get('task_id', '')
        task_name = payload.get('history_items', [{}])[0].get('name', '')

        # Check if knowledge-related task
        if 'knowledge' in task_name.lower():
            return {
                'status': 'processed',
                'event': 'taskCreated',
                'task_id': task_id,
                'task_name': task_name,
                'actions': [{
                    'type': 'workflow',
                    'name': 'clickup-sync',
                    'args': {'task_id': task_id, 'action': 'created'}
                }]
            }

        return {'status': 'ignored', 'reason': 'Not a knowledge task'}

    def handle_task_updated(self, payload: Dict) -> Dict:
        """Handle task updates."""
        task_id = payload.get('task_id', '')

        return {
            'status': 'processed',
            'event': 'taskUpdated',
            'task_id': task_id,
            'actions': [{
                'type': 'notification',
                'message': f'ClickUp task updated: {task_id}'
            }]
        }

    def handle_task_deleted(self, payload: Dict) -> Dict:
        """Handle task deletion."""
        return {'status': 'ignored', 'reason': 'Task deletions not processed'}

    def handle_task_comment(self, payload: Dict) -> Dict:
        """Handle task comments."""
        task_id = payload.get('task_id', '')
        comment = payload.get('history_items', [{}])[0].get('comment', {})
        comment_text = comment.get('text_content', '')

        # Check for @udos mentions
        if '@udos' in comment_text:
            return {
                'status': 'processed',
                'event': 'taskCommentPosted',
                'task_id': task_id,
                'actions': [{
                    'type': 'command',
                    'command': 'ASSIST',
                    'args': {'query': comment_text.replace('@udos', '').strip()}
                }]
            }

        return {'status': 'ignored', 'reason': 'No @udos mention'}


# Global handler instances
_slack_handler = None
_notion_handler = None
_clickup_handler = None


def get_slack_handler() -> SlackWebhookHandler:
    """Get global Slack webhook handler."""
    global _slack_handler
    if _slack_handler is None:
        _slack_handler = SlackWebhookHandler()
    return _slack_handler


def get_notion_handler() -> NotionWebhookHandler:
    """Get global Notion webhook handler."""
    global _notion_handler
    if _notion_handler is None:
        _notion_handler = NotionWebhookHandler()
    return _notion_handler


def get_clickup_handler() -> ClickUpWebhookHandler:
    """Get global ClickUp webhook handler."""
    global _clickup_handler
    if _clickup_handler is None:
        _clickup_handler = ClickUpWebhookHandler()
    return _clickup_handler
