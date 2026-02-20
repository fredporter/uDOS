"""
Vibe CLI Service Handler

Routes CLI commands to Vibe backend services.
Integrates with bin/ucli command dispatcher.

Format: <SKILL> <ACTION> [options]
Examples:
  DEVICE LIST
  VAULT GET api-key
  WORKSPACE SWITCH workspace-id
  WIZARD START task-name
"""

from typing import Dict, Any, Optional, List
import asyncio
import sys

from core.services.logging_manager import get_logger
from core.services.vibe_device_service import get_device_service
from core.services.vibe_vault_service import get_vault_service
from core.services.vibe_workspace_service import get_workspace_service
from core.services.vibe_network_service import get_network_service
from core.services.vibe_script_service import get_script_service
from core.services.vibe_user_service import get_user_service
from core.services.vibe_wizard_service import get_wizard_service
from core.services.vibe_help_service import get_help_service
from core.services.vibe_ask_service import get_ask_service
from core.services.vibe_binder_service import get_binder_service
from core.services.vibe_tui_service import get_tui_service
from core.services.vibe_skill_mapper import get_default_mapper
from core.services.vibe_sync_service import get_sync_service


class VibeCliHandler:
    """Handle Vibe skill commands from CLI."""

    def __init__(self):
        """Initialize CLI handler."""
        self.logger = get_logger("vibe-cli")
        self.mapper = get_default_mapper()

    def is_vibe_command(self, command_text: str) -> bool:
        """
        Check if command is a Vibe skill command.

        Args:
            command_text: Command text (e.g., "DEVICE LIST")

        Returns:
            True if command matches a Vibe skill
        """
        parts = command_text.strip().split(None, 1)
        if not parts:
            return False

        skill_name = parts[0].lower()
        return self.mapper.get_skill(skill_name) is not None

    def execute(self, command_text: str) -> Dict[str, Any]:
        """
        Execute a Vibe skill command.

        Args:
            command_text: Command text (e.g., "DEVICE LIST")

        Returns:
            Dict with status, output, rendered, message
        """
        try:
            parts = command_text.strip().split(None, 2)
            if not parts:
                return self._error("Empty command")

            skill_name = parts[0].lower()
            action = parts[1].upper() if len(parts) > 1 else "HELP"
            args = parts[2].split() if len(parts) > 2 else []

            # Get skill contract
            skill = self.mapper.get_skill(skill_name)
            if not skill:
                return self._error(f"Unknown skill: {skill_name}")

            self.logger.info(f"Executing Vibe command: {skill_name} {action}")

            # Route to skill handler
            handler = getattr(self, f"_handle_{skill_name}", None)
            if handler:
                return handler(action, args)

            return self._error(f"No handler for skill: {skill_name}")

        except Exception as e:
            self.logger.error(f"CLI execution failed: {e}")
            return self._error(str(e))

    def _handle_device(self, action: str, args: List[str]) -> Dict[str, Any]:
        """Handle device skill commands."""
        service = get_device_service()

        if action == "LIST":
            result = service.list_devices()
        elif action == "STATUS" and args:
            result = service.device_status(args[0])
        elif action == "ADD" and len(args) >= 3:
            result = service.add_device(args[0], args[1], args[2])
        else:
            result = self._error(f"Unknown device action: {action}")

        return self._format_output(result)

    def _handle_vault(self, action: str, args: List[str]) -> Dict[str, Any]:
        """Handle vault skill commands."""
        service = get_vault_service()

        if action == "LIST":
            result = service.list_keys()
        elif action == "GET" and args:
            result = service.get_secret(args[0])
        elif action == "SET" and len(args) >= 2:
            result = service.set_secret(args[0], args[1])
        elif action == "DELETE" and args:
            result = service.delete_secret(args[0])
        else:
            result = self._error(f"Unknown vault action: {action}")

        return self._format_output(result)

    def _handle_workspace(self, action: str, args: List[str]) -> Dict[str, Any]:
        """Handle workspace skill commands."""
        service = get_workspace_service()

        if action == "LIST":
            result = service.list_workspaces()
        elif action == "SWITCH":
            if args:
                result = service.switch_workspace(args[0])
            else:
                result = self._error_dict(f"workspace {action} requires workspace name")
        elif action == "CREATE":
            if len(args) >= 1:
                desc = args[1] if len(args) > 1 else f"Workspace {args[0]}"
                result = service.create_workspace(args[0], desc)
            else:
                result = self._error_dict(f"workspace {action} requires workspace name")
        elif action == "DELETE":
            if args:
                result = service.delete_workspace(args[0])
            else:
                result = self._error_dict(f"workspace {action} requires workspace name")
        else:
            result = self._error_dict(f"Unknown workspace action: {action}")

        return self._format_output(result)

    def _handle_network(self, action: str, args: List[str]) -> Dict[str, Any]:
        """Handle network skill commands."""
        service = get_network_service()

        if action == "SCAN":
            result = service.scan_network()
        elif action == "CHECK" and args:
            result = service.check_connectivity(args[0])
        elif action == "CONNECT" and len(args) >= 2:
            result = service.connect_host(args[0], int(args[1]))
        else:
            result = self._error(f"Unknown network action: {action}")

        return self._format_output(result)

    def _handle_script(self, action: str, args: List[str]) -> Dict[str, Any]:
        """Handle script skill commands."""
        service = get_script_service()

        if action == "LIST":
            result = service.list_scripts()
        elif action == "RUN" and args:
            result = service.run_script(args[0], args[1:])
        elif action == "EDIT" and len(args) >= 2:
            result = service.edit_script(args[0], args[1])
        else:
            result = self._error(f"Unknown script action: {action}")

        return self._format_output(result)

    def _handle_user(self, action: str, args: List[str]) -> Dict[str, Any]:
        """Handle user skill commands."""
        service = get_user_service()

        if action == "LIST":
            result = service.list_users()
        elif action == "ADD" and len(args) >= 3:
            result = service.add_user(args[0], args[1], args[2])
        elif action == "REMOVE" and args:
            result = service.remove_user(args[0])
        else:
            result = self._error(f"Unknown user action: {action}")

        return self._format_output(result)

    def _handle_wizard(self, action: str, args: List[str]) -> Dict[str, Any]:
        """Handle wizard skill commands."""
        service = get_wizard_service()

        if action == "LIST":
            result = service.list_tasks()
        elif action == "START":
            if args:
                result = service.start_task(args[0])
            else:
                result = self._error_dict(f"wizard {action} requires task name")
        elif action == "STOP":
            if args:
                result = service.stop_task(args[0])
            else:
                result = self._error_dict(f"wizard {action} requires task id")
        elif action == "STATUS":
            if args:
                result = service.task_status(args[0])
            else:
                result = self._error_dict(f"wizard {action} requires task id")
        else:
            result = self._error_dict(f"Unknown wizard action: {action}")

        return self._format_output(result)

    def _handle_help(self, action: str, args: List[str]) -> Dict[str, Any]:
        """Handle help skill commands."""
        service = get_help_service()

        if action == "LIST" or action == "COMMANDS":
            result = service.list_commands()
        elif action == "GUIDE" and args:
            result = service.get_guide(args[0])
        else:
            result = self._error(f"Unknown help action: {action}")

        return self._format_output(result)

    def _handle_ask(self, action: str, args: List[str]) -> Dict[str, Any]:
        """Handle ask skill commands."""
        service = get_ask_service()

        if action == "QUERY" and args:
            prompt = " ".join(args)
            result = service.query(prompt)
        elif action == "EXPLAIN" and args:
            topic = args[0]
            detail = args[1].lower() if len(args) > 1 else "medium"
            result = service.explain(topic, detail)
        elif action == "SUGGEST" and args:
            context = " ".join(args)
            result = service.suggest(context)
        else:
            result = self._error(f"Unknown ask action: {action}")

        return self._format_output(result)

    def _handle_binder(self, action: str, args: List[str]) -> Dict[str, Any]:
        """Handle binder skill commands (unified task management)."""
        service = get_binder_service()

        if action == "LIST":
            result = service.list_binders()
        elif action == "CREATE" and len(args) >= 2:
            mission_id = args[0]
            name = args[1]
            template = args[2].lower() if len(args) > 2 else None
            result = service.initialize_project(mission_id, name, template)
        elif action == "GET" and args:
            result = service.get_mission(args[0])
        elif action == "ADD_TASK" and len(args) >= 2:
            mission_id = args[0]
            title = args[1]
            description = args[2] if len(args) > 2 else None
            result = service.add_move(mission_id, title, description, "task")
        elif action == "ADD_CALENDAR" and len(args) >= 2:
            mission_id = args[0]
            title = args[1]
            start_date = args[2] if len(args) > 2 else None
            end_date = args[3] if len(args) > 3 else None
            result = service.add_calendar_event(mission_id, title, start_date, end_date)
        elif action == "ADD_IMPORT" and len(args) >= 3:
            mission_id = args[0]
            title = args[1]
            source = args[2]
            source_id = args[3] if len(args) > 3 else None
            result = service.add_imported_item(mission_id, title, source, source_id)
        elif action == "LIST_TASKS" and args:
            mission_id = args[0]
            status = args[1].lower() if len(args) > 1 else None
            result = service.list_moves(mission_id, status)
        elif action == "GET_TASK" and len(args) >= 2:
            mission_id = args[0]
            move_id = args[1]
            moves = service.list_moves(mission_id)
            move = next((m for m in moves.get("moves", []) if m.get("id") == move_id), None)
            result = {"status": "success", "move": move} if move else {"status": "error", "message": "Task not found"}
        elif action == "COMPLETE" and len(args) >= 2:
            mission_id = args[0]
            move_id = args[1]
            result = service.complete_move(mission_id, move_id)
        elif action == "AI_SUMMARY" and args:
            result = service.get_task_summary_for_ai(args[0])
        else:
            result = self._error(f"Unknown binder action: {action}")

        return self._format_output(result)

    def _handle_ucli(self, action: str, args: List[str]) -> Dict[str, Any]:
        """Handle ucli TUI skill commands (interactive UI views)."""
        service = get_tui_service()

        if action == "BINDER":
            mission_id = args[0] if args else None
            result = service.launch_binder_ui(mission_id)
        elif action == "TASKS" and args:
            mission_id = args[0]
            status = args[1].lower() if len(args) > 1 else None
            item_type = args[2] if len(args) > 2 else None
            result = service.launch_tasks_ui(mission_id, status, item_type)
        elif action == "MISSIONS":
            result = service.launch_missions_ui()
        elif action == "SEARCH":
            query = args[0] if args else None
            result = service.launch_search_ui(query)
        elif action == "STATISTICS":
            mission_id = args[0] if args else None
            result = service.launch_statistics_view(mission_id)
        elif action == "HELP":
            topic = args[0] if args else None
            result = service.launch_help_ui(topic)
        else:
            result = self._error(f"Unknown ucode action: {action}")

        return self._format_output(result)

    def _handle_sync(self, action: str, args: List[str]) -> Dict[str, Any]:
        """Handle sync skill commands (external system synchronization)."""
        service = get_sync_service()

        if action == "CALENDAR" and len(args) >= 2:
            provider = args[0]
            mission_id = args[1]
            result = self._run_async(service.sync_calendar(provider, mission_id))
        elif action == "EMAIL" and len(args) >= 2:
            provider = args[0]
            mission_id = args[1]
            result = self._run_async(service.sync_emails(provider, mission_id))
        elif action == "JIRA" and len(args) >= 2:
            workspace_id = args[0]
            mission_id = args[1]
            jql = args[2] if len(args) > 2 else None
            result = self._run_async(service.sync_jira(workspace_id, mission_id, jql))
        elif action == "LINEAR" and len(args) >= 2:
            team_id = args[0]
            mission_id = args[1]
            status_filter = args[2] if len(args) > 2 else None
            result = self._run_async(service.sync_linear(team_id, mission_id, status_filter))
        elif action == "SLACK" and len(args) >= 2:
            workspace = args[0]
            mission_id = args[1]
            channels = args[2:] if len(args) > 2 else None
            result = self._run_async(service.sync_slack(workspace, mission_id, channels))
        elif action == "ALL" and args:
            systems = args[1:] if len(args) > 1 else None
            result = self._run_async(service.trigger_full_sync(systems))
        elif action == "STATUS":
            result = self._run_async(service.get_sync_status())
        else:
            result = self._error(f"Unknown sync action: {action}")

        return self._format_output(result)

    def _run_async(self, coro):
        """Run async coroutine in CLI context."""
        return asyncio.run(coro)

    def _format_output(self, service_result: Dict[str, Any]) -> Dict[str, Any]:
        """Format service result for CLI output."""
        status = service_result.get("status", "unknown")

        # Build human-readable output
        lines = []

        if status == "success":
            lines.append(f"✓ {service_result.get('message', 'Success')}")
        elif status == "error":
            lines.append(f"✗ Error: {service_result.get('message', 'Unknown error')}")
        else:
            lines.append(f"⚠ {service_result.get('message', 'Request pending')}")

        # Add data if present
        if "devices" in service_result:
            lines.append(f"Devices: {len(service_result['devices'])}")
            for device in service_result["devices"][:5]:  # Show first 5
                lines.append(f"  - {device.get('name', device.get('id'))}: {device.get('status', 'unknown')}")

        if "workspaces" in service_result:
            lines.append(f"Workspaces: {len(service_result['workspaces'])}")
            for ws in service_result["workspaces"][:5]:
                lines.append(f"  - {ws.get('name')}: {ws.get('description', '')}")

        if "tasks" in service_result:
            lines.append(f"Tasks: {len(service_result['tasks'])}")
            for task in service_result["tasks"][:5]:
                lines.append(f"  - {task.get('name')}: {task.get('status', 'idle')}")

        if "response" in service_result:
            lines.append(service_result["response"])

        if "commands" in service_result:
            lines.append(f"Commands available: {service_result.get('count', 0)}")
            for cmd in service_result["commands"][:10]:
                lines.append(f"  {cmd.get('name'):<15} {cmd.get('description', '')}")

        output = "\n".join(lines)

        return {
            "status": status,
            "output": output,
            "rendered": output,
            "message": service_result.get("message", ""),
            "data": service_result,
        }

    def _error(self, message: str) -> Dict[str, Any]:
        """Format error response for direct return (pre-formatted)."""
        return {
            "status": "error",
            "message": message,
            "output": f"✗ Error: {message}",
            "rendered": f"✗ Error: {message}",
        }

    def _error_dict(self, message: str) -> Dict[str, Any]:
        """Return raw error dict for _format_output."""
        return {
            "status": "error",
            "message": message,
        }


# Global handler
_handler: Optional[VibeCliHandler] = None


def get_cli_handler() -> VibeCliHandler:
    """Get or create CLI handler."""
    global _handler
    if _handler is None:
        _handler = VibeCliHandler()
    return _handler


def handle_vibe_command(command_text: str) -> Dict[str, Any]:
    """
    Handle a Vibe skill command.

    Args:
        command_text: Command text (e.g., "DEVICE LIST")

    Returns:
        Dict with status, output, message
    """
    handler = get_cli_handler()
    return handler.execute(command_text)
