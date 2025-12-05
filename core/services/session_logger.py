"""
Session Logger Wrapper - Backward Compatibility for v1.1.6

This wrapper provides backward compatibility with the old Logger class
while using the new flat-file logging system internally.

Maintains move tracking and session numbering features.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import json
from core.services.logging_manager import get_logger


class SessionLogger:
    """Backward-compatible logger for session tracking.

    Wraps new logging system while maintaining old Logger interface.
    """

    def __init__(self, log_dir: str = "memory/logs"):
        """Initialize session logger.

        Args:
            log_dir: Log directory (maintained for compatibility)
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Calculate session number (count existing session log files)
        existing_sessions = list(self.log_dir.glob('session-commands-*.log'))
        self.session_number = len(existing_sessions)

        # Move tracking
        self.move_count = 0
        self.pending_input = False
        self.total_moves = self._calculate_total_moves()

        # Get logger from new logging system with custom log_dir
        from core.services.logging_manager import LoggingManager
        self._manager = LoggingManager(log_dir=str(self.log_dir))
        self.logger = self._manager.get_logger('session-commands', level=logging.DEBUG)
        self.logger.info('SESSION START')

    def _calculate_total_moves(self) -> int:
        """Calculate total moves across all sessions."""
        total = 0
        for log_file in self.log_dir.glob('session-commands-*.log'):
            try:
                content = log_file.read_text()
                # Count [MOVE] entries
                total += content.count('[MOVE]')
            except Exception:
                pass
        return total

    def log(self, message_type: str, content: str = ""):
        """Log a message (backward-compatible interface).

        Args:
            message_type: Type of message (INPUT, OUTPUT, ERROR, etc.)
            content: Message content
        """
        # Sanitize content
        sanitized_content = str(content).replace('\n', '\\n')

        # Map old message types to new log levels
        level_map = {
            'ERROR': logging.ERROR,
            'WARNING': logging.WARNING,
            'INPUT': logging.INFO,
            'OUTPUT': logging.INFO,
            'EVENT': logging.INFO,
            'ACTION': logging.DEBUG,
            'MOVE': logging.INFO
        }

        level = level_map.get(message_type, logging.INFO)
        message = f"[{message_type}] {sanitized_content}"

        # Log using new system
        self.logger.log(level, message)

        # Track moves: INPUT + OUTPUT = 1 move
        if message_type == "INPUT":
            self.pending_input = True
        elif message_type == "OUTPUT" and self.pending_input:
            self.move_count += 1
            self.total_moves += 1
            self.pending_input = False
            self.logger.info(f"[MOVE] {self.move_count} (Total: {self.total_moves})")

    def log_action(self, action_type: str, action_data: Dict[str, Any]):
        """Log a reversible action in structured format.

        Args:
            action_type: Type of action (PANEL_CREATE, FILE_SAVE, etc.)
            action_data: Action data including before/after state
        """
        action_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': action_type,
            'data': action_data
        }

        # Log as JSON
        action_json = json.dumps(action_entry, separators=(',', ':'))
        self.logger.debug(f"[ACTION] {action_json}")

    def get_session_actions(self):
        """Parse session log to extract reversible actions.

        Returns:
            List of action dictionaries
        """
        actions = []

        # Get today's log file
        date_str = datetime.now().strftime('%Y-%m-%d')
        log_file = self.log_dir / f"session-commands-{date_str}.log"

        if not log_file.exists():
            return actions

        try:
            with open(log_file, 'r') as f:
                for line in f:
                    if '[ACTION]' in line:
                        # Extract JSON from log line
                        json_start = line.find('{')
                        if json_start != -1:
                            json_str = line[json_start:].strip()
                            action = json.loads(json_str)
                            actions.append(action)
        except Exception as e:
            self.logger.error(f"Error reading session actions: {e}")

        return actions

    def get_move_stats(self) -> Dict[str, int]:
        """Get move statistics.

        Returns:
            Dictionary with session_number, move_count, total_moves
        """
        return {
            'session_number': self.session_number,
            'move_count': self.move_count,
            'total_moves': self.total_moves
        }

    def get_session_number(self) -> int:
        """Get current session number."""
        return self.session_number

    def get_total_moves(self) -> int:
        """Get total moves across all sessions."""
        return self.total_moves

    def close(self):
        """Close logger (backward compatibility).

        The new logging system handles cleanup automatically,
        but this method is provided for compatibility with old code.
        """
        self.logger.info('SESSION END')
        # New logging system manages file handles automatically
        pass
