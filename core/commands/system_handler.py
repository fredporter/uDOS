"""
uDOS v1.0.0 - System Command Handler (Modular)

Handles system administration commands by delegating to specialized handlers:
- REPAIR: Delegates to RepairHandler for comprehensive diagnostics and maintenance
- STATUS, DASHBOARD, VIEWPORT, PALETTE: Delegates to DashboardHandler
- SETTINGS, CONFIG: Delegates to ConfigurationHandler
- REBOOT, DESTROY: Core system commands handled directly
"""

import os
import sys
import json
import shutil
from pathlib import Path
from .base_handler import BaseCommandHandler


class SystemCommandHandler(BaseCommandHandler):
    """Modular system administration handler with specialized delegation."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Import services only when needed (lazy loading)
        self._startup_module = None
        self._settings_manager = None
        self._workspace_manager = None
        self._config_manager = None
        self._help_manager = None

    @property
    def startup(self):
        """Lazy load startup module."""
        if self._startup_module is None:
            from core import uDOS_startup
            self._startup_module = uDOS_startup
        return self._startup_module

    @property
    def settings_manager(self):
        """Lazy load settings manager."""
        if self._settings_manager is None:
            from core.services.settings_manager import SettingsManager
            self._settings_manager = SettingsManager()
        return self._settings_manager

    @property
    def workspace_manager(self):
        """Lazy load workspace manager."""
        if self._workspace_manager is None:
            from core.services.workspace_manager import WorkspaceManager
            self._workspace_manager = WorkspaceManager()
        return self._workspace_manager

    @property
    def config_manager(self):
        """Lazy load config manager."""
        if self._config_manager is None:
            from core.services.config_manager import ConfigManager
            self._config_manager = ConfigManager()
        return self._config_manager

    @property
    def help_manager(self):
        """Lazy load help manager."""
        if self._help_manager is None:
            from core.services.help_manager import HelpManager
            self._help_manager = HelpManager()
        return self._help_manager

    def handle(self, command, params, grid, parser):
        """
        Route system commands to appropriate handlers.

        Args:
            command: Command name (e.g., 'REPAIR', 'STATUS')
            params: List of command parameters
            grid: Grid instance
            parser: Parser instance

        Returns:
            Command result string
        """
        # Map commands to handler methods
        handlers = {
            'BLANK': self.handle_blank,
            'HELP': self.handle_help,
            'HISTORY': self.handle_history,
            'UNDO': self.handle_undo,
            'REDO': self.handle_redo,
            'RESTORE': self.handle_restore,
            'THEME': self.handle_theme,
            'PROGRESS': self.handle_progress,
            'SESSION': self.handle_session,
            'LAYOUT': self.handle_layout,
            'STATUS': self.handle_status,
            'REPAIR': self.handle_repair,
            'REBOOT': self.handle_reboot,
            'DESTROY': self.handle_destroy,
            'VIEWPORT': self.handle_viewport,
            'PALETTE': self.handle_palette,
            'DASH': self.handle_dashboard,
            'DASHBOARD': self.handle_dashboard,
            'TREE': self.handle_tree,
            'CLEAN': self.handle_clean,
            'CONFIG': self.handle_config,
            'SETTINGS': self.handle_settings,
            'SETUP': self.handle_setup,
            'WORKSPACE': self.handle_workspace,
            'OUTPUT': self.handle_output,
            'SERVER': self.handle_output,  # Alias for OUTPUT
        }

        handler = handlers.get(command)
        if handler:
            return handler(params, grid, parser)
        else:
            return self.get_message("ERROR_UNKNOWN_SYSTEM_COMMAND", command=command)

    def handle_blank(self, params, grid, parser):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
        return self.get_message("ACTION_SUCCESS_SCREEN_CLEARED")

    def handle_help(self, params, grid, parser):
        """
        Display help information with enhanced features.

        Supports:
        - HELP: List all commands by category
        - HELP <command>: Detailed help for specific command
        - HELP SEARCH <query>: Search help content
        - HELP CATEGORY <category>: Filter by category
        - HELP RECENT: Show recently used commands (if usage tracker available)

        Args:
            params: List with optional command/subcommand
            grid: Grid instance (unused)
            parser: Parser instance (unused)

        Returns:
            Formatted help text
        """
        # Handle subcommands
        if params and len(params) >= 2:
            subcommand = params[0].upper()

            # HELP SEARCH <query>
            if subcommand == 'SEARCH':
                query = ' '.join(params[1:])
                return self.help_manager.format_search_results(query)

            # HELP CATEGORY <category>
            elif subcommand == 'CATEGORY':
                category = ' '.join(params[1:])
                return self.help_manager.format_help_category(category)

            # HELP RECENT (placeholder for future usage tracker integration)
            elif subcommand == 'RECENT':
                return ("╔═══════════════════════════════════════════════════════════════════════════════╗\n"
                       "║  📊 Recently Used Commands                                                    ║\n"
                       "╠═══════════════════════════════════════════════════════════════════════════════╣\n"
                       "║  ⚠️  Usage tracking not yet implemented                                        ║\n"
                       "║                                                                               ║\n"
                       "║  This feature will be available when UsageTracker service is integrated.     ║\n"
                       "╚═══════════════════════════════════════════════════════════════════════════════╝\n")

        # HELP ALL or no params: Show all commands by category
        if not params or params[0].upper() == 'ALL':
            help_text = "╔" + "═"*78 + "╗\n"
            help_text += "║" + " "*26 + "📚 uDOS COMMAND REFERENCE" + " "*27 + "║\n"
            help_text += "╠" + "═"*78 + "╣\n"

            # Display commands by category
            for category, commands in self.help_manager.categories.items():
                if not commands:
                    continue

                help_text += "║ " + category.ljust(77) + "║\n"
                help_text += "║ " + "─"*77 + "║\n"

                for cmd_name in sorted(commands):
                    cmd_data = self.help_manager.get_command_details(cmd_name)
                    if cmd_data:
                        desc = cmd_data.get('DESCRIPTION', '')[:56]
                        help_text += f"║  {cmd_name:<18} - {desc.ljust(56)}║\n"

                help_text += "║" + " "*78 + "║\n"

            # Footer with enhanced hints
            help_text += "╠" + "═"*78 + "╣\n"
            help_text += "║  💡 HELP <command>           - Detailed help for a command".ljust(79) + "║\n"
            help_text += "║  🔍 HELP SEARCH <query>      - Search commands".ljust(79) + "║\n"
            help_text += "║  📁 HELP CATEGORY <name>     - Filter by category".ljust(79) + "║\n"
            help_text += "║  📖 Full docs: https://github.com/fredporter/uDOS/wiki".ljust(79) + "║\n"
            help_text += "╚" + "═"*78 + "╝\n"

            return help_text

        # HELP <command>: Show detailed help for specific command
        else:
            cmd_name = params[0].upper()
            return self.help_manager.format_help_detailed(cmd_name)

    def handle_history(self, params, grid, parser):
        """
        Command history management with search and statistics.

        Subcommands:
        - HISTORY SEARCH <query>   # Search command history
        - HISTORY STATS           # Show usage statistics
        - HISTORY CLEAR [days]    # Clear history (optional: older than X days)
        - HISTORY EXPORT <file>   # Export history to file
        - HISTORY RECENT [count]  # Show recent commands

        Args:
            params: List of command parameters
            grid: Grid instance (unused)
            parser: Parser instance (unused)

        Returns:
            Formatted history information
        """
        # Use the command history from the base class
        if self.command_history is None:
            return "❌ Command history system not available"

        try:
            history = self.command_history
            # Test if it's working by trying to access a method
            _ = len(history)
        except Exception as e:
            return f"❌ Command history system error: {e}"

        if not params:
            # Default: show recent commands
            return self._show_recent_history(history, 10)

        subcommand = params[0].upper()

        if subcommand == "SEARCH":
            if len(params) < 2:
                return "❌ Usage: HISTORY SEARCH <query>"
            query = " ".join(params[1:])
            return self._search_history(history, query)

        elif subcommand == "STATS":
            return self._show_history_stats(history)

        elif subcommand == "CLEAR":
            days = None
            if len(params) > 1:
                try:
                    days = int(params[1])
                except ValueError:
                    return "❌ Invalid days parameter. Use: HISTORY CLEAR [days]"
            return self._clear_history(history, days)

        elif subcommand == "EXPORT":
            if len(params) < 2:
                return "❌ Usage: HISTORY EXPORT <filename>"
            filename = params[1]
            return self._export_history(history, filename)

        elif subcommand == "RECENT":
            count = 10  # Default
            if len(params) > 1:
                try:
                    count = int(params[1])
                    count = max(1, min(count, 100))  # Limit between 1-100
                except ValueError:
                    return "❌ Invalid count parameter. Use: HISTORY RECENT [count]"
            return self._show_recent_history(history, count)

        else:
            return f"❌ Unknown history subcommand: {subcommand}\n💡 Use: HELP HISTORY for usage information"

    def _show_recent_history(self, history, count):
        """Show recent command history."""
        try:
            # Get recent commands from cache
            recent = list(history)[:count]
            if not recent:
                return "📜 No command history available"

            result = f"📜 Recent Commands (last {len(recent)}):\n"
            result += "┌" + "─" * 78 + "┐\n"

            for i, cmd in enumerate(recent, 1):
                # Truncate long commands
                display_cmd = cmd if len(cmd) <= 70 else cmd[:67] + "..."
                result += f"│ {i:2d}. {display_cmd:<70} │\n"

            result += "└" + "─" * 78 + "┘\n"
            result += f"💡 Use 'HISTORY SEARCH <term>' to find specific commands"
            return result

        except Exception as e:
            return f"❌ Error retrieving history: {e}"

    def _search_history(self, history, query):
        """Search command history with relevance scoring."""
        try:
            results = history.search_history(query, limit=15)
            if not results:
                return f"🔍 No commands found matching '{query}'"

            result = f"🔍 Search results for '{query}' ({len(results)} found):\n"
            result += "┌" + "─" * 78 + "┐\n"

            for i, (cmd, score, freq) in enumerate(results, 1):
                # Truncate and show relevance info
                display_cmd = cmd if len(cmd) <= 55 else cmd[:52] + "..."
                score_str = f"{score:.2f}"
                freq_str = f"used {freq}x"
                result += f"│ {i:2d}. {display_cmd:<55} │ {score_str} │ {freq_str:<8} │\n"

            result += "└" + "─" * 78 + "┘\n"
            result += f"💡 Score: relevance (0.0-1.0), Frequency: usage count"
            return result

        except Exception as e:
            return f"❌ Error searching history: {e}"

    def _show_history_stats(self, history):
        """Show command usage statistics."""
        try:
            stats = history.get_command_stats()

            result = "📊 Command History Statistics:\n"
            result += "┌" + "─" * 78 + "┐\n"
            result += f"│ Total Commands:     {stats['total_commands']:<10} │ Unique Commands:   {stats['unique_commands']:<10} │\n"
            result += f"│ Recent Activity:    {stats['recent_activity']:<10} │ Database Size:     {'~' + str(stats['total_commands'] * 100) + 'B':<10} │\n"
            result += "├" + "─" * 78 + "┤\n"
            result += "│ Top Command Types:" + " " * 58 + "│\n"

            for cmd_type, count in stats['top_command_types']:
                result += f"│   {cmd_type:<20} {count:<10} times" + " " * 42 + "│\n"

            result += "└" + "─" * 78 + "┘\n"
            result += f"📁 Database: {stats['database_path']}"
            return result

        except Exception as e:
            return f"❌ Error retrieving statistics: {e}"

    def _clear_history(self, history, days):
        """Clear command history."""
        try:
            if days:
                deleted = history.clear_history(older_than_days=days)
                return f"🗑️  Cleared {deleted} commands older than {days} days"
            else:
                # Confirm total clear
                deleted = history.clear_history()
                return f"🗑️  Cleared all command history ({deleted} commands removed)"

        except Exception as e:
            return f"❌ Error clearing history: {e}"

    def _export_history(self, history, filename):
        """Export command history to file."""
        try:
            # Determine format from extension
            if filename.endswith('.json'):
                format_type = 'json'
            elif filename.endswith('.txt'):
                format_type = 'txt'
            else:
                format_type = 'txt'  # Default
                filename += '.txt'

            # Create export path in memory/logs/
            export_path = Path("memory/logs") / filename
            export_path.parent.mkdir(parents=True, exist_ok=True)

            success = history.export_history(str(export_path), format_type)
            if success:
                return f"📤 History exported to: {export_path}"
            else:
                return f"❌ Failed to export history to {export_path}"

        except Exception as e:
            return f"❌ Error exporting history: {e}"

    def handle_theme(self, params, grid, parser):
        """
        Advanced theme management with accessibility features.

        Subcommands:
        - THEME LIST              # List available themes
        - THEME SET <name>        # Set active theme
        - THEME INFO              # Show current theme info
        - THEME ACCESSIBILITY ON|OFF  # Toggle accessibility mode
        - THEME CONTRAST ON|OFF   # Toggle high contrast mode
        - THEME COLORBLIND <type> # Set colorblind support
        - THEME CREATE <name>     # Create custom theme (interactive)

        Args:
            params: List of command parameters
            grid: Grid instance (unused)
            parser: Parser instance (unused)

        Returns:
            Formatted theme information
        """
        # Initialize theme manager
        try:
            from core.services.theme_manager import ThemeManager, ThemeMode
            theme_manager = ThemeManager()
            theme_manager.load_settings()
        except Exception as e:
            return f"❌ Error accessing theme system: {e}"

        if not params:
            # Default: show current theme info
            return self._show_theme_info(theme_manager)

        subcommand = params[0].upper()

        if subcommand == "LIST":
            return self._list_themes(theme_manager)

        elif subcommand == "SET":
            if len(params) < 2:
                return "❌ Usage: THEME SET <theme_name>"
            theme_name = params[1].lower()
            return self._set_theme(theme_manager, theme_name)

        elif subcommand == "INFO":
            return self._show_theme_info(theme_manager)

        elif subcommand == "ACCESSIBILITY":
            if len(params) < 2:
                return "❌ Usage: THEME ACCESSIBILITY ON|OFF"
            enable = params[1].upper() == "ON"
            return self._toggle_accessibility(theme_manager, enable)

        elif subcommand == "CONTRAST":
            if len(params) < 2:
                return "❌ Usage: THEME CONTRAST ON|OFF"
            enable = params[1].upper() == "ON"
            return self._toggle_contrast(theme_manager, enable)

        elif subcommand == "COLORBLIND":
            if len(params) < 2:
                return "❌ Usage: THEME COLORBLIND <type|off>\n💡 Types: deuteranopia, protanopia, tritanopia"
            cb_type = params[1].lower() if params[1].lower() != "off" else None
            return self._set_colorblind_support(theme_manager, cb_type)

        elif subcommand == "CREATE":
            if len(params) < 2:
                return "❌ Usage: THEME CREATE <name>"
            name = params[1]
            return self._create_custom_theme(theme_manager, name)

        else:
            return f"❌ Unknown theme subcommand: {subcommand}\n💡 Use: HELP THEME for usage information"

    def _show_theme_info(self, theme_manager):
        """Show current theme information."""
        try:
            info = theme_manager.get_theme_info()
            scheme = theme_manager.get_current_scheme()

            result = theme_manager.format_text("🎨 Current Theme Information", "accent") + "\n"
            result += "┌" + "─" * 60 + "┐\n"
            result += f"│ Active Theme:     {theme_manager.format_text(info['current_mode'], 'primary'):<45} │\n"
            result += f"│ Accessibility:    {theme_manager.format_text('ON' if info['accessibility_mode'] else 'OFF', 'success' if info['accessibility_mode'] else 'text_muted'):<45} │\n"
            result += f"│ High Contrast:    {theme_manager.format_text('ON' if info['high_contrast_mode'] else 'OFF', 'success' if info['high_contrast_mode'] else 'text_muted'):<45} │\n"
            result += f"│ Colorblind Mode:  {theme_manager.format_text(info['colorblind_mode'] or 'OFF', 'info' if info['colorblind_mode'] else 'text_muted'):<45} │\n"
            result += f"│ Custom Themes:    {theme_manager.format_text(str(info['custom_themes_count']), 'secondary'):<45} │\n"
            result += "└" + "─" * 60 + "┘\n"

            # Show color preview
            result += "\n" + theme_manager.format_text("🌈 Color Preview", "accent") + "\n"
            result += "┌" + "─" * 60 + "┐\n"
            result += f"│ Primary:    {theme_manager.format_text('Sample Text', 'primary'):<45} │\n"
            result += f"│ Secondary:  {theme_manager.format_text('Sample Text', 'secondary'):<45} │\n"
            result += f"│ Success:    {theme_manager.format_text('Sample Text', 'success'):<45} │\n"
            result += f"│ Warning:    {theme_manager.format_text('Sample Text', 'warning'):<45} │\n"
            result += f"│ Error:      {theme_manager.format_text('Sample Text', 'error'):<45} │\n"
            result += "└" + "─" * 60 + "┘"

            return result

        except Exception as e:
            return f"❌ Error retrieving theme info: {e}"

    def _list_themes(self, theme_manager):
        """List all available themes."""
        try:
            themes = theme_manager.list_available_themes()
            current_mode = theme_manager.current_mode.value

            result = theme_manager.format_text("🎨 Available Themes", "accent") + "\n"
            result += "┌" + "─" * 70 + "┐\n"

            for theme_id, description in themes.items():
                is_active = theme_id == current_mode or (current_mode == "custom" and theme_id.startswith("custom-"))
                marker = "→" if is_active else " "
                status = theme_manager.format_text("ACTIVE", "success") if is_active else ""

                result += f"│ {marker} {theme_id:<20} │ {description:<30} │ {status:<8} │\n"

            result += "└" + "─" * 70 + "┘\n"
            result += theme_manager.format_text("💡 Use 'THEME SET <name>' to switch themes", "info")

            return result

        except Exception as e:
            return f"❌ Error listing themes: {e}"

    def _set_theme(self, theme_manager, theme_name):
        """Set the active theme."""
        try:
            # Handle theme name mapping
            theme_mapping = {
                'classic': ThemeMode.CLASSIC,
                'cyberpunk': ThemeMode.CYBERPUNK,
                'accessibility': ThemeMode.ACCESSIBILITY,
                'monochrome': ThemeMode.MONOCHROME
            }

            if theme_name in theme_mapping:
                success = theme_manager.set_theme(theme_mapping[theme_name])
                if success:
                    return theme_manager.format_text(f"✅ Theme switched to: {theme_name}", "success")
                else:
                    return theme_manager.format_text(f"❌ Failed to set theme: {theme_name}", "error")
            elif theme_name.startswith('custom-'):
                custom_name = theme_name[7:]  # Remove 'custom-' prefix
                if custom_name in theme_manager.custom_themes:
                    theme_manager.current_mode = ThemeMode.CUSTOM
                    return theme_manager.format_text(f"✅ Custom theme activated: {custom_name}", "success")
                else:
                    return theme_manager.format_text(f"❌ Custom theme not found: {custom_name}", "error")
            else:
                available = ", ".join(theme_manager.list_available_themes().keys())
                return f"❌ Unknown theme: {theme_name}\n💡 Available: {available}"

        except Exception as e:
            return f"❌ Error setting theme: {e}"

    def _toggle_accessibility(self, theme_manager, enable):
        """Toggle accessibility mode."""
        try:
            theme_manager.enable_accessibility_mode(enable)
            status = theme_manager.format_text("enabled", "success") if enable else theme_manager.format_text("disabled", "text_muted")
            return f"♿ Accessibility mode {status}"
        except Exception as e:
            return f"❌ Error toggling accessibility: {e}"

    def _toggle_contrast(self, theme_manager, enable):
        """Toggle high contrast mode."""
        try:
            theme_manager.enable_high_contrast_mode(enable)
            status = theme_manager.format_text("enabled", "success") if enable else theme_manager.format_text("disabled", "text_muted")
            return f"🔆 High contrast mode {status}"
        except Exception as e:
            return f"❌ Error toggling contrast: {e}"

    def _set_colorblind_support(self, theme_manager, cb_type):
        """Set colorblind support mode."""
        try:
            success = theme_manager.set_colorblind_support(cb_type)
            if success:
                if cb_type:
                    return theme_manager.format_text(f"👁️ Colorblind support enabled: {cb_type}", "success")
                else:
                    return theme_manager.format_text("👁️ Colorblind support disabled", "text_muted")
            else:
                return theme_manager.format_text("❌ Invalid colorblind type", "error") + "\n💡 Valid types: deuteranopia, protanopia, tritanopia"
        except Exception as e:
            return f"❌ Error setting colorblind support: {e}"

    def _create_custom_theme(self, theme_manager, name):
        """Create a custom theme (simplified for now)."""
        try:
            # For now, create a sample custom theme based on current theme
            current_scheme = theme_manager.get_current_scheme()
            success = theme_manager.create_custom_theme(name, current_scheme)

            if success:
                return theme_manager.format_text(f"🎨 Custom theme created: {name}", "success") + "\n💡 Use 'THEME SET custom-{name}' to activate"
            else:
                return theme_manager.format_text(f"❌ Failed to create theme: {name}", "error")
        except Exception as e:
            return f"❌ Error creating custom theme: {e}"

    def handle_progress(self, params, grid, parser):
        """
        Progress indicator testing and management commands.

        Subcommands:
        - PROGRESS TEST               # Test basic progress indicator
        - PROGRESS TEST MULTI         # Test multi-stage progress
        - PROGRESS TEST SEARCH        # Test file search with progress
        - PROGRESS LIST               # List active progress indicators
        - PROGRESS CANCEL [id]        # Cancel active progress (or all)
        - PROGRESS DEMO               # Full demo of all progress types

        Args:
            params: List of command parameters
            grid: Grid instance (unused)
            parser: Parser instance (unused)

        Returns:
            Formatted progress information or demo results
        """
        if not params:
            # Default: show active progress indicators
            return self._show_active_progress()

        subcommand = params[0].upper()

        if subcommand == "TEST":
            if len(params) > 1 and params[1].upper() == "MULTI":
                return self._test_multi_stage_progress()
            elif len(params) > 1 and params[1].upper() == "SEARCH":
                return self._test_search_progress()
            else:
                return self._test_basic_progress()

        elif subcommand == "LIST":
            return self._list_active_progress()

        elif subcommand == "CANCEL":
            progress_id = params[1] if len(params) > 1 else None
            return self._cancel_progress(progress_id)

        elif subcommand == "DEMO":
            return self._run_progress_demo()

        else:
            return f"❌ Unknown progress subcommand: {subcommand}\n💡 Use: HELP PROGRESS for usage information"

    def _show_active_progress(self):
        """Show current active progress indicators."""
        try:
            from core.services.progress_manager import progress_manager

            active_count = progress_manager.get_active_count()
            if active_count == 0:
                return "📊 No active progress indicators\n💡 Use: PROGRESS TEST to test progress features"

            result = [f"📊 Active Progress Indicators ({active_count})"]
            result.append("=" * 50)

            for task_id, indicator in progress_manager.indicators.items():
                if indicator.status == "running":
                    elapsed = indicator.last_update - indicator.start_time
                    result.append(f"• {task_id}: {indicator.description}")
                    result.append(f"  Status: {indicator.status} | Elapsed: {elapsed}")
                    if indicator.total:
                        percentage = (indicator.current / indicator.total * 100) if indicator.total > 0 else 0
                        result.append(f"  Progress: {indicator.current}/{indicator.total} ({percentage:.1f}%)")

            result.append("\n💡 Use: PROGRESS CANCEL to stop all progress")
            return "\n".join(result)

        except Exception as e:
            return f"❌ Error checking progress: {e}"

    def _test_basic_progress(self):
        """Test basic progress indicator."""
        import threading
        import time

        try:
            from core.services.progress_manager import progress_manager, ProgressConfig

            # Create a simple progress test
            config = ProgressConfig(show_time_estimate=True, show_percentage=True)
            progress = progress_manager.create_progress(
                "test_basic",
                "Testing basic progress indicator",
                100,
                config
            )

            def test_work():
                progress.start()
                for i in range(101):
                    time.sleep(0.05)  # Simulate work
                    progress.update(i, f"Processing item {i}")
                    if progress.cancelled:
                        break
                progress.complete("Basic test completed!")

                # Clean up after a delay
                time.sleep(3)
                progress_manager.remove_progress("test_basic")

            # Start test in background
            threading.Thread(target=test_work, daemon=True).start()

            return "🚀 Started basic progress test (100 items, 5 seconds)\n👀 Watch the progress indicator above\n💡 Use Ctrl+C to cancel"

        except Exception as e:
            return f"❌ Error starting progress test: {e}"

    def _test_multi_stage_progress(self):
        """Test multi-stage progress indicator."""
        import threading
        import time

        try:
            from core.services.progress_manager import progress_manager, ProgressConfig

            stages = ["Initialization", "Data Processing", "Analysis", "Finalization"]
            config = ProgressConfig(show_time_estimate=True, width=30)

            multi_progress = progress_manager.create_multi_stage_progress(
                "test_multi",
                stages,
                config
            )

            def test_multi_work():
                for stage_idx, stage_name in enumerate(stages):
                    items_in_stage = 50 + (stage_idx * 10)  # Variable stage lengths
                    multi_progress.start_stage(stage_idx, stage_name, items_in_stage)

                    for i in range(items_in_stage + 1):
                        time.sleep(0.02)  # Simulate work
                        multi_progress.update_stage(i, f"{stage_name}: item {i}")

                        # Check for cancellation
                        if multi_progress.current_indicator and multi_progress.current_indicator.cancelled:
                            return

                    multi_progress.complete_stage(f"{stage_name} completed")
                    time.sleep(0.5)  # Brief pause between stages

                multi_progress.complete("All stages completed successfully!")

                # Clean up after delay
                time.sleep(3)
                progress_manager.remove_progress("test_multi")

            # Start test in background
            threading.Thread(target=test_multi_work, daemon=True).start()

            return f"🚀 Started multi-stage progress test ({len(stages)} stages)\n👀 Watch the progress indicators above\n💡 Use Ctrl+C to cancel"

        except Exception as e:
            return f"❌ Error starting multi-stage test: {e}"

    def _test_search_progress(self):
        """Test search operation with progress."""
        try:
            # This will trigger the file search with progress
            # from core.commands.file_handler import FileCommandHandler

            # file_handler = FileCommandHandler()

            # Test search with progress indicators
            return file_handler._handle_search(["test", "sandbox"])

        except Exception as e:
            return f"❌ Error testing search progress: {e}"

    def _list_active_progress(self):
        """List all active progress indicators with details."""
        try:
            from core.services.progress_manager import progress_manager

            active_indicators = []

            # Check regular indicators
            for task_id, indicator in progress_manager.indicators.items():
                if indicator.status == "running":
                    active_indicators.append({
                        'id': task_id,
                        'type': 'simple',
                        'description': indicator.description,
                        'progress': f"{indicator.current}/{indicator.total}" if indicator.total else "N/A",
                        'elapsed': str(indicator.last_update - indicator.start_time).split('.')[0]
                    })

            # Check multi-stage indicators
            for task_id, indicator in progress_manager.multi_stage_indicators.items():
                if indicator.status == "running":
                    overall_progress = indicator.get_overall_progress()
                    active_indicators.append({
                        'id': task_id,
                        'type': 'multi-stage',
                        'description': f"Stage {indicator.current_stage + 1}/{len(indicator.stages)}",
                        'progress': f"{overall_progress:.1f}%",
                        'elapsed': str(indicator.start_time).split('.')[0]
                    })

            if not active_indicators:
                return "📊 No active progress indicators\n💡 Use: PROGRESS TEST to start a test"

            result = ["📊 Active Progress Indicators"]
            result.append("=" * 80)
            result.append(f"{'ID':<15} {'Type':<12} {'Description':<30} {'Progress':<15} {'Elapsed':<10}")
            result.append("-" * 80)

            for indicator in active_indicators:
                result.append(
                    f"{indicator['id']:<15} {indicator['type']:<12} "
                    f"{indicator['description']:<30} {indicator['progress']:<15} {indicator['elapsed']:<10}"
                )

            result.append(f"\n💡 Use: PROGRESS CANCEL <id> to cancel specific progress")
            return "\n".join(result)

        except Exception as e:
            return f"❌ Error listing progress: {e}"

    def _cancel_progress(self, progress_id):
        """Cancel progress indicator(s)."""
        try:
            from core.services.progress_manager import progress_manager

            if progress_id:
                # Cancel specific progress
                if progress_id in progress_manager.indicators:
                    progress_manager.indicators[progress_id].cancel("Cancelled by user")
                    progress_manager.remove_progress(progress_id)
                    return f"🚫 Cancelled progress: {progress_id}"
                elif progress_id in progress_manager.multi_stage_indicators:
                    indicator = progress_manager.multi_stage_indicators[progress_id]
                    if indicator.current_indicator:
                        indicator.current_indicator.cancel("Cancelled by user")
                    progress_manager.remove_progress(progress_id)
                    return f"🚫 Cancelled multi-stage progress: {progress_id}"
                else:
                    return f"❌ Progress indicator not found: {progress_id}"
            else:
                # Cancel all progress
                progress_manager.cancel_all()
                return "🚫 Cancelled all active progress indicators"

        except Exception as e:
            return f"❌ Error cancelling progress: {e}"

    def _run_progress_demo(self):
        """Run a comprehensive demo of all progress features."""
        import threading
        import time

        try:
            from core.services.progress_manager import progress_manager, ProgressConfig

            def demo_sequence():
                # Demo 1: Basic determinate progress
                config1 = ProgressConfig(style="block", show_time_estimate=True)
                p1 = progress_manager.create_progress("demo_basic", "Demo: Basic Progress", 50, config1)
                p1.start()

                for i in range(51):
                    time.sleep(0.1)
                    p1.update(i, f"Processing item {i}/50")
                p1.complete("Basic demo completed")
                time.sleep(1)

                # Demo 2: Indeterminate progress
                config2 = ProgressConfig(show_cancel_hint=True)
                p2 = progress_manager.create_progress("demo_spinner", "Demo: Indeterminate Progress")
                p2.start()

                time.sleep(3)  # Spinner for 3 seconds
                p2.complete("Indeterminate demo completed")
                time.sleep(1)

                # Demo 3: Multi-stage progress
                stages = ["Setup", "Processing", "Cleanup"]
                config3 = ProgressConfig(style="bar", width=25)
                p3 = progress_manager.create_multi_stage_progress("demo_multi", stages, config3)

                for i, stage in enumerate(stages):
                    p3.start_stage(i, f"Demo: {stage}", 20)
                    for j in range(21):
                        time.sleep(0.05)
                        p3.update_stage(j, f"{stage} item {j}")
                    p3.complete_stage(f"{stage} completed")

                p3.complete("Multi-stage demo completed")

                # Cleanup
                time.sleep(2)
                progress_manager.cleanup_completed()

            # Start demo in background
            threading.Thread(target=demo_sequence, daemon=True).start()

            return ("🎭 Starting comprehensive progress demo!\n"
                   "👀 Watch for 3 different types of progress indicators:\n"
                   "   1. Basic determinate progress (50 items)\n"
                   "   2. Indeterminate spinner (3 seconds)\n"
                   "   3. Multi-stage progress (3 stages)\n"
                   "⏱️ Total demo time: ~15 seconds")

        except Exception as e:
            return f"❌ Error starting progress demo: {e}"

    def handle_session(self, params, grid, parser):
        """
        Session management commands for workspace state persistence.

        Subcommands:
        - SESSION LIST                    # List all sessions
        - SESSION SAVE [name] [desc]      # Save current session
        - SESSION LOAD <id>               # Load/restore session
        - SESSION DELETE <id>             # Delete session
        - SESSION CURRENT                 # Show current session info
        - SESSION AUTO ON|OFF             # Toggle auto-save
        - SESSION CHECKPOINT [desc]       # Create checkpoint
        - SESSION EXPORT <id> <file>      # Export session to file
        - SESSION IMPORT <file> [name]    # Import session from file

        Args:
            params: List of command parameters
            grid: Grid instance (unused)
            parser: Parser instance (unused)

        Returns:
            Formatted session information or operation results
        """
        # Initialize session manager
        try:
            from core.services.session_manager import session_manager, SessionType
        except Exception as e:
            return f"❌ Error accessing session system: {e}"

        if not params:
            # Default: show current session info
            return self._show_current_session(session_manager)

        subcommand = params[0].upper()

        if subcommand == "LIST":
            session_type = None
            if len(params) > 1:
                type_map = {
                    'MANUAL': SessionType.MANUAL,
                    'AUTO': SessionType.AUTOMATIC,
                    'CHECKPOINT': SessionType.CHECKPOINT,
                    'BACKUP': SessionType.BACKUP
                }
                session_type = type_map.get(params[1].upper())
            return self._list_sessions(session_manager, session_type)

        elif subcommand == "SAVE":
            name = params[1] if len(params) > 1 else None
            description = " ".join(params[2:]) if len(params) > 2 else ""
            return self._save_session(session_manager, name, description)

        elif subcommand == "LOAD":
            if len(params) < 2:
                return "❌ Usage: SESSION LOAD <session_id>"
            session_id = params[1]
            return self._load_session(session_manager, session_id)

        elif subcommand == "DELETE":
            if len(params) < 2:
                return "❌ Usage: SESSION DELETE <session_id>"
            session_id = params[1]
            return self._delete_session(session_manager, session_id)

        elif subcommand == "CURRENT":
            return self._show_current_session(session_manager)

        elif subcommand == "AUTO":
            if len(params) < 2:
                return "❌ Usage: SESSION AUTO ON|OFF"
            enable = params[1].upper() == "ON"
            return self._toggle_auto_save(session_manager, enable)

        elif subcommand == "CHECKPOINT":
            description = " ".join(params[1:]) if len(params) > 1 else ""
            return self._create_checkpoint(session_manager, description)

        elif subcommand == "EXPORT":
            if len(params) < 3:
                return "❌ Usage: SESSION EXPORT <session_id> <file_path>"
            session_id = params[1]
            file_path = params[2]
            return self._export_session(session_manager, session_id, file_path)

        elif subcommand == "IMPORT":
            if len(params) < 2:
                return "❌ Usage: SESSION IMPORT <file_path> [new_name]"
            file_path = params[1]
            new_name = params[2] if len(params) > 2 else None
            return self._import_session(session_manager, file_path, new_name)

        else:
            return f"❌ Unknown session subcommand: {subcommand}\n💡 Use: HELP SESSION for usage information"

    def _show_current_session(self, session_manager):
        """Show current session information."""
        try:
            current = session_manager.current_session

            if not current:
                result = "📋 No active session\n"
                result += "💡 Use 'SESSION SAVE' to create a session or 'SESSION LOAD' to restore one"
                return result

            result = "📋 Current Session Information\n"
            result += "┌" + "─" * 70 + "┐\n"
            result += f"│ Session ID:    {current.session_id:<50} │\n"
            result += f"│ Name:          {current.name:<50} │\n"
            result += f"│ Type:          {current.session_type.value.title():<50} │\n"
            result += f"│ Created:       {current.created_at.strftime('%Y-%m-%d %H:%M:%S'):<50} │\n"
            result += f"│ Last Access:   {current.last_accessed.strftime('%Y-%m-%d %H:%M:%S'):<50} │\n"
            result += f"│ Description:   {current.description[:48]:<50} │\n"
            result += f"│ Directory:     {current.current_directory[-48:]:<50} │\n"
            result += f"│ Active Files:  {len(current.active_files):<50} │\n"
            result += f"│ Bookmarks:     {len(current.bookmarks):<50} │\n"
            result += f"│ History Items: {len(current.command_history):<50} │\n"
            result += "└" + "─" * 70 + "┘\n"

            if session_manager.auto_save_enabled:
                next_auto = session_manager.auto_save_interval
                result += f"🔄 Auto-save enabled (every {next_auto // 60} minutes)"
            else:
                result += "⏸️ Auto-save disabled"

            return result

        except Exception as e:
            return f"❌ Error showing current session: {e}"

    def _list_sessions(self, session_manager, session_type=None):
        """List available sessions."""
        try:
            sessions = session_manager.list_sessions(session_type)

            if not sessions:
                type_desc = f" ({session_type.value})" if session_type else ""
                return f"📋 No sessions found{type_desc}\n💡 Use 'SESSION SAVE' to create your first session"

            type_desc = f" ({session_type.value.title()})" if session_type else ""
            result = [f"📋 Available Sessions{type_desc} ({len(sessions)})"]
            result.append("=" * 80)
            result.append(f"{'ID':<25} {'Name':<20} {'Type':<12} {'Created':<15} {'Description':<20}")
            result.append("-" * 80)

            current_id = session_manager.current_session.session_id if session_manager.current_session else None

            for session in sessions[:20]:  # Show first 20 sessions
                is_current = "→" if session.session_id == current_id else " "
                created = session.created_at.strftime('%m/%d %H:%M')
                description = session.description[:18] + "..." if len(session.description) > 18 else session.description

                result.append(
                    f"{is_current}{session.session_id[:24]:<24} {session.name[:19]:<20} "
                    f"{session.session_type.value:<12} {created:<15} {description:<20}"
                )

            if len(sessions) > 20:
                result.append(f"\n... and {len(sessions) - 20} more sessions")

            result.append("\n💡 Use 'SESSION LOAD <id>' to restore a session")
            return "\n".join(result)

        except Exception as e:
            return f"❌ Error listing sessions: {e}"

    def _save_session(self, session_manager, name, description):
        """Save current session."""
        try:
            if not name:
                from datetime import datetime
                name = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            session_id = session_manager.create_session(name, description)
            return f"💾 Session saved successfully!\n📋 Session ID: {session_id}\n📝 Name: {name}"

        except Exception as e:
            return f"❌ Error saving session: {e}"

    def _load_session(self, session_manager, session_id):
        """Load/restore a session."""
        try:
            success = session_manager.restore_session(session_id)
            if success:
                session = session_manager.load_session(session_id)
                return (f"✅ Session restored successfully!\n"
                       f"📋 Loaded: {session.name}\n"
                       f"📁 Directory: {session.current_directory}\n"
                       f"💡 Workspace state has been restored")
            else:
                return f"❌ Failed to restore session: {session_id}\n💡 Check session ID with 'SESSION LIST'"

        except Exception as e:
            return f"❌ Error loading session: {e}"

    def _delete_session(self, session_manager, session_id):
        """Delete a session."""
        try:
            # Load session info before deletion for confirmation
            session = session_manager.load_session(session_id)
            if not session:
                return f"❌ Session not found: {session_id}"

            success = session_manager.delete_session(session_id)
            if success:
                return f"🗑️ Session deleted successfully!\n📋 Deleted: {session.name} ({session_id})"
            else:
                return f"❌ Failed to delete session: {session_id}"

        except Exception as e:
            return f"❌ Error deleting session: {e}"

    def _toggle_auto_save(self, session_manager, enable):
        """Toggle auto-save functionality."""
        try:
            session_manager.auto_save_enabled = enable
            session_manager._save_config()

            if enable:
                interval_min = session_manager.auto_save_interval // 60
                return f"🔄 Auto-save enabled (every {interval_min} minutes)\n💾 Sessions will be automatically saved"
            else:
                return "⏸️ Auto-save disabled\n💡 Sessions will only be saved manually"

        except Exception as e:
            return f"❌ Error toggling auto-save: {e}"

    def _create_checkpoint(self, session_manager, description):
        """Create a checkpoint."""
        try:
            if not description:
                from datetime import datetime
                description = f"Manual checkpoint - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            checkpoint_id = session_manager.create_checkpoint(description)
            return f"📍 Checkpoint created successfully!\n📋 Checkpoint ID: {checkpoint_id}\n📝 Description: {description}"

        except Exception as e:
            return f"❌ Error creating checkpoint: {e}"

    def _export_session(self, session_manager, session_id, file_path):
        """Export a session to file."""
        try:
            from pathlib import Path

            export_path = Path(file_path)

            # Ensure .json extension
            if not export_path.suffix:
                export_path = export_path.with_suffix('.json')

            success = session_manager.export_session(session_id, export_path)
            if success:
                return f"📤 Session exported successfully!\n💾 Exported to: {export_path}\n📋 Session: {session_id}"
            else:
                return f"❌ Failed to export session: {session_id}\n💡 Check session ID and file path"

        except Exception as e:
            return f"❌ Error exporting session: {e}"

    def _import_session(self, session_manager, file_path, new_name):
        """Import a session from file."""
        try:
            from pathlib import Path

            import_path = Path(file_path)
            if not import_path.exists():
                return f"❌ Import file not found: {file_path}"

            session_id = session_manager.import_session(import_path, new_name)
            if session_id:
                return f"📥 Session imported successfully!\n📋 New Session ID: {session_id}\n💾 Imported from: {file_path}"
            else:
                return f"❌ Failed to import session from: {file_path}\n💡 Check file format and content"

        except Exception as e:
            return f"❌ Error importing session: {e}"

    def handle_layout(self, params, grid, parser):
        """
        Adaptive layout management commands for responsive terminal interface.

        Subcommands:
        - LAYOUT INFO                     # Show current layout information
        - LAYOUT MODE <mode>              # Set layout mode (compact/standard/expanded/split/dashboard)
        - LAYOUT RESIZE                   # Force resize detection
        - LAYOUT AUTO ON|OFF              # Toggle automatic resize detection
        - LAYOUT CONFIG <setting> <value> # Update layout configuration
        - LAYOUT TEST                     # Test adaptive formatting
        - LAYOUT DEMO                     # Demo different layout modes
        - LAYOUT SPLIT <content1> <content2> # Create split layout demo

        Args:
            params: List of command parameters
            grid: Grid instance (unused)
            parser: Parser instance (unused)

        Returns:
            Formatted layout information or demo results
        """
        # Initialize layout manager
        try:
            from core.services.layout_manager import layout_manager, LayoutMode, ContentType
        except Exception as e:
            return f"❌ Error accessing layout system: {e}"

        if not params:
            # Default: show layout info
            return self._show_layout_info(layout_manager)

        subcommand = params[0].upper()

        if subcommand == "INFO":
            return self._show_layout_info(layout_manager)

        elif subcommand == "MODE":
            if len(params) < 2:
                return "❌ Usage: LAYOUT MODE <compact|standard|expanded|split|dashboard>"
            mode_name = params[1].upper()
            return self._set_layout_mode(layout_manager, mode_name)

        elif subcommand == "RESIZE":
            return self._force_resize_detection(layout_manager)

        elif subcommand == "AUTO":
            if len(params) < 2:
                return "❌ Usage: LAYOUT AUTO ON|OFF"
            enable = params[1].upper() == "ON"
            return self._toggle_auto_resize(layout_manager, enable)

        elif subcommand == "CONFIG":
            if len(params) < 3:
                return "❌ Usage: LAYOUT CONFIG <setting> <value>"
            setting = params[1].lower()
            value = params[2]
            return self._update_layout_config(layout_manager, setting, value)

        elif subcommand == "TEST":
            return self._test_adaptive_formatting(layout_manager)

        elif subcommand == "DEMO":
            return self._layout_demo(layout_manager)

        elif subcommand == "SPLIT":
            content1 = params[1] if len(params) > 1 else "Sample content 1"
            content2 = params[2] if len(params) > 2 else "Sample content 2"
            return self._demo_split_layout(layout_manager, content1, content2)

        else:
            return f"❌ Unknown layout subcommand: {subcommand}\n💡 Use: HELP LAYOUT for usage information"

    def _show_layout_info(self, layout_manager):
        """Show current layout information."""
        try:
            info = layout_manager.get_layout_info()
            dims = info['dimensions']
            config = info['config']

            # Use layout manager to format this response
            content = f"""Terminal Dimensions: {dims['width']}x{dims['height']}
