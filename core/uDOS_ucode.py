"""
uDOS uCODE Interpreter
Executes .uscript files with advanced programming features
Version: 1.0.14

Features:
- Variables (SET/GET/${var})
- Control flow (IF/ELSE, FOR/WHILE)
- Functions (FUNCTION/RETURN)
- Error handling (TRY/CATCH)
- Modules (IMPORT/EXPORT)
"""

import os
import re
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


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

        # Persistence
        self.variables_file = Path("data/system/ucode_variables.json")
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
        Substitute ${variable} placeholders in text.

        Args:
            text: Text with ${var} placeholders

        Returns:
            Text with variables substituted
        """
        def replacer(match):
            var_name = match.group(1)
            value = self.get_variable(var_name)
            if value is None:
                return match.group(0)  # Keep placeholder if not found
            return str(value)

        return re.sub(r'\$\{(\w+)\}', replacer, text)

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
        # Substitute variables first
        line = self.substitute_variables(line)

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
        Handle SET command for variable assignment.

        Syntax: SET varname = value [PERSISTENT]

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

        # Parse assignment
        if '=' not in line:
            return "❌ SET syntax: SET varname = value [PERSISTENT]"

        parts = line.split('=', 1)
        var_name = parts[0].strip()
        var_value = parts[1].strip() if len(parts) > 1 else ""

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
        Handle GET command for variable retrieval.

        Syntax: GET varname

        Args:
            line: GET command line

        Returns:
            Variable value or error
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
