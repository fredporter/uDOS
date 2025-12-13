"""
uCODE Syntax Validator and Parser
v1.2.x - Updated for uPY v1.2.x syntax

Validates and parses uCODE scripts (.upy files).
Supports v1.2.x syntax:
  - Variables: {$variable}
  - Commands: (command|params)
  - Conditionals: [IF condition: action]
  - THEN/ELSE: [IF cond THEN: action ELSE: action]
  - Long form: IF/ELSE IF/END IF
  - Functions: @name(...): expression and FUNCTION/END FUNCTION
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum


class TokenType(Enum):
    """Token types for uCODE syntax."""
    COMMAND = "command"
    VARIABLE = "variable"
    STRING = "string"
    NUMBER = "number"
    OPERATOR = "operator"
    KEYWORD = "keyword"
    COMMENT = "comment"
    PIPE = "pipe"
    BRACKET = "bracket"


@dataclass
class Token:
    """A single token in uCODE syntax."""
    type: TokenType
    value: str
    line: int
    column: int


@dataclass
class ValidationError:
    """A validation error with context."""
    message: str
    line: int
    column: int
    severity: str = "error"  # error, warning, info

    def __str__(self):
        return f"Line {self.line}, Col {self.column}: {self.severity.upper()}: {self.message}"


class CommandRegistry:
    """Registry of valid uCODE commands and their schemas."""

    # Command categories with their valid commands
    COMMANDS = {
        "GENERATE": {
            "params": ["type", "path", "format", "complexity", "style", "perspective"],
            "required": ["type", "path"],
            "description": "Generate content (guides, diagrams, checklists)"
        },
        "CONVERT": {
            "params": ["source_format", "target_format", "input", "output"],
            "required": ["source_format", "target_format", "input"],
            "description": "Convert content between formats"
        },
        "REFRESH": {
            "params": ["target", "--check", "--force", "--report"],
            "required": ["target"],
            "description": "Update content to new standards"
        },
        "MANAGE": {
            "params": ["action", "target", "options"],
            "required": ["action"],
            "description": "Organize and maintain content"
        },
        "SEARCH": {
            "params": ["query", "category", "type", "quality", "pattern"],
            "required": ["query"],
            "description": "Find and filter content"
        },
        "MISSION": {
            "params": ["action", "name"],
            "required": ["action"],
            "description": "Execute complex workflows"
        },
        "CONFIG": {
            "params": ["key", "value"],
            "required": ["key"],
            "description": "Manage settings and preferences"
        },
        "SYSTEM": {
            "params": ["action", "options"],
            "required": ["action"],
            "description": "System operations and monitoring"
        },
        "HELP": {
            "params": ["topic"],
            "required": [],
            "description": "Show help information"
        },
        "VERSION": {
            "params": [],
            "required": [],
            "description": "Show version information"
        },
        "STATUS": {
            "params": [],
            "required": [],
            "description": "Show system status"
        },
        "LOG": {
            "params": ["level", "message"],
            "required": ["level", "message"],
            "description": "Log a message"
        },
        "NOTIFY": {
            "params": ["message"],
            "required": ["message"],
            "description": "Send notification"
        },
        "REPORT": {
            "params": ["type", "options"],
            "required": ["type"],
            "description": "Generate report"
        },
        "EXTENSION": {
            "params": ["action", "name", "options"],
            "required": ["action"],
            "description": "Manage extensions"
        },
        "EXIT": {
            "params": ["code"],
            "required": [],
            "description": "Exit script"
        },
        "COMMENT": {
            "params": ["text"],
            "required": ["text"],
            "description": "Inline comment"
        },
        "DATE": {
            "params": ["format"],
            "required": [],
            "description": "Get current date or date component"
        },
        "CLEANUP": {
            "params": ["target"],
            "required": [],
            "description": "Cleanup files or directories"
        },
        "PARALLEL": {
            "params": ["commands"],
            "required": ["commands"],
            "description": "Execute commands in parallel"
        },
        "REMOTE": {
            "params": ["node", "command"],
            "required": ["node", "command"],
            "description": "Execute command on remote node"
        },
        "PROMPT": {
            "params": ["message", "options"],
            "required": ["message"],
            "description": "Interactive prompt for user input"
        },
        "IF": {
            "params": ["condition", "action"],
            "required": ["condition"],
            "description": "Conditional execution (compact syntax)"
        },
        "FOR": {
            "params": ["var", "list", "command"],
            "required": ["var", "list"],
            "description": "Loop execution (compact syntax)"
        },
        "TRY": {
            "params": ["command", "catch", "action"],
            "required": ["command"],
            "description": "Error handling (compact syntax)"
        },
        "CONTINUE": {
            "params": [],
            "required": [],
            "description": "Continue execution despite error"
        }
    }

    # Reserved keywords
    KEYWORDS = ["if", "then", "else", "elif", "fi", "for", "in", "done",
                "while", "do", "try", "catch", "finally", "on", "end"]

    # Reserved variables
    RESERVED_VARS = ["USER", "HOME", "DATE", "TIME", "WORKSPACE", "CATEGORY"]

    @classmethod
    def is_valid_command(cls, command: str) -> bool:
        """Check if command is valid."""
        return command.upper() in cls.COMMANDS

    @classmethod
    def get_command_schema(cls, command: str) -> Optional[Dict]:
        """Get schema for a command."""
        return cls.COMMANDS.get(command.upper())

    @classmethod
    def is_keyword(cls, word: str) -> bool:
        """Check if word is a reserved keyword."""
        return word.lower() in cls.KEYWORDS

    @classmethod
    def is_reserved_var(cls, var: str) -> bool:
        """Check if variable name is reserved."""
        return var.upper() in cls.RESERVED_VARS


class UCodeParser:
    """Parser for uCODE syntax - v2.0.2."""

    # v2.0.2 Regex patterns (legacy support)
    # Variables: {$name} (v1.2.24+: $name without braces)
    VARIABLE_PATTERN = re.compile(r'\{\$([a-zA-Z_][a-zA-Z0-9_.-]*)\}')

    # Commands: COMMAND[ param1 | param2 ] (v1.2.24+ bracket syntax)
    COMMAND_PATTERN = re.compile(r'\(([A-Z_]+)(?:\|([^\)]+))?\)')

    # Short conditionals: [IF condition: action]
    SHORT_COND_PATTERN = re.compile(r'\[IF\s+(.+?):\s*(.+?)\]')

    # Medium conditionals: [IF cond THEN: action ELSE: action]
    MEDIUM_COND_PATTERN = re.compile(r'\[IF\s+(.+?)\s+THEN:\s*(.+?)(?:\s+ELSE:\s*(.+?))?\]')

    # Ternary: [condition ? action : else_action]
    TERNARY_PATTERN = re.compile(r'\[(.+?)\s*\?\s*(.+?)\s*:\s*(.+?)\]')

    # Long form conditionals (IF/END IF)
    LONG_IF_START = re.compile(r'^IF\s+(.+?)$', re.MULTILINE)
    LONG_ELSE_IF = re.compile(r'^ELSE\s+IF\s+(.+?)$', re.MULTILINE)
    LONG_ELSE = re.compile(r'^ELSE$', re.MULTILINE)
    LONG_END_IF = re.compile(r'^END\s+IF$', re.MULTILINE)

    # Short functions: @name(...): expression
    SHORT_FUNC_PATTERN = re.compile(r'@([a-z_][a-z0-9_]*)\(([^\)]*)\):\s*(.+?)$')

    # Long functions: FUNCTION/END FUNCTION
    LONG_FUNC_START = re.compile(r'^FUNCTION\s+([a-z_][a-z0-9_]*)\(([^\)]*)\)$', re.MULTILINE)
    LONG_FUNC_END = re.compile(r'^END\s+FUNCTION$', re.MULTILINE)

    # Comments and strings
    COMMENT_PATTERN = re.compile(r'#\s*(.+)$')
    STRING_PATTERN = re.compile(r"'([^']*)'")

    # Keywords for v2.0.2
    KEYWORDS = ['IF', 'ELSE', 'END IF', 'THEN', 'FUNCTION', 'END FUNCTION',
                'RETURN', 'FOREACH', 'WHILE', 'END', 'LABEL', 'BRANCH']

    def __init__(self):
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
        self.variables: Dict[str, Any] = {}

    def parse_file(self, filepath: Path) -> Tuple[Dict, List[str], List[ValidationError]]:
        """
        Parse a .uscript file.

        Returns:
            (metadata, commands, errors)
        """
        if not filepath.exists():
            self.errors.append(ValidationError(
                f"File not found: {filepath}",
                line=0, column=0
            ))
            return {}, [], self.errors

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse YAML frontmatter
        metadata = self._parse_frontmatter(content)

        # Remove frontmatter from content
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                content = parts[2]

        # Parse commands
        commands = self._parse_commands(content)

        return metadata, commands, self.errors + self.warnings

    def _parse_frontmatter(self, content: str) -> Dict:
        """Extract and parse YAML frontmatter."""
        if not content.startswith('---'):
            return {}

        parts = content.split('---', 2)
        if len(parts) < 3:
            return {}

        try:
            return yaml.safe_load(parts[1]) or {}
        except yaml.YAMLError as e:
            self.errors.append(ValidationError(
                f"Invalid YAML frontmatter: {e}",
                line=1, column=0
            ))
            return {}

    def _parse_commands(self, content: str) -> List[Dict]:
        """Parse commands from content - v2.0.2 syntax."""
        commands = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            # Skip empty lines and comments
            if not line.strip() or line.strip().startswith('#'):
                continue

            # Parse v1.2.24+ command syntax: COMMAND[ params ] (legacy pattern support)
            for match in self.COMMAND_PATTERN.finditer(line):
                command = self._parse_command(match, line_num, match.start())
                if command:
                    commands.append(command)

            # Parse short conditionals: [IF ...: ...]
            for match in self.SHORT_COND_PATTERN.finditer(line):
                commands.append({
                    "type": "conditional_short",
                    "condition": match.group(1),
                    "action": match.group(2),
                    "line": line_num
                })

            # Parse medium conditionals: [IF ... THEN: ... ELSE: ...]
            for match in self.MEDIUM_COND_PATTERN.finditer(line):
                commands.append({
                    "type": "conditional_medium",
                    "condition": match.group(1),
                    "then_action": match.group(2),
                    "else_action": match.group(3) or None,
                    "line": line_num
                })

            # Parse ternary: [cond ? action : else]
            for match in self.TERNARY_PATTERN.finditer(line):
                commands.append({
                    "type": "conditional_ternary",
                    "condition": match.group(1),
                    "then_action": match.group(2),
                    "else_action": match.group(3),
                    "line": line_num
                })

            # Parse short functions: @name(...): expr
            for match in self.SHORT_FUNC_PATTERN.finditer(line):
                commands.append({
                    "type": "function_short",
                    "name": match.group(1),
                    "params": match.group(2).split('|') if match.group(2) else [],
                    "expression": match.group(3),
                    "line": line_num
                })

        return commands

    def _parse_command(self, match: re.Match, line: int, column: int) -> Optional[Dict]:
        """Parse a single command match."""
        command_name = match.group(1)
        params_str = match.group(2) or ""

        # Validate command exists
        if not CommandRegistry.is_valid_command(command_name):
            self.errors.append(ValidationError(
                f"Unknown command: {command_name}",
                line=line, column=column,
                severity="error"
            ))
            return None

        # Parse parameters
        params = self._parse_parameters(params_str, line, column)

        # Validate parameters against schema
        schema = CommandRegistry.get_command_schema(command_name)
        self._validate_params(command_name, params, schema, line, column)

        return {
            "command": command_name,
            "params": params,
            "line": line,
            "column": column
        }

    def _parse_parameters(self, params_str: str, line: int, column: int) -> List[str]:
        """Parse command parameters."""
        if not params_str:
            return []

        # Split by pipe, respecting quoted strings
        params = []
        current = ""
        in_quotes = False

        for char in params_str:
            if char == '"':
                in_quotes = not in_quotes
                current += char
            elif char == '|' and not in_quotes:
                if current.strip():
                    params.append(current.strip())
                current = ""
            else:
                current += char

        if current.strip():
            params.append(current.strip())

        return params

    def _validate_params(self, command: str, params: List[str],
                        schema: Dict, line: int, column: int):
        """Validate parameters against command schema."""
        if not schema:
            return

        required = schema.get("required", [])
        valid_params = schema.get("params", [])

        # Check required parameters
        if len(params) < len(required):
            self.errors.append(ValidationError(
                f"Command {command} requires {len(required)} parameters, got {len(params)}",
                line=line, column=column,
                severity="error"
            ))

        # Warn about too many parameters
        if len(params) > len(valid_params):
            self.warnings.append(ValidationError(
                f"Command {command} has {len(params)} parameters, expected max {len(valid_params)}",
                line=line, column=column,
                severity="warning"
            ))

    def validate_variables(self, content: str) -> List[ValidationError]:
        """Validate variable usage - v2.0.2 {$var} syntax."""
        errors = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            # Find variable assignments in SET commands: SET (var|value)
            assignment_match = re.match(r'\s*SET\s*\(([a-zA-Z_][a-zA-Z0-9_.-]*)\|', line)
            if assignment_match:
                var_name = assignment_match.group(1)

                # Check for reserved variable names
                if CommandRegistry.is_reserved_var(var_name):
                    errors.append(ValidationError(
                        f"Cannot assign to reserved variable: {var_name}",
                        line=line_num, column=0,
                        severity="error"
                    ))
                else:
                    # Track defined variables
                    self.variables[var_name] = True

            # Find variable usage {$var}
            for match in self.VARIABLE_PATTERN.finditer(line):
                var_name = match.group(1)

                # Warn about undefined variables (unless reserved or system)
                if not CommandRegistry.is_reserved_var(var_name.upper()) and \
                   '.' not in var_name and \
                   var_name not in self.variables:
                    errors.append(ValidationError(
                        f"Variable {{{var_name}}} used before assignment",
                        line=line_num, column=match.start(),
                        severity="warning"
                    ))

        return errors


class UCodeValidator:
    """Main validator for uCODE scripts."""

    def __init__(self):
        self.parser = UCodeParser()

    def validate_file(self, filepath: Path) -> Tuple[bool, List[ValidationError]]:
        """
        Validate a .upy file (v1.2.x).

        Returns:
            (is_valid, errors_and_warnings)
        """
        if filepath.suffix not in ['.upy', '.uscript']:
            return False, [ValidationError(
                f"File must have .upy or .uscript extension, got {filepath.suffix}",
                line=0, column=0
            )]

        # Parse file
        metadata, commands, parse_errors = self.parser.parse_file(filepath)

        # Read content for additional validation
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Validate variables
        var_errors = self.parser.validate_variables(content)

        # Combine all errors
        all_errors = parse_errors + var_errors

        # Check if there are any actual errors (not just warnings)
        has_errors = any(e.severity == "error" for e in all_errors)

        return not has_errors, all_errors

    def validate_syntax(self, code: str) -> Tuple[bool, List[ValidationError]]:
        """
        Validate uCODE syntax without a file.

        Returns:
            (is_valid, errors_and_warnings)
        """
        parser = UCodeParser()
        commands = parser._parse_commands(code)
        var_errors = parser.validate_variables(code)

        all_errors = parser.errors + parser.warnings + var_errors
        has_errors = any(e.severity == "error" for e in all_errors)

        return not has_errors, all_errors

    def lint_file(self, filepath: Path) -> Dict:
        """
        Lint a .uscript file and return detailed report.

        Returns:
            Dictionary with statistics and issues
        """
        is_valid, errors = self.validate_file(filepath)

        with open(filepath, 'r') as f:
            content = f.read()

        lines = content.split('\n')
        commands = self.parser.COMMAND_PATTERN.findall(content)
        variables = self.parser.VARIABLE_PATTERN.findall(content)
        comments = [line for line in lines if line.strip().startswith(('#', '//'))]

        return {
            "valid": is_valid,
            "total_lines": len(lines),
            "total_commands": len(commands),
            "total_variables": len(set(variables)),
            "total_comments": len(comments),
            "errors": [e for e in errors if e.severity == "error"],
            "warnings": [e for e in errors if e.severity == "warning"],
            "info": [e for e in errors if e.severity == "info"]
        }


def main():
    """CLI interface for validator."""
    import argparse

    parser = argparse.ArgumentParser(
        description="uCODE Syntax Validator"
    )
    parser.add_argument(
        'files',
        nargs='+',
        help='.upy or .uscript files to validate'
    )
    parser.add_argument(
        '--lint',
        action='store_true',
        help='Run linter and show detailed report'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Treat warnings as errors'
    )

    args = parser.parse_args()

    validator = UCodeValidator()
    total_errors = 0
    total_warnings = 0

    for filepath in args.files:
        path = Path(filepath)
        print(f"\nValidating: {path}")
        print("=" * 80)

        if args.lint:
            # Lint mode
            report = validator.lint_file(path)

            print(f"Lines: {report['total_lines']}")
            print(f"Commands: {report['total_commands']}")
            print(f"Variables: {report['total_variables']}")
            print(f"Comments: {report['total_comments']}")
            print()

            if report['errors']:
                print(f"Errors ({len(report['errors'])}):")
                for error in report['errors']:
                    print(f"  {error}")
                total_errors += len(report['errors'])

            if report['warnings']:
                print(f"\nWarnings ({len(report['warnings'])}):")
                for warning in report['warnings']:
                    print(f"  {warning}")
                total_warnings += len(report['warnings'])

            if report['valid'] and not report['warnings']:
                print("✅ No issues found")
        else:
            # Validation mode
            is_valid, errors = validator.validate_file(path)

            if errors:
                for error in errors:
                    print(f"  {error}")

                error_count = sum(1 for e in errors if e.severity == "error")
                warning_count = sum(1 for e in errors if e.severity == "warning")

                total_errors += error_count
                total_warnings += warning_count

                if error_count:
                    print(f"\n❌ {error_count} errors, {warning_count} warnings")
                else:
                    print(f"\n⚠️  {warning_count} warnings")
            else:
                print("✅ Valid")

    print("\n" + "=" * 80)
    print(f"Total: {total_errors} errors, {total_warnings} warnings")

    # Exit with error code if there are errors (or warnings in strict mode)
    if total_errors > 0 or (args.strict and total_warnings > 0):
        return 1
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
