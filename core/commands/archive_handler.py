"""
uDOS v1.2.12 - Archive Command Handler

Handles archival of completed missions, workflows, and checklists.
Provides clean separation of active vs historical work with metadata preservation.
"""

from .base_handler import BaseCommandHandler
from pathlib import Path
import json
import shutil
from datetime import datetime
from core.utils.paths import PATHS


class ArchiveHandler(BaseCommandHandler):
    """Handler for archiving completed work (missions, workflows, checklists).

    v1.1.16: Now uses .archive/completed/ folders within each workspace area
    instead of centralized memory/system/archived/.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # v1.2.12: Use distributed .archive/completed/ folders with PATHS
        # Mission archives: memory/workflows/missions/.archive/completed/
        # Workflow archives: memory/workflows/.archive/completed/
        # Checklist archives: memory/checklists/.archive/completed/
        self.mission_archive = PATHS.MEMORY_WORKFLOWS_MISSIONS / ".archive" / "completed"
        self.workflow_archive = PATHS.MEMORY_WORKFLOWS / ".archive" / "completed"
        self.checklist_archive = PATHS.MEMORY_CHECKLISTS / ".archive" / "completed"

        # Ensure archive folders exist
        self.mission_archive.mkdir(parents=True, exist_ok=True)
        self.workflow_archive.mkdir(parents=True, exist_ok=True)
        self.checklist_archive.mkdir(parents=True, exist_ok=True)

    def handle(self, params, grid, parser):
        """
        Archive completed missions, workflows, or checklists.

        Usage:
            ARCHIVE                           → Interactive mode
            ARCHIVE LIST [type]               → List archived items
            ARCHIVE mission <id>              → Archive specific mission
            ARCHIVE workflow <id>             → Archive specific workflow
            ARCHIVE checklist <id>            → Archive specific checklist
            ARCHIVE all completed             → Archive all completed items
            ARCHIVE restore <type> <id>       → Restore archived item

        Examples:
            ARCHIVE mission knowledge-gen-001
            ARCHIVE LIST mission
            ARCHIVE all completed
            ARCHIVE restore workflow content-gen-2024
        """
        if not params:
            return self._interactive_archive()

        command = params[0].lower()

        if command == "list":
            archive_type = params[1] if len(params) > 1 else None
            return self._list_archived(archive_type)

        elif command == "mission":
            if len(params) < 2:
                return self.output_formatter.format_error(
                    "Mission ID required",
                    "Usage: ARCHIVE mission <id>"
                )
            return self._archive_mission(params[1])

        elif command == "workflow":
            if len(params) < 2:
                return self.output_formatter.format_error(
                    "Workflow ID required",
                    "Usage: ARCHIVE workflow <id>"
                )
            return self._archive_workflow(params[1])

        elif command == "checklist":
            if len(params) < 2:
                return self.output_formatter.format_error(
                    "Checklist ID required",
                    "Usage: ARCHIVE checklist <id>"
                )
            return self._archive_checklist(params[1])

        elif command == "all":
            if len(params) < 2 or params[1].lower() != "completed":
                return self.output_formatter.format_error(
                    "Confirmation required",
                    "Usage: ARCHIVE all completed"
                )
            return self._archive_all_completed()

        elif command == "restore":
            if len(params) < 3:
                return self.output_formatter.format_error(
                    "Type and ID required",
                    "Usage: ARCHIVE restore <type> <id>"
                )
            return self._restore_archived(params[1], params[2])

        else:
            return self.output_formatter.format_error(
                f"Unknown archive command: {command}",
                "Use: ARCHIVE LIST, mission, workflow, checklist, all completed, restore"
            )

    def _interactive_archive(self):
        """Interactive archive mode using InputManager."""
        if not self.input_manager:
            return self.output_formatter.format_error(
                "Interactive mode unavailable",
                "Use: ARCHIVE <type> <id>"
            )

        choices = [
            "Archive mission",
            "Archive workflow",
            "Archive checklist",
            "Archive all completed items",
            "List archived items",
            "Restore archived item",
            "Cancel"
        ]

        choice = self.input_manager.prompt_choice(
            "What would you like to archive?",
            choices=choices
        )

        if "Cancel" in choice:
            return "Operation cancelled"

        if "List" in choice:
            return self._list_archived()

        if "all completed" in choice:
            confirm = self.input_manager.prompt_choice(
                "Archive ALL completed items?",
                choices=["Yes", "No"],
                default="No"
            )
            if confirm == "Yes":
                return self._archive_all_completed()
            return "Operation cancelled"

        if "Restore" in choice:
            archive_type = self.input_manager.prompt_choice(
                "Restore which type?",
                choices=["mission", "workflow", "checklist"]
            )
            archived_items = self._get_archived_items(archive_type)
            if not archived_items:
                return f"No archived {archive_type}s found"

            item_id = self.input_manager.prompt_choice(
                f"Select {archive_type} to restore:",
                choices=[item['id'] for item in archived_items]
            )
            return self._restore_archived(archive_type, item_id)

        # Archive specific item
        if "mission" in choice:
            item_id = self.input_manager.prompt_user(
                "Mission ID to archive:",
                required=True
            )
            return self._archive_mission(item_id)

        elif "workflow" in choice:
            item_id = self.input_manager.prompt_user(
                "Workflow ID to archive:",
                required=True
            )
            return self._archive_workflow(item_id)

        elif "checklist" in choice:
            item_id = self.input_manager.prompt_user(
                "Checklist ID to archive:",
                required=True
            )
            return self._archive_checklist(item_id)

    def _archive_mission(self, mission_id: str):
        """Archive a specific mission with metadata (v1.1.16: uses .archive/completed/)."""
        mission_path = Path(f"memory/workflows/missions/{mission_id}")

        if not mission_path.exists():
            return self.output_formatter.format_error(
                f"Mission not found: {mission_id}",
                f"Path: {mission_path}"
            )

        # Create archive directory in mission-specific .archive/completed/
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_dir = self.mission_archive / f"{mission_id}_{timestamp}"
        archive_dir.mkdir(parents=True, exist_ok=True)

        # Copy mission files
        if mission_path.is_dir():
            shutil.copytree(mission_path, archive_dir / "mission", dirs_exist_ok=True)
        else:
            shutil.copy2(mission_path, archive_dir / "mission")

        # Create metadata
        metadata = {
            "id": mission_id,
            "type": "mission",
            "archived_at": datetime.now().isoformat(),
            "original_path": str(mission_path),
            "archive_path": str(archive_dir)
        }

        success, error = self.save_json_file(archive_dir / "metadata.json", metadata)
        if not success:
            return self.output_formatter.format_error(f"Failed to save metadata: {error}")

        # Remove original (optional - can be configured)
        # shutil.rmtree(mission_path) if mission_path.is_dir() else mission_path.unlink()

        return self.output_formatter.format_success(
            f"Mission archived: {mission_id}",
            details={
                "Archive location": str(archive_dir),
                "Timestamp": timestamp,
                "Files": "Preserved with metadata"
            }
        )

    def _archive_workflow(self, workflow_id: str):
        """Archive a specific workflow with checkpoints (v1.1.16: uses .archive/completed/)."""
        workflow_file = Path(f"memory/workflows/missions/{workflow_id}.upy")

        if not workflow_file.exists():
            return self.output_formatter.format_error(
                f"Workflow not found: {workflow_id}",
                f"Path: {workflow_file}"
            )

        # Create archive directory in workflow-specific .archive/completed/
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_dir = self.workflow_archive / f"{workflow_id}_{timestamp}"
        archive_dir.mkdir(parents=True, exist_ok=True)

        # Copy workflow file
        shutil.copy2(workflow_file, archive_dir / f"{workflow_id}.upy")

        # Copy related checkpoints
        checkpoint_dir = PATHS.MEMORY_WORKFLOWS_CHECKPOINTS
        if checkpoint_dir.exists():
            checkpoints = list(checkpoint_dir.glob(f"{workflow_id}*.json"))
            if checkpoints:
                checkpoint_archive = archive_dir / "checkpoints"
                checkpoint_archive.mkdir(exist_ok=True)
                for cp in checkpoints:
                    shutil.copy2(cp, checkpoint_archive / cp.name)

        # Create metadata
        metadata = {
            "id": workflow_id,
            "type": "workflow",
            "archived_at": datetime.now().isoformat(),
            "original_path": str(workflow_file),
            "archive_path": str(archive_dir),
            "checkpoints_count": len(checkpoints) if checkpoint_dir.exists() else 0
        }

        success, error = self.save_json_file(archive_dir / "metadata.json", metadata)
        if not success:
            return self.output_formatter.format_error(f"Failed to save metadata: {error}")

        return self.output_formatter.format_success(
            f"Workflow archived: {workflow_id}",
            details={
                "Archive location": str(archive_dir),
                "Checkpoints": metadata['checkpoints_count'],
                "Timestamp": timestamp
            }
        )

    def _archive_checklist(self, checklist_id: str):
        """Archive a specific checklist with progress state."""
        # Get checklist progress from state file
        state_file = PATHS.CHECKLIST_STATE
        state = {}
        if state_file.exists():
            success, state, error = self.load_json_file(state_file)
            if not success:
                return self.output_formatter.format_error(f"Failed to load state: {error}")

        checklist_state = state.get(checklist_id, {})

        # Create archive directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_dir = self.archive_base / "checklists" / f"{checklist_id}_{timestamp}"
        archive_dir.mkdir(parents=True, exist_ok=True)

        # Save state snapshot
        metadata = {
            "id": checklist_id,
            "type": "checklist",
            "archived_at": datetime.now().isoformat(),
            "progress": checklist_state
        }

        success, error = self.save_json_file(archive_dir / "metadata.json", metadata)
        if not success:
            return self.output_formatter.format_error(f"Failed to save metadata: {error}")

        # Remove from active state
        if checklist_id in state:
            del state[checklist_id]
            success, error = self.save_json_file(state_file, state)
            if not success:
                return self.output_formatter.format_error(f"Failed to update state: {error}")

        return self.output_formatter.format_success(
            f"Checklist archived: {checklist_id}",
            details={
                "Archive location": str(archive_dir),
                "Progress saved": "Yes",
                "Timestamp": timestamp
            }
        )

    def _archive_all_completed(self):
        """Archive all items marked as completed."""
        archived = {
            "missions": 0,
            "workflows": 0,
            "checklists": 0
        }

        # This is a placeholder - would integrate with mission/workflow managers
        # to identify completed items

        return self.output_formatter.format_success(
            "Archived all completed items",
            details=archived
        )

    def _list_archived(self, archive_type: str = None):
        """List archived items with metadata (v1.1.16: scans .archive/completed/ folders)."""
        output = ["📦 ARCHIVED ITEMS\n" + "=" * 60 + "\n"]

        # Map type names to archive locations
        type_locations = {
            "missions": self.mission_archive,
            "workflows": self.workflow_archive,
            "checklists": self.checklist_archive
        }

        types_to_check = [archive_type] if archive_type else ["missions", "workflows", "checklists"]

        for item_type in types_to_check:
            type_dir = type_locations.get(item_type)
            if not type_dir or not type_dir.exists():
                continue

            archives = sorted(type_dir.iterdir(), reverse=True)
            if not archives:
                continue

            output.append(f"\n{item_type.upper()}:")
            for archive in archives[:10]:  # Show latest 10
                metadata_file = archive / "metadata.json"
                if metadata_file.exists():
                    success, metadata, error = self.load_json_file(metadata_file)
                    if not success:
                        continue

                    archived_time = metadata.get('archived_at', 'Unknown')
                    item_id = metadata.get('id', archive.name)
                    output.append(f"  • {item_id} ({archived_time})")

        return "\n".join(output)

    def _restore_archived(self, archive_type: str, item_id: str):
        """Restore an archived item to active state (v1.1.16: uses .archive/completed/)."""
        # Map type names to archive locations
        type_locations = {
            "missions": self.mission_archive,
            "workflows": self.workflow_archive,
            "checklists": self.checklist_archive
        }

        type_dir = type_locations.get(archive_type)

        if not type_dir or not type_dir.exists():
            return self.output_formatter.format_error(
                f"No archived {archive_type}s found"
            )

        # Find most recent archive matching ID
        archives = sorted(type_dir.glob(f"{item_id}_*"), reverse=True)
        if not archives:
            return self.output_formatter.format_error(
                f"Archived {archive_type} not found: {item_id}"
            )

        archive_dir = archives[0]
        metadata_file = archive_dir / "metadata.json"

        if not metadata_file.exists():
            return self.output_formatter.format_error(
                "Archive metadata missing"
            )

        success, metadata, error = self.load_json_file(metadata_file)
        if not success:
            return self.output_formatter.format_error(f"Failed to load metadata: {error}")

        original_path = Path(metadata['original_path'])

        # Restore based on type
        if archive_type == "mission":
            mission_source = archive_dir / "mission"
            if mission_source.is_dir():
                shutil.copytree(mission_source, original_path, dirs_exist_ok=True)
            else:
                shutil.copy2(mission_source, original_path)

        elif archive_type == "workflow":
            workflow_file = archive_dir / f"{item_id}.upy"
            shutil.copy2(workflow_file, original_path)

            # Restore checkpoints
            checkpoint_dir = archive_dir / "checkpoints"
            if checkpoint_dir.exists():
                target_checkpoint_dir = PATHS.MEMORY_WORKFLOWS_CHECKPOINTS
                target_checkpoint_dir.mkdir(parents=True, exist_ok=True)
                for cp in checkpoint_dir.iterdir():
                    shutil.copy2(cp, target_checkpoint_dir / cp.name)

        elif archive_type == "checklist":
            # Restore progress state
            state_file = PATHS.CHECKLIST_STATE
            state = {}
            if state_file.exists():
                success, state, error = self.load_json_file(state_file)
                if not success:
                    return self.output_formatter.format_error(f"Failed to load state: {error}")

            state[item_id] = metadata.get('progress', {})

            success, error = self.save_json_file(state_file, state)
            if not success:
                return self.output_formatter.format_error(f"Failed to save state: {error}")

        return self.output_formatter.format_success(
            f"Restored {archive_type}: {item_id}",
            details={
                "Restored to": str(original_path),
                "Archived": metadata['archived_at']
            }
        )

    def _get_archived_items(self, archive_type: str):
        """Get list of archived items of a specific type."""
        type_dir = self.archive_base / archive_type
        if not type_dir.exists():
            return []

        items = []
        for archive in type_dir.iterdir():
            metadata_file = archive / "metadata.json"
            if metadata_file.exists():
                success, metadata, error = self.load_json_file(metadata_file)
                if success:
                    items.append(metadata)

        return sorted(items, key=lambda x: x['archived_at'], reverse=True)
