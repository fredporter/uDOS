# uDOS v1.0.0 - Session Logger

import os
import datetime
import json

class Logger:
    """
    A simple logger to record session activity to a file.
    Enhanced to support reversible actions for UNDO/REDO/RESTORE.
    Tracks MOVES (INPUT/OUTPUT pairs) for lifespan management.
    """
    def __init__(self, log_dir="memory/logs/sessions"):
        """
        Initializes the logger and creates a new log file.
        """
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(log_dir, f"session_{timestamp}.log")
        self.log_dir = log_dir

        # Calculate session number (count existing log files + 1)
        existing_sessions = [f for f in os.listdir(log_dir) if f.startswith('session_') and f.endswith('.log')]
        self.session_number = len(existing_sessions)

        # Move tracking
        self.move_count = 0
        self.pending_input = False  # Track if we're waiting for output to complete a move
        self.total_moves = self._calculate_total_moves()

        self.log("SESSION START")

    def log(self, message_type, content=""):
        """
        Writes a message to the log file.
        Tracks MOVES as INPUT/OUTPUT pairs.

        Args:
            message_type (str): The type of message (e.g., 'INPUT', 'OUTPUT', 'ERROR').
            content (str): The content of the message.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Sanitize content by removing newlines to keep the log format clean
        sanitized_content = str(content).replace('\n', '\\n')

        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] [{message_type}] {sanitized_content}\n")

        # Track moves: INPUT + OUTPUT = 1 move
        if message_type == "INPUT":
            self.pending_input = True
        elif message_type == "OUTPUT" and self.pending_input:
            self.move_count += 1
            self.total_moves += 1
            self.pending_input = False
            # Log the move
            with open(self.log_file, 'a') as f:
                f.write(f"[{timestamp}] [MOVE] {self.move_count} (Total: {self.total_moves})\n")

    def log_action(self, action_type, action_data):
        """
        Log a reversible action in structured format for UNDO/REDO/RESTORE.

        Args:
            action_type (str): Type of action (PANEL_CREATE, FILE_SAVE, etc.)
            action_data (dict): Complete action data including before/after state
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        action_entry = {
            'timestamp': timestamp,
            'type': action_type,
            'data': action_data
        }

        # Log as JSON for easy parsing
        action_json = json.dumps(action_entry, separators=(',', ':'))

        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] [ACTION] {action_json}\n")

    def get_session_actions(self):
        """
        Parse current session log to extract all reversible actions.
        Returns list of action dictionaries.
        """
        actions = []
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    if '[ACTION]' in line:
                        # Extract JSON from log line
                        json_start = line.find('{')
                        if json_start != -1:
                            json_str = line[json_start:].strip()
                            action = json.loads(json_str)
                            actions.append(action)
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
