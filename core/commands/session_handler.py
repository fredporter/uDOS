"""
uDOS Session & History Handler (v1.1.5.1)

Manages session lifecycle, command history, and state restoration.

Extracted from SystemCommandHandler as part of v1.1.5.1 refactoring.

Commands:
- SESSION: Session management (save, load, delete, export, import)
- HISTORY: Command history tracking and search
- UNDO: Reverse last operation
- REDO: Reapply undone operation
- RESTORE: Bulk undo to previous session state
"""

from .base_handler import BaseCommandHandler


class SessionHandler(BaseCommandHandler):
    """Handles session management and command history operations."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._session_manager = None
        self._usage_tracker = None

    @property
    def session_manager(self):
        """Lazy load session manager."""
        if self._session_manager is None:
            from core.services.session_manager import session_manager
            self._session_manager = session_manager
        return self._session_manager

    @property
    def usage_tracker(self):
        """Lazy load usage tracker."""
        if self._usage_tracker is None:
            from core.utils.usage_tracker import UsageTracker
            self._usage_tracker = UsageTracker()
        return self._usage_tracker

    def handle(self, command, params, grid, parser):
        """Route session and history commands."""
        handlers = {
            'SESSION': self.handle_session,
            'HISTORY': self.handle_history,
            'UNDO': self.handle_undo,
            'REDO': self.handle_redo,
            'RESTORE': self.handle_restore
        }

        handler = handlers.get(command)
        if handler:
            return handler(params, grid, parser)

        return False

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
            from core.services.session_manager import SessionType
        except Exception as e:
            return f"❌ Error accessing session system: {e}"

        if not params:
            # Default: show current session info
            return self._show_current_session(self.session_manager)

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
            return self._list_sessions(self.session_manager, session_type)

        elif subcommand == "SAVE":
            name = params[1] if len(params) > 1 else None
            description = " ".join(params[2:]) if len(params) > 2 else ""
            return self._save_session(self.session_manager, name, description)

        elif subcommand == "LOAD":
            if len(params) < 2:
                return "❌ Usage: SESSION LOAD <session_id>"
            session_id = params[1]
            return self._load_session(self.session_manager, session_id)

        elif subcommand == "DELETE":
            if len(params) < 2:
                return "❌ Usage: SESSION DELETE <session_id>"
            session_id = params[1]
            return self._delete_session(self.session_manager, session_id)

        elif subcommand == "CURRENT":
            return self._show_current_session(self.session_manager)

        elif subcommand == "AUTO":
            if len(params) < 2:
                return "❌ Usage: SESSION AUTO ON|OFF"
            enable = params[1].upper() == "ON"
            return self._toggle_auto_save(self.session_manager, enable)

        elif subcommand == "CHECKPOINT":
            description = " ".join(params[1:]) if len(params) > 1 else ""
            return self._create_checkpoint(self.session_manager, description)

        elif subcommand == "EXPORT":
            if len(params) < 3:
                return "❌ Usage: SESSION EXPORT <session_id> <file_path>"
            session_id = params[1]
            file_path = params[2]
            return self._export_session(self.session_manager, session_id, file_path)

        elif subcommand == "IMPORT":
            if len(params) < 2:
                return "❌ Usage: SESSION IMPORT <file_path> [new_name]"
            file_path = params[1]
            new_name = params[2] if len(params) > 2 else None
            return self._import_session(self.session_manager, file_path, new_name)

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
                return f"❌ Failed to import session from {file_path}"

        except Exception as e:
            return f"❌ Error importing session: {e}"

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
                return f"🗑️  Cleared {deleted} commands from history"

        except Exception as e:
            return f"❌ Error clearing history: {e}"

    def _export_history(self, history, filename):
        """Export command history to file."""
        try:
            import json
            from pathlib import Path
            from datetime import datetime

            export_path = Path(filename)
            if not export_path.suffix:
                export_path = export_path.with_suffix('.json')

            # Get all commands and stats
            commands = list(history)
            stats = history.get_command_stats()

            export_data = {
                'exported_at': datetime.now().isoformat(),
                'total_commands': len(commands),
                'statistics': stats,
                'commands': commands
            }

            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)

            return f"📤 History exported successfully!\n💾 Exported {len(commands)} commands to: {export_path}"

        except Exception as e:
            return f"❌ Error exporting history: {e}"

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
                    output += f"⚠️  Stopped at undo #{i+1}: {msg}\n"
                    break

            if success_count == undo_count:
                output += f"✅ Successfully restored to session #{target_session}\n"
                output += f"↩️  Performed {success_count} undo operations"
            else:
                output += f"⚠️  Partially restored ({success_count}/{undo_count} undos completed)"

            return output

        except ValueError:
            return f"❌ Invalid session number: {subcommand}\n💡 Use RESTORE LIST to see available sessions"
        except Exception as e:
            return f"❌ Error during restore: {e}"
