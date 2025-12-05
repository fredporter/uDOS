"""
uPY v2.0.2 Runtime Engine
Interpreter for v2.0.2 syntax

Syntax Support:
- Variables: {$VARIABLE} or {$VARIABLE.PROPERTY}
- Commands: (COMMAND|param1|param2)
- Short conditionals: [IF condition: action]
- Medium conditionals: [IF cond THEN: action ELSE: action]
- Ternary: [condition ? action : else_action]
- Long conditionals: IF/ELSE IF/ELSE/END IF
- Short functions: @name(params): expression
- Long functions: FUNCTION/END FUNCTION
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path


class UPYRuntimeError(Exception):
    """Raised when uPY execution fails"""
    def __init__(self, message: str, line: int = 0):
        self.line = line
        super().__init__(f"{message} (line {line})" if line else message)


class UPYRuntime:
    """
    Runtime interpreter for uPY v2.0.2 syntax.

    Executes scripts without converting to Python.
    """

    def __init__(self, command_handler=None, grid=None, parser=None):
        """
        Initialize runtime.

        Args:
            command_handler: Optional CommandHandler for executing commands
            grid: Optional Grid instance
            parser: Optional Parser instance
        """
        self.command_handler = command_handler
        self.grid = grid
        self.parser = parser
        self.variables: Dict[str, Any] = {}
        self.functions: Dict[str, Dict] = {}
        self.labels: Dict[str, int] = {}
        self.output: List[str] = []        # System variables (read-only)
        self.system_vars = {
            'MISSION.ID': 'test-mission',
            'MISSION.NAME': 'Test Mission',
            'MISSION.STATUS': 'ACTIVE',
            'MISSION.PROGRESS': '0',
            'WORKFLOW.PHASE': 'INIT',
            'WORKFLOW.NAME': 'test-workflow',
            'THEME': 'foundation',
            'SPRITE-LOCATION': 'AA340',
            'SPRITE-HP': 100,
            'SPRITE-HP-MAX': 100,
            'SPRITE-LEVEL': 1,
            'SPRITE-XP': 0,
        }

        # Patterns for v2.0.2
        self.var_pattern = re.compile(r'\{\$([a-zA-Z_][a-zA-Z0-9_.-]*)\}')
        self.cmd_pattern = re.compile(r'\(([A-Z_]+)(?:\|([^\)]+))?\)')
        self.short_cond_pattern = re.compile(r'\[IF\s+(.+?):\s*(.+?)\]')
        self.medium_cond_pattern = re.compile(r'\[IF\s+(.+?)\s+THEN:\s*(.+?)(?:\s+ELSE:\s*(.+?))?\]')
        self.ternary_pattern = re.compile(r'\[(.+?)\s*\?\s*(.+?)\s*:\s*(.+?)\]')

    def split_actions(self, action_str: str) -> List[str]:
        """
        Split actions on | but respect parentheses and brackets.

        Args:
            action_str: String with potentially multiple actions like "(CMD|param)|(CMD2|param)"

        Returns:
            List of individual actions
        """
        actions = []
        current = []
        paren_depth = 0
        bracket_depth = 0

        for char in action_str:
            if char == '(':
                paren_depth += 1
                current.append(char)
            elif char == ')':
                paren_depth -= 1
                current.append(char)
            elif char == '[':
                bracket_depth += 1
                current.append(char)
            elif char == ']':
                bracket_depth -= 1
                current.append(char)
            elif char == '|' and paren_depth == 0 and bracket_depth == 0:
                # Split here
                if current:
                    actions.append(''.join(current).strip())
                    current = []
            else:
                current.append(char)

        # Add last action
        if current:
            actions.append(''.join(current).strip())

        return actions

    def set_variable(self, name: str, value: Any):
        """Set a variable value."""
        self.variables[name] = value

    def get_variable(self, name: str) -> Any:
        """Get a variable value."""
        # Check system variables first
        if name in self.system_vars:
            return self.system_vars[name]
        # Then user variables
        return self.variables.get(name, None)

    def substitute_variables(self, text: str) -> str:
        """Replace {$variable} with values."""
        def replacer(match):
            var_name = match.group(1)
            value = self.get_variable(var_name)
            return str(value) if value is not None else match.group(0)

        return self.var_pattern.sub(replacer, text)

    def evaluate_value(self, value: str) -> Any:
        """
        Evaluate value - try function calls, math expressions, then numbers, then string.

        Args:
            value: String value to evaluate

        Returns:
            Evaluated value (int, float, or string)
        """
        value = value.strip()
        
        # Check for function calls: @function(args)
        func_call_pattern = re.compile(r'^@([a-zA-Z_][a-zA-Z0-9_-]*)\(([^\)]*)\)$')
        match = func_call_pattern.match(value)
        if match:
            func_name = match.group(1)
            args_str = match.group(2)
            
            # Parse arguments (pipe-separated or comma-separated)
            args = []
            if args_str.strip():
                # Try pipe-separated first
                if '|' in args_str:
                    # Split on | but respect nested parentheses
                    current_arg = []
                    paren_depth = 0
                    for char in args_str:
                        if char == '(':
                            paren_depth += 1
                            current_arg.append(char)
                        elif char == ')':
                            paren_depth -= 1
                            current_arg.append(char)
                        elif char == '|' and paren_depth == 0:
                            args.append(''.join(current_arg).strip())
                            current_arg = []
                        else:
                            current_arg.append(char)
                    
                    # Add last argument
                    if current_arg:
                        args.append(''.join(current_arg).strip())
                else:
                    # Try comma-separated
                    current_arg = []
                    paren_depth = 0
                    for char in args_str:
                        if char == '(':
                            paren_depth += 1
                            current_arg.append(char)
                        elif char == ')':
                            paren_depth -= 1
                            current_arg.append(char)
                        elif char == ',' and paren_depth == 0:
                            args.append(''.join(current_arg).strip())
                            current_arg = []
                        else:
                            current_arg.append(char)
                    
                    # Add last argument
                    if current_arg:
                        args.append(''.join(current_arg).strip())
            
            # Call function
            result = self.call_function(func_name, args)
            return result
        
        # Check if it contains math operators
        has_math = any(op in value for op in ['+', '-', '*', '/', '%', '**', '(', ')'])

        if has_math:
            # Try to evaluate as math expression
            try:
                from core.runtime.upy_math import evaluate
                # Build variables dict for math parser
                result = evaluate(value, self.variables)
                return result
            except Exception as e:
                # Fall through to simple conversion
                pass

        # Try to convert to number
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            # Return as string
            return value

    def parse_command(self, text: str) -> Optional[Tuple[str, List[str]]]:
        """
        Parse command: (COMMAND|param1|param2)
        Handles nested parentheses in parameters.

        Returns:
            (command_name, params) tuple or None
        """
        text = text.strip()
        if not text.startswith('(') or not text.endswith(')'):
            return None
        
        # Remove outer parentheses
        inner = text[1:-1]
        
        # Split on | but respect nested parentheses
        parts = []
        current = []
        paren_depth = 0
        
        for char in inner:
            if char == '(':
                paren_depth += 1
                current.append(char)
            elif char == ')':
                paren_depth -= 1
                current.append(char)
            elif char == '|' and paren_depth == 0:
                parts.append(''.join(current))
                current = []
            else:
                current.append(char)
        
        # Add last part
        if current:
            parts.append(''.join(current))
        
        if not parts:
            return None
        
        command = parts[0].strip().upper()
        params = [self.substitute_variables(p.strip()) for p in parts[1:]]
        
        return (command, params)

    def evaluate_condition(self, condition: str) -> bool:
        """
        Evaluate a conditional expression.

        Args:
            condition: Expression like "{$hp} < 30" or "{$gold} >= 100"

        Returns:
            Boolean result
        """
        # Substitute variables first
        expr = self.substitute_variables(condition)

        # Parse simple comparisons
        # Support: ==, !=, <, >, <=, >=, NOT IN, IN
        operators = ['NOT IN', 'IN', '==', '!=', '<=', '>=', '<', '>']

        for op in operators:
            if op in expr:
                parts = expr.split(op, 1)
                if len(parts) == 2:
                    left = parts[0].strip().strip('"\'')
                    right = parts[1].strip().strip('"\'')

                    # Convert to numbers if both sides are numeric
                    left_is_num = False
                    right_is_num = False

                    try:
                        if '.' in str(left):
                            left = float(left)
                        else:
                            left = int(left)
                        left_is_num = True
                    except (ValueError, TypeError):
                        pass

                    try:
                        if '.' in str(right):
                            right = float(right)
                        else:
                            right = int(right)
                        right_is_num = True
                    except (ValueError, TypeError):
                        pass

                    # If one side is numeric and the other isn't, convert both to strings
                    if left_is_num != right_is_num:
                        left = str(left)
                        right = str(right)

                    # Evaluate
                    if op == '==':
                        return left == right
                    elif op == '!=':
                        return left != right
                    elif op == '<':
                        return left < right
                    elif op == '>':
                        return left > right
                    elif op == '<=':
                        return left <= right
                    elif op == '>=':
                        return left >= right
                    elif op == 'IN':
                        return str(left) in str(right)
                    elif op == 'NOT IN':
                        return str(left) not in str(right)

        # Default to False if can't evaluate
        return False

    def execute_command(self, command: str, params: List[str]) -> Any:
        """
        Execute a command.

        Args:
            command: Command name (e.g., 'PRINT', 'SET', 'GET')
            params: Parameter list

        Returns:
            Command result
        """
        # Built-in commands
        if command == 'PRINT':
            text = params[0] if params else ''
            text = self.substitute_variables(text)
            print(text)
            self.output.append(text)
            return text

        elif command == 'SET':
            if len(params) >= 2:
                # Format: SET|var|value
                var_name = params[0].strip()
                value = params[1].strip() if len(params) > 1 else ''
                # Evaluate first (handles @function calls), then substitute variables
                value = self.evaluate_value(value)
                value = self.substitute_variables(str(value)) if isinstance(value, str) else value
                self.set_variable(var_name, value)
                return value
            elif len(params) == 1 and '|' in params[0]:
                # Old format: SET (var|value) - support for backward compat
                parts = params[0].split('|', 1)
                var_name = parts[0].strip()
                value = parts[1].strip() if len(parts) > 1 else ''
                # Evaluate first (handles @function calls), then substitute variables
                value = self.evaluate_value(value)
                value = self.substitute_variables(str(value)) if isinstance(value, str) else value
                self.set_variable(var_name, value)
                return value

        elif command == 'GET':
            var_name = params[0] if params else ''
            var_name = var_name.strip('{}$')
            return self.get_variable(var_name)

        elif command == 'EXIT':
            code = int(params[0]) if params else 0
            return ('EXIT', code)

        elif command == 'RETURN':
            # Return from function with optional value
            if params:
                value = params[0].strip()
                value = self.substitute_variables(value)
                value = self.evaluate_value(value)
                return ('RETURN', value)
            else:
                return ('RETURN', None)

        # Delegate to command handler if available
        elif self.command_handler:
            try:
                # CommandHandler uses handle_command(input_str, grid, parser) method
                # Format: "COMMAND option1 option2"
                cmd_str = f"{command} {' '.join(params)}" if params else command
                return self.command_handler.handle_command(cmd_str, self.grid, self.parser)
            except Exception as e:
                print(f"⚠️  Command '{command}' failed: {e}")
                return None

        else:
            # Stub for unimplemented commands
            print(f"ℹ️  Stub: {command}({', '.join(params)})")
            return None

    def define_function(self, name: str, params: List[str], body: List[str]) -> None:
        """
        Define a function.

        Args:
            name: Function name (without @ prefix)
            params: Parameter names (without $ prefix)
            body: List of code lines in function body
        """
        self.functions[name] = {
            'params': params,
            'body': body
        }

    def call_function(self, name: str, args: List[Any]) -> Any:
        """
        Call a function.

        Args:
            name: Function name (without @ prefix)
            args: Argument values

        Returns:
            Function return value or None
        """
        if name not in self.functions:
            raise UPYRuntimeError(f"Undefined function: @{name}")

        func = self.functions[name]
        func_params = func['params']
        func_body = func['body']

        # Check argument count
        if len(args) != len(func_params):
            raise UPYRuntimeError(
                f"Function @{name} expects {len(func_params)} arguments, got {len(args)}"
            )

        # Save current variable state (only parameters need isolation)
        saved_params = {}
        for param_name in func_params:
            if param_name in self.variables:
                saved_params[param_name] = self.variables[param_name]

        # Bind parameters
        for param_name, arg_value in zip(func_params, args):
            # Evaluate argument (substitute variables, evaluate math)
            if isinstance(arg_value, str):
                arg_value = self.substitute_variables(arg_value)
                arg_value = self.evaluate_value(arg_value)
            self.variables[param_name] = arg_value

        # Execute function body
        return_value = None
        for line in func_body:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Handle RETURN statement
            if line.startswith('RETURN '):
                expr = line[7:].strip()
                expr = self.substitute_variables(expr)
                return_value = self.evaluate_value(expr)
                break
            elif line == 'RETURN':
                return_value = None
                break

            # Execute line normally
            result = self.execute_line(line)
            
            # Check if line returned early (nested RETURN)
            if isinstance(result, tuple) and len(result) == 2 and result[0] == 'RETURN':
                return_value = result[1]
                break

        # Restore parameter variables (remove function params, restore previous values if they existed)
        for param_name in func_params:
            if param_name in saved_params:
                self.variables[param_name] = saved_params[param_name]
            else:
                # Remove parameter that didn't exist before
                self.variables.pop(param_name, None)

        return return_value

    def execute_line(self, line: str, line_num: int = 0) -> Any:
        """
        Execute a single line of uPY code.

        Args:
            line: Line to execute
            line_num: Line number (for error reporting)

        Returns:
            Execution result
        """
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith('#'):
            return None

        # Short conditionals: [IF condition: action]
        match = self.short_cond_pattern.search(line)
        if match:
            condition = match.group(1)
            action = match.group(2)

            if self.evaluate_condition(condition):
                # Execute action(s) - may have multiple separated by |
                actions = self.split_actions(action)
                for act in actions:
                    result = self.execute_line(act.strip(), line_num)
                    # Propagate RETURN from inside conditional
                    if isinstance(result, tuple) and len(result) == 2 and result[0] == 'RETURN':
                        return result
            return None

        # Medium conditionals: [IF cond THEN: action ELSE: action]
        match = self.medium_cond_pattern.search(line)
        if match:
            condition = match.group(1)
            then_action = match.group(2)
            else_action = match.group(3)

            if self.evaluate_condition(condition):
                # Execute THEN actions
                actions = self.split_actions(then_action)
                for act in actions:
                    result = self.execute_line(act.strip(), line_num)
                    # Propagate RETURN from inside conditional
                    if isinstance(result, tuple) and len(result) == 2 and result[0] == 'RETURN':
                        return result
            elif else_action:
                # Execute ELSE actions
                actions = self.split_actions(else_action)
                for act in actions:
                    result = self.execute_line(act.strip(), line_num)
                    # Propagate RETURN from inside conditional
                    if isinstance(result, tuple) and len(result) == 2 and result[0] == 'RETURN':
                        return result
            return None

        # Ternary: [condition ? action : else_action]
        match = self.ternary_pattern.search(line)
        if match:
            condition = match.group(1)
            then_action = match.group(2)
            else_action = match.group(3)

            if self.evaluate_condition(condition):
                actions = self.split_actions(then_action)
                for act in actions:
                    result = self.execute_line(act.strip(), line_num)
                    # Propagate RETURN from inside conditional
                    if isinstance(result, tuple) and len(result) == 2 and result[0] == 'RETURN':
                        return result
            else:
                actions = self.split_actions(else_action)
                for act in actions:
                    result = self.execute_line(act.strip(), line_num)
                    # Propagate RETURN from inside conditional
                    if isinstance(result, tuple) and len(result) == 2 and result[0] == 'RETURN':
                        return result
            return None

        # Function calls: @function(arg1|arg2|...)
        if line.startswith('@'):
            func_call_pattern = re.compile(r'@([a-zA-Z_][a-zA-Z0-9_-]*)\(([^\)]*)\)')
            match = func_call_pattern.match(line)
            if match:
                func_name = match.group(1)
                args_str = match.group(2)
                
                # Parse arguments (pipe-separated)
                args = []
                if args_str.strip():
                    # Split on | but respect nested parentheses
                    current_arg = []
                    paren_depth = 0
                    for char in args_str:
                        if char == '(':
                            paren_depth += 1
                            current_arg.append(char)
                        elif char == ')':
                            paren_depth -= 1
                            current_arg.append(char)
                        elif char == '|' and paren_depth == 0:
                            args.append(''.join(current_arg).strip())
                            current_arg = []
                        else:
                            current_arg.append(char)
                    
                    # Add last argument
                    if current_arg:
                        args.append(''.join(current_arg).strip())
                
                # Call function
                return self.call_function(func_name, args)

        # Commands: (COMMAND|params)
        parsed = self.parse_command(line)
        if parsed:
            command, params = parsed
            return self.execute_command(command, params)

        # If nothing matched, it might be a keyword (IF, ELSE, END IF, etc.)
        # These are handled by execute_script for multi-line structures
        return None

    def execute_script(self, script: str) -> List[str]:
        """
        Execute a complete uPY script.

        Args:
            script: Script content

        Returns:
            List of output lines
        """
        self.output = []
        lines = script.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                i += 1
                continue

            # FUNCTION definition: FUNCTION [@name($param1, $param2) ... ]
            if line.startswith('FUNCTION '):
                # Parse function signature
                func_pattern = re.compile(r'FUNCTION\s+\[@([a-zA-Z_][a-zA-Z0-9_-]*)\(([^\)]*)\)')
                match = func_pattern.match(line)
                
                if not match:
                    raise UPYRuntimeError(f"Invalid FUNCTION syntax: {line}", i)
                
                func_name = match.group(1)
                params_str = match.group(2)
                
                # Parse parameters
                params = []
                if params_str.strip():
                    # Parameters are comma-separated with $ prefix
                    for param in params_str.split(','):
                        param = param.strip()
                        if param.startswith('$'):
                            param = param[1:]  # Remove $ prefix
                        params.append(param)
                
                # Collect function body (until closing ])
                i += 1
                func_body = []
                
                while i < len(lines):
                    body_line = lines[i].strip()
                    
                    # Check for closing bracket
                    if body_line == ']':
                        # Define function
                        self.define_function(func_name, params, func_body)
                        break
                    
                    # Add to body (including empty lines for structure)
                    func_body.append(lines[i].rstrip())
                    i += 1
                
                i += 1
                continue

            # Long-form IF statement
            if line.startswith('IF '):
                # Find matching END IF
                indent_level = 0
                if_block = []
                else_if_blocks = []
                else_block = []
                current_block = if_block

                # Extract condition
                if_condition = line[3:].strip()
                i += 1

                # Collect block content
                while i < len(lines):
                    block_line = lines[i]
                    stripped = block_line.strip()

                    if stripped.startswith('ELSE IF '):
                        # New ELSE IF block
                        else_if_condition = stripped[8:].strip()
                        current_block = []
                        else_if_blocks.append((else_if_condition, current_block))
                    elif stripped == 'ELSE':
                        current_block = else_block
                    elif stripped == 'END IF':
                        # Execute the appropriate block
                        executed = False

                        if self.evaluate_condition(if_condition):
                            for if_line in if_block:
                                self.execute_line(if_line, i)
                            executed = True
                        else:
                            for elif_cond, elif_block in else_if_blocks:
                                if self.evaluate_condition(elif_cond):
                                    for elif_line in elif_block:
                                        self.execute_line(elif_line, i)
                                    executed = True
                                    break

                        if not executed and else_block:
                            for else_line in else_block:
                                self.execute_line(else_line, i)

                        break
                    else:
                        current_block.append(stripped)

                    i += 1

                i += 1
                continue

            # WHILE loop
            if line.startswith('WHILE '):
                condition = line[6:].strip()
                loop_block = []
                i += 1

                while i < len(lines):
                    block_line = lines[i].strip()
                    if block_line == 'END':
                        # Execute loop
                        while self.evaluate_condition(condition):
                            for loop_line in loop_block:
                                self.execute_line(loop_line, i)
                        break
                    else:
                        loop_block.append(block_line)
                    i += 1

                i += 1
                continue

            # FOREACH loop
            if line.startswith('FOREACH '):
                # Parse: FOREACH {$item} IN {$list}
                parts = line[8:].split(' IN ')
                if len(parts) == 2:
                    item_var = parts[0].strip().strip('{}$')
                    list_expr = parts[1].strip()

                    loop_block = []
                    i += 1

                    while i < len(lines):
                        block_line = lines[i].strip()
                        if block_line == 'END':
                            # Get list items
                            list_value = self.get_variable(list_expr.strip('{}$'))
                            if isinstance(list_value, (list, tuple)):
                                items = list_value
                            else:
                                items = str(list_value).split(',')

                            # Execute loop
                            for item in items:
                                self.set_variable(item_var, item)
                                for loop_line in loop_block:
                                    self.execute_line(loop_line, i)
                            break
                        else:
                            loop_block.append(block_line)
                        i += 1

                i += 1
                continue

            # Regular line execution
            try:
                result = self.execute_line(line, i + 1)
                if result and isinstance(result, tuple) and result[0] == 'EXIT':
                    break
            except Exception as e:
                print(f"❌ Error on line {i + 1}: {e}")
                raise UPYRuntimeError(str(e), i + 1)

            i += 1

        return self.output

    def execute_file(self, filepath: Path) -> List[str]:
        """
        Execute a uPY script file.

        Args:
            filepath: Path to .upy file

        Returns:
            List of output lines
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            script = f.read()

        return self.execute_script(script)


# Global runtime instance
_runtime = None


def get_runtime(command_handler=None, grid=None, parser=None) -> UPYRuntime:
    """Get or create global runtime instance."""
    global _runtime
    if _runtime is None:
        _runtime = UPYRuntime(command_handler, grid, parser)
    return _runtime
