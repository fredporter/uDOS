"""
uPY Preprocessor - Convert .upy scripts to Python

Part of uDOS v1.1.9+: Python-First Architecture with Enhanced Syntax

Converts uPY-style syntax to executable Python code:
- $VAR-NAME = value → vm.set_variable('VAR-NAME', value)
- PRINT("msg") → print("msg")  [emojis: :heart: → ❤️]
- IF {$HP <= 0 | PRINT("Dead")} → if vm.get_variable('HP') <= 0: print("Dead")
- FUNCTION [@NAME($PARAMS) ... ] → def function_NAME(PARAMS):
- JSON.load('file') → vm.load_json('file')
- $var.field → vm.get_nested('var', 'field')

v1.1.9+ New Features:
- Assignment operator: $VAR = value
- Emoji codes: :emoji: in PRINT strings
- JSON integration: JSON.load/save with dot notation
- Function blocks: FUNCTION [@NAME($PARAMS) ... ]
- Quote strategy: "" for PRINT, '' elsewhere
- UPPERCASE-HYPHEN naming convention

Example:
    # Input (.upy)
    $HP = 100
    PRINT(":heart: HP: $HP")

    FUNCTION [@CHECK-HEALTH($PLAYER-HP)
        IF {$PLAYER-HP <= 0 | RETURN 'dead'}
        RETURN 'alive'
    ]

    $STATUS = @CHECK-HEALTH($HP)

    # Output (Python)
    vm.set_variable('HP', 100, 'session')
    print(f"❤️ HP: {vm.get_variable('HP')}")

    def function_CHECK_HEALTH(PLAYER_HP):
        if vm.get_variable('PLAYER-HP') <= 0: return 'dead'
        return 'alive'

    vm.set_variable('STATUS', function_CHECK_HEALTH(vm.get_variable('HP')), 'session')
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


# ============================================================================
# EMOJI SYSTEM - Convert :emoji: codes to Unicode
# ============================================================================

EMOJI_MAP = {
    # Status indicators
    'check': '✅', 'cross': '❌', 'warning': '⚠️', 'info': 'ℹ️',
    'star': '⭐', 'heart': '❤️', 'ok': '👌', 'thumbsup': '👍',

    # Game items
    'sword': '⚔️', 'shield': '🛡️', 'bow': '🏹', 'axe': '🪓',
    'potion': '🧪', 'coin': '🪙', 'gem': '💎', 'diamond': '💠',
    'key': '🔑', 'chest': '📦', 'map': '🗺️', 'scroll': '📜',
    'book': '📖', 'hammer': '🔨', 'wrench': '🔧', 'pick': '⛏️',

    # Status effects
    'fire': '🔥', 'ice': '❄️', 'poison': '☠️', 'skull': '💀',
    'heal': '💚', 'magic': '✨', 'bolt': '⚡', 'zap': '⚡',
    'sparkles': '✨', 'dizzy': '💫', 'boom': '💥',

    # Directions & navigation
    'north': '⬆️', 'south': '⬇️', 'east': '➡️', 'west': '⬅️',
    'up': '⏫', 'down': '⏬', 'updown': '↕️', 'leftright': '↔️',
    'compass': '🧭', 'pin': '📍',

    # UI elements
    'menu': '☰', 'search': '🔍', 'settings': '⚙️', 'gear': '⚙️',
    'save': '💾', 'load': '📂', 'exit': '🚪', 'door': '🚪',
    'home': '🏠', 'bell': '🔔', 'flag': '🚩', 'target': '🎯',

    # Nature & environment
    'sun': '☀️', 'moon': '🌙', 'cloud': '☁️', 'rain': '🌧️',
    'snow': '🌨️', 'tree': '🌲', 'mountain': '⛰️', 'water': '💧',

    # Creatures
    'dragon': '🐉', 'snake': '🐍', 'spider': '🕷️', 'bat': '🦇',
    'wolf': '🐺', 'bear': '🐻', 'ghost': '👻', 'alien': '👽',

    # Emotions
    'smile': '😊', 'happy': '😄', 'sad': '😢', 'angry': '😠',
    'surprised': '😲', 'cool': '😎', 'scared': '😱', 'sick': '🤢',
    'sleep': '😴', 'zzz': '💤', 'think': '🤔', 'sweat': '😅',

    # Numbers & symbols
    'zero': '0️⃣', 'one': '1️⃣', 'two': '2️⃣', 'three': '3️⃣',
    'four': '4️⃣', 'five': '5️⃣', 'six': '6️⃣', 'seven': '7️⃣',
    'eight': '8️⃣', 'nine': '9️⃣', 'ten': '🔟',

    # Special characters (for escaping conflicts)
    'lbrack': '[', 'rbrack': ']',
    'lparen': '(', 'rparen': ')',
    'lbrace': '{', 'rbrace': '}',
    'langle': '<', 'rangle': '>',
    'quot': '"', 'apos': "'", 'backtick': '`',
    'laquo': '«', 'raquo': '»',
    'lsaquo': '‹', 'rsaquo': '›',

    # Typography
    'rarr': '→', 'larr': '←', 'uarr': '↑', 'darr': '↓',
    'rrarr': '⇒', 'llarr': '⇐',
    'bullet': '•', 'circle': '◦', 'square': '▪', 'diamond': '◆',
    'ndash': '–', 'mdash': '—', 'hellip': '…', 'middot': '·',
    'nbsp': '\u00A0',

    # Legal & copyright
    'copy': '©', 'reg': '®', 'tm': '™',

    # Math & logic
    'plus': '+', 'minus': '−', 'times': '×', 'divide': '÷',
    'equals': '=', 'not': '¬', 'approx': '≈', 'infinity': '∞',
    'lt': '<', 'gt': '>', 'le': '≤', 'ge': '≥', 'ne': '≠',

    # Currency
    'dollar': '$', 'euro': '€', 'pound': '£', 'yen': '¥',
}


def replace_emojis(text: str) -> str:
    """
    Replace :emoji: codes with Unicode characters.

    Examples:
        'HP: :heart: 100' → 'HP: ❤️ 100'
        'Quest :check:' → 'Quest ✅'
    """
    def replacer(match):
        emoji_name = match.group(1).lower()
        return EMOJI_MAP.get(emoji_name, match.group(0))

    return re.sub(r':([a-z0-9]+):', replacer, text)


@dataclass
class PreprocessorContext:
    """Context for preprocessing."""

    indent_level: int = 0
    block_stack: List[str] = None  # Track block types (if, label, etc.)
    labels: Dict[str, int] = None
    variables: set = None
    imports: set = None

    def __post_init__(self):
        if self.block_stack is None:
            self.block_stack = []
        if self.labels is None:
            self.labels = {}
        if self.variables is None:
            self.variables = set()
        if self.imports is None:
            self.imports = set()

    @property
    def in_block(self) -> bool:
        """Check if currently in a block."""
        return len(self.block_stack) > 0


class UPYPreprocessor:
    """
    Convert .upy scripts to executable Python code.

    Transforms uCODE syntax to Python while maintaining:
    - Variable scoping (session, persistent, temporary)
    - Control flow (IF/THEN/ELSE, GOTO/LABEL)
    - Command calls (PRINT, ROLL, CHOICE, etc.)
    - Expressions and interpolation
    """

    def __init__(self):
        """Initialize preprocessor."""
        self.context = PreprocessorContext()
        self.output_lines: List[str] = []

    def preprocess(self, source: str) -> str:
        """
        Convert .upy source to Python code.

        Args:
            source: .upy source code

        Returns:
            Python code string
        """
        self.context = PreprocessorContext()
        self.output_lines = []

        # Add imports
        self._add_imports()

        # Process each line
        for line_num, line in enumerate(source.split('\n'), 1):
            try:
                self._process_line(line, line_num)
            except Exception as e:
                raise ValueError(f"Error on line {line_num}: {e}\n  {line}")

        return '\n'.join(self.output_lines)

    def preprocess_file(self, filepath: Path) -> str:
        """
        Preprocess a .upy file.

        Args:
            filepath: Path to .upy file

        Returns:
            Python code string
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        return self.preprocess(source)

    def _add_imports(self):
        """Add necessary imports to output."""
        self.output_lines.extend([
            "# Auto-generated from .upy source",
            "# uDOS v1.1.9 Round 3",
            "",
            "from typing import List, Any",
            "from core.utils.variables import VariableManager",
            "from core.utils.command_registry import get_registry",
            "",
            "# Initialize managers",
            "vm = VariableManager()",
            "registry = get_registry()",
            "",
        ])

    def _process_line(self, line: str, line_num: int):
        """
        Process a single line of .upy code.

        Args:
            line: Source line
            line_num: Line number (for errors)
        """
        stripped = line.strip()

        # Skip empty lines and comments
        if not stripped or stripped.startswith('#'):
            self.output_lines.append(line)
            return

        # Detect command type and convert (v1.1.9+ syntax first)

        # v1.1.9+ JSON load: $VAR = JSON.load('file')
        if 'JSON.load(' in stripped and stripped.startswith('$'):
            self._convert_json_load(stripped)
        # v1.1.9+ JSON save: JSON.save('file', $var)
        elif stripped.startswith('JSON.save('):
            self._convert_json_save(stripped)
        # v1.1.9+ Assignment with dot notation or array: $VAR.field = ... or $VAR[0] = ...
        elif re.match(r'^\$[A-Z][A-Z0-9-]*[.\[]', stripped):
            self._convert_assignment(stripped)
        # v1.1.9+ Simple assignment: $VAR = value
        elif re.match(r'^\$[A-Z][A-Z0-9-]*\s*=\s*', stripped):
            self._convert_assignment(stripped)
        # v1.1.9+ Function definition: FUNCTION [@NAME($PARAMS) ... ]
        elif stripped.startswith('FUNCTION ['):
            self._convert_function_start(stripped)
        # v1.1.9+ Function end: ] (on its own line)
        elif stripped == ']' and 'function' in self.context.block_stack:
            self._convert_function_end(stripped)
        # Original commands (backwards compatible)
        elif stripped.startswith('SET '):
            self._convert_set(stripped)
        elif stripped.startswith('PRINT('):
            self._convert_print(stripped)
        elif stripped.startswith('CHOICE '):
            self._convert_choice(stripped)
        elif stripped.startswith('ROLL '):
            self._convert_roll(stripped)
        elif stripped.startswith('IF '):
            self._convert_if(stripped)
        elif stripped.startswith('ELSE'):
            self._convert_else(stripped)
        elif stripped.startswith('END'):
            self._convert_end(stripped)
        elif stripped.startswith('LABEL '):
            self._convert_label(stripped)
        elif stripped.startswith('GOTO '):
            self._convert_goto(stripped)
        elif stripped.startswith('INCLUDE '):
            self._convert_include(stripped)
        elif stripped.startswith('CALL '):
            self._convert_call(stripped)
        elif stripped.startswith('RETURN'):
            self._convert_return(stripped)
        else:
            # Unknown command - pass through as Python
            self.output_lines.append(line)

    def _convert_set(self, line: str):
        """
        Convert SET command to Python.

        Examples:
            SET HP 100 → vm.set_variable('HP', 100, 'session')
            SET NAME "Hero" → vm.set_variable('NAME', "Hero", 'session')
            SET SCORE $SCORE + 10 → vm.set_variable('SCORE', vm.get_variable('SCORE') + 10, 'session')
            SET HP-MAX 100 → vm.set_variable('HP-MAX', 100, 'session')
        """
        # Parse: SET <var> <value> [<scope>]
        # Variable names can contain hyphens (HP-MAX)
        match = re.match(r'SET\s+([\w-]+)\s+(.+?)(?:\s+(session|persistent|temporary))?$', line)
        if not match:
            raise ValueError(f"Invalid SET syntax: {line}")

        var_name = match.group(1)
        value_expr = match.group(2)
        scope = match.group(3) or 'session'

        # Convert value expression
        value_py = self._convert_expression(value_expr)

        # Track variable
        self.context.variables.add(var_name)

        # Generate Python
        indent = '    ' * self.context.indent_level
        self.output_lines.append(
            f"{indent}vm.set_variable('{var_name}', {value_py}, '{scope}')"
        )

    def _convert_assignment(self, line: str):
        """
        Convert assignment operator to Python (v1.1.9+).

        Examples:
            $HP = 100 → vm.set_variable('HP', 100, 'session')
            $PLAYER-NAME = 'Hero' → vm.set_variable('PLAYER-NAME', 'Hero', 'session')
            $HP = $HP + 10 → vm.set_variable('HP', vm.get_variable('HP') + 10, 'session')
            $PLAYER.stats.hp = 100 → vm.set_nested('PLAYER', 'stats.hp', 100)
            $ITEMS[0] = 'Sword' → vm.set_index('ITEMS', 0, 'Sword')
        """
        # Parse: $VAR-NAME = value
        # Supports: $VAR, $VAR.field, $VAR.nested.field, $VAR[index]
        match = re.match(r'^\$([A-Z][A-Z0-9-]*)([.\[].*?)?\s*=\s*(.+)$', line)
        if not match:
            raise ValueError(f"Invalid assignment syntax: {line}")

        var_name = match.group(1)
        accessor = match.group(2) or ''  # .field or [index] part
        value_expr = match.group(3)

        # Convert value expression
        value_py = self._convert_expression(value_expr)

        indent = '    ' * self.context.indent_level

        # Case 1: Nested field access ($VAR.field.subfield = value)
        if accessor.startswith('.'):
            field_path = accessor[1:]  # Remove leading dot
            self.output_lines.append(
                f"{indent}vm.set_nested('{var_name}', '{field_path}', {value_py})"
            )
        # Case 2: Array index access ($VAR[0] = value)
        elif accessor.startswith('['):
            index_match = re.match(r'\[(\d+)\]', accessor)
            if not index_match:
                raise ValueError(f"Invalid array index: {accessor}")
            index = index_match.group(1)
            self.output_lines.append(
                f"{indent}vm.set_index('{var_name}', {index}, {value_py})"
            )
        # Case 3: Simple assignment ($VAR = value)
        else:
            self.context.variables.add(var_name)
            self.output_lines.append(
                f"{indent}vm.set_variable('{var_name}', {value_py}, 'session')"
            )

    def _convert_function_start(self, line: str):
        """
        Convert FUNCTION block start to Python (v1.1.9+).

        Examples:
            FUNCTION [@CHECK-HEALTH($HP) ... ] → def function_CHECK_HEALTH(HP):
            FUNCTION [@ATTACK($TARGET, $DAMAGE) ... ] → def function_ATTACK(TARGET, DAMAGE):
        """
        # Parse: FUNCTION [@NAME($PARAM1, $PARAM2, ...) or FUNCTION [@NAME()
        match = re.match(r'FUNCTION\s+\[@([A-Z][A-Z0-9-]*)\(([^)]*)\)', line)
        if not match:
            raise ValueError(f"Invalid FUNCTION syntax: {line}")

        func_name = match.group(1)
        params_str = match.group(2).strip()

        # Parse parameters: $PARAM1, $PARAM2 → PARAM1, PARAM2
        if params_str:
            params = []
            for param in params_str.split(','):
                param = param.strip()
                if param.startswith('$'):
                    params.append(param[1:].replace('-', '_'))  # Remove $ and convert hyphens
                else:
                    raise ValueError(f"Function parameters must start with $: {param}")
            params_py = ', '.join(params)
        else:
            params_py = ''

        # Generate Python function definition
        func_name_py = func_name.replace('-', '_')  # Python doesn't like hyphens
        indent = '    ' * self.context.indent_level
        self.output_lines.append(f"{indent}def function_{func_name_py}({params_py}):")

        # Track function scope
        self.context.indent_level += 1
        self.context.block_stack.append('function')

    def _convert_function_end(self, line: str):
        """Convert FUNCTION block end ] to Python (dedent)."""
        if not self.context.in_block or self.context.block_stack[-1] != 'function':
            raise ValueError("Closing ] without FUNCTION block")

        # Pop function from stack
        self.context.block_stack.pop()
        self.context.indent_level -= 1

    def _convert_json_load(self, line: str):
        """
        Convert JSON.load() to Python (v1.1.9+).

        Examples:
            $DATA = JSON.load('player.json') → vm.set_variable('DATA', vm.load_json('player.json'), 'session')
        """
        # Parse: $VAR = JSON.load('file') or $VAR = JSON.load("file")
        match = re.match(r'^\$([A-Z][A-Z0-9-]*)\s*=\s*JSON\.load\([\'"]([^"\']+)[\'"]\)$', line)
        if not match:
            raise ValueError(f"Invalid JSON.load syntax: {line}")

        var_name = match.group(1)
        filepath = match.group(2)

        self.context.variables.add(var_name)
        indent = '    ' * self.context.indent_level
        self.output_lines.append(
            f"{indent}vm.set_variable('{var_name}', vm.load_json('{filepath}'), 'session')"
        )

    def _convert_json_save(self, line: str):
        """
        Convert JSON.save() to Python (v1.1.9+).

        Examples:
            JSON.save('player.json', $DATA) → vm.save_json('player.json', vm.get_variable('DATA'))
        """
        # Parse: JSON.save('file', $VAR)
        match = re.match(r'^JSON\.save\([\'"]([^"\']+)[\'"],\s*(.+)\)$', line)
        if not match:
            raise ValueError(f"Invalid JSON.save syntax: {line}")

        filepath = match.group(1)
        value_expr = match.group(2)

        # Convert value expression (handles $VAR)
        value_py = self._convert_expression(value_expr)

        indent = '    ' * self.context.indent_level
        self.output_lines.append(
            f"{indent}vm.save_json('{filepath}', {value_py})"
        )

    def _convert_print(self, line: str):
        """
        Convert PRINT command to Python (v1.1.9+ with emoji support).

        Examples:
            PRINT("Hello") → print("Hello")
            PRINT(":heart: HP: $HP") → print(f"❤️ HP: {vm.get_variable('HP')}")
            PRINT($HP) → print(vm.get_variable('HP'))
            PRINT("Score: $SCORE") → print(f"Score: {vm.get_variable('SCORE')}")

        v1.1.9+: Uses double quotes, supports :emoji: codes
        """
        # Parse: PRINT("message") or PRINT($variable)
        match = re.match(r'PRINT\((.+)\)$', line)
        if not match:
            raise ValueError(f"Invalid PRINT syntax: {line}")

        content = match.group(1).strip()

        # Case 1: Bare variable $HP
        if re.match(r'^\$[A-Z][A-Z0-9-]*$', content):
            var_name = content[1:]  # Remove $
            indent = '    ' * self.context.indent_level
            self.output_lines.append(f"{indent}print(vm.get_variable('{var_name}'))")
            return

        # Case 2: String literal (must be double-quoted in v1.1.9+)
        if content.startswith('"') and content.endswith('"'):
            message = content[1:-1]  # Remove quotes

            # Apply emoji replacement FIRST
            message = replace_emojis(message)

            # Check for variable interpolation
            if '$' in message:
                # Replace $VAR-NAME with {vm.get_variable('VAR-NAME')}
                message_py = re.sub(
                    r'\$([A-Z][A-Z0-9-]*)',
                    lambda m: f"{{vm.get_variable('{m.group(1)}')}}",
                    message
                )
                # Escape any existing braces (from emojis or text)
                # Actually, no - f-strings handle this
                indent = '    ' * self.context.indent_level
                self.output_lines.append(f'{indent}print(f"{message_py}")')
            else:
                # Plain string (already has emojis replaced)
                indent = '    ' * self.context.indent_level
                self.output_lines.append(f'{indent}print("{message}")')
            return

        # Case 3: Expression (no quotes)
        value_py = self._convert_expression(content)
        indent = '    ' * self.context.indent_level
        self.output_lines.append(f"{indent}print({value_py})")

    def _convert_choice(self, line: str):
        """
        Convert CHOICE command to Python.

        Examples:
            CHOICE "North|South|East" → choice = choice_handler(["North", "South", "East"])
        """
        # Parse: CHOICE <options>
        match = re.match(r'CHOICE\s+(.+)$', line)
        if not match:
            raise ValueError(f"Invalid CHOICE syntax: {line}")

        options_str = match.group(1).strip('"\'')
        options = [opt.strip() for opt in options_str.split('|')]

        indent = '    ' * self.context.indent_level
        self.output_lines.append(
            f"{indent}choice = choice_handler({options})"
        )

    def _convert_roll(self, line: str):
        """
        Convert ROLL command to Python.

        Examples:
            ROLL 1d20 → result = roll_dice('1d20')
            ROLL 2d6+3 → result = roll_dice('2d6+3')
        """
        # Parse: ROLL <dice>
        match = re.match(r'ROLL\s+(.+)$', line)
        if not match:
            raise ValueError(f"Invalid ROLL syntax: {line}")

        dice_expr = match.group(1)

        indent = '    ' * self.context.indent_level
        self.output_lines.append(
            f"{indent}result = roll_dice('{dice_expr}')"
        )

    def _convert_if(self, line: str):
        """
        Convert IF command to Python (v1.1.9+ enhanced).

        Examples:
            IF $HP > 50 THEN → if vm.get_variable('HP') > 50:
            IF {$HP > 50 | PRINT("High HP")} → if vm.get_variable('HP') > 50: print("High HP")
            IF {$HP <= 0 | RETURN 'dead'} → if vm.get_variable('HP') <= 0: return 'dead'
        """
        # Check for inline IF: IF {condition | action}
        inline_match = re.match(r'IF\s+\{(.+?)\s+\|\s+(.+)\}$', line)
        if inline_match:
            condition = inline_match.group(1)
            action = inline_match.group(2)

            condition_py = self._convert_expression(condition)

            indent = '    ' * self.context.indent_level
            # Process the action as a separate line
            action_line = self._convert_inline_action(action)
            self.output_lines.append(f"{indent}if {condition_py}: {action_line}")
            return

        # Parse block IF: IF <condition> THEN
        match = re.match(r'IF\s+(.+?)\s+THEN', line)
        if not match:
            raise ValueError(f"Invalid IF syntax: {line}")

        condition = match.group(1)
        condition_py = self._convert_expression(condition)

        indent = '    ' * self.context.indent_level
        self.output_lines.append(f"{indent}if {condition_py}:")

        self.context.indent_level += 1
        self.context.block_stack.append('if')

    def _convert_else(self, line: str):
        """Convert ELSE to Python."""
        if not self.context.in_block or self.context.block_stack[-1] != 'if':
            raise ValueError("ELSE without IF")

        self.context.indent_level -= 1
        indent = '    ' * self.context.indent_level
        self.output_lines.append(f"{indent}else:")
        self.context.indent_level += 1
        # Replace 'if' with 'else' on stack
        self.context.block_stack[-1] = 'else'

    def _convert_end(self, line: str):
        """Convert END to Python (dedent)."""
        if not self.context.in_block:
            raise ValueError("END without block start")

        # Pop block from stack
        block_type = self.context.block_stack.pop()
        self.context.indent_level -= 1

    def _convert_label(self, line: str):
        """
        Convert LABEL to Python function.

        Examples:
            LABEL start → def label_start():
        """
        # Parse: LABEL <name>
        match = re.match(r'LABEL\s+(\w+)', line)
        if not match:
            raise ValueError(f"Invalid LABEL syntax: {line}")

        label_name = match.group(1)
        self.context.labels[label_name] = len(self.output_lines)

        indent = '    ' * self.context.indent_level
        self.output_lines.append(f"{indent}def label_{label_name}():")
        self.context.indent_level += 1
        self.context.block_stack.append('label')

    def _convert_goto(self, line: str):
        """
        Convert GOTO to Python function call.

        Examples:
            GOTO start → label_start()
        """
        # Parse: GOTO <label>
        match = re.match(r'GOTO\s+(\w+)', line)
        if not match:
            raise ValueError(f"Invalid GOTO syntax: {line}")

        label_name = match.group(1)

        indent = '    ' * self.context.indent_level
        self.output_lines.append(f"{indent}label_{label_name}()")

    def _convert_include(self, line: str):
        """
        Convert INCLUDE to Python import.

        Examples:
            INCLUDE helpers → from helpers import *
        """
        # Parse: INCLUDE <module>
        match = re.match(r'INCLUDE\s+(\w+)', line)
        if not match:
            raise ValueError(f"Invalid INCLUDE syntax: {line}")

        module_name = match.group(1)
        self.context.imports.add(module_name)

        # Add import at top
        import_line = f"from {module_name} import *"
        # Insert after existing imports
        for i, line in enumerate(self.output_lines):
            if line.startswith("# Initialize"):
                self.output_lines.insert(i, import_line)
                break

    def _convert_call(self, line: str):
        """
        Convert CALL command to Python function call.

        Examples:
            CALL HELP → registry.get_handler('HELP')([])
            CALL MAP-SHOW → registry.get_handler('MAP-SHOW')([])
        """
        # Parse: CALL <command> [args...]
        match = re.match(r'CALL\s+([\w-]+)(?:\s+(.+))?$', line)
        if not match:
            raise ValueError(f"Invalid CALL syntax: {line}")

        command = match.group(1)
        args_str = match.group(2) or ''

        # Parse arguments
        args = []
        if args_str:
            # Simple split for now (TODO: handle quoted strings)
            args = [arg.strip() for arg in args_str.split()]

        indent = '    ' * self.context.indent_level
        self.output_lines.append(
            f"{indent}registry.get_handler('{command}')({args})"
        )

    def _convert_return(self, line: str):
        """Convert RETURN to Python."""
        indent = '    ' * self.context.indent_level

        # Parse: RETURN [value]
        match = re.match(r'RETURN(?:\s+(.+))?$', line)
        if match and match.group(1):
            value = self._convert_expression(match.group(1))
            self.output_lines.append(f"{indent}return {value}")
        else:
            self.output_lines.append(f"{indent}return")

    def _convert_inline_action(self, action: str) -> str:
        """
        Convert inline action to Python (for inline IF statements).

        Examples:
            PRINT("Success!") → print("Success!")
            PRINT($HP) → print(vm.get_variable('HP'))
            RETURN 'dead' → return 'dead'
            @CHECK-HP($HP) → function_CHECK_HP(vm.get_variable('HP'))
        """
        action = action.strip()

        # PRINT("message") or PRINT($var) - v1.1.9+ syntax
        if action.startswith('PRINT(') and action.endswith(')'):
            content = action[6:-1]  # Remove 'PRINT(' and ')'

            # Bare variable $HP
            if re.match(r'^\$[A-Z][A-Z0-9-]*$', content):
                var_name = content[1:]
                return f"print(vm.get_variable('{var_name}'))"

            # String with emojis and interpolation
            if content.startswith('"') and content.endswith('"'):
                message = content[1:-1]
                message = replace_emojis(message)  # Apply emoji replacement

                if '$' in message:
                    message_py = re.sub(
                        r'\$([A-Z][A-Z0-9-]*)',
                        lambda m: f"{{vm.get_variable('{m.group(1)}')}}",
                        message
                    )
                    return f'print(f"{message_py}")'
                else:
                    return f'print("{message}")'

        # RETURN 'value' or RETURN $VAR
        if action.startswith('RETURN '):
            value = action[7:].strip()
            value_py = self._convert_expression(value)
            return f"return {value_py}"

        # Function call @FUNC-NAME($PARAMS)
        if action.startswith('@'):
            func_call_py = self._convert_expression(action)
            return func_call_py

        # SET var value (backwards compatible)
        if action.startswith('SET '):
            match = re.match(r'SET\s+([A-Z][A-Z0-9-]*)\s+(.+)$', action)
            if match:
                var_name = match.group(1)
                value = self._convert_expression(match.group(2))
                return f"vm.set_variable('{var_name}', {value}, 'session')"

        # GOTO label (backwards compatible)
        if action.startswith('GOTO '):
            label = action[5:].strip()
            return f"label_{label}()"

        # Default: return as-is
        return action

    def _convert_expression(self, expr: str) -> str:
        """
        Convert uPY expression to Python (v1.1.9+ enhanced).

        Examples:
            $HP → vm.get_variable('HP')
            $HP + 10 → vm.get_variable('HP') + 10
            $HP-MAX → vm.get_variable('HP-MAX')
            $PLAYER.stats.hp → vm.get_nested('PLAYER', 'stats.hp')
            $ITEMS[0] → vm.get_index('ITEMS', 0)
            @CHECK-HEALTH($HP) → function_CHECK_HEALTH(vm.get_variable('HP'))
            'text' → 'text'
            100 → 100
        """
        expr = expr.strip()

        # Function calls: @FUNC-NAME($PARAM1, $PARAM2)
        if '@' in expr:
            expr = re.sub(
                r'@([A-Z][A-Z0-9-]*)\(([^)]*)\)',
                lambda m: self._convert_function_call(m.group(1), m.group(2)),
                expr
            )

        # Variable with dot notation: $VAR.field.subfield
        expr = re.sub(
            r'\$([A-Z][A-Z0-9-]*)(\.[a-zA-Z_][a-zA-Z0-9_.]*)',
            lambda m: f"vm.get_nested('{m.group(1)}', '{m.group(2)[1:]}')",
            expr
        )

        # Variable with array indexing: $VAR[0]
        expr = re.sub(
            r'\$([A-Z][A-Z0-9-]*)\[(\d+)\]',
            lambda m: f"vm.get_index('{m.group(1)}', {m.group(2)})",
            expr
        )

        # Simple variables: $VAR or $VAR-NAME
        expr = re.sub(
            r'\$([A-Z][A-Z0-9-]*)',
            lambda m: f"vm.get_variable('{m.group(1)}')",
            expr
        )

        return expr

    def _convert_function_call(self, func_name: str, params_str: str) -> str:
        """
        Convert function call to Python.

        Examples:
            @CHECK-HEALTH, '$HP' → function_CHECK_HEALTH(vm.get_variable('HP'))
            @ATTACK, '$TARGET, 50' → function_ATTACK(vm.get_variable('TARGET'), 50)
        """
        func_name_py = func_name.replace('-', '_')

        # Parse parameters
        if params_str.strip():
            params = [p.strip() for p in params_str.split(',')]
            # Convert each parameter expression
            params_py = ', '.join(self._convert_expression(p) for p in params)
        else:
            params_py = ''

        return f"function_{func_name_py}({params_py})"
