"""
uDOS uCODE Interpreter [DEPRECATED]
Executes .uscript files with advanced programming features
Version: 1.1.1 (Modern Syntax Update)

⚠️  DEPRECATED in v2.0.0
Use core/runtime/upy_parser.py for new .upy files with COMMAND(args) syntax.
This interpreter remains for backward compatibility with .uscript files.
Will be removed in v3.0.0.

Features:
- Variables (SET/GET/${var})
- Modern Syntax (v1.1.1+):
  * PRINT[] with ${var} template strings
  * Flexible bracket notation: PRINT[x], PRINT [x], [PRINT|x]
  * SET[]/GET[] bracket support
  * One-line IF{condition} THEN command
  * ECHO soft deprecation (still functional)
- Control flow (IF/ELSE, FOR/WHILE)
- Functions (FUNCTION/RETURN)
- Error handling (TRY/CATCH)
- Modules (IMPORT/EXPORT)
- Interactive Debugger (DEBUG, BREAK, STEP, INSPECT)

Syntax Notes:
- Reserved chars for normalization: ~^-+|<>*
- Template strings use ${var} instead of concatenation
- Curly braces {} for IF conditions, square brackets [] for commands
- Context-sensitive normalization (SET allows =, IF preserves operators)
"""

import os
import re
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from enum import Enum


class DebugState(Enum):
    """Debugger execution states."""
    NOT_STARTED = "not_started"
    RUNNING = "running"
    PAUSED = "paused"
    STEPPING = "stepping"
    STOPPED = "stopped"


