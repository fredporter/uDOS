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
        if self.user_manager and self.user_manager.user_data:
            user_profile = self.user_manager.user_data.get('user_profile', {})
            output.append(f"  Username: {user_profile.get('username', 'Not set')}")
            output.append(f"  Project: {user_profile.get('project_name', 'Not set')}")

            # Get theme from system settings
            system_settings = self.user_manager.user_data.get('system_settings', {})
            display = system_settings.get('display', {})
            output.append(f"  Theme: {display.get('theme', 'Not set')}")
        else:
            output.append("  User profile: Not loaded")

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
            if self.user_manager and self.user_manager.user_data:
                user_profile = self.user_manager.user_data.get('USER_PROFILE', {})
                return (f"User settings:\n"
                       f"  Name: {user_profile.get('NAME', 'Not set')}\n"
                       f"  Location: {user_profile.get('LOCATION', 'Not set')}\n"
                       f"  Timezone: {user_profile.get('TIMEZONE', 'UTC')}")
            else:
                return "User profile not loaded"

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
            theme_file = Path(f'data/themes/{theme_name.lower()}.json')
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
            theme_file = Path(f'data/themes/{theme_name.lower()}.json')
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
        Manage configuration files and system settings.

        Usage:
            CONFIG               - Show config status
            CONFIG BACKUP        - Backup all configs
            CONFIG RESTORE       - Restore from backup
            CONFIG RESET         - Reset to defaults
            CONFIG VALIDATE      - Validate all configs
            CONFIG VIEWPORT      - Show viewport information
            CONFIG VIEWPORT <w> <h> - Set custom viewport (in cells)

        Manages configuration files in data/system/ directory.
        """
        if not params:
            return self._show_config_status()

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
        else:
            return ("❌ Unknown config command\n\n"
                   "Available commands:\n"
                   "  CONFIG BACKUP    - Backup configurations\n"
                   "  CONFIG RESTORE   - Restore from backup\n"
                   "  CONFIG RESET     - Reset to defaults\n"
                   "  CONFIG VALIDATE  - Validate configurations\n"
                   "  CONFIG VIEWPORT  - Manage viewport settings")

    def _show_config_status(self):
        """Show current configuration status."""
        config_dir = Path('data/system')
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
            config_dir = Path('data/system')
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

            config_dir = Path('data/system')
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
               "2. Restore from templates in data/templates/\n"
               "3. Or reinstall uDOS")

    def _validate_configs(self):
        """Validate all configuration files."""
        config_dir = Path('data/system')
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
                "💾 Settings saved to data/system/viewport.json",
                "💡 Use: REBOOT to apply changes fully",
                "💡 Use: CONFIG VIEWPORT to view current settings"
            ]

            return "\n".join(output)

        except ImportError:
            return "❌ Viewport manager not available"
        except Exception as e:
            return f"❌ Error setting viewport config: {str(e)}"
