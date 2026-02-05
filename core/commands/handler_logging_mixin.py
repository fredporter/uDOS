"""
Handler Logging Mixin - Instrumentation for all command handlers

Provides consistent logging and performance tracking across all handlers.
Automatically tracks command execution with timing, parameters, and results.

Usage:
    class MyHandler(BaseCommandHandler, HandlerLoggingMixin):
        def handle(self, command, params, grid, parser):
            with self.trace_command(command, params) as trace:
                # Your handler logic
                result = self.do_something()
                trace.add_event('operation_complete', {'items': len(result)})
                return result

Features:
    - Automatic timing of command execution
    - Parameter logging (sanitized)
    - Result status tracking
    - Performance profiling via DevTrace
    - Error tracking and categorization
    - Audit trail for sensitive operations

Author: uDOS Engineering
Version: v1.0.0
Date: 2026-01-28
"""

from contextlib import contextmanager
from datetime import datetime
from typing import Dict, Any, Optional, List
import sys


class HandlerLoggingMixin:
    """Mixin for automatic handler instrumentation.
    
    Add this to any handler class to get automatic logging:
    
        class MyHandler(BaseCommandHandler, HandlerLoggingMixin):
            ...
    
    Then use in handle() method:
    
        def handle(self, command, params, grid, parser):
            with self.trace_command(command, params) as trace:
                result = self.do_work()
                trace.add_event('work_done', {'status': 'ok'})
                return result
    """
    
    # Handlers can override these
    SENSITIVE_PARAMS = ['password', 'key', 'token', 'secret', 'api_key', 'credentials']
    SENSITIVE_KEYS = ['password', 'api_key', 'token', 'secret']
    
    def _get_logger(self):
        """Get unified logger (lazy import to avoid circular deps)."""
        try:
            from core.services.unified_logging import get_unified_logger
            return get_unified_logger()
        except:
            return None
    
    def _sanitize_params(self, params: List[str]) -> List[str]:
        """Remove sensitive parameters from logging.
        
        Args:
            params: Parameter list
        
        Returns:
            Sanitized parameter list
        """
        if not params:
            return []
        
        sanitized = []
        for param in params:
            param_lower = param.lower()
            
            # Check if param is a sensitive key
            is_sensitive = any(
                sensitive in param_lower 
                for sensitive in self.SENSITIVE_PARAMS
            )
            
            if is_sensitive:
                sanitized.append("[REDACTED]")
            else:
                # Truncate long params
                if len(param) > 100:
                    sanitized.append(param[:97] + "...")
                else:
                    sanitized.append(param)
        
        return sanitized
    
    def _get_handler_category(self, command: str) -> str:
        """Categorize command for logging.
        
        Args:
            command: Command name
        
        Returns:
            Category name (navigation, game-state, system, etc.)
        """
        nav_commands = {'MAP', 'PANEL', 'GOTO', 'FIND', 'TELL'}
        game_commands = {'BAG', 'GRAB', 'SPAWN', 'SAVE', 'LOAD'}
        system_commands = {'REPAIR', 'REBOOT', 'DESTROY', 'BACKUP', 'RESTORE'}
        npc_commands = {'NPC', 'TALK', 'REPLY'}
        wizard_commands = {'CONFIG', 'PROVIDER', 'WIZARD', 'AI'}
        
        cmd_upper = command.upper()
        
        if cmd_upper in nav_commands:
            return 'navigation'
        elif cmd_upper in game_commands:
            return 'game_state'
        elif cmd_upper in system_commands:
            return 'system'
        elif cmd_upper in npc_commands:
            return 'npc'
        elif cmd_upper in wizard_commands:
            return 'wizard'
        else:
            return 'other'
    
    @contextmanager
    def trace_command(self, command: str, params: List[str]):
        """Context manager for command tracing.
        
        Usage:
            with self.trace_command(command, params) as trace:
                result = self.do_work()
                trace.add_event('milestone', {'status': 'ok'})
                return result
        
        Args:
            command: Command name
            params: Parameter list
        
        Yields:
            CommandTrace object for event tracking
        """
        unified_logger = self._get_logger()
        trace = CommandTrace(
            command=command,
            params=params,
            logger=unified_logger,
            sanitize_fn=self._sanitize_params,
            category=self._get_handler_category(command)
        )
        
        trace.start()
        try:
            yield trace
        except Exception as e:
            trace.record_error(e)
            raise
        finally:
            trace.finish()
    
    def log_param_error(self, command: str, params: List[str], error: str):
        """Log a parameter validation error.
        
        Args:
            command: Command name
            params: Parameter list
            error: Error message
        """
        unified_logger = self._get_logger()
        if unified_logger:
            sanitized = self._sanitize_params(params)
            unified_logger.log_core(
                category='command_error',
                message=f'{command} parameter error',
                metadata={
                    'command': command,
                    'params': sanitized,
                    'error': error,
                    'error_type': 'param_validation'
                }
            )
    
    def log_permission_denied(self, command: str, reason: str):
        """Log a permission denied event.
        
        Args:
            command: Command name
            reason: Reason for denial
        """
        unified_logger = self._get_logger()
        if unified_logger:
            unified_logger.log_core(
                category='permission_denied',
                message=f'{command} permission denied',
                metadata={
                    'command': command,
                    'reason': reason
                }
            )
    
    def log_operation(self, command: str, operation: str, metadata: Dict[str, Any]):
        """Log a specific operation within command.
        
        Args:
            command: Command name
            operation: Operation name
            metadata: Operation metadata
        """
        unified_logger = self._get_logger()
        if unified_logger:
            unified_logger.log_core(
                category=f'command_{command.lower()}',
                message=f'{operation}',
                metadata={
                    'command': command,
                    'operation': operation,
                    **metadata
                }
            )


