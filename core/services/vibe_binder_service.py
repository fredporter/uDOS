"""
Vibe Binder Service

Manages missions, tasks, and milestones within uDOS binders.
Each binder represents a project with workflow files:
- mission.json: Mission definition, guidelines, process
- moves.json: Active tasks/moves (unified JSON format for AI ingestion)
- milestones.json: Completed tasks/achievements

Supports multiple item types in moves.json:
- task: Standard work items
- calendar_event: Calendar events mapped as tasks
- invite: Meeting/event invitations
- reminder: Time-sensitive reminders
- imported: Generic imported items from external systems
"""

import os
import json
import uuid
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict

from core.services.logging_manager import get_logger
from core.services.persistence_service import get_persistence_service

_logger = get_logger(__name__)
_binder_service_instance = None


@dataclass
class Mission:
    """Mission definition."""
    id: str
    name: str
    description: str
    guidelines: str
    process: str
    created: str
    updated: str


@dataclass
class Move:
    """
    Enhanced active task/move with support for multiple item types.

    Unified format suitable for AI ingestion:
    - Consistent schema across all item types
    - Extensible metadata for custom fields
    - Source tracking for imported items
    - Multiple date fields for scheduling
    """
    id: str
    mission_id: str
    title: str
    description: str
    item_type: str  # "task", "calendar_event", "invite", "reminder", "imported"
    status: str  # "todo", "in_progress", "blocked", "review", "done", "archived"
    priority: Optional[str] = None  # "high", "medium", "low"
    assigned_to: Optional[str] = None
    tags: Optional[List[str]] = None

    # Date fields (for calendar events, reminders, deadlines)
    due_date: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    # Participants (for invites, meetings)
    organizer: Optional[str] = None
    attendees: Optional[List[Dict[str, Any]]] = None

    # Source tracking (for imported items)
    source: str = "manual"  # "manual", "calendar", "invite", "reminder", "email", etc.
    source_id: Optional[str] = None  # Original ID from source system

    # Extensible metadata for AI ingestion and future features
    metadata: Optional[Dict[str, Any]] = None

    # Timestamps
    created: str = None
    updated: str = None
    completed: Optional[str] = None


@dataclass
class Milestone:
    """Completed task/achievement."""
    id: str
    mission_id: str
    title: str
    description: str
    item_type: str = "task"
    completed: str = None
    achievements: List[str] = None


