# uPY v1.2 Runtime Architecture

**Version:** v1.2 (uDOS v1.2.21)
**Last Updated:** December 8, 2025
**Status:** Production Ready

## Overview

The uPY v1.2 runtime is a custom interpreter designed to execute `.upy` scripts with native support for v1.2 syntax. Unlike previous versions that relied on Python transpilation, v2.0.2 uses direct interpretation with pattern matching for better performance, type safety, and cleaner error messages.

## Design Principles

### 1. **No Transpilation**
- Scripts execute directly without converting to Python code
- Eliminates `exec()` security concerns
- Faster execution (no compilation overhead)
- Cleaner error messages (no Python stack traces)

### 2. **Pattern-Based Interpretation**
- Regex patterns match v1.2 syntax
- Clear separation between syntax types
- Easy to extend with new features
- Type-safe operations

### 3. **Integration with uDOS Core**
- Full access to CommandHandler (all uDOS commands)
- Grid system integration (mapping, locations)
- Config system integration (user settings)
- Knowledge system integration (survival guides)

### 4. **Backward Compatibility**
- Supports v1.x syntax (legacy mode)
- Automatic version detection
- Graceful degradation for unsupported features

## Architecture Components

### Core Modules

```
core/runtime/
├── upy_runtime.py      # Main interpreter engine (1,179 lines)
├── upy_math.py            # Math expression parser (343 lines)
├── upy_lists.py           # List operations (325 lines)
├── upy_file_io.py         # File I/O module (344 lines)
└── __init__.py            # Package initialization
```

### Component Responsibilities

#### 1. **UPYRuntime** (`upy_runtime.py`)

**Main interpreter engine** - Orchestrates script execution and manages state.

**Key Features:**
- Variable storage and substitution (`{$var}`)
- Function definitions and calls (`@function()`)
- Conditional execution (`IF/ELSE IF/ELSE`)
- Loop structures (`WHILE`, `FOREACH`)
- Command execution via CommandHandler
- Scope management (global, function-local)
- Return value handling

**Execution Flow:**
```python
1. Parse script into lines
2. For each line:
   a. Strip comments (#)
   b. Substitute variables {$var}
   c. Match syntax pattern (function, conditional, loop, command)
   d. Execute matched pattern
   e. Handle RETURN early exit
3. Return final output
```

**Pattern Hierarchy:**
1. Comments (`#`)
2. Function definitions (`FUNCTION ... END FUNCTION`)
3. Conditionals (`IF ... END IF`)
4. Loops (`WHILE ... END WHILE`, `FOREACH`)
5. Commands (`(COMMAND|params)`)
6. Short conditionals (`[IF cond: action]`)

#### 2. **MathParser** (`upy_math.py`)

**Arithmetic expression evaluator** - Parses and evaluates math expressions with PEMDAS.

**Supported Operations:**
- Addition: `{$x} + 5`
- Subtraction: `{$y} - 10`
- Multiplication: `{$a} * 2`
- Division: `{$b} / 3`
- Modulo: `{$n} % 7`
- Power: `{$base} ** {$exp}`
- Parentheses: `({$a} + {$b}) * 2`

**Algorithm:**
- Recursive descent parser
- Tokenization (numbers, operators, variables, parentheses)
- Operator precedence (PEMDAS)
- Variable substitution from runtime context
- Type coercion (int/float)

**Example:**
```python
# Input: "{$hp} * 2 + 10"
# Variables: {"hp": 50}
# Output: 110

# Parsing steps:
1. Tokenize: ["{$hp}", "*", "2", "+", "10"]
2. Substitute: ["50", "*", "2", "+", "10"]
3. Parse expression tree:
       +
      / \
     *   10
    / \
   50  2
4. Evaluate: (50 * 2) + 10 = 110
```

**Performance:**
- O(n) tokenization (single pass)
- O(log n) tree depth (balanced expressions)
- <1ms for typical expressions

#### 3. **ListOperations** (`upy_lists.py`)

**List data structure support** - Manages list literals and operations.