def preprocess_upy(source: str) -> str:
    """
    Convenience function to preprocess .upy source.

    Args:
        source: .upy source code

    Returns:
        Python code string
    """
    preprocessor = UPYPreprocessor()
    return preprocessor.preprocess(source)


def preprocess_upy_file(filepath: Path) -> str:
    """
    Convenience function to preprocess .upy file.

    Args:
        filepath: Path to .upy file

    Returns:
        Python code string
    """
    preprocessor = UPYPreprocessor()
    return preprocessor.preprocess_file(filepath)


# Helper functions (to be implemented in runtime)
def choice_handler(options: List[str]) -> str:
    """Present choices and get user selection."""
    print("\nChoose:")
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")

    while True:
        choice = input("> ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx]
        except ValueError:
            # Try text match
            for option in options:
                if choice.lower() == option.lower():
                    return option

        print("Invalid choice. Try again.")


def roll_dice(dice_expr: str) -> int:
    """
    Roll dice from expression.

    Examples:
        roll_dice('1d20') → 1-20
        roll_dice('2d6+3') → 5-15
    """
    import random

    # Parse dice expression (simple version)
    match = re.match(r'(\d+)d(\d+)(?:([+\-])(\d+))?', dice_expr)
    if not match:
        raise ValueError(f"Invalid dice expression: {dice_expr}")

    num_dice = int(match.group(1))
    die_size = int(match.group(2))
    modifier_op = match.group(3)
    modifier_val = int(match.group(4)) if match.group(4) else 0

    # Roll dice
    total = sum(random.randint(1, die_size) for _ in range(num_dice))

    # Apply modifier
    if modifier_op == '+':
        total += modifier_val
    elif modifier_op == '-':
        total -= modifier_val

    return total