Screen Type: {'📱 Mobile' if dims['is_mobile'] else '🖥️ Wide' if dims['is_wide'] else '💻 Standard'}
Layout Mode: {info['layout_mode'].title()}
Aspect Ratio: {dims['aspect_ratio']:.2f}

Configuration:
• Auto-adapt: {'✅' if config['auto_adapt'] else '❌'}
• Responsive Tables: {'✅' if config['responsive_tables'] else '❌'}
• Adaptive Columns: {'✅' if config['adaptive_columns'] else '❌'}
• Compact Mode: {'✅' if config['compact_mode'] else '❌'}
• Auto-resize: {'✅' if info['auto_resize_enabled'] else '❌'}

Screen Features:
• Wide Screen: {'✅' if dims['is_wide'] else '❌'} (>120 cols)
• Tall Screen: {'✅' if dims['is_tall'] else '❌'} (>30 rows)
• Ultra-wide: {'✅' if dims['is_ultra_wide'] else '❌'} (>200 cols)"""

            from core.services.layout_manager import ContentType
            return layout_manager.format_content(
                content,
                ContentType.STATUS,
                "Layout Manager Status"
            )

        except Exception as e:
            return f"❌ Error showing layout info: {e}"

    def _set_layout_mode(self, layout_manager, mode_name):
        """Set layout mode."""
        try:
            from core.services.layout_manager import LayoutMode

            mode_mapping = {
                'COMPACT': LayoutMode.COMPACT,
                'STANDARD': LayoutMode.STANDARD,
                'EXPANDED': LayoutMode.EXPANDED,
                'SPLIT': LayoutMode.SPLIT,
                'DASHBOARD': LayoutMode.DASHBOARD
            }

            if mode_name not in mode_mapping:
                available = ", ".join(mode_mapping.keys())
                return f"❌ Invalid layout mode: {mode_name}\n💡 Available modes: {available}"

            layout_manager.set_layout_mode(mode_mapping[mode_name])
            return f"🎨 Layout mode set to: {mode_name.lower()}\n✨ Interface will adapt to new layout"

        except Exception as e:
            return f"❌ Error setting layout mode: {e}"

    def _force_resize_detection(self, layout_manager):
        """Force resize detection."""
        try:
            old_dims = layout_manager.current_dimensions
            new_dims = layout_manager._get_terminal_dimensions()

            if (old_dims.width != new_dims.width or old_dims.height != new_dims.height):
                layout_manager._handle_resize(new_dims)
                return (f"🔄 Resize detected and applied!\n"
                       f"📏 Changed from {old_dims.width}x{old_dims.height} to {new_dims.width}x{new_dims.height}\n"
                       f"🎨 Layout mode: {layout_manager.current_mode.value}")
            else:
                return (f"📏 No resize detected\n"
                       f"📊 Current dimensions: {new_dims.width}x{new_dims.height}\n"
                       f"🎨 Layout mode: {layout_manager.current_mode.value}")

        except Exception as e:
            return f"❌ Error detecting resize: {e}"

    def _toggle_auto_resize(self, layout_manager, enable):
        """Toggle automatic resize detection."""
        try:
            layout_manager.auto_resize_enabled = enable

            if enable:
                if not layout_manager._resize_thread or not layout_manager._resize_thread.is_alive():
                    layout_manager._start_resize_monitoring()
                return "🔄 Auto-resize detection enabled\n📐 Terminal layout will automatically adapt to size changes"
            else:
                return "⏸️ Auto-resize detection disabled\n💡 Use 'LAYOUT RESIZE' to manually check for changes"

        except Exception as e:
            return f"❌ Error toggling auto-resize: {e}"

    def _update_layout_config(self, layout_manager, setting, value):
        """Update layout configuration."""
        try:
            # Convert value to appropriate type
            if value.lower() in ['true', 'on', 'yes', '1']:
                value = True
            elif value.lower() in ['false', 'off', 'no', '0']:
                value = False
            elif value.isdigit():
                value = int(value)

            # Map setting names
            setting_map = {
                'auto_adapt': 'auto_adapt',
                'responsive_tables': 'responsive_tables',
                'adaptive_columns': 'adaptive_columns',
                'compact_mode': 'compact_mode',
                'show_borders': 'show_borders',
                'use_unicode': 'use_unicode',
                'content_margin': 'content_margin',
                'min_width': 'min_width',
                'max_width': 'max_width'
            }

            if setting not in setting_map:
                available = ", ".join(setting_map.keys())
                return f"❌ Unknown setting: {setting}\n💡 Available settings: {available}"

            layout_manager.update_config(**{setting_map[setting]: value})
            return f"⚙️ Layout setting updated: {setting} = {value}\n✨ Changes will apply to new content"

        except Exception as e:
            return f"❌ Error updating config: {e}"

    def _test_adaptive_formatting(self, layout_manager):
        """Test adaptive formatting with sample content."""
        try:
            from core.services.layout_manager import ContentType

            # Test different content types
            test_results = []

            # Test table formatting
            table_content = """Name|Type|Size|Date