**Supported Operations:**
- `LIST CREATE <name> [item1, item2, ...]` - Create list
- `LIST APPEND <name> <value>` - Add to end
- `LIST REMOVE <name> <index>` - Remove by index
- `LIST INSERT <name> <index> <value>` - Insert at position
- `LIST GET <name> <index>` - Read element
- `LIST SET <name> <index> <value>` - Update element
- `LIST SIZE <name>` - Get length
- `LIST SLICE <name> <start> <end>` - Extract sublist
- `LIST CONTAINS <name> <value>` - Check membership
- `LIST INDEX <name> <value>` - Find position
- `LIST CLEAR <name>` - Empty list
- `LIST JOIN <name> <delimiter>` - Convert to string
- `LIST SPLIT <string> <delimiter>` - Parse into list

**List Literal Syntax:**
```python
# Basic literal
[apple, banana, cherry]

# With variables
[{$item1}, {$item2}, {$item3}]

# Mixed types
[42, text, {$var}]

# Nested lists
[[a, b], [c, d], [e, f]]
```

**Parsing Algorithm:**
1. Find opening `[` and closing `]`
2. Extract content between brackets
3. Split by commas (respecting quotes and nested brackets)
4. Trim whitespace from each item
5. Substitute variables (`{$var}`)
6. Return list of strings

**Integration:**
- Lists stored in runtime variables
- FOREACH iterates over lists
- SET command evaluates list literals
- Functions can accept list parameters

#### 4. **FileIO** (`upy_file_io.py`)

**File system operations** - Read/write files with JSON support.

**Supported Operations:**
- `FILE READ <path>` - Read entire file
- `FILE WRITE <path> <content>` - Write file (overwrite)
- `FILE EXISTS <path>` - Check if file exists
- `FILE DELETE <path>` - Remove file
- `FILE SIZE <path>` - Get byte size
- `FILE LIST <directory>` - List directory contents
- `JSON PARSE <json_string>` - Parse JSON to dict
- `JSON STRINGIFY <data>` - Convert to JSON string
- `JSON READ <path>` - Load JSON file
- `JSON WRITE <path> <data>` - Save JSON file

**Path Handling:**
- Absolute paths supported
- Relative paths from project root
- `memory/` workspace integration
- `.archive/` folder support

**JSON Integration:**
```python
# Read JSON config
(SET|config|(JSON READ|memory/config.json))

# Parse inline JSON
(SET|data|(JSON PARSE|{"name": "Alice", "age": 30}))

# Write data
(JSON WRITE|memory/output.json|{$data})
```

**Error Handling:**
- File not found → returns error message
- Permission denied → returns error message
- Invalid JSON → returns parse error
- Directory operations → list files/folders

### Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     uPY Script (.upy)                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 UPYRuntimeV2 Engine                          │
│  • Parse lines                                               │
│  • Match patterns                                            │
│  • Execute logic                                             │
└───┬─────────────┬──────────────┬─────────────┬──────────────┘
    │             │              │             │
    ▼             ▼              ▼             ▼
┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│ Math    │  │ Lists    │  │ File I/O │  │ Commands │
│ Parser  │  │ Ops      │  │ Module   │  │ Handler  │
└─────────┘  └──────────┘  └──────────┘  └────┬─────┘
                                               │
                                               ▼
                                    ┌──────────────────────┐
                                    │   uDOS Core          │
                                    │  • Grid System       │
                                    │  • Config Manager    │
                                    │  • Knowledge System  │
                                    │  • Extension System  │
                                    └──────────────────────┘
```

## Execution Model

### Variable Substitution

Variables use `{$name}` syntax and are substituted before execution.

**Variable Sources:**
1. **User-defined:** `(SET|name|value)`
2. **System variables:** `{$MISSION.ID}`, `{$WORKFLOW.PHASE}`
3. **Function parameters:** `{$param1}`, `{$param2}`
4. **Loop variables:** `{$item}` in FOREACH

**Substitution Algorithm:**
```python
def substitute_variables(line, variables):
    pattern = r'\{\$([a-zA-Z_][a-zA-Z0-9_.]*)\}'

    def replace(match):
        var_name = match.group(1)

        # Check function scope first (local variables)
        if var_name in function_scope:
            return str(function_scope[var_name])

        # Check global scope
        if var_name in variables:
            return str(variables[var_name])

        # System variables (MISSION, WORKFLOW, etc.)
        if var_name.startswith('MISSION.'):
            return get_mission_variable(var_name)

        # Variable not found - return original
        return match.group(0)

    return re.sub(pattern, replace, line)
