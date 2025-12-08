"""
Checklist Manager Service

Manages interactive checklists with progress tracking, persistence, and validation.
Supports JSON-based checklists with nested items and cross-referencing.

Author: uDOS Team
Version: 1.1.14
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import jsonschema
from core.utils.paths import PATHS


class ChecklistManager:
    """Manage checklists with progress tracking and persistence."""

    def __init__(self, config=None):
        """Initialize checklist manager.

        Args:
            config: Optional Config instance for paths
        """
        self.config = config
        self.checklist_dir = Path("knowledge/checklists")
        self.state_file = PATHS.CHECKLIST_STATE
        self.schema_file = Path("core/data/schemas/checklist.schema.json")
        self.state = self._load_state()
        self.schema = self._load_schema()

    def _load_schema(self) -> Dict:
        """Load checklist JSON schema."""
        if not self.schema_file.exists():
            return {}

        with open(self.schema_file, 'r') as f:
            return json.load(f)

    def _load_state(self) -> Dict:
        """Load checklist progress state from disk."""
        if not self.state_file.exists():
            return {"checklists": {}, "last_updated": None}

        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"checklists": {}, "last_updated": None}

    def _save_state(self) -> bool:
        """Save checklist progress state to disk."""
        try:
            self.state["last_updated"] = datetime.now().isoformat()
            os.makedirs(self.state_file.parent, exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
            return True
        except IOError as e:
            print(f"Error saving checklist state: {e}")
            return False

    def validate_checklist(self, checklist: Dict) -> tuple[bool, Optional[str]]:
        """Validate checklist against schema.

        Args:
            checklist: Checklist data to validate

        Returns:
            (valid, error_message) tuple
        """
        if not self.schema:
            return True, None

        try:
            jsonschema.validate(instance=checklist, schema=self.schema)
            return True, None
        except jsonschema.ValidationError as e:
            return False, str(e.message)

    def load_checklist(self, checklist_id: str) -> Optional[Dict]:
        """Load checklist from JSON file.

        Args:
            checklist_id: Checklist identifier

        Returns:
            Checklist data or None if not found
        """
        # Search for checklist in all subdirectories
        for json_file in self.checklist_dir.rglob(f"{checklist_id}.json"):
            try:
                with open(json_file, 'r') as f:
                    checklist = json.load(f)

                # Validate
                valid, error = self.validate_checklist(checklist)
                if not valid:
                    print(f"Warning: Checklist {checklist_id} failed validation: {error}")

                return checklist
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading checklist {checklist_id}: {e}")
                return None

        return None

    def list_checklists(self, category: Optional[str] = None) -> List[Dict]:
        """List available checklists.

        Args:
            category: Optional category filter

        Returns:
            List of checklist metadata
        """
        checklists = []

        for json_file in self.checklist_dir.rglob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)

                if category and data.get("category") != category:
                    continue

                # Get progress if available
                progress = self.get_progress(data["id"])

                checklists.append({
                    "id": data["id"],
                    "title": data["title"],
                    "category": data.get("category", "unknown"),
                    "difficulty": data.get("difficulty", "unknown"),
                    "progress": progress,
                    "path": str(json_file.relative_to(self.checklist_dir))
                })
            except (json.JSONDecodeError, KeyError, IOError):
                continue

        return sorted(checklists, key=lambda x: x["title"])

    def get_progress(self, checklist_id: str) -> Dict[str, Any]:
        """Get progress for a checklist.

        Args:
            checklist_id: Checklist identifier

        Returns:
            Progress data including completed items and percentage
        """
        if checklist_id not in self.state["checklists"]:
            return {
                "completed": [],
                "total": 0,
                "percentage": 0.0,
                "started": None,
                "last_updated": None
            }

        state = self.state["checklists"][checklist_id]
        completed = state.get("completed", [])

        # Load checklist to get total count
        checklist = self.load_checklist(checklist_id)
        if not checklist:
            return state

        total = self._count_items(checklist["items"])
        percentage = (len(completed) / total * 100) if total > 0 else 0.0

        return {
            "completed": completed,
            "total": total,
            "percentage": round(percentage, 1),
            "started": state.get("started"),
            "last_updated": state.get("last_updated")
        }

    def _count_items(self, items: List[Dict], include_optional: bool = True) -> int:
        """Count total items including subitems.

        Args:
            items: List of checklist items
            include_optional: Whether to count optional items

        Returns:
            Total item count
        """
        count = 0
        for item in items:
            if include_optional or not item.get("optional", False):
                count += 1
                if "subitems" in item:
                    count += self._count_items(item["subitems"], include_optional)
        return count

    def complete_item(self, checklist_id: str, item_id: str) -> bool:
        """Mark an item as completed.

        Args:
            checklist_id: Checklist identifier
            item_id: Item identifier

        Returns:
            True if successful
        """
        if checklist_id not in self.state["checklists"]:
            self.state["checklists"][checklist_id] = {
                "completed": [],
                "started": datetime.now().isoformat(),
                "last_updated": None
            }

        completed = self.state["checklists"][checklist_id]["completed"]
        if item_id not in completed:
            completed.append(item_id)
            self.state["checklists"][checklist_id]["last_updated"] = datetime.now().isoformat()
            return self._save_state()

        return True

    def uncomplete_item(self, checklist_id: str, item_id: str) -> bool:
        """Unmark an item as completed.

        Args:
            checklist_id: Checklist identifier
            item_id: Item identifier

        Returns:
            True if successful
        """
        if checklist_id not in self.state["checklists"]:
            return False

        completed = self.state["checklists"][checklist_id]["completed"]
        if item_id in completed:
            completed.remove(item_id)
            self.state["checklists"][checklist_id]["last_updated"] = datetime.now().isoformat()
            return self._save_state()

        return True

    def reset_progress(self, checklist_id: str) -> bool:
        """Reset progress for a checklist.

        Args:
            checklist_id: Checklist identifier

        Returns:
            True if successful
        """
        if checklist_id in self.state["checklists"]:
            del self.state["checklists"][checklist_id]
            return self._save_state()
        return True

    def is_completed(self, checklist_id: str, item_id: str) -> bool:
        """Check if an item is completed.

        Args:
            checklist_id: Checklist identifier
            item_id: Item identifier

        Returns:
            True if item is completed
        """
        if checklist_id not in self.state["checklists"]:
            return False

        return item_id in self.state["checklists"][checklist_id]["completed"]
