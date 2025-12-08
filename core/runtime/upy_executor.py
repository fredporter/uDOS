"""
uPY Script Executor with Debug Support (v1.2.2)

Provides enhanced execution for .upy scripts with integrated debugging:
- Line-by-line execution with breakpoint checking
- #BREAK directive support
- Variable inspection during pause
- Integration with DEV MODE debug engine
- Call stack tracking

Usage:
    from core.runtime.upy_executor import UPYExecutor

    executor = UPYExecutor()
    result = executor.execute_script("path/to/script.upy", variables={})

    # With debug mode:
    from core.services.debug_engine import DebugEngine
    debug = DebugEngine(logger)
    debug.enable()

    executor = UPYExecutor(debug_engine=debug)
    result = executor.execute_script("script.upy")  # Will pause at breakpoints
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from core.runtime.upy_parser import UPYParser, UPYParseError
from core.runtime.upy_preprocessor import UPYPreprocessor


class UPYExecutionContext:
    """Execution context for a uPY script."""

    def __init__(self, script_path: str, variables: Optional[Dict] = None):
        """
        Initialize execution context.

        Args:
            script_path: Path to script being executed
            variables: Initial variable scope
        """
        self.script_path = script_path
        self.variables = variables or {}
        self.current_line = 0
        self.paused = False
        self.breakpoints_hit = []
        self.execution_log = []

    def log_execution(self, line_num: int, code: str, result: Any = None):
        """Log execution of a line."""
        self.execution_log.append({
            'line': line_num,
            'code': code,
            'result': result
        })


class UPYExecutor:
    """
    Enhanced executor for uPY scripts with debug support.

    Integrates with DEV MODE for interactive debugging including
    breakpoints, step-through execution, and variable inspection.
    """

    def __init__(self, debug_engine=None, command_handler=None):
        """
        Initialize executor.

        Args:
            debug_engine: Optional DebugEngine instance for debugging
            command_handler: Optional CommandHandler for executing commands
        """
        self.debug_engine = debug_engine
        self.command_handler = command_handler
        self.parser = UPYParser()
        self.preprocessor = UPYPreprocessor()
        self.pause_callback: Optional[Callable] = None

    def set_pause_callback(self, callback: Callable[[int, str, Dict], None]):
        """
        Set callback function to be called when execution pauses.

        Args:
            callback: Function(line_num, code, variables) to call on pause
        """
        self.pause_callback = callback

    def execute_script(self, script_path: str, variables: Optional[Dict] = None) -> str:
        """
        Execute a .upy script file with debug support.

        Args:
            script_path: Path to .upy script
            variables: Initial variable scope

        Returns:
            Execution result/output

        Raises:
            FileNotFoundError: If script not found
            UPYParseError: If script has syntax errors
        """
        path = Path(script_path)
        if not path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")

        # Read script
        with open(path, 'r') as f:
            code = f.read()

        # Create execution context
        context = UPYExecutionContext(script_path, variables)

        # Update debug engine with script name
        if self.debug_engine:
            self.debug_engine.current_script = script_path

        # Execute
        return self.execute_code(code, context)

    def execute_code(self, code: str, context: Optional[UPYExecutionContext] = None) -> str:
        """
        Execute uPY code with debug support.

        Args:
            code: uPY code to execute
            context: Execution context (created if not provided)

        Returns:
            Execution result
        """
        if context is None:
            context = UPYExecutionContext("<inline>", {})

        # Split into lines
        lines = code.split('\n')
        results = []

        for line_num, line in enumerate(lines, start=1):
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Check for #BREAK directive
            if line.upper() == '#BREAK':
                if self.debug_engine and self.debug_engine.enabled:
                    self._handle_breakpoint(line_num, line, context)
                continue

            # Skip comments (but allow #BREAK to pass through)
            if line.startswith('#'):
                continue

            # Update context
            context.current_line = line_num

            # Check for breakpoint (if debug mode enabled)
            if self.debug_engine and self.debug_engine.enabled:
                if self.debug_engine.should_pause(line_num, context.variables):
                    self._handle_breakpoint(line_num, line, context)

                    # If still paused (waiting for CONTINUE), we need to pause execution
                    # In practice, this would integrate with the command loop
                    # For now, we just log and continue
                    if self.debug_engine.paused:
                        # Wait for user to CONTINUE or STEP
                        # This is where integration with main event loop would happen
                        pass

                # Trace logging
                if self.debug_engine.trace_enabled:
                    self.debug_engine.trace_line(line_num, line, context.variables)

            # Execute the line
            try:
                result = self._execute_line(line, context)
                if result:
                    # Convert result to string if needed
                    result_str = str(result) if not isinstance(result, str) else result
                    results.append(result_str)
                    context.log_execution(line_num, line, result)
            except UPYParseError as e:
                error_msg = f"Line {line_num}: {e}"
                context.log_execution(line_num, line, error_msg)
                raise UPYParseError(error_msg)
            except Exception as e:
                error_msg = f"Line {line_num}: Execution error: {e}"
                context.log_execution(line_num, line, error_msg)
                raise Exception(error_msg)

        return '\n'.join(results) if results else ""

    def _execute_line(self, line: str, context: UPYExecutionContext) -> Optional[str]:
        """
        Execute a single line of uPY code.

        Args:
            line: Code line to execute
            context: Execution context

        Returns:
            Execution result or None
        """
        # Preprocess variables
        processed_line = self.preprocessor.expand_variables(line, context.variables)

        # Parse command
        parsed = self.parser.parse_command(processed_line)

        if not parsed:
            return None

        # If we have a command handler, execute the command
        if self.command_handler:
            # parsed is in [MODULE|COMMAND*ARGS] format
            try:
                result = self.command_handler.handle_command(parsed, grid=None, parser=self.parser)
                return result
            except Exception as e:
                raise Exception(f"Command execution failed: {e}")

        # Otherwise just return the parsed command (for testing/dry-run)
        return parsed

    def _handle_breakpoint(self, line_num: int, code: str, context: UPYExecutionContext):
        """
        Handle breakpoint hit.

        Args:
            line_num: Line number where breakpoint hit
            code: Code at breakpoint
            context: Execution context
        """
        if not self.debug_engine:
            return

        # Pause execution
        self.debug_engine.pause(line_num, context.variables, code)
        context.paused = True
        context.breakpoints_hit.append(line_num)

        # Call pause callback if set
        if self.pause_callback:
            self.pause_callback(line_num, code, context.variables)

        # In a real implementation, this would wait for user input (STEP/CONTINUE)
        # For now, we just log the pause
        print(f"⏸️  Paused at line {line_num}: {code}")
        print(f"💡 Use 'DEV STEP' to execute next line or 'DEV CONTINUE' to resume")

    def get_execution_summary(self, context: UPYExecutionContext) -> Dict[str, Any]:
        """
        Get execution summary statistics.

        Args:
            context: Execution context

        Returns:
            Dictionary with execution statistics
        """
        return {
            'script': context.script_path,
            'total_lines': len(context.execution_log),
            'breakpoints_hit': len(context.breakpoints_hit),
            'final_variables': context.variables,
            'paused': context.paused,
            'current_line': context.current_line
        }


def execute_upy_script(script_path: str, debug_mode: bool = False, variables: Optional[Dict] = None) -> str:
    """
    Convenience function to execute a uPY script.

    Args:
        script_path: Path to .upy script file
        debug_mode: Enable debug mode
        variables: Initial variable scope

    Returns:
        Execution result

    Example:
        result = execute_upy_script("workflow.upy", debug_mode=True)
    """
    debug_engine = None
    if debug_mode:
        from core.services.debug_engine import DebugEngine
        from core.services.unified_logger import UnifiedLogger

        logger = UnifiedLogger()
        debug_engine = DebugEngine(logger)
        debug_engine.enable()

    executor = UPYExecutor(debug_engine=debug_engine)
    return executor.execute_script(script_path, variables)


def execute_upy_code(code: str, debug_mode: bool = False, variables: Optional[Dict] = None) -> str:
    """
    Convenience function to execute uPY code.

    Args:
        code: uPY code string
        debug_mode: Enable debug mode
        variables: Initial variable scope

    Returns:
        Execution result

    Example:
        code = '''
        SPRITE-SET('NAME'|'Hero')
        #BREAK
        SPRITE-SET('HP'|100)
        '''
        result = execute_upy_code(code, debug_mode=True)
    """
    debug_engine = None
    if debug_mode:
        from core.services.debug_engine import DebugEngine
        from core.services.unified_logger import UnifiedLogger

        logger = UnifiedLogger()
        debug_engine = DebugEngine(logger)
        debug_engine.enable()

    executor = UPYExecutor(debug_engine=debug_engine)
    context = UPYExecutionContext("<inline>", variables)
    return executor.execute_code(code, context)