```

**Example:**
```python
# Script:
(SET|hp|100)
(SET|damage|25)
(SET|new_hp|{$hp} - {$damage})
(ECHO|HP: {$new_hp})

# Execution:
1. SET hp = 100
2. SET damage = 25
3. Substitute: {$hp} - {$damage} → 100 - 25
4. Evaluate math: 100 - 25 = 75
5. SET new_hp = 75
6. Substitute: HP: {$new_hp} → HP: 75
7. ECHO: HP: 75
```

### Function Execution

Functions support both short and long forms with parameter binding.

**Short Function (Inline):**
```python
# Definition
@add(a, b): {$a} + {$b}

# Call
(SET|sum|@add(5, 10))
# Result: sum = 15
```

**Long Function (Block):**
```python
# Definition
FUNCTION calculate_damage($attack, $defense)
    (SET|base_damage|{$attack} * 2)
    (SET|reduction|{$defense} / 10)
    (SET|final_damage|{$base_damage} - {$reduction})
    RETURN {$final_damage}
END FUNCTION

# Call
(SET|damage|@calculate_damage(50, 20))
# Result: damage = 98 (50*2 - 20/10 = 100 - 2)
```

**Execution Steps:**
1. **Parse function definition**
   - Extract name, parameters, body
   - Store in `self.functions` dict
2. **Match function call** (`@name(args)`)
   - Extract arguments (comma or pipe separated)
   - Create function scope (isolated from global)
3. **Bind parameters**
   - Map arguments to parameter names
   - Store in function scope
4. **Execute function body**
   - Run each line in function context
   - Variables use function scope first, then global
5. **Handle RETURN**
   - Extract return value
   - Exit function immediately
   - Return value to caller
6. **Clean up scope**
   - Function scope discarded after execution
   - Only return value persists

**Scope Isolation:**
```python
# Global scope
(SET|x|10)

FUNCTION test()
    (SET|x|20)  # Local x (shadows global)
    (ECHO|Inside: {$x})  # Prints 20
END FUNCTION

@test()
(ECHO|Outside: {$x})  # Prints 10 (global unchanged)
```

### Conditional Execution

Three conditional formats with different complexity levels.

**Short Conditional (Inline):**
```python
[IF {$hp} < 20: (ECHO|Low health!)]
```

**Medium Conditional (Ternary):**
```python
[IF {$hp} > 50 THEN: (ECHO|Healthy) ELSE: (ECHO|Damaged)]
```

**Long Conditional (Block):**
```python
IF {$hp} > 80
    (ECHO|Full health)
    (SET|status|healthy)
ELSE IF {$hp} > 50
    (ECHO|Moderate health)
    (SET|status|okay)
ELSE IF {$hp} > 20
    (ECHO|Low health)
    (SET|status|injured)
ELSE
    (ECHO|Critical!)
    (SET|status|critical)
END IF
```

**Condition Evaluation:**
- Comparison operators: `>`, `<`, `>=`, `<=`, `==`, `!=`
- Variable substitution before comparison
- Type coercion (numbers vs strings)
- Boolean logic (AND, OR, NOT planned for future)

### Loop Structures

Two loop types: WHILE (condition-based) and FOREACH (iteration).

**WHILE Loop:**
```python
(SET|counter|0)
WHILE {$counter} < 5
    (ECHO|Count: {$counter})
    (SET|counter|{$counter} + 1)
END WHILE
```

**FOREACH Loop:**
```python
# Iterate over list literal
FOREACH item IN [apple, banana, cherry]
    (ECHO|Fruit: {$item})
END FOREACH

# Iterate over list variable
(SET|fruits|[apple, banana, cherry])
FOREACH fruit IN {$fruits}
    (ECHO|{$fruit})
END FOREACH
```

**Loop Control:**
- WHILE evaluates condition each iteration
- FOREACH iterates until list exhausted
- Variables update in place
- Break/continue not yet implemented (planned)

## Command Integration

### CommandHandler Interface

All uDOS commands are accessible via `(COMMAND|params)` syntax.

**Command Execution:**
```python
def execute_command(self, command_line):
    # Parse: (COMMAND|param1|param2|...)
    match = re.match(r'\(([A-Z]+)\|(.+?)\)', command_line)
    if not match:
        return None

    command = match.group(1)
    params_str = match.group(2)

    # Split parameters by pipe (respecting nested parentheses)
    params = self.smart_split_action(params_str)

    # Call CommandHandler
    result = self.command_handler.execute_command(command, params)

    return result
