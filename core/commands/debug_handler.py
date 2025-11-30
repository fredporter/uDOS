"""
Debug Handler for uDOS v1.1.5.1
Extracted from system_handler.py - Phase A3

Handles debugging commands:
- DEBUG: Start/stop debugging sessions
- BREAK/BREAKPOINT: Manage breakpoints
- STEP: Step through code execution
- CONTINUE: Continue execution
- INSPECT: Inspect variables
- WATCH: Watch variables
- STACK: Show call stack
- MODIFY: Modify variables during debugging
- PROFILE: Performance profiling

Author: uDOS Development Team
License: MIT
"""


class DebugHandler:
    """
    Handler for uCODE debugging and profiling commands.

    This handler provides a comprehensive debugging interface for uCODE scripts,
    including breakpoints, stepping, variable inspection, and performance profiling.

    Commands:
        DEBUG: Start/stop debugging sessions, show status
        BREAK/BREAKPOINT: Set, list, clear, enable/disable breakpoints
        STEP: Step over/into/out of code
        CONTINUE: Continue execution until breakpoint
        INSPECT: Inspect variable values
        WATCH: Watch variables for changes
        STACK: Show call stack
        MODIFY: Modify variable values during debugging
        PROFILE: Show performance profiling data

    All methods use lazy loading for dependencies to avoid circular imports.
    """

    def __init__(self, config):
        """
        Initialize the debug handler.

        Args:
            config: Configuration instance
        """
        self.config = config

    def handle(self, command, params, grid, parser):
        """
        Route debug commands to appropriate handlers.

        Args:
            command: Command name (DEBUG, BREAK, STEP, etc.)
            params: Command parameters
            grid: Grid instance
            parser: Parser instance

        Returns:
            Command result or error message
        """
        command_upper = command.upper()

        # Route to appropriate handler
        if command_upper == 'DEBUG':
            return self.handle_debug(params, grid, parser)
        elif command_upper in ['BREAK', 'BREAKPOINT']:
            return self.handle_breakpoint(params, grid, parser)
        elif command_upper == 'STEP':
            return self.handle_step(params, grid, parser)
        elif command_upper == 'CONTINUE':
            return self.handle_continue(params, grid, parser)
        elif command_upper == 'INSPECT':
            return self.handle_inspect(params, grid, parser)
        elif command_upper == 'WATCH':
            return self.handle_watch(params, grid, parser)
        elif command_upper == 'STACK':
            return self.handle_stack(params, grid, parser)
        elif command_upper == 'MODIFY':
            return self.handle_modify(params, grid, parser)
        elif command_upper == 'PROFILE':
            return self.handle_profile(params, grid, parser)
        else:
            return f"❌ Unknown debug command: {command}\n💡 Use HELP DEBUG for available commands"

    # ═══════════════════════════════════════════════════════════════════════════
    # MAIN COMMAND HANDLERS
    # ═══════════════════════════════════════════════════════════════════════════

    def handle_debug(self, params, grid, parser):
        """
        Start debugging session for a uCODE script.

        Usage:
            DEBUG <script_path>          - Start debugging session
            DEBUG STATUS                 - Show debugger status
            DEBUG STOP                   - Stop debugging session

        Args:
            params: Command parameters [script_path or subcommand]
            grid: Grid instance
            parser: Parser instance

        Returns:
            Status message
        """
        if not params:
            return """╔════════════════════════════════════════════════════════════════════════╗
║                        uCODE DEBUGGER v1.0.17                          ║
╠════════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║  USAGE:                                                                ║
║    DEBUG <script>        Start debugging a uCODE script               ║
║    DEBUG STATUS          Show current debugger status                 ║
║    DEBUG STOP            Stop debugging session                       ║
║                                                                        ║
║  DEBUGGING COMMANDS:                                                   ║
║    BREAK <line>          Set breakpoint at line number                ║
║    BREAK LIST            List all breakpoints                         ║
║    BREAK CLEAR <line>    Clear breakpoint at line                     ║
║    BREAK CLEAR ALL       Clear all breakpoints                        ║
║                                                                        ║
║    STEP                  Execute next line (step over)                ║
║    STEP INTO             Step into function call                      ║
║    STEP OUT              Step out of current function                 ║
║    CONTINUE              Continue execution until breakpoint          ║
║                                                                        ║
║    INSPECT <var>         Inspect variable value                       ║
║    INSPECT ALL           Show all variables in current scope          ║
║                                                                        ║
║    WATCH <var>           Add variable to watch list                   ║
║    WATCH LIST            Show all watched variables                   ║
║    WATCH CLEAR <var>     Remove variable from watch list              ║
║    WATCH CLEAR ALL       Clear all watches                            ║
║                                                                        ║
║    STACK                 Show call stack                              ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝"""

        subcommand = params[0].upper()

        if subcommand == 'STATUS':
            return self._show_debug_status(parser)

        elif subcommand == 'STOP':
            return self._stop_debugging(parser)

        else:
            # Start debugging a script
            script_path = ' '.join(params)
            return self._start_debugging(parser, script_path)

    def handle_breakpoint(self, params, grid, parser):
        """
        Manage breakpoints in debugging session.

        Usage:
            BREAK <line>                 - Set breakpoint at line
            BREAK LIST                   - List all breakpoints
            BREAK CLEAR <line>           - Clear specific breakpoint
            BREAK CLEAR ALL              - Clear all breakpoints
            BREAK DISABLE <line>         - Disable breakpoint
            BREAK ENABLE <line>          - Enable breakpoint
            BREAK <line> IF <condition>  - Set conditional breakpoint

        Args:
            params: Command parameters
            grid: Grid instance
            parser: Parser instance

        Returns:
            Status message
        """
        if not hasattr(parser, 'ucode') or not parser.ucode:
            return "❌ uCODE interpreter not available"

        debugger = parser.ucode.debugger

        if not params:
            return """Usage:
  BREAK <line>          Set breakpoint at line number
  BREAK LIST            List all breakpoints
  BREAK CLEAR <line>    Clear breakpoint at line
  BREAK CLEAR ALL       Clear all breakpoints
  BREAK DISABLE <line>  Disable breakpoint
  BREAK ENABLE <line>   Enable breakpoint
  BREAK <line> IF <cond> Set conditional breakpoint"""

        subcommand = params[0].upper()

        if subcommand == 'LIST':
            return self._list_breakpoints(debugger)

        elif subcommand == 'CLEAR':
            return self._clear_breakpoint(debugger, params[1:])

        elif subcommand == 'DISABLE':
            return self._disable_breakpoint(debugger, params[1:])

        elif subcommand == 'ENABLE':
            return self._enable_breakpoint(debugger, params[1:])

        else:
            # Set breakpoint (regular or conditional)
            return self._set_breakpoint(debugger, params)

    def handle_step(self, params, grid, parser):
        """
        Execute next line in debugger.

        Usage:
            STEP                         - Step over (execute next line)
            STEP INTO                    - Step into function call
            STEP OUT                     - Step out of current function

        Args:
            params: Command parameters
            grid: Grid instance
            parser: Parser instance

        Returns:
            Status message
        """
        if not hasattr(parser, 'ucode') or not parser.ucode:
            return "❌ uCODE interpreter not available"

        debugger = parser.ucode.debugger

        if not params:
            # Step over
            debugger.step_over()
            return "➡️  Stepped to next line"

        subcommand = ' '.join(params).upper()

        if subcommand == 'INTO':
            debugger.step_into()
            return "⬇️  Stepped into function"

        elif subcommand == 'OUT':
            debugger.step_out()
            return "⬆️  Stepped out of function"

        else:
            return "❌ Unknown STEP command. Use: STEP, STEP INTO, or STEP OUT"

    def handle_continue(self, params, grid, parser):
        """
        Continue execution until next breakpoint.

        Args:
            params: Command parameters (unused)
            grid: Grid instance
            parser: Parser instance

        Returns:
            Status message
        """
        if not hasattr(parser, 'ucode') or not parser.ucode:
            return "❌ uCODE interpreter not available"

        debugger = parser.ucode.debugger
        debugger.continue_execution()
        return "▶️  Continuing execution..."

    def handle_inspect(self, params, grid, parser):
        """
        Inspect variables during debugging.

        Usage:
            INSPECT <variable>           - Inspect specific variable
            INSPECT ALL                  - Show all variables in scope

        Args:
            params: Command parameters
            grid: Grid instance
            parser: Parser instance

        Returns:
            Variable information
        """
        if not hasattr(parser, 'ucode') or not parser.ucode:
            return "❌ uCODE interpreter not available"

        debugger = parser.ucode.debugger

        if not params:
            return "Usage:\n  INSPECT <variable>    Inspect specific variable\n  INSPECT ALL           Show all variables"

        var_name = ' '.join(params)

        if var_name.upper() == 'ALL':
            return self._inspect_all_variables(debugger)
        else:
            return self._inspect_variable(debugger, var_name)

    def handle_watch(self, params, grid, parser):
        """
        Manage watch expressions in debugger.

        Usage:
            WATCH <variable>             - Add variable to watch list
            WATCH LIST                   - Show all watched variables
            WATCH CLEAR <variable>       - Remove variable from watch list
            WATCH CLEAR ALL              - Clear all watches

        Args:
            params: Command parameters
            grid: Grid instance
            parser: Parser instance

        Returns:
            Status message
        """
        if not hasattr(parser, 'ucode') or not parser.ucode:
            return "❌ uCODE interpreter not available"

        debugger = parser.ucode.debugger

        if not params:
            return """Usage:
  WATCH <variable>      Add variable to watch list
  WATCH LIST            Show all watched variables
  WATCH CLEAR <var>     Remove variable from watch list
  WATCH CLEAR ALL       Clear all watches"""

        subcommand = params[0].upper()

        if subcommand == 'LIST':
            return self._list_watches(debugger)

        elif subcommand == 'CLEAR':
            return self._clear_watch(debugger, params[1:])

        else:
            # Add watch
            var_name = ' '.join(params)
            debugger.add_watch(var_name)
            return f"👁️  Watching: {var_name}"

    def handle_stack(self, params, grid, parser):
        """
        Show call stack during debugging.

        Args:
            params: Command parameters (unused)
            grid: Grid instance
            parser: Parser instance

        Returns:
            Call stack information
        """
        if not hasattr(parser, 'ucode') or not parser.ucode:
            return "❌ uCODE interpreter not available"

        debugger = parser.ucode.debugger
        stack = debugger.get_call_stack()

        if not stack:
            return "ℹ️  Call stack is empty"

        output = "╔════════════════════════════════════════════════════════════════════════╗\n"
        output += "║                          CALL STACK                                    ║\n"
        output += "╠════════════════════════════════════════════════════════════════════════╣\n"

        for i, frame in enumerate(reversed(stack)):
            prefix = "➤ " if i == len(stack) - 1 else "  "
            func_name = frame.get('function', '<main>')
            line = frame.get('line', '?')
            output += f"║  {prefix}#{i} {func_name:<50} (line {line:<4}) ║\n"

        output += "╚════════════════════════════════════════════════════════════════════════╝"
        return output

    def handle_modify(self, params, grid, parser):
        """
        Modify variable value during debugging.

        Usage:
            MODIFY <variable> = <value>     - Set variable to new value

        Args:
            params: Command parameters [variable, '=', value]
            grid: Grid instance
            parser: Parser instance

        Returns:
            Status message
        """
        if not hasattr(parser, 'ucode') or not parser.ucode:
            return "❌ uCODE interpreter not available"

        debugger = parser.ucode.debugger

        if not params or len(params) < 3:
            return """Usage:
  MODIFY <variable> = <value>    Set variable to new value

Examples:
  MODIFY x = 100
  MODIFY name = "test"
  MODIFY active = True"""

        # Parse: variable = value
        var_name = params[0]

        if params[1] != '=':
            return "❌ Usage: MODIFY <variable> = <value>"

        # Join remaining params as value
        value_str = ' '.join(params[2:])

        # Try to evaluate the value
        try:
            # Try Python literal eval for safety
            import ast
            value = ast.literal_eval(value_str)
        except (ValueError, SyntaxError):
            # If that fails, treat as string
            value = value_str

        # Set the variable
        result = debugger.set_variable(var_name, value)
        return result

    def handle_profile(self, params, grid, parser):
        """
        Show performance profiling information.

        Usage:
            PROFILE                         - Show full performance profile
            PROFILE TOP <n>                 - Show top N slowest lines
            PROFILE CLEAR                   - Clear profiling data
            PROFILE AUTO ON/OFF             - Enable/disable auto-profiling

        Args:
            params: Command parameters
            grid: Grid instance
            parser: Parser instance

        Returns:
            Profiling information
        """
        if not hasattr(parser, 'ucode') or not parser.ucode:
            return "❌ uCODE interpreter not available"

        debugger = parser.ucode.debugger

        if not params:
            return self._show_performance_profile(debugger)

        subcommand = params[0].upper()

        if subcommand == 'TOP':
            return self._show_top_slowest_lines(debugger, params[1:])

        elif subcommand == 'CLEAR':
            debugger.line_execution_times.clear()
            debugger.function_call_times.clear()
            return "✅ Profiling data cleared"

        elif subcommand == 'AUTO':
            return self._toggle_auto_profiling(debugger, params[1:])

        else:
            return f"❌ Unknown PROFILE subcommand: {subcommand}"

    # ═══════════════════════════════════════════════════════════════════════════
    # HELPER METHODS - Debug Session Management
    # ═══════════════════════════════════════════════════════════════════════════

    def _show_debug_status(self, parser):
        """Show current debugger status."""
        if not hasattr(parser, 'ucode') or not parser.ucode:
            return "❌ uCODE interpreter not available"

        debugger = parser.ucode.debugger
        status = debugger.get_status()

        # Format values safely
        script = status.get('current_script') or 'None'
        line = status.get('current_line', 0)

        output = "╔════════════════════════════════════════════════════════════════════════╗\n"
        output += "║                        DEBUGGER STATUS                                 ║\n"
        output += "╠════════════════════════════════════════════════════════════════════════╣\n"
        output += f"║  State:       {status['state']:<57} ║\n"
        output += f"║  Script:      {script:<57} ║\n"
        output += f"║  Line:        {line:<57} ║\n"
        output += f"║  Breakpoints: {len(status.get('breakpoints', [])):<57} ║\n"
        output += f"║  Watches:     {len(status.get('watches', [])):<57} ║\n"
        output += "╚════════════════════════════════════════════════════════════════════════╝"

        return output

    def _stop_debugging(self, parser):
        """Stop debugging session."""
        if not hasattr(parser, 'ucode') or not parser.ucode:
            return "❌ uCODE interpreter not available"

        parser.ucode.debugger.stop()
        parser.ucode.debug_mode = False
        return "✅ Debugging session stopped"

    def _start_debugging(self, parser, script_path):
        """Start debugging a script."""
        if not hasattr(parser, 'ucode') or not parser.ucode:
            return "❌ uCODE interpreter not available"

        # Validate script exists
        import os
        if not os.path.isfile(script_path):
            return f"❌ Script not found: {script_path}"

        # Start debugging
        parser.ucode.debug_mode = True
        parser.ucode.debugger.start(script_path)

        return f"🐛 Debugging session started: {script_path}\n💡 Use STEP, CONTINUE, or BREAK commands to control execution"

    # ═══════════════════════════════════════════════════════════════════════════
    # HELPER METHODS - Breakpoint Management
    # ═══════════════════════════════════════════════════════════════════════════

    def _list_breakpoints(self, debugger):
        """List all breakpoints with details."""
        breakpoint_info = debugger.get_all_breakpoint_info()

        if not breakpoint_info:
            return "ℹ️  No breakpoints set"

        output = "╔════════════════════════════════════════════════════════════════════════╗\n"
        output += "║                          BREAKPOINTS                                   ║\n"
        output += "╠════════════════════════════════════════════════════════════════════════╣\n"
        for bp in breakpoint_info:
            line = bp['line']
            hit_count = bp['hit_count']
            condition = bp['condition']
            enabled = debugger.is_breakpoint_enabled(line)
            status = "🔴" if enabled else "⚪"

            if condition:
                output += f"║ {status} Line {line:<4} (hits: {hit_count:<3}) IF {condition:<45} ║\n"
            else:
                output += f"║ {status} Line {line:<4} (hits: {hit_count:<3}){'':<51} ║\n"
        output += "╚════════════════════════════════════════════════════════════════════════╝"
        return output

    def _clear_breakpoint(self, debugger, params):
        """Clear breakpoint(s)."""
        if not params:
            return "❌ Usage: BREAK CLEAR <line> or BREAK CLEAR ALL"

        if params[0].upper() == 'ALL':
            debugger.clear_all_breakpoints()
            return "✅ All breakpoints cleared"

        try:
            line = int(params[0])
            debugger.clear_breakpoint(line)
            return f"✅ Breakpoint cleared at line {line}"
        except ValueError:
            return f"❌ Invalid line number: {params[0]}"

    def _disable_breakpoint(self, debugger, params):
        """Disable a breakpoint."""
        if not params:
            return "❌ Usage: BREAK DISABLE <line>"

        try:
            line = int(params[0])
            debugger.disable_breakpoint(line)
            return f"⚪ Breakpoint disabled at line {line}"
        except ValueError:
            return f"❌ Invalid line number: {params[0]}"

    def _enable_breakpoint(self, debugger, params):
        """Enable a breakpoint."""
        if not params:
            return "❌ Usage: BREAK ENABLE <line>"

        try:
            line = int(params[0])
            debugger.enable_breakpoint(line)
            return f"🔴 Breakpoint enabled at line {line}"
        except ValueError:
            return f"❌ Invalid line number: {params[0]}"

    def _set_breakpoint(self, debugger, params):
        """Set a regular or conditional breakpoint."""
        try:
            line = int(params[0])

            # Check if this is a conditional breakpoint (BREAK <line> IF <condition>)
            if len(params) > 1 and params[1].upper() == 'IF':
                condition = ' '.join(params[2:])
                debugger.set_breakpoint(line, condition)
                return f"🔴 Conditional breakpoint set at line {line}: {condition}"
            else:
                debugger.set_breakpoint(line)
                return f"🔴 Breakpoint set at line {line}"
        except ValueError:
            return f"❌ Invalid line number: {params[0]}"

    # ═══════════════════════════════════════════════════════════════════════════
    # HELPER METHODS - Variable Inspection
    # ═══════════════════════════════════════════════════════════════════════════

    def _inspect_all_variables(self, debugger):
        """Show all variables in current scope."""
        variables = debugger.get_variables()

        if not variables:
            return "ℹ️  No variables in current scope"

        output = "╔════════════════════════════════════════════════════════════════════════╗\n"
        output += "║                          VARIABLES                                     ║\n"
        output += "╠════════════════════════════════════════════════════════════════════════╣\n"
        for name, value in variables.items():
            value_str = str(value)[:50]  # Truncate long values
            output += f"║  {name:<20} = {value_str:<47} ║\n"
        output += "╚════════════════════════════════════════════════════════════════════════╝"
        return output

    def _inspect_variable(self, debugger, var_name):
        """Inspect a specific variable."""
        value = debugger.inspect_variable(var_name)

        if value is None:
            return f"⚠️  Variable '{var_name}' not found in current scope"

        return f"📍 {var_name} = {value}"

    # ═══════════════════════════════════════════════════════════════════════════
    # HELPER METHODS - Watch Management
    # ═══════════════════════════════════════════════════════════════════════════

    def _list_watches(self, debugger):
        """List all watched variables."""
        watches = debugger.get_watches()

        if not watches:
            return "ℹ️  No variables being watched"

        output = "╔════════════════════════════════════════════════════════════════════════╗\n"
        output += "║                          WATCH LIST                                    ║\n"
        output += "╠════════════════════════════════════════════════════════════════════════╣\n"
        for var_name, value in watches.items():
            value_str = str(value)[:50]
            output += f"║  👁️  {var_name:<18} = {value_str:<45} ║\n"
        output += "╚════════════════════════════════════════════════════════════════════════╝"
        return output

    def _clear_watch(self, debugger, params):
        """Clear watch(es)."""
        if not params:
            return "❌ Usage: WATCH CLEAR <variable> or WATCH CLEAR ALL"

        if params[0].upper() == 'ALL':
            debugger.clear_all_watches()
            return "✅ All watches cleared"

        var_name = ' '.join(params)
        debugger.remove_watch(var_name)
        return f"✅ Watch removed: {var_name}"

    # ═══════════════════════════════════════════════════════════════════════════
    # HELPER METHODS - Performance Profiling
    # ═══════════════════════════════════════════════════════════════════════════

    def _show_performance_profile(self, debugger):
        """Show full performance profile."""
        profile = debugger.get_performance_profile()

        if not profile['lines']:
            return "ℹ️  No profiling data available (enable debug mode and run a script)"

        output = "╔════════════════════════════════════════════════════════════════════════╗\n"
        output += "║                      PERFORMANCE PROFILE                               ║\n"
        output += "╠════════════════════════════════════════════════════════════════════════╣\n"
        output += f"║  Total execution time: {profile['total_time']:.4f}s{'':<38} ║\n"
        output += "╠════════════════════════════════════════════════════════════════════════╣\n"
        output += "║  Top 10 Slowest Lines                                                  ║\n"
        output += "╠════════════════════════════════════════════════════════════════════════╣\n"

        for line, data in profile['slowest_lines']:
            exec_count = data['executions']
            total_time = data['total_time']
            avg_time = data['avg_time']
            output += f"║  Line {line:<4}  {exec_count:<4} runs  {total_time:>8.4f}s total  {avg_time:>8.6f}s avg  ║\n"

        output += "╚════════════════════════════════════════════════════════════════════════╝"
        return output

    def _show_top_slowest_lines(self, debugger, params):
        """Show top N slowest lines."""
        n = 10  # default
        if params:
            try:
                n = int(params[0])
            except ValueError:
                return f"❌ Invalid number: {params[0]}"

        profile = debugger.get_performance_profile()

        if not profile['lines']:
            return "ℹ️  No profiling data available"

        output = f"🐢 Top {n} Slowest Lines:\n"
        for i, (line, data) in enumerate(profile['slowest_lines'][:n], 1):
            output += f"  {i}. Line {line}: {data['total_time']:.4f}s ({data['executions']} runs)\n"

        return output

    def _toggle_auto_profiling(self, debugger, params):
        """Enable/disable automatic profiling."""
        if not params:
            return f"ℹ️  Auto-profiling: {'ON' if debugger.auto_profile else 'OFF'}"

        mode = params[0].upper()
        if mode == 'ON':
            debugger.auto_profile = True
            return "✅ Auto-profiling enabled (will track all line executions)"
        elif mode == 'OFF':
            debugger.auto_profile = False
            return "✅ Auto-profiling disabled"
        else:
            return f"❌ Unknown mode: {mode} (use ON or OFF)"
