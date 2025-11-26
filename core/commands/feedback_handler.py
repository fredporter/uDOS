"""
User Feedback Handler v1.1.0
=============================

Captures user feedback during development and production:
- FEEDBACK: General comments, confusion points, feature requests
- REPORT: Structured error/bug reports with full context
- Integrates with session analytics for context capture

Development Methodology: Local-first, TUI-based iterative development
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

from core.services.session_analytics import SessionAnalytics, FeedbackEntry


@dataclass
class BugReport:
    """Structured bug report"""
    timestamp: str
    category: str  # bug, feature_request, confusion, question, praise
    severity: str  # critical, high, medium, low, info
    title: str
    description: str
    steps_to_reproduce: List[str]
    expected_behavior: str
    actual_behavior: str
    context: Dict[str, Any]
    session_id: str

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)


class FeedbackHandler:
    """
    Handle user feedback collection for v1.1.0 development

    Features:
    - Quick feedback capture during TUI sessions
    - Structured bug reports with full context
    - Automatic session context attachment
    - Integration with session analytics
    """

    def __init__(self,
                 session_analytics: Optional[SessionAnalytics] = None,
                 memory_root: Optional[Path] = None):
        """
        Initialize feedback handler

        Args:
            session_analytics: Session analytics instance
            memory_root: Root path for MEMORY directory
        """
        self.analytics = session_analytics or SessionAnalytics()
        self.memory_root = memory_root or Path("memory")
        # v1.5.0: Flat log structure - feedback files in sandbox/logs/
        self.feedback_dir = self.memory_root / "logs"
        self.feedback_dir.mkdir(parents=True, exist_ok=True)

        self.reports_file = self.feedback_dir / "bug_reports.jsonl"
        self.feedback_file = self.feedback_dir / "user_feedback.jsonl"

    def handle_feedback(self,
                       message: str,
                       category: str = "general",
                       context: Optional[Dict[str, Any]] = None) -> str:
        """
        Handle quick feedback command

        Args:
            message: Feedback message from user
            category: Feedback category (general, confusion, request, praise)
            context: Additional context

        Returns:
            Confirmation message
        """
        if not message or not message.strip():
            return "❌ Feedback message cannot be empty. Usage: FEEDBACK <your message>"

        # Create feedback entry
        feedback = FeedbackEntry(
            timestamp=datetime.now().isoformat(),
            type=category,
            message=message.strip(),
            context=context or {}
        )

        # Log to session analytics
        self.analytics.track_feedback(
            feedback_type=category,
            message=message.strip(),
            context=context or {}
        )        # Save to feedback log
        self._save_feedback(feedback)

        return f"✅ Feedback recorded: '{message[:50]}...'\n" \
               f"   Category: {category}\n" \
               f"   Thank you for helping improve uDOS!"

    def handle_report(self,
                     title: str,
                     description: str,
                     category: str = "bug",
                     severity: str = "medium",
                     steps: Optional[List[str]] = None,
                     expected: str = "",
                     actual: str = "",
                     context: Optional[Dict[str, Any]] = None) -> str:
        """
        Handle structured bug/issue report

        Args:
            title: Short issue title
            description: Detailed description
            category: bug, feature_request, confusion, question
            severity: critical, high, medium, low, info
            steps: Steps to reproduce
            expected: Expected behavior
            actual: Actual behavior
            context: Additional context

        Returns:
            Confirmation message with report ID
        """
        if not title or not title.strip():
            return "❌ Report title required. Usage: REPORT TITLE='...' DESC='...'"

        if not description or not description.strip():
            return "❌ Report description required."

        # Create bug report
        report = BugReport(
            timestamp=datetime.now().isoformat(),
            category=category,
            severity=severity,
            title=title.strip(),
            description=description.strip(),
            steps_to_reproduce=steps or [],
            expected_behavior=expected,
            actual_behavior=actual,
            context=context or {},
            session_id=self.analytics.session_id
        )

        # Save to reports file
        report_id = self._save_report(report)

        # Also track as feedback in session analytics
        feedback = FeedbackEntry(
            timestamp=report.timestamp,
            type=f"report_{category}",
            message=f"{title}: {description}",
            context={
                "severity": severity,
                "report_id": report_id,
                **report.context
            }
        )
        self.analytics.track_feedback(
            feedback_type=f"report_{category}",
            message=f"{title}: {description}",
            context={
                "severity": severity,
                "report_id": report_id,
                **report.context
            }
        )        # Format confirmation
        severity_icon = self._get_severity_icon(severity)
        return f"{severity_icon} Report #{report_id} created: {title}\n" \
               f"   Category: {category}\n" \
               f"   Severity: {severity}\n" \
               f"   Session: {self.analytics.session_id[:8]}...\n" \
               f"   Thank you for the detailed report!"

    def get_feedback_summary(self, limit: int = 10) -> str:
        """
        Get summary of recent feedback

        Args:
            limit: Number of recent items to show

        Returns:
            Formatted feedback summary
        """
        feedback_items = self._load_feedback(limit)

        if not feedback_items:
            return "📊 No feedback recorded yet."

        output = [f"📊 Recent Feedback ({len(feedback_items)} items):"]
        output.append("-" * 60)

        for item in feedback_items:
            timestamp = item.get("timestamp", "unknown")
            category = item.get("type", "general")
            message = item.get("message", "")

            # Format timestamp
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%Y-%m-%d %H:%M")
            except:
                time_str = timestamp

            output.append(f"[{time_str}] {category.upper()}")
            output.append(f"  {message[:80]}...")
            output.append("")

        return "\n".join(output)

    def get_reports_summary(self, limit: int = 10) -> str:
        """
        Get summary of recent bug reports

        Args:
            limit: Number of recent reports to show

        Returns:
            Formatted reports summary
        """
        reports = self._load_reports(limit)

        if not reports:
            return "🐛 No bug reports yet."

        output = [f"🐛 Recent Reports ({len(reports)} items):"]
        output.append("-" * 60)

        for i, report in enumerate(reports, 1):
            title = report.get("title", "Untitled")
            severity = report.get("severity", "medium")
            category = report.get("category", "bug")
            timestamp = report.get("timestamp", "unknown")

            # Format timestamp
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%Y-%m-%d %H:%M")
            except:
                time_str = timestamp

            icon = self._get_severity_icon(severity)
            output.append(f"{icon} #{i} [{category}] {title}")
            output.append(f"     {time_str} | {severity.upper()}")
            output.append("")

        return "\n".join(output)

    # Internal methods

    def _save_feedback(self, feedback: FeedbackEntry) -> None:
        """Save feedback to JSONL file"""
        with open(self.feedback_file, 'a') as f:
            json.dump(asdict(feedback), f)
            f.write('\n')

    def _save_report(self, report: BugReport) -> str:
        """
        Save bug report to JSONL file

        Returns:
            Report ID (timestamp-based)
        """
        with open(self.reports_file, 'a') as f:
            json.dump(report.to_dict(), f)
            f.write('\n')

        # Generate simple ID from timestamp
        report_id = report.timestamp.replace(":", "").replace("-", "").replace(".", "")[:14]
        return report_id

    def _load_feedback(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Load recent feedback entries"""
        if not self.feedback_file.exists():
            return []

        feedback_items = []
        with open(self.feedback_file, 'r') as f:
            for line in f:
                if line.strip():
                    feedback_items.append(json.loads(line))

        # Return most recent first
        return feedback_items[-limit:][::-1]

    def _load_reports(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Load recent bug reports"""
        if not self.reports_file.exists():
            return []

        reports = []
        with open(self.reports_file, 'r') as f:
            for line in f:
                if line.strip():
                    reports.append(json.loads(line))

        # Return most recent first
        return reports[-limit:][::-1]

    def _get_severity_icon(self, severity: str) -> str:
        """Get icon for severity level"""
        icons = {
            "critical": "🚨",
            "high": "⚠️",
            "medium": "📌",
            "low": "ℹ️",
            "info": "💡"
        }
        return icons.get(severity.lower(), "📌")


# Convenience function for global feedback handler
_global_feedback_handler: Optional[FeedbackHandler] = None


def get_feedback_handler() -> FeedbackHandler:
    """Get or create global feedback handler instance"""
    global _global_feedback_handler
    if _global_feedback_handler is None:
        _global_feedback_handler = FeedbackHandler()
    return _global_feedback_handler


def capture_feedback(message: str,
                     category: str = "general",
                     context: Optional[Dict[str, Any]] = None) -> str:
    """
    Convenience function to capture user feedback

    Args:
        message: Feedback message
        category: Feedback category
        context: Additional context

    Returns:
        Confirmation message
    """
    handler = get_feedback_handler()
    return handler.handle_feedback(message, category, context)


def submit_report(title: str,
                 description: str,
                 category: str = "bug",
                 severity: str = "medium",
                 **kwargs) -> str:
    """
    Convenience function to submit bug report

    Args:
        title: Report title
        description: Report description
        category: Report category
        severity: Severity level
        **kwargs: Additional report fields

    Returns:
        Confirmation message
    """
    handler = get_feedback_handler()
    return handler.handle_report(
        title=title,
        description=description,
        category=category,
        severity=severity,
        **kwargs
    )
