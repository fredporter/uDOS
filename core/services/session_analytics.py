"""
uDOS v1.1.0 - Session Analytics Service

Comprehensive session logging and analysis for developer-driven testing and debugging.

Features:
- Structured JSON session logs with full command context
- Error pattern detection and classification
- Performance metrics tracking (response times, resource usage)
- Session replay capabilities
- Integration with Gemini API for intelligent analysis
- User feedback capture and categorization

Version: 1.1.0
Status: Foundation - Active Development
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class CommandTrace:
    """Single command execution trace"""
    timestamp: str
    command: str
    params: List[str]
    duration_ms: float
    success: bool
    error_type: Optional[str] = None
    error_msg: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    gemini_api_call: Optional[Dict[str, Any]] = None

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class ErrorEntry:
    """Structured error log entry"""
    timestamp: str
    command: str
    params: List[str]
    error_type: str
    error_msg: str
    context: Dict[str, Any]
    resolution: Optional[str] = None  # 'retry', 'help', 'reported', 'ignored'
    ai_suggested_fix: Optional[str] = None
    user_feedback: Optional[str] = None

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class FeedbackEntry:
    """User feedback or confusion point"""
    timestamp: str
    type: str  # 'feedback', 'confusion', 'bug', 'feature_request'
    message: str
    context: Dict[str, Any]
    command_context: Optional[str] = None
    resolved: bool = False

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {k: v for k, v in asdict(self).items() if v is not None}


class SessionAnalytics:
    """
    Comprehensive session logging and analysis for v1.1.0+ development.

    Tracks all user interactions, errors, performance, and feedback in structured
    JSON format to enable:
    - Session replay for debugging
    - Error pattern analysis
    - Performance optimization
    - User experience improvement
    - AI-powered assistance
    """

    def __init__(self, session_dir: str = "memory/sessions", log_dir: str = "memory/logs"):
        """
        Initialize session analytics.

        Args:
            session_dir: Directory for structured session logs
            log_dir: Directory for traditional text logs (compatibility)
        """
        self.session_dir = Path(session_dir) / "auto"
        self.log_dir = Path(log_dir) / "sessions"

        # Ensure directories exist
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Current session state
        self.session_id = self._generate_session_id()
        self.session_file = self.session_dir / f"{self.session_id}.json"
        self.started_at = datetime.now().isoformat()
        self.user_role = "user"  # Default, will be updated when RBAC implemented

        # Session data
        self.commands: List[CommandTrace] = []
        self.errors: List[ErrorEntry] = []
        self.feedback: List[FeedbackEntry] = []

        # Performance tracking
        self.command_timings: List[float] = []

        # Start session
        self._initialize_session()

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def _initialize_session(self):
        """Initialize new session log file"""
        session_data = {
            "session_id": self.session_id,
            "started_at": self.started_at,
            "user_role": self.user_role,
            "commands": [],
            "errors": [],
            "feedback": [],
            "performance": {},
            "metadata": {
                "version": "1.1.0",
                "platform": "macOS",  # Could be detected
                "terminal": "VSCode"  # Could be detected
            }
        }

        with open(self.session_file, 'w') as f:
            json.dump(session_data, f, indent=2)

    def track_command(
        self,
        command: str,
        params: List[str],
        duration_ms: float,
        success: bool,
        error_type: Optional[str] = None,
        error_msg: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        gemini_api_call: Optional[Dict[str, Any]] = None
    ):
        """
        Track command execution.

        Args:
            command: Command name (e.g., "MAP", "OK ASK")
            params: Command parameters
            duration_ms: Execution time in milliseconds
            success: Whether command succeeded
            error_type: Exception type if failed
            error_msg: Error message if failed
            context: Additional context (current panel, planet, etc.)
            gemini_api_call: API usage data if Gemini was called
        """
        trace = CommandTrace(
            timestamp=datetime.now().isoformat(),
            command=command,
            params=params,
            duration_ms=duration_ms,
            success=success,
            error_type=error_type,
            error_msg=error_msg,
            context=context,
            gemini_api_call=gemini_api_call
        )

        self.commands.append(trace)
        self.command_timings.append(duration_ms)

        # Save incrementally (every 5 commands)
        if len(self.commands) % 5 == 0:
            self._save_session()

    def track_error(
        self,
        command: str,
        params: List[str],
        error_type: str,
        error_msg: str,
        context: Dict[str, Any],
        resolution: Optional[str] = None,
        ai_suggested_fix: Optional[str] = None,
        user_feedback: Optional[str] = None
    ):
        """
        Track error occurrence with context.

        Args:
            command: Command that failed
            params: Command parameters
            error_type: Exception type
            error_msg: Error message
            context: System state at error time
            resolution: How user handled it
            ai_suggested_fix: AI-generated solution
            user_feedback: User's comment on the error
        """
        error = ErrorEntry(
            timestamp=datetime.now().isoformat(),
            command=command,
            params=params,
            error_type=error_type,
            error_msg=error_msg,
            context=context,
            resolution=resolution,
            ai_suggested_fix=ai_suggested_fix,
            user_feedback=user_feedback
        )

        self.errors.append(error)
        self._save_session()

    def track_feedback(
        self,
        feedback_type: str,
        message: str,
        context: Dict[str, Any],
        command_context: Optional[str] = None
    ):
        """
        Track user feedback or confusion point.

        Args:
            feedback_type: 'feedback', 'confusion', 'bug', 'feature_request'
            message: User's comment
            context: Current system state
            command_context: Related command if applicable
        """
        feedback = FeedbackEntry(
            timestamp=datetime.now().isoformat(),
            type=feedback_type,
            message=message,
            context=context,
            command_context=command_context
        )

        self.feedback.append(feedback)
        self._save_session()

    def _save_session(self):
        """Save current session state to file"""
        session_data = {
            "session_id": self.session_id,
            "started_at": self.started_at,
            "last_updated": datetime.now().isoformat(),
            "user_role": self.user_role,
            "commands": [cmd.to_dict() for cmd in self.commands],
            "errors": [err.to_dict() for err in self.errors],
            "feedback": [fb.to_dict() for fb in self.feedback],
            "performance": self._calculate_performance(),
            "metadata": {
                "version": "1.1.0",
                "total_commands": len(self.commands),
                "total_errors": len(self.errors),
                "total_feedback": len(self.feedback)
            }
        }

        with open(self.session_file, 'w') as f:
            json.dump(session_data, f, indent=2)

    def _calculate_performance(self) -> Dict[str, Any]:
        """Calculate performance metrics"""
        if not self.command_timings:
            return {}

        return {
            "avg_response_ms": sum(self.command_timings) / len(self.command_timings),
            "max_response_ms": max(self.command_timings),
            "min_response_ms": min(self.command_timings),
            "total_commands": len(self.commands),
            "successful_commands": sum(1 for cmd in self.commands if cmd.success),
            "failed_commands": sum(1 for cmd in self.commands if not cmd.success),
            "error_rate": len(self.errors) / len(self.commands) if self.commands else 0,
            "slow_commands": sum(1 for t in self.command_timings if t > 1000)  # >1s
        }

    def get_error_patterns(self) -> Dict[str, Any]:
        """
        Analyze error patterns for debugging.

        Returns dict with:
        - most_common_errors
        - commands_with_most_errors
        - unresolved_errors
        """
        if not self.errors:
            return {}

        error_types = defaultdict(int)
        error_commands = defaultdict(int)
        unresolved = []

        for error in self.errors:
            error_types[error.error_type] += 1
            error_commands[error.command] += 1
            if not error.resolution:
                unresolved.append(error)

        return {
            "most_common_errors": sorted(
                error_types.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "commands_with_most_errors": sorted(
                error_commands.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "unresolved_errors": len(unresolved),
            "unresolved_details": [err.to_dict() for err in unresolved[:5]]
        }

    def get_session_summary(self) -> str:
        """
        Generate human-readable session summary.

        Returns:
            Formatted string with session statistics
        """
        perf = self._calculate_performance()
        patterns = self.get_error_patterns()

        summary = f"""
