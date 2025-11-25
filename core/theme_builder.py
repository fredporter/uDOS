"""
uDOS v1.0.13 - Theme Builder Service

Interactive theme creation wizard for building custom uDOS themes.
Guides users through creating themes with proper structure and validation.

Features:
- Interactive step-by-step theme creation
- Template-based theme generation
- Color palette suggestions
- Component-by-component customization
- Validation and preview integration
- Export to .json and .udostheme formats

Version: 1.0.13
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from core.services.standardized_input import StandardizedInput


class ThemeBuilder:
    """Interactive theme builder with wizard-style creation."""

    def __init__(self, theme_manager=None):
        """
        Initialize Theme Builder.

        Args:
            theme_manager: Optional ThemeManager instance for validation
        """
        self.theme_manager = theme_manager
        self.templates_dir = Path("knowledge/system/themes/templates")
        self.output_dir = Path("knowledge/system/themes")
        self.input_service = StandardizedInput()

        # Default templates
        self.templates = {
            "minimal": self._get_minimal_template(),
            "sci-fi": self._get_scifi_template(),
            "fantasy": self._get_fantasy_template(),
            "corporate": self._get_corporate_template()
        }

    def _get_minimal_template(self) -> Dict:
        """Get minimal theme template with required fields."""
        return {
            "THEME_NAME": "",
            "VERSION": "1.0.0",
            "NAME": "",
            "STYLE": "",
            "DESCRIPTION": "",
            "ICON": "🎨",
            "VERBOSE_LEVEL": "MEDIUM",

            "CORE_SYSTEM": {
                "PROMPT_BASE": ">",
                "SYSTEM_NAME": "SYSTEM",
                "SYSTEM_STATUS": "OPERATIONAL",
                "SYSTEM_VERSION": "1.0.0"
            },

            "CORE_USER": {
                "USER_NAME": "User",
                "USER_TITLE": "Operator",
                "USER_LOCATION": "Terminal",
                "USER_TIMEZONE": "UTC",
                "USER_PROJECT": "Default",
                "USER_PROJECT_TYPE": "General",
                "USER_MODE": "Standard",
                "USER_LEVEL": "User",
                "USER_EXPERIENCE": 0
            },

            "TERMINOLOGY": {
                "PROMPT_BASE": ">",
                "CMD_CATALOG": "LIST",
                "CMD_LOAD": "LOAD",
                "CMD_SAVE": "SAVE",
                "CMD_RUN": "RUN",
                "CMD_CLS": "CLEAR",
                "CMD_COMMANDS": "COMMANDS",
                "CMD_HELP": "HELP",
                "CMD_RESTART": "RESTART"
            }
        }

    def _get_scifi_template(self) -> Dict:
        """Get sci-fi themed template."""
        template = self._get_minimal_template()
        template.update({
            "STYLE": "Science Fiction",
            "ICON": "🚀",
            "CORE_SYSTEM": {
                "PROMPT_BASE": "CONSOLE>",
                "SYSTEM_NAME": "MAINFRAME",
                "SYSTEM_STATUS": "ONLINE",
                "SYSTEM_VERSION": "1.0.0"
            },
            "CORE_USER": {
                "USER_NAME": "Operator",
                "USER_TITLE": "Systems Technician",
                "USER_LOCATION": "Command Deck",
                "USER_TIMEZONE": "Ship Time",
                "USER_PROJECT": "Mission Control",
                "USER_PROJECT_TYPE": "Space Operations",
                "USER_MODE": "Active",
                "USER_LEVEL": "Officer",
                "USER_EXPERIENCE": 0
            },
            "TERMINOLOGY": {
                "PROMPT_BASE": "CONSOLE>",
                "CMD_CATALOG": "SCAN",
                "CMD_LOAD": "ACCESS",
                "CMD_SAVE": "STORE",
                "CMD_RUN": "EXECUTE",
                "CMD_CLS": "PURGE",
                "CMD_COMMANDS": "PROTOCOLS",
                "CMD_HELP": "MANUAL",
                "CMD_RESTART": "REBOOT"
            }
        })
        return template

    def _get_fantasy_template(self) -> Dict:
        """Get fantasy themed template."""
        template = self._get_minimal_template()
        template.update({
            "STYLE": "Fantasy RPG",
            "ICON": "⚔️",
            "CORE_SYSTEM": {
                "PROMPT_BASE": "QUEST>",
                "SYSTEM_NAME": "TOME_OF_KNOWLEDGE",
                "SYSTEM_STATUS": "ACTIVE",
                "SYSTEM_VERSION": "1.0.0"
            },
            "CORE_USER": {
                "USER_NAME": "Adventurer",
                "USER_TITLE": "Wanderer",
                "USER_LOCATION": "Tavern",
                "USER_TIMEZONE": "Realm Time",
                "USER_PROJECT": "Quest Log",
                "USER_PROJECT_TYPE": "Adventure",
                "USER_MODE": "Explore",
                "USER_LEVEL": "Level 1",
                "USER_EXPERIENCE": 0
            },
            "TERMINOLOGY": {
                "PROMPT_BASE": "QUEST>",
                "CMD_CATALOG": "INVENTORY",
                "CMD_LOAD": "EXAMINE",
                "CMD_SAVE": "CHRONICLE",
                "CMD_RUN": "CAST",
                "CMD_CLS": "DISPEL",
                "CMD_COMMANDS": "ABILITIES",
                "CMD_HELP": "GUIDE",
                "CMD_RESTART": "RESURRECT"
            }
        })
        return template

    def _get_corporate_template(self) -> Dict:
        """Get corporate/professional themed template."""
        template = self._get_minimal_template()
        template.update({
            "STYLE": "Corporate Professional",
            "ICON": "💼",
            "CORE_SYSTEM": {
                "PROMPT_BASE": "CMD>",
                "SYSTEM_NAME": "WORKSTATION",
                "SYSTEM_STATUS": "READY",
                "SYSTEM_VERSION": "1.0.0"
            },
            "CORE_USER": {
                "USER_NAME": "Professional",
                "USER_TITLE": "Analyst",
                "USER_LOCATION": "Office",
                "USER_TIMEZONE": "Local Time",
                "USER_PROJECT": "Current Project",
                "USER_PROJECT_TYPE": "Business",
                "USER_MODE": "Work",
                "USER_LEVEL": "Staff",
                "USER_EXPERIENCE": 0
            },
            "TERMINOLOGY": {
                "PROMPT_BASE": "CMD>",
                "CMD_CATALOG": "INDEX",
                "CMD_LOAD": "OPEN",
                "CMD_SAVE": "SAVE",
                "CMD_RUN": "EXECUTE",
                "CMD_CLS": "CLEAR",
                "CMD_COMMANDS": "MENU",
                "CMD_HELP": "HELP",
                "CMD_RESTART": "RESTART"
            }
        })
        return template

    def create_theme_interactive(self) -> Optional[Dict]:
        """
        Interactive theme creation wizard.

        Returns:
            Created theme dict or None if cancelled
        """
        print("\n╔═══════════════════════════════════════════════════════════╗")
        print("║            THEME BUILDER - Interactive Wizard             ║")
        print("╚═══════════════════════════════════════════════════════════╝\n")

        # Step 1: Choose template
        template_choice = self.input_service.select_option(
            title="Step 1: Choose a starting template",
            options=["Minimal - Start from scratch",
                    "Sci-Fi - Space/technology theme",
                    "Fantasy - RPG/adventure theme",
                    "Corporate - Professional/business theme"],
            show_numbers=True
        )

        template_map = {
            "Minimal - Start from scratch": "minimal",
            "Sci-Fi - Space/technology theme": "sci-fi",
            "Fantasy - RPG/adventure theme": "fantasy",
            "Corporate - Professional/business theme": "corporate"
        }

        template_name = template_map.get(template_choice, "minimal")
        theme_data = self.templates[template_name].copy()

        print(f"\n✓ Using {template_name} template\n")

        # Step 2: Basic information
        print("Step 2: Basic Information")

        theme_name = self.input_service.text_input(
            "Theme Name (e.g., CYBERPUNK)",
            required=True
        ).strip().upper()

        theme_data["THEME_NAME"] = theme_name

        display_name = self.input_service.text_input(
            "Display Name (e.g., Cyberpunk 2077)"
        ).strip()
        if display_name:
            theme_data["NAME"] = display_name

        style = self.input_service.text_input(
            "Style (e.g., Cyberpunk/Sci-Fi)"
        ).strip()
        if style:
            theme_data["STYLE"] = style

        description = self.input_service.text_input(
            "Description"
        ).strip()
        if description:
            theme_data["DESCRIPTION"] = description

        # Step 3: Icon
        print("\nStep 3: Theme Icon")
        print("  Suggested icons: 🎨 🚀 ⚔️ 💼 🌟 🔮 🎯 🌈 🎭 🔥")
        icon = self.input_service.text_input(
            "Choose an icon",
            default="🎨"
        ).strip()
        if icon:
            theme_data["ICON"] = icon

        # Step 4: System configuration
        print("\nStep 4: System Configuration")

        customize_system = self.input_service.select_option(
            title="Customize system settings?",
            options=["Yes", "No"],
            default_index=1
        )

        if customize_system == "Yes":
            prompt = self.input_service.text_input(
                f"Command prompt (current: {theme_data['CORE_SYSTEM']['PROMPT_BASE']})"
            ).strip()
            if prompt:
                theme_data["CORE_SYSTEM"]["PROMPT_BASE"] = prompt
                theme_data["TERMINOLOGY"]["PROMPT_BASE"] = prompt

            system_name = self.input_service.text_input(
                f"System name (current: {theme_data['CORE_SYSTEM']['SYSTEM_NAME']})"
            ).strip()
            if system_name:
                theme_data["CORE_SYSTEM"]["SYSTEM_NAME"] = system_name

        # Step 5: User configuration
        print("\nStep 5: User Configuration")

        customize_user = self.input_service.select_option(
            title="Customize user settings?",
            options=["Yes", "No"],
            default_index=1
        )

        if customize_user == "Yes":
            user_name = self.input_service.text_input(
                f"User name (current: {theme_data['CORE_USER']['USER_NAME']})"
            ).strip()
            if user_name:
                theme_data["CORE_USER"]["USER_NAME"] = user_name

            user_title = self.input_service.text_input(
                f"User title (current: {theme_data['CORE_USER']['USER_TITLE']})"
            ).strip()
            if user_title:
                theme_data["CORE_USER"]["USER_TITLE"] = user_title

            location = self.input_service.text_input(
                f"Location (current: {theme_data['CORE_USER']['USER_LOCATION']})"
            ).strip()
            if location:
                theme_data["CORE_USER"]["USER_LOCATION"] = location

        # Step 6: Terminology
        print("\nStep 6: Command Terminology")

        customize_terms = self.input_service.select_option(
            title="Customize command names?",
            options=["Yes", "No"],
            default_index=1
        )

        if customize_terms == "Yes":
            print("\n  Customize key commands (press Enter to keep current):")

            commands = [
                ("CMD_CATALOG", "List files command"),
                ("CMD_LOAD", "Open file command"),
                ("CMD_SAVE", "Save file command"),
                ("CMD_HELP", "Help command"),
                ("CMD_CLS", "Clear screen command")
            ]

            for cmd_key, description in commands:
                current = theme_data["TERMINOLOGY"][cmd_key]
                new_value = self.input_service.text_input(
                    f"{description} (current: {current})"
                ).strip()
                if new_value:
                    theme_data["TERMINOLOGY"][cmd_key] = new_value

        # Add metadata
        theme_data["AUTHOR"] = "Custom Theme Builder"
        theme_data["CREATED"] = datetime.now().isoformat()
        theme_data["UDOS_VERSION"] = "1.0.13"

        print("\n✓ Theme creation complete!\n")
        return theme_data

    def create_from_template(self, template_name: str, customizations: Dict) -> Dict:
        """
        Create theme from template with specific customizations.

        Args:
            template_name: Name of template to use
            customizations: Dict of fields to customize

        Returns:
            Created theme dict
        """
        if template_name not in self.templates:
            template_name = "minimal"

        theme_data = self.templates[template_name].copy()

        # Apply customizations
        for key, value in customizations.items():
            if isinstance(value, dict):
                # Nested update
                if key in theme_data and isinstance(theme_data[key], dict):
                    theme_data[key].update(value)
                else:
                    theme_data[key] = value
            else:
                theme_data[key] = value

        # Add metadata
        theme_data["AUTHOR"] = customizations.get("AUTHOR", "Theme Builder")
        theme_data["CREATED"] = datetime.now().isoformat()
        theme_data["UDOS_VERSION"] = "1.0.13"

        return theme_data

    def save_theme(self, theme_data: Dict, filename: Optional[str] = None) -> bool:
        """
        Save theme to file.

        Args:
            theme_data: Theme data to save
            filename: Optional filename (uses THEME_NAME if not provided)

        Returns:
            True if successful
        """
        if not filename:
            filename = theme_data.get("THEME_NAME", "custom_theme").lower()

        # Ensure .json extension
        if not filename.endswith('.json'):
            filename += '.json'

        output_file = self.output_dir / filename

        try:
            with open(output_file, 'w') as f:
                json.dump(theme_data, f, indent=2)

            print(f"✅ Theme saved to: {output_file}")
            return True

        except Exception as e:
            print(f"❌ Error saving theme: {e}")
            return False

    def copy_theme(self, source_theme: str, new_name: str, modifications: Optional[Dict] = None) -> Optional[Dict]:
        """
        Copy an existing theme with modifications.

        Args:
            source_theme: Name of theme to copy
            new_name: Name for new theme
            modifications: Optional modifications to apply

        Returns:
            New theme dict or None if error
        """
        # Load source theme using theme manager if available
        if self.theme_manager:
            source_data = self.theme_manager.load_json_theme(source_theme)
        else:
            # Try loading directly
            source_file = self.output_dir / f"{source_theme}.json"
            if not source_file.exists():
                print(f"Error: Source theme '{source_theme}' not found")
                return None

            try:
                with open(source_file, 'r') as f:
                    source_data = json.load(f)
            except Exception as e:
                print(f"Error loading source theme: {e}")
                return None

        if not source_data:
            return None

        # Create copy
        new_theme = source_data.copy()
        new_theme["THEME_NAME"] = new_name.upper()
        new_theme["NAME"] = new_name.title()
        new_theme["MODIFIED"] = datetime.now().isoformat()
        new_theme["BASED_ON"] = source_theme

        # Apply modifications if provided
        if modifications:
            for key, value in modifications.items():
                if isinstance(value, dict) and key in new_theme and isinstance(new_theme[key], dict):
                    new_theme[key].update(value)
                else:
                    new_theme[key] = value

        return new_theme

    def validate_and_fix(self, theme_data: Dict) -> Tuple[Dict, List[str]]:
        """
        Validate theme and attempt to fix common issues.

        Args:
            theme_data: Theme data to validate

        Returns:
            Tuple of (fixed_theme_data, list_of_warnings)
        """
        warnings = []
        fixed_data = theme_data.copy()

        # Check required fields
        required_fields = {
            "THEME_NAME": "CUSTOM_THEME",
            "VERSION": "1.0.0",
            "NAME": "Custom Theme",
            "STYLE": "Custom",
            "DESCRIPTION": "No description provided",
            "ICON": "🎨"
        }

        for field, default in required_fields.items():
            if field not in fixed_data or not fixed_data[field]:
                fixed_data[field] = default
                warnings.append(f"Added missing field: {field}")

        # Check required sections
        required_sections = ["CORE_SYSTEM", "CORE_USER", "TERMINOLOGY"]
        for section in required_sections:
            if section not in fixed_data:
                if section == "CORE_SYSTEM":
                    fixed_data[section] = {"PROMPT_BASE": ">", "SYSTEM_NAME": "SYSTEM"}
                elif section == "CORE_USER":
                    fixed_data[section] = {"USER_NAME": "User", "USER_LOCATION": "Terminal"}
                elif section == "TERMINOLOGY":
                    fixed_data[section] = {"CMD_CATALOG": "LIST", "CMD_HELP": "HELP"}
                warnings.append(f"Added missing section: {section}")

        # Validate TERMINOLOGY has basic commands
        required_commands = ["CMD_CATALOG", "CMD_LOAD", "CMD_SAVE", "CMD_HELP"]
        term = fixed_data.get("TERMINOLOGY", {})
        for cmd in required_commands:
            if cmd not in term:
                term[cmd] = cmd.replace("CMD_", "")
                warnings.append(f"Added missing command: {cmd}")

        return fixed_data, warnings

    def get_color_palette_suggestions(self, style: str) -> Dict[str, List[str]]:
        """
        Get color palette suggestions based on style.

        Args:
            style: Theme style (sci-fi, fantasy, corporate, etc.)

        Returns:
            Dict of color categories with hex values
        """
        palettes = {
            "sci-fi": {
                "primary": ["#00FFFF", "#0080FF", "#00FF80"],
                "accent": ["#FF00FF", "#FF0080", "#8000FF"],
                "background": ["#000020", "#001030", "#002040"]
            },
            "fantasy": {
                "primary": ["#FFD700", "#FF8C00", "#FF4500"],
                "accent": ["#9370DB", "#8B008B", "#4B0082"],
                "background": ["#1A0A00", "#2D1810", "#3F2418"]
            },
            "corporate": {
                "primary": ["#0066CC", "#003366", "#004080"],
                "accent": ["#00CC99", "#009966", "#006644"],
                "background": ["#F5F5F5", "#E8E8E8", "#D3D3D3"]
            },
            "cyberpunk": {
                "primary": ["#FF00FF", "#00FFFF", "#FFFF00"],
                "accent": ["#FF0080", "#00FF80", "#8000FF"],
                "background": ["#000000", "#0A0A0A", "#1A001A"]
            }
        }

        return palettes.get(style.lower(), palettes["sci-fi"])

    def list_templates(self) -> str:
        """
        List available theme templates.

        Returns:
            Formatted string of templates
        """
        output = []
        output.append("\n╔═══════════════════════════════════════════════════════════╗")
        output.append("║              AVAILABLE THEME TEMPLATES                    ║")
        output.append("╚═══════════════════════════════════════════════════════════╝\n")

        template_descriptions = {
            "minimal": "🎨 Minimal - Basic template with required fields only",
            "sci-fi": "🚀 Sci-Fi - Space/technology themed template",
            "fantasy": "⚔️ Fantasy - RPG/adventure themed template",
            "corporate": "💼 Corporate - Professional/business themed template"
        }

        for name, description in template_descriptions.items():
            output.append(f"  {description}")

        output.append("")
        return "\n".join(output)

    def get_quick_start_guide(self) -> str:
        """
        Get quick start guide for theme creation.

        Returns:
            Formatted guide string
        """
        guide = """