file1.py|Python|1.2KB|2024-01-15
file2.txt|Text|856B|2024-01-14
document.md|Markdown|3.4KB|2024-01-13"""

            table_result = layout_manager.format_content(table_content, ContentType.TABLE, "File List")
            test_results.append(("📊 Table Format Test", table_result))

            # Test list formatting
            list_content = """• Command history with SQLite persistence
• Advanced tab completion with fuzzy matching
• Dynamic color themes and accessibility features
• Real-time progress indicators for operations
• Session management with workspace persistence"""

            list_result = layout_manager.format_content(list_content, ContentType.LIST, "Feature List")
            test_results.append(("📋 List Format Test", list_result))

            # Test status formatting
            status_content = """System Status: Online
CPU Usage: 23%
Memory: 4.2GB / 8GB
Active Sessions: 3
Auto-save: Enabled"""

            status_result = layout_manager.format_content(status_content, ContentType.STATUS, "System Status")
            test_results.append(("📊 Status Format Test", status_result))

            # Combine results
            final_result = []
            for title, content in test_results:
                final_result.append(f"\n{title}")
                final_result.append("─" * 50)
                final_result.append(content)

            return "\n".join(final_result)

        except Exception as e:
            return f"❌ Error testing adaptive formatting: {e}"

    def _layout_demo(self, layout_manager):
        """Demo different layout capabilities."""
        try:
            from core.services.layout_manager import ContentType

            dims = layout_manager.current_dimensions

            demo_content = f"""Layout Demo - Current Configuration

