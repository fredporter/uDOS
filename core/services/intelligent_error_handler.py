"""
uDOS v1.1.0 - Intelligent Error Handler

AI-powered error handling with contextual solutions and user-friendly error resolution flow.

Features:
- Catches exceptions with full context (command, state, history)
- Classifies error types automatically
- Queries Gemini API for intelligent error analysis (role-permitting)
- Presents user with actionable options: Retry, Get Help (AI), Report Bug, Continue
- Logs all error interactions for pattern analysis
- Integrates with session analytics

Version: 1.1.0
Status: Foundation - Active Development
"""

import traceback
import sys
from typing import Dict, Optional, Tuple, Callable, Any
from datetime import datetime
from pathlib import Path


class IntelligentErrorHandler:
    """
    AI-powered error handling with contextual solutions.

    Flow:
    1. Catch exception with full context
    2. Classify error type
    3. Query Gemini API for analysis (if permitted by role)
    4. Present user with options:
       - Retry: Attempt command again
       - Get Help (AI): Get AI-suggested fix
       - Report Bug: Submit to feedback system
       - Continue: Skip and continue
    5. Log interaction for pattern analysis
    """

    def __init__(self, gemini=None, session_analytics=None, audit_logger=None):
        """
        Initialize intelligent error handler.

        Args:
            gemini: Gemini API instance (optional, lazy loaded)
            session_analytics: Session analytics instance (optional)
            audit_logger: API audit logger (optional)
        """
        self.gemini = gemini
        self._session_analytics = session_analytics
        self._audit_logger = audit_logger
        self.user_role = "user"  # Default, updated by command handler

        # Error classification patterns
        self.error_patterns = {
            'FileNotFoundError': {
                'category': 'file_access',
                'severity': 'medium',
                'common_causes': ['File path incorrect', 'File not created yet', 'Wrong directory'],
                'quick_fixes': ['Check file path', 'Use absolute path', 'Create file first']
            },
            'PermissionError': {
                'category': 'file_access',
                'severity': 'high',
                'common_causes': ['Insufficient permissions', 'Read-only file', 'Protected directory'],
                'quick_fixes': ['Check file permissions', 'Run with appropriate role', 'Change file access']
            },
            'ValueError': {
                'category': 'data_validation',
                'severity': 'medium',
                'common_causes': ['Invalid input format', 'Out of range value', 'Wrong data type'],
                'quick_fixes': ['Check input format', 'Validate data', 'Review command parameters']
            },
            'KeyError': {
                'category': 'data_access',
                'severity': 'medium',
                'common_causes': ['Missing configuration', 'Invalid key', 'Data not initialized'],
                'quick_fixes': ['Check configuration', 'Verify key exists', 'Initialize data first']
            },
            'ImportError': {
                'category': 'dependency',
                'severity': 'high',
                'common_causes': ['Missing module', 'Import path incorrect', 'Dependency not installed'],
                'quick_fixes': ['Install missing package', 'Check import path', 'Verify dependencies']
            },
            'AttributeError': {
                'category': 'code_error',
                'severity': 'medium',
                'common_causes': ['Object not initialized', 'Wrong attribute name', 'Type mismatch'],
                'quick_fixes': ['Check object type', 'Verify attribute exists', 'Initialize object first']
            },
            'TypeError': {
                'category': 'data_validation',
                'severity': 'medium',
                'common_causes': ['Wrong argument type', 'Missing arguments', 'Incompatible operation'],
                'quick_fixes': ['Check argument types', 'Verify function signature', 'Convert data type']
            }
        }

    @property
    def session_analytics(self):
        """Lazy load session analytics"""
        if self._session_analytics is None:
            from core.services.session_analytics import get_session_analytics
            self._session_analytics = get_session_analytics()
        return self._session_analytics

    @property
    def audit_logger(self):
        """Lazy load audit logger"""
        if self._audit_logger is None:
            from core.services.api_audit import get_audit_logger
            self._audit_logger = get_audit_logger()
        return self._audit_logger

    def handle_error(
        self,
        error: Exception,
        command: str,
        params: list,
        context: Optional[Dict] = None,
        allow_retry: bool = True,
        retry_callback: Optional[Callable] = None
    ) -> Tuple[str, Optional[str]]:
        """
        Handle an error with intelligent analysis and user options.

        Args:
            error: The exception that occurred
            command: Command that triggered the error
            params: Command parameters
            context: Additional context (current state, etc.)
            allow_retry: Whether retry option should be offered
            retry_callback: Function to call if user chooses retry

        Returns:
            Tuple of (error_message, user_choice)
            user_choice can be: 'retry', 'help', 'report', 'continue', None
        """
        # Classify error
        error_type = type(error).__name__
        error_msg = str(error)

        # Get error classification
        classification = self.error_patterns.get(error_type, {
            'category': 'unknown',
            'severity': 'medium',
            'common_causes': [],
            'quick_fixes': []
        })

        # Build context
        full_context = {
            'command': command,
            'params': params,
            'error_type': error_type,
            'error_message': error_msg,
            'classification': classification,
            'timestamp': datetime.now().isoformat()
        }

        if context:
            full_context.update(context)

        # Get traceback
        tb = traceback.format_exc()
        full_context['traceback'] = tb

        # Log to session analytics
        self.session_analytics.track_error(
            command=command,
            params=params,
            error_type=error_type,
            error_msg=error_msg,
            context=full_context
        )

        # Build user-friendly error message
        error_display = self._format_error_message(
            error_type=error_type,
            error_msg=error_msg,
            command=command,
            classification=classification
        )

        # For now, return the formatted error
        # In full implementation, this would present interactive options
        return error_display, None

    def _format_error_message(
        self,
        error_type: str,
        error_msg: str,
        command: str,
        classification: Dict
    ) -> str:
        """
        Format user-friendly error message.

        Args:
            error_type: Exception class name
            error_msg: Error message
            command: Command that failed
            classification: Error classification info

        Returns:
            Formatted error message string
        """
        severity_icons = {
            'low': '💡',
            'medium': '⚠️',
            'high': '❌',
            'critical': '🔴'
        }

        icon = severity_icons.get(classification['severity'], '⚠️')

        message = f"{icon} Error in {command}\n"
        message += f"{'=' * 60}\n\n"
        message += f"Error Type: {error_type}\n"
        message += f"Message: {error_msg}\n\n"

        if classification['common_causes']:
            message += "💭 Common Causes:\n"
            for cause in classification['common_causes']:
                message += f"  • {cause}\n"
            message += "\n"

        if classification['quick_fixes']:
            message += "🔧 Quick Fixes:\n"
            for fix in classification['quick_fixes']:
                message += f"  • {fix}\n"
            message += "\n"

        message += "💡 Options:\n"
        message += "  • Check your input and try again\n"
        message += "  • Use HELP command for guidance\n"
        message += "  • Use FEEDBACK to report persistent issues\n"

        return message

    async def get_ai_suggestion(
        self,
        error: Exception,
        command: str,
        params: list,
        context: Dict
    ) -> Optional[str]:
        """
        Get AI-powered error analysis and suggestion.

        Args:
            error: The exception
            command: Command that failed
            params: Command parameters
            context: Error context

        Returns:
            AI-suggested fix or None if unavailable
        """
        # Check if user role allows API access
        if self.user_role == "user":
            # For user role, limit AI suggestions to reduce API usage
            # Could implement rate limiting here
            pass

        if not self.gemini:
            return None

        try:
            # Build prompt for AI
            prompt = self._build_ai_prompt(error, command, params, context)

            # Query Gemini
            import time
            start_time = time.time()

            response = await self.gemini.ask(prompt)

            duration_ms = (time.time() - start_time) * 1000

            # Log API usage
            self.audit_logger.log_api_call(
                user_role=self.user_role,
                operation="ERROR_ANALYSIS",
                api_type="gemini",
                query=f"Error: {type(error).__name__} in {command}",
                duration_ms=duration_ms,
                success=True
            )

            return response

        except Exception as e:
            # Failed to get AI suggestion
            self.audit_logger.log_api_call(
                user_role=self.user_role,
                operation="ERROR_ANALYSIS",
                api_type="gemini",
                query=f"Error: {type(error).__name__}",
                success=False,
                error_msg=str(e)
            )
            return None

    def _build_ai_prompt(
        self,
        error: Exception,
        command: str,
        params: list,
        context: Dict
    ) -> str:
        """
        Build prompt for AI error analysis.

        Args:
            error: The exception
            command: Command that failed
            params: Command parameters
            context: Error context

        Returns:
            Formatted prompt string
        """
        error_type = type(error).__name__
        error_msg = str(error)

        prompt = f"""Analyze this uDOS command error and suggest a fix:

Command: {command}
Parameters: {params}
Error Type: {error_type}
Error Message: {error_msg}

Context:
- Category: {context.get('classification', {}).get('category', 'unknown')}
- Severity: {context.get('classification', {}).get('severity', 'medium')}

Please provide:
1. Brief explanation of what went wrong
2. Specific fix for this situation
3. How to prevent this error in the future

Keep the response concise and actionable."""

        return prompt

    def format_interactive_prompt(
        self,
        error_msg: str,
        allow_retry: bool = True,
        ai_suggestion: Optional[str] = None
    ) -> str:
        """
        Format interactive error prompt with options.

        Args:
            error_msg: Formatted error message
            allow_retry: Whether to offer retry option
            ai_suggestion: AI-suggested fix (optional)

        Returns:
            Formatted prompt with options
        """
        prompt = error_msg + "\n"
        prompt += "─" * 60 + "\n"
        prompt += "What would you like to do?\n\n"

        options = []
        if allow_retry:
            options.append("1. Retry - Try the command again")
        options.append("2. Get Help - View detailed help for this command")
        if ai_suggestion:
            options.append("3. AI Suggestion - See AI-powered fix suggestion")
        options.append("4. Report - Report this as a bug")
        options.append("5. Continue - Skip and continue")

        for option in options:
            prompt += f"  {option}\n"

        prompt += "\nEnter your choice (1-5): "

        return prompt


# Global error handler instance
_error_handler: Optional[IntelligentErrorHandler] = None


def get_error_handler() -> IntelligentErrorHandler:
    """Get or create global error handler instance"""
    global _error_handler
    if _error_handler is None:
        _error_handler = IntelligentErrorHandler()
    return _error_handler


def handle_command_error(
    error: Exception,
    command: str,
    params: list,
    context: Optional[Dict] = None
) -> str:
    """
    Convenience function to handle command errors.

    Usage:
        try:
            result = execute_command()
        except Exception as e:
            return handle_command_error(e, "MAP", ["CREATE"], context)

    Args:
        error: The exception
        command: Command name
        params: Command parameters
        context: Additional context

    Returns:
        Formatted error message
    """
    handler = get_error_handler()
    error_msg, choice = handler.handle_error(
        error=error,
        command=command,
        params=params,
        context=context
    )
    return error_msg
