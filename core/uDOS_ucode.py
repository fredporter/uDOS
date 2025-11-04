"""
uDOS uCODE Interpreter
Executes .uscript files with basic command sequencing
Version: 1.0.6
"""

import os
from pathlib import Path


class UCodeInterpreter:
    """Simple interpreter for .uscript files."""

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
        self.variables = {}
        self.last_result = None

    def execute_script(self, script_path):
        """
        Execute a .uscript file.

        Args:
            script_path: Path to .uscript file

        Returns:
            Execution results as string
        """
        if not os.path.exists(script_path):
            return f"❌ Script not found: {script_path}"

        # Read script file
        with open(script_path, 'r') as f:
            lines = f.readlines()

        results = []
        results.append(f"📜 Executing script: {script_path}")
        results.append("=" * 60)

        line_num = 0
        for line in lines:
            line_num += 1
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue

            # Execute command
            try:
                result = self.execute_line(line, line_num)
                if result:
                    results.append(f"\n[Line {line_num}] {line}")
                    results.append(result)
            except Exception as e:
                error_msg = f"❌ Error on line {line_num}: {str(e)}\n   Command: {line}"
                results.append(error_msg)
                # Continue execution unless critical error
                if "critical" in str(e).lower():
                    break

        results.append("\n" + "=" * 60)
        results.append(f"✅ Script execution complete")

        return "\n".join(results)

    def execute_line(self, line, line_num=0):
        """
        Execute a single line of uCODE/command.

        Args:
            line: Command line to execute
            line_num: Line number (for error reporting)

        Returns:
            Command result
        """
        # Handle variable assignments (future feature)
        if '=' in line and not line.startswith('['):
            # VAR = VALUE syntax (not implemented yet)
            return None

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