```

**Available Commands:**
- **File operations:** `FILE READ`, `FILE WRITE`, `FILE DELETE`, etc.
- **List operations:** `LIST CREATE`, `LIST APPEND`, etc.
- **JSON operations:** `JSON PARSE`, `JSON STRINGIFY`, etc.
- **Graphics:** `DRAW`, `SPRITE`, `PANEL`
- **Knowledge:** `GUIDE`, `SEARCH`
- **Mapping:** `MAP`, `NAVIGATE`
- **System:** `ECHO`, `SET`, `GET`
- **Extensions:** All extension commands

**Nested Commands:**
```python
# Command within command
(SET|data|(FILE READ|memory/config.json))

# Multiple nesting levels
(SET|parsed|(JSON PARSE|(FILE READ|memory/data.json)))
```

### Smart Action Splitting

Handles complex parameter parsing with nested parentheses.

**Algorithm:**
```python
def smart_split_action(self, action):
    parts = []
    current = ""
    depth = 0

    for char in action:
        if char == '(':
            depth += 1
            current += char
        elif char == ')':
            depth -= 1
            current += char
        elif char == '|' and depth == 0:
            parts.append(current.strip())
            current = ""
        else:
            current += char

    if current:
        parts.append(current.strip())

    return parts
```

**Example:**
```python
# Input: "SET|data|(JSON PARSE|(FILE READ|file.json))"
# Output: ["SET", "data", "(JSON PARSE|(FILE READ|file.json))"]

# Parsing:
1. char='S': depth=0, current="S"
2. char='E': depth=0, current="SE"
3. char='T': depth=0, current="SET"
4. char='|': depth=0, append "SET", current=""
5. char='d': depth=0, current="d"
6. ...
7. char='|': depth=0, append "data", current=""
8. char='(': depth=1, current="("
9. char='J': depth=1, current="(J"
10. ...
11. char='(': depth=2, current="...(FILE READ"
12. char=')': depth=1, current="...READ|file.json)"
13. char=')': depth=0, current="...|file.json))"
14. End: append "(JSON PARSE|(FILE READ|file.json))"
```

## Performance Characteristics

### Execution Speed

**Benchmarks** (on 2023 MacBook Pro M2):

| Operation | Time | Notes |
|-----------|------|-------|
| Variable substitution | <0.1ms | Per line |
| Math expression | <1ms | Typical complexity |
| Function call | <2ms | Including parameter binding |
| Conditional | <0.5ms | Simple comparison |
| Loop iteration | <1ms | Per iteration |
| Command execution | 1-50ms | Depends on command |
| List operation | <0.5ms | Average |
| File I/O | 5-20ms | Disk latency |

**Script Execution:**
- Small scripts (10-50 lines): <10ms
- Medium scripts (100-500 lines): 20-100ms
- Large scripts (1000+ lines): 100-500ms

**Optimization Strategies:**
1. **Variable caching** - Store substituted values
2. **Pattern pre-compilation** - Compile regex once
3. **Function memoization** - Cache pure function results
4. **Lazy evaluation** - Defer command execution when possible

### Memory Usage

**Memory Footprint:**
- Runtime instance: ~100 KB
- Variables: ~1 KB per variable
- Functions: ~5 KB per function
- Lists: ~1 KB per 100 items
- Typical script: 200-500 KB total

**Memory Management:**
- Variables garbage collected when out of scope
- Function scopes discarded after execution
- Large lists stored as references (not copied)
- File I/O uses streaming for large files

## Error Handling

### Error Types

1. **Syntax Errors**
   - Invalid function syntax
   - Malformed conditionals
   - Unclosed loops
   - Missing END markers

2. **Runtime Errors**
   - Undefined variable
   - Division by zero
   - File not found
   - Invalid JSON

3. **Type Errors**
   - Non-numeric in math operation
   - Invalid list index
   - Type mismatch in comparison

4. **Logic Errors**
   - Infinite loops
   - Stack overflow (deep recursion)
   - Return outside function

### Error Messages

**Clear, actionable errors:**
```python
# Undefined variable
Error: Variable 'hp' not defined
  Line 5: (ECHO|HP: {$hp})
  Suggestion: Use (SET|hp|100) before referencing

