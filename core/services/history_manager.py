# uDOS v1.0.0 - UNDO/REDO System

from collections import deque
import json
import os
import datetime

class ActionHistory:
    """
    Manages reversible operations for UNDO/REDO functionality.
    Integrates with session logging for persistent history and RESTORE capability.
    """

    def __init__(self, logger=None, max_history=50):
        self.undo_stack = deque(maxlen=max_history)
        self.redo_stack = deque(maxlen=max_history)
        self.logger = logger

    def record_action(self, action_type, action_data):
        """
        Record a reversible action.

        Args:
            action_type (str): Type of action (PANEL_CREATE, PANEL_DELETE, FILE_SAVE, etc.)
            action_data (dict): Data needed to reverse the action
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        action = {
            'type': action_type,
            'data': action_data,
            'timestamp': timestamp
        }
        self.undo_stack.append(action)
        # Clear redo stack when new action is performed
        self.redo_stack.clear()

        # Log to session file for RESTORE functionality
        if self.logger:
            self.logger.log_action(action_type, action_data)

    def undo(self, grid):
        """
        Undo the last action.
        Adjusts move counter (-1).
        Returns: (success, message)
        """
        if not self.undo_stack:
            return False, "Nothing to undo."

        action = self.undo_stack.pop()

        # Perform reverse action based on type
        success, msg = self._reverse_action(action, grid)

        if success:
            # Move to redo stack
            self.redo_stack.append(action)
            # Adjust moves: UNDO decrements
            if self.logger:
                self.logger.adjust_moves(-1)

        return success, msg

    def redo(self, grid):
        """
        Redo the last undone action.
        Adjusts move counter (+1).
        Returns: (success, message)
        """
        if not self.redo_stack:
            return False, "Nothing to redo."

        action = self.redo_stack.pop()

        # Re-perform the original action
        success, msg = self._perform_action(action, grid)

        if success:
            # Move back to undo stack
            self.undo_stack.append(action)
            # Adjust moves: REDO increments
            if self.logger:
                self.logger.adjust_moves(+1)

        return success, msg

    def _reverse_action(self, action, grid):
        """Reverse a specific action."""
        action_type = action['type']
        data = action['data']

        if action_type == 'PANEL_CREATE':
            # Reverse: Delete the panel
            panel_name = data['panel_name']
            if grid.remove_panel(panel_name):
                return True, f"Undone: Removed panel '{panel_name}'"
            return False, f"Failed to undo panel creation"

        elif action_type == 'PANEL_DELETE':
            # Reverse: Recreate the panel with original content
            panel_name = data['panel_name']
            content = data.get('content', '')
            grid.add_panel(panel_name, content)
            return True, f"Undone: Restored panel '{panel_name}'"

        elif action_type == 'PANEL_EDIT':
            # Reverse: Restore original content
            panel_name = data['panel_name']
            old_content = data['old_content']
            if panel_name in grid.panels:
                grid.panels[panel_name] = old_content
                return True, f"Undone: Restored content of '{panel_name}'"
            return False, f"Panel '{panel_name}' not found"

        elif action_type == 'FILE_SAVE':
            # Reverse: Restore original file or delete if new
            file_path = data['file_path']
            if data.get('was_new'):
                # Delete the file
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    return True, f"Undone: Deleted new file '{file_path}'"
                except Exception as e:
                    return False, f"Failed to undo file save: {e}"
            else:
                # Restore original content
                old_content = data.get('old_content', '')
                try:
                    with open(file_path, 'w') as f:
                        f.write(old_content)
                    return True, f"Undone: Restored '{file_path}'"
                except Exception as e:
                    return False, f"Failed to undo file save: {e}"

        return False, f"Unknown action type: {action_type}"

    def _perform_action(self, action, grid):
        """Re-perform an action (for REDO)."""
        action_type = action['type']
        data = action['data']

        if action_type == 'PANEL_CREATE':
            panel_name = data['panel_name']
            grid.add_panel(panel_name, '')
            return True, f"Redone: Created panel '{panel_name}'"

        elif action_type == 'PANEL_DELETE':
            panel_name = data['panel_name']
            if grid.remove_panel(panel_name):
                return True, f"Redone: Deleted panel '{panel_name}'"
            return False, f"Failed to redo panel deletion"

        elif action_type == 'PANEL_EDIT':
            panel_name = data['panel_name']
            new_content = data['new_content']
            if panel_name in grid.panels:
                grid.panels[panel_name] = new_content
                return True, f"Redone: Updated content of '{panel_name}'"
            return False, f"Panel '{panel_name}' not found"

        elif action_type == 'FILE_SAVE':
            file_path = data['file_path']
            new_content = data['new_content']
            try:
                with open(file_path, 'w') as f:
                    f.write(new_content)
                return True, f"Redone: Saved '{file_path}'"
            except Exception as e:
                return False, f"Failed to redo file save: {e}"

        return False, f"Unknown action type: {action_type}"

    def clear(self):
        """Clear all history."""
        self.undo_stack.clear()
        self.redo_stack.clear()

    def get_history_info(self):
        """Get information about undo/redo stacks."""
        return {
            'undo_available': len(self.undo_stack),
            'redo_available': len(self.redo_stack)
        }

    def restore_from_session(self, session_number, grid):
        """
        Restore state to a previous session by undoing all actions since then.

        Args:
            session_number (int): Session number (1=current, 2=previous, etc.)
            grid: Grid object for panel operations

        Returns: (success, message, actions_undone)
        """
        if not self.logger:
            return False, "No logger available for session restore", 0

        # Get all sessions
        sessions = self.logger.get_all_sessions()

        if session_number < 1 or session_number > len(sessions):
            return False, f"Invalid session number. Available: 1-{len(sessions)}", 0

        # Current session is #1, so we need to undo all actions from sessions 1 through session_number-1
        if session_number == 1:
            return True, "Already at current session", 0

        # Calculate how many sessions to undo
        sessions_to_undo = session_number - 1

        # Collect all actions from current and intermediate sessions
        actions_to_undo = []
        for i in range(sessions_to_undo):
            if i < len(sessions):
                session_file, _, _ = sessions[i]
                session_actions = self._get_session_actions_from_file(session_file)
                # Reverse order for proper undo
                actions_to_undo.extend(reversed(session_actions))

        # Perform bulk undo
        undone_count = 0
        errors = []

        for action in actions_to_undo:
            success, msg = self._reverse_action(action, grid)
            if success:
                undone_count += 1
            else:
                errors.append(msg)

        # Clear current history stacks since we've restored to a previous state
        self.undo_stack.clear()
        self.redo_stack.clear()

        if errors:
            error_summary = f" ({len(errors)} errors)"
        else:
            error_summary = ""

        return True, f"Restored to session #{session_number}, undone {undone_count} actions{error_summary}", undone_count

    def _get_session_actions_from_file(self, session_file):
        """Extract actions from a session log file."""
        actions = []
        try:
            with open(session_file, 'r') as f:
                for line in f:
                    if '[ACTION]' in line:
                        # Extract JSON from log line
                        json_start = line.find('{')
                        if json_start != -1:
                            json_str = line[json_start:].strip()
                            action = json.loads(json_str)
                            actions.append(action)
        except Exception as e:
            pass  # Silently skip errors in reading old sessions

        return actions

    def get_session_list(self):
        """
        Get list of available sessions for RESTORE command.
        Returns list of dicts with session info.
        """
        if not self.logger:
            return []

        sessions = self.logger.get_all_sessions()
        session_list = []

        for filepath, timestamp, session_num in sessions:
            summary = self.logger.get_session_summary(filepath)
            session_list.append({
                'number': session_num,
                'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                'start_time': summary.get('start_time', 'Unknown'),
                'end_time': summary.get('end_time', 'Unknown'),
                'action_count': summary.get('action_count', 0),
                'is_current': summary.get('is_current', False)
            })

        return session_list
