"""
Vibe TUI Service

Handles interactive TUI operations for ucode terminal interface.
Provides vibe skill actions for:
- Launching TUI views and interactions
- Binder/mission exploration
- Task/move browsing and management
- Real-time terminal UI control
"""

from typing import Dict, Any, Optional, List
import os
from pathlib import Path

from core.services.logging_manager import get_logger

_logger = get_logger(__name__)
_tui_service_instance = None


class VibeUCodeTUIService:
    """
    Manage ucode terminal UI interactions.

    Exposes TUI views for Vibe skill system through ucli:
    - UCODE BINDER: Interactive binder explorer
    - UCODE TASKS: Task/move browser with filtering
    - UCODE MISSIONS: Mission selector and detail view
    - UCODE SEARCH: Full-text search in tasks
    """

    def __init__(self):
        """Initialize TUI service."""
        self.logger = get_logger("vibe-tui-service")

    def launch_binder_ui(self, mission_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Launch interactive binder UI for mission.

        Args:
            mission_id: Optional specific mission to focus on

        Returns:
            Status dict with UI control info
        """
        try:
            self.logger.info(f"Launching binder UI for mission: {mission_id or 'all'}")

            return {
                "status": "success",
                "message": f"Binder UI launched",
                "mode": "interactive",
                "view": "binder",
                "mission_id": mission_id,
                "controls": {
                    "navigation": ["arrows", "hjkl"],
                    "actions": ["enter", "e", "d", "c", "q"],
                    "shortcuts": {
                        "e": "edit",
                        "d": "delete",
                        "c": "complete",
                        "a": "add",
                        "f": "filter",
                        "/": "search",
                        "?": "help",
                    },
                },
                "rendered": f"🎯 Binder UI - {mission_id or 'All Missions'}\n\nPress '?' for help, 'q' to quit"
            }
        except Exception as e:
            self.logger.error(f"Failed to launch binder UI: {e}")
            return {
                "status": "error",
                "message": f"Failed to launch binder UI: {e}",
            }

    def launch_tasks_ui(
        self,
        mission_id: str,
        status: Optional[str] = None,
        item_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Launch tasks/moves browser for mission.

        Args:
            mission_id: Mission ID to browse
            status: Filter by status (optional)
            item_type: Filter by item type (optional)

        Returns:
            Status dict with UI control info
        """
        try:
            self.logger.info(f"Launching tasks UI for mission: {mission_id}")

            filters = []
            if status:
                filters.append(f"status={status}")
            if item_type:
                filters.append(f"type={item_type}")

            filter_text = f" (Filters: {', '.join(filters)})" if filters else ""

            return {
                "status": "success",
                "message": "Tasks UI launched",
                "mode": "interactive",
                "view": "tasks",
                "mission_id": mission_id,
                "filters": {
                    "status": status,
                    "item_type": item_type,
                },
                "controls": {
                    "navigation": ["arrows", "hjkl", "pg_up", "pg_down"],
                    "actions": ["enter", "e", "d", "x", "q"],
                    "shortcuts": {
                        "e": "edit task",
                        "d": "delete task",
                        "x": "toggle status",
                        "a": "add task",
                        "f": "filter",
                        "s": "sort",
                        "/": "search",
                        "?": "help",
                    },
                },
                "rendered": f"📋 Tasks - {mission_id}{filter_text}\n\nPress '?' for help, 'q' to quit"
            }
        except Exception as e:
            self.logger.error(f"Failed to launch tasks UI: {e}")
            return {
                "status": "error",
                "message": f"Failed to launch tasks UI: {e}",
            }

    def launch_missions_ui(self) -> Dict[str, Any]:
        """
        Launch missions selector and detail view.

        Returns:
            Status dict with UI control info
        """
        try:
            self.logger.info("Launching missions UI")

            return {
                "status": "success",
                "message": "Missions UI launched",
                "mode": "interactive",
                "view": "missions",
                "controls": {
                    "navigation": ["arrows", "hjkl"],
                    "actions": ["enter", "n", "d", "q"],
                    "shortcuts": {
                        "enter": "open mission",
                        "n": "new mission",
                        "d": "delete mission",
                        "e": "edit mission",
                        "f": "filter",
                        "/": "search",
                        "?": "help",
                    },
                },
                "rendered": "🗂️  Missions\n\nPress '?' for help, 'q' to quit"
            }
        except Exception as e:
            self.logger.error(f"Failed to launch missions UI: {e}")
            return {
                "status": "error",
                "message": f"Failed to launch missions UI: {e}",
            }

    def launch_search_ui(self, query: Optional[str] = None) -> Dict[str, Any]:
        """
        Launch search interface for tasks and missions.

        Args:
            query: Optional initial search query

        Returns:
            Status dict with UI control info
        """
        try:
            self.logger.info(f"Launching search UI with query: {query or 'empty'}")

            return {
                "status": "success",
                "message": "Search UI launched",
                "mode": "interactive",
                "view": "search",
                "query": query,
                "scopes": ["tasks", "missions", "milestones", "metadata"],
                "controls": {
                    "input": ["type to search"],
                    "actions": ["enter", "tab", "q"],
                    "shortcuts": {
                        "tab": "next result",
                        "shift+tab": "prev result",
                        "enter": "select",
                        "escape": "cancel",
                        "ctrl+a": "select all",
                        "?": "help",
                    },
                },
                "rendered": f"🔍 Search{f' - {query}' if query else ''}\n\nPress '?' for help, 'q' to quit"
            }
        except Exception as e:
            self.logger.error(f"Failed to launch search UI: {e}")
            return {
                "status": "error",
                "message": f"Failed to launch search UI: {e}",
            }

    def launch_statistics_view(self, mission_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Launch statistics and metrics view.

        Args:
            mission_id: Optional mission to show stats for

        Returns:
            Status dict with statistics info
        """
        try:
            self.logger.info(f"Launching statistics view for mission: {mission_id or 'all'}")

            return {
                "status": "success",
                "message": "Statistics view launched",
                "mode": "view",
                "view": "statistics",
                "mission_id": mission_id,
                "metrics": [
                    "completion_rate",
                    "tasks_by_type",
                    "tasks_by_status",
                    "priority_distribution",
                    "time_to_completion",
                    "imported_items_summary",
                ],
                "rendered": f"📊 Statistics{f' - {mission_id}' if mission_id else ''}\n\nLoading metrics..."
            }
        except Exception as e:
            self.logger.error(f"Failed to launch statistics view: {e}")
            return {
                "status": "error",
                "message": f"Failed to launch statistics view: {e}",
            }

    def launch_help_ui(self, topic: Optional[str] = None) -> Dict[str, Any]:
        """
        Launch help interface.

        Args:
            topic: Optional specific topic to show help for

        Returns:
            Status dict with help info
        """
        try:
            self.logger.info(f"Launching help UI for topic: {topic or 'general'}")

            topics = [
                "binder",
                "tasks",
                "missions",
                "search",
                "shortcuts",
                "workflow",
                "ai_summary",
                "imports",
            ]

            return {
                "status": "success",
                "message": "Help UI launched",
                "mode": "view",
                "view": "help",
                "topic": topic or "general",
                "available_topics": topics,
                "rendered": f"❓ Help{f' - {topic}' if topic else ''}\n\nPress 'q' to quit"
            }
        except Exception as e:
            self.logger.error(f"Failed to launch help UI: {e}")
            return {
                "status": "error",
                "message": f"Failed to launch help UI: {e}",
            }


def get_tui_service() -> VibeUCodeTUIService:
    """Get or create TUI service instance."""
    global _tui_service_instance
    if _tui_service_instance is None:
        _tui_service_instance = VibeUCodeTUIService()
    return _tui_service_instance