# Invalid math
Error: Cannot divide by zero
  Line 12: (SET|result|{$x} / {$y})
  Values: x=10, y=0

# File not found
Error: File not found: memory/config.json
  Line 8: (FILE READ|memory/config.json)
  Suggestion: Check path or use FILE EXISTS first

# Invalid function call
Error: Function 'calculate' expects 2 parameters, got 1
  Line 15: @calculate(5)
  Definition: FUNCTION calculate($a, $b)
```

### Error Recovery

**Graceful degradation:**
- Continue execution on non-fatal errors
- Log errors to `memory/logs/runtime_errors.log`
- Return error messages instead of crashing
- Provide suggestions for common mistakes

## Testing

### Test Coverage

**Test Suite:** `memory/ucode/test_upy_v2_0_2_*.py`

**Categories:**
1. **Math Operations** (75 tests)
   - Basic arithmetic (+, -, *, /, %)
   - Power operator (**)
   - Parentheses and PEMDAS
   - Variable substitution
   - Type coercion

2. **Functions** (150 tests)
   - Short function definitions
   - Long function blocks
   - Parameter binding
   - Return values
   - Nested calls
   - Scope isolation

3. **Lists** (296 tests)
   - List literals
   - All LIST commands
   - FOREACH iteration
   - Negative indexing
   - Nested lists
   - Variable substitution

4. **File I/O** (380 tests)
   - FILE commands (read, write, exists, delete, size, list)
   - JSON commands (parse, stringify, read, write)
   - Path handling
   - Error conditions
   - Integration with variables

5. **Integration** (272 tests)
   - Math + lists
   - Math + file I/O
   - Lists + file I/O
   - Complex workflows

6. **Validation** (238 tests)
   - Syntax validation
   - Error detection
   - Edge cases
   - Performance benchmarks

**Total:** 1,411 tests, 100% passing

### Running Tests

```bash
# All tests
pytest memory/ucode/test_upy_v2_0_2_*.py -v

# Specific category
pytest memory/ucode/test_upy_math.py -v
pytest memory/ucode/test_upy_functions.py -v
pytest memory/ucode/test_upy_lists.py -v
pytest memory/ucode/test_upy_file_io.py -v

# Integration tests
pytest memory/ucode/test_upy_integration.py -v

# With coverage
pytest memory/ucode/test_upy_v2_0_2_*.py --cov=core/runtime --cov-report=html
```

## Future Enhancements

### Planned Features

1. **Boolean Logic**
   - AND, OR, NOT operators
   - Complex conditionals
   - Short-circuit evaluation

2. **Loop Control**
   - BREAK statement
   - CONTINUE statement
   - LOOP counter variable

3. **String Operations**
   - STRING SPLIT, JOIN, REPLACE
   - Regular expressions
   - String formatting

4. **Error Handling**
   - TRY/CATCH blocks
   - Custom error messages
   - Error recovery strategies

5. **Advanced Functions**
   - Default parameters
   - Variable arguments (*args)
   - Lambda functions
   - Closures

6. **Performance Optimizations**
   - Bytecode compilation
   - JIT compilation for hot paths
   - Parallel execution
   - Lazy evaluation

7. **Debugging Tools**
   - Step-through debugger
   - Breakpoints
   - Variable inspection
   - Call stack traces

## Migration from v1.x

See [uPY Migration Guide](uPY-Migration-Guide.md) for detailed migration instructions.

**Key Changes:**
- Commands use `(COMMAND|params)` instead of Python syntax
- Variables use `{$var}` instead of `{var}`
- Functions use `@name(args)` instead of `name(args)`
- List literals use `[item1, item2]` instead of Python lists
- Conditionals use `IF/ELSE IF/ELSE` instead of Python if/elif/else

## Conclusion

The uPY v2.0.2 runtime provides a robust, performant, and type-safe execution environment for `.upy` scripts. Its pattern-based interpretation model enables clean syntax, fast execution, and excellent error messages while maintaining full integration with the uDOS ecosystem.

**Key Strengths:**
- ✅ No transpilation overhead
- ✅ Type-safe operations
- ✅ Clear error messages
- ✅ Full uDOS integration
- ✅ Extensive test coverage
- ✅ Production-ready performance

---

**Version:** 2.0.2
**Last Updated:** December 5, 2025
**Maintainer:** @fredporter
**License:** MIT
