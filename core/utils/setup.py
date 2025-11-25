# uDOS v1.0.0 - System Setup & Initialization

import json
import os
from datetime import datetime
from prompt_toolkit import prompt as pt_prompt
from prompt_toolkit.shortcuts import message_dialog

class SystemSetup:
    """
    Handles first-time setup and story.json initialization for uDOS v1.0.0.
    Creates user profile from templates and configures initial environment.
    """

    def __init__(self):
        self.story_path = "knowledge/system/templates/story.template.json"
        self.story_file = self.story_path  # Alias for compatibility
        self.template_path = "knowledge/system/templates/story.template.json"
        self.theme_index_path = "knowledge/system/themes/_index.json"
        self.session_log_file = "memory/logs/session.log"
        self.sandbox_path = "memory/sandbox"
        self.logs_path = "memory/logs"
        self.available_themes = self._load_available_themes()

    def _load_available_themes(self):
        """
        Load available themes from theme index.
        Returns list of theme IDs or defaults if index not found.
        """
        try:
            with open(self.theme_index_path, 'r') as f:
                theme_data = json.load(f)
                return theme_data.get('AVAILABLE_THEMES', ['DUNGEON', 'GALAXY', 'FOUNDATION', 'SCIENCE', 'PROJECT'])
        except (FileNotFoundError, json.JSONDecodeError):
            # Fallback to known themes if index doesn't exist
            return ['DUNGEON', 'GALAXY', 'FOUNDATION', 'SCIENCE', 'PROJECT']

    def needs_setup(self):
        """
        Check if system setup is required.
        Returns True if story.json doesn't exist or is incomplete.
        """
        if not os.path.exists(self.story_path):
            return True

        try:
            with open(self.story_path, 'r') as f:
                story = json.load(f)
                # Check if critical fields are populated
                return not story.get('STORY', {}).get('PROJECT_NAME') or \
                       not story.get('STORY', {}).get('USER_NAME')
        except (FileNotFoundError, json.JSONDecodeError):
            return True

    def ensure_directories(self):
        """
        Create necessary directories if they don't exist.
        """
        os.makedirs(self.sandbox_path, exist_ok=True)
        os.makedirs(self.logs_path, exist_ok=True)

    def run_setup(self):
        """
        Interactive setup process to capture STORY data.
        """
        self.ensure_directories()

        print("\n" + "="*60)
        print("🏰 Welcome to uDOS v1.0.0 - First Time Setup")
        print("="*60 + "\n")
        print("Let's configure your uDOS environment...\n")

        # Load template
        if os.path.exists(self.template_path):
            with open(self.template_path, 'r') as f:
                story_data = json.load(f)
        else:
            # Fallback if template doesn't exist
            print(f"⚠️  Warning: Template not found at {self.template_path}")
            print("    Using minimal default structure...")
            story_data = {
                "SYSTEM_NAME": "uDOS",
                "VERSION": "1.0.0",
                "STORY": {},
                "OPTIONS": {},
                "METADATA": {}
            }

        # Get theme choices dynamically
        theme_choices = "/".join(self.available_themes)
        default_theme = self.available_themes[0] if self.available_themes else "DUNGEON"

        # Capture user data
        try:
            user_name = pt_prompt("Enter your name (adventurer): ").strip()
            if not user_name:
                user_name = "adventurer"

            project_name = pt_prompt("Enter project/story name (default: my-quest): ").strip()
            if not project_name:
                project_name = "my-quest"

            project_desc = pt_prompt("Brief project description (optional): ").strip()

            theme = pt_prompt(f"Choose theme ({theme_choices}) [{default_theme}]: ").strip().upper()
            if theme not in self.available_themes:
                theme = default_theme

        except (KeyboardInterrupt, EOFError):
            print("\n\n⚠️  Setup cancelled. Using defaults...")
            user_name = "adventurer"
            project_name = "my-quest"
            project_desc = "A new uDOS adventure"
            theme = default_theme

        # Populate STORY data
        now = datetime.now().isoformat()
        story_data['STORY'] = {
            "PROJECT_NAME": project_name,
            "PROJECT_DESCRIPTION": project_desc,
            "USER_NAME": user_name,
            "SESSION_START": now,
            "LAST_UPDATED": now,
            "THEME": theme,
            "ACTIVE_PANELS": ["main"],
            "WORKSPACE_PATH": os.getcwd(),
            "NOTES": ""
        }

        # Initialize metadata
        story_data['METADATA'] = {
            "CREATED": now,
            "TOTAL_SESSIONS": 0,
            "TOTAL_COMMANDS": 0
        }

        # Set default options if not present
        if 'OPTIONS' not in story_data or not story_data['OPTIONS']:
            story_data['OPTIONS'] = {
                "AUTO_SAVE_SESSIONS": True,
                "LOG_LEVEL": "INFO",
                "SHOW_TIMESTAMPS": True,
                "PROMPT_STYLE": "dynamic",
                "ENABLE_AI": True,
                "DEFAULT_PANEL": "main",
                "MAX_HISTORY": 100
            }

        # Save story.json
        with open(self.story_path, 'w') as f:
            json.dump(story_data, f, indent=2)

        print(f"\n✅ Setup complete!")
        print(f"📖 Story: {project_name}")
        print(f"👤 User: {user_name}")
        print(f"🎨 Theme: {theme}")
        print(f"📁 Data saved to: {self.story_path}\n")

        return story_data

    def create_default_story(self):
        """
        Create a default story.json without user interaction (for script mode).
        """
        self.ensure_directories()

        # Load template
        if os.path.exists(self.template_path):
            with open(self.template_path, 'r') as f:
                story_data = json.load(f)
        else:
            print(f"⚠️  Warning: Template not found at {self.template_path}")
            story_data = {
                "SYSTEM_NAME": "uDOS",
                "VERSION": "1.0.0",
                "STORY": {},
                "OPTIONS": {},
                "METADATA": {}
            }

        # Set defaults
        default_theme = self.available_themes[0] if self.available_themes else "DUNGEON"
        now = datetime.now().isoformat()
        story_data['STORY'] = {
            "PROJECT_NAME": "my-quest",
            "PROJECT_DESCRIPTION": "A uDOS adventure",
            "USER_NAME": "adventurer",
            "SESSION_START": now,
            "LAST_UPDATED": now,
            "THEME": default_theme,
            "ACTIVE_PANELS": ["main"],
            "WORKSPACE_PATH": os.getcwd(),
            "NOTES": ""
        }

        story_data['METADATA'] = {
            "CREATED": now,
            "TOTAL_SESSIONS": 0,
            "TOTAL_COMMANDS": 0
        }

        if 'OPTIONS' not in story_data or not story_data['OPTIONS']:
            story_data['OPTIONS'] = {
                "AUTO_SAVE_SESSIONS": True,
                "LOG_LEVEL": "INFO",
                "SHOW_TIMESTAMPS": True,
                "PROMPT_STYLE": "dynamic",
                "ENABLE_AI": True,
                "DEFAULT_PANEL": "main",
                "MAX_HISTORY": 100
            }

        # Save story.json
        with open(self.story_path, 'w') as f:
            json.dump(story_data, f, indent=2)

        return story_data

    def load_story(self):
        """
        Load existing story.json data.
        Returns None if file doesn't exist or is invalid.
        """
        try:
            with open(self.story_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"⚠️  Error loading story data: {e}")
            return None

    def update_story(self, story_data):
        """
        Update story.json with new data.
        Automatically updates LAST_UPDATED timestamp.
        """
        story_data['STORY']['LAST_UPDATED'] = datetime.now().isoformat()
        with open(self.story_path, 'w') as f:
            json.dump(story_data, f, indent=2)

    def increment_session(self):
        """
        Increment session counter.
        """
        story = self.load_story()
        if story:
            story['METADATA']['TOTAL_SESSIONS'] = story['METADATA'].get('TOTAL_SESSIONS', 0) + 1
            self.update_story(story)