╔═══════════════════════════════════════════════════════════╗
║               THEME BUILDER - Quick Start                 ║
╚═══════════════════════════════════════════════════════════╝

Creating a Custom Theme:

1. Interactive Mode:
   THEME CREATE INTERACTIVE
   - Step-by-step wizard
   - Choose template and customize
   - Preview before saving

2. From Template:
   THEME CREATE FROM <template>
   - Start with pre-built template
   - Customize specific fields
   - Quick theme generation

3. Copy Existing:
   THEME COPY <source> <new_name>
   - Copy any existing theme
   - Modify specific elements
   - Preserve working structure

Required Theme Fields:
  - THEME_NAME: Unique identifier (uppercase)
  - VERSION: Theme version (e.g., 1.0.0)
  - NAME: Display name
  - STYLE: Theme style/category
  - DESCRIPTION: Brief description
  - ICON: Emoji icon
  - CORE_SYSTEM: System configuration
  - CORE_USER: User defaults
  - TERMINOLOGY: Command names

Tips:
  • Start with a template close to your vision
  • Use THEME PREVIEW to see changes
  • Validate before saving with THEME VALIDATE
  • Export for sharing with THEME EXPORT

Examples:
  THEME CREATE INTERACTIVE
  THEME CREATE FROM sci-fi
  THEME COPY foundation my-foundation
  THEME PREVIEW my-theme
"""
        return guide
