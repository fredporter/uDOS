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

"""
uDOS v1.2.4 - User Feedback Command Handler

Processes USER module commands:
- FEEDBACK: Quick user feedback capture (local)
- FEEDBACK --github: Open pre-filled GitHub Issue/Discussion (v1.2.4)
- REPORT: Structured bug/issue reports

Routes to feedback_handler service for persistence and session integration.

Version: 1.2.4 (added GitHub browser integration)
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

        Format: 
            FEEDBACK <message> [<category>] - Local feedback
            FEEDBACK --github [--open] [--issue|--discussion] [--bug|--feature|--question] - GitHub

        Args:
            params: Command parameters with optional flags

        Returns:
            Feedback confirmation message
        """
        if not params:
            return self._feedback_help()

        # Parse flags
        flags = {
            "github": "--github" in params,
            "open": "--open" in params,
            "issue": "--issue" in params,
            "discussion": "--discussion" in params,
            "bug": "--bug" in params,
            "feature": "--feature" in params,
            "question": "--question" in params,
            "idea": "--idea" in params,
            "general": "--general" in params
        }

        # Handle GitHub feedback
        if flags["github"]:
            return self._handle_github_feedback(flags)

        # Handle local feedback (original behavior)
        # Filter out any flags to get actual message
        message_parts = [p for p in params if not p.startswith("--")]
        
        if not message_parts:
            return "❌ FEEDBACK requires a message\n" \
                   "   Usage: FEEDBACK \"<your feedback>\" [TYPE <category>]\n" \
                   "   Or use: FEEDBACK --github for browser-based feedback"

        message = message_parts[0]
        category = message_parts[1] if len(message_parts) > 1 else "general"

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

    def _handle_github_feedback(self, flags):
        """
        Handle GitHub browser-based feedback.

        Args:
            flags: Parsed flags dictionary

        Returns:
            Confirmation message with GitHub URL
        """
        # Determine feedback type (issue vs discussion)
        if flags["issue"]:
            feedback_type = "issue"
        elif flags["discussion"]:
            feedback_type = "discussion"
        else:
            # Default to discussion for general feedback
            feedback_type = "discussion"

        # Determine category
        if flags["bug"]:
            category = "bug"
        elif flags["feature"]:
            category = "feature"
        elif flags["question"]:
            category = "question"
        elif flags["idea"]:
            category = "idea"
        else:
            category = "general"

        # Call GitHub feedback handler
        return self.feedback_handler.handle_github_feedback(
            feedback_type=feedback_type,
            category=category,
            pre_fill=None,
            auto_open=flags["open"]
        )

    def _feedback_help(self):
        """Return FEEDBACK command help text."""
        return """
📝 FEEDBACK Command

Local Feedback (saved to memory/logs/):
  FEEDBACK "<message>" [TYPE <category>]
  
  Categories: general, confusion, request, praise
  
  Example:
    FEEDBACK "Love the hot reload feature!"
    FEEDBACK "Confused about workflow syntax" TYPE confusion

GitHub Feedback (browser-based, no API key needed):
  FEEDBACK --github [--open] [--issue|--discussion] [--category]
  
  Types:
    --issue       : Bug report or feature request
    --discussion  : General feedback, questions, ideas
  
  Categories:
    --bug         : Report a bug (creates Issue)
    --feature     : Request a feature (creates Issue)
    --question    : Ask a question (creates Discussion)
    --idea        : Share an idea (creates Discussion)
    --general     : General feedback (creates Discussion)
  
  Flags:
    --open        : Automatically open browser (skip confirmation)
  
  Examples:
    FEEDBACK --github --bug
    FEEDBACK --github --feature --open
    FEEDBACK --github --discussion --question
    FEEDBACK --github --idea --open

All feedback helps improve uDOS! 🚀
""".strip()

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
