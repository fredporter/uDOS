# RUN Command - uDOS Automation

## Overview
The RUN command executes .uscript files containing sequences of uDOS commands. This enables automation, batch operations, and script-based workflows.

## Basic Usage

```
RUN <script-file>
```

## uCODE Format

```
[FILE|RUN*knowledge/demos/hello-automation.uscript]
```

## Script Format

.uscript files support:
- **uCODE commands**: `[MODULE|COMMAND*PARAM]`
- **Plain text commands**: Converted automatically via parser
- **Comments**: Lines starting with `#`
- **Blank lines**: Ignored automatically

### Example Script

```bash
# hello-automation.uscript
# Basic automation demonstration

# Show system status
[SYSTEM|STATUS]

# Show command history statistics
[SYSTEM|HISTORY*STATS]

# Show map status
[MAP|STATUS]
```

## Command Line Execution

Scripts can also be executed directly from the command line:

```bash
./start_udos.sh knowledge/demos/hello-automation.uscript
```

This runs the script in non-interactive mode and exits when complete.

## Interactive Execution

From within uDOS:

```
uDOS> RUN knowledge/demos/hello-automation.uscript
```

Or use the interactive file picker:

```
uDOS> RUN
▶️  Run script
  > knowledge/demos/hello-automation.uscript
    memory/tests/shakedown.uscript
```

## Implementation Details

### UCodeInterpreter Class

Located in `core/uDOS_ucode.py`:
- Reads .uscript files line by line
- Skips comments and blank lines
- Executes commands through main CommandHandler
- Reports errors but continues execution
- Returns formatted execution summary

### Key Features

1. **Format Auto-Detection**: Handles both uCODE format `[MODULE|COMMAND]` and plain text commands
2. **Error Resilience**: Continues execution after errors unless critical
3. **Context Awareness**: Full access to grid, parser, and all command handlers
4. **Execution Reporting**: Shows line numbers and results for each command

## Architecture

```
FileCommandHandler._handle_run()
   ↓
UCodeInterpreter.execute_script()
   ↓
UCodeInterpreter.execute_line()
   ↓
UCodeInterpreter._execute_ucode()
   ↓
CommandHandler.handle_command()
   ↓
[Specialized handler executes command]
```

## Example Scripts

### System Health Check

```bash
# system-check.uscript
[SYSTEM|STATUS]
[SYSTEM|REPAIR]
[BANK|STATS]
[HISTORY|STATS]
```

### Workspace Setup

```bash
# workspace-setup.uscript
# Configure new workspace

# Clear sandbox
[FILE|WORKSPACE*SWITCH*sandbox]
[FILE|WORKSPACE*CLEAR]

# Show available templates
[ASSIST|GENERATE*project setup script]
```

### Data Analysis

```bash
# analyze-data.uscript
# Analyze data bank and history

[BANK|INDEX]
[BANK|STATS]
[HISTORY|STATS]
[HISTORY|RECENT*20]
```

## Testing

Basic test suite: `memory/tests/test_run_command.py`

```bash
python memory/tests/test_run_command.py
```

Tests standalone execution, comment parsing, and error handling.

## Limitations (v1.0.6)

- No variable support (planned for future)
- No conditional logic (IF/THEN) yet
- No loop constructs
- Sequential execution only (no parallel)
- No script-to-script calling

## Future Enhancements

Planned for later versions:
- Variable assignment and substitution
- Conditional execution (IF/THEN/ELSE)
- Loop constructs (FOR, WHILE)
- Function definitions
- Script composition (calling scripts from scripts)
- Parallel execution for independent commands
- Background process support

## Related Commands

- **GENERATE**: AI-assisted script generation
- **WORKSPACE**: Manage execution contexts
- **HISTORY**: Track script execution
- **READ**: Analyze script output

## Version History

- **v1.0.6**: Initial RUN command implementation
  - Basic script execution
  - Comment and blank line handling
  - Error resilience
  - Integration with command line arguments
