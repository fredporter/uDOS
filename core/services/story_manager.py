"""
uDOS v1.0.29 - Story Manager
Manages story.json lifecycle, user profile, and session data
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional, List
import pytz


class StoryManager:
    """
    Manages story.json lifecycle and user profile configuration.
    Provides unified access to user data, session tracking, and story fields.
    """

    def __init__(self, story_path: str = "memory/sandbox/user.json"):
        """
        Initialize story manager.

        Args:
            story_path: Path to story.json file
        """
        self.story_path = Path(story_path)
        self.template_path = Path("knowledge/system/templates/story.template.json")
        self.story_data = None
        self._load_story()

    def _load_story(self) -> Dict[str, Any]:
        """Load story.json from disk"""
        if self.story_path.exists():
            try:
                with open(self.story_path, 'r') as f:
                    self.story_data = json.load(f)
                return self.story_data
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️  Error loading story: {e}")
                self.story_data = self._create_default_story()
                return self.story_data
        else:
            self.story_data = self._create_default_story()
            return self.story_data

    def _create_default_story(self) -> Dict[str, Any]:
        """Create default story structure from template"""
        # Try to load template
        if self.template_path.exists():
            try:
                with open(self.template_path, 'r') as f:
                    template = json.load(f)
                    # Ensure required sections exist
                    if 'STORY' not in template:
                        template['STORY'] = {}
                    if 'OPTIONS' not in template:
                        template['OPTIONS'] = {}
                    if 'METADATA' not in template:
                        template['METADATA'] = {}
                    return template
            except (json.JSONDecodeError, IOError):
                pass

        # Fallback: create minimal structure
        return {
            "SYSTEM_NAME": "uDOS",
            "VERSION": "1.0.29",
            "STORY": {
                "PROJECT_NAME": "",
                "USER_NAME": "",
                "THEME": "dungeon",
                "SESSION_START": datetime.now().isoformat(),
                "WORKSPACE_PATH": os.getcwd()
            },
            "OPTIONS": {
                "AUTO_SAVE_SESSIONS": True,
                "LOG_LEVEL": "INFO",
                "ENABLE_AI": True
            },
            "METADATA": {
                "CREATED": datetime.now().isoformat(),
                "TOTAL_SESSIONS": 0,
                "TOTAL_COMMANDS": 0
            }
        }

    def needs_setup(self) -> bool:
        """
        Check if initial setup is required.

        Returns:
            True if story is incomplete and needs setup
        """
        if not self.story_data:
            return True

        # Check required fields
        story = self.story_data.get('STORY', {})

        # User name is required
        if not story.get('USER_NAME'):
            return True

        # Project name is required
        if not story.get('PROJECT_NAME'):
            return True

        return False

    def get_field(self, field_path: str, default: Any = None) -> Any:
        """
        Get field value using dot notation.

        Args:
            field_path: Dot-separated path (e.g., "STORY.USER_NAME")
            default: Default value if not found

        Returns:
            Field value or default

        Example:
            name = story_mgr.get_field("STORY.USER_NAME", "adventurer")
            theme = story_mgr.get_field("STORY.THEME", "dungeon")
        """
        if not self.story_data:
            return default

        try:
            parts = field_path.split('.')
            current = self.story_data

            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return default

            return current if current is not None else default

        except (KeyError, TypeError, AttributeError):
            return default

    def set_field(self, field_path: str, value: Any, auto_save: bool = True) -> bool:
        """
        Set field value using dot notation.

        Args:
            field_path: Dot-separated path
            value: Value to set
            auto_save: Automatically save to disk after setting

        Returns:
            True if successful

        Example:
            story_mgr.set_field("STORY.USER_NAME", "Fred")
            story_mgr.set_field("OPTIONS.THEME", "hacker")
        """
        if not self.story_data:
            self.story_data = self._create_default_story()

        try:
            parts = field_path.split('.')
            current = self.story_data

            # Navigate to parent, creating dicts as needed
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                elif not isinstance(current[part], dict):
                    current[part] = {}
                current = current[part]

            # Set final value
            current[parts[-1]] = value

            # Update last modified timestamp
            if 'STORY' in self.story_data:
                self.story_data['STORY']['LAST_UPDATED'] = datetime.now().isoformat()

            # Auto-save if requested
            if auto_save:
                return self.save()

            return True

        except (KeyError, TypeError, AttributeError) as e:
            print(f"❌ Error setting field {field_path}: {e}")
            return False

    def save(self) -> bool:
        """
        Save story data to disk.

        Returns:
            True if successful
        """
        if not self.story_data:
            return False

        try:
            # Ensure directory exists
            self.story_path.parent.mkdir(parents=True, exist_ok=True)

            # Write to file
            with open(self.story_path, 'w') as f:
                json.dump(self.story_data, f, indent=2)

            return True

        except IOError as e:
            print(f"❌ Error saving story: {e}")
            return False

    def validate(self) -> tuple[bool, List[str]]:
        """
        Validate story data completeness.

        Returns:
            (is_valid, list of errors)
        """
        errors = []

        if not self.story_data:
            errors.append("Story data not loaded")
            return (False, errors)

        # Check required sections
        required_sections = ['STORY', 'OPTIONS', 'METADATA']
        for section in required_sections:
            if section not in self.story_data:
                errors.append(f"Missing section: {section}")

        # Check required STORY fields
        story = self.story_data.get('STORY', {})
        required_fields = {
            'PROJECT_NAME': 'Project name',
            'USER_NAME': 'User name',
            'THEME': 'Theme'
        }

        for field, name in required_fields.items():
            if not story.get(field):
                errors.append(f"Missing required field: {name}")

        return (len(errors) == 0, errors)

    def increment_session(self) -> int:
        """
        Increment session counter.

        Returns:
            New session count
        """
        if not self.story_data:
            self._load_story()

        if 'METADATA' not in self.story_data:
            self.story_data['METADATA'] = {}

        current = self.story_data['METADATA'].get('TOTAL_SESSIONS', 0)
        new_count = current + 1

        self.story_data['METADATA']['TOTAL_SESSIONS'] = new_count
        self.save()

        return new_count

    def increment_commands(self, count: int = 1) -> int:
        """
        Increment command counter.

        Args:
            count: Number of commands to add

        Returns:
            New command count
        """
        if not self.story_data:
            self._load_story()

        if 'METADATA' not in self.story_data:
            self.story_data['METADATA'] = {}

        current = self.story_data['METADATA'].get('TOTAL_COMMANDS', 0)
        new_count = current + count

        self.story_data['METADATA']['TOTAL_COMMANDS'] = new_count
        self.save()

        return new_count

    def get_user_profile(self) -> Dict[str, Any]:
        """
        Get complete user profile.

        Returns:
            User profile dictionary
        """
        story = self.story_data.get('STORY', {}) if self.story_data else {}

        return {
            'name': story.get('USER_NAME', 'adventurer'),
            'project': story.get('PROJECT_NAME', 'my-quest'),
            'theme': story.get('THEME', 'dungeon'),
            'timezone': story.get('TIMEZONE', 'UTC'),
            'location': story.get('LOCATION', 'Unknown'),
            'workspace': story.get('WORKSPACE_PATH', os.getcwd())
        }

    def detect_timezone(self) -> str:
        """
        Auto-detect user's timezone.

        Returns:
            Timezone string (e.g., "Australia/Brisbane")
        """
        try:
            import tzlocal
            local_tz = tzlocal.get_localzone()
            return str(local_tz)
        except:
            # Fallback: use UTC offset
            from datetime import timezone
            local_tz = datetime.now(timezone.utc).astimezone().tzinfo
            return str(local_tz) if local_tz else "UTC"

    def export_story(self, output_path: str) -> bool:
        """
        Export story to a file.

        Args:
            output_path: Path to export file

        Returns:
            True if successful
        """
        if not self.story_data:
            return False

        try:
            output = Path(output_path)
            output.parent.mkdir(parents=True, exist_ok=True)

            with open(output, 'w') as f:
                json.dump(self.story_data, f, indent=2)

            return True

        except IOError as e:
            print(f"❌ Error exporting story: {e}")
            return False

    def import_story(self, import_path: str) -> bool:
        """
        Import story from a file.

        Args:
            import_path: Path to import file

        Returns:
            True if successful
        """
        try:
            import_file = Path(import_path)

            if not import_file.exists():
                print(f"❌ File not found: {import_path}")
                return False

            with open(import_file, 'r') as f:
                imported_data = json.load(f)

            # Validate imported data
            if 'STORY' not in imported_data:
                print(f"❌ Invalid story file: missing STORY section")
                return False

            # Backup current story
            if self.story_path.exists():
                backup_path = self.story_path.with_suffix('.json.backup')
                with open(self.story_path, 'r') as f:
                    with open(backup_path, 'w') as b:
                        b.write(f.read())

            # Import new story
            self.story_data = imported_data
            return self.save()

        except (IOError, json.JSONDecodeError) as e:
            print(f"❌ Error importing story: {e}")
            return False


def create_story_manager(story_path: str = "memory/sandbox/user.json") -> StoryManager:
    """
    Factory function to create StoryManager instance.

    Args:
        story_path: Path to story.json file

    Returns:
        StoryManager instance
    """
    return StoryManager(story_path=story_path)
