"""
uDOS v1.0.29 - Setup Wizard Service (Smart Mode)

Interactive onboarding and configuration wizard for new users.
Guides users through initial setup with step-by-step prompts.

Features:
- Interactive step-by-step wizard with InputManager
- Complete story.json user profile setup
- Theme selection with previews
- Viewport configuration
- Extension discovery and installation
- Quick setup with sensible defaults
- Configuration validation
- Settings export/import

Version: 1.0.29 (Smart Input Integration)
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any


class SetupWizard:
    """Interactive setup wizard for uDOS configuration."""

    def __init__(self, input_manager=None, story_manager=None, output_formatter=None):
        """
        Initialize Setup Wizard.

        Args:
            input_manager: InputManager instance for smart prompts
            story_manager: StoryManager instance for story.json access
            output_formatter: OutputFormatter instance for consistent output
        """
        from core.utils.paths import PATHS
        self.config_file = str(PATHS.MEMORY_BANK / "user" / "USER.UDT")
        self.themes_dir = Path("core/data/themes")
        self.user_config = {}

        # v1.0.29: Smart input services
        self._input_manager = input_manager
        self._story_manager = story_manager
        self._output_formatter = output_formatter

        # Available options
        self.available_themes = self._load_available_themes()
        self.available_viewports = self._get_viewport_presets()

    @property
    def input_manager(self):
        """Lazy-load InputManager if not provided."""
        if self._input_manager is None:
            from core.services.input_manager import InputManager
            self._input_manager = InputManager()
        return self._input_manager

    @property
    def story_manager(self):
        """Lazy-load StoryManager if not provided."""
        if self._story_manager is None:
            from core.output.story_manager import StoryManager
            # Use same file as Config reads from
            self._story_manager = StoryManager(story_path=str(PATHS.MEMORY_BANK / "user" / "user.json"))
        return self._story_manager

    @property
    def output_formatter(self):
        """Lazy-load OutputFormatter if not provided."""
        if self._output_formatter is None:
            from core.output.output_formatter import OutputFormatter
            self._output_formatter = OutputFormatter()
        return self._output_formatter

    def _load_available_themes(self) -> List[str]:
        """Load list of available themes."""
        try:
            themes_index = self.themes_dir / "_index.json"
            if themes_index.exists():
                with open(themes_index, 'r') as f:
                    data = json.load(f)
                    # Try different keys
                    themes = data.get('AVAILABLE_THEMES') or data.get('themes', [])
                    if themes:
                        return [t.lower() for t in themes]  # Normalize to lowercase
        except:
            pass

        # Try scanning directory
        try:
            if self.themes_dir.exists():
                themes = [f.stem for f in self.themes_dir.glob("*.json")
                         if not f.name.startswith("_")]
                if themes:
                    return themes
        except:
            pass

        pass

        # Fallback to known themes
        return ["dungeon", "foundation", "galaxy", "project", "science"]

    def _get_viewport_presets(self) -> List[Dict[str, Any]]:
        """Get viewport presets."""
        return [
            {"name": "Watch", "size": "13×13", "tier": 0},
            {"name": "Mobile", "size": "20×40", "tier": 3},
            {"name": "Tablet", "size": "30×60", "tier": 6},
            {"name": "Desktop", "size": "40×80", "tier": 9},
            {"name": "Cinema", "size": "360×150", "tier": 14}
        ]

    def run_full_wizard(self) -> str:
        """
        Run the complete interactive setup wizard (v1.0.29 Smart Mode).

        Returns:
            Success message with summary
        """
        try:
            output = []

            # Welcome screen
            output.append(self._format_welcome())
            output.append("\n")

            # Check if user needs setup
            needs_setup = self.story_manager.needs_setup()

            if needs_setup:
                output.append(self.output_formatter.format_info(
                    "First-time setup required. Let's configure your profile!"
                ))
            else:
                # Ask if user wants to reconfigure
                reconfigure = self.input_manager.prompt_confirm(
                    message="Your profile is already configured. Reconfigure?",
                    default=False
                )
                if not reconfigure:
                    return "Setup cancelled. Your current configuration is unchanged."

            output.append("\n")

            # Step 1: User Profile (required for first-time setup)
            output.append(self.output_formatter.format_panel(
                "Step 1/4: User Profile",
                "Let's set up your personal information"
            ))
            self._wizard_step_user_profile()
            output.append("✅ User profile configured\n")

            # Step 2: Theme selection
            output.append(self.output_formatter.format_panel(
                "Step 2/4: Theme Selection",
                "Choose your visual theme"
            ))
            theme = self._wizard_step_theme()
            output.append(f"✅ Theme set to: {theme}\n")

            # Step 3: Viewport configuration
            output.append(self.output_formatter.format_panel(
                "Step 3/4: Viewport Configuration",
                "Configure your display settings"
            ))
            viewport = self._wizard_step_viewport()
            output.append(f"✅ Viewport configured: {viewport}\n")

            # Step 4: Extensions (optional)
            skip_extensions = self.input_manager.prompt_confirm(
                message="Skip extension setup? (You can configure later with POKE)",
                default=True
            )

            if not skip_extensions:
                output.append(self.output_formatter.format_panel(
                    "Step 4/4: Extensions",
                    "Configure web extensions"
                ))
                extensions = self._wizard_step_extensions()
                ext_count = sum(1 for v in extensions.values() if v)
                output.append(f"✅ {ext_count} extensions enabled\n")
            else:
                output.append("⏭️  Extensions skipped\n")

            # Summary
            output.append("\n")
            output.append(self._format_completion_summary())

            return "\n".join(output)

        except KeyboardInterrupt:
            return "\n⚠️ Setup cancelled by user. Run SETUP again to complete configuration."
        except Exception as e:
            return self.output_formatter.format_error(
                "Setup wizard failed",
                error_details=str(e)
            )

    def run_quick_setup(self) -> str:
        """
        Run quick setup with sensible defaults (v1.0.29).

        Returns:
            Success message
        """
        try:
            # Check if profile exists
            needs_setup = self.story_manager.needs_setup()

            if needs_setup:
                # Auto-detect timezone and location
                from core.utils.system_info import get_system_timezone
                detected_timezone, detected_city = get_system_timezone()

                # Must get user name at minimum
                user_name = self.input_manager.prompt_user(
                    message="Your name:",
                    required=True
                )

                self.story_manager.set_field('USER_PROFILE.NAME', user_name, auto_save=False)

                # Auto-set timezone and location from detection
                self.story_manager.set_field('USER_PROFILE.TIMEZONE', detected_timezone, auto_save=False)
                self.story_manager.set_field('USER_PROFILE.LOCATION', detected_city, auto_save=False)

            # Apply default theme if not set
            current_theme = self.story_manager.get_field('system_settings.interface.theme', '')
            if not current_theme:
                self.story_manager.set_field('system_settings.interface.theme', 'dungeon', auto_save=False)

            # Save all changes
            self.story_manager.save()

            output = []
            output.append(self.output_formatter.format_success(
                "Quick setup complete!",
                details={
                    'Theme': self.story_manager.get_field('system_settings.interface.theme', 'dungeon'),
                    'Viewport': 'Auto-detect',
                    'Extensions': 'Enabled (web, teletext, dashboard)'
                }
            ))
            output.append("\n💡 Run SETUP for full configuration wizard")

            return "\n".join(output)

        except Exception as e:
            return self.output_formatter.format_error(
                "Quick setup failed",
                error_details=str(e)
            )

    def setup_theme_only(self) -> str:
        """Run theme selection wizard only (v1.0.29)."""
        try:
            theme = self._wizard_step_theme()
            return self.output_formatter.format_success(
                f"Theme changed to: {theme}",
                details="Restart uDOS to apply theme changes"
            )
        except Exception as e:
            return self.output_formatter.format_error(
                "Theme setup failed",
                error_details=str(e)
            )

    def setup_viewport_only(self) -> str:
        """Run viewport configuration wizard only (v1.0.29)."""
        try:
            viewport = self._wizard_step_viewport()
            return self.output_formatter.format_success(
                f"Viewport configured: {viewport}",
                details="Changes will take effect on next restart"
            )
        except Exception as e:
            return self.output_formatter.format_error(
                "Viewport setup failed",
                error_details=str(e)
            )

    def setup_extensions_only(self) -> str:
        """Run extensions configuration wizard only (v1.0.29)."""
        try:
            extensions = self._wizard_step_extensions()
            enabled = [name.replace('enable_', '') for name, value in extensions.items() if value]

            return self.output_formatter.format_success(
                f"Extensions configured: {len(enabled)} enabled",
                details=f"Enabled: {', '.join(enabled) if enabled else 'none'}"
            )
        except Exception as e:
            return self.output_formatter.format_error(
                "Extensions setup failed",
                error_details=str(e)
            )

    def _wizard_step_user_profile(self) -> None:
        """
        User profile configuration step (v1.0.29 Smart Mode).
        Includes system location (Galaxy, Planet, City with TILE codes).
        """
        # Auto-detect timezone and location from system
        from core.utils.system_info import get_system_timezone
        detected_timezone, detected_city = get_system_timezone()

        # Get current values
        current_name = self.story_manager.get_field('USER_PROFILE.NAME', '')
        current_password = self.story_manager.get_field('USER_PROFILE.PASSWORD', '')
        current_timezone = self.story_manager.get_field('USER_PROFILE.TIMEZONE', '')

        # System location values
        current_galaxy = self.story_manager.get_field('SYSTEM.GALAXY', 'Milky Way')
        current_planet = self.story_manager.get_field('SYSTEM.PLANET', 'Earth')
        current_city = self.story_manager.get_field('SYSTEM.CITY', '')

        # Use detected values as defaults if not set
        if not current_timezone:
            current_timezone = detected_timezone
        if not current_city:
            current_city = detected_city

        # Prompt for user name (required)
        user_name = self.input_manager.prompt_user(
            message="What's your name?",
            default=current_name,
            required=True
        )
        self.story_manager.set_field('USER_PROFILE.NAME', user_name, auto_save=False)

        # Prompt for password (optional)
        password = self.input_manager.prompt_user(
            message="Enter password (leave blank for none):",
            default="",
            required=False
        )
        self.story_manager.set_field('USER_PROFILE.PASSWORD', password, auto_save=False)

        # System Location Configuration
        print("\n🌌 System Location Configuration")
        print("=" * 50)

        # Galaxy selection (from universe.json)
        galaxy = self.input_manager.prompt_user(
            message="Galaxy:",
            default=current_galaxy,
            required=False
        )
        if galaxy:
            self.story_manager.set_field('SYSTEM.GALAXY', galaxy, auto_save=False)

        # Planet selection (from universe.json Sol system)
        available_planets = ["Earth", "Mars", "Venus", "Mercury", "Jupiter", "Saturn", "Uranus", "Neptune"]
        planet = self.input_manager.prompt_choice(
            message="Select planet:",
            choices=available_planets,
            default=current_planet if current_planet in available_planets else "Earth"
        )
        self.story_manager.set_field('SYSTEM.PLANET', planet, auto_save=False)

        # City selection (from cities.json with TILE codes)
        city_data = self._load_city_data()
        if city_data:
            city_choices = [f"{city['name']}, {city['country']} ({city['grid_cell']})"
                          for city in city_data]
            city_choice = self.input_manager.prompt_choice(
                message="Select city:",
                choices=city_choices,
                default=city_choices[0] if city_choices else current_city
            )
            # Parse selection
            selected_city = city_choice.split(',')[0]
            selected_grid = city_choice.split('(')[1].rstrip(')')

            # Find full city data
            for city in city_data:
                if city['name'] == selected_city:
                    self.story_manager.set_field('SYSTEM.CITY', city['name'], auto_save=False)
                    self.story_manager.set_field('SYSTEM.CITY_GRID', city['grid_cell'], auto_save=False)
                    self.story_manager.set_field('SYSTEM.CITY_LAYER', 100, auto_save=False)  # World layer
                    self.story_manager.set_field('SYSTEM.TIMEZONE', city.get('tzone', detected_timezone), auto_save=False)
                    # Also update USER_PROFILE for backward compatibility
                    self.story_manager.set_field('USER_PROFILE.LOCATION', city['name'], auto_save=False)
                    break
        else:
            # Fallback to manual entry
            city = self.input_manager.prompt_user(
                message="City:",
                default=current_city or detected_city,
                required=False
            )
            if city:
                self.story_manager.set_field('SYSTEM.CITY', city, auto_save=False)
                self.story_manager.set_field('USER_PROFILE.LOCATION', city, auto_save=False)

        # Timezone (auto-detected, modifiable)
        print(f"\nℹ️  Detected timezone: {detected_timezone}")
        timezone = self.input_manager.prompt_user(
            message="Timezone:",
            default=current_timezone,
            required=False
        )
        if timezone:
            self.story_manager.set_field('USER_PROFILE.TIMEZONE', timezone, auto_save=False)
        else:
            self.story_manager.set_field('USER_PROFILE.TIMEZONE', current_timezone, auto_save=False)

        # Save all profile changes
        self.story_manager.save()

    def _load_city_data(self) -> List[Dict]:
        """Load city data from cities.json."""
        try:
            cities_path = Path('core/data/geography/cities.json')
            if cities_path.exists():
                with open(cities_path, 'r') as f:
                    data = json.load(f)
                    return data.get('cities', [])
        except Exception as e:
            print(f"⚠️  Could not load cities.json: {e}")
        return []

    def _wizard_step_theme(self) -> str:
        """Theme selection step (v1.0.29 Smart Mode)."""
        current_theme = self.story_manager.get_field('system_settings.interface.theme', 'dungeon')

        # Show available themes
        if not self.available_themes:
            return current_theme

        theme = self.input_manager.prompt_choice(
            message="Select a theme:",
            choices=self.available_themes,
            default=current_theme if current_theme in self.available_themes else self.available_themes[0]
        )

        self.story_manager.set_field('system_settings.interface.theme', theme, auto_save=True)
        return theme

    def _wizard_step_viewport(self) -> str:
        """Viewport configuration step (v1.0.29 Smart Mode)."""
        # Offer preset choices
        choices = ["Auto-detect (recommended)"]
        for preset in self.available_viewports:
            choices.append(f"{preset['name']} - {preset['size']}")
        choices.append("Custom size")

        choice = self.input_manager.prompt_choice(
            message="Select viewport configuration:",
            choices=choices,
            default="Auto-detect (recommended)"
        )

        if choice == "Auto-detect (recommended)":
            return "auto"
        elif choice == "Custom size":
            width = self.input_manager.prompt_user(
                message="Enter width (cells, 10-1000):",
                default="80",
                required=True
            )
            height = self.input_manager.prompt_user(
                message="Enter height (cells, 5-1000):",
                default="24",
                required=True
            )
            return f"{width}×{height}"
        else:
            # Parse preset choice
            preset_name = choice.split(" - ")[0]
            for preset in self.available_viewports:
                if preset['name'] == preset_name:
                    return preset['size']
            return "auto"

    def _wizard_step_extensions(self) -> Dict[str, bool]:
        """Extensions configuration step (v1.0.29 Smart Mode)."""
        extensions = {}

        # Web Interface
        enable_web = self.input_manager.prompt_confirm(
            message="Enable Web Dashboard extension?",
            default=True
        )
        extensions['enable_web'] = enable_web

        # Teletext
        enable_teletext = self.input_manager.prompt_confirm(
            message="Enable Teletext Renderer extension?",
            default=True
        )
        extensions['enable_teletext'] = enable_teletext

        # Dashboard Builder
        enable_dashboard = self.input_manager.prompt_confirm(
            message="Enable Dashboard Builder extension?",
            default=True
        )
        extensions['enable_dashboard'] = enable_dashboard

        return extensions

    def _format_completion_summary(self) -> str:
        """Format completion summary with current config (v1.0.29)."""
        user_name = self.story_manager.get_field('USER_PROFILE.NAME', 'Not set')
        password = self.story_manager.get_field('USER_PROFILE.PASSWORD', '')
        theme = self.story_manager.get_field('system_settings.interface.theme', 'dungeon')
        timezone = self.story_manager.get_field('USER_PROFILE.TIMEZONE', 'UTC')

        # System location fields
        galaxy = self.story_manager.get_field('SYSTEM.GALAXY', 'Not set')
        planet = self.story_manager.get_field('SYSTEM.PLANET', 'Not set')
        city = self.story_manager.get_field('SYSTEM.CITY', 'Not set')
        city_grid = self.story_manager.get_field('SYSTEM.CITY_GRID', 'N/A')
        city_layer = self.story_manager.get_field('SYSTEM.CITY_LAYER', 100)

        # Format full TILE code with layer
        full_tile = f"{city_grid}-{city_layer}" if city_grid != 'N/A' else 'N/A'

        password_display = '●●●●●●' if password else 'Not set'

        summary_data = {
            'Username': user_name,
            'Password': password_display,
            'Galaxy': galaxy,
            'Planet': planet,
            'City': f"{city} (TILE: {full_tile})",
            'Timezone': timezone,
            'Theme': theme
        }

        return self.output_formatter.format_panel(
            "✅ Setup Complete!",
            self.output_formatter.format_key_value(summary_data) +
            "\n\n💡 You can reconfigure anytime with: SETUP\n" +
            "💡 Change individual settings with: CONFIG"
        )

    def _show_summary(self, config: Dict[str, Any]) -> None:
        """Display configuration summary."""
        print(self._format_summary(config))

    def _format_welcome(self) -> str:
        """Format welcome screen."""
        welcome = "╔" + "═"*78 + "╗\n"
        welcome += "║" + " "*24 + "🚀 uDOS Setup Wizard" + " "*34 + "║\n"
        welcome += "╠" + "═"*78 + "╣\n"
        welcome += "║  Welcome to uDOS! Let's configure your system.".ljust(79) + "║\n"
        welcome += "║".ljust(79) + "║\n"
        welcome += "║  This wizard will guide you through:".ljust(79) + "║\n"
        welcome += "║    1. Theme Selection".ljust(79) + "║\n"
        welcome += "║    2. Viewport Configuration".ljust(79) + "║\n"
        welcome += "║    3. Extension Setup".ljust(79) + "║\n"
        welcome += "║    4. Advanced Settings".ljust(79) + "║\n"
        welcome += "║".ljust(79) + "║\n"
        welcome += "║  You can skip this with 'SETUP QUICK' for defaults.".ljust(79) + "║\n"
        welcome += "╚" + "═"*78 + "╝\n"
        return welcome

    def _format_summary(self, config: Dict[str, Any]) -> str:
        """Format configuration summary."""
        summary = "╔" + "═"*78 + "╗\n"
        summary += "║  📋 Configuration Summary".ljust(79) + "║\n"
        summary += "╠" + "═"*78 + "╣\n"
        summary += f"║  Theme: {config.get('theme', 'N/A')}".ljust(79) + "║\n"
        summary += f"║  Viewport: {config.get('viewport', 'N/A')}".ljust(79) + "║\n"

        extensions = config.get('extensions', {})
        ext_count = sum(1 for v in extensions.values() if v)
        summary += f"║  Extensions: {ext_count} enabled".ljust(79) + "║\n"

        summary += "║".ljust(79) + "║\n"
        summary += "║  ✅ Configuration complete!".ljust(79) + "║\n"
        summary += "╚" + "═"*78 + "╝\n"
        return summary

    def format_theme_options(self) -> str:
        """Format theme selection options."""
        output = "╔" + "═"*78 + "╗\n"
        output += "║  🎨 Available Themes".ljust(79) + "║\n"
        output += "╠" + "═"*78 + "╣\n"

        for i, theme in enumerate(self.available_themes, 1):
            output += f"║  {i}. {theme.capitalize()}".ljust(79) + "║\n"

        output += "║".ljust(79) + "║\n"
        output += "║  Use: SETUP THEME <name>".ljust(79) + "║\n"
        output += "╚" + "═"*78 + "╝\n"
        return output

    def format_viewport_options(self) -> str:
        """Format viewport preset options."""
        output = "╔" + "═"*78 + "╗\n"
        output += "║  📺 Viewport Presets".ljust(79) + "║\n"
        output += "╠" + "═"*78 + "╣\n"

        for preset in self.available_viewports:
            name = preset['name']
            size = preset['size']
            tier = preset['tier']
            output += f"║  {name:<12} - {size:<10} (Tier {tier})".ljust(79) + "║\n"

        output += "║".ljust(79) + "║\n"
        output += "║  Current: Auto-detect (recommended)".ljust(79) + "║\n"
        output += "║  Use: SETUP VIEWPORT <preset>".ljust(79) + "║\n"
        output += "╚" + "═"*78 + "╝\n"
        return output

    def format_extensions_options(self) -> str:
        """Format extension options."""
        output = "╔" + "═"*78 + "╗\n"
        output += "║  🔌 Available Extensions".ljust(79) + "║\n"
        output += "╠" + "═"*78 + "╣\n"
        output += "║  • Web Interface (Dashboard)".ljust(79) + "║\n"
        output += "║  • Teletext Renderer".ljust(79) + "║\n"
        output += "║  • Font Editor".ljust(79) + "║\n"
        output += "║  • System Desktop".ljust(79) + "║\n"
        output += "║".ljust(79) + "║\n"
        output += "║  Use: SETUP EXTENSIONS to configure".ljust(79) + "║\n"
        output += "╚" + "═"*78 + "╝\n"
        return output

    def format_help(self) -> str:
        """Format SETUP command help."""
        help_text = "╔" + "═"*78 + "╗\n"
        help_text += "║  📖 SETUP - Interactive Configuration Wizard".ljust(79) + "║\n"
        help_text += "╠" + "═"*78 + "╣\n"
        help_text += "║  Available Commands:".ljust(79) + "║\n"
        help_text += "║".ljust(79) + "║\n"
        help_text += "║  SETUP              - Run full interactive wizard".ljust(79) + "║\n"
        help_text += "║  SETUP WIZARD       - Same as SETUP".ljust(79) + "║\n"
        help_text += "║  SETUP QUICK        - Quick setup with defaults".ljust(79) + "║\n"
        help_text += "║  SETUP THEME        - Theme selection only".ljust(79) + "║\n"
        help_text += "║  SETUP VIEWPORT     - Viewport configuration only".ljust(79) + "║\n"
        help_text += "║  SETUP EXTENSIONS   - Extension management only".ljust(79) + "║\n"
        help_text += "║".ljust(79) + "║\n"
        help_text += "║  Examples:".ljust(79) + "║\n"
        help_text += "║    SETUP            → Full interactive wizard".ljust(79) + "║\n"
        help_text += "║    SETUP QUICK      → Use sensible defaults".ljust(79) + "║\n"
        help_text += "║    SETUP THEME      → Change theme only".ljust(79) + "║\n"
        help_text += "╚" + "═"*78 + "╝\n"
        return help_text

    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate configuration dictionary.

        Args:
            config: Configuration to validate

        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []

        # Validate theme
        if 'theme' in config:
            if config['theme'] not in self.available_themes:
                errors.append(f"Invalid theme: {config['theme']}")

        # Validate viewport
        if 'viewport' in config:
            valid_viewports = ['auto'] + [p['name'].lower() for p in self.available_viewports]
            if config['viewport'].lower() not in valid_viewports:
                errors.append(f"Invalid viewport: {config['viewport']}")

        return (len(errors) == 0, errors)

    def export_config(self, config: Dict[str, Any]) -> str:
        """Export configuration to JSON string."""
        return json.dumps(config, indent=2)

    def import_config(self, config_json: str) -> Dict[str, Any]:
        """Import configuration from JSON string."""
        try:
            return json.loads(config_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON configuration: {e}")


# Standalone test function
def test_setup_wizard():
    """Test SetupWizard functionality."""
    print("Testing SetupWizard...")

    wizard = SetupWizard()

    # Test theme options
    themes = wizard.format_theme_options()
    print(f"✅ Theme options: {len(themes)} characters")

    # Test viewport options
    viewports = wizard.format_viewport_options()
    print(f"✅ Viewport options: {len(viewports)} characters")

    # Test quick setup
    quick_config = wizard.run_quick_setup()
    print(f"✅ Quick setup: {len(quick_config)} settings")
    print(f"   Theme: {quick_config['theme']}")
    print(f"   Viewport: {quick_config['viewport']}")

    # Test validation
    is_valid, errors = wizard.validate_config(quick_config)
    print(f"✅ Validation: {is_valid}, {len(errors)} errors")

    # Test help
    help_text = wizard.format_help()
    print(f"✅ Help text: {len(help_text)} characters")

    print("\n✅ SetupWizard tests passed")


if __name__ == "__main__":
    test_setup_wizard()