Terminal Size: {dims.width}x{dims.height}
Layout Mode: {layout_manager.current_mode.value}
Screen Type: {'Mobile' if dims.is_mobile else 'Wide' if dims.is_wide else 'Standard'}

Adaptive Features Demonstrated:
✅ Responsive table formatting
✅ Dynamic content wrapping
✅ Context-aware layout selection
✅ Mobile-optimized display
✅ Wide-screen enhancements

This content is automatically formatted based on your terminal size.
Try resizing your terminal and running 'LAYOUT RESIZE' to see adaptive changes!"""

            return layout_manager.format_content(
                demo_content,
                ContentType.HELP,
                "uDOS Adaptive Layout Demo"
            )

        except Exception as e:
            return f"❌ Error running layout demo: {e}"

    def _demo_split_layout(self, layout_manager, content1, content2):
        """Demo split layout functionality."""
        try:
            if not layout_manager.current_dimensions.is_wide:
                return ("📱 Split layout not available on narrow screens\n"
                       "💡 Try expanding your terminal width to >120 columns")

            # Create split layout demo
            pane_configs = [
                {
                    'title': 'Left Pane',
                    'content': f"Content 1:\n{content1}\n\nThis is the left pane of the split layout.",
                    'content_type': 'text'
                },
                {
                    'title': 'Right Pane',
                    'content': f"Content 2:\n{content2}\n\nThis is the right pane of the split layout.",
                    'content_type': 'text'
                }
            ]

            split_result = layout_manager.create_split_layout(pane_configs)

            return (f"🪟 Split Layout Demo\n"
                   f"{'═' * min(layout_manager.current_dimensions.width, 60)}\n\n"
                   f"{split_result}\n\n"
                   f"💡 Split layouts automatically adapt to terminal width")

        except Exception as e:
            return f"❌ Error creating split layout demo: {e}"

    # ======================================================================
    # DELEGATED HANDLERS - Route to specialized handlers
    # ======================================================================

    def handle_repair(self, params, grid, parser):
        """
        System diagnostics and repair with extension management.
        Delegates to specialized RepairHandler for comprehensive functionality.
        """
        from .repair_handler import RepairHandler

        # Create repair handler with same context
        repair_handler = RepairHandler(
            connection=self.connection,
            viewport=self.viewport,
            user_manager=self.user_manager,
            history=self.history,
            theme=self.theme,
            logger=self.logger
        )

        return repair_handler.handle_repair(params, grid, parser)

    def handle_status(self, params, grid, parser):
        """
        Display comprehensive system status.
        Delegates to specialized DashboardHandler for functionality.
        """
        from .dashboard_handler import DashboardHandler

        # Create dashboard handler with same context
        dashboard_handler = DashboardHandler(
            connection=self.connection,
            viewport=self.viewport,
            user_manager=self.user_manager,
            history=self.history,
            theme=self.theme,
            logger=self.logger
        )

        return dashboard_handler.handle_status(params, grid, parser)

    def handle_dashboard(self, params, grid, parser):
        """
        Display system dashboard.
        Delegates to specialized DashboardHandler for functionality.
        """
        from .dashboard_handler import DashboardHandler

        # Create dashboard handler with same context
        dashboard_handler = DashboardHandler(
            connection=self.connection,
            viewport=self.viewport,
            user_manager=self.user_manager,
            history=self.history,
            theme=self.theme,
            logger=self.logger
        )

        return dashboard_handler.handle_dashboard(params, grid, parser)

    def handle_viewport(self, params, grid, parser):
        """
        Display viewport visualization.
        Delegates to specialized DashboardHandler for functionality.
        """
        from .dashboard_handler import DashboardHandler

        # Create dashboard handler with same context
        dashboard_handler = DashboardHandler(
            connection=self.connection,
            viewport=self.viewport,
            user_manager=self.user_manager,
            history=self.history,
            theme=self.theme,
            logger=self.logger
        )

        return dashboard_handler.handle_viewport(params, grid, parser)

    def handle_palette(self, params, grid, parser):
        """
        Display color palette.
        Delegates to specialized DashboardHandler for functionality.
        """
        from .dashboard_handler import DashboardHandler

        # Create dashboard handler with same context
        dashboard_handler = DashboardHandler(
            connection=self.connection,
            viewport=self.viewport,
            user_manager=self.user_manager,
            history=self.history,
            theme=self.theme,
            logger=self.logger
        )

        return dashboard_handler.handle_palette(params, grid, parser)

    def handle_settings(self, params, grid, parser):
        """
        Manage system settings.
        Delegates to specialized ConfigurationHandler for functionality.
        """
        from .configuration_handler import ConfigurationHandler

        # Create configuration handler with same context
        config_handler = ConfigurationHandler(
            connection=self.connection,
            viewport=self.viewport,
            user_manager=self.user_manager,
            history=self.history,
            theme=self.theme,
            logger=self.logger
        )

        return config_handler.handle_settings(params, grid, parser)

    def handle_config(self, params, grid, parser):
        """
        Manage configuration files.
        Delegates to specialized ConfigurationHandler for functionality.
        """
        from .configuration_handler import ConfigurationHandler

        # Create configuration handler with same context
        config_handler = ConfigurationHandler(
            connection=self.connection,
            viewport=self.viewport,
            user_manager=self.user_manager,
            history=self.history,
            theme=self.theme,
            logger=self.logger
        )

        return config_handler.handle_config(params, grid, parser)

    # ======================================================================
    # CORE SYSTEM COMMANDS - Handled directly
    # ======================================================================

    def handle_reboot(self, params, grid, parser):
        """
        Restart the entire uDOS system.
        Equivalent to exiting and re-running uDOS.py
        """
        output = "\n🔄 REBOOTING uDOS SYSTEM...\n\n"
        output += "✅ Saving current state...\n"
        output += "✅ Clearing memory buffers...\n"

        # Refresh viewport detection
        try:
            from core.services.viewport_manager import ViewportManager
            viewport = ViewportManager()
            viewport_info = viewport.refresh_viewport()
            tier = viewport_info["screen_tier"]
            output += f"🖥️  Viewport refreshed: {tier['label']} ({tier['actual_width_cells']}×{tier['actual_height_cells']} cells)\n"
        except Exception as e:
            output += f"⚠️  Viewport refresh warning: {str(e)}\n"

        output += "✅ Reinitializing components...\n\n"
        output += "🚀 System restart complete!\n"
        output += "Welcome back to uDOS v1.0.8\n\n"

        # Signal for system restart
        if hasattr(self, '_signal_restart'):
            self._signal_restart()

        return output

    def handle_destroy(self, params, grid, parser):
        """
        Destructive reset command with safety confirmations.
        Supports: --all, --env, --reset flags

        Args:
            params: List with optional flags (--all, --env, --reset)
            grid: Grid instance (unused)
            parser: Parser instance (unused)

        Returns:
            Destruction confirmation or cancellation message
        """
        # Safety confirmation required
        destruction_type = params[0] if params else None

        # Warning message based on destruction type
        if destruction_type == "--all":
            warning_msg = "⚠️  DANGER: This will DELETE ALL user data, extensions, and settings!"
            target = "entire uDOS installation"
        elif destruction_type == "--env":
            warning_msg = "⚠️  This will reset the Python environment and dependencies"
            target = "Python environment"
        elif destruction_type == "--reset":
            warning_msg = "⚠️  This will reset all settings to defaults"
            target = "configuration settings"
        else:
            return ("❌ DESTROY requires a flag\n\n"
                   "Available options:\n"
                   "  DESTROY --reset    Reset settings to defaults\n"
                   "  DESTROY --env      Reset Python environment\n"
                   "  DESTROY --all      Delete all user data (DANGER!)\n\n"
                   "⚠️  All DESTROY operations require confirmation")

        # Return warning and ask for confirmation
        result = f"🚨 DESTRUCTION CONFIRMATION REQUIRED\n"
        result += "=" * 50 + "\n"
        result += f"{warning_msg}\n\n"
        result += f"Target: {target}\n\n"
        result += "To proceed, type: DESTROY CONFIRM\n"
        result += "To cancel, type any other command\n"
        result += "\n⚠️  This action cannot be undone!"

        return result

    # ======================================================================
    # STUB METHODS - To be implemented or moved to other handlers
    # ======================================================================

    def handle_tree(self, params, grid, parser):
        """File tree display - to be implemented or moved to file handler."""
        return "🌳 TREE command - Implementation moved to file handler"

    def handle_clean(self, params, grid, parser):
        """Clean sandbox - to be implemented or moved to file handler."""
        return "🧹 CLEAN command - Implementation moved to file handler"

    def handle_setup(self, params, grid, parser):
        """Setup wizard - to be implemented."""
        return "⚙️ SETUP command - Implementation pending"

    def handle_workspace(self, params, grid, parser):
        """Workspace management - to be implemented."""
        return "🏢 WORKSPACE command - Implementation pending"

    def handle_output(self, params, grid, parser):
        """
        Manage web-based output interfaces (servers) and extensions.
        Implementation for v1.0.11 Extension System Formalization.
        """
        if not params:
            return ("❌ Usage: POKE <command> [name] [options]\n\n"
                   "🖥️  Server Management:\n"
                   "  POKE LIST                      # List all available extensions\n"
                   "  POKE START dashboard           # Start dashboard server\n"
                   "  POKE STATUS                    # Show all server status\n"
                   "  POKE HEALTH                    # Check server health\n"
                   "  POKE RESTART dashboard         # Restart specific server\n"
                   "  POKE STOP teletext            # Stop teletext server\n\n"
                   "🔧 Extension Management:\n"
                   "  POKE DISCOVER                  # Scan for new extensions\n"
                   "  POKE INFO <name>               # Detailed extension information\n"
                   "  POKE INSTALL <name>            # Install extension from source\n"
                   "  POKE UNINSTALL <name>          # Remove extension\n"
                   "  POKE MARKETPLACE               # Browse extension marketplace")

        subcommand = params[0].upper()

        if subcommand == "LIST":
            return self._handle_output_list()
        elif subcommand == "STATUS":
            extension_name = params[1] if len(params) > 1 else None
            return self._handle_output_status(extension_name)
        elif subcommand == "HEALTH":
            return self._handle_output_health()
        elif subcommand == "START":
            if len(params) < 2:
                return "❌ Usage: POKE START <extension_name> [--port N] [--no-browser]"
            extension_name = params[1]
            options = params[2:] if len(params) > 2 else []
            return self._handle_output_start(extension_name, options)
        elif subcommand == "STOP":
            if len(params) < 2:
                return "❌ Usage: POKE STOP <extension_name>"
            extension_name = params[1]
            return self._handle_output_stop(extension_name)
        elif subcommand == "RESTART":
            if len(params) < 2:
                return "❌ Usage: POKE RESTART <extension_name>"
            extension_name = params[1]
            return self._handle_output_restart(extension_name)
        # New extension management commands for v1.0.11
        elif subcommand == "DISCOVER":
            return self._handle_extension_discover()
        elif subcommand == "INFO":
            if len(params) < 2:
                return "❌ Usage: POKE INFO <extension_name>"
            extension_name = params[1]
            return self._handle_extension_info(extension_name)
        elif subcommand == "INSTALL":
            if len(params) < 2:
                return "❌ Usage: POKE INSTALL <extension_name>"
            extension_name = params[1]
            return self._handle_extension_install(extension_name)
        elif subcommand == "UNINSTALL":
            if len(params) < 2:
                return "❌ Usage: POKE UNINSTALL <extension_name>"
            extension_name = params[1]
            return self._handle_extension_uninstall(extension_name)
        elif subcommand == "MARKETPLACE":
            return self._handle_extension_marketplace()
        else:
            return f"❌ Unknown POKE subcommand: {subcommand}\nUse: START, STOP, STATUS, LIST, HEALTH, RESTART, DISCOVER, INFO, INSTALL, UNINSTALL, or MARKETPLACE"

    def _handle_output_list(self):
        """List all available web extensions."""
        try:
            from core.uDOS_server import ServerManager
            server_manager = ServerManager()
            return server_manager.list_servers()
        except Exception as e:
            return f"❌ Error listing extensions: {str(e)}"

    def _handle_output_status(self, extension_name=None):
        """Show status of web extensions."""
        try:
            from core.uDOS_server import ServerManager
            server_manager = ServerManager()
            return server_manager.get_status(extension_name)
        except Exception as e:
            return f"❌ Error getting status: {str(e)}"

    def _handle_output_start(self, extension_name, options):
        """Start a web extension server."""
        try:
            from core.uDOS_server import ServerManager
            server_manager = ServerManager()

            # Parse options
            port = None
            no_browser = False

            for option in options:
                if option.startswith('--port'):
                    if '=' in option:
                        port = int(option.split('=')[1])
                    else:
                        # Look for next parameter
                        port_index = options.index(option) + 1
                        if port_index < len(options):
                            port = int(options[port_index])
                elif option == '--no-browser':
                    no_browser = True

            return server_manager.start_server(extension_name, port=port, open_browser=not no_browser)
        except Exception as e:
            return f"❌ Error starting {extension_name}: {str(e)}"

    def _handle_output_stop(self, extension_name):
        """Stop a web extension server."""
        try:
            from core.uDOS_server import ServerManager
            server_manager = ServerManager()
            success, message = server_manager.stop_server(extension_name)
            return f"🛑 {message}" if success else f"⚠️  {message}"
        except Exception as e:
            return f"❌ Error stopping {extension_name}: {str(e)}"

    def _handle_output_health(self):
        """Perform health check on all running servers."""
        try:
            from core.uDOS_server import ServerManager
            server_manager = ServerManager()

            # Get current status
            status_result = server_manager.get_status()

            # Count running/stopped servers
            running_count = status_result.count("✅")
            stopped_count = status_result.count("❌")
            total_count = running_count + stopped_count

            health_report = f"🏥 Server Health Report\n"
            health_report += f"{'='*40}\n"
            health_report += f"📊 Summary:\n"
            health_report += f"   ✅ Running: {running_count}\n"
            health_report += f"   ❌ Stopped: {stopped_count}\n"
            health_report += f"   📈 Total: {total_count}\n\n"

            if running_count == 0:
                health_report += "⚠️  No servers currently running\n"
                health_report += "💡 Tip: Use 'OUTPUT START <name>' to start servers\n"
            elif stopped_count == 0:
                health_report += "✅ All servers are running healthy!\n"
            else:
                health_percentage = (running_count / total_count) * 100 if total_count > 0 else 0
                health_report += f"📊 System Health: {health_percentage:.1f}%\n"

                if health_percentage >= 80:
                    health_report += "✅ System health is good\n"
                elif health_percentage >= 50:
                    health_report += "⚠️  System health is moderate\n"
                else:
                    health_report += "❌ System health needs attention\n"

            return health_report

        except Exception as e:
            return f"❌ Error checking health: {str(e)}"

    def _handle_output_restart(self, extension_name):
        """Restart a web extension server."""
        try:
            from core.uDOS_server import ServerManager
            server_manager = ServerManager()

            # Stop the server first
            stop_success, stop_message = server_manager.stop_server(extension_name)

            # Wait a moment for cleanup
            import time
            time.sleep(1)

            # Start the server again
            start_result = server_manager.start_server(extension_name)

            if stop_success or "not running" in stop_message:
                return f"🔄 Restarted {extension_name}:\n🛑 Stop: {stop_message}\n{start_result}"
            else:
                return f"⚠️  Restart {extension_name} (stop failed, attempting start anyway):\n🛑 Stop: {stop_message}\n{start_result}"

        except Exception as e:
            return f"❌ Error restarting {extension_name}: {str(e)}"

    # Extension Management Methods - v1.0.11 Extension System Formalization

    def _handle_extension_discover(self):
        """Discover available extensions in the system and scan for new ones."""
        try:
            import json
            from pathlib import Path

            discovered = []
            report = "🔍 EXTENSION DISCOVERY REPORT\n" + "="*50 + "\n\n"

            # Scan bundled extensions
            bundled_path = Path(__file__).parent.parent.parent / "extensions" / "bundled" / "web"
            if bundled_path.exists():
                manifest_path = bundled_path / "version-manifest.json"
                if manifest_path.exists():
                    try:
                        with open(manifest_path, 'r') as f:
                            manifest = json.load(f)

                        report += "🎁 BUNDLED EXTENSIONS:\n"
                        for name, info in manifest.get('extensions', {}).items():
                            status = "🟢 Available" if (bundled_path / name).exists() else "🔴 Missing"
                            report += f"  {status} {name} v{info.get('version', 'unknown')}\n"
                            report += f"    📝 {info.get('description', 'No description')}\n"
                            if info.get('port'):
                                report += f"    🌐 Port: {info['port']}\n"
                            report += "\n"
                            discovered.append(name)
                    except Exception as e:
                        report += f"❌ Error reading manifest: {str(e)}\n"

            # Scan cloned extensions
            cloned_path = Path(__file__).parent.parent.parent / "extensions" / "cloned"
            if cloned_path.exists():
                cloned_dirs = [d for d in cloned_path.iterdir() if d.is_dir()]
                if cloned_dirs:
                    report += "\n🌐 CLONED EXTENSIONS:\n"
                    for ext_dir in cloned_dirs:
                        report += f"  📂 {ext_dir.name}\n"
                        # Check for package.json or README
                        if (ext_dir / "package.json").exists():
                            report += f"    📦 Node.js project detected\n"
                        if (ext_dir / "README.md").exists():
                            report += f"    📖 Documentation available\n"
                        discovered.append(ext_dir.name)

            # Check extension manager status
            from core.services.extension_manager import ExtensionManager
            ext_mgr = ExtensionManager()
            status = ext_mgr.get_extension_status()

            report += "\n🔧 INSTALLATION STATUS:\n"
            for ext, installed in status.items():
                symbol = "✅" if installed else "❌"
                report += f"  {symbol} {ext}\n"

            report += f"\n📊 SUMMARY: {len(discovered)} extensions discovered\n"
            return report

        except Exception as e:
            return f"❌ Error during discovery: {str(e)}"

    def _handle_extension_info(self, extension_name):
        """Get detailed information about a specific extension using enhanced metadata."""
        try:
            # Use the enhanced metadata manager for comprehensive information
            from core.services.extension_metadata_manager import ExtensionMetadataManager
            metadata_mgr = ExtensionMetadataManager()

            # Generate comprehensive report
            report = metadata_mgr.generate_extension_report(extension_name)
            return report

        except ImportError:
            # Fallback to basic implementation if metadata manager is not available
            return self._handle_extension_info_basic(extension_name)
        except Exception as e:
            return f"❌ Error getting extension info: {str(e)}"

    def _handle_extension_info_basic(self, extension_name):
        """Basic extension info implementation (fallback)."""
        try:
            import json
            from pathlib import Path

            info_report = f"📋 EXTENSION INFO: {extension_name}\n" + "="*50 + "\n\n"

            # Check bundled extensions first
            bundled_path = Path(__file__).parent.parent.parent / "extensions" / "bundled" / "web"
            manifest_path = bundled_path / "version-manifest.json"

            extension_found = False

            if manifest_path.exists():
                try:
                    with open(manifest_path, 'r') as f:
                        manifest = json.load(f)

                    if extension_name in manifest.get('extensions', {}):
                        ext_info = manifest['extensions'][extension_name]
                        extension_found = True

                        info_report += f"📦 NAME: {extension_name}\n"
                        info_report += f"🏷️  VERSION: {ext_info.get('version', 'unknown')}\n"
                        info_report += f"📝 DESCRIPTION: {ext_info.get('description', 'No description')}\n"

                        if ext_info.get('port'):
                            info_report += f"🌐 PORT: {ext_info['port']}\n"

                        if ext_info.get('features'):
                            info_report += f"\n✨ FEATURES:\n"
                            for feature in ext_info['features']:
                                info_report += f"  • {feature}\n"

                        if ext_info.get('dependencies'):
                            info_report += f"\n📦 DEPENDENCIES:\n"
                            for dep in ext_info['dependencies']:
                                info_report += f"  • {dep}\n"

                        # Check if extension files exist
                        ext_path = bundled_path / extension_name
                        if ext_path.exists():
                            info_report += f"\n📂 STATUS: ✅ Installed\n"
                            info_report += f"📍 LOCATION: {ext_path}\n"

                            # Count files
                            try:
                                files = list(ext_path.rglob('*'))
                                file_count = len([f for f in files if f.is_file()])
                                info_report += f"📄 FILES: {file_count}\n"
                            except:
                                pass
                        else:
                            info_report += f"\n📂 STATUS: ❌ Not installed\n"

                except Exception as e:
                    info_report += f"❌ Error reading manifest: {str(e)}\n"

            # Check extension manager
            try:
                from core.services.extension_manager import ExtensionManager
                ext_mgr = ExtensionManager()
                ext_details = ext_mgr.get_extension_info(extension_name)

                if ext_details and not extension_found:
                    extension_found = True
                    info_report += f"📦 NAME: {ext_details.get('name', extension_name)}\n"
                    info_report += f"📝 DESCRIPTION: {ext_details.get('description', 'No description')}\n"
                    info_report += f"🔗 REPOSITORY: {ext_details.get('repository', 'Not specified')}\n"
                    info_report += f"⚙️  TYPE: {ext_details.get('type', 'unknown')}\n"

                    if ext_details.get('port'):
                        info_report += f"🌐 PORT: {ext_details['port']}\n"

                    # Check installation status
                    is_installed = ext_mgr.check_extension_installed(extension_name)
                    status = "✅ Installed" if is_installed else "❌ Not installed"
                    info_report += f"\n📂 STATUS: {status}\n"

            except Exception as e:
                info_report += f"\n⚠️  Extension manager error: {str(e)}\n"

            if not extension_found:
                info_report += f"❌ Extension '{extension_name}' not found.\n"
                info_report += f"💡 Use 'POKE DISCOVER' to see available extensions.\n"

            return info_report

        except Exception as e:
            return f"❌ Error getting extension info: {str(e)}"

    def _handle_extension_install(self, extension_name):
        """Install an extension."""
        try:
            from core.services.extension_manager import ExtensionManager
            ext_mgr = ExtensionManager()

            install_report = f"📦 INSTALLING EXTENSION: {extension_name}\n" + "="*50 + "\n\n"

            # Check if already installed
            if ext_mgr.check_extension_installed(extension_name):
                return f"✅ Extension '{extension_name}' is already installed.\n💡 Use 'POKE RESTART {extension_name}' to restart if needed."

            install_report += f"🔄 Installing {extension_name}...\n"

            success, message = ext_mgr.install_extension(extension_name, quiet=False)

            if success:
                install_report += f"✅ SUCCESS: {message}\n"
                install_report += f"🚀 Extension '{extension_name}' is now available.\n"
                install_report += f"💡 Use 'POKE START {extension_name}' to launch it."
            else:
                install_report += f"❌ FAILED: {message}\n"
                install_report += f"💡 Use 'POKE DISCOVER' to see available extensions."

            return install_report

        except Exception as e:
            return f"❌ Error installing extension: {str(e)}"

    def _handle_extension_uninstall(self, extension_name):
        """Uninstall an extension (placeholder for future implementation)."""
        return (f"🚧 UNINSTALL FEATURE COMING SOON\n\n"
                f"Extension uninstallation for '{extension_name}' is not yet implemented.\n"
                f"This feature will be added in a future version.\n\n"
                f"📝 For now, you can manually remove extension files from:\n"
                f"   • extensions/bundled/web/{extension_name}/\n"
                f"   • extensions/cloned/{extension_name}/\n\n"
                f"⚠️  CAUTION: Manual removal may affect system stability.")

    def _handle_extension_marketplace(self):
        """Browse the extension marketplace (placeholder for future implementation)."""
        return ("🏪 EXTENSION MARKETPLACE\n" + "="*30 + "\n\n"
                "🚧 COMING SOON: Extension Marketplace\n\n"
                "The extension marketplace will provide:\n"
                "• 🌐 Community-contributed extensions\n"
                "• 🔍 Search and discovery features\n"
                "• ⭐ Ratings and reviews\n"
                "• 🔒 Security verification\n"
                "• 📦 One-click installation\n"
                "• 🔄 Automatic updates\n\n"
                "🎯 CURRENT EXTENSIONS:\n"
                "Use 'POKE DISCOVER' to see available extensions\n"
                "Use 'POKE INFO <name>' for detailed information\n\n"
                "📧 Want to contribute? Contact the uDOS development team!")

    def handle_undo(self, params, grid, parser):
        """
        Undo the last reversible operation.

        Usage: UNDO

        Reverses the last recorded action and adjusts the move counter.
        Undone actions can be reapplied using REDO.
        """
        if not self.history:
            return "❌ History system not initialized."

        success, message = self.history.undo(grid)

        if success:
            return f"↩️  {message}"
        else:
            return f"⚠️  {message}"

    def handle_redo(self, params, grid, parser):
        """
        Redo the last undone operation.

        Usage: REDO

        Re-applies the last action that was undone with UNDO.
        Re-doing an action adjusts the move counter forward.
        """
        if not self.history:
            return "❌ History system not initialized."

        success, message = self.history.redo(grid)

        if success:
            return f"↪️  {message}"
        else:
            return f"⚠️  {message}"

    def handle_restore(self, params, grid, parser):
        """
        Restore state to a previous session (bulk undo).

        Usage:
            RESTORE                - Show session list (default)
            RESTORE LIST           - Show available sessions
            RESTORE <session_num>  - Restore to specific session

        Performs multiple UNDO operations to return to the specified session state.
        """
        if not self.history:
            return "❌ History system not initialized."

        # If no params or params is ['LIST'], show session list
        if not params or (len(params) == 1 and params[0].upper() == "LIST"):
            # Get session history from logger
            if not self.logger:
                return "❌ Logger not available for session history."

            # Get move stats to show session info
            move_stats = self.logger.get_move_stats()
            current_session = move_stats.get('session_number', 0)

            output = "╔" + "═"*78 + "╗\n"
            output += "║  📜 SESSION HISTORY".ljust(79) + "║\n"
            output += "╠" + "═"*78 + "╣\n"
            output += f"║  Current Session: #{current_session}".ljust(79) + "║\n"
            output += "║".ljust(79) + "║\n"
            output += "║  Use RESTORE <session_num> to restore to a previous session.".ljust(79) + "║\n"
            output += "║  All actions after that session will be undone.".ljust(79) + "║\n"
            output += "║".ljust(79) + "║\n"
            output += "║  💡 Tip: Use HISTORY command for detailed command history.".ljust(79) + "║\n"
            output += "╚" + "═"*78 + "╝"
            return output

        # Attempt to restore to specific session
        subcommand = params[0]
        try:
            target_session = int(subcommand)

            # Get current session
            if not self.logger:
                return "❌ Logger not available."

            move_stats = self.logger.get_move_stats()
            current_session = move_stats.get('session_number', 0)

            if target_session >= current_session:
                return f"⚠️  Cannot restore to session #{target_session} (current: #{current_session})"

            # Calculate how many undos needed
            undo_count = current_session - target_session

            # Perform bulk undo
            output = f"🔄 Restoring to session #{target_session}...\n\n"
            success_count = 0

            for i in range(undo_count):
                success, msg = self.history.undo(grid)
                if success:
                    success_count += 1
                else:
                    output += f"⚠️  Stopped at undo {i+1}/{undo_count}: {msg}\n"
                    break

            if success_count > 0:
                output += f"✅ Restored {success_count} operations\n"
                output += f"📍 Current position: Session #{target_session}"
            else:
                output += "❌ No operations could be restored"

            return output

        except ValueError:
            return f"❌ Invalid session number: '{subcommand}'. Use RESTORE LIST to see available sessions."
