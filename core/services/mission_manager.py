"""
Mission Manager - Project Management System
Manages long-running projects through missions, moves, and steps.

Version: 1.1.2
Status: In Development

Philosophy:
- Work measured in STEPS (atomic operations)
- MOVES group steps into milestones
- MISSIONS group moves toward goals
- Progress tracked, not time
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum


class MissionStatus(Enum):
    """Mission lifecycle states."""
    NOT_STARTED = "not_started"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    CANCELLED = "cancelled"


class MissionPriority(Enum):
    """Mission priority levels."""
    HIGH = "high"        # ⚡ Urgent, time-sensitive
    MEDIUM = "medium"    # 📊 Standard priority
    LOW = "low"          # 🔧 Background work


class Step:
    """Atomic operation within a move."""

    def __init__(
        self,
        id: int,
        title: str,
        description: str = "",
        estimated_duration: int = 15,  # minutes
        status: str = "not_started"
    ):
        self.id = id
        self.title = title
        self.description = description
        self.estimated_duration = estimated_duration
        self.status = status  # not_started, in_progress, completed, skipped
        self.started_at: Optional[str] = None
        self.completed_at: Optional[str] = None
        self.notes: List[str] = []

    def to_dict(self) -> dict:
        """Convert step to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'estimated_duration': self.estimated_duration,
            'status': self.status,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'notes': self.notes
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Step':
        """Create step from dictionary."""
        step = cls(
            id=data['id'],
            title=data['title'],
            description=data.get('description', ''),
            estimated_duration=data.get('estimated_duration', 15),
            status=data.get('status', 'not_started')
        )
        step.started_at = data.get('started_at')
        step.completed_at = data.get('completed_at')
        step.notes = data.get('notes', [])
        return step


