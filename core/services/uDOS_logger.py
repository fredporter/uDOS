# uDOS v1.1.6 - Session Logger (Updated for new Logging Manager)

import os
import datetime
import json
import logging

# Import new logging system
from core.services.logging_manager import get_logging_manager, get_logger

class Logger:
    """
    uDOS Session Logger v1.1.6

    Compatibility wrapper around the new flat directory logging system.
    Maintains existing API while using the new logging manager internally.

    Features:
    - Session activity logging
    - Reversible actions for UNDO/REDO/RESTORE
    - MOVES tracking (INPUT/OUTPUT pairs)
    - Backward compatibility with existing code
    """
    def __init__(self, log_dir="memory/logs"):
        """
        Initialize the logger with new logging manager backend.
        """
        # Initialize new logging manager
        self.logging_manager = get_logging_manager()

        # Create loggers for different types
        self.session_logger = get_logger('ucode-execution')
        self.command_logger = get_logger('command-history')
        self.system_logger = get_logger('system-startup')

        # Legacy compatibility
        self.log_dir = log_dir
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(log_dir, f"ucode-execution-{datetime.datetime.now().strftime('%Y-%m-%d')}.log")

        # Calculate session number (for backward compatibility)
        try:
            import glob
            existing_sessions = glob.glob(os.path.join(log_dir, "session_*.log")) + \
                              glob.glob(os.path.join(log_dir, "ucode-execution-*.log"))
            self.session_number = len(existing_sessions)
        except:
            self.session_number = 1

        # Move tracking
        self.move_count = 0
        self.pending_input = False  # Track if we're waiting for output to complete a move
        self.total_moves = self._calculate_total_moves()

        # Log session start
        self.system_logger.info(f"Session started (#{self.session_number})")
        self.log("SESSION START")

    def log(self, message_type, content=""):
        """
        Write message using new logging system with backward compatibility.

        Args:
            message_type (str): The type of message (e.g., 'INPUT', 'OUTPUT', 'ERROR').
            content (str): The content of the message.
        """
        # Sanitize content
        sanitized_content = str(content).replace('\n', '\\n')

        # Route to appropriate logger based on message type
        context = {'move_count': self.move_count, 'session': self.session_number}

        if message_type == "INPUT":
            self.command_logger.info(f"INPUT: {sanitized_content}", extra={'context': context})
            self.pending_input = True

        elif message_type == "OUTPUT":
            self.session_logger.info(f"OUTPUT: {sanitized_content}", extra={'context': context})

            # Track moves: INPUT + OUTPUT = 1 move
            if self.pending_input:
                self.move_count += 1
                self.total_moves += 1
                self.pending_input = False
                self.session_logger.info(f"MOVE {self.move_count} completed (Total: {self.total_moves})",
                                       extra={'context': context})

        elif message_type == "ERROR":
            self.system_logger.error(f"ERROR: {sanitized_content}", extra={'context': context})

        elif message_type == "SESSION START":
            self.system_logger.info("Session started", extra={'context': context})

        elif message_type == "SESSION END":
            self.system_logger.info("Session ended", extra={'context': context})

        else:
            # Generic message
            self.session_logger.info(f"{message_type}: {sanitized_content}", extra={'context': context})

    def log_action(self, action_type, action_data):
        """
        Log a reversible action using structured logging.

        Args:
            action_type (str): Type of action (PANEL_CREATE, FILE_SAVE, etc.)
            action_data (dict): Complete action data including before/after state
        """
        # Create structured logger for actions
        action_logger = get_logger('system-audit', structured=True)

        # Create action entry
        action_entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'type': action_type,
            'data': action_data,
            'session': self.session_number,
            'move': self.move_count
        }

        # Log structured action
        action_logger.info(f"Action: {action_type}", extra={'context': action_entry})

    def get_session_actions(self):
        """
        Parse session logs to extract reversible actions using new logging system.
        Returns list of action dictionaries.
        """
        actions = []
        try:
            # Use new logging manager to search for actions
            matches = self.logging_manager.search_logs("Action:", category="system-audit", days=1)

            for match in matches:
                try:
                    # Extract action data from structured log
                    line = match['line']
                    if 'Action:' in line and self.session_number:
                        # Parse JSON from structured log if available
                        # This is a simplified parser - in practice, structured logs would be easier
                        action_data = {
                            'timestamp': match.get('timestamp', ''),
                            'type': line.split('Action: ')[1].split(' ')[0] if 'Action: ' in line else 'unknown',
                            'session': self.session_number,
                            'file': match['file'],
                            'line_num': match['line_num']
                        }
                        actions.append(action_data)
                except Exception as e:
                    continue

        except Exception as e:
            print(f"Error reading session actions: {e}")

        return actions

    def get_all_sessions(self):
        """
        Get list of all session log files, sorted by date (newest first).
        Returns list of tuples: (filepath, timestamp, session_number)
        """
        sessions = []
        try:
            for filename in os.listdir(self.log_dir):
                if filename.startswith('session_') and filename.endswith('.log'):
                    filepath = os.path.join(self.log_dir, filename)
                    # Extract timestamp from filename
                    timestamp_str = filename.replace('session_', '').replace('.log', '')
                    try:
                        timestamp = datetime.datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                        sessions.append((filepath, timestamp, filename))
                    except:
                        pass

            # Sort by timestamp, newest first
            sessions.sort(key=lambda x: x[1], reverse=True)

            # Add session numbers (1 = current, 2 = previous, etc.)
            numbered_sessions = []
            for i, (filepath, timestamp, filename) in enumerate(sessions):
                numbered_sessions.append((filepath, timestamp, i + 1))

            return numbered_sessions
        except Exception as e:
            print(f"Error listing sessions: {e}")
            return []

    def get_session_summary(self, session_file):
        """
        Get summary of a session: start time, end time, action count.
        """
        try:
            with open(session_file, 'r') as f:
                lines = f.readlines()

            start_time = None
            end_time = None
            action_count = 0

            for line in lines:
                if '[SESSION START]' in line:
                    # Extract timestamp
                    start_time = line.split('[')[1].split(']')[0]
                elif '[SESSION END]' in line:
                    end_time = line.split('[')[1].split(']')[0]
                elif '[ACTION]' in line:
                    action_count += 1

            return {
                'start_time': start_time,
                'end_time': end_time if end_time else 'In Progress',
                'action_count': action_count,
                'is_current': session_file == self.log_file
            }
        except Exception as e:
            return {'error': str(e)}

    def close(self):
        """
        Logs the end of the session.
        """
        self.log("SESSION END")

    def _calculate_total_moves(self):
        """
        Calculate total moves across all previous sessions.
        Returns the cumulative move count.
        """
        total = 0
        try:
            sessions = self.get_all_sessions()
            for filepath, _, _ in sessions:
                if filepath == self.log_file:
                    continue  # Skip current session
                total += self._count_moves_in_session(filepath)
        except Exception as e:
            pass  # If error, start from 0
        return total

    def _count_moves_in_session(self, session_file):
        """Count moves in a specific session file."""
        count = 0
        try:
            with open(session_file, 'r') as f:
                for line in f:
                    if '[MOVE]' in line:
                        count += 1
        except:
            pass
        return count

    def get_move_stats(self):
        """Get current move statistics."""
        return {
            'session_number': self.session_number,
            'session_moves': self.move_count,
            'total_moves': self.total_moves,
            'pending_input': self.pending_input
        }

    def adjust_moves(self, delta):
        """
        Adjust move count (for UNDO/REDO).

        Args:
            delta (int): +1 for REDO, -1 for UNDO
        """
        self.move_count += delta
        self.total_moves += delta
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(self.log_file, 'a') as f:
            action = "REDO" if delta > 0 else "UNDO"
            f.write(f"[{timestamp}] [MOVE_ADJUST] {action} {delta:+d} (Session: {self.move_count}, Total: {self.total_moves})\n")


# Alias for backward compatibility with tests
uDOSLogger = Logger