class CommandTrace:
    """Tracks command execution with timing and events."""
    
    def __init__(self, command: str, params: List[str], logger=None, 
                 sanitize_fn=None, category: str = 'other'):
        """Initialize command trace.
        
        Args:
            command: Command name
            params: Parameter list
            logger: UnifiedLogger instance
            sanitize_fn: Function to sanitize params
            category: Command category
        """
        self.command = command
        self.params = params or []
        self.logger = logger
        self.sanitize_fn = sanitize_fn or (lambda x: x)
        self.category = category
        
        self.start_time = None
        self.finish_time = None
        self.duration = 0
        self.error = None
        self.events: List[Dict[str, Any]] = []
        self.result_status = 'pending'
    
    def start(self):
        """Mark trace start."""
        self.start_time = datetime.now()
        
        if self.logger:
            sanitized = self.sanitize_fn(self.params)
            self.logger.log_core(
                category=f'command_start_{self.category}',
                message=f'{self.command} started',
                metadata={
                    'command': self.command,
                    'params': sanitized,
                    'timestamp': self.start_time.isoformat()
                }
            )
    
    def finish(self):
        """Mark trace finish."""
        self.finish_time = datetime.now()
        self.duration = (self.finish_time - self.start_time).total_seconds()
        
        if self.logger:
            metadata = {
                'command': self.command,
                'duration_seconds': round(self.duration, 3),
                'status': self.result_status,
                'event_count': len(self.events),
                'timestamp': self.finish_time.isoformat()
            }
            
            if self.error:
                metadata['error'] = str(self.error)
                metadata['error_type'] = type(self.error).__name__
            
            if self.events:
                metadata['events'] = self.events
            
            self.logger.log_core(
                category=f'command_finish_{self.category}',
                message=f'{self.command} finished ({self.result_status})',
                metadata=metadata
            )
    
    def add_event(self, event_name: str, data: Dict[str, Any] = None):
        """Record an event during command execution.
        
        Args:
            event_name: Event name
            data: Event data
        """
        timestamp = datetime.now()
        event = {
            'name': event_name,
            'timestamp': timestamp.isoformat(),
            'elapsed_seconds': (timestamp - self.start_time).total_seconds()
        }
        
        if data:
            event.update(data)
        
        self.events.append(event)
    
    def set_status(self, status: str):
        """Set result status (success, error, partial, cancelled).
        
        Args:
            status: Status name
        """
        self.result_status = status
    
    def record_error(self, error: Exception):
        """Record an error that occurred.
        
        Args:
            error: Exception instance
        """
        self.error = error
        self.result_status = 'error'
        self.add_event('error_occurred', {
            'error_type': type(error).__name__,
            'error_message': str(error)
        })
    
    def mark_milestone(self, milestone: str):
        """Mark a key milestone in execution.
        
        Args:
            milestone: Milestone name
        """
        self.add_event('milestone', {'milestone': milestone})