class Move:
    """Collection of steps forming a milestone."""

    def __init__(
        self,
        id: int,
        title: str,
        description: str = "",
        steps: Optional[List[Step]] = None
    ):
        self.id = id
        self.title = title
        self.description = description
        self.steps: List[Step] = steps or []
        self.status: str = "not_started"
        self.started_at: Optional[str] = None
        self.completed_at: Optional[str] = None

    def add_step(self, step: Step):
        """Add step to move."""
        self.steps.append(step)

    def get_step(self, step_id: int) -> Optional[Step]:
        """Get step by ID."""
        for step in self.steps:
            if step.id == step_id:
                return step
        return None

    def total_steps(self) -> int:
        """Total number of steps in move."""
        return len(self.steps)

    def completed_steps(self) -> int:
        """Number of completed steps."""
        return sum(1 for s in self.steps if s.status == 'completed')

    def progress_percentage(self) -> float:
        """Calculate progress percentage."""
        total = self.total_steps()
        if total == 0:
            return 0.0
        return (self.completed_steps() / total) * 100

    def is_complete(self) -> bool:
        """Check if all steps are completed."""
        return all(s.status in ['completed', 'skipped'] for s in self.steps)

    def to_dict(self) -> dict:
        """Convert move to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'steps': [s.to_dict() for s in self.steps],
            'status': self.status,
            'started_at': self.started_at,
            'completed_at': self.completed_at
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Move':
        """Create move from dictionary."""
        move = cls(
            id=data['id'],
            title=data['title'],
            description=data.get('description', ''),
            steps=[Step.from_dict(s) for s in data.get('steps', [])]
        )
        move.status = data.get('status', 'not_started')
        move.started_at = data.get('started_at')
        move.completed_at = data.get('completed_at')
        return move


class Mission:
    """Collection of moves toward a goal."""

    def __init__(
        self,
        id: str,
        title: str,
        description: str = "",
        priority: str = "medium",
        moves: Optional[List[Move]] = None
    ):
        self.id = id
        self.title = title
        self.description = description
        self.priority = priority
        self.status = MissionStatus.NOT_STARTED.value
        self.moves: List[Move] = moves or []
        self.created_at = datetime.now().isoformat()
        self.started_at: Optional[str] = None
        self.paused_at: Optional[str] = None
        self.completed_at: Optional[str] = None
        self.workspace_path: Optional[str] = None
        self.dependencies: List[str] = []  # Mission IDs this depends on
        self.metadata: Dict[str, Any] = {}

    def add_move(self, move: Move):
        """Add move to mission."""
        self.moves.append(move)

    def get_move(self, move_id: int) -> Optional[Move]:
        """Get move by ID."""
        for move in self.moves:
            if move.id == move_id:
                return move
        return None

    def total_steps(self) -> int:
        """Total number of steps across all moves."""
        return sum(move.total_steps() for move in self.moves)

    def completed_steps(self) -> int:
        """Number of completed steps."""
        return sum(move.completed_steps() for move in self.moves)

    def progress_percentage(self) -> float:
        """Calculate overall progress percentage."""
        total = self.total_steps()
        if total == 0:
            return 0.0
        return (self.completed_steps() / total) * 100

    def current_move(self) -> Optional[Move]:
        """Get the currently active move."""
        for move in self.moves:
            if move.status == 'in_progress':
                return move
        # If no move in progress, return first incomplete move
        for move in self.moves:
            if not move.is_complete():
                return move
        return None

    def get_current_move(self) -> Optional[Move]:
        """Alias for current_move() for compatibility."""
        return self.current_move()

    def get_progress(self) -> dict:
        """Get detailed progress information."""
        return {
            'total_steps': self.total_steps(),
            'completed_steps': self.completed_steps(),
            'percentage': round(self.progress_percentage(), 2)
        }

    def get_status_summary(self) -> str:
        """Get formatted status summary."""
        progress = self.get_progress()
        priority_icon = {
            'high': '⚡',
            'medium': '📊',
            'low': '🔧'
        }.get(self.priority, '📊')

        status_icon = {
            'not_started': '⚪',
            'active': '🟢',
            'paused': '🟡',
            'completed': '✅',
            'archived': '📦',
            'cancelled': '❌'
        }.get(self.status, '⚪')

        lines = [
            f"\n{status_icon} Mission: {self.id} - {self.title}",
            f"{priority_icon} Priority: {self.priority}",
            f"📈 Progress: {progress['completed_steps']}/{progress['total_steps']} steps ({progress['percentage']:.2f}%)",
            f"📋 Status: {self.status}"
        ]

        if self.started_at:
            lines.append(f"🕐 Started: {self.started_at}")
        if self.completed_at:
            lines.append(f"✅ Completed: {self.completed_at}")

        return '\n'.join(lines)

    def is_complete(self) -> bool:
        """Check if all moves are completed."""
        return all(move.is_complete() for move in self.moves)

    def to_dict(self) -> dict:
        """Convert mission to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'moves': [m.to_dict() for m in self.moves],
            'created_at': self.created_at,
            'started_at': self.started_at,
            'paused_at': self.paused_at,
            'completed_at': self.completed_at,
            'workspace_path': self.workspace_path,
            'dependencies': self.dependencies,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Mission':
        """Create mission from dictionary."""
        mission = cls(
            id=data['id'],
            title=data['title'],
            description=data.get('description', ''),
            priority=data.get('priority', 'medium'),
            moves=[Move.from_dict(m) for m in data.get('moves', [])]
        )
        mission.status = data.get('status', MissionStatus.NOT_STARTED.value)
        mission.created_at = data.get('created_at', datetime.now().isoformat())
        mission.started_at = data.get('started_at')
        mission.paused_at = data.get('paused_at')
        mission.completed_at = data.get('completed_at')
        mission.workspace_path = data.get('workspace_path')
        mission.dependencies = data.get('dependencies', [])
        mission.metadata = data.get('metadata', {})
        return mission


