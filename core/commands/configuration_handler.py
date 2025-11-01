"""
uDOS v1.0.0 - Configuration Handler

Handles configuration management operations:
- Settings display and modification
- Theme switching and configuration
- Configuration file management
- User preferences
"""

import json
import shutil
from pathlib import Path
from .base_handler import BaseCommandHandler


class ConfigurationHandler(BaseCommandHandler):
    """Handles configuration and settings management operations."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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
            user_profile = self.user_manager.user_data.get('USER_PROFILE', {})
            output.append(f"  Name: {user_profile.get('NAME', 'Not set')}")
            output.append(f"  Location: {user_profile.get('LOCATION', 'Not set')}")
            output.append(f"  Timezone: {user_profile.get('TIMEZONE', 'UTC')}")
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
        Manage color themes.

        Usage:
            THEME               - Show current theme
            THEME LIST          - List available themes
            THEME <name>        - Switch to theme
            THEME BACKUP        - Backup current theme
            THEME RESTORE       - Restore from backup

        Available themes are in data/themes/ directory.
        """
        if not params:
            return self._show_current_theme()

        command = params[0].upper()

        if command == 'LIST':
            return self._list_themes()
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

    def _list_themes(self):
        """List all available themes."""
        themes_dir = Path('data/themes')
        if not themes_dir.exists():
            return "❌ Themes directory not found"

        theme_files = list(themes_dir.glob('*.json'))
        if not theme_files:
            return "❌ No themes found in data/themes/"

        output = []
        output.append("🎨 AVAILABLE THEMES")
        output.append("=" * 50)

        current_theme = getattr(self.theme, 'name', '') if self.theme else ''

        for theme_file in sorted(theme_files):
            theme_name = theme_file.stem

            try:
                with open(theme_file, 'r') as f:
                    theme_data = json.load(f)

                description = theme_data.get('THEME', {}).get('DESCRIPTION', 'No description')
                version = theme_data.get('THEME', {}).get('VERSION', '1.0')

                # Mark current theme
                marker = " ← CURRENT" if theme_name == current_theme else ""

                output.append(f"  {theme_name.ljust(20)} v{version} - {description}{marker}")

            except Exception as e:
                output.append(f"  {theme_name.ljust(20)} (error loading)")

        output.append("")
        output.append("💡 Use: THEME <name> to switch to a theme")
        output.append("💡 Use: THEME BACKUP to save current settings")

        return "\n".join(output)

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
        Manage configuration files.

        Usage:
            CONFIG               - Show config status
            CONFIG BACKUP        - Backup all configs
            CONFIG RESTORE       - Restore from backup
            CONFIG RESET         - Reset to defaults
            CONFIG VALIDATE      - Validate all configs

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
        else:
            return ("❌ Unknown config command\n\n"
                   "Available commands:\n"
                   "  CONFIG BACKUP    - Backup configurations\n"
                   "  CONFIG RESTORE   - Restore from backup\n"
                   "  CONFIG RESET     - Reset to defaults\n"
                   "  CONFIG VALIDATE  - Validate configurations")

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
