"""
uDOS v1.1.12 - Variable Command Handler

Handles variable operations: GET, SET, HISTORY
Manages STORY fields, CONFIG settings, and SYSTEM values.
"""

from .base_handler import BaseCommandHandler


class VariableHandler(BaseCommandHandler):
    """Handler for variable get/set/history commands."""

    def handle_get(self, params, grid, parser):
        """
        GET field value from story/config/system interactively or explicitly.

        Usage:
            GET                          → Interactive field browser
            GET USER_NAME                → Get STORY.USER_NAME (shorthand)
            GET STORY.USER_NAME          → Get story field (explicit)
            GET CONFIG.GEMINI_API_KEY    → Get config field
            GET SYSTEM.THEME             → Get system setting

        Returns:
            Field value or interactive picker result
        """
        if not params:
            # Interactive mode - show field browser
            field_categories = [
                "User Profile (name, location, timezone)",
                "System Settings (theme, viewport)",
                "All Fields"
            ]

            choice = self.input_manager.prompt_choice(
                "What would you like to view?",
                choices=field_categories
            )

            if "User" in choice:
                # Show user profile fields
                user_name = self.story_manager.get_field('STORY.USER_NAME', 'Not set')
                password = self.story_manager.get_field('STORY.PASSWORD', '')
                location = self.story_manager.get_field('STORY.LOCATION', 'Not set')
                timezone = self.story_manager.get_field('STORY.TIMEZONE', 'UTC')

                password_display = '●●●●●●' if password else 'Not set'

                profile = {
                    'Username': user_name,
                    'Password': password_display,
                    'Location': location,
                    'Timezone': timezone
                }
                return self.output_formatter.format_panel(
                    "User Profile",
                    self.output_formatter.format_key_value(profile)
                )
            elif "System" in choice:
                # Show system settings
                theme = self.story_manager.get_field('STORY.THEME', 'dungeon')
                settings = {
                    'Theme': theme,
                    'Viewport': f"{self.viewport.width}×{self.viewport.height}" if self.viewport else "Unknown",
                    'Connection': self.connection.get_mode() if self.connection else "Unknown"
                }
                return self.output_formatter.format_panel(
                    "System Settings",
                    self.output_formatter.format_key_value(settings)
                )
            else:
                # Browse all fields
                user_name = self.story_manager.get_field('STORY.USER_NAME', 'Not set')
                password = self.story_manager.get_field('STORY.PASSWORD', '')
                location = self.story_manager.get_field('STORY.LOCATION', 'Not set')
                timezone = self.story_manager.get_field('STORY.TIMEZONE', 'UTC')
                theme = self.story_manager.get_field('STORY.THEME', 'dungeon')

                password_display = '●●●●●●' if password else 'Not set'

                all_fields = {
                    'Username': user_name,
                    'Password': password_display,
                    'Location': location,
                    'Timezone': timezone,
                    'Theme': theme,
                    'Viewport': f"{self.viewport.width}×{self.viewport.height}" if self.viewport else "Unknown"
                }
                return self.output_formatter.format_panel(
                    "All Fields",
                    self.output_formatter.format_key_value(all_fields)
                )

        # Explicit mode - get specific field
        field_path = params[0].upper()

        # Smart shorthand: if no dot, assume STORY prefix
        if '.' not in field_path:
            field_path = f"STORY.{field_path}"

        # Parse field source (STORY.*, CONFIG.*, SYSTEM.*)
        source, *path_parts = field_path.split('.')
        remaining_path = '.'.join(path_parts)

        if source == 'STORY':
            value = self.story_manager.get_field(field_path, default="<not set>")
            # Mask password display
            if 'PASSWORD' in field_path.upper() and value != "<not set>":
                value = '●●●●●●' if value else '<not set>'
            return f"{field_path} = {value}"
        elif source == 'SYSTEM':
            # System settings
            system_fields = {
                'THEME': self.story_manager.get_field('STORY.THEME', 'dungeon'),
                'VIEWPORT.WIDTH': self.viewport.width if self.viewport else None,
                'VIEWPORT.HEIGHT': self.viewport.height if self.viewport else None,
            }
            value = system_fields.get(remaining_path, "<unknown field>")
            return f"{field_path} = {value}"
        elif source == 'CONFIG':
            # Delegate to CONFIG GET
            from .system_handler import SystemCommandHandler
            system_handler = SystemCommandHandler(**self.__dict__)
            return system_handler.handle_config(['get', remaining_path], grid, parser)
        else:
            return self.output_formatter.format_error(
                f"Unknown field source: {source}",
                "Valid sources: STORY, SYSTEM, CONFIG\n" +
                "💡 Tip: Just use field name for STORY fields (e.g., GET USER_NAME)"
            )

    def handle_set(self, params, grid, parser):
        """
        SET field value in story/config/system interactively or explicitly.

        Usage:
            SET                                    → Interactive setter
            SET USER_NAME Fred                     → Set STORY.USER_NAME (shorthand)
            SET STORY.USER_NAME "Fred"             → Set story field (explicit)
            SET STORY.THEME dungeon                → Set story field
            SET CONFIG.OFFLINE_MODE true           → Set config

        Returns:
            Success message or error
        """
        if not params:
            # Interactive mode
            field_path = self.input_manager.prompt_user(
                "Field to set (e.g., USER_NAME or STORY.USER_NAME)",
                required=True
            )

            if not field_path:
                return self.output_formatter.format_warning("Operation cancelled")

            # Smart shorthand: if no dot, assume STORY prefix
            if '.' not in field_path.upper():
                field_path = f"STORY.{field_path.upper()}"

            value = self.input_manager.prompt_user(
                f"New value for {field_path}",
                required=True
            )

            if not value:
                return self.output_formatter.format_warning("Operation cancelled")

            params = [field_path, value]

        if len(params) < 2:
            return self.output_formatter.format_error(
                "Missing value",
                "Usage: SET FIELD value\n" +
                "💡 Tip: Just use field name for STORY fields (e.g., SET USER_NAME Fred)"
            )

        field_path = params[0].upper()
        value = ' '.join(params[1:])  # Join remaining params as value

        # Remove quotes if present
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1]

        # Smart shorthand: if no dot, assume STORY prefix
        if '.' not in field_path:
            field_path = f"STORY.{field_path}"

        # Parse field source
        source, *path_parts = field_path.split('.')
        remaining_path = '.'.join(path_parts)

        if source == 'STORY':
            # Set story field
            success = self.story_manager.set_field(field_path, value, auto_save=True)

            if success:
                # Don't show password in output
                display_value = '●●●●●●' if 'PASSWORD' in field_path else value
                return self.output_formatter.format_success(
                    f"Story field updated: {field_path} = {display_value}",
                    details=f"Saved to: {self.story_manager.story_path}"
                )
            else:
                return self.output_formatter.format_error(
                    "Failed to update story field"
                )
        elif source == 'CONFIG':
            # Delegate to CONFIG SET
            from .system_handler import SystemCommandHandler
            system_handler = SystemCommandHandler(**self.__dict__)
            return system_handler.handle_config(['set', remaining_path, value], grid, parser)
        elif source == 'SYSTEM':
            return self.output_formatter.format_warning(
                "System fields are read-only",
                "Use CONFIG or SETTINGS to modify system settings"
            )
        else:
            return self.output_formatter.format_error(
                f"Unknown field source: {source}",
                "Valid sources: STORY, CONFIG\n" +
                "💡 Tip: Just use field name for STORY fields (e.g., SET USER_NAME Fred)"
            )

    def handle_history(self, params, grid, parser):
        """
        Show variable change history.

        Usage:
            HISTORY <variable>              - Show all changes to variable
            HISTORY <variable> <n>          - Show last N changes
            HISTORY CLEAR <variable>        - Clear history for variable
            HISTORY CLEAR ALL               - Clear all history

        Args:
            params: Command parameters
            grid: Grid instance
            parser: Parser instance

        Returns:
            Variable history
        """
        if not hasattr(parser, 'ucode') or not parser.ucode:
            return "❌ uCODE interpreter not available"

        debugger = parser.ucode.debugger

        if not params:
            return "❌ Usage: HISTORY <variable> [n] or HISTORY CLEAR [variable|ALL]"

        if params[0].upper() == 'CLEAR':
            if len(params) < 2:
                return "❌ Usage: HISTORY CLEAR <variable> or HISTORY CLEAR ALL"

            if params[1].upper() == 'ALL':
                debugger.clear_variable_history()
                return "✅ All variable history cleared"
            else:
                var_name = params[1]
                debugger.clear_variable_history(var_name)
                return f"✅ History cleared for variable: {var_name}"

        var_name = params[0]
        history = debugger.get_variable_history(var_name)

        if not history:
            return f"ℹ️  No history for variable: {var_name}"

        # Limit number of entries if specified
        limit = None
        if len(params) > 1:
            try:
                limit = int(params[1])
            except ValueError:
                return f"❌ Invalid number: {params[1]}"

        entries = history[-limit:] if limit else history

        output = "╔════════════════════════════════════════════════════════════════════════╗\n"
        output += f"║                   VARIABLE HISTORY: {var_name:<44} ║\n"
        output += "╠════════════════════════════════════════════════════════════════════════╣\n"

        for entry in entries:
            line = entry['line']
            old_val = entry['old_value']
            new_val = entry['new_value']
            timestamp = entry['timestamp'][:19]  # Strip microseconds

            output += f"║  Line {line:<4}  {old_val!r:<20} → {new_val!r:<20} {timestamp:<14} ║\n"

        output += "╚════════════════════════════════════════════════════════════════════════╝"
        return output