class MissionManager:
    """Manages all missions and their lifecycle."""

    def __init__(self, missions_dir: str = "sandbox/workflow/missions"):
        self.missions_dir = Path(missions_dir)
        self.missions_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir = Path("sandbox/workflow/templates/missions")
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.missions: Dict[str, Mission] = {}
        self.templates_cache: Dict[str, dict] = {}
        self.load_all_missions()
        self.load_templates()

    def load_all_missions(self):
        """Load all missions from disk."""
        if not self.missions_dir.exists():
            return

        for mission_file in self.missions_dir.glob("*.json"):
            try:
                with open(mission_file, 'r') as f:
                    data = json.load(f)
                    mission = Mission.from_dict(data)
                    self.missions[mission.id] = mission
            except Exception as e:
                print(f"⚠️  Error loading mission {mission_file}: {e}")

    def save_mission(self, mission: Mission):
        """Save mission to disk."""
        mission_file = self.missions_dir / f"{mission.id}.json"
        with open(mission_file, 'w') as f:
            json.dump(mission.to_dict(), f, indent=2)

    def create_mission(
        self,
        id: str,
        title: str,
        description: str = "",
        priority: str = "medium"
    ) -> Mission:
        """Create new mission."""
        if id in self.missions:
            raise ValueError(f"Mission '{id}' already exists")

        mission = Mission(id, title, description, priority)

        # Create workspace directory
        workspace = self.missions_dir / id
        workspace.mkdir(exist_ok=True)
        mission.workspace_path = str(workspace)

        self.missions[id] = mission
        self.save_mission(mission)

        return mission

    def get_mission(self, mission_id: str) -> Optional[Mission]:
        """Get mission by ID."""
        return self.missions.get(mission_id)

    def list_missions(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None
    ) -> List[Mission]:
        """List missions with optional filtering."""
        missions = list(self.missions.values())

        if status:
            missions = [m for m in missions if m.status == status]

        if priority:
            missions = [m for m in missions if m.priority == priority]

        return missions

    def start_mission(self, mission_id: str) -> Mission:
        """Start a mission."""
        mission = self.get_mission(mission_id)
        if not mission:
            raise ValueError(f"Mission '{mission_id}' not found")

        if mission.status != MissionStatus.NOT_STARTED.value:
            raise ValueError(f"Mission '{mission_id}' already started")

        mission.status = MissionStatus.ACTIVE.value
        mission.started_at = datetime.now().isoformat()
        self.save_mission(mission)

        return mission

    def pause_mission(self, mission_id: str) -> Mission:
        """Pause an active mission."""
        mission = self.get_mission(mission_id)
        if not mission:
            raise ValueError(f"Mission '{mission_id}' not found")

        if mission.status != MissionStatus.ACTIVE.value:
            raise ValueError(f"Mission '{mission_id}' is not active")

        mission.status = MissionStatus.PAUSED.value
        mission.paused_at = datetime.now().isoformat()
        self.save_mission(mission)

        return mission

    def resume_mission(self, mission_id: str) -> Mission:
        """Resume a paused mission."""
        mission = self.get_mission(mission_id)
        if not mission:
            raise ValueError(f"Mission '{mission_id}' not found")

        if mission.status != MissionStatus.PAUSED.value:
            raise ValueError(f"Mission '{mission_id}' is not paused")

        mission.status = MissionStatus.ACTIVE.value
        mission.paused_at = None
        self.save_mission(mission)

        return mission

    def complete_mission(self, mission_id: str) -> Mission:
        """Mark mission as completed."""
        mission = self.get_mission(mission_id)
        if not mission:
            raise ValueError(f"Mission '{mission_id}' not found")

        mission.status = MissionStatus.COMPLETED.value
        mission.completed_at = datetime.now().isoformat()
        self.save_mission(mission)

        return mission

    def set_priority(self, mission_id: str, priority: str) -> Mission:
        """Change mission priority."""
        mission = self.get_mission(mission_id)
        if not mission:
            raise ValueError(f"Mission '{mission_id}' not found")

        if priority not in ['high', 'medium', 'low']:
            raise ValueError(f"Invalid priority: {priority}")

        mission.priority = priority
        self.save_mission(mission)

        return mission

    def archive_mission(self, mission_id: str) -> Mission:
        """Archive a completed or cancelled mission."""
        mission = self.get_mission(mission_id)
        if not mission:
            raise ValueError(f"Mission '{mission_id}' not found")

        if mission.status not in [MissionStatus.COMPLETED.value, MissionStatus.CANCELLED.value]:
            raise ValueError(f"Can only archive completed or cancelled missions")

        mission.status = MissionStatus.ARCHIVED.value
        self.save_mission(mission)

        # Move to archive directory
        archive_dir = self.missions_dir / "archive"
        archive_dir.mkdir(exist_ok=True)

        source = self.missions_dir / f"{mission.id}.json"
        dest = archive_dir / f"{mission.id}.json"
        source.rename(dest)

        return mission

    def clone_mission(self, mission_id: str, new_id: str) -> Mission:
        """Clone an existing mission with new ID."""
        mission = self.get_mission(mission_id)
        if not mission:
            raise ValueError(f"Mission '{mission_id}' not found")

        if new_id in self.missions:
            raise ValueError(f"Mission '{new_id}' already exists")

        # Create deep copy
        mission_dict = mission.to_dict()
        mission_dict['id'] = new_id
        mission_dict['status'] = MissionStatus.NOT_STARTED.value
        mission_dict['started_at'] = None
        mission_dict['paused_at'] = None
        mission_dict['completed_at'] = None
        mission_dict['created_at'] = datetime.now().isoformat()

        # Reset all move and step statuses
        for move in mission_dict['moves']:
            move['status'] = 'not_started'
            move['started_at'] = None
            move['completed_at'] = None
            for step in move['steps']:
                step['status'] = 'not_started'
                step['started_at'] = None
                step['completed_at'] = None

        new_mission = Mission.from_dict(mission_dict)

        # Create workspace
        workspace = self.missions_dir / new_id
        workspace.mkdir(exist_ok=True)
        new_mission.workspace_path = str(workspace)

        self.missions[new_id] = new_mission
        self.save_mission(new_mission)

        return new_mission

    def get_status_summary(self, mission_id: str) -> dict:
        """Get mission status summary."""
        mission = self.get_mission(mission_id)
        if not mission:
            raise ValueError(f"Mission '{mission_id}' not found")

        total_moves = len(mission.moves)
        completed_moves = sum(1 for m in mission.moves if m.is_complete())
        current_move = mission.current_move()

        summary = {
            'id': mission.id,
            'title': mission.title,
            'status': mission.status,
            'priority': mission.priority,
            'progress': f"{mission.progress_percentage():.1f}%",
            'steps': {
                'completed': mission.completed_steps(),
                'total': mission.total_steps()
            },
            'moves': {
                'completed': completed_moves,
                'total': total_moves
            },
            'current_move': current_move.title if current_move else None,
            'started_at': mission.started_at,
            'completed_at': mission.completed_at
        }

        return summary

    # Template System Methods

    def load_templates(self):
        """Load all mission templates from templates directory."""
        if not self.templates_dir.exists():
            return

        for template_file in self.templates_dir.glob("*.json"):
            # Skip schema file
            if template_file.name == "template-schema.json":
                continue

            try:
                with open(template_file, 'r') as f:
                    template = json.load(f)
                    template_id = template.get('id')
                    if template_id:
                        self.templates_cache[template_id] = template
            except Exception as e:
                print(f"⚠️  Error loading template {template_file}: {e}")

    def list_templates(self, category: Optional[str] = None) -> List[dict]:
        """List available mission templates."""
        templates = list(self.templates_cache.values())

        if category:
            templates = [t for t in templates if t.get('category') == category]

        # Sort by category, then name
        templates.sort(key=lambda t: (t.get('category', ''), t.get('name', '')))

        return templates

    def get_template(self, template_id: str) -> Optional[dict]:
        """Get template by ID."""
        return self.templates_cache.get(template_id)

    def preview_template(self, template_id: str, variables: Optional[Dict[str, Any]] = None) -> dict:
        """Preview template with optional variable substitution."""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template '{template_id}' not found")

        preview = {
            'id': template['id'],
            'name': template['name'],
            'description': template.get('description', ''),
            'category': template.get('category', ''),
            'version': template.get('version', ''),
            'priority': template.get('priority', 'MEDIUM'),
            'estimated_duration': template.get('estimated_duration', ''),
            'tags': template.get('tags', []),
            'variables': template.get('variables', {}),
            'moves_count': len(template.get('moves', [])),
            'total_steps': sum(len(m.get('steps', [])) for m in template.get('moves', [])),
            'resources': template.get('resources', {}),
            'help': template.get('help', '')
        }

        # If variables provided, show sample substitution
        if variables:
            preview['sample_title'] = self._substitute_variables(template['name'], variables)
            if template.get('moves'):
                first_move = template['moves'][0]
                preview['sample_move'] = self._substitute_variables(first_move['name'], variables)

        return preview

    def validate_template_variables(self, template_id: str, variables: Dict[str, Any]) -> List[str]:
        """Validate that all required variables are provided."""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template '{template_id}' not found")

        errors = []
        template_vars = template.get('variables', {})

        for var_name, var_config in template_vars.items():
            if var_config.get('required', False):
                if var_name not in variables:
                    errors.append(f"Required variable '{var_name}' not provided")
                    continue

            # Type validation
            if var_name in variables:
                value = variables[var_name]
                var_type = var_config.get('type', 'string')

                if var_type == 'number' and not isinstance(value, (int, float)):
                    errors.append(f"Variable '{var_name}' must be a number")
                elif var_type == 'boolean' and not isinstance(value, bool):
                    errors.append(f"Variable '{var_name}' must be boolean")
                elif var_type == 'choice':
                    choices = var_config.get('choices', [])
                    if value not in choices:
                        errors.append(f"Variable '{var_name}' must be one of: {', '.join(choices)}")
                elif var_type == 'string' and var_config.get('validation'):
                    pattern = var_config['validation']
                    if not re.match(pattern, str(value)):
                        errors.append(f"Variable '{var_name}' does not match required pattern")

        return errors

    def _substitute_variables(self, text: str, variables: Dict[str, Any]) -> str:
        """Substitute {{VAR_NAME}} placeholders with actual values."""
        result = text
        for var_name, value in variables.items():
            # Support both {{VAR}} and ${VAR} syntax
            result = result.replace(f"{{{{{var_name}}}}}", str(value))
            result = result.replace(f"${{{var_name}}}", str(value))
        return result

    def create_mission_from_template(
        self,
        template_id: str,
        mission_id: str,
        variables: Dict[str, Any],
        custom_title: Optional[str] = None,
        custom_description: Optional[str] = None
    ) -> Mission:
        """Create mission from template with variable substitution."""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template '{template_id}' not found")

        # Validate variables
        errors = self.validate_template_variables(template_id, variables)
        if errors:
            raise ValueError(f"Template validation failed:\n" + "\n".join(errors))

        # Check for existing mission
        if mission_id in self.missions:
            raise ValueError(f"Mission '{mission_id}' already exists")

        # Substitute variables in title and description
        title = custom_title or self._substitute_variables(template['name'], variables)
        description = custom_description or self._substitute_variables(
            template.get('description', ''),
            variables
        )

        # Create mission
        priority = template.get('priority', 'MEDIUM').lower()
        mission = Mission(mission_id, title, description, priority)

        # Store template metadata
        mission.metadata['template_id'] = template_id
        mission.metadata['template_version'] = template.get('version', '1.0.0')
        mission.metadata['variables'] = variables

        # Create moves and steps from template
        for move_idx, move_template in enumerate(template.get('moves', []), start=1):
            move_title = self._substitute_variables(move_template['name'], variables)
            move_desc = self._substitute_variables(move_template.get('description', ''), variables)

            move = Move(move_idx, move_title, move_desc)

            # Create steps
            for step_idx, step_template in enumerate(move_template.get('steps', []), start=1):
                step_desc = self._substitute_variables(step_template['description'], variables)

                step = Step(
                    id=step_idx,
                    title=step_desc,
                    description=self._substitute_variables(
                        step_template.get('command', ''),
                        variables
                    ) if step_template.get('command') else '',
                    estimated_duration=step_template.get('estimated_duration', 15)
                )

                move.add_step(step)

            mission.add_move(move)

        # Create workspace
        workspace = self.missions_dir / mission_id
        workspace.mkdir(exist_ok=True)
        mission.workspace_path = str(workspace)

        # Save mission
        self.missions[mission_id] = mission
        self.save_mission(mission)

        return mission


# Singleton instance
_mission_manager: Optional[MissionManager] = None


def get_mission_manager() -> MissionManager:
    """Get or create mission manager singleton."""
    global _mission_manager
    if _mission_manager is None:
        _mission_manager = MissionManager()
    return _mission_manager