class UCodeDebugger:
    """Interactive debugger for uCODE scripts."""

    def __init__(self, interpreter):
        """
        Initialize debugger.

        Args:
            interpreter: UCodeInterpreter instance
        """
        self.interpreter = interpreter
        self.state = DebugState.NOT_STARTED
        self.breakpoints = set()  # Set of line numbers
        self.conditional_breakpoints = {}  # {line: condition_expr}
        self.breakpoint_hit_counts = {}  # {line: count}
        self.current_line = 0
        self.current_file = None
        self.script_path = None  # Current script being debugged
        self.call_stack = []
        self.watch_expressions = {}
        self.step_mode = None  # None, 'STEP', 'STEP_INTO', 'STEP_OUT'
        self.step_target_depth = None  # For STEP OUT
        # v1.0.17 Phase 4: Performance tracking
        self.line_execution_times = {}  # {line: [times]}
        self.function_call_times = {}  # {function: [times]}
        # v1.0.17 Phase 4+: Enhanced features
        self.disabled_breakpoints = set()  # Disabled but not deleted breakpoints
        self.variable_history = {}  # {var_name: [(value, timestamp, line)]}
        self.auto_profile = False  # Auto-profile during execution

    def start(self, script_path: str):
        """Start debugging session for a script."""
        self.script_path = script_path
        self.current_file = script_path
        self.state = DebugState.RUNNING
        self.current_line = 0
        return f"✓ Debugging started: {script_path}"

    def stop(self):
        """Stop debugging session."""
        self.state = DebugState.STOPPED
        self.script_path = None
        self.current_file = None
        self.current_line = 0
        self.step_mode = None
        return "✓ Debugging stopped"

    def set_breakpoint(self, line: int, condition: str = None) -> str:
        """
        Set breakpoint at line number, optionally with condition.

        Args:
            line: Line number for breakpoint
            condition: Optional condition expression (e.g., "x > 10")
        """
        self.breakpoints.add(line)
        if condition:
            self.conditional_breakpoints[line] = condition
            return f"✓ Conditional breakpoint set at line {line}: {condition}"
        return f"✓ Breakpoint set at line {line}"

    def clear_breakpoint(self, line: int = None) -> str:
        """Clear breakpoint(s)."""
        if line is None:
            count = len(self.breakpoints)
            self.breakpoints.clear()
            self.conditional_breakpoints.clear()
            self.breakpoint_hit_counts.clear()
            return f"✓ Cleared {count} breakpoint(s)"
        elif line in self.breakpoints:
            self.breakpoints.remove(line)
            if line in self.conditional_breakpoints:
                del self.conditional_breakpoints[line]
            if line in self.breakpoint_hit_counts:
                del self.breakpoint_hit_counts[line]
            return f"✓ Breakpoint cleared at line {line}"
        else:
            return f"✗ No breakpoint at line {line}"

    def list_breakpoints(self) -> str:
        """List all breakpoints."""
        if not self.breakpoints:
            return "No breakpoints set"
        lines = sorted(self.breakpoints)
        return "Breakpoints:\n" + "\n".join(f"  Line {line}" for line in lines)

    def should_pause(self, line: int) -> bool:
        """
        Check if execution should pause at this line.

        v1.0.17 Phase 4: Supports conditional breakpoints and hit counting.
        """
        # Pause if breakpoint hit
        if line in self.breakpoints:
            # Check if breakpoint is disabled
            if line in self.disabled_breakpoints:
                return False  # Skip disabled breakpoints

            # Track hit count
            self.breakpoint_hit_counts[line] = self.breakpoint_hit_counts.get(line, 0) + 1

            # Check conditional breakpoint
            if line in self.conditional_breakpoints:
                condition = self.conditional_breakpoints[line]
                try:
                    # Evaluate condition in current scope
                    if self._evaluate_condition(condition):
                        self.state = DebugState.PAUSED
                        return True
                    else:
                        # Condition not met, continue execution
                        return False
                except Exception as e:
                    # If condition evaluation fails, pause anyway and show error
                    self.state = DebugState.PAUSED
                    print(f"⚠️  Breakpoint condition error: {e}")
                    return True
            else:
                # Unconditional breakpoint
                self.state = DebugState.PAUSED
                return True

        # Pause if in step mode
        if self.step_mode == 'STEP':
            self.state = DebugState.PAUSED
            self.step_mode = None
            return True
        elif self.step_mode == 'STEP_INTO':
            self.state = DebugState.PAUSED
            self.step_mode = None
            return True
        elif self.step_mode == 'STEP_OUT':
            if len(self.call_stack) <= self.step_target_depth:
                self.state = DebugState.PAUSED
                self.step_mode = None
                self.step_target_depth = None
                return True

        return False

    def step(self):
        """Execute one line."""
        self.step_mode = 'STEP'
        self.state = DebugState.STEPPING

    def step_into(self):
        """Step into function calls."""
        self.step_mode = 'STEP_INTO'
        self.state = DebugState.STEPPING

    def step_out(self):
        """Step out of current function."""
        self.step_mode = 'STEP_OUT'
        self.step_target_depth = len(self.call_stack) - 1
        self.state = DebugState.STEPPING

    def continue_execution(self):
        """Continue until next breakpoint."""
        self.step_mode = None
        self.state = DebugState.RUNNING

    def get_context(self) -> Dict[str, Any]:
        """Get current execution context."""
        return {
            'line': self.current_line,
            'file': self.current_file,
            'state': self.state.value,
            'call_stack': self.call_stack.copy(),
            'variables': self.interpreter.current_scope.list_variables(),
            'breakpoints': sorted(self.breakpoints)
        }

    def inspect_variable(self, name: str) -> Any:
        """Inspect variable value."""
        # Try current_scope first
        if hasattr(self.interpreter, 'current_scope') and self.interpreter.current_scope:
            if self.interpreter.current_scope.has(name):
                return self.interpreter.current_scope.get(name)

        # Fall back to variables dict
        if hasattr(self.interpreter, 'variables') and name in self.interpreter.variables:
            return self.interpreter.variables[name]

        # Variable not found
        return None

    def add_watch(self, expr: str, name: str = None):
        """Add watch expression."""
        watch_name = name or expr
        self.watch_expressions[watch_name] = expr
        return f"✓ Watching: {watch_name}"

    def remove_watch(self, name: str):
        """Remove watch expression."""
        if name in self.watch_expressions:
            del self.watch_expressions[name]
            return f"✓ Removed watch: {name}"
        return f"✗ No watch named: {name}"

    def evaluate_watches(self) -> Dict[str, Any]:
        """Evaluate all watch expressions."""
        results = {}
        for name, expr in self.watch_expressions.items():
            try:
                # Try to get as variable first
                if self.interpreter.current_scope.has(expr):
                    results[name] = self.interpreter.current_scope.get(expr)
                else:
                    results[name] = f"<undefined: {expr}>"
            except Exception as e:
                results[name] = f"<error: {str(e)}>"
        return results

    # ═══════════════════════════════════════════════════════════════════════════
    # v1.0.17: Additional debugger methods for command integration
    # ═══════════════════════════════════════════════════════════════════════════

    def get_status(self) -> Dict[str, Any]:
        """Get current debugger status."""
        return {
            'state': self.state.name,
            'current_script': getattr(self, 'script_path', None),
            'current_line': self.current_line,
            'breakpoints': list(self.breakpoints),
            'watches': list(self.watch_expressions.keys())
        }

    def get_variables(self) -> Dict[str, Any]:
        """Get all variables in current scope."""
        if self.interpreter:
            # Try current_scope first, fall back to variables dict
            if hasattr(self.interpreter, 'current_scope') and self.interpreter.current_scope:
                return self.interpreter.current_scope.variables.copy()
            elif hasattr(self.interpreter, 'variables'):
                return self.interpreter.variables.copy()
        return {}

    def get_watches(self) -> Dict[str, Any]:
        """Get all watched variables with their current values."""
        return self.evaluate_watches()

    def get_call_stack(self) -> list:
        """Get current call stack."""
        return self.call_stack.copy()

    def clear_all_breakpoints(self):
        """Clear all breakpoints."""
        count = len(self.breakpoints)
        self.breakpoints.clear()
        return f"✓ Cleared {count} breakpoints"

    def clear_all_watches(self):
        """Clear all watch expressions."""
        count = len(self.watch_expressions)
        self.watch_expressions.clear()
        return f"✓ Cleared {count} watches"

    def step_over(self):
        """Step over current line (don't enter function calls)."""
        self.state = DebugState.STEPPING
        self.step_mode = 'over'

    # ═══════════════════════════════════════════════════════════════════════════
    # v1.0.17 Phase 4: Advanced Debugging Features
    # ═══════════════════════════════════════════════════════════════════════════

    def _evaluate_condition(self, condition: str) -> bool:
        """
        Evaluate a breakpoint condition in the current scope.

        Args:
            condition: Condition expression (e.g., "x > 10", "name == 'test'")

        Returns:
            True if condition is met, False otherwise
        """
        try:
            # Get variables from current scope
            variables = self.get_variables()

            # Evaluate condition using Python's eval with limited scope
            # This is safe because we only expose debugger variables
            result = eval(condition, {"__builtins__": {}}, variables)
            return bool(result)
        except Exception:
            # If evaluation fails, return False (don't pause)
            return False

    def set_variable(self, name: str, value: Any) -> str:
        """
        Set/modify a variable during debugging.

        Args:
            name: Variable name
            value: New value

        Returns:
            Confirmation message
        """
        try:
            # Try to set in current scope first
            if hasattr(self.interpreter, 'current_scope') and self.interpreter.current_scope:
                self.interpreter.current_scope.set(name, value)
                return f"✓ Variable '{name}' set to: {value}"

            # Fall back to global scope
            if hasattr(self.interpreter, 'global_scope'):
                self.interpreter.global_scope.set(name, value)
                return f"✓ Variable '{name}' set to: {value}"

            return f"✗ Cannot set variable: no scope available"
        except Exception as e:
            return f"✗ Error setting variable: {e}"

    def get_breakpoint_info(self, line: int) -> Dict[str, Any]:
        """
        Get detailed information about a breakpoint.

        Args:
            line: Line number

        Returns:
            Dict with breakpoint details
        """
        if line not in self.breakpoints:
            return None

        return {
            'line': line,
            'condition': self.conditional_breakpoints.get(line),
            'hit_count': self.breakpoint_hit_counts.get(line, 0),
            'enabled': True
        }

    def get_all_breakpoint_info(self) -> list:
        """Get detailed info for all breakpoints."""
        return [self.get_breakpoint_info(line) for line in sorted(self.breakpoints)]

    def record_line_time(self, line: int, execution_time: float):
        """
        Record execution time for a line (for profiling).

        Args:
            line: Line number
            execution_time: Time in seconds
        """
        if line not in self.line_execution_times:
            self.line_execution_times[line] = []
        self.line_execution_times[line].append(execution_time)

    def get_performance_profile(self) -> Dict[str, Any]:
        """
        Get performance profiling data.

        Returns:
            Dict with profiling statistics
        """
        profile = {
            'lines': {},
            'slowest_lines': [],
            'total_time': 0.0
        }

        # Calculate stats for each line
        for line, times in self.line_execution_times.items():
            avg_time = sum(times) / len(times) if times else 0
            total_time = sum(times)
            profile['lines'][line] = {
                'executions': len(times),
                'avg_time': avg_time,
                'total_time': total_time,
                'min_time': min(times) if times else 0,
                'max_time': max(times) if times else 0
            }
            profile['total_time'] += total_time

        # Find slowest lines
        sorted_lines = sorted(
            profile['lines'].items(),
            key=lambda x: x[1]['total_time'],
            reverse=True
        )
        profile['slowest_lines'] = [(line, data) for line, data in sorted_lines[:10]]

        return profile

    # ═══════════════════════════════════════════════════════════════════════════
    # v1.0.17 Phase 4+: Additional Enhanced Features
    # ═══════════════════════════════════════════════════════════════════════════

    def disable_breakpoint(self, line: int) -> str:
        """Disable a breakpoint without deleting it."""
        self.disabled_breakpoints.add(line)
        if line in self.breakpoints:
            return f"✓ Breakpoint at line {line} disabled"
        return f"✓ Line {line} marked as disabled"

    def enable_breakpoint(self, line: int) -> str:
        """Enable a previously disabled breakpoint."""
        if line in self.disabled_breakpoints:
            self.disabled_breakpoints.remove(line)
            return f"✓ Breakpoint at line {line} enabled"
        return f"✓ Line {line} not in disabled list"

    def is_breakpoint_enabled(self, line: int) -> bool:
        """Check if a breakpoint is enabled."""
        return line in self.breakpoints and line not in self.disabled_breakpoints

    def track_variable_change(self, var_name: str, old_value: Any, new_value: Any, line: int):
        """
        Track variable value changes for history.

        Args:
            var_name: Variable name
            old_value: Previous value (None if first assignment)
            new_value: New value
            line: Line number where change occurred
        """
        from datetime import datetime

        if var_name not in self.variable_history:
            self.variable_history[var_name] = []

        self.variable_history[var_name].append({
            'old_value': old_value,
            'new_value': new_value,
            'timestamp': datetime.now().isoformat(),
            'line': line
        })

        # Keep only last 100 changes per variable
        if len(self.variable_history[var_name]) > 100:
            self.variable_history[var_name] = self.variable_history[var_name][-100:]

    def get_variable_history(self, var_name: str) -> list:
        """Get history of variable changes."""
        return self.variable_history.get(var_name, [])

    def clear_variable_history(self, var_name: str = None):
        """
        Clear variable history.

        Args:
            var_name: Variable name to clear, or None to clear all
        """
        if var_name:
            if var_name in self.variable_history:
                del self.variable_history[var_name]
        else:
            self.variable_history.clear()


