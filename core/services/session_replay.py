"""
uDOS v1.1.0 - Session Replay & Analysis System

Developer tools for analyzing and replaying user sessions. Enables:
- Command sequence replay from session logs
- Step-through debugging of user interactions
- Pattern analysis via Gemini API
- UX improvement suggestions
- Error pattern detection

Feature: 1.1.0.12
Version: 1.1.0
Status: Active Development
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict, Counter

from core.services.session_analytics import CommandTrace, ErrorEntry, FeedbackEntry

# Note: OK Assistant deprecated - use extensions/assistant (v1.2.0)
try:
    from extensions.assistant.gemini_service import get_gemini_service
    GeminiCLI = get_gemini_service  # Compatibility alias
except ImportError:
    GeminiCLI = None  # Gemini extension optional


@dataclass
class ReplayStep:
    """Single step in replay sequence"""
    index: int
    timestamp: str
    command: str
    params: List[str]
    duration_ms: float
    success: bool
    error_type: Optional[str] = None
    error_msg: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

    def to_dict(self):
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class PatternInsight:
    """AI-generated insight from pattern analysis"""
    category: str  # 'ux_friction', 'error_pattern', 'confusion_point', 'feature_gap'
    severity: str  # 'critical', 'high', 'medium', 'low'
    description: str
    evidence: List[str]  # Command sequences or error messages
    suggestion: str
    impact: str  # Estimated user impact

    def to_dict(self):
        return asdict(self)


class SessionReplayer:
    """
    Replay and analyze user sessions for debugging and UX improvement.

    Features:
    - Load session logs
    - Replay command sequences
    - Step-through debugging
    - Pause/resume/skip
    - Pattern detection
    """

    def __init__(self, session_dir: str = "memory/logs/sessions/auto"):
        """
        Initialize session replayer.

        Args:
            session_dir: Directory containing session log files
        """
        self.session_dir = Path(session_dir)
        self.current_session: Optional[Dict[str, Any]] = None
        self.replay_steps: List[ReplayStep] = []
        self.current_step: int = 0
        self.paused: bool = False

    def load_session(self, session_id: str) -> bool:
        """
        Load session from JSON log file.

        Args:
            session_id: Session ID or filename (with or without .json)

        Returns:
            True if session loaded successfully
        """
        # Handle both session_YYYYMMDD_HHMMSS and full filename
        if not session_id.endswith('.json'):
            session_file = self.session_dir / f"{session_id}.json"
        else:
            session_file = self.session_dir / session_id

        if not session_file.exists():
            return False

        try:
            with open(session_file, 'r') as f:
                self.current_session = json.load(f)

            # Convert to ReplayStep objects
            self.replay_steps = []
            for idx, cmd in enumerate(self.current_session.get('commands', [])):
                step = ReplayStep(
                    index=idx,
                    timestamp=cmd.get('timestamp', ''),
                    command=cmd.get('command', ''),
                    params=cmd.get('params', []),
                    duration_ms=cmd.get('duration_ms', 0),
                    success=cmd.get('success', True),
                    error_type=cmd.get('error_type'),
                    error_msg=cmd.get('error_msg'),
                    context=cmd.get('context')
                )
                self.replay_steps.append(step)

            self.current_step = 0
            self.paused = False
            return True

        except (json.JSONDecodeError, IOError):
            return False

    def list_available_sessions(self) -> List[Dict[str, str]]:
        """
        List all available session logs.

        Returns:
            List of dicts with session metadata
        """
        sessions = []
        for session_file in sorted(self.session_dir.glob('session_*.json'), reverse=True):
            try:
                with open(session_file, 'r') as f:
                    data = json.load(f)

                sessions.append({
                    'session_id': data.get('session_id', session_file.stem),
                    'started_at': data.get('started_at', ''),
                    'total_commands': data.get('metadata', {}).get('total_commands', 0),
                    'total_errors': data.get('metadata', {}).get('total_errors', 0),
                    'filename': session_file.name
                })
            except (json.JSONDecodeError, IOError):
                continue

        return sessions

    def get_step(self, index: Optional[int] = None) -> Optional[ReplayStep]:
        """
        Get replay step at index (or current step).

        Args:
            index: Step index (None for current step)

        Returns:
            ReplayStep or None if invalid
        """
        if not self.replay_steps:
            return None

        idx = index if index is not None else self.current_step
        if 0 <= idx < len(self.replay_steps):
            return self.replay_steps[idx]
        return None

    def next_step(self) -> Optional[ReplayStep]:
        """Advance to next step"""
        if self.current_step < len(self.replay_steps) - 1:
            self.current_step += 1
            return self.get_step()
        return None

    def previous_step(self) -> Optional[ReplayStep]:
        """Go back to previous step"""
        if self.current_step > 0:
            self.current_step -= 1
            return self.get_step()
        return None

    def jump_to(self, index: int) -> Optional[ReplayStep]:
        """Jump to specific step"""
        if 0 <= index < len(self.replay_steps):
            self.current_step = index
            return self.get_step()
        return None

    def find_errors(self) -> List[ReplayStep]:
        """Find all steps with errors"""
        return [step for step in self.replay_steps if not step.success]

    def find_slow_commands(self, threshold_ms: float = 1000) -> List[ReplayStep]:
        """Find steps exceeding duration threshold"""
        return [step for step in self.replay_steps if step.duration_ms > threshold_ms]

    def find_command_sequence(self, commands: List[str]) -> List[int]:
        """
        Find indices where command sequence occurs.

        Args:
            commands: List of command names to match

        Returns:
            List of starting indices where sequence was found
        """
        matches = []
        seq_len = len(commands)

        for i in range(len(self.replay_steps) - seq_len + 1):
            if all(self.replay_steps[i + j].command == commands[j] for j in range(seq_len)):
                matches.append(i)

        return matches

    def get_session_stats(self) -> Dict[str, Any]:
        """Calculate session statistics"""
        if not self.current_session:
            return {}

        commands = self.replay_steps
        errors = self.current_session.get('errors', [])
        feedback = self.current_session.get('feedback', [])

        # Command frequency
        command_counts = Counter(step.command for step in commands)

        # Error analysis
        error_types = Counter(err.get('error_type', 'Unknown') for err in errors)

        # Performance
        durations = [step.duration_ms for step in commands]
        avg_duration = sum(durations) / len(durations) if durations else 0

        return {
            'session_id': self.current_session.get('session_id'),
            'started_at': self.current_session.get('started_at'),
            'total_commands': len(commands),
            'total_errors': len(errors),
            'total_feedback': len(feedback),
            'error_rate': len(errors) / len(commands) if commands else 0,
            'avg_duration_ms': avg_duration,
            'most_used_commands': command_counts.most_common(5),
            'most_common_errors': error_types.most_common(5),
            'slow_commands': len([d for d in durations if d > 1000])
        }

    def format_step(self, step: ReplayStep, show_context: bool = False) -> str:
        """
        Format replay step for display.

        Args:
            step: ReplayStep to format
            show_context: Include context information

        Returns:
            Formatted string
        """
        status = "✅" if step.success else "❌"
        params_str = " " + " ".join(step.params) if step.params else ""

        output = f"[{step.index}] {status} {step.command}{params_str} ({step.duration_ms:.0f}ms)"

        if not step.success:
            output += f"\n    Error: {step.error_type}: {step.error_msg}"

        if show_context and step.context:
            output += f"\n    Context: {json.dumps(step.context, indent=4)}"

        return output


class SessionPatternAnalyzer:
    """
    Analyze sessions for UX patterns and improvement opportunities.

    Uses Gemini API for intelligent pattern recognition and suggestion generation.
    """

    def __init__(self, gemini_service: Optional[GeminiCLI] = None):
        """
        Initialize pattern analyzer.

        Args:
            gemini_service: Optional GeminiCLI instance (creates if None, may fail if no API key)
        """
        try:
            self.gemini = gemini_service or GeminiCLI()
            self.gemini_available = True
        except (FileNotFoundError, ValueError, RuntimeError):
            # Gemini not configured - use local analysis only
            self.gemini = None
            self.gemini_available = False

        self.insights: List[PatternInsight] = []

    def analyze_session(self, session_data: Dict[str, Any]) -> List[PatternInsight]:
        """
        Analyze session for patterns and generate insights.

        Args:
            session_data: Session JSON data

        Returns:
            List of PatternInsight objects
        """
        self.insights = []

        # Local pattern detection
        self._detect_error_patterns(session_data)
        self._detect_confusion_points(session_data)
        self._detect_ux_friction(session_data)

        # AI-powered analysis (if available)
        if self.gemini_available and self.gemini:
            ai_insights = self._ai_analyze_patterns(session_data)
            self.insights.extend(ai_insights)

        return sorted(self.insights, key=lambda x: self._severity_score(x.severity), reverse=True)

    def _detect_error_patterns(self, session_data: Dict[str, Any]):
        """Detect repeated error patterns"""
        errors = session_data.get('errors', [])
        if not errors:
            return

        # Group by error type
        error_groups = defaultdict(list)
        for err in errors:
            error_groups[err.get('error_type', 'Unknown')].append(err)

        # Look for repeated errors
        for error_type, occurrences in error_groups.items():
            if len(occurrences) >= 3:  # Threshold for pattern
                commands = [err.get('command', '') for err in occurrences]

                insight = PatternInsight(
                    category='error_pattern',
                    severity='high' if len(occurrences) >= 5 else 'medium',
                    description=f"Repeated {error_type} errors in {', '.join(set(commands))} commands",
                    evidence=[f"{err.get('command')} {err.get('params', [])}" for err in occurrences[:3]],
                    suggestion=f"Review error handling in affected commands. {len(occurrences)} occurrences detected.",
                    impact=f"{len(occurrences)} user disruptions"
                )
                self.insights.append(insight)

    def _detect_confusion_points(self, session_data: Dict[str, Any]):
        """Detect user confusion from feedback and command patterns"""
        feedback = session_data.get('feedback', [])
        commands = session_data.get('commands', [])

        # Look for help/doc commands after errors
        for i, cmd in enumerate(commands[:-1]):
            if not cmd.get('success') and i + 1 < len(commands):
                next_cmd = commands[i + 1]
                if next_cmd.get('command', '').upper() in ['HELP', 'DOC', 'DOCS', 'MANUAL']:
                    insight = PatternInsight(
                        category='confusion_point',
                        severity='medium',
                        description=f"User sought help after {cmd.get('command')} error",
                        evidence=[f"{cmd.get('command')} → {next_cmd.get('command')}"],
                        suggestion=f"Improve error message for {cmd.get('command')} to be more actionable",
                        impact="User had to manually seek documentation"
                    )
                    self.insights.append(insight)

        # Analyze confusion feedback
        confusion_feedback = [fb for fb in feedback if fb.get('type') == 'confusion']
        if confusion_feedback:
            for fb in confusion_feedback:
                insight = PatternInsight(
                    category='confusion_point',
                    severity='high',
                    description=f"User reported confusion: {fb.get('message', '')[:50]}...",
                    evidence=[fb.get('command_context', 'N/A')],
                    suggestion="Review UX and documentation for this interaction",
                    impact="Direct user confusion reported"
                )
                self.insights.append(insight)

    def _detect_ux_friction(self, session_data: Dict[str, Any]):
        """Detect UX friction points from command patterns"""
        commands = session_data.get('commands', [])

        # Look for command retries (same command repeated)
        for i in range(len(commands) - 2):
            if (commands[i].get('command') == commands[i + 1].get('command') == commands[i + 2].get('command')):
                cmd_name = commands[i].get('command')

                insight = PatternInsight(
                    category='ux_friction',
                    severity='medium',
                    description=f"User repeated {cmd_name} command 3+ times",
                    evidence=[f"{cmd_name} attempted at indices {i}, {i+1}, {i+2}"],
                    suggestion=f"Review {cmd_name} command feedback - may need clearer success confirmation",
                    impact="User uncertainty about command success"
                )
                self.insights.append(insight)
                break  # Avoid duplicate insights

        # Look for slow commands
        slow_commands = [cmd for cmd in commands if cmd.get('duration_ms', 0) > 2000]
        if len(slow_commands) > 3:
            cmd_types = Counter(cmd.get('command') for cmd in slow_commands)
            slowest = cmd_types.most_common(1)[0]

            insight = PatternInsight(
                category='ux_friction',
                severity='medium',
                description=f"{slowest[0]} command consistently slow ({slowest[1]} instances >2s)",
                evidence=[f"{cmd.get('command')} ({cmd.get('duration_ms', 0):.0f}ms)" for cmd in slow_commands[:3]],
                suggestion=f"Optimize {slowest[0]} performance or add progress indicator",
                impact="User waiting time degraded experience"
            )
            self.insights.append(insight)

    def _ai_analyze_patterns(self, session_data: Dict[str, Any]) -> List[PatternInsight]:
        """
        Use Gemini API to analyze patterns and suggest improvements.

        Args:
            session_data: Session JSON data

        Returns:
            List of AI-generated insights
        """
        insights = []

        # Prepare session summary for AI
        commands = session_data.get('commands', [])
        errors = session_data.get('errors', [])
        feedback = session_data.get('feedback', [])

        summary = {
            'total_commands': len(commands),
            'command_sequence': [cmd.get('command') for cmd in commands[:50]],  # First 50
            'errors': [
                {
                    'type': err.get('error_type'),
                    'command': err.get('command'),
                    'message': err.get('error_msg', '')[:100]
                } for err in errors[:10]
            ],
            'feedback': [
                {
                    'type': fb.get('type'),
                    'message': fb.get('message', '')[:100]
                } for fb in feedback
            ],
            'performance': session_data.get('performance', {})
        }

        prompt = f"""Analyze this user session from uDOS (text-based survival/knowledge system).

