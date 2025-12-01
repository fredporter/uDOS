"""
uPY Parser - Python-First Command Syntax

Bridges uCODE and Python with clean, predictable syntax:
- COMMAND(arg1|arg2|$VARIABLE|'value') - Function-style commands
- {IF condition: COMMAND(args)} - Inline conditionals
- [LABEL: code] - Named blocks/functions
- $UPPERCASE-HYPHEN - Variables
- 'strings' or "strings" - String literals

This replaces the old [MODULE|COMMAND*ARGS] format with Python-aligned syntax.
"""

import re
from typing import Dict, List, Tuple, Any, Optional
from core.runtime.upy_preprocessor import UPYPreprocessor


class UPYParseError(Exception):
    """Raised when uPY syntax is invalid"""
    pass


class UPYParser:
    """
    Parser for uPY command syntax.
    
    Syntax:
        SYSTEM-STATUS()              # No args
        FILE-SAVE('test.txt')        # String arg
        SPRITE-SET('HP'|100)         # Multiple args
        KNOWLEDGE-SEARCH($QUERY)     # Variable arg
        
    Conditionals:
        {IF $SPRITE-HP < 50: GAME-HEAL(25)}
        {IF condition: COMMAND(args) ELSE: OTHER(args)}
        
    Blocks:
        [INIT:
            SPRITE-SET('NAME'|'Hero')
            SPRITE-SET('HP'|100)
        ]
        
    Variables:
        $SPRITE-HP                   # Get variable
        SPRITE-SET('HP'|$SPRITE-HP-MAX)  # Use in command
    """
    
    def __init__(self, preprocessor: Optional[UPYPreprocessor] = None):
        """
        Initialize parser.
        
        Args:
            preprocessor: UPYPreprocessor for variable expansion
        """
        self.preprocessor = preprocessor or UPYPreprocessor()
        self.variables: Dict[str, Any] = {}
        
        # Command pattern: COMMAND-NAME(args)
        self.command_pattern = re.compile(
            r'([A-Z]+(?:-[A-Z]+)+)\s*\((.*?)\)',
            re.DOTALL
        )
        
        # Conditional pattern: {IF condition: command ELSE: command}
        self.conditional_pattern = re.compile(
            r'\{IF\s+(.+?):\s*(.+?)(?:\s+ELSE:\s*(.+?))?\}',
            re.DOTALL
        )
        
        # Block pattern: [LABEL: commands]
        self.block_pattern = re.compile(
            r'\[([A-Z-]+):\s*(.+?)\]',
            re.DOTALL
        )
        
        # Variable pattern: $UPPERCASE-HYPHEN
        self.variable_pattern = re.compile(r'\$([A-Z]+(?:-[A-Z]+)+)')
    
    def parse_args(self, args_str: str) -> List[Any]:
        """
        Parse command arguments.
        
        Args:
            args_str: Argument string (e.g., "'test'|100|$VAR")
        
        Returns:
            List of parsed arguments
        """
        if not args_str.strip():
            return []
        
        args = []
        parts = args_str.split('|')
        
        for part in parts:
            part = part.strip()
            
            # Variable reference
            if part.startswith('$'):
                var_name = part[1:]
                value = self.variables.get(var_name, part)
                args.append(value)
            
            # String literal (single or double quotes)
            elif (part.startswith("'") and part.endswith("'")) or \
                 (part.startswith('"') and part.endswith('"')):
                args.append(part[1:-1])
            
            # Number
            elif part.isdigit() or (part.startswith('-') and part[1:].isdigit()):
                args.append(int(part))
            
            # Float
            elif '.' in part:
                try:
                    args.append(float(part))
                except ValueError:
                    args.append(part)
            
            # Boolean
            elif part.upper() in ('TRUE', 'FALSE'):
                args.append(part.upper() == 'TRUE')
            
            # Raw value
            else:
                args.append(part)
        
        return args
    
    def parse_command(self, line: str) -> Optional[Tuple[str, List[Any]]]:
        """
        Parse a single command line.
        
        Args:
            line: Command line (e.g., "SYSTEM-STATUS()")
        
        Returns:
            (command_name, args) tuple or None
        """
        match = self.command_pattern.match(line.strip())
        if not match:
            return None
        
        command = match.group(1)
        args_str = match.group(2)
        args = self.parse_args(args_str)
        
        return (command, args)
    
    def parse_conditional(self, line: str) -> Optional[Dict[str, Any]]:
        """
        Parse conditional statement.
        
        Args:
            line: Conditional (e.g., "{IF $HP < 50: HEAL(25)}")
        
        Returns:
            Dict with condition, if_command, else_command
        """
        match = self.conditional_pattern.match(line.strip())
        if not match:
            return None
        
        condition = match.group(1).strip()
        if_command = match.group(2).strip()
        else_command = match.group(3).strip() if match.group(3) else None
        
        return {
            'condition': condition,
            'if_command': if_command,
            'else_command': else_command
        }
    
    def parse_block(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Parse labeled block.
        
        Args:
            text: Block (e.g., "[INIT: commands]")
        
        Returns:
            Dict with label and commands
        """
        match = self.block_pattern.match(text.strip())
        if not match:
            return None
        
        label = match.group(1)
        commands = match.group(2).strip()
        
        return {
            'label': label,
            'commands': commands
        }
    
    def evaluate_condition(self, condition: str) -> bool:
        """
        Evaluate conditional expression.
        
        Args:
            condition: Condition string (e.g., "$HP < 50")
        
        Returns:
            Boolean result
        """
        # Expand variables first
        expanded = condition
        for match in self.variable_pattern.finditer(condition):
            var_name = match.group(1)
            value = self.variables.get(var_name, 0)
            expanded = expanded.replace(match.group(0), str(value))
        
        # Evaluate safely
        try:
            # Only allow basic comparisons and numbers
            allowed_chars = set('0123456789 +-*/<>=!().')
            cleaned = ''.join(c for c in expanded if c in allowed_chars)
            
            # If cleaning changed it significantly, it's unsafe
            if len(cleaned) < len(expanded) * 0.8:
                return False
            
            return bool(eval(cleaned))
        except:
            return False
    
    def parse_line(self, line: str) -> Optional[Dict[str, Any]]:
        """
        Parse a single line of uPY code.
        
        Args:
            line: Line to parse
        
        Returns:
            Parsed structure or None
        """
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            return None
        
        # Conditional
        if line.startswith('{IF'):
            conditional = self.parse_conditional(line)
            if conditional:
                return {'type': 'conditional', **conditional}
        
        # Block
        elif line.startswith('['):
            block = self.parse_block(line)
            if block:
                return {'type': 'block', **block}
        
        # Command
        else:
            command = self.parse_command(line)
            if command:
                return {
                    'type': 'command',
                    'command': command[0],
                    'args': command[1]
                }
        
        return None
    
    def parse(self, content: str) -> List[Dict[str, Any]]:
        """
        Parse entire uPY script.
        
        Args:
            content: Script content
        
        Returns:
            List of parsed statements
        """
        statements = []
        
        for line in content.split('\n'):
            parsed = self.parse_line(line)
            if parsed:
                statements.append(parsed)
        
        return statements
    
    def to_python(self, content: str) -> str:
        """
        Convert uPY to Python code.
        
        Args:
            content: uPY script content
        
        Returns:
            Equivalent Python code
        """
        python_lines = [
            "# Auto-generated from uPY",
            "from core.runtime import get_registry",
            "",
            "def main():",
            "    registry = get_registry()",
            "    variables = {}",
            ""
        ]
        
        statements = self.parse(content)
        
        for stmt in statements:
            if stmt['type'] == 'command':
                cmd = stmt['command']
                args = stmt['args']
                args_repr = ', '.join(repr(a) for a in args)
                python_lines.append(
                    f"    registry.execute('{cmd}', [{args_repr}])"
                )
            
            elif stmt['type'] == 'conditional':
                condition = stmt['condition']
                if_cmd = stmt['if_command']
                else_cmd = stmt.get('else_command')
                
                python_lines.append(f"    if {condition}:")
                python_lines.append(f"        # {if_cmd}")
                if else_cmd:
                    python_lines.append(f"    else:")
                    python_lines.append(f"        # {else_cmd}")
            
            elif stmt['type'] == 'block':
                label = stmt['label']
                python_lines.append(f"    # Block: {label}")
                python_lines.append(f"    # {stmt['commands']}")
        
        python_lines.extend([
            "",
            "if __name__ == '__main__':",
            "    main()"
        ])
        
        return '\n'.join(python_lines)


def migrate_ucode_to_upy(ucode: str) -> str:
    """
    Migrate old [MODULE|COMMAND*ARGS] format to new uPY format.
    
    Args:
        ucode: Old uCODE command
    
    Returns:
        New uPY command
    
    Examples:
        [FILE|SAVE*test.txt] → FILE-SAVE('test.txt')
        [SPRITE|SET*HP*100] → SPRITE-SET('HP'|100)
        [SYSTEM|STATUS] → SYSTEM-STATUS()
    """
    # Strip brackets
    if ucode.startswith('[') and ucode.endswith(']'):
        ucode = ucode[1:-1]
    
    # Split module and command
    if '|' not in ucode:
        return ucode
    
    parts = ucode.split('|')
    module = parts[0].upper()
    command_parts = parts[1].split('*')
    command = command_parts[0].upper()
    args = command_parts[1:] if len(command_parts) > 1 else []
    
    # Build new format: MODULE-COMMAND(args)
    command_name = f"{module}-{command}"
    
    # Format arguments
    formatted_args = []
    for arg in args:
        # Check if it's a number
        if arg.isdigit() or (arg.startswith('-') and arg[1:].isdigit()):
            formatted_args.append(arg)
        # Check if it's a variable
        elif arg.startswith('$'):
            formatted_args.append(arg)
        # Otherwise quote it
        else:
            formatted_args.append(f"'{arg}'")
    
    args_str = '|'.join(formatted_args)
    
    return f"{command_name}({args_str})"