class VariableScope:
    """Manage variable scopes for functions and blocks."""

    def __init__(self, parent=None):
        """
        Initialize variable scope.

        Args:
            parent: Parent scope for nested scopes
        """
        self.parent = parent
        self.variables = {}

    def set(self, name: str, value: Any):
        """Set variable in current scope."""
        self.variables[name] = value

    def get(self, name: str) -> Any:
        """Get variable from current or parent scope."""
        if name in self.variables:
            return self.variables[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            raise NameError(f"Variable '{name}' not defined")

    def has(self, name: str) -> bool:
        """Check if variable exists in scope chain."""
        if name in self.variables:
            return True
        elif self.parent:
            return self.parent.has(name)
        return False

    def delete(self, name: str):
        """Delete variable from scope."""
        if name in self.variables:
            del self.variables[name]
        else:
            raise NameError(f"Variable '{name}' not defined")

    def list_variables(self) -> Dict[str, Any]:
        """Get all variables in scope chain."""
        if self.parent:
            vars_dict = self.parent.list_variables()
            vars_dict.update(self.variables)
            return vars_dict
        return self.variables.copy()


class UCodeInterpreter:
    """Enhanced interpreter for .uscript files with full programming features."""

    def __init__(self, command_handler=None, parser=None, grid=None):
        """
        Initialize interpreter.

        Args:
            command_handler: Main CommandHandler instance (from uDOS_commands.py)
            parser: Parser instance for converting user input to uCODE
            grid: Grid instance for command execution
        """
        self.command_handler = command_handler  # Main CommandHandler, not FileCommandHandler
        self.parser = parser
        self.grid = grid

        # Variable management
        self.global_scope = VariableScope()
        self.current_scope = self.global_scope

        # Execution state
        self.last_result = None
        self.functions = {}
        self.imported_modules = {}

        # Debugger
        self.debugger = UCodeDebugger(self)
        self.debug_mode = False

        # Deprecation tracking (v1.1.1)
        self._deprecation_warnings_shown = set()  # Track warnings shown this session

        # Persistence
        self.variables_file = Path("core/data/ucode_variables.json")
        self._load_persistent_variables()

    def _load_persistent_variables(self):
        """Load persistent variables from file."""
        if self.variables_file.exists():
            try:
                with open(self.variables_file, 'r') as f:
                    data = json.load(f)
                    for name, value in data.items():
                        self.global_scope.set(name, value)
            except Exception as e:
                print(f"⚠️  Could not load persistent variables: {e}")

    def _save_persistent_variables(self):
        """Save global variables to file."""
        try:
            self.variables_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.variables_file, 'w') as f:
                json.dump(self.global_scope.variables, f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not save persistent variables: {e}")

    def set_variable(self, name: str, value: Any, persistent: bool = False):
        """
        Set a variable value.

        Args:
            name: Variable name
            value: Variable value (will be type-converted)
            persistent: Save to disk for next session
        """
        # Type conversion
        converted_value = self._convert_value(value)

        # Set in current scope
        self.current_scope.set(name, converted_value)

        # Save if persistent
        if persistent:
            self.global_scope.set(name, converted_value)
            self._save_persistent_variables()

    def get_variable(self, name: str, default: Any = None) -> Any:
        """
        Get a variable value.

        Args:
            name: Variable name
            default: Default value if not found

        Returns:
            Variable value or default
        """
        try:
            return self.current_scope.get(name)
        except NameError:
            return default

    def delete_variable(self, name: str):
        """Delete a variable."""
        self.current_scope.delete(name)

    def list_variables(self) -> Dict[str, Any]:
        """Get all variables in current scope."""
        return self.current_scope.list_variables()

    def _convert_value(self, value: str) -> Any:
        """
        Convert string value to appropriate type.

        Args:
            value: String value

        Returns:
            Converted value (int, float, bool, list, or string)
        """
        if not isinstance(value, str):
            return value

        value = value.strip()

        # Boolean
        if value.lower() in ('true', 'yes', 'on'):
            return True
        if value.lower() in ('false', 'no', 'off'):
            return False

        # Number
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            pass

        # Explicit list (surrounded by brackets)
        if value.startswith('[') and value.endswith(']'):
            inner = value[1:-1]
            if inner:
                return [item.strip() for item in inner.split(',')]
            return []

        # Comma-separated values (only if multiple items and not quoted)
        if ',' in value and not ((value.startswith('"') and value.endswith('"')) or \
                                  (value.startswith("'") and value.endswith("'"))):
            items = [item.strip() for item in value.split(',')]
            # Only return as list if we have multiple non-empty items
            non_empty = [item for item in items if item]
            if len(non_empty) > 1:
                return non_empty

        # String (remove quotes if present)
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            return value[1:-1]

        return value

    def substitute_variables(self, text: str) -> str:
        """
        Substitute variable placeholders in text.

        Supports two syntaxes:
        - ${variable} - Traditional shell-style (backward compatible)
        - @variable - Modern clean syntax (v1.1.2+)

        Args:
            text: Text with ${var} or @var placeholders

        Returns:
            Text with variables substituted
        """
        def replacer(match):
            var_name = match.group(1)
            value = self.get_variable(var_name)
            if value is None:
                return match.group(0)  # Keep placeholder if not found
            return str(value)

        # First substitute ${variable} syntax
        text = re.sub(r'\$\{(\w+)\}', replacer, text)

        # Then substitute @variable syntax (v1.1.2+)
        # Match @word but not @@ or @ at end
        text = re.sub(r'@(\w+)', replacer, text)

        return text

    def evaluate_condition(self, condition: str) -> bool:
        """
        Evaluate a conditional expression.

        Supports:
        - Comparison: ==, !=, <, >, <=, >=
        - Logical: AND, OR, NOT
        - Parentheses for grouping

        Args:
            condition: Conditional expression

        Returns:
            Boolean result
        """
        # Substitute variables first
        condition = self.substitute_variables(condition)

        # Handle NOT operator
        if condition.strip().upper().startswith('NOT '):
            inner = condition.strip()[4:]
            return not self.evaluate_condition(inner)

        # Handle OR operator (lowest precedence)
        if ' OR ' in condition.upper():
            parts = re.split(r'\s+OR\s+', condition, flags=re.IGNORECASE)
            return any(self.evaluate_condition(part) for part in parts)

        # Handle AND operator
        if ' AND ' in condition.upper():
            parts = re.split(r'\s+AND\s+', condition, flags=re.IGNORECASE)
            return all(self.evaluate_condition(part) for part in parts)

        # Handle parentheses
        if '(' in condition:
            # Simple parentheses handling (not full recursive)
            condition = re.sub(r'\(([^)]+)\)',
                             lambda m: str(self.evaluate_condition(m.group(1))),
                             condition)

        # Handle comparison operators
        for op, func in [
            ('==', lambda a, b: a == b),
            ('!=', lambda a, b: a != b),
            ('<=', lambda a, b: self._compare_values(a, b) <= 0),
            ('>=', lambda a, b: self._compare_values(a, b) >= 0),
            ('<', lambda a, b: self._compare_values(a, b) < 0),
            ('>', lambda a, b: self._compare_values(a, b) > 0),
        ]:
            if op in condition:
                parts = condition.split(op, 1)
                if len(parts) == 2:
                    left = self._parse_value(parts[0].strip())
                    right = self._parse_value(parts[1].strip())
                    return func(left, right)

        # Single value (truthy check)
        value = self._parse_value(condition.strip())
        return bool(value)

    def _parse_value(self, value_str: str) -> Any:
        """Parse a value string to its actual type."""
        # Try to get as variable
        if value_str.isidentifier():
            var_value = self.get_variable(value_str)
            if var_value is not None:
                return var_value

        # Convert literal value
        return self._convert_value(value_str)

    def _compare_values(self, a: Any, b: Any) -> int:
        """
        Compare two values.

        Returns:
            -1 if a < b, 0 if a == b, 1 if a > b
        """
        # Convert to comparable types
        if isinstance(a, str) and isinstance(b, str):
            return -1 if a < b else (1 if a > b else 0)

        # Try numeric comparison
        try:
            a_num = float(a) if not isinstance(a, (int, float)) else a
            b_num = float(b) if not isinstance(b, (int, float)) else b
            return -1 if a_num < b_num else (1 if a_num > b_num else 0)
        except (ValueError, TypeError):
            # Fallback to string comparison
            return -1 if str(a) < str(b) else (1 if str(a) > str(b) else 0)

    def execute_script(self, script_path):
        """
        Execute a .uscript file with control flow support.

        Args:
            script_path: Path to .uscript file

        Returns:
            Execution results as string
        """
        if not os.path.exists(script_path):
            return f"❌ Script not found: {script_path}"

        # Read script file
        with open(script_path, 'r') as f:
            lines = [line.rstrip() for line in f.readlines()]

        results = []
        results.append(f"📜 Executing script: {script_path}")
        results.append("=" * 60)

        # Execute with control flow
        try:
            self._execute_lines(lines, results, start_index=0)
        except Exception as e:
            results.append(f"\n❌ Script execution error: {str(e)}")

            # v1.0.17: Show stack trace in debug mode
            if self.debug_mode:
                import traceback
                results.append("\n🐛 Debug Stack Trace:")
                results.append(traceback.format_exc())

                # Show debugger context
                results.append("\n" + self._show_debug_context())

        results.append("\n" + "=" * 60)
        results.append(f"✅ Script execution complete")

        return "\n".join(results)

    def _show_debug_context(self) -> str:
        """
        Show debugging context (variables, watches, stack).

        Returns:
            Formatted debug context string
        """
        output = []

        # Show watched variables
        watches = self.debugger.get_watches()
        if watches:
            output.append("👁️  Watches:")
            for name, value in watches.items():
                output.append(f"   {name} = {value}")

        # Show local variables (first 5)
        variables = self.debugger.get_variables()
        if variables:
            output.append("📍 Variables:")
            for i, (name, value) in enumerate(list(variables.items())[:5]):
                output.append(f"   {name} = {value}")
            if len(variables) > 5:
                output.append(f"   ... and {len(variables) - 5} more")

        # Show call stack
        stack = self.debugger.get_call_stack()
        if stack:
            output.append(f"📚 Call stack depth: {len(stack)}")

        return "\n".join(output) if output else "ℹ️  No debug context"

    def _execute_lines(self, lines: List[str], results: List[str],
                      start_index: int = 0, end_index: Optional[int] = None) -> int:
        """
        Execute a block of lines with control flow support.

        Args:
            lines: List of script lines
            results: Results accumulator
            start_index: Starting line index
            end_index: Ending line index (None = end of file)

        Returns:
            Index of last executed line
        """
        if end_index is None:
            end_index = len(lines)

        i = start_index
        while i < end_index:
            line = lines[i].strip()
            line_num = i + 1

            # v1.0.17: Update debugger current line
            if self.debug_mode:
                self.debugger.current_line = line_num

                # Check if we should pause at this line
                if self.debugger.should_pause(line_num):
                    results.append(f"\n🐛 Paused at line {line_num}: {line}")
                    results.append(self._show_debug_context())
                    # In interactive mode, this would wait for user input
                    # For now, we just log the pause

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                i += 1
                continue

            # Handle FUNCTION definitions
            if line.upper().startswith('FUNCTION '):
                i = self._handle_function_definition(lines, results, i, end_index)
                continue

            # Handle TRY/CATCH/FINALLY blocks
            if line.upper() == 'TRY':
                i = self._handle_try_block(lines, results, i, end_index)
                continue

            # Handle IF statements
            if line.upper().startswith('IF ') or line.upper().startswith('IF{'):
                # Check if it's a one-line IF with THEN (v1.1.1)
                if ' THEN ' in line.upper():
                    # One-line IF, execute via execute_line
                    result = self.execute_line(line, line_num)
                    if result is not None:
                        results.append(result)
                    i += 1
                    continue
                else:
                    # Multi-line IF block
                    i = self._handle_if_block(lines, results, i, end_index)
                    continue

            # Handle FOR loops
            if line.upper().startswith('FOR '):
                i = self._handle_for_loop(lines, results, i, end_index)
                continue

            # Handle WHILE loops
            if line.upper().startswith('WHILE '):
                i = self._handle_while_loop(lines, results, i, end_index)
                continue

            # Handle BREAK (should only be in loop context)
            if line.upper() == 'BREAK':
                raise StopIteration("BREAK")

            # Handle CONTINUE (should only be in loop context)
            if line.upper() == 'CONTINUE':
                raise StopIteration("CONTINUE")

            # Execute regular command
            try:
                # v1.0.17 Phase 4+: Auto-profiling
                if self.debug_mode and self.debugger.auto_profile:
                    import time
                    start_time = time.time()
                    result = self.execute_line(line, line_num)
                    execution_time = time.time() - start_time
                    self.debugger.record_line_time(line_num, execution_time)
                else:
                    result = self.execute_line(line, line_num)

                if result:
                    results.append(f"\n[Line {line_num}] {line}")
                    results.append(result)
            except StopIteration:
                # Let RETURN, BREAK, CONTINUE propagate up
                raise
            except Exception as e:
                # Let all exceptions propagate (TRY/CATCH will handle them)
                # Only report and continue for non-critical errors at top level
                raise

            i += 1

        return i

    def _handle_if_block(self, lines: List[str], results: List[str],
                        start_index: int, end_index: int) -> int:
        """
        Handle IF/ELSE/ENDIF block (both old and new syntax).

        Old syntax: IF condition ... ELSE ... ENDIF
        New syntax: IF (condition) { ... } ELSE { ... }

        Args:
            lines: List of script lines
            results: Results accumulator
            start_index: Index of IF line
            end_index: End boundary

        Returns:
            Index after ENDIF or closing }
        """
        if_line = lines[start_index].strip()
        line_num = start_index + 1

        # Check if using curly brace syntax
        uses_braces = if_line.endswith('{')

        # Parse condition from "IF condition THEN", "IF condition", or "IF (condition) {"
        condition_text = if_line[3:].strip()  # Remove "IF "
        if condition_text.upper().endswith(' THEN'):
            condition_text = condition_text[:-5].strip()
        elif uses_braces:
            # Remove trailing {
            condition_text = condition_text[:-1].strip()
            # Remove parentheses if present
            if condition_text.startswith('(') and condition_text.endswith(')'):
                condition_text = condition_text[1:-1].strip()

        # Evaluate condition
        try:
            condition_result = self.evaluate_condition(condition_text)
        except Exception as e:
            results.append(f"❌ Error evaluating condition on line {line_num}: {str(e)}")
            condition_result = False

        # Find ELSE and block end (ENDIF or })
        else_index = None
        block_end_index = None
        nesting_level = 0
        brace_depth = 0
        found_else_with_closing_brace = False

        for i in range(start_index + 1, end_index):
            line = lines[i].strip()
            line_upper = line.upper()

            # Track brace depth for new syntax
            if uses_braces:
                # Check for } ELSE { pattern on same line
                if line_upper == '} ELSE {' and brace_depth == 0 and else_index is None:
                    else_index = i
                    found_else_with_closing_brace = True
                    # Continue searching for final }
                    continue
                elif line == '{':
                    brace_depth += 1
                elif line == '}':
                    if brace_depth == 0:
                        # This is the closing brace for IF or ELSE
                        if found_else_with_closing_brace:
                            # This closes the ELSE block
                            block_end_index = i
                            break
                        elif else_index is None:
                            # No ELSE found yet, keep searching
                            block_end_index = i
                            # But keep looking for possible ELSE after this
                            # Actually, if we found }, we're done unless there's ELSE
                            # Let's check the next line
                            if i + 1 < end_index:
                                next_line = lines[i + 1].strip().upper()
                                if next_line == 'ELSE {' or next_line.startswith('ELSE '):
                                    # Don't break, there's an ELSE coming
                                    else_index = i + 1
                                    if next_line == 'ELSE {':
                                        found_else_with_closing_brace = False
                                    continue
                            # No ELSE, we're done
                            break
                        else:
                            # We already found ELSE, this closes it
                            block_end_index = i
                            break
                    else:
                        brace_depth -= 1

            # Check for nested IF blocks
            if line_upper.startswith('IF '):
                if uses_braces and line.endswith('{'):
                    brace_depth += 1
                else:
                    nesting_level += 1

            # Check for ELSE (works in both syntaxes)
            elif line_upper == 'ELSE' and nesting_level == 0 and brace_depth == 0 and else_index is None:
                else_index = i
            elif line_upper == 'ELSE {' and uses_braces and brace_depth == 0 and else_index is None:
                else_index = i

            # Check for ENDIF (old syntax)
            elif not uses_braces and line_upper == 'ENDIF':
                if nesting_level == 0:
                    block_end_index = i
                    break
                else:
                    nesting_level -= 1

        if block_end_index is None:
            end_marker = '}' if uses_braces else 'ENDIF'
            results.append(f"❌ Error on line {line_num}: IF without matching {end_marker}")
            return start_index + 1

        # Execute appropriate block
        if condition_result:
            # Execute IF block
            block_end = else_index if else_index else block_end_index
            self._execute_lines(lines, results, start_index + 1, block_end)
        elif else_index is not None:
            # Execute ELSE block
            else_line = lines[else_index].strip()
            else_line_upper = else_line.upper()

            if else_line_upper == '} ELSE {':
                # Inline } ELSE { - ELSE block is on next line
                else_start = else_index + 1
            elif else_line_upper == 'ELSE {' or else_line_upper == 'ELSE':
                # ELSE block starts after ELSE line
                else_start = else_index + 1
            else:
                else_start = else_index + 1

            self._execute_lines(lines, results, else_start, block_end_index)

        # Return index after block end
        return block_end_index + 1

    def _handle_for_loop(self, lines: List[str], results: List[str],
                        start_index: int, end_index: int) -> int:
        """
        Handle FOR loop.

        Syntax:
        - FOR var IN list ... ENDFOR
        - FOR var FROM start TO end ... ENDFOR

        Args:
            lines: List of script lines
            results: Results accumulator
            start_index: Index of FOR line
            end_index: End boundary

        Returns:
            Index after ENDFOR
        """
        for_line = lines[start_index].strip()
        line_num = start_index + 1

        # Find ENDFOR
        endfor_index = None
        nesting_level = 0

        for i in range(start_index + 1, end_index):
            line = lines[i].strip().upper()
            if line.startswith('FOR '):
                nesting_level += 1
            elif line.startswith('WHILE '):
                nesting_level += 1
            elif line == 'ENDFOR' or line == 'ENDWHILE':
                if nesting_level == 0:
                    endfor_index = i
                    break
                else:
                    nesting_level -= 1

        if endfor_index is None:
            results.append(f"❌ Error on line {line_num}: FOR without matching ENDFOR")
            return start_index + 1

        # Parse FOR statement
        for_text = for_line[4:].strip()  # Remove "FOR "

        # Check for "FOR var IN list" syntax
        if ' IN ' in for_text.upper():
            parts = re.split(r'\s+IN\s+', for_text, maxsplit=1, flags=re.IGNORECASE)
            var_name = parts[0].strip()
            list_expr = parts[1].strip()

            # Evaluate list expression
            list_expr = self.substitute_variables(list_expr)

            # Get the iterable
            if list_expr.startswith('[') and list_expr.endswith(']'):
                # Explicit list
                items = self._convert_value(list_expr)
            elif ',' in list_expr:
                # Comma-separated
                items = [item.strip() for item in list_expr.split(',')]
            else:
                # Try to get as variable
                items = self.get_variable(list_expr)
                if items is None:
                    items = [list_expr]

            # Ensure it's iterable
            if not isinstance(items, (list, tuple)):
                items = [items]

            # Execute loop for each item
            for item in items:
                self.set_variable(var_name, item)
                try:
                    self._execute_lines(lines, results, start_index + 1, endfor_index)
                except StopIteration as e:
                    if str(e) == "BREAK":
                        break
                    elif str(e) == "CONTINUE":
                        continue

        # Check for "FOR var FROM start TO end" syntax
        elif ' FROM ' in for_text.upper() and ' TO ' in for_text.upper():
            match = re.match(r'(\w+)\s+FROM\s+(.+?)\s+TO\s+(.+)', for_text, re.IGNORECASE)
            if match:
                var_name = match.group(1)
                start_expr = match.group(2).strip()
                end_expr = match.group(3).strip()

                # Substitute variables and convert
                start_val = self.substitute_variables(start_expr)
                end_val = self.substitute_variables(end_expr)

                # Try to get as variable if it's an identifier
                if start_val.isidentifier():
                    start_val = self.get_variable(start_val, start_val)
                if end_val.isidentifier():
                    end_val = self.get_variable(end_val, end_val)

                try:
                    start_num = int(self._convert_value(str(start_val)))
                    end_num = int(self._convert_value(str(end_val)))

                    # Execute loop for range
                    for i in range(start_num, end_num + 1):
                        self.set_variable(var_name, i)
                        try:
                            self._execute_lines(lines, results, start_index + 1, endfor_index)
                        except StopIteration as e:
                            if str(e) == "BREAK":
                                break
                            elif str(e) == "CONTINUE":
                                continue
                except ValueError:
                    results.append(f"❌ Error on line {line_num}: Invalid range in FOR loop")
        else:
            results.append(f"❌ Error on line {line_num}: Invalid FOR syntax")

        return endfor_index + 1

    def _handle_while_loop(self, lines: List[str], results: List[str],
                          start_index: int, end_index: int) -> int:
        """
        Handle WHILE loop.

        Syntax: WHILE condition ... ENDWHILE

        Args:
            lines: List of script lines
            results: Results accumulator
            start_index: Index of WHILE line
            end_index: End boundary

        Returns:
            Index after ENDWHILE
        """
        while_line = lines[start_index].strip()
        line_num = start_index + 1

        # Parse condition
        condition_text = while_line[6:].strip()  # Remove "WHILE "

        # Find ENDWHILE
        endwhile_index = None
        nesting_level = 0

        for i in range(start_index + 1, end_index):
            line = lines[i].strip().upper()
            if line.startswith('WHILE ') or line.startswith('FOR '):
                nesting_level += 1
            elif line == 'ENDWHILE' or line == 'ENDFOR':
                if nesting_level == 0:
                    endwhile_index = i
                    break
                else:
                    nesting_level -= 1

        if endwhile_index is None:
            results.append(f"❌ Error on line {line_num}: WHILE without matching ENDWHILE")
            return start_index + 1

        # Execute loop while condition is true
        max_iterations = 10000  # Safety limit
        iteration = 0

        while iteration < max_iterations:
            try:
                condition_result = self.evaluate_condition(condition_text)
            except Exception as e:
                results.append(f"❌ Error evaluating WHILE condition on line {line_num}: {str(e)}")
                break

            if not condition_result:
                break

            try:
                self._execute_lines(lines, results, start_index + 1, endwhile_index)
            except StopIteration as e:
                if str(e) == "BREAK":
                    break
                elif str(e) == "CONTINUE":
                    pass  # Continue to next iteration

            iteration += 1

        if iteration >= max_iterations:
            results.append(f"⚠️  Warning: WHILE loop exceeded maximum iterations ({max_iterations})")

        return endwhile_index + 1

    def _handle_function_definition(self, lines: List[str], results: List[str],
                                   start_index: int, end_index: int) -> int:
        """
        Handle FUNCTION definition.

        Syntax: FUNCTION name(param1, param2, ...)
                  ...function body...
                RETURN value
                ENDFUNCTION

        Args:
            lines: List of script lines
            results: Results accumulator
            start_index: Index of FUNCTION line
            end_index: End boundary

        Returns:
            Index after ENDFUNCTION
        """
        func_line = lines[start_index].strip()
        line_num = start_index + 1

        # Parse function signature: FUNCTION name(params)
        if '(' not in func_line or ')' not in func_line:
            results.append(f"❌ Error on line {line_num}: Invalid FUNCTION syntax. Use: FUNCTION name(param1, param2)")
            return start_index + 1

        # Extract function name and parameters
        func_header = func_line[9:].strip()  # Remove "FUNCTION "
        paren_pos = func_header.index('(')
        func_name = func_header[:paren_pos].strip()

        params_str = func_header[paren_pos+1:func_header.rindex(')')].strip()
        params = [p.strip() for p in params_str.split(',') if p.strip()] if params_str else []

        # Validate function name
        if not func_name.isidentifier():
            results.append(f"❌ Error on line {line_num}: Invalid function name '{func_name}'")
            return start_index + 1

        # Find ENDFUNCTION
        endfunction_index = None
        nesting_level = 0

        for i in range(start_index + 1, end_index):
            line = lines[i].strip().upper()
            if line.startswith('FUNCTION '):
                nesting_level += 1
            elif line == 'ENDFUNCTION':
                if nesting_level == 0:
                    endfunction_index = i
                    break
                else:
                    nesting_level -= 1

        if endfunction_index is None:
            results.append(f"❌ Error on line {line_num}: FUNCTION without matching ENDFUNCTION")
            return start_index + 1

        # Store function definition
        self.functions[func_name] = {
            'params': params,
            'body_start': start_index + 1,
            'body_end': endfunction_index,
            'lines': lines
        }

        results.append(f"✅ Function '{func_name}' defined with {len(params)} parameter(s)")

        return endfunction_index + 1

    def _handle_call(self, line: str) -> str:
        """
        Handle CALL command for function execution.

        Syntax: CALL function_name(arg1, arg2, ...)

        Args:
            line: CALL command line

        Returns:
            Function return value or success message
        """
        # Remove 'CALL ' prefix
        call_expr = line[5:].strip()

        # Parse function name and arguments
        if '(' not in call_expr or ')' not in call_expr:
            return "❌ CALL syntax: CALL function_name(arg1, arg2, ...)"

        paren_pos = call_expr.index('(')
        func_name = call_expr[:paren_pos].strip()
        args_str = call_expr[paren_pos+1:call_expr.rindex(')')].strip()

        # Parse arguments (handle quoted strings, variables, etc.)
        args = []
        if args_str:
            # Simple argument parsing (could be enhanced for complex expressions)
            for arg in args_str.split(','):
                arg = arg.strip()
                # Evaluate the argument (could be variable, number, string)
                if arg.startswith('"') and arg.endswith('"'):
                    args.append(arg[1:-1])  # String literal
                elif arg.startswith("'") and arg.endswith("'"):
                    args.append(arg[1:-1])  # String literal
                elif arg.isdigit() or (arg.startswith('-') and arg[1:].isdigit()):
                    args.append(int(arg))  # Integer
                elif arg.replace('.', '', 1).isdigit():
                    args.append(float(arg))  # Float
                else:
                    # Try to get as variable
                    try:
                        args.append(self.get_variable(arg))
                    except:
                        args.append(arg)  # Use as-is

        # Check if function exists
        if func_name not in self.functions:
            return f"❌ Function '{func_name}' not defined"

        func_def = self.functions[func_name]
        params = func_def['params']

        # Check argument count
        if len(args) != len(params):
            return f"❌ Function '{func_name}' expects {len(params)} argument(s), got {len(args)}"

        # Create new scope for function execution
        func_scope = VariableScope(parent=self.global_scope)

        # Bind parameters to arguments
        for param, arg in zip(params, args):
            func_scope.set(param, arg)

        # Save current scope and switch to function scope
        prev_scope = self.current_scope
        self.current_scope = func_scope

        # Execute function body
        results = []
        return_value = None

        try:
            body_lines = func_def['lines'][func_def['body_start']:func_def['body_end']]
            self._execute_lines(body_lines, results, 0, len(body_lines))
        except StopIteration as e:
            # Handle RETURN statement
            error_msg = str(e)
            if error_msg.startswith("RETURN:"):
                return_value = error_msg[7:]  # Extract return value
        except Exception as e:
            return_value = f"❌ Error in function '{func_name}': {str(e)}"
        finally:
            # Restore previous scope
            self.current_scope = prev_scope

        # Store return value in special variable (accessible in global scope)
        if return_value:
            self.global_scope.set('RETURN_VALUE', return_value)
            # Perform variable substitution on return value
            return_value = self.substitute_variables(str(return_value))
            return f"✅ Function '{func_name}' returned: {return_value}"
        else:
            self.global_scope.set('RETURN_VALUE', None)
            return f"✅ Function '{func_name}' executed"

    def _handle_try_block(self, lines: List[str], results: List[str],
                         start_index: int, end_index: int) -> int:
        """
        Handle TRY/CATCH/FINALLY block.

        Syntax: TRY
                  ...try body...
                CATCH error_var
                  ...catch body...
                FINALLY
                  ...finally body...
                ENDTRY

        Args:
            lines: List of script lines
            results: Results accumulator
            start_index: Index of TRY line
            end_index: End boundary

        Returns:
            Index after ENDTRY
        """
        line_num = start_index + 1

        # Find CATCH, FINALLY, and ENDTRY
        catch_index = None
        finally_index = None
        endtry_index = None
        nesting_level = 0
        error_var = None

        for i in range(start_index + 1, end_index):
            line = lines[i].strip().upper()

            if line == 'TRY':
                nesting_level += 1
            elif line.startswith('CATCH') and nesting_level == 0 and catch_index is None:
                catch_index = i
                # Extract error variable name if provided
                catch_line = lines[i].strip()
                if len(catch_line) > 5:  # "CATCH" is 5 characters
                    error_var = catch_line[5:].strip()
            elif line == 'FINALLY' and nesting_level == 0 and finally_index is None:
                finally_index = i
            elif line == 'ENDTRY':
                if nesting_level == 0:
                    endtry_index = i
                    break
                else:
                    nesting_level -= 1

        if endtry_index is None:
            results.append(f"❌ Error on line {line_num}: TRY without matching ENDTRY")
            return start_index + 1

        # Execute TRY block
        error_occurred = None
        try:
            try_end = catch_index if catch_index else (finally_index if finally_index else endtry_index)
            self._execute_lines(lines, results, start_index + 1, try_end)
        except StopIteration:
            # Let RETURN, BREAK, CONTINUE propagate
            raise
        except Exception as e:
            error_occurred = e
            # Store error message in variable if specified
            if error_var:
                self.current_scope.set(error_var, str(e))
            # Also store in special ERROR variable
            self.global_scope.set('ERROR', str(e))
            self.global_scope.set('ERROR_TYPE', type(e).__name__)

            # Execute CATCH block if present
            if catch_index is not None:
                try:
                    catch_end = finally_index if finally_index else endtry_index
                    self._execute_lines(lines, results, catch_index + 1, catch_end)
                except StopIteration:
                    raise
                except Exception as catch_error:
                    results.append(f"⚠️  Error in CATCH block: {str(catch_error)}")
            else:
                # No CATCH block, report the error
                results.append(f"❌ Uncaught error: {str(e)}")

        # Execute FINALLY block if present (always runs)
        if finally_index is not None:
            try:
                self._execute_lines(lines, results, finally_index + 1, endtry_index)
            except StopIteration:
                raise
            except Exception as finally_error:
                results.append(f"⚠️  Error in FINALLY block: {str(finally_error)}")

        return endtry_index + 1

    def _normalize_bracket_syntax(self, line: str) -> str:
        """
        Normalize flexible bracket syntax to standard uCODE format (v1.1.1).

        Modern Syntax Support:
        - PRINT[text] -> PRINT "text"
        - PRINT [text] -> PRINT "text"
        - [PRINT|text] -> PRINT "text"
        - SET[var=value] -> SET var "value"
        - GET[var] -> GET var
        - Variables: PRINT[System: ${name}] -> PRINT "System: ${name}"

        Reserved uCODE characters (NOT allowed in simple bracket content):
        ~^-+|<>*

        Context-Sensitive Normalization:
        - SET command: = allowed (for assignment syntax)
        - IF command: NOT normalized (preserves operators like >, <, ==)
        - Other commands: Normalize if no reserved chars present

        Note: $ { } are allowed for variable substitution (${var})

        Args:
            line: Original command line

        Returns:
            Normalized command line
        """
        line = line.strip()

        # Reserved characters that indicate this is NOT simple bracket notation
        # Note: $ { } are allowed for variable substitution ${var}
        # Note: = is allowed for SET command (var = value)
        RESERVED_CHARS = set('~^-+|<>*')  # Removed = for SET support

        # Format 1: [COMMAND|params] - standard uCODE format
        if line.startswith('[') and '|' in line and line.endswith(']'):
            # Extract command and params
            inner = line[1:-1]  # Remove outer brackets
            if '|' in inner:
                parts = inner.split('|', 1)
                command = parts[0].strip()
                params = parts[1].strip() if len(parts) > 1 else ""

                # Check if params contain reserved characters (except | and = for SET)
                param_chars = set(params) - set('|')
                if command.upper() == 'SET':
                    param_chars = param_chars - set('=')  # Allow = for SET

                if param_chars & RESERVED_CHARS:
                    # Contains reserved chars, leave as-is for parser
                    return line

                # Simple text, convert to plain syntax
                # SET and GET don't use quotes, others do
                if command.upper() in ['SET', 'GET']:
                    return f'{command} {params}' if params else command
                else:
                    return f'{command} "{params}"' if params else command

        # Format 2: COMMAND[params] or COMMAND [params]
        if '[' in line and line.endswith(']'):
            # Find command part
            bracket_pos = line.index('[')
            command = line[:bracket_pos].strip()
            params = line[bracket_pos+1:-1].strip()  # Content between [ ]

            # Only process known simple commands
            if command.upper() in ['PRINT', 'ECHO', 'SET', 'GET', 'CALL']:
                # Check if params contain reserved characters
                param_chars = set(params)
                if command.upper() == 'SET':
                    param_chars = param_chars - set('=')  # Allow = for SET

                if param_chars & RESERVED_CHARS:
                    # Contains reserved chars, leave as-is
                    return line

                # Simple text, convert to plain syntax
                # SET and GET don't use quotes, others do
                if command.upper() in ['SET', 'GET']:
                    return f'{command} {params}' if params else command
                else:
                    return f'{command} "{params}"' if params else command

        return line

    def execute_line(self, line, line_num=0):
        """
        Execute a single line of uCODE/command.

        Args:
            line: Command line to execute
            line_num: Line number (for error reporting)

        Returns:
            Command result
        """
        # v1.0.17: Update debugger line tracking
        if self.debug_mode and line_num > 0:
            self.debugger.current_line = line_num

        # Normalize bracket syntax (v1.1.1)
        line = self._normalize_bracket_syntax(line)

        # Substitute variables first
        line = self.substitute_variables(line)

        # Handle one-line IF with THEN (v1.1.1)
        # Matches: IF condition THEN, IF{condition} THEN
        if (line.upper().startswith('IF ') or line.upper().startswith('IF{')) and ' THEN ' in line.upper():
            return self._handle_oneline_if(line)

        # Handle IMPORT command (module imports)
        if line.upper().startswith('IMPORT '):
            return self._handle_import(line)

        # Handle EXPORT command (module exports)
        if line.upper().startswith('EXPORT '):
            return self._handle_export(line)

        # Handle CALL command (function calls)
        if line.upper().startswith('CALL '):
            return self._handle_call(line)

        # Handle RETURN command (function returns)
        if line.upper().startswith('RETURN'):
            raise StopIteration(f"RETURN:{line[6:].strip() if len(line) > 6 else ''}")

        # Handle THROW command (raise errors)
        if line.upper().startswith('THROW '):
            error_msg = line[6:].strip()
            raise RuntimeError(error_msg)

        # Handle SET command (variable assignment)
        if line.upper().startswith('SET '):
            return self._handle_set(line)

        # Handle GET command (variable retrieval)
        if line.upper().startswith('GET '):
            return self._handle_get(line)

        # Handle DELETE command (variable deletion)
        if line.upper().startswith('DELETE ') or line.upper().startswith('UNSET '):
            return self._handle_delete(line)

        # Handle VARS command (list all variables)
        if line.upper() == 'VARS' or line.upper() == 'VARIABLES':
            return self._handle_vars()

        # Handle PRINT command (modern output)
        if line.upper().startswith('PRINT '):
            return self._handle_print(line)

        # Handle ECHO command (deprecated, use PRINT)
        if line.upper().startswith('ECHO '):
            return self._handle_echo_deprecated(line)

        # Handle uCODE format [MODULE|COMMAND*PARAMS]
        if line.startswith('[') and line.endswith(']'):
            return self._execute_ucode(line)

        # Handle plain text commands (convert via parser)
        if self.parser:
            ucode = self.parser.parse(line)
            return self._execute_ucode(ucode)
        else:
            # Try to execute as-is (basic support without parser)
            return f"⚠️  Parser not available, skipping: {line}"

    def _handle_set(self, line: str) -> str:
        """
        Handle SET command for variable assignment (v1.1.1 Modern Syntax).

        Syntax:
            SET varname = value [PERSISTENT]
            SET varname value [PERSISTENT]  # shorthand (no =)
            SET[varname = value]  # v1.1.1 bracket notation
            SET[varname=value]    # v1.1.1 compact notation

        Examples:
            SET name = "Alice"
            SET name "Alice"      # shorthand
            SET[count=42]
            SET status active PERSISTENT

        Args:
            line: SET command line

        Returns:
            Success message
        """
        # Remove 'SET ' prefix
        line = line[4:].strip()

        # Check for PERSISTENT flag
        persistent = line.upper().endswith(' PERSISTENT')
        if persistent:
            line = line[:-11].strip()

        # Parse assignment (support both = and space-separated syntax)
        if '=' in line:
            # SET varname = value format
            parts = line.split('=', 1)
            var_name = parts[0].strip()
            var_value = parts[1].strip() if len(parts) > 1 else ""
        else:
            # SET varname value format (shorthand)
            parts = line.split(maxsplit=1)
            if len(parts) < 2:
                return "❌ SET syntax: SET varname value [PERSISTENT] or SET varname = value [PERSISTENT]"
            var_name = parts[0].strip()
            var_value = parts[1].strip()

        # Validate variable name
        if not var_name.isidentifier():
            return f"❌ Invalid variable name: {var_name}"

        # Set variable
        self.set_variable(var_name, var_value, persistent)

        # Format output
        converted = self.get_variable(var_name)
        type_name = type(converted).__name__
        persist_flag = " [PERSISTENT]" if persistent else ""

        return f"✅ Variable '{var_name}' = {converted} ({type_name}){persist_flag}"

    def _handle_get(self, line: str) -> str:
        """
        Handle GET command for variable retrieval (v1.1.1 Modern Syntax).

        Syntax:
            GET varname
            GET[varname]  # v1.1.1 bracket notation

        Examples:
            GET name
            GET[count]
            GET status

        Args:
            line: GET command line

        Returns:
            Variable value or error message
        """
        # Remove 'GET ' prefix
        var_name = line[4:].strip()

        # Validate variable name
        if not var_name:
            return "❌ GET syntax: GET varname"

        # Get variable
        value = self.get_variable(var_name)

        if value is None:
            return f"❌ Variable '{var_name}' not defined"

        type_name = type(value).__name__
        return f"{var_name} = {value} ({type_name})"

    def _handle_delete(self, line: str) -> str:
        """
        Handle DELETE/UNSET command for variable deletion.

        Syntax: DELETE varname

        Args:
            line: DELETE command line

        Returns:
            Success message or error
        """
        # Remove 'DELETE ' or 'UNSET ' prefix
        parts = line.split(maxsplit=1)
        if len(parts) < 2:
            return "❌ DELETE syntax: DELETE varname"

        var_name = parts[1].strip()

        # Delete variable
        try:
            self.delete_variable(var_name)
            return f"✅ Variable '{var_name}' deleted"
        except NameError as e:
            return f"❌ {str(e)}"

    def _handle_vars(self) -> str:
        """
        Handle VARS command to list all variables.

        Returns:
            Formatted list of variables
        """
        variables = self.list_variables()

        if not variables:
            return "No variables defined"

        lines = ["Variables:"]
        lines.append("─" * 60)

        for name, value in sorted(variables.items()):
            type_name = type(value).__name__
            # Truncate long values
            value_str = str(value)
            if len(value_str) > 50:
                value_str = value_str[:47] + "..."
            lines.append(f"  {name:<20} = {value_str} ({type_name})")

        lines.append("─" * 60)
        lines.append(f"Total: {len(variables)} variable(s)")

        return "\n".join(lines)

    def _handle_print(self, line: str) -> str:
        """
        Handle PRINT command with template string support (v1.1.1 Modern Syntax).

        Syntax:
            PRINT "text"
            PRINT "Value: ${var}"
            PRINT variable_name
            PRINT[text]               # v1.1.1 bracket notation
            PRINT[System: ${name}]    # v1.1.1 with templates

        Template Strings:
            ${var} - Variable substitution within quoted strings
            Example: PRINT "Hello ${name}, you have ${count} items"

        Args:
            line: PRINT command line

        Returns:
            Output string (printed value)
        """
        content = line[6:].strip()  # Remove "PRINT "

        if not content:
            return ""  # Empty PRINT just outputs blank line

        # Check if it's a quoted string
        if (content.startswith('"') and content.endswith('"')) or \
           (content.startswith("'") and content.endswith("'")):
            # Remove quotes
            text = content[1:-1]

            # Process escape sequences (v1.1.1 fix)
            text = text.replace('\\n', '\n')
            text = text.replace('\\t', '\t')
            text = text.replace('\\"', '"')
            text = text.replace("\\'", "'")
            text = text.replace('\\\\', '\\')

            # Substitute ${var} template strings
            # Pattern: ${variable_name}
            template_pattern = r'\$\{([a-zA-Z_][a-zA-Z0-9_]*)\}'

            def replace_var(match):
                var_name = match.group(1)
                # Check if variable exists
                if self.current_scope.has(var_name):
                    value = self.get_variable(var_name)
                    return str(value)
                else:
                    return f"${{{var_name}}}"  # Keep original if not found

            text = re.sub(template_pattern, replace_var, text)
            return text
        else:
            # Treat as variable name or expression
            # Check if variable exists
            if self.current_scope.has(content):
                value = self.get_variable(content)
                return str(value)
            else:
                # Not a variable, return as-is
                return content

    def _handle_echo_deprecated(self, line: str) -> str:
        """
        Handle ECHO command (deprecated in v1.1.1).

        Shows deprecation warning once per session, then executes as PRINT.

        Args:
            line: ECHO command line

        Returns:
            Output string with deprecation warning (first time only)
        """
        # Show warning once per session
        warning_key = 'ECHO'
        if warning_key not in self._deprecation_warnings_shown:
            self._deprecation_warnings_shown.add(warning_key)
            warning = "⚠️  DEPRECATED: ECHO command is deprecated in uDOS v1.1.1. Use PRINT instead.\n" + \
                     "   This warning will only be shown once per session.\n"
        else:
            warning = ""

        # Convert ECHO to PRINT and execute
        print_line = "PRINT " + line[5:]  # Replace "ECHO " with "PRINT "
        result = self._handle_print(print_line)

        # Return warning + result
        if warning:
            return warning + result
        return result

    def _handle_oneline_if(self, line: str) -> str:
        """
        Handle one-line IF with THEN (v1.1.1 Modern Syntax).

        Syntax Examples:
            IF condition THEN command
            IF{condition} THEN command
            IF{x > 5} THEN PRINT[Value is large]
            IF{status == "ready"} THEN SET[active=true]

        Features:
        - Curly braces {} for conditions (v1.1.1 modern syntax)
        - Supports complex operators: >, <, ==, !=, >=, <=, AND, OR, NOT
        - THEN keyword required for one-line IF
        - Can execute any command after THEN (including PRINT[], SET[], etc.)

        Args:
            line: One-line IF command

        Returns:
            Command result or None if condition false
        """
        # Find THEN keyword (case-insensitive)
        upper_line = line.upper()
        then_pos = upper_line.find(' THEN ')

        if then_pos == -1:
            return "❌ One-line IF syntax: IF condition THEN command"

        # Extract condition part (everything between IF and THEN)
        # Handle both: "IF condition" and "IF{condition}"
        if line.upper().startswith('IF{'):
            # IF{condition} format - extract from position 2 (after "IF")
            condition_part = line[2:then_pos].strip()
        else:
            # IF condition format - extract from position 3 (after "IF ")
            condition_part = line[3:then_pos].strip()

        # Remove curly braces if present: {condition} → condition
        if condition_part.startswith('{') and condition_part.endswith('}'):
            condition_part = condition_part[1:-1].strip()

        # Extract command part (after THEN)
        command_part = line[then_pos + 6:].strip()  # Skip " THEN "

        # Evaluate condition using debugger's condition evaluator
        try:
            condition_result = self.debugger._evaluate_condition(condition_part)
        except Exception as e:
            return f"❌ IF condition error: {e}"        # Execute command if condition is true
        if condition_result:
            try:
                return self.execute_line(command_part)
            except Exception as e:
                return f"❌ Command error: {e}"

        # Condition false, return None (no output)
        return None

    def _handle_import(self, line: str) -> str:
        """Handle IMPORT command for module loading."""
        import_path = line[7:].strip()
        if not import_path:
            return "❌ IMPORT syntax: IMPORT module_name or IMPORT path/to/module.uscript"

        # Check if importing specific item
        specific_item = None
        if '.' in import_path and not import_path.startswith('.') and not import_path.endswith('.uscript'):
            parts = import_path.rsplit('.', 1)
            import_path = parts[0]
            specific_item = parts[1]

        # Resolve module path
        module_path = self._resolve_module_path(import_path)
        if not module_path or not os.path.exists(module_path):
            return f"❌ Module not found: {import_path}"

        # Check for circular imports
        if module_path in self.imported_modules:
            return f"⚠️  Module already imported: {import_path}"

        # Execute module
        try:
            with open(module_path, 'r') as f:
                module_lines = [line.rstrip() for line in f.readlines()]

            module_exports = {'functions': {}, 'variables': {}}
            results = []
            module_interpreter = UCodeInterpreter(
                command_handler=self.command_handler,
                parser=self.parser,
                grid=self.grid
            )
            module_interpreter._execute_lines(module_lines, results, 0, len(module_lines))

            if hasattr(module_interpreter, '_exports'):
                module_exports = module_interpreter._exports
            else:
                module_exports['functions'] = module_interpreter.functions.copy()

            # Import items
            if specific_item:
                if specific_item in module_exports['functions']:
                    self.functions[specific_item] = module_exports['functions'][specific_item]
                    return f"✅ Imported function '{specific_item}' from {import_path}"
                elif specific_item in module_exports['variables']:
                    self.global_scope.set(specific_item, module_exports['variables'][specific_item])
                    return f"✅ Imported variable '{specific_item}' from {import_path}"
                else:
                    return f"❌ Item '{specific_item}' not found in module {import_path}"
            else:
                func_count = 0
                for name, func_def in module_exports['functions'].items():
                    self.functions[name] = func_def
                    func_count += 1
                var_count = 0
                for name, value in module_exports['variables'].items():
                    self.global_scope.set(name, value)
                    var_count += 1
                self.imported_modules[module_path] = module_exports
                return f"✅ Imported module {import_path} ({func_count} function(s), {var_count} variable(s))"
        except Exception as e:
            return f"❌ Error importing module {import_path}: {str(e)}"

    def _handle_export(self, line: str) -> str:
        """Handle EXPORT command for marking items as exportable."""
        item_name = line[7:].strip()
        if not item_name:
            return "❌ EXPORT syntax: EXPORT function_name or EXPORT variable_name"

        if not hasattr(self, '_exports'):
            self._exports = {'functions': {}, 'variables': {}}

        if item_name in self.functions:
            self._exports['functions'][item_name] = self.functions[item_name]
            return f"✅ Exported function '{item_name}'"

        if self.global_scope.has(item_name):
            self._exports['variables'][item_name] = self.global_scope.get(item_name)
            return f"✅ Exported variable '{item_name}'"

        return f"⚠️  '{item_name}' not found (export will apply when defined)"

    def _resolve_module_path(self, import_path: str) -> Optional[str]:
        """Resolve module import path to actual file path."""
        if import_path.endswith('.uscript'):
            if os.path.isabs(import_path):
                return import_path
            else:
                return os.path.abspath(import_path)

        stdlib_paths = [
            f"memory/modules/{import_path}.uscript",
            f"memory/modules/stdlib/{import_path}.uscript",
            f"examples/modules/{import_path}.uscript"
        ]

        for path in stdlib_paths:
            if os.path.exists(path):
                return os.path.abspath(path)

        if import_path.startswith('./') or import_path.startswith('../'):
            path = os.path.abspath(import_path + '.uscript')
            if os.path.exists(path):
                return path

        return None


    def _execute_ucode(self, ucode):
        """
        Execute uCODE format command.

        Args:
            ucode: uCODE string [MODULE|COMMAND*PARAMS]

        Returns:
            Command result
        """
        if not self.command_handler:
            return "⚠️  Command handler not available"

        try:
            # Create a temporary grid if not provided
            # (grid is needed for some commands but not all)
            grid = self.grid
            if not grid:
                try:
                    from core.uDOS_grid import Grid
                    grid = Grid()
                except:
                    grid = None  # Some commands don't need grid

            result = self.command_handler.handle_command(ucode, grid, self.parser)
            self.last_result = result
            return result
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            return f"❌ Execution error: {str(e)}\n{error_detail}"
def execute_script_standalone(script_path):
    """
    Execute a script without full uDOS context (for testing).

    Args:
        script_path: Path to .uscript file

    Returns:
        Execution results
    """
    interpreter = UCodeInterpreter()
    return interpreter.execute_script(script_path)


# Example usage
if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        script_file = sys.argv[1]
        result = execute_script_standalone(script_file)
        print(result)
    else:
        print("Usage: python uDOS_ucode.py <script.uscript>")
