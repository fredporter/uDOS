"""
uDOS v1.0.13 - Configuration Handler

Handles configuration management operations:
- Settings display and modification
- Theme switching and configuration
- Configuration file management
- User preferences
- Advanced theme management (v1.0.13+)
"""

import json
import shutil
from pathlib import Path
from .base_handler import BaseCommandHandler
from core.services.theme_manager import ThemeManager
from core.services.theme_builder import ThemeBuilder


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

    def handle_settings(self, params, grid, parser):
        """
        Display or modify system settings.

        Usage:
            SETTINGS                 - Show all settings
            SETTINGS <key>           - Show specific setting
            SETTINGS <key> <value>   - Set setting value

        Settings categories:
            - THEME: Color theme settings
            - GRID: Grid display settings
            - USER: User profile settings
            - SYSTEM: System configuration
        """
        if not params:
            return self._show_all_settings()
        elif len(params) == 1:
            return self._show_setting(params[0])
        elif len(params) == 2:
            return self._set_setting(params[0], params[1])
        else:
            return ("❌ Invalid settings command\n\n"
                   "Usage:\n"
                   "  SETTINGS                  - Show all settings\n"
                   "  SETTINGS <key>           - Show specific setting\n"
                   "  SETTINGS <key> <value>   - Set setting value")

    def _show_all_settings(self):
        """Display all current settings organized by category."""
        output = []
        output.append("⚙️ uDOS SYSTEM SETTINGS")
        output.append("=" * 60)

        # Theme settings
        output.append("")
        output.append("🎨 THEME SETTINGS:")
        output.append("-" * 40)
        if self.theme:
            output.append(f"  Current Theme: {getattr(self.theme, 'name', 'Default')}")
            output.append(f"  Color Mode: {getattr(self.theme, 'color_mode', 'AUTO')}")
        else:
            output.append("  Theme: Not loaded")

        # Grid settings
        output.append("")
        output.append("📐 GRID SETTINGS:")
        output.append("-" * 40)
        if self.viewport:
            output.append(f"  Terminal Size: {self.viewport.width}×{self.viewport.height}")
            output.append(f"  Grid Size: {getattr(self.viewport, 'grid_width', '?')}×{getattr(self.viewport, 'grid_height', '?')}")
            output.append(f"  Device Type: {getattr(self.viewport, 'device_type', 'UNKNOWN')}")
        else:
            output.append("  Grid: Not initialized")

        # User settings
        output.append("")
        output.append("👤 USER SETTINGS:")
        output.append("-" * 40)

        # Get user data from story_manager (STORY section)
        user_name = self.story_manager.get_field('STORY.USER_NAME', 'Not set')
        location = self.story_manager.get_field('STORY.LOCATION', 'Not set')
        timezone = self.story_manager.get_field('STORY.TIMEZONE', 'UTC')
        password = self.story_manager.get_field('STORY.PASSWORD', '')
        project_name = self.story_manager.get_field('STORY.PROJECT_NAME', 'Not set')

        password_display = '●●●●●●' if password else 'Not set'

        output.append(f"  Username: {user_name}")
        output.append(f"  Password: {password_display}")
        output.append(f"  Project: {project_name}")
        output.append(f"  Location: {location}")
        output.append(f"  Timezone: {timezone}")

        # Get theme from story manager
        theme_name = self.story_manager.get_field('STORY.THEME', 'Not set')
        output.append(f"  Theme: {theme_name}")

        # System settings
        output.append("")
        output.append("🔧 SYSTEM SETTINGS:")
        output.append("-" * 40)
        output.append(f"  Debug Mode: {getattr(self.logger, 'debug_enabled', False) if self.logger else False}")
        output.append(f"  Auto-save: Enabled")
        output.append(f"  Connection Mode: {self.connection.get_mode() if self.connection else 'OFFLINE'}")

        output.append("")
        output.append("=" * 60)
        output.append("💡 Use: SETTINGS <key> <value> to modify settings")
        output.append("💡 Use: THEME LIST to see available themes")

        return "\n".join(output)

    def _show_setting(self, key):
        """Show a specific setting value."""
        key_upper = key.upper()

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
            # Get user data from story_manager (STORY section)
            user_name = self.story_manager.get_field('STORY.USER_NAME', 'Not set')
            location = self.story_manager.get_field('STORY.LOCATION', 'Not set')
            timezone = self.story_manager.get_field('STORY.TIMEZONE', 'UTC')
            password = self.story_manager.get_field('STORY.PASSWORD', '')

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
            theme_file = Path(f'knowledge/system/themes/{theme_name.lower()}.json')
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
            theme_file = Path(f'knowledge/system/themes/{theme_name.lower()}.json')
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

        Manages configuration files in knowledge/system/ directory.
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
        """Show current configuration status."""
        config_dir = Path('knowledge/system')
        if not config_dir.exists():
            return "❌ Configuration directory not found"

        config_files = [
            'commands.json',
            'extensions.json',
            'palette.json',
            'fonts.json',
            'worldmap.json',
            'credits.json'
        ]

        output = []
        output.append("⚙️ CONFIGURATION STATUS")
        output.append("=" * 50)

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
            config_dir = Path('knowledge/system')
            backup_dir = Path('memory/config/system_backup')
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
            backup_dir = Path('memory/config/system_backup')
            if not backup_dir.exists():
                return "❌ No backup directory found\n\nUse: CONFIG BACKUP first"

            config_dir = Path('knowledge/system')
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
               "2. Restore from templates in knowledge/system/templates/\n"
               "3. Or reinstall uDOS")

    def _validate_configs(self):
        """Validate all configuration files."""
        config_dir = Path('knowledge/system')
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
                "💾 Settings saved to knowledge/system/viewport.json",
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
                "Backup/Restore Configuration",
                "Validate All Configurations",
                "View All Settings (Detailed)",
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

            elif choice == "Backup/Restore Configuration":
                return self._manage_backup_restore_interactive()

            elif choice == "Validate All Configurations":
                return self._validate_configs()

            elif choice == "View All Settings (Detailed)":
                return self._show_all_settings()

            else:  # Cancel
                return "Configuration menu cancelled."

        except Exception as e:
            return self.output_formatter.format_error(
                "Configuration menu failed",
                error_details=str(e)
            )

    def _manage_api_keys_interactive(self):
        """Interactive API key management."""
        try:
            # Get current API keys
            gemini_key = self.story_manager.get_field('CONFIG.API_KEY', '')
            github_token = self.story_manager.get_field('CONFIG.GITHUB_TOKEN', '')

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
                    self.story_manager.set_field('CONFIG.API_KEY', new_key, auto_save=True)
                    output.append("\n✅ Gemini API Key updated")
                else:
                    output.append("\n⚠️ Gemini API Key unchanged")

            elif action == "Set GitHub Token":
                new_token = self.input_manager.prompt_user(
                    message="Enter GitHub Personal Access Token:",
                    default=github_token,
                    required=False
                )
                if new_token:
                    self.story_manager.set_field('CONFIG.GITHUB_TOKEN', new_token, auto_save=True)
                    output.append("\n✅ GitHub Token updated")
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
                    self.story_manager.set_field('CONFIG.API_KEY', '', auto_save=True)
                    self.story_manager.set_field('CONFIG.GITHUB_TOKEN', '', auto_save=True)
                    output.append("\n✅ API Keys cleared")
                else:
                    output.append("\n⚠️ Operation cancelled")

            return "\n".join(output)

        except Exception as e:
            return self.output_formatter.format_error(
                "API key management failed",
                error_details=str(e)
            )

    def _manage_user_profile_interactive(self):
        """Interactive user profile management."""
        try:
            # Auto-detect system timezone and location
            from core.utils.system_info import get_system_timezone
            detected_timezone, detected_city = get_system_timezone()

            # Get current profile
            user_name = self.story_manager.get_field('STORY.USER_NAME', '')
            password = self.story_manager.get_field('STORY.PASSWORD', '')
            location = self.story_manager.get_field('STORY.LOCATION', '')
            timezone = self.story_manager.get_field('STORY.TIMEZONE', '')

            # Use detected values as defaults if not set
            if not timezone:
                timezone = detected_timezone
            if not location:
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
                self.story_manager.set_field('STORY.USER_NAME', new_name, auto_save=True)
                output.append(f"\n✅ Username updated to: {new_name}")

            elif action == "Password":
                new_password = self.input_manager.prompt_user(
                    message="Enter password (leave blank for none):",
                    default="",
                    required=False
                )
                self.story_manager.set_field('STORY.PASSWORD', new_password, auto_save=True)
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
                self.story_manager.set_field('STORY.LOCATION', new_location, auto_save=True)
                output.append(f"\n✅ Location updated to: {new_location}")

            elif action == "Timezone":
                new_timezone = self.input_manager.prompt_user(
                    message=f"Enter timezone (detected: {detected_timezone}):",
                    default=timezone or detected_timezone,
                    required=False
                )
                self.story_manager.set_field('STORY.TIMEZONE', new_timezone, auto_save=True)
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

                # Save all fields
                self.story_manager.set_field('STORY.USER_NAME', new_name, auto_save=False)
                self.story_manager.set_field('STORY.PASSWORD', new_password, auto_save=False)
                self.story_manager.set_field('STORY.TIMEZONE', new_timezone, auto_save=False)
                self.story_manager.set_field('STORY.LOCATION', new_location, auto_save=True)

                output.append("\n✅ User profile updated")

            return "\n".join(output)

        except Exception as e:
            return self.output_formatter.format_error(
                "User profile management failed",
                error_details=str(e)
            )

    def _manage_system_settings_interactive(self):
        """Interactive system settings management."""
        try:
            # Get current settings
            current_theme = self.story_manager.get_field('STORY.THEME', 'dungeon')
            debug_mode = getattr(self.logger, 'debug_enabled', False) if self.logger else False
            offline_mode = self.story_manager.get_field('SYSTEM.OFFLINE_MODE', False)

            # Show current settings
            output = []
            output.append(self.output_formatter.format_panel(
                "System Settings",
                f"Theme: {current_theme}\n"
                f"Debug Mode: {'Enabled' if debug_mode else 'Disabled'}\n"
                f"Offline Mode: {'Enabled' if offline_mode else 'Disabled'}"
            ))

            # Ask what to update
            action = self.input_manager.prompt_choice(
                message="What would you like to change?",
                choices=[
                    "Change Theme",
                    "Toggle Debug Mode",
                    "Configure Viewport",
                    "View Viewport Info",
                    "Back to Main Menu"
                ],
                default="Back to Main Menu"
            )

            if action == "Change Theme":
                # Get available themes
                themes_dir = Path('knowledge/system/themes')
                available_themes = []
                if themes_dir.exists():
                    available_themes = [f.stem for f in themes_dir.glob('*.json')]

                if not available_themes:
                    output.append("\n❌ No themes found in knowledge/system/themes/")
                else:
                    new_theme = self.input_manager.prompt_choice(
                        message="Select a theme:",
                        choices=available_themes,
                        default=current_theme if current_theme in available_themes else available_themes[0]
                    )
                    self.story_manager.set_field('STORY.THEME', new_theme, auto_save=True)
                    output.append(f"\n✅ Theme changed to: {new_theme}")
                    output.append("⚠️ Restart uDOS to apply theme changes")

            elif action == "Toggle Debug Mode":
                if self.logger:
                    self.logger.debug_enabled = not debug_mode
                    new_state = "enabled" if self.logger.debug_enabled else "disabled"
                    output.append(f"\n✅ Debug mode {new_state}")
                else:
                    output.append("\n❌ Logger not available")

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
        """Get a configuration value by key (dot notation)."""
        try:
            # Parse key path
            if '.' in key:
                value = self.story_manager.get_field(key, default='Not found')
            else:
                # Backward compatibility: simple keys
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
        """Set a configuration value by key (dot notation)."""
        try:
            # Parse key path
            if '.' in key:
                self.story_manager.set_field(key, value, auto_save=True)
            else:
                # Backward compatibility: simple keys go to CONFIG
                self.story_manager.set_field(f'CONFIG.{key}', value, auto_save=True)

            return self.output_formatter.format_success(
                f"Configuration updated: {key} = {value}"
            )

        except Exception as e:
            return self.output_formatter.format_error(
                f"Failed to set config: {key}",
                error_details=str(e)
            )
