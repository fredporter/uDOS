"""
Debug Engine Service - DEV MODE Integration (v1.2.2)

Provides comprehensive debugging capabilities for uPY scripts including:
- Breakpoint management (line-based and conditional)
- Step-through execution (step, step-over, step-into)
- Variable inspection at any execution point
- Call stack tracking
- Trace logging integration with unified logger

Usage:
    from core.services.debug_engine import DebugEngine
    from core.services.unified_logger import UnifiedLogger

    logger = UnifiedLogger()
    debug = DebugEngine(logger)

    debug.enable()
    debug.set_breakpoint(line=10, condition="counter > 5")

    # In execution loop:
    if debug.should_pause(current_line):
        debug.pause(current_line, variables)
        # Wait for user command (STEP, CONTINUE, INSPECT)
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone


@dataclass
class Breakpoint:
    """Represents a breakpoint in script execution."""
    line: int
    condition: Optional[str] = None
    enabled: bool = True
    hit_count: int = 0
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class CallFrame:
    """Represents a frame in the call stack."""
    script_name: str
    line: int
    function: Optional[str] = None
    variables: Dict[str, Any] = None

    def __post_init__(self):
        if self.variables is None:
            self.variables = {}

    def to_dict(self) -> dict:
        """Convert to dictionary for display."""
        return {
            'script': self.script_name,
            'line': self.line,
            'function': self.function or '<main>',
            'variables_count': len(self.variables)
        }


class DebugEngine:
    """
    Core debugging engine for uPY script execution.

    Provides breakpoint management, step-through execution, variable inspection,
    and integration with the unified logging system for trace logging.
    """

    def __init__(self, logger=None):
        """
        Initialize the debug engine.

        Args:
            logger: UnifiedLogger instance for trace logging (optional)
        """
        self.logger = logger
        self.enabled = False
        self.breakpoints: Dict[int, Breakpoint] = {}
        self.current_line = 0
        self.current_script = ""
        self.paused = False
        self.step_mode = False  # True when stepping line-by-line
        self.call_stack: List[CallFrame] = []
        self.watch_vars: List[str] = []  # Variable watch list
        self.trace_enabled = False
        self.execution_history: List[Tuple[int, str]] = []  # (line, code) history
        self.max_history = 100  # Keep last 100 lines

    def enable(self):
        """Enable debug mode."""
        self.enabled = True
        if self.logger:
            self.logger.log_debug("Debug mode enabled")

    def disable(self):
        """Disable debug mode and clear state."""
        self.enabled = False
        self.paused = False
        self.step_mode = False
        if self.logger:
            self.logger.log_debug("Debug mode disabled")

    def set_breakpoint(self, line: int, condition: Optional[str] = None) -> bool:
        """
        Set a breakpoint at the specified line.

        Args:
            line: Line number (1-based)
            condition: Optional condition expression (e.g., "counter > 5")

        Returns:
            True if breakpoint was set successfully
        """
        if line < 1:
            return False

        self.breakpoints[line] = Breakpoint(line=line, condition=condition)

        if self.logger:
            cond_str = f" (condition: {condition})" if condition else ""
            self.logger.log_debug(f"Breakpoint set at line {line}{cond_str}")

        return True

    def remove_breakpoint(self, line: int) -> bool:
        """
        Remove a breakpoint from the specified line.

        Args:
            line: Line number (1-based)

        Returns:
            True if breakpoint was removed
        """
        if line in self.breakpoints:
            del self.breakpoints[line]
            if self.logger:
                self.logger.log_debug(f"Breakpoint removed from line {line}")
            return True
        return False

    def toggle_breakpoint(self, line: int) -> bool:
        """
        Toggle breakpoint enabled/disabled state.

        Args:
            line: Line number

        Returns:
            True if breakpoint exists and was toggled
        """
        if line in self.breakpoints:
            bp = self.breakpoints[line]
            bp.enabled = not bp.enabled
            state = "enabled" if bp.enabled else "disabled"
            if self.logger:
                self.logger.log_debug(f"Breakpoint at line {line} {state}")
            return True
        return False

    def clear_all_breakpoints(self):
        """Remove all breakpoints."""
        count = len(self.breakpoints)
        self.breakpoints.clear()
        if self.logger:
            self.logger.log_debug(f"Cleared {count} breakpoints")

    def should_pause(self, line: int, variables: Optional[Dict] = None) -> bool:
        """
        Check if execution should pause at this line.

        Args:
            line: Current line number
            variables: Current variable scope (for conditional breakpoints)

        Returns:
            True if execution should pause
        """
        if not self.enabled:
            return False

        # Step mode: pause at every line
        if self.step_mode:
            return True

        # Check for breakpoint at this line
        if line in self.breakpoints:
            bp = self.breakpoints[line]

            if not bp.enabled:
                return False

            # Unconditional breakpoint
            if not bp.condition:
                bp.hit_count += 1
                return True

            # Conditional breakpoint: evaluate condition
            if variables and self._evaluate_condition(bp.condition, variables):
                bp.hit_count += 1
                return True

        return False

    def _evaluate_condition(self, condition: str, variables: Dict) -> bool:
        """
        Safely evaluate a breakpoint condition.

        Args:
            condition: Condition expression (e.g., "counter > 5")
            variables: Current variable scope

        Returns:
            True if condition evaluates to True
        """
        try:
            # Create safe evaluation namespace with only variables
            namespace = {k: v for k, v in variables.items()}
            result = eval(condition, {"__builtins__": {}}, namespace)
            return bool(result)
        except Exception as e:
            if self.logger:
                self.logger.log_error(f"Breakpoint condition error: {condition} - {e}")
            return False

    def pause(self, line: int, variables: Optional[Dict] = None, code: str = ""):
        """
        Pause execution at the current line.

        Args:
            line: Current line number
            variables: Current variable scope
            code: Code at current line (for display)
        """
        self.paused = True
        self.current_line = line

        # Update call stack
        if not self.call_stack or self.call_stack[-1].line != line:
            frame = CallFrame(
                script_name=self.current_script or "<unknown>",
                line=line,
                variables=variables or {}
            )
            # Keep only last 50 frames to prevent memory bloat
            if len(self.call_stack) > 50:
                self.call_stack.pop(0)
            self.call_stack.append(frame)

        if self.logger:
            self.logger.log_debug(f"Paused at line {line}: {code[:50]}")

    def step(self) -> bool:
        """
        Execute one line and pause again.

        Returns:
            True if step was initiated
        """
        if not self.enabled:
            return False

        self.step_mode = True
        self.paused = False

        if self.logger:
            self.logger.log_debug("Step execution")

        return True

    def continue_execution(self) -> bool:
        """
        Resume execution until next breakpoint or completion.

        Returns:
            True if execution resumed
        """
        if not self.enabled:
            return False

        self.step_mode = False
        self.paused = False

        if self.logger:
            self.logger.log_debug("Continue execution")

        return True

    def inspect_variable(self, var_name: str, variables: Optional[Dict] = None) -> Any:
        """
        Get the value of a variable at the current execution point.

        Args:
            var_name: Variable name (supports nested access like "obj.field")
            variables: Current variable scope (uses call stack if not provided)

        Returns:
            Variable value or None if not found
        """
        # Use provided variables or get from current call frame
        scope = variables
        if scope is None and self.call_stack:
            scope = self.call_stack[-1].variables

        if scope is None:
            return None

        # Support nested variable access (e.g., "user.name")
        parts = var_name.split('.')
        value = scope

        try:
            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part)
                else:
                    value = getattr(value, part, None)

                if value is None:
                    return None

            return value
        except (KeyError, AttributeError):
            return None

    def get_call_stack(self) -> List[Dict]:
        """
        Get the current call stack.

        Returns:
            List of call frame dictionaries
        """
        return [frame.to_dict() for frame in self.call_stack]

    def add_watch(self, var_name: str):
        """
        Add a variable to the watch list.

        Args:
            var_name: Variable name to watch
        """
        if var_name not in self.watch_vars:
            self.watch_vars.append(var_name)
            if self.logger:
                self.logger.log_debug(f"Added watch: {var_name}")

    def remove_watch(self, var_name: str):
        """
        Remove a variable from the watch list.

        Args:
            var_name: Variable name to remove
        """
        if var_name in self.watch_vars:
            self.watch_vars.remove(var_name)
            if self.logger:
                self.logger.log_debug(f"Removed watch: {var_name}")

    def get_watched_values(self, variables: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Get current values of all watched variables.

        Args:
            variables: Current variable scope

        Returns:
            Dictionary of variable names to values
        """
        values = {}
        for var_name in self.watch_vars:
            values[var_name] = self.inspect_variable(var_name, variables)
        return values

    def trace_line(self, line: int, code: str, variables: Optional[Dict] = None):
        """
        Log execution trace for the current line.

        Args:
            line: Line number
            code: Code being executed
            variables: Current variable scope
        """
        if not self.trace_enabled or not self.logger:
            return

        # Add to execution history
        self.execution_history.append((line, code))
        if len(self.execution_history) > self.max_history:
            self.execution_history.pop(0)

        # Log trace
        watched = ""
        if self.watch_vars and variables:
            watched_values = self.get_watched_values(variables)
            watched = " | " + ", ".join(
                f"{k}={v}" for k, v in watched_values.items()
            )

        self.logger.log_debug(f"[TRACE] Line {line}: {code[:60]}{watched}")

    def enable_trace(self):
        """Enable trace logging for every line execution."""
        self.trace_enabled = True
        if self.logger:
            self.logger.log_debug("Trace logging enabled")

    def disable_trace(self):
        """Disable trace logging."""
        self.trace_enabled = False
        if self.logger:
            self.logger.log_debug("Trace logging disabled")

    def get_status(self) -> Dict[str, Any]:
        """
        Get current debug engine status.

        Returns:
            Dictionary with debug state information
        """
        return {
            'enabled': self.enabled,
            'paused': self.paused,
            'step_mode': self.step_mode,
            'current_line': self.current_line,
            'current_script': self.current_script,
            'breakpoints': len(self.breakpoints),
            'breakpoint_list': [bp.to_dict() for bp in self.breakpoints.values()],
            'call_stack_depth': len(self.call_stack),
            'watched_variables': self.watch_vars,
            'trace_enabled': self.trace_enabled
        }

    def save_state(self, path: Path):
        """
        Save debug state to JSON file.

        Args:
            path: Path to save file
        """
        state = {
            'enabled': self.enabled,
            'breakpoints': [bp.to_dict() for bp in self.breakpoints.values()],
            'watch_vars': self.watch_vars,
            'trace_enabled': self.trace_enabled,
            'saved_at': datetime.now(timezone.utc).isoformat()
        }

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(state, f, indent=2)

        if self.logger:
            self.logger.log_debug(f"Debug state saved to {path}")

    def load_state(self, path: Path) -> bool:
        """
        Load debug state from JSON file.

        Args:
            path: Path to load from

        Returns:
            True if loaded successfully
        """
        try:
            with open(path, 'r') as f:
                state = json.load(f)

            self.enabled = state.get('enabled', False)
            self.trace_enabled = state.get('trace_enabled', False)
            self.watch_vars = state.get('watch_vars', [])

            # Restore breakpoints
            self.breakpoints.clear()
            for bp_data in state.get('breakpoints', []):
                bp = Breakpoint(**bp_data)
                self.breakpoints[bp.line] = bp

            if self.logger:
                self.logger.log_debug(f"Debug state loaded from {path}")

            return True
        except Exception as e:
            if self.logger:
                self.logger.log_error(f"Failed to load debug state: {e}")
            return False
