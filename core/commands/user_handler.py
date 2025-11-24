"""
uDOS v1.1.0 - User Feedback Command Handler

Processes USER module commands:
- FEEDBACK: Quick user feedback capture
- REPORT: Structured bug/issue reports

Routes to feedback_handler service for persistence and session integration.

Version: 1.1.0
Author: Fred Porter
"""

from core.commands.feedback_handler import FeedbackHandler


class UserCommandHandler:
    """Handler for user feedback and reporting commands."""

    def __init__(self, **kwargs):
        """
        Initialize user command handler.

        Args:
            **kwargs: Common handler kwargs (logger, viewport, etc.)
        """
        self.logger = kwargs.get('logger')
        self.viewport = kwargs.get('viewport')
        self.feedback_handler = FeedbackHandler()

    def handle(self, command, params, grid=None):
        """
        Route USER module commands to appropriate handlers.

        Args:
            command: Command name (FEEDBACK, REPORT)
            params: Command parameters
            grid: Grid instance (optional)

        Returns:
            Command result message
        """
        if command == "FEEDBACK":
            return self._handle_feedback(params)
        elif command == "REPORT":
            return self._handle_report(params)
        else:
            return f"❌ Unknown USER command: {command}\n" \
                   f"   Available: FEEDBACK, REPORT"

    def _handle_feedback(self, params):
        """
        Handle FEEDBACK command.

        Format: FEEDBACK <message> [<category>]

        Args:
            params: [message, category (optional)]

        Returns:
            Feedback confirmation message
        """
        if not params or not params[0]:
            return "❌ FEEDBACK requires a message\n" \
                   "   Usage: FEEDBACK \"<your feedback>\" [TYPE <category>]\n" \
                   "   Categories: general, confusion, request, praise"

        message = params[0]
        category = params[1] if len(params) > 1 else "general"

        # Capture session context if available
        context = {}
        if self.logger:
            # Add recent command history for context
            context["logger_active"] = True

        return self.feedback_handler.handle_feedback(
            message=message,
            category=category,
            context=context
        )

    def _handle_report(self, params):
        """
        Handle REPORT command.

        Format: REPORT <title> <description> [<severity>] [<category>]

        Args:
            params: [title, description, severity (optional), category (optional)]

        Returns:
            Report confirmation message
        """
        if len(params) < 2:
            return "❌ REPORT requires TITLE and DESC\n" \
                   "   Usage: REPORT TITLE=\"<title>\" DESC=\"<description>\" [SEVERITY <level>] [CATEGORY <type>]\n" \
                   "   Severity: critical, high, medium, low, info\n" \
                   "   Category: bug, feature_request, confusion, question"

        title = params[0]
        description = params[1]
        severity = params[2] if len(params) > 2 else "medium"
        category = params[3] if len(params) > 3 else "bug"

        # Capture session context if available
        context = {}
        if self.logger:
            context["logger_active"] = True
        if self.viewport:
            context["viewport_active"] = True

        return self.feedback_handler.handle_report(
            title=title,
            description=description,
            category=category,
            severity=severity,
            context=context
        )