Session Summary:
{json.dumps(summary, indent=2)}

Identify:
1. UX friction points (confusing flows, unclear feedback)
2. Error patterns (repeated failures, unclear error messages)
3. Feature gaps (what user tried to do but couldn't)
4. Usability improvements

Return analysis as JSON array of insights:
[{{
  "category": "ux_friction|error_pattern|confusion_point|feature_gap",
  "severity": "critical|high|medium|low",
  "description": "Brief description",
  "evidence": ["specific command or pattern"],
  "suggestion": "Actionable improvement",
  "impact": "Expected user benefit"
}}]

Focus on actionable insights that improve user experience."""

        try:
            response_text = self.gemini.ask(prompt)

            # Extract JSON from response
            if response_text and not response_text.startswith('❌'):
                # Try to find JSON array in response
                start = response_text.find('[')
                end = response_text.rfind(']') + 1
                if start != -1 and end > start:
                    json_str = response_text[start:end]
                    ai_insights_data = json.loads(json_str)

                    for insight_data in ai_insights_data:
                        insight = PatternInsight(
                            category=insight_data.get('category', 'feature_gap'),
                            severity=insight_data.get('severity', 'low'),
                            description=insight_data.get('description', ''),
                            evidence=insight_data.get('evidence', []),
                            suggestion=insight_data.get('suggestion', ''),
                            impact=insight_data.get('impact', '')
                        )
                        insights.append(insight)

        except (json.JSONDecodeError, KeyError, Exception) as e:
            # AI analysis failed - gracefully degrade
            pass

        return insights

    def _severity_score(self, severity: str) -> int:
        """Convert severity to numeric score for sorting"""
        scores = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        return scores.get(severity, 0)

    def generate_report(self, session_data: Dict[str, Any]) -> str:
        """
        Generate comprehensive analysis report.

        Args:
            session_data: Session JSON data

        Returns:
            Formatted report string
        """
        insights = self.analyze_session(session_data)

        report = f"""
🔍 Session Pattern Analysis Report
{"=" * 70}

Session: {session_data.get('session_id', 'Unknown')}
Started: {session_data.get('started_at', 'Unknown')}

📊 Overview:
  • Commands: {len(session_data.get('commands', []))}
  • Errors: {len(session_data.get('errors', []))}
  • Feedback: {len(session_data.get('feedback', []))}
  • Insights: {len(insights)}

"""

        if insights:
            # Group by category
            by_category = defaultdict(list)
            for insight in insights:
                by_category[insight.category].append(insight)

            for category in ['error_pattern', 'ux_friction', 'confusion_point', 'feature_gap']:
                category_insights = by_category.get(category, [])
                if not category_insights:
                    continue

                report += f"\n{'─' * 70}\n"
                report += f"📌 {category.replace('_', ' ').title()}\n"
                report += f"{'─' * 70}\n\n"

                for idx, insight in enumerate(category_insights, 1):
                    severity_icon = {
                        'critical': '🔴',
                        'high': '🟠',
                        'medium': '🟡',
                        'low': '🟢'
                    }.get(insight.severity, '⚪')

                    report += f"{idx}. {severity_icon} [{insight.severity.upper()}] {insight.description}\n"
                    report += f"   Evidence: {', '.join(insight.evidence[:3])}\n"
                    report += f"   💡 Suggestion: {insight.suggestion}\n"
                    report += f"   Impact: {insight.impact}\n\n"

        else:
            report += "✅ No significant issues detected in this session.\n"

        report += f"\n{'=' * 70}\n"
        report += f"Report generated: {datetime.now().isoformat()}\n"

        return report


# Convenience functions for common operations

def replay_session(session_id: str) -> Optional[SessionReplayer]:
    """
    Quick session replay setup.

    Args:
        session_id: Session ID to replay

    Returns:
        SessionReplayer instance or None if session not found
    """
    replayer = SessionReplayer()
    if replayer.load_session(session_id):
        return replayer
    return None


def analyze_session_file(session_file: str) -> str:
    """
    Quick session analysis.

    Args:
        session_file: Path to session JSON file

    Returns:
        Analysis report string
    """
    try:
        with open(session_file, 'r') as f:
            session_data = json.load(f)

        analyzer = SessionPatternAnalyzer()
        return analyzer.generate_report(session_data)

    except (IOError, json.JSONDecodeError) as e:
        return f"Error analyzing session: {e}"


def list_sessions() -> List[Dict[str, str]]:
    """
    List all available sessions.

    Returns:
        List of session metadata dicts
    """
    replayer = SessionReplayer()
    return replayer.list_available_sessions()