class VibeBinderService:
    """
    Manage missions, tasks (moves), and completed tasks (milestones)
    within project binders in vault/@binders/.
    """

    _DATA_FILE = "binders"

    def __init__(self):
        """Initialize binder service."""
        self.logger = get_logger("vibe-binder-service")
        self.persistence_service = get_persistence_service()
        self.vault_root = Path(os.getenv("VAULT_ROOT", "./vault"))
        self.binder_root = self.vault_root / "@binders"

        # Ensure binder directory exists
        self.binder_root.mkdir(parents=True, exist_ok=True)

        # Cache: mission_id -> {mission, moves, milestones}
        self.binders: Dict[str, Dict[str, Any]] = {}
        self._load_binders()

    def _load_binders(self) -> None:
        """Load all binders from vault/@binders/ directory."""
        self.logger.debug(f"Loading binders from {self.binder_root}")

        if not self.binder_root.exists():
            self.logger.warning(f"Binder directory not found: {self.binder_root}")
            return

        # Scan for mission directories
        for mission_dir in self.binder_root.iterdir():
            if not mission_dir.is_dir() or mission_dir.name.startswith("."):
                continue

            mission_id = mission_dir.name

            try:
                # Load mission.json
                mission_file = mission_dir / "mission.json"
                moves_file = mission_dir / "moves.json"
                milestones_file = mission_dir / "milestones.json"

                mission_data = self._load_json(mission_file) if mission_file.exists() else {}
                moves_data = self._load_json(moves_file) if moves_file.exists() else {}
                milestones_data = self._load_json(milestones_file) if milestones_file.exists() else {}

                self.binders[mission_id] = {
                    "mission": mission_data,
                    "moves": moves_data.get("moves", []),
                    "milestones": milestones_data.get("milestones", []),
                }

                self.logger.info(f"Loaded binder: {mission_id}")
            except Exception as e:
                self.logger.error(f"Error loading binder {mission_id}: {e}")

        # Also load from persistence (for binder state tracking)
        data = self.persistence_service.read_data(self._DATA_FILE)
        if data:
            self.logger.debug("Loaded binder state from persistence")

    def _load_json(self, file_path: Path) -> Dict[str, Any]:
        """Helper to load JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading {file_path}: {e}")
            return {}

    def _save_mission_file(self, mission_id: str, filename: str, data: Dict[str, Any]) -> bool:
        """Save mission-specific JSON file."""
        mission_dir = self.binder_root / mission_id
        mission_dir.mkdir(parents=True, exist_ok=True)

        file_path = mission_dir / filename

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            self.logger.error(f"Error saving {file_path}: {e}")
            return False

    def list_binders(self) -> Dict[str, Any]:
        """List all available binders (missions)."""
        binder_list = []

        for mission_id, binder_data in self.binders.items():
            binder_list.append({
                "mission_id": mission_id,
                "mission": binder_data.get("mission", {}),
                "active_moves": len(binder_data.get("moves", [])),
                "completed_milestones": len(binder_data.get("milestones", [])),
            })

        return {
            "status": "success",
            "binders": binder_list,
            "count": len(binder_list),
        }

    def get_mission(self, mission_id: str) -> Dict[str, Any]:
        """Get mission definition and all related data."""
        if mission_id not in self.binders:
            return {
                "status": "error",
                "message": f"Mission not found: {mission_id}",
            }

        binder_data = self.binders[mission_id]

        return {
            "status": "success",
            "mission_id": mission_id,
            "mission": binder_data.get("mission", {}),
            "active_moves_count": len(binder_data.get("moves", [])),
            "completed_milestones_count": len(binder_data.get("milestones", [])),
        }

    def list_moves(self, mission_id: str, status: Optional[str] = None, item_type: Optional[str] = None) -> Dict[str, Any]:
        """
        List active moves (tasks) for a mission.

        Args:
            mission_id: Target mission
            status: Filter by status (todo, in_progress, done, etc.)
            item_type: Filter by item type (task, calendar_event, invite, reminder, imported)
        """
        if mission_id not in self.binders:
            return {
                "status": "error",
                "message": f"Mission not found: {mission_id}",
            }

        moves = self.binders[mission_id].get("moves", [])

        if status:
            moves = [m for m in moves if m.get("status") == status]

        if item_type:
            moves = [m for m in moves if m.get("item_type") == item_type]

        return {
            "status": "success",
            "mission_id": mission_id,
            "moves": moves,
            "count": len(moves),
        }

    def list_moves_by_date_range(
        self,
        mission_id: str,
        start_date: str,
        end_date: str,
        date_field: str = "due_date"
    ) -> Dict[str, Any]:
        """
        List moves within a date range.

        Args:
            mission_id: Target mission
            start_date: ISO 8601 datetime
            end_date: ISO 8601 datetime
            date_field: Field to check (due_date, start_date, end_date, created)
        """
        if mission_id not in self.binders:
            return {
                "status": "error",
                "message": f"Mission not found: {mission_id}",
            }

        moves = self.binders[mission_id].get("moves", [])
        filtered = []

        for move in moves:
            date_value = move.get(date_field)
            if date_value and start_date <= date_value <= end_date:
                filtered.append(move)

        return {
            "status": "success",
            "mission_id": mission_id,
            "date_range": {"start": start_date, "end": end_date},
            "moves": filtered,
            "count": len(filtered),
        }

    def list_moves_by_tag(self, mission_id: str, tag: str) -> Dict[str, Any]:
        """
        List moves with a specific tag.

        Args:
            mission_id: Target mission
            tag: Tag to filter by
        """
        if mission_id not in self.binders:
            return {
                "status": "error",
                "message": f"Mission not found: {mission_id}",
            }

        moves = self.binders[mission_id].get("moves", [])
        filtered = [m for m in moves if tag in m.get("tags", [])]

        return {
            "status": "success",
            "mission_id": mission_id,
            "tag": tag,
            "moves": filtered,
            "count": len(filtered),
        }

    def list_moves_by_source(self, mission_id: str, source: str) -> Dict[str, Any]:
        """
        List moves from a specific source (imported items mapping).

        Args:
            mission_id: Target mission
            source: Source system (calendar, invite, email, jira, linear, etc.)
        """
        if mission_id not in self.binders:
            return {
                "status": "error",
                "message": f"Mission not found: {mission_id}",
            }

        moves = self.binders[mission_id].get("moves", [])
        filtered = [m for m in moves if m.get("source") == source]

        return {
            "status": "success",
            "mission_id": mission_id,
            "source": source,
            "moves": filtered,
            "count": len(filtered),
        }

    def add_move(
        self,
        mission_id: str,
        title: str,
        description: str,
        priority: str = "medium",
        item_type: str = "task",
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Add a new move (task) to a mission.

        Supports multiple item types: task, calendar_event, invite, reminder, imported
        Additional fields depend on item_type (see add_calendar_event, add_invite, etc.)
        """
        if mission_id not in self.binders:
            return {
                "status": "error",
                "message": f"Mission not found: {mission_id}",
            }

        # Delegate to specific handlers for other item types
        if item_type == "calendar_event":
            return self.add_calendar_event(mission_id, title, description, **kwargs)
        elif item_type == "invite":
            return self.add_invite(mission_id, title, description, **kwargs)
        elif item_type == "reminder":
            return self.add_reminder(mission_id, title, description, **kwargs)
        elif item_type == "imported":
            return self.add_imported_item(mission_id, title, description, **kwargs)

        # Standard task
        move_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        move = {
            "id": move_id,
            "mission_id": mission_id,
            "title": title,
            "description": description,
            "item_type": item_type,
            "priority": priority,
            "status": "todo",
            "assigned_to": kwargs.get("assigned_to"),
            "tags": kwargs.get("tags", []),
            "due_date": kwargs.get("due_date"),
            "start_date": kwargs.get("start_date"),
            "end_date": kwargs.get("end_date"),
            "source": kwargs.get("source", "manual"),
            "source_id": kwargs.get("source_id"),
            "metadata": kwargs.get("metadata", {}),
            "created": now,
            "updated": now,
        }

        # Add to binder
        self.binders[mission_id]["moves"].append(move)

        # Save moves.json
        moves_data = {"moves": self.binders[mission_id]["moves"]}
        self._save_mission_file(mission_id, "moves.json", moves_data)

        self.logger.info(f"Added {item_type} to mission {mission_id}: {move_id}")

        return {
            "status": "success",
            "message": f"{item_type.title()} added to mission {mission_id}",
            "move_id": move_id,
            "move": move,
        }

    def add_calendar_event(
        self,
        mission_id: str,
        title: str,
        description: str,
        start_date: str,
        end_date: Optional[str] = None,
        location: Optional[str] = None,
        organizer: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Add a calendar event as a task.

        Args:
            mission_id: Target mission
            title: Event title
            description: Event description
            start_date: ISO 8601 datetime (2026-02-20T10:30:00)
            end_date: ISO 8601 datetime (optional)
            location: Event location
            organizer: Who organized the event
            **kwargs: Additional fields (source, source_id, metadata, etc.)
        """
        if mission_id not in self.binders:
            return {
                "status": "error",
                "message": f"Mission not found: {mission_id}",
            }

        move_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        move = {
            "id": move_id,
            "mission_id": mission_id,
            "title": title,
            "description": description,
            "item_type": "calendar_event",
            "status": "todo",
            "priority": kwargs.get("priority"),
            "start_date": start_date,
            "end_date": end_date,
            "location": location,
            "organizer": organizer,
            "attendees": kwargs.get("attendees", []),
            "source": kwargs.get("source", "calendar"),
            "source_id": kwargs.get("source_id"),
            "metadata": {
                **(kwargs.get("metadata", {})),
                "calendar_location": location,
                "recurring": kwargs.get("recurring", False),
            },
            "tags": kwargs.get("tags", ["calendar"]),
            "created": now,
            "updated": now,
        }

        self.binders[mission_id]["moves"].append(move)
        moves_data = {"moves": self.binders[mission_id]["moves"]}
        self._save_mission_file(mission_id, "moves.json", moves_data)

        self.logger.info(f"Added calendar event to mission {mission_id}: {move_id}")

        return {
            "status": "success",
            "message": f"Calendar event '{title}' added to mission {mission_id}",
            "move_id": move_id,
            "move": move,
        }

    def add_invite(
        self,
        mission_id: str,
        title: str,
        description: str,
        organizer: str,
        attendees: List[Dict[str, str]],
        event_date: Optional[str] = None,
        response_due: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Add a meeting invite as a task.

        Args:
            mission_id: Target mission
            title: Invite/meeting title
            description: Invite description
            organizer: Organizer email/name
            attendees: List of attendee dicts {name, email, status}
            event_date: ISO 8601 datetime
            response_due: Deadline to RSVP
            **kwargs: Additional fields
        """
        if mission_id not in self.binders:
            return {
                "status": "error",
                "message": f"Mission not found: {mission_id}",
            }

        move_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        move = {
            "id": move_id,
            "mission_id": mission_id,
            "title": title,
            "description": description,
            "item_type": "invite",
            "status": "todo",
            "priority": "high",
            "organizer": organizer,
            "attendees": attendees,
            "start_date": event_date,
            "source": kwargs.get("source", "invite"),
            "source_id": kwargs.get("source_id"),
            "metadata": {
                **(kwargs.get("metadata", {})),
                "response_due": response_due,
                "rsvp_required": True,
            },
            "tags": kwargs.get("tags", ["meeting", "invite"]),
            "created": now,
            "updated": now,
        }

        self.binders[mission_id]["moves"].append(move)
        moves_data = {"moves": self.binders[mission_id]["moves"]}
        self._save_mission_file(mission_id, "moves.json", moves_data)

        self.logger.info(f"Added invite to mission {mission_id}: {move_id}")

        return {
            "status": "success",
            "message": f"Invite '{title}' added to mission {mission_id}",
            "move_id": move_id,
            "move": move,
        }

    def add_reminder(
        self,
        mission_id: str,
        title: str,
        description: str,
        due_date: str,
        alert_type: str = "notification",
        alert_interval: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Add a reminder as a task.

        Args:
            mission_id: Target mission
            title: Reminder title
            description: Reminder details
            due_date: ISO 8601 datetime
            alert_type: "notification", "email", "sms", etc.
            alert_interval: e.g., "15min", "1hour", "1day"
            **kwargs: Additional fields
        """
        if mission_id not in self.binders:
            return {
                "status": "error",
                "message": f"Mission not found: {mission_id}",
            }

        move_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        move = {
            "id": move_id,
            "mission_id": mission_id,
            "title": title,
            "description": description,
            "item_type": "reminder",
            "status": "todo",
            "priority": kwargs.get("priority", "high"),
            "due_date": due_date,
            "source": kwargs.get("source", "reminder"),
            "source_id": kwargs.get("source_id"),
            "metadata": {
                **(kwargs.get("metadata", {})),
                "alert_type": alert_type,
                "alert_interval": alert_interval,
            },
            "tags": kwargs.get("tags", ["reminder"]),
            "created": now,
            "updated": now,
        }

        self.binders[mission_id]["moves"].append(move)
        moves_data = {"moves": self.binders[mission_id]["moves"]}
        self._save_mission_file(mission_id, "moves.json", moves_data)

        self.logger.info(f"Added reminder to mission {mission_id}: {move_id}")

        return {
            "status": "success",
            "message": f"Reminder '{title}' added to mission {mission_id}",
            "move_id": move_id,
            "move": move,
        }

    def add_imported_item(
        self,
        mission_id: str,
        title: str,
        description: str,
        source: str,
        source_id: str,
        item_category: str = "imported",
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Add a generic imported item (from email, external systems, etc).

        Args:
            mission_id: Target mission
            title: Item title
            description: Item description
            source: Source system (email, slack, jira, linear, etc.)
            source_id: Original ID from source
            item_category: Category of imported item
            **kwargs: Additional fields
        """
        if mission_id not in self.binders:
            return {
                "status": "error",
                "message": f"Mission not found: {mission_id}",
            }

        move_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        move = {
            "id": move_id,
            "mission_id": mission_id,
            "title": title,
            "description": description,
            "item_type": "imported",
            "status": "todo",
            "priority": kwargs.get("priority", "medium"),
            "source": source,
            "source_id": source_id,
            "metadata": {
                **(kwargs.get("metadata", {})),
                "item_category": item_category,
                "import_timestamp": now,
                "original_format": kwargs.get("original_format"),
            },
            "tags": kwargs.get("tags", [source, item_category]),
            "due_date": kwargs.get("due_date"),
            "created": now,
            "updated": now,
        }

        self.binders[mission_id]["moves"].append(move)
        moves_data = {"moves": self.binders[mission_id]["moves"]}
        self._save_mission_file(mission_id, "moves.json", moves_data)

        self.logger.info(f"Added imported item to mission {mission_id}: {move_id}")

        return {
            "status": "success",
            "message": f"Item imported from {source} to mission {mission_id}",
            "move_id": move_id,
            "move": move,
        }

    def update_move(
        self,
        mission_id: str,
        move_id: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Update a move's status or details.

        Supports updating any field: status, priority, assigned_to, tags, metadata, etc.
        """
        if mission_id not in self.binders:
            return {
                "status": "error",
                "message": f"Mission not found: {mission_id}",
            }

        moves = self.binders[mission_id]["moves"]
        move = next((m for m in moves if m["id"] == move_id), None)

        if not move:
            return {
                "status": "error",
                "message": f"Move not found: {move_id}",
            }

        # Update all supported fields
        updatable_fields = [
            "status", "priority", "assigned_to", "description", "title",
            "tags", "due_date", "start_date", "end_date", "attendees",
            "metadata", "source_id"
        ]

        for field in updatable_fields:
            if field in kwargs:
                move[field] = kwargs[field]

        move["updated"] = datetime.now().isoformat()

        # Save
        moves_data = {"moves": self.binders[mission_id]["moves"]}
        self._save_mission_file(mission_id, "moves.json", moves_data)

        self.logger.info(f"Updated move {move_id} in mission {mission_id}")

        return {
            "status": "success",
            "message": f"Move updated: {move_id}",
            "move": move,
        }

    def complete_move(self, mission_id: str, move_id: str) -> Dict[str, Any]:
        """Move a task from active moves to milestones."""
        if mission_id not in self.binders:
            return {
                "status": "error",
                "message": f"Mission not found: {mission_id}",
            }

        moves = self.binders[mission_id]["moves"]
        move = next((m for m in moves if m["id"] == move_id), None)

        if not move:
            return {
                "status": "error",
                "message": f"Move not found: {move_id}",
            }

        # Convert move to milestone
        now = datetime.now().isoformat()
        milestone = {
            "id": move["id"],
            "mission_id": mission_id,
            "title": move["title"],
            "description": move["description"],
            "item_type": move.get("item_type", "task"),
            "completed": now,
            "achievements": move.get("tags", []),
            "_source_move": move,  # Archive original move data for reference
        }

        # Add to milestones
        self.binders[mission_id]["milestones"].append(milestone)

        # Remove from moves
        self.binders[mission_id]["moves"] = [m for m in moves if m["id"] != move_id]

        # Save both files
        moves_data = {"moves": self.binders[mission_id]["moves"]}
        milestones_data = {"milestones": self.binders[mission_id]["milestones"]}

        self._save_mission_file(mission_id, "moves.json", moves_data)
        self._save_mission_file(mission_id, "milestones.json", milestones_data)

        self.logger.info(f"Completed move {move_id} in mission {mission_id}")

        return {
            "status": "success",
            "message": f"Move completed and added to milestones: {move_id}",
            "milestone": milestone,
        }

    def list_milestones(self, mission_id: str) -> Dict[str, Any]:
        """List completed tasks (milestones) for a mission."""
        if mission_id not in self.binders:
            return {
                "status": "error",
                "message": f"Mission not found: {mission_id}",
            }

        milestones = self.binders[mission_id].get("milestones", [])

        return {
            "status": "success",
            "mission_id": mission_id,
            "milestones": milestones,
            "count": len(milestones),
        }

    def get_imported_items_summary(self, mission_id: str) -> Dict[str, Any]:
        """
        Get summary of imported items for a mission.
        Useful for understanding what external items have been mapped to tasks.
        """
        if mission_id not in self.binders:
            return {
                "status": "error",
                "message": f"Mission not found: {mission_id}",
            }

        moves = self.binders[mission_id].get("moves", [])

        # Group by source
        by_source = {}
        by_type = {}

        for move in moves:
            source = move.get("source", "manual")
            item_type = move.get("item_type", "task")

            if source not in by_source:
                by_source[source] = []
            if item_type not in by_type:
                by_type[item_type] = []

            by_source[source].append(move["id"])
            by_type[item_type].append(move["id"])

        return {
            "status": "success",
            "mission_id": mission_id,
            "imported_summary": {
                "total_moves": len(moves),
                "by_source": by_source,
                "by_item_type": by_type,
            },
        }

    def get_task_summary_for_ai(self, mission_id: str) -> Dict[str, Any]:
        """
        Get comprehensive task summary suitable for AI ingestion.
        Includes full task details, metadata, and relationships.
        """
        if mission_id not in self.binders:
            return {
                "status": "error",
                "message": f"Mission not found: {mission_id}",
            }

        binder_data = self.binders[mission_id]
        moves = binder_data.get("moves", [])
        milestones = binder_data.get("milestones", [])
        mission = binder_data.get("mission", {})

        # Enrich moves with statistics
        moves_by_status = {}
        for move in moves:
            status = move.get("status", "unknown")
            if status not in moves_by_status:
                moves_by_status[status] = []
            moves_by_status[status].append(move)

        # Statistics
        high_priority = [m for m in moves if m.get("priority") == "high"]
        overdue = [m for m in moves if m.get("due_date") and m.get("due_date") < datetime.now().isoformat()]
        assigned = [m for m in moves if m.get("assigned_to")]

        return {
            "status": "success",
            "mission_id": mission_id,
            "mission_info": mission,
            "task_summary": {
                "total_active_moves": len(moves),
                "total_completed_milestones": len(milestones),
                "by_status": {k: len(v) for k, v in moves_by_status.items()},
                "by_item_type": {
                    item_type: len([m for m in moves if m.get("item_type") == item_type])
                    for item_type in set(m.get("item_type") for m in moves)
                },
                "high_priority_count": len(high_priority),
                "overdue_count": len(overdue),
                "assigned_count": len(assigned),
                "metrics": {
                    "completion_rate": len(milestones) / (len(moves) + len(milestones)) if (len(moves) + len(milestones)) > 0 else 0,
                    "average_priority": self._calculate_avg_priority(moves),
                },
            },
            "moves": moves,
            "milestones": milestones,
        }

    def _calculate_avg_priority(self, moves: List[Dict[str, Any]]) -> str:
        """Helper to calculate average priority across moves."""
        if not moves:
            return "medium"

        priority_scores = {"high": 3, "medium": 2, "low": 1}
        scored_moves = [m for m in moves if m.get("priority")]

        if not scored_moves:
            return "medium"

        avg_score = sum(priority_scores.get(m.get("priority"), 2) for m in scored_moves) / len(scored_moves)

        if avg_score >= 2.5:
            return "high"
        elif avg_score >= 1.5:
            return "medium"
        else:
            return "low"


def get_binder_service() -> VibeBinderService:
    """Get or create the global binder service."""
    global _binder_service_instance
    if _binder_service_instance is None:
        _binder_service_instance = VibeBinderService()
    return _binder_service_instance