📊 Session Analytics Summary
{"=" * 60}

Session ID: {self.session_id}
Started: {self.started_at}
Duration: {self._get_session_duration()}

📈 Performance:
  • Total Commands: {perf.get('total_commands', 0)}
  • Successful: {perf.get('successful_commands', 0)}
  • Failed: {perf.get('failed_commands', 0)}
  • Error Rate: {perf.get('error_rate', 0):.1%}
  • Avg Response Time: {perf.get('avg_response_ms', 0):.0f}ms
  • Slow Commands (>1s): {perf.get('slow_commands', 0)}

❌ Errors:
  • Total Errors: {len(self.errors)}
  • Unresolved: {patterns.get('unresolved_errors', 0)}
"""

        if patterns.get('most_common_errors'):
            summary += "\n  Most Common Errors:\n"
            for error_type, count in patterns['most_common_errors']:
                summary += f"    - {error_type}: {count}\n"

        if self.feedback:
            summary += f"\n💬 User Feedback: {len(self.feedback)} entries\n"

        return summary

    def _get_session_duration(self) -> str:
        """Calculate session duration"""
        start = datetime.fromisoformat(self.started_at)
        duration = datetime.now() - start
        hours = int(duration.total_seconds() // 3600)
        minutes = int((duration.total_seconds() % 3600) // 60)
        return f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

    def close_session(self):
        """Finalize and close current session"""
        self._save_session()

        # Create final summary file
        summary_file = self.session_dir / f"{self.session_id}_summary.txt"
        with open(summary_file, 'w') as f:
            f.write(self.get_session_summary())

    def log_event(self, event_type: str, data: Dict[str, Any]):
        """
        Log a general event to the session.

        Args:
            event_type: Type of event (e.g., 'boundary_violation', 'file_operation')
            data: Event data

        Feature: 1.1.0.14 - Data Architecture Enforcement
        """
        # Add to context of last command if exists
        if self.commands:
            if not self.commands[-1].context:
                self.commands[-1].context = {}
            if 'events' not in self.commands[-1].context:
                self.commands[-1].context['events'] = []
            self.commands[-1].context['events'].append({
                'type': event_type,
                'data': data
            })

        # Save session
        self._save_session()

    def log_boundary_violation(self, source: str, dest: str, command: str, violation_type: str = None):
        """
        Log data boundary violation attempt.

        Args:
            source: Source path
            dest: Destination path
            command: Command that attempted the violation
            violation_type: Type of violation (optional)

        Feature: 1.1.0.14 - Data Architecture Enforcement
        """
        self.log_event('boundary_violation', {
            'command': command,
            'source': source,
            'dest': dest,
            'violation_type': violation_type or 'unauthorized_write',
            'timestamp': datetime.now().isoformat()
        })

    def log_file_operation(self, operation: str, path: str, success: bool, error: str = None):
        """
        Log file operation for boundary tracking.

        Args:
            operation: Operation type ('read', 'write', 'delete', etc.)
            path: File path
            success: Whether operation succeeded
            error: Error message if failed

        Feature: 1.1.0.14 - Data Architecture Enforcement
        """
        self.log_event('file_operation', {
            'operation': operation,
            'path': path,
            'success': success,
            'error': error,
            'timestamp': datetime.now().isoformat()
        })

        self.log_event('file_operation', {
            'operation': operation,
            'path': path,
            'success': success,
            'error': error,
            'timestamp': datetime.now().isoformat()
        })


# Global session analytics instance
_session_analytics: Optional[SessionAnalytics] = None


def get_session_analytics() -> SessionAnalytics:
    """Get or create global session analytics instance"""
    global _session_analytics
    if _session_analytics is None:
        _session_analytics = SessionAnalytics()
    return _session_analytics


def track_command_execution(command: str, params: List[str], start_time: float,
                            success: bool, error=None, context=None, gemini_call=None):
    """
    Convenience function to track command execution.

    Usage in command handlers:
        start = time.time()
        try:
            result = execute_command()
            track_command_execution("MAP", ["CREATE"], start, True)
            return result
        except Exception as e:
            track_command_execution("MAP", ["CREATE"], start, False, error=e)
            raise
    """
    duration_ms = (time.time() - start_time) * 1000

    analytics = get_session_analytics()
    analytics.track_command(
        command=command,
        params=params,
        duration_ms=duration_ms,
        success=success,
        error_type=type(error).__name__ if error else None,
        error_msg=str(error) if error else None,
        context=context,
        gemini_api_call=gemini_call
    )
