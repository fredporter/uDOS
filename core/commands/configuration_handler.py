"""
uDOS v1.5.0 - Configuration Handler

Handles configuration management operations:
- Settings display and modification
- Theme switching and configuration
- Configuration file management
- User preferences
- Advanced theme management (v1.0.13+)
- Unified configuration via ConfigManager (v1.5.0+)
"""

import json
import shutil
from pathlib import Path
from .base_handler import BaseCommandHandler
from core.services.theme.theme_manager import ThemeManager
from core.services.theme.theme_builder import ThemeBuilder
from core.uDOS_main import get_config  # v1.5.0 Unified configuration
from core.utils.paths import PATHS


class ConfigurationHandler(BaseCommandHandler):
    """Handles configuration and settings management operations."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._theme_manager = None
        self._theme_builder = None

    @property
    def theme_manager(self):
        """Lazy-load ThemeManager service."""
        if self._theme_manager is None:
            self._theme_manager = ThemeManager()
        return self._theme_manager

    @property
    def theme_builder(self):
        """Lazy-load ThemeBuilder service."""
        if self._theme_builder is None:
            self._theme_builder = ThemeBuilder(theme_manager=self.theme_manager)
        return self._theme_builder

    def handle_setup(self, params, grid, parser):
        """
        Interactive story-style setup wizard.

        Usage:
            SETUP                 - Run interactive setup wizard
            SETUP --show          - Display all current settings
            SETUP <key>           - Show specific setting
            SETUP <key> <value>   - Set setting value

        The interactive wizard will guide you through:
            - User profile (name, location, timezone)
            - System preferences (theme, editor, offline mode)
            - Optional world map location
        """
        # Check for --show flag or no params runs wizard
        if not params:
            return self._run_interactive_setup()
        elif params[0] == '--show' or params[0].upper() == 'SHOW':
            return self._show_all_settings()
        elif len(params) == 1:
            return self._show_setting(params[0])
        elif len(params) == 2:
            return self._set_setting(params[0], params[1])
        else:
            return ("❌ Invalid setup command\n\n"
                   "Usage:\n"
                   "  SETUP                  - Run interactive setup wizard\n"
                   "  SETUP --show           - Display all settings\n"
                   "  SETUP <key>           - Show specific setting\n"
                   "  SETUP <key> <value>   - Set setting value")

    def _run_interactive_setup(self):
        """Run interactive story-style setup wizard."""
        try:
            from core.config import Config
            config = Config()

            output = []
            output.append("")
            output.append("╔══════════════════════════════════════════════════════════╗")
            output.append("║     🎮 Welcome to uDOS Interactive Setup Wizard!        ║")
            output.append("╚══════════════════════════════════════════════════════════╝")
            output.append("")
            output.append("This wizard will help you configure your uDOS environment.")
            output.append("")

            # Get current values
            current_username = config.get_user('USER_PROFILE.NAME', '')
            current_location = config.get_user('USER_PROFILE.LOCATION', '')
            current_timezone = config.get_user('USER_PROFILE.TIMEZONE', 'UTC')
            current_theme = config.get_env('THEME', 'dungeon')

            changes_made = False

            # Username
            output.append("┌─────────────────────────────────────────────────────────┐")
            output.append("│ Step 1: User Profile                                    │")
            output.append("└─────────────────────────────────────────────────────────┘")
            output.append("")

            if not current_username or current_username == 'user':
                if self.input_manager:
                    username = self.input_manager.prompt_user(
                        message="What should we call you?",
                        default="Explorer",
                        required=True
                    )
                    config.set_user('USER_PROFILE.NAME', username)
                    output.append(f"✅ Username set to: {username}")
                    changes_made = True
                else:
                    output.append(f"Current username: {current_username}")
                    output.append("💡 To change: SETUP username <new_name>")
            else:
                output.append(f"✅ Username: {current_username}")

            output.append("")

            # Location & Timezone
            output.append("┌─────────────────────────────────────────────────────────┐")
            output.append("│ Step 2: Location & Time                                 │")
            output.append("└─────────────────────────────────────────────────────────┘")
            output.append("")

            # Auto-detect timezone
            try:
                from core.utils.system_info import get_system_timezone
                detected_tz, detected_city = get_system_timezone()
                output.append(f"📍 Detected: {detected_city} ({detected_tz})")

                if not current_location or current_location == 'Unknown':
                    if self.input_manager:
                        # Load cities from cities.json
                        cities_data = self._load_cities_list()

                        if cities_data:
                            # Offer to use detected or select from list
                            use_detected = self.input_manager.prompt_choice(
                                message="Use detected location?",
                                choices=["Yes", "No, select from list"],
                                default="Yes"
                            )

                            if use_detected == "Yes":
                                # Find full city info from cities.json
                                city_info = next((c for c in cities_data if c['name'] == detected_city), None)
                                if city_info:
                                    config.set_user('USER_PROFILE.LOCATION', city_info['name'])
                                    config.set_user('USER_PROFILE.TIMEZONE', city_info['timezone']['name'])
                                else:
                                    config.set_user('USER_PROFILE.LOCATION', detected_city)
                                    config.set_user('USER_PROFILE.TIMEZONE', detected_tz)
                                output.append(f"✅ Location set to: {detected_city}")
                                output.append(f"✅ Timezone set to: {detected_tz}")
                                changes_made = True
                            else:
                                # Show cities selection
                                city_names = [f"{c['name']}, {c['country']}" for c in cities_data]
                                selected = self.input_manager.prompt_choice(
                                    message="Select your location:",
                                    choices=city_names[:20],  # Show first 20 cities
                                    default=city_names[0] if city_names else ""
                                )

                                if selected:
                                    # Extract city name
                                    city_name = selected.split(',')[0].strip()
                                    city_info = next((c for c in cities_data if c['name'] == city_name), None)

                                    if city_info:
                                        config.set_user('USER_PROFILE.LOCATION', city_info['name'])
                                        config.set_user('USER_PROFILE.TIMEZONE', city_info['timezone']['name'])
                                        output.append(f"✅ Location set to: {city_info['name']}, {city_info['country']}")
                                        output.append(f"✅ Timezone set to: {city_info['timezone']['name']}")
                                        changes_made = True
                        else:
                            # Fallback to manual entry if cities.json not available
                            use_detected = self.input_manager.prompt_choice(
                                message="Use detected location?",
                                choices=["Yes", "No, enter manually"],
                                default="Yes"
                            )

                            if use_detected == "Yes":
                                config.set_user('USER_PROFILE.LOCATION', detected_city)
                                config.set_user('USER_PROFILE.TIMEZONE', detected_tz)
                                output.append(f"✅ Location set to: {detected_city}")
                                output.append(f"✅ Timezone set to: {detected_tz}")
                                changes_made = True
                            else:
                                location = self.input_manager.prompt_user(
                                    message="Enter your location (city, country):",
                                    default=detected_city,
                                    required=False
                                )
                                if location:
                                    config.set_user('USER_PROFILE.LOCATION', location)
                                    config.set_user('USER_PROFILE.TIMEZONE', detected_tz)
                                    output.append(f"✅ Location set to: {location}")
                                    changes_made = True
                    else:
                        output.append(f"Current location: {current_location}")
                        output.append("💡 To change: SETUP location <city>")
                else:
                    output.append(f"✅ Location: {current_location}")
                    output.append(f"✅ Timezone: {current_timezone}")
            except:
                output.append(f"Location: {current_location}")
                output.append(f"Timezone: {current_timezone}")

            output.append("")

            # Theme selection
            output.append("┌─────────────────────────────────────────────────────────┐")
            output.append("│ Step 3: Visual Theme                                    │")
            output.append("└─────────────────────────────────────────────────────────┘")
            output.append("")
            output.append(f"Current theme: {current_theme}")
            output.append("")
            output.append("💡 Available themes: dungeon, cyberpunk, foundation")
            output.append("💡 To change theme: THEME <name>")
            output.append("")

            # Summary
            output.append("")
            output.append("╔══════════════════════════════════════════════════════════╗")
            if changes_made:
                output.append("║  ✅ Setup Complete - Configuration Saved!               ║")
            else:
                output.append("║  ✅ Setup Complete - Configuration Verified!            ║")
            output.append("╚══════════════════════════════════════════════════════════╝")
            output.append("")
            output.append("📝 Quick reference:")
            output.append("   • View all settings: SETUP --show")
            output.append("   • Interactive config: CONFIG")
            output.append("   • Change theme: THEME <name>")
            output.append("   • Edit settings: SETUP <key> <value>")
            output.append("")

            return "\n".join(output)

        except Exception as e:
            return f"❌ Setup wizard error: {e}\n\n💡 Try: SETUP --show to view current settings"

    def _show_all_settings(self):
        """Display all current settings organized by category."""
        output = []
        output.append("⚙️ uDOS SYSTEM SETTINGS")
        output.append("=" * 60)

        # Get user data from ConfigManager (v2.0)
        config = get_config()

        # System Location
        output.append("")
        output.append("🌌 SYSTEM LOCATION:")
        output.append("-" * 40)
        # Read from USER_PROFILE and LOCATION_DATA (authoritative as of v1.2.21)
        galaxy = config.get_user('USER_PROFILE.GALAXY', 'Milky Way')
        planet = config.get_user('USER_PROFILE.PLANET', 'Earth')
        city = config.get_user('USER_PROFILE.LOCATION', 'Not set')  # City name
        tile_code = config.get_user('USER_PROFILE.TILE', 'N/A')  # TILE code
        full_tile = tile_code if tile_code != 'N/A' else 'N/A'

        output.append(f"  Galaxy: {galaxy}")
        output.append(f"  Planet: {planet}")
        output.append(f"  City: {city}")
        output.append(f"  TILE Code: {full_tile}")

        # User Profile
        output.append("")
        output.append("👤 USER PROFILE:")
        output.append("-" * 40)
        user_name = config.get_user('USER_PROFILE.NAME', 'Not set')
        location = config.get_user('USER_PROFILE.LOCATION', 'Not set')
        timezone = config.get_user('USER_PROFILE.TIMEZONE', 'UTC')
        password = config.get_user('USER_PROFILE.PASSWORD', '')
        password_display = '●●●●●●' if password else 'Not set'

        output.append(f"  Username: {user_name}")
        output.append(f"  Password: {password_display}")
        output.append(f"  Location: {location}")
        output.append(f"  Timezone: {timezone}")

        # Theme & Display
        output.append("")
        output.append("🎨 THEME & DISPLAY:")
        output.append("-" * 40)
        theme_name = config.get_env('THEME', 'dungeon')
        color_palette = config.get_user('system_settings.interface.color_palette', 'polaroid')

        output.append(f"  Theme: {theme_name}")
        output.append(f"  Color Palette: {color_palette}")

        if self.viewport:
            output.append(f"  Viewport: {self.viewport.width}×{self.viewport.height}")
            output.append(f"  Device: {getattr(self.viewport, 'device_type', 'TERMINAL')}")

        # Connection & Services
        output.append("")
        output.append("🌐 CONNECTION & SERVICES:")
        output.append("-" * 40)

        # Handle connection object safely (might be boolean or ConnectionMonitor)
        if self.connection and hasattr(self.connection, 'get_mode'):
            connection_mode = self.connection.get_mode()
            internet_available = self.connection.is_online()
        else:
            connection_mode = 'OFFLINE'
            internet_available = False

        output.append(f"  Connection: {connection_mode}")
        output.append(f"  Internet: {'✓ Available' if internet_available else '✗ Offline'}")

        # Check for cloud extension API
        try:
            from extensions.cloud.poke_commands import get_tunnel_status
            tunnel_status = get_tunnel_status()
            if tunnel_status:
                output.append(f"  Cloud Tunnel: {tunnel_status}")
        except:
            pass

        # Development & Tools
        output.append("")
        output.append("🔧 DEVELOPMENT & TOOLS:")
        output.append("-" * 40)
        debug_mode = getattr(self.logger, 'debug_enabled', False) if self.logger else False
        dev_mode = config.get('DEV_MODE', False)
        cli_editor = config.get_env('CLI_EDITOR', 'micro')

        output.append(f"  Debug Mode: {'✓ Enabled' if debug_mode else '✗ Disabled'}")
        output.append(f"  Dev Mode: {'✓ Enabled' if dev_mode else '✗ Disabled'}")
        output.append(f"  CLI Editor: {cli_editor} (fallback: nano)")
        output.append(f"  Auto-save: ✓ Enabled")

        output.append("")
        output.append("=" * 60)
        output.append("💡 Use: SETUP <key> <value> to modify settings")
        output.append("💡 Use: CONFIG for interactive menu")
        output.append("💡 Use: WIZARD to reconfigure system")

        return "\n".join(output)

    def _show_setting(self, key):
        """Show a specific setting value."""
        key_upper = key.upper()

        # Special case: SHOW (from default params) means show all settings
        if key_upper == 'SHOW':
            return self._show_all_settings()

        # Special case: EDIT means launch interactive editor
        elif key_upper == 'EDIT':
            return self.handle_config([])  # Launch interactive CONFIG menu

        # Special case: RESET means reset to defaults
        elif key_upper == 'RESET':
            return self._reset_configs()

        # Check different setting categories
        if key_upper == 'THEME':
            if self.theme:
                return f"Current theme: {getattr(self.theme, 'name', 'Default')}"
            else:
                return "Theme not loaded"

        elif key_upper in ['GRID', 'VIEWPORT']:
            if self.viewport:
                return (f"Grid settings:\n"
                       f"  Terminal: {self.viewport.width}×{self.viewport.height}\n"
                       f"  Grid: {getattr(self.viewport, 'grid_width', '?')}×{getattr(self.viewport, 'grid_height', '?')}\n"
                       f"  Device: {getattr(self.viewport, 'device_type', 'UNKNOWN')}")
            else:
                return "Grid not initialized"

        elif key_upper == 'USER':
            # Get user data from ConfigManager (v1.5.0)
            config = get_config()
            user_name = config.get_user('USER_PROFILE.NAME', 'Not set')
            location = config.get_user('USER_PROFILE.LOCATION', 'Not set')
            timezone = config.get_user('USER_PROFILE.TIMEZONE', 'UTC')
            password = config.get_user('USER_PROFILE.PASSWORD', '')

            password_display = '●●●●●●' if password else 'Not set'

            return (f"User settings:\n"
                   f"  Username: {user_name}\n"
                   f"  Password: {password_display}\n"
                   f"  Location: {location}\n"
                   f"  Timezone: {timezone}")

        elif key_upper == 'DEBUG':
            debug_enabled = getattr(self.logger, 'debug_enabled', False) if self.logger else False
            return f"Debug mode: {'Enabled' if debug_enabled else 'Disabled'}"

        else:
            return f"❌ Unknown setting: {key}\n\nAvailable settings: THEME, GRID, USER, DEBUG"

    def _set_setting(self, key, value):
        """Set a specific setting value."""
        key_upper = key.upper()
        value_upper = value.upper()

        if key_upper == 'THEME':
            return self._set_theme(value)

        elif key_upper == 'DEBUG':
            if value_upper in ['TRUE', 'ON', '1', 'ENABLED']:
                if self.logger:
                    self.logger.debug_enabled = True
                    return "✅ Debug mode enabled"
                else:
                    return "❌ Logger not available"
            elif value_upper in ['FALSE', 'OFF', '0', 'DISABLED']:
                if self.logger:
                    self.logger.debug_enabled = False
                    return "✅ Debug mode disabled"
                else:
                    return "❌ Logger not available"
            else:
                return "❌ Invalid debug value. Use: TRUE/FALSE or ON/OFF"

        else:
            return f"❌ Setting '{key}' cannot be modified directly\n\nModifiable settings: THEME, DEBUG"

    def _set_theme(self, theme_name):
        """Set the current theme."""
        try:
            # Load theme data
            theme_file = Path(f'core/data/themes/{theme_name.lower()}.json')
            if not theme_file.exists():
                return f"❌ Theme '{theme_name}' not found\n\nUse: THEME LIST to see available themes"

            with open(theme_file, 'r') as f:
                theme_data = json.load(f)

            # Apply theme through theme manager
            if self.theme and hasattr(self.theme, 'load_theme'):
                self.theme.load_theme(theme_name.lower())
                return f"✅ Theme changed to '{theme_name}'"
            else:
                return "❌ Theme manager not available"

        except Exception as e:
            return f"❌ Failed to set theme: {str(e)}"

    def handle_theme(self, params, grid, parser):
        """
        Manage color themes (Enhanced in v1.0.13).

        Usage:
            THEME                    - Show current theme
            THEME LIST               - List all available themes
            THEME LIST DETAILED      - List themes with full details
            THEME <name>             - Switch to theme
            THEME PREVIEW <name>     - Preview theme without applying
            THEME CREATE             - Create new theme (interactive wizard)
            THEME CREATE INTERACTIVE - Create theme with step-by-step wizard
            THEME CREATE FROM <template> - Create from template
            THEME COPY <source> <new_name> - Copy existing theme
            THEME EXPORT <name> [path] - Export theme to .udostheme file
            THEME IMPORT <path> [name] - Import theme from .udostheme file
            THEME VALIDATE <name>    - Validate theme structure
            THEME DETAILS <name>     - Show detailed theme information
            THEME STATS              - Show theme statistics
            THEME TEMPLATES          - List available templates
            THEME BACKUP             - Backup current theme
            THEME RESTORE            - Restore from backup

        Available themes are in data/themes/ directory.
        """
        if not params:
            return self._show_current_theme()

        command = params[0].upper()

        # New v1.0.13 commands
        if command == 'PREVIEW':
            if len(params) < 2:
                return "❌ Usage: THEME PREVIEW <name>"
            return self._preview_theme(params[1])

        elif command == 'CREATE':
            if len(params) == 1:
                return self._create_theme_interactive()
            elif params[1].upper() == 'INTERACTIVE':
                return self._create_theme_interactive()
            elif params[1].upper() == 'FROM':
                if len(params) < 3:
                    return "❌ Usage: THEME CREATE FROM <template>"
                return self._create_theme_from_template(params[2])
            else:
                return "❌ Unknown CREATE option. Use: INTERACTIVE or FROM <template>"

        elif command == 'COPY':
            if len(params) < 3:
                return "❌ Usage: THEME COPY <source> <new_name>"
            return self._copy_theme(params[1], params[2])

        elif command == 'EXPORT':
            if len(params) < 2:
                return "❌ Usage: THEME EXPORT <name> [path]"
            output_path = params[2] if len(params) > 2 else f"{params[1]}.udostheme"
            return self._export_theme(params[1], output_path)

        elif command == 'IMPORT':
            if len(params) < 2:
                return "❌ Usage: THEME IMPORT <path> [name]"
            theme_name = params[2] if len(params) > 2 else None
            return self._import_theme(params[1], theme_name)

        elif command == 'VALIDATE':
            if len(params) < 2:
                return "❌ Usage: THEME VALIDATE <name>"
            return self._validate_theme(params[1])

        elif command == 'DETAILS':
            if len(params) < 2:
                return "❌ Usage: THEME DETAILS <name>"
            return self._show_theme_details(params[1])

        elif command == 'STATS':
            return self._show_theme_stats()

        elif command == 'TEMPLATES':
            return self._list_templates()

        # Existing commands
        elif command == 'LIST':
            detailed = len(params) > 1 and params[1].upper() == 'DETAILED'
            return self._list_themes(detailed)
        elif command == 'BACKUP':
            return self._backup_theme()
        elif command == 'RESTORE':
            return self._restore_theme()
        else:
            # Assume it's a theme name
            return self._switch_theme(params[0])

    def _show_current_theme(self):
        """Show current theme information."""
        if not self.theme:
            return "❌ Theme system not initialized"

        try:
            theme_name = getattr(self.theme, 'name', 'Unknown')
            theme_version = getattr(self.theme, 'version', 'Unknown')

            output = []
            output.append(f"🎨 CURRENT THEME: {theme_name.upper()}")
            output.append("=" * 50)
            output.append(f"Name: {theme_name}")
            output.append(f"Version: {theme_version}")

            # Show color preview if available
            if hasattr(self.theme, 'colors'):
                output.append("")
                output.append("Color preview:")
                # Add basic color samples
                colors = ['red', 'green', 'yellow', 'blue', 'purple', 'cyan']
                preview_line = ""
                for color in colors:
                    if hasattr(self.theme, color):
                        ansi_code = getattr(self.theme, color, '')
                        if ansi_code:
                            preview_line += f"{ansi_code}██\033[0m "
                if preview_line:
                    output.append(f"  {preview_line}")

            output.append("")
            output.append("💡 Use: THEME LIST to see all available themes")
            output.append("💡 Use: THEME <name> to switch themes")

            return "\n".join(output)

        except Exception as e:
            return f"❌ Failed to show theme info: {str(e)}"

    def _list_themes(self, detailed=False):
        """List all available themes (enhanced in v1.0.13)."""
        return self.theme_manager.list_json_themes(detailed=detailed)

    def _switch_theme(self, theme_name):
        """Switch to a different theme."""
        try:
            theme_file = Path(f'core/data/themes/{theme_name.lower()}.json')
            if not theme_file.exists():
                return f"❌ Theme '{theme_name}' not found\n\nUse: THEME LIST to see available themes"

            # Load theme data to validate
            with open(theme_file, 'r') as f:
                theme_data = json.load(f)

            # Apply theme
            if self.theme and hasattr(self.theme, 'load_theme'):
                self.theme.load_theme(theme_name.lower())
                return f"✅ Switched to theme: {theme_name}"
            else:
                return "❌ Theme manager not available"

        except Exception as e:
            return f"❌ Failed to switch theme: {str(e)}"

    # ==================== New v1.0.13 Theme Methods ====================

    def _preview_theme(self, theme_name):
        """Preview a theme without applying it."""
        try:
            return self.theme_manager.preview_json_theme(theme_name)
        except Exception as e:
            return f"❌ Failed to preview theme: {str(e)}"

    def _create_theme_interactive(self):
        """Create theme using interactive wizard."""
        try:
            print("\n🎨 Starting interactive theme creation wizard...")
            print("This will guide you through creating a custom theme.\n")

            theme_data = self.theme_builder.create_theme_interactive()

            if not theme_data:
                return "❌ Theme creation cancelled"

            # Validate and fix
            fixed_data, warnings = self.theme_builder.validate_and_fix(theme_data)

            if warnings:
                print("\n⚠️  Auto-fixed issues:")
                for warning in warnings:
                    print(f"  - {warning}")

            # Save theme
            theme_name = fixed_data.get("THEME_NAME", "custom_theme").lower()
            if self.theme_builder.save_theme(fixed_data, theme_name):
                return f"\n✅ Theme '{theme_name}' created successfully!\n" \
                       f"💡 Use: THEME PREVIEW {theme_name} to preview\n" \
                       f"💡 Use: THEME {theme_name} to activate"
            else:
                return "❌ Failed to save theme"

        except Exception as e:
            return f"❌ Failed to create theme: {str(e)}"

    def _create_theme_from_template(self, template_name):
        """Create theme from a template."""
        try:
            print(f"\n🎨 Creating theme from template: {template_name}\n")

            # Get basic customizations
            theme_name = input("Theme Name (e.g., MY_THEME): ").strip().upper()
            if not theme_name:
                return "❌ Theme name is required"

            display_name = input("Display Name: ").strip()
            description = input("Description: ").strip()

            customizations = {
                "THEME_NAME": theme_name,
                "NAME": display_name or theme_name.title(),
                "DESCRIPTION": description or f"Theme based on {template_name}",
            }

            # Create from template
            theme_data = self.theme_builder.create_from_template(template_name, customizations)

            # Validate and fix
            fixed_data, warnings = self.theme_builder.validate_and_fix(theme_data)

            # Save theme
            if self.theme_builder.save_theme(fixed_data, theme_name.lower()):
                return f"\n✅ Theme '{theme_name}' created from template!\n" \
                       f"💡 Use: THEME PREVIEW {theme_name.lower()} to preview\n" \
                       f"💡 Use: THEME {theme_name.lower()} to activate"
            else:
                return "❌ Failed to save theme"

        except Exception as e:
            return f"❌ Failed to create theme from template: {str(e)}"

    def _copy_theme(self, source_name, new_name):
        """Copy an existing theme."""
        try:
            print(f"\n🎨 Copying theme '{source_name}' to '{new_name}'...\n")

            # Optional modifications
            modify = input("Apply modifications? (y/n): ").strip().lower()
            modifications = None

            if modify == 'y':
                print("\nEnter modifications (press Enter to skip):")
                description = input("  New description: ").strip()
                icon = input("  New icon: ").strip()

                modifications = {}
                if description:
                    modifications["DESCRIPTION"] = description
                if icon:
                    modifications["ICON"] = icon

            # Copy theme
            new_theme = self.theme_builder.copy_theme(source_name, new_name, modifications)

            if not new_theme:
                return f"❌ Failed to copy theme '{source_name}'"

            # Save copied theme
            if self.theme_builder.save_theme(new_theme, new_name.lower()):
                return f"\n✅ Theme copied successfully as '{new_name}'!\n" \
                       f"💡 Use: THEME PREVIEW {new_name.lower()} to preview\n" \
                       f"💡 Use: THEME {new_name.lower()} to activate"
            else:
                return "❌ Failed to save copied theme"

        except Exception as e:
            return f"❌ Failed to copy theme: {str(e)}"

    def _export_theme(self, theme_name, output_path):
        """Export theme to .udostheme file."""
        try:
            if self.theme_manager.export_json_theme(theme_name, output_path):
                return f"✅ Theme '{theme_name}' exported successfully"
            else:
                return f"❌ Failed to export theme '{theme_name}'"
        except Exception as e:
            return f"❌ Export failed: {str(e)}"

    def _import_theme(self, import_path, theme_name):
        """Import theme from .udostheme file."""
        try:
            if self.theme_manager.import_json_theme(import_path, theme_name):
                imported_name = theme_name or Path(import_path).stem
                return f"✅ Theme imported successfully as '{imported_name}'\n" \
                       f"💡 Use: THEME PREVIEW {imported_name} to preview\n" \
                       f"💡 Use: THEME {imported_name} to activate"
            else:
                return "❌ Failed to import theme"
        except Exception as e:
            return f"❌ Import failed: {str(e)}"

    def _validate_theme(self, theme_name):
        """Validate theme structure."""
        try:
            theme_data = self.theme_manager.load_json_theme(theme_name)
            if not theme_data:
                return f"❌ Theme '{theme_name}' not found"

            is_valid, errors = self.theme_manager.validate_json_theme(theme_data)

            output = []
            output.append(f"\n🔍 VALIDATION RESULTS: {theme_name}")
            output.append("=" * 60)

            if is_valid:
                output.append("✅ Theme is VALID")
                output.append("\nAll required fields and sections present.")
            else:
                output.append("❌ Theme is INVALID")
                output.append(f"\nFound {len(errors)} error(s):")
                for error in errors:
                    output.append(f"  • {error}")

            output.append("")
            return "\n".join(output)

        except Exception as e:
            return f"❌ Validation failed: {str(e)}"

    def _show_theme_details(self, theme_name):
        """Show detailed theme information."""
        try:
            metadata = self.theme_manager.get_json_theme_metadata(theme_name)
            if not metadata:
                return f"❌ Theme '{theme_name}' not found"

            theme_data = self.theme_manager.load_json_theme(theme_name)

            output = []
            output.append(f"\n{metadata.icon} {metadata.name.upper()}")
            output.append("=" * 60)
            output.append(f"Version: {metadata.version}")
            output.append(f"Style: {metadata.style}")
            output.append(f"Description: {metadata.description}")

            if metadata.author:
                output.append(f"Author: {metadata.author}")
            if metadata.created:
                output.append(f"Created: {metadata.created}")

            # Show sections
            output.append("\nSections:")
            sections = ["CORE_SYSTEM", "CORE_USER", "TERMINOLOGY", "MESSAGE_STYLES",
                       "CHARACTER_TYPES", "OBJECT_TYPES", "LOCATION_TRACKING"]
            for section in sections:
                has_section = "✓" if section in theme_data else "✗"
                output.append(f"  {has_section} {section}")

            # Validation
            is_valid, errors = self.theme_manager.validate_json_theme(theme_data)
            output.append(f"\nValidation: {'✅ VALID' if is_valid else '❌ INVALID'}")

            output.append("\n💡 Use: THEME PREVIEW " + theme_name + " to see preview")
            output.append("")

            return "\n".join(output)

        except Exception as e:
            return f"❌ Failed to show details: {str(e)}"

    def _show_theme_stats(self):
        """Show theme statistics."""
        try:
            return self.theme_manager.get_json_theme_stats()
        except Exception as e:
            return f"❌ Failed to show stats: {str(e)}"

    def _list_templates(self):
        """List available theme templates."""
        try:
            return self.theme_builder.list_templates()
        except Exception as e:
            return f"❌ Failed to list templates: {str(e)}"

    # ==================== End v1.0.13 Methods ====================

    def _backup_theme(self):
        """Backup current theme configuration."""
        try:
            backup_dir = Path('memory/config')
            backup_dir.mkdir(parents=True, exist_ok=True)

            current_theme = getattr(self.theme, 'name', 'default') if self.theme else 'default'
            backup_file = backup_dir / f'theme_backup_{current_theme}.json'

            # Create backup data
            backup_data = {
                'theme_name': current_theme,
                'backup_timestamp': Path().cwd().name,  # Simple timestamp
                'settings': {
                    'debug_mode': getattr(self.logger, 'debug_enabled', False) if self.logger else False
                }
            }

            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2)

            return f"✅ Theme backup saved to: {backup_file}"

        except Exception as e:
            return f"❌ Failed to backup theme: {str(e)}"

    def _restore_theme(self):
        """Restore theme from backup."""
        try:
            backup_dir = Path('memory/config')
            if not backup_dir.exists():
                return "❌ No backup directory found"

            backup_files = list(backup_dir.glob('theme_backup_*.json'))
            if not backup_files:
                return "❌ No theme backups found"

            # Use most recent backup
            latest_backup = max(backup_files, key=lambda f: f.stat().st_mtime)

            with open(latest_backup, 'r') as f:
                backup_data = json.load(f)

            theme_name = backup_data.get('theme_name', 'default')

            # Restore theme
            if self.theme and hasattr(self.theme, 'load_theme'):
                self.theme.load_theme(theme_name)
                return f"✅ Restored theme: {theme_name} from backup"
            else:
                return "❌ Theme manager not available"

        except Exception as e:
            return f"❌ Failed to restore theme: {str(e)}"

    def handle_config(self, params, grid, parser):
        """
        Manage configuration files and system settings (Smart Mode v1.0.29).

        Smart Mode (no arguments):
            CONFIG               - Interactive menu for all config operations

        Explicit Mode (backward compatible):
            CONFIG BACKUP        - Backup all configs
            CONFIG RESTORE       - Restore from backup
            CONFIG RESET         - Reset to defaults
            CONFIG VALIDATE      - Validate all configs
            CONFIG VIEWPORT      - Show viewport information
            CONFIG VIEWPORT <w> <h> - Set custom viewport (in cells)
            CONFIG GET <key>     - Get configuration value
            CONFIG SET <key> <value> - Set configuration value

        Manages configuration files in core/data/ directory.
        """
        # SMART MODE: No params → Interactive menu
        if not params:
            return self._config_interactive_menu()

        # EXPLICIT MODE: Backward compatible command routing
        command = params[0].upper()

        if command == 'BACKUP':
            return self._backup_configs()
        elif command == 'RESTORE':
            return self._restore_configs()
        elif command == 'RESET':
            return self._reset_configs()
        elif command == 'VALIDATE':
            return self._validate_configs()
        elif command == 'CHECK':
            return self._check_folder_structure()
        elif command == 'FIX':
            return self._fix_folder_structure()
        elif command == 'VIEWPORT':
            if len(params) == 1:
                return self._show_viewport_config()
            elif len(params) == 3:
                try:
                    width = int(params[1])
                    height = int(params[2])
                    return self._set_viewport_config(width, height)
                except ValueError:
                    return "❌ Invalid viewport dimensions. Use: CONFIG VIEWPORT <width> <height>"
            else:
                return ("❌ Invalid viewport command\n\n"
                       "Usage:\n"
                       "  CONFIG VIEWPORT        - Show current viewport\n"
                       "  CONFIG VIEWPORT <w> <h> - Set custom viewport in cells")
        elif command == 'GET':
            if len(params) < 2:
                return "❌ Usage: CONFIG GET <key>"
            return self._get_config_value(params[1])
        elif command == 'SET':
            if len(params) < 3:
                return "❌ Usage: CONFIG SET <key> <value>"
            return self._set_config_value(params[1], ' '.join(params[2:]))
        else:
            return ("❌ Unknown config command\n\n"
                   "Available commands:\n"
                   "  CONFIG           - Interactive menu (smart mode)\n"
                   "  CONFIG BACKUP    - Backup configurations\n"
                   "  CONFIG RESTORE   - Restore from backup\n"
                   "  CONFIG RESET     - Reset to defaults\n"
                   "  CONFIG VALIDATE  - Validate configurations\n"
                   "  CONFIG VIEWPORT  - Manage viewport settings\n"
                   "  CONFIG GET <key> - Get configuration value\n"
                   "  CONFIG SET <key> <value> - Set configuration value")

    def _show_config_status(self):
        """Show current configuration status with v1.5.0 features."""
        config_dir = Path('core/data')
        if not config_dir.exists():
            return self.get_message('ERROR_CONFIG_DIR_NOT_FOUND', path=config_dir)

        config_files = [
            'commands.json',
            'extensions.json',
            'font-system.json',  # v2.0.0: Includes color palette
            'fonts.json',
            'locations.json'  # v2.0.0: TILE code system
        ]

        # Get current settings
        user_role = self.config_manager.get('USER_ROLE', 'user') if hasattr(self, 'config_manager') else 'user'
        theme = self.config_manager.get('THEME', 'dungeon') if hasattr(self, 'config_manager') else 'dungeon'
        auto_save = self.config_manager.get('AUTO_SAVE', 'true') if hasattr(self, 'config_manager') else 'true'

        output = []
        output.append("╔══════════════════════════════════════════════════════════╗")
        output.append("║           ⚙️  uDOS CONFIGURATION STATUS                 ║")
        output.append("╚══════════════════════════════════════════════════════════╝")
        output.append("")
        output.append("📊 SYSTEM SETTINGS")
        output.append("─" * 60)
        output.append(f"  User Role:        {user_role}")
        output.append(f"  Theme:            {theme}")
        output.append(f"  Auto-save:        {auto_save}")
        output.append("")
        output.append("📁 CONFIGURATION FILES")
        output.append("─" * 60)

        total_size = 0
        valid_count = 0

        for config_file in config_files:
            file_path = config_dir / config_file
            if file_path.exists():
                size = file_path.stat().st_size
                total_size += size

                # Validate JSON
                try:
                    with open(file_path, 'r') as f:
                        json.load(f)
                    status = "✅ Valid"
                    valid_count += 1
                except:
                    status = "❌ Invalid JSON"

                size_str = f"{size:,} bytes" if size < 1024 else f"{size//1024} KB"
                output.append(f"  {config_file.ljust(20)} {size_str.rjust(10)} {status}")
            else:
                output.append(f"  {config_file.ljust(20)} {'Missing'.rjust(10)} ❌ Not found")

        output.append("")
        output.append(f"Total: {len(config_files)} files, {valid_count} valid, {total_size:,} bytes")
        output.append("")
        output.append("💡 Use: CONFIG VALIDATE for detailed validation")
        output.append("💡 Use: CONFIG BACKUP to save current state")

        return "\n".join(output)

    def _backup_configs(self):
        """Backup all configuration files."""
        try:
            config_dir = Path('core/data')
            backup_dir = Path('memory/system/backup')
            backup_dir.mkdir(parents=True, exist_ok=True)

            backed_up = []
            for config_file in config_dir.glob('*.json'):
                backup_file = backup_dir / config_file.name
                shutil.copy2(config_file, backup_file)
                backed_up.append(config_file.name)

            if backed_up:
                return (f"✅ Backed up {len(backed_up)} configuration files\n\n"
                       f"Backup location: {backup_dir}\n"
                       f"Files: {', '.join(backed_up)}")
            else:
                return "❌ No configuration files found to backup"

        except Exception as e:
            return f"❌ Failed to backup configs: {str(e)}"

    def _restore_configs(self):
        """Restore configuration files from backup."""
        try:
            backup_dir = Path('memory/system/backup')
            if not backup_dir.exists():
                return "❌ No backup directory found\n\nUse: CONFIG BACKUP first"

            config_dir = Path('core/data')
            restored = []

            for backup_file in backup_dir.glob('*.json'):
                target_file = config_dir / backup_file.name
                shutil.copy2(backup_file, target_file)
                restored.append(backup_file.name)

            if restored:
                return (f"✅ Restored {len(restored)} configuration files\n\n"
                       f"Files: {', '.join(restored)}\n\n"
                       "💡 Use: REBOOT to apply changes")
            else:
                return "❌ No backup files found to restore"

        except Exception as e:
            return f"❌ Failed to restore configs: {str(e)}"

    def _reset_configs(self):
        """Reset configurations to defaults."""
        # This would require default config templates
        return ("⚠️  CONFIG RESET not implemented\n\n"
               "To reset configurations:\n"
               "1. Backup current configs: CONFIG BACKUP\n"
               "2. Restore from templates in core/data/templates/\n"
               "3. Or reinstall uDOS")

    def _validate_configs(self):
        """Validate all configuration files."""
        config_dir = Path('core/data')
        if not config_dir.exists():
            return "❌ Configuration directory not found"

        output = []
        output.append("🔍 CONFIGURATION VALIDATION")
        output.append("=" * 50)

        valid_count = 0
        total_count = 0

        for config_file in config_dir.glob('*.json'):
            total_count += 1
            try:
                with open(config_file, 'r') as f:
                    data = json.load(f)

                # Basic validation
                if isinstance(data, dict) and data:
                    output.append(f"  ✅ {config_file.name}: Valid JSON with {len(data)} keys")
                    valid_count += 1
                else:
                    output.append(f"  ⚠️  {config_file.name}: Valid JSON but empty or invalid structure")

            except json.JSONDecodeError as e:
                output.append(f"  ❌ {config_file.name}: JSON Error - {str(e)}")
            except Exception as e:
                output.append(f"  ❌ {config_file.name}: Error - {str(e)}")

        output.append("")
        if valid_count == total_count:
            output.append(f"✅ All {total_count} configuration files are valid")
        else:
            output.append(f"⚠️  {valid_count}/{total_count} configuration files are valid")
            output.append("💡 Use: CONFIG RESTORE to restore from backup")

        return "\n".join(output)

    def _show_viewport_config(self):
        """Show current viewport configuration."""
        try:
            from core.services.viewport_manager import ViewportManager

            viewport = ViewportManager()
            summary = viewport.get_viewport_summary()
            chart = viewport.get_size_comparison_chart()

            output = [
                "📐 Viewport Configuration",
                "=" * 50,
                summary,
                "",
                chart,
                "",
                "💡 Use: CONFIG VIEWPORT <width> <height> to set custom dimensions",
                "💡 Use: REBOOT to refresh auto-detection"
            ]

            return "\n".join(output)

        except ImportError:
            return "❌ Viewport manager not available"
        except Exception as e:
            return f"❌ Error reading viewport config: {str(e)}"

    def _set_viewport_config(self, width_cells: int, height_cells: int):
        """Set custom viewport configuration."""
        try:
            from core.services.viewport_manager import ViewportManager

            # Validate dimensions
            if width_cells < 10 or height_cells < 5:
                return "❌ Viewport too small. Minimum: 10×5 cells"

            if width_cells > 1000 or height_cells > 1000:
                return "❌ Viewport too large. Maximum: 1000×1000 cells"

            viewport = ViewportManager()
            viewport_info = viewport.set_custom_viewport(width_cells, height_cells)

            tier = viewport_info["screen_tier"]

            output = [
                "✅ Viewport configuration updated",
                "",
                f"📐 Custom Viewport: {width_cells}×{height_cells} cells",
                f"📏 Pixel Dimensions: {tier['width_pixels']}×{tier['height_pixels']}px",
                f"📺 Nearest Tier: {tier['label']} (Tier {tier['tier']})",
                f"📊 Aspect Ratio: {tier['aspect']}",
                "",
                "💾 Settings saved to core/data/viewport.json",
                "💡 Use: REBOOT to apply changes fully",
                "💡 Use: CONFIG VIEWPORT to view current settings"
            ]

            return "\n".join(output)

        except ImportError:
            return "❌ Viewport manager not available"
        except Exception as e:
            return f"❌ Error setting viewport config: {str(e)}"

    # ======================================================================
    # SMART MODE (v1.0.29) - Interactive Configuration
    # ======================================================================

    def _config_interactive_menu(self):
        """
        Smart mode: Interactive configuration menu.
        Shows all config options and prompts user for action.
        """
        try:
            # Present menu choices
            choices = [
                "View Configuration Status",
                "API Keys & Credentials",
                "User Profile Settings",
                "System Settings (Theme, Viewport, Debug)",
                "Quick Setup (View/Edit All Settings)",
                "Backup/Restore Configuration",
                "Validate All Configurations",
                "Cancel"
            ]

            choice = self.input_manager.prompt_choice(
                message="What would you like to configure?",
                choices=choices,
                default="View Configuration Status"
            )

            if choice == "View Configuration Status":
                return self._show_config_status()

            elif choice == "API Keys & Credentials":
                return self._manage_api_keys_interactive()

            elif choice == "User Profile Settings":
                return self._manage_user_profile_interactive()

            elif choice == "System Settings (Theme, Viewport, Debug)":
                return self._manage_system_settings_interactive()

            elif choice == "Quick Setup (View/Edit All Settings)":
                return self._show_all_settings()

            elif choice == "Backup/Restore Configuration":
                return self._manage_backup_restore_interactive()

            elif choice == "Validate All Configurations":
                return self._validate_configs()

            else:  # Cancel
                return "Configuration menu cancelled."

        except Exception as e:
            return self.output_formatter.format_error(
                "Configuration menu failed",
                error_details=str(e)
            )

    def _manage_api_keys_interactive(self):
        """Interactive API key management (v1.5.0: Uses ConfigManager)."""
        try:
            # Get ConfigManager instance
            config = get_config()

            # Get current API keys from ConfigManager
            gemini_key = config.get_env('GEMINI_API_KEY', '')
            github_token = config.get_env('GITHUB_TOKEN', '')

            # Show current status
            output = []
            output.append(self.output_formatter.format_panel(
                "API Keys & Credentials",
                f"Gemini API Key: {'✅ Set' if gemini_key else '❌ Not set'}\n"
                f"GitHub Token: {'✅ Set' if github_token else '❌ Not set'}"
            ))

            # Ask what to do
            action = self.input_manager.prompt_choice(
                message="Choose an action:",
                choices=[
                    "Set Gemini API Key",
                    "Set GitHub Token",
                    "View Current Keys (masked)",
                    "Clear API Keys",
                    "Back to Main Menu"
                ],
                default="Back to Main Menu"
            )

            if action == "Set Gemini API Key":
                new_key = self.input_manager.prompt_user(
                    message="Enter Gemini API Key (or leave blank to skip):",
                    default=gemini_key,
                    required=False
                )
                if new_key:
                    config.set_env('GEMINI_API_KEY', new_key)
                    output.append("\n✅ Gemini API Key updated")
                    output.append("📝 Changes saved to .env")
                else:
                    output.append("\n⚠️ Gemini API Key unchanged")

            elif action == "Set GitHub Token":
                new_token = self.input_manager.prompt_user(
                    message="Enter GitHub Personal Access Token:",
                    default=github_token,
                    required=False
                )
                if new_token:
                    config.set_env('GITHUB_TOKEN', new_token)
                    output.append("\n✅ GitHub Token updated")
                    output.append("📝 Changes saved to .env")
                else:
                    output.append("\n⚠️ GitHub Token unchanged")

            elif action == "View Current Keys (masked)":
                masked_gemini = f"{gemini_key[:8]}...{gemini_key[-4:]}" if len(gemini_key) > 12 else "Not set"
                masked_github = f"{github_token[:8]}...{github_token[-4:]}" if len(github_token) > 12 else "Not set"
                output.append(f"\nGemini API Key: {masked_gemini}")
                output.append(f"GitHub Token: {masked_github}")

            elif action == "Clear API Keys":
                confirm = self.input_manager.prompt_confirm(
                    message="Are you sure you want to clear all API keys?",
                    default=False
                )
                if confirm:
                    config.set_env('GEMINI_API_KEY', '')
                    config.set_env('GITHUB_TOKEN', '')
                    output.append("\n✅ API Keys cleared")
                    output.append("📝 Changes saved to .env")
                else:
                    output.append("\n⚠️ Operation cancelled")

            return "\n".join(output)

        except Exception as e:
            return self.output_formatter.format_error(
                "API key management failed",
                error_details=str(e)
            )

    def _manage_user_profile_interactive(self):
        """Interactive user profile management (v1.5.0: Uses ConfigManager)."""
        try:
            # Get ConfigManager instance
            config = get_config()

            # Auto-detect system timezone and location
            from core.utils.system_info import get_system_timezone
            detected_timezone, detected_city = get_system_timezone()

            # Get current profile from ConfigManager (user.json only - single source of truth)
            user_name = config.get_user('USER_PROFILE.NAME', '')
            password = config.get_user('USER_PROFILE.PASSWORD', '')
            location = config.get_user('USER_PROFILE.LOCATION', '')
            timezone = config.get_user('USER_PROFILE.TIMEZONE', '')

            # Use detected values as defaults if not set
            if not timezone or timezone == 'UTC':
                timezone = detected_timezone
            if not location or location == 'Unknown':
                location = detected_city

            # Show current profile
            output = []
            output.append(self.output_formatter.format_panel(
                "User Profile",
                f"Username: {user_name or 'Not set'}\n"
                f"Password: {'●●●●●●' if password else 'Not set (optional)'}\n"
                f"Location: {location or 'Not set'}\n"
                f"Timezone: {timezone}\n"
                f"\nℹ️  Detected: {detected_timezone} ({detected_city})"
            ))

            # Ask what to update
            action = self.input_manager.prompt_choice(
                message="What would you like to update?",
                choices=[
                    "Username",
                    "Password",
                    "Location",
                    "Timezone",
                    "Update All Fields",
                    "Back to Main Menu"
                ],
                default="Back to Main Menu"
            )

            if action == "Username":
                new_name = self.input_manager.prompt_user(
                    message="Enter username:",
                    default=user_name,
                    required=True
                )
                # Update via ConfigManager (user.json only - single source of truth)
                config.set_user('USER_PROFILE.NAME', new_name)
                output.append(f"\n✅ Username updated to: {new_name}")

            elif action == "Password":
                new_password = self.input_manager.prompt_user(
                    message="Enter password (leave blank for none):",
                    default="",
                    required=False
                )
                config.set_user('USER_PROFILE.PASSWORD', new_password if new_password else '')
                if new_password:
                    output.append("\n✅ Password updated")
                else:
                    output.append("\n✅ Password cleared")

            elif action == "Location":
                new_location = self.input_manager.prompt_user(
                    message=f"Enter location (detected: {detected_city}):",
                    default=location or detected_city,
                    required=False
                )
                config.set_user('USER_PROFILE.LOCATION', new_location)
                output.append(f"\n✅ Location updated to: {new_location}")

            elif action == "Timezone":
                new_timezone = self.input_manager.prompt_user(
                    message=f"Enter timezone (detected: {detected_timezone}):",
                    default=timezone or detected_timezone,
                    required=False
                )
                config.set_user('USER_PROFILE.TIMEZONE', new_timezone)
                output.append(f"\n✅ Timezone updated to: {new_timezone}")

            elif action == "Update All Fields":
                # Prompt for all fields with auto-detected defaults
                new_name = self.input_manager.prompt_user(
                    message="Username:",
                    default=user_name,
                    required=True
                )

                new_password = self.input_manager.prompt_user(
                    message="Password (leave blank for none):",
                    default="",
                    required=False
                )

                new_timezone = self.input_manager.prompt_user(
                    message=f"Timezone (detected: {detected_timezone}):",
                    default=timezone or detected_timezone,
                    required=False
                )

                new_location = self.input_manager.prompt_user(
                    message=f"Location (defaults to timezone city):",
                    default=location or detected_city,
                    required=False
                )

                # Save all fields via ConfigManager (user.json only - single source of truth)
                config.set_user('USER_PROFILE.NAME', new_name)
                if new_password:
                    config.set_user('USER_PROFILE.PASSWORD', new_password)
                config.set_user('USER_PROFILE.TIMEZONE', new_timezone)
                config.set_user('USER_PROFILE.LOCATION', new_location)

                output.append("\n✅ User profile updated")
                output.append("📝 Changes saved to user.json")

            return "\n".join(output)

        except Exception as e:
            return self.output_formatter.format_error(
                "User profile management failed",
                error_details=str(e)
            )

    def _manage_system_settings_interactive(self):
        """Interactive system settings management (v2.0: Enhanced with palettes, dev mode)."""
        try:
            # Get ConfigManager instance
            config = get_config()

            # Get current settings
            current_theme = config.get_env('THEME', 'dungeon')
            current_palette = config.get_user('system_settings.interface.color_palette', 'polaroid')
            debug_mode = getattr(self.logger, 'debug_enabled', False) if self.logger else False
            dev_mode = config.get('DEV_MODE', False)
            cli_editor = config.get_env('CLI_EDITOR', 'micro')

            # Show current settings
            output = []
            output.append(self.output_formatter.format_panel(
                "System Settings",
                f"Theme: {current_theme}\n"
                f"Color Palette: {current_palette}\n"
                f"Debug Mode: {'Enabled' if debug_mode else 'Disabled'}\n"
                f"Dev Mode: {'Enabled' if dev_mode else 'Disabled'}\n"
                f"CLI Editor: {cli_editor}"
            ))

            # Ask what to update
            action = self.input_manager.prompt_choice(
                message="What would you like to change?",
                choices=[
                    "Change Theme",
                    "Select Color Palette",
                    "Toggle Debug Mode",
                    "Toggle Dev Mode",
                    "Configure Viewport",
                    "Set CLI Editor (micro/nano/vim)",
                    "Edit System Location (Galaxy/Planet/City)",
                    "View Viewport Info",
                    "Back to Main Menu"
                ],
                default="Back to Main Menu"
            )

            if action == "Change Theme":
                # Get available themes
                themes_dir = Path('core/data/themes')
                available_themes = []
                if themes_dir.exists():
                    available_themes = [f.stem for f in themes_dir.glob('*.json')]

                if not available_themes:
                    output.append("\n❌ No themes found in core/data/themes/")
                else:
                    new_theme = self.input_manager.prompt_choice(
                        message="Select a theme:",
                        choices=available_themes,
                        default=current_theme if current_theme in available_themes else available_themes[0]
                    )
                    config.set_env('THEME', new_theme)
                    output.append(f"\n✅ Theme changed to: {new_theme}")
                    output.append("📝 Changes saved to .env and user.json")
                    output.append("⚠️ Restart uDOS to apply theme changes")

            elif action == "Select Color Palette":
                # Available palettes from uDOS style guide
                palettes = [
                    "polaroid",      # Default: warm, nostalgic
                    "concrete",      # Neutral grays
                    "brutalist",     # High contrast
                    "terminal",      # Classic green/amber
                    "cyberpunk",     # Neon colors
                    "sepia",         # Vintage brown tones
                    "mono",          # Black and white
                    "earth"          # Natural earth tones
                ]

                new_palette = self.input_manager.prompt_choice(
                    message="Select color palette:",
                    choices=palettes,
                    default=current_palette if current_palette in palettes else "polaroid"
                )
                config.set_user('system_settings.interface.color_palette', new_palette)
                output.append(f"\n✅ Color palette set to: {new_palette}")
                output.append("📝 Changes saved to user.json")
                output.append("💡 Restart for full palette application")

            elif action == "Toggle Debug Mode":
                if self.logger:
                    self.logger.debug_enabled = not debug_mode
                    new_state = "enabled" if self.logger.debug_enabled else "disabled"
                    output.append(f"\n✅ Debug mode {new_state}")
                else:
                    output.append("\n❌ Logger not available")

            elif action == "Toggle Dev Mode":
                new_dev_mode = not dev_mode
                config.set('DEV_MODE', new_dev_mode)
                output.append(f"\n✅ Dev Mode {'enabled' if new_dev_mode else 'disabled'}")
                output.append("📝 Changes saved to user.json")
                if new_dev_mode:
                    output.append("💡 Dev Mode unlocks: sandbox write access, debug commands, verbose logging")

            elif action == "Configure Viewport":
                width = self.input_manager.prompt_user(
                    message="Enter viewport width (cells, 10-1000):",
                    default="80",
                    required=True
                )
                height = self.input_manager.prompt_user(
                    message="Enter viewport height (cells, 5-1000):",
                    default="24",
                    required=True
                )
                try:
                    return self._set_viewport_config(int(width), int(height))
                except ValueError:
                    output.append("\n❌ Invalid dimensions")

            elif action == "Set CLI Editor (micro/nano/vim)":
                # Get current editor
                current_editor = config.get_env('CLI_EDITOR', 'micro')

                # Detect available editors
                from core.services.editor_manager import EditorManager
                editor_mgr = EditorManager()
                available = editor_mgr.detect_available_editors()

                if not available['CLI']:
                    output.append("\n❌ No CLI editors found!")
                else:
                    # Prioritize micro as default
                    choices = available['CLI'].copy()
                    if 'micro' not in available['CLI']:
                        choices.append("📥 Install micro editor")
                    choices.append("Back")

                    new_editor = self.input_manager.prompt_choice(
                        message="Select default CLI editor (micro recommended):",
                        choices=choices,
                        default='micro' if 'micro' in available['CLI'] else current_editor
                    )

                    if new_editor == "📥 Install micro editor":
                        output.append("\n📦 Installing micro editor...")
                        if editor_mgr.install_micro():
                            output.append("✅ Micro editor installed successfully!")
                            config.set_env('CLI_EDITOR', 'micro')
                            output.append("📝 Set as default CLI editor")
                            output.append("💡 Use 'edit filename' to open files in micro")
                        else:
                            output.append("❌ Failed to install micro editor")
                    elif new_editor != "Back":
                        config.set_env('CLI_EDITOR', new_editor)

                        # Reload environment variable immediately
                        import os
                        os.environ['CLI_EDITOR'] = new_editor

                        output.append(f"\n✅ CLI editor set to: {new_editor}")
                        output.append("📝 Changes saved to .env")
                        output.append(f"💡 Use 'edit filename' to open files in {new_editor}")

            elif action == "Edit System Location (Galaxy/Planet/City)":
                # Show current location (from USER_PROFILE and LOCATION_DATA)
                galaxy = config.get_user('USER_PROFILE.GALAXY', 'Milky Way')
                planet = config.get_user('USER_PROFILE.PLANET', 'Earth')
                city = config.get_user('USER_PROFILE.LOCATION', 'Not set')  # City name

                output.append(f"\n📍 Current Location: {galaxy} > {planet} > {city}")
                output.append("\n💡 To change location, run: WIZARD")
                output.append("   This will guide you through city selection with TILE codes")

            elif action == "View Viewport Info":
                return self._show_viewport_config()

            return "\n".join(output)

        except Exception as e:
            return self.output_formatter.format_error(
                "System settings management failed",
                error_details=str(e)
            )

    def _manage_backup_restore_interactive(self):
        """Interactive backup/restore management."""
        try:
            action = self.input_manager.prompt_choice(
                message="Backup/Restore Options:",
                choices=[
                    "Backup All Configurations",
                    "Restore from Backup",
                    "Reset to Defaults",
                    "Back to Main Menu"
                ],
                default="Back to Main Menu"
            )

            if action == "Backup All Configurations":
                return self._backup_configs()

            elif action == "Restore from Backup":
                confirm = self.input_manager.prompt_confirm(
                    message="Restore configurations from backup? Current configs will be overwritten.",
                    default=False
                )
                if confirm:
                    return self._restore_configs()
                else:
                    return "⚠️ Restore cancelled"

            elif action == "Reset to Defaults":
                confirm = self.input_manager.prompt_confirm(
                    message="Reset all configurations to defaults? This cannot be undone.",
                    default=False
                )
                if confirm:
                    return self._reset_configs()
                else:
                    return "⚠️ Reset cancelled"

            else:
                return "Backup/restore menu cancelled."

        except Exception as e:
            return self.output_formatter.format_error(
                "Backup/restore failed",
                error_details=str(e)
            )

    def _get_config_value(self, key: str):
        """Get a configuration value by key (v1.5.0: Uses ConfigManager)."""
        try:
            config = get_config()

            # Try ConfigManager first for known keys
            # Check ENV keys first, then user config
            if key.upper() in config.ENV_KEYS:
                value = config.get_env(key.upper())
            else:
                value = config.get_user(key)

            if value is not None:
                return self.output_formatter.format_panel(
                    f"Configuration: {key}",
                    str(value)
                )

            # Fallback to story_manager for legacy/unknown keys
            if '.' in key:
                value = self.story_manager.get_field(key, default='Not found')
            else:
                value = self.story_manager.get_field(f'CONFIG.{key}', default='Not found')

            return self.output_formatter.format_panel(
                f"Configuration: {key}",
                str(value)
            )

        except Exception as e:
            return self.output_formatter.format_error(
                f"Failed to get config: {key}",
                error_details=str(e)
            )

    def _set_config_value(self, key: str, value: str):
        """Set a configuration value by key (v1.5.0: Uses ConfigManager)."""
        try:
            config = get_config()

            # Try ConfigManager first for known keys
            try:
                # Route to appropriate method based on key type
                if key.upper() in config.ENV_KEYS:
                    config.set_env(key.upper(), value)
                else:
                    config.set_user(key, value)
                return self.output_formatter.format_panel(
                    f"Configuration Updated: {key}",
                    f"New value: {value}\n📝 Changes saved to .env and user.json"
                )
            except KeyError:
                # Fallback to story_manager for legacy/unknown keys
                if '.' in key:
                    self.story_manager.set_field(key, value, auto_save=True)
                else:
                    self.story_manager.set_field(f'CONFIG.{key}', value, auto_save=True)

            return self.output_formatter.format_success(
                f"Configuration updated: {key} = {value}"
            )

        except Exception as e:
            return self.output_formatter.format_error(
                f"Failed to set config: {key}",
                error_details=str(e)
            )

    def _load_cities_list(self):
        """Load cities from cities.json for location selection."""
        try:
            from core.utils.paths import PATHS
            cities_path = PATHS.CORE_DATA_GEOGRAPHY_CITIES
            if cities_path.exists():
                with open(cities_path, 'r') as f:
                    data = json.load(f)
                    return data.get('cities', [])
        except Exception:
            pass
        return None

    def _check_folder_structure(self):
        """Check v1.2.12 folder structure and report issues."""
        from pathlib import Path
        
        output = []
        output.append("═" * 70)
        output.append("📁 CONFIG CHECK - Folder Structure Validation (v1.2.12)")
        output.append("═" * 70)
        output.append("")
        
        root = Path.cwd()
        
        # Define required v1.2.x structure
        required_folders = [
            ('memory/ucode/scripts', 'User .upy scripts'),
            ('memory/ucode/tests', 'Test suites'),
            ('memory/ucode/sandbox', 'Experimental scripts'),
            ('memory/ucode/stdlib', 'Standard library'),
            ('memory/ucode/examples', 'Example scripts'),
            (str(PATHS.MEMORY_UCODE_ADVENTURES), 'Adventure scripts'),
            (str(PATHS.MEMORY_WORKFLOWS_MISSIONS), 'Mission scripts'),
            (str(PATHS.MEMORY_WORKFLOWS_CHECKPOINTS), 'State snapshots'),
            (str(PATHS.MEMORY_WORKFLOWS_STATE), 'Current execution state'),
            ('memory/workflows/extensions', 'Gameplay integration'),
            ('memory/system/user', 'User settings'),
            ('memory/system/themes', 'Custom themes'),
            ('memory/bank', 'Banking/transactions'),
            ('memory/shared', 'Shared/community content'),
            ('memory/docs', 'User documentation'),
            ('memory/drafts', 'Draft content'),
        ]
        
        missing = []
        present = []
        
        for folder, description in required_folders:
            folder_path = root / folder
            if folder_path.exists():
                present.append((folder, description))
            else:
                missing.append((folder, description))
        
        # Report results
        output.append(f"✅ Present: {len(present)}/{len(required_folders)}")
        if missing:
            output.append(f"❌ Missing: {len(missing)}/{len(required_folders)}")
            output.append("")
            output.append("Missing folders:")
            for folder, description in missing:
                output.append(f"  ❌ {folder}/")
                output.append(f"     {description}")
            output.append("")
            output.append("💡 Run 'CONFIG FIX' to create missing folders")
        else:
            output.append("")
            output.append("✅ All required folders present!")
        
        output.append("")
        return "\n".join(output)

    def _fix_folder_structure(self):
        """Create missing v1.2.12 folders with .gitkeep files."""
        from pathlib import Path
        
        output = []
        output.append("═" * 70)
        output.append("🔧 CONFIG FIX - Creating Missing Folders (v1.2.12)")
        output.append("═" * 70)
        output.append("")
        
        root = Path.cwd()
        
        # Define required v1.2.x structure
        required_folders = [
            'memory/ucode/scripts',
            'memory/ucode/tests',
            'memory/ucode/sandbox',
            'memory/ucode/stdlib',
            'memory/ucode/examples',
            str(PATHS.MEMORY_UCODE_ADVENTURES),
            str(PATHS.MEMORY_WORKFLOWS_MISSIONS),
            str(PATHS.MEMORY_WORKFLOWS_CHECKPOINTS),
            str(PATHS.MEMORY_WORKFLOWS_STATE),
            'memory/workflows/extensions',
            'memory/system/user',
            'memory/system/themes',
            'memory/bank',
            'memory/shared',
            'memory/docs',
            'memory/drafts',
        ]
        
        created = []
        existed = []
        
        for folder in required_folders:
            folder_path = root / folder
            if folder_path.exists():
                existed.append(folder)
            else:
                try:
                    folder_path.mkdir(parents=True, exist_ok=True)
                    # Add .gitkeep for empty tracked directories
                    gitkeep = folder_path / '.gitkeep'
                    if not gitkeep.exists():
                        gitkeep.touch()
                    created.append(folder)
                    output.append(f"  ✅ Created: {folder}/")
                except Exception as e:
                    output.append(f"  ❌ Failed: {folder}/ - {e}")
        
        output.append("")
        output.append(f"Summary:")
        output.append(f"  ✅ Created: {len(created)} folders")
        output.append(f"  ℹ️  Existed: {len(existed)} folders")
        output.append("")
        
        if created:
            output.append("✅ Folder structure fixed!")
        else:
            output.append("ℹ️  All folders already present")
        
        output.append("")
        return "\n".join(output)
