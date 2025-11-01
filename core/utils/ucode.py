# uDOS v1.0.0 - uCODE Script Interpreter
# Supports IF/THEN/ELSE/ENDIF logic for setup scripts

import json
import os
import re
from datetime import datetime
import time

class UCodeInterpreter:
    """
    Interprets uCODE scripts with IF/THEN/ELSE logic.
    Used for setup scripts and automation.
    """

    def __init__(self, command_handler=None):
        self.command_handler = command_handler
        self.variables = {}  # Script variables
        self.json_cache = {}  # Cached JSON data
        self.if_stack = []  # Track nested IF blocks
        self.skip_mode = False  # Skip execution in false IF blocks

    def execute_script(self, script_path):
        """Execute a uCODE script file."""
        if not os.path.exists(script_path):
            return f"❌ ERROR: Script not found: {script_path}"

        with open(script_path, 'r') as f:
            lines = f.readlines()

        return self.execute_lines(lines)

    def execute_lines(self, lines):
        """Execute lines of uCODE."""
        results = []
        line_num = 0

        while line_num < len(lines):
            line = lines[line_num].strip()

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                line_num += 1
                continue

            # Check for control flow
            if line.startswith('[IF|'):
                line_num = self._handle_if(lines, line_num)
                continue
            elif line.startswith('[ELSE]'):
                self._handle_else()
                line_num += 1
                continue
            elif line.startswith('[ENDIF]'):
                self._handle_endif()
                line_num += 1
                continue

            # Execute if not in skip mode
            if not self.skip_mode:
                result = self._execute_ucode_line(line)
                if result:
                    results.append(result)

            line_num += 1

        return "\n".join(results)

    def _handle_if(self, lines, start_line):
        """Handle IF statement and nested block."""
        line = lines[start_line].strip()

        # Parse condition
        match = re.match(r'\[IF\|([^\]]+)\]', line)
        if not match:
            return start_line + 1

        condition = match.group(1)
        condition_met = self._evaluate_condition(condition)

        # Push to stack
        self.if_stack.append({
            'condition_met': condition_met,
            'has_else': False,
            'previous_skip': self.skip_mode
        })

        # Update skip mode
        if not condition_met:
            self.skip_mode = True

        return start_line + 1

    def _handle_else(self):
        """Handle ELSE statement."""
        if not self.if_stack:
            return

        current_if = self.if_stack[-1]
        current_if['has_else'] = True

        # Toggle skip mode
        if current_if['condition_met']:
            self.skip_mode = True
        else:
            self.skip_mode = current_if['previous_skip']

    def _handle_endif(self):
        """Handle ENDIF statement."""
        if not self.if_stack:
            return

        current_if = self.if_stack.pop()

        # Restore previous skip mode
        if self.if_stack:
            self.skip_mode = self.if_stack[-1].get('in_false_block', False)
        else:
            self.skip_mode = False

    def _evaluate_condition(self, condition):
        """Evaluate an IF condition."""
        parts = condition.split('*')
        if len(parts) < 2:
            return False

        operator = parts[0]
        operands = parts[1:]

        if operator == "EMPTY":
            var_name = operands[0]
            value = self.variables.get(var_name, "")
            return not value or value == ""

        elif operator == "NOT_EMPTY":
            var_name = operands[0]
            value = self.variables.get(var_name, "")
            return value and value != ""

        elif operator == "EQUALS":
            if len(operands) < 2:
                return False
            var_name = operands[0]
            expected = operands[1]
            actual = self.variables.get(var_name, "")
            return str(actual) == str(expected)

        elif operator == "NOT_EQUALS":
            if len(operands) < 2:
                return False
            var_name = operands[0]
            expected = operands[1]
            actual = self.variables.get(var_name, "")
            return str(actual) != str(expected)

        elif operator == "FILE_MISSING":
            file_path = operands[0]
            return not os.path.exists(file_path)

        elif operator == "FILE_EXISTS":
            file_path = operands[0]
            return os.path.exists(file_path)

        return False

    def _execute_ucode_line(self, line):
        """Execute a single uCODE line."""
        # Parse uCODE format: [MODULE|COMMAND*PARAM1*PARAM2]
        match = re.match(r'\[([^\|]+)\|([^\]]+)\]', line)
        if not match:
            return None

        module = match.group(1)
        command_str = match.group(2)
        parts = command_str.split('*')
        command = parts[0]
        params = parts[1:] if len(parts) > 1 else []

        # Substitute variables in params
        params = [self._substitute_vars(p) for p in params]

        if module == "SYSTEM":
            return self._handle_system_command(command, params)
        elif module == "FILE":
            return self._handle_file_command(command, params)
        else:
            # Pass through to command handler if available
            if self.command_handler:
                return self.command_handler.handle_command(line, None, None)

        return None

    def _substitute_vars(self, text):
        """Substitute {VAR_NAME} with variable values."""
        def replace_var(match):
            var_name = match.group(1)
            return str(self.variables.get(var_name, ""))

        return re.sub(r'\{([^\}]+)\}', replace_var, text)

    def _handle_system_command(self, command, params):
        """Handle SYSTEM module commands."""
        if command == "SET_VAR":
            if len(params) >= 2:
                self.variables[params[0]] = params[1]

        elif command == "GET_FIELD":
            if len(params) >= 2:
                json_path = params[0]
                var_name = params[1]
                value = self._get_json_field(json_path)
                self.variables[var_name] = value if value is not None else ""

        elif command == "SET_FIELD":
            if len(params) >= 2:
                json_path = params[0]
                value = params[1]
                self._set_json_field(json_path, value)

        elif command == "LOAD_JSON":
            if len(params) >= 2:
                file_path = params[0]
                cache_name = params[1]
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        self.json_cache[cache_name] = json.load(f)

        elif command == "SAVE_JSON":
            if len(params) >= 2:
                cache_name = params[0]
                file_path = params[1]
                if cache_name in self.json_cache:
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, 'w') as f:
                        json.dump(self.json_cache[cache_name], f, indent=2)

        elif command == "LOG":
            if params:
                message = " ".join(params)
                return f"📝 {message}"

        elif command == "DISPLAY":
            if params:
                return " ".join(params)
            return ""

        elif command == "PROMPT":
            if len(params) >= 2:
                prompt_text = params[0]
                var_name = params[1]
                is_required = len(params) > 2 and params[2] == "REQUIRED"

                try:
                    value = input(f"{prompt_text}: ").strip()
                    self.variables[var_name] = value

                    if is_required and not value:
                        return "❌ ERROR: Required field cannot be empty"
                except (KeyboardInterrupt, EOFError):
                    self.variables[var_name] = ""

        elif command == "TIMESTAMP":
            if params:
                var_name = params[0]
                self.variables[var_name] = datetime.now().isoformat()

        elif command == "DETECT_TIMEZONE":
            if params:
                var_name = params[0]
                # Simple timezone detection
                tz_offset = -time.timezone / 3600
                tz = f"UTC{'+' if tz_offset >= 0 else ''}{int(tz_offset)}"
                self.variables[var_name] = tz

        elif command == "CHECK_FILE":
            if params:
                file_path = params[0]
                exists = os.path.exists(file_path)
                return f"✅ File exists: {file_path}" if exists else f"❌ File missing: {file_path}"

        elif command == "ERROR":
            if params:
                return f"❌ ERROR: {' '.join(params)}"

        elif command == "WARNING":
            if params:
                return f"⚠️  WARNING: {' '.join(params)}"

        elif command == "EXIT":
            if params:
                exit_code = int(params[0]) if params[0].isdigit() else 0
                # For now, just return exit message
                return f"🚪 Exit code: {exit_code}"

        return None

    def _handle_file_command(self, command, params):
        """Handle FILE module commands."""
        if command == "COPY":
            if len(params) >= 2:
                src = params[0]
                dst = params[1]
                if os.path.exists(src):
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    with open(src, 'r') as f:
                        content = f.read()
                    with open(dst, 'w') as f:
                        f.write(content)
                    return f"✅ Copied {src} → {dst}"
                else:
                    return f"❌ Source file not found: {src}"

        return None

    def _get_json_field(self, path):
        """Get a field from cached JSON using dot notation."""
        parts = path.split('.')
        if len(parts) < 2:
            return None

        cache_name = parts[0]
        field_path = parts[1:]

        if cache_name not in self.json_cache:
            return None

        current = self.json_cache[cache_name]
        for part in field_path:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        return current

    def _set_json_field(self, path, value):
        """Set a field in cached JSON using dot notation."""
        parts = path.split('.')
        if len(parts) < 2:
            return

        cache_name = parts[0]
        field_path = parts[1:]

        if cache_name not in self.json_cache:
            self.json_cache[cache_name] = {}

        # Navigate to parent
        current = self.json_cache[cache_name]
        for part in field_path[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]

        # Set final value
        final_key = field_path[-1]

        # Convert string booleans/numbers
        if value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False
        elif value.isdigit():
            value = int(value)
        elif value.replace('.', '', 1).isdigit():
            value = float(value)

        current[final_key] = value
