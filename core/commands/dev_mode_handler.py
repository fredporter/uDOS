"""
DEV MODE Command Handler - Interactive Debugging for uPY Scripts (v1.2.21)

Provides interactive debugging for ALL USERS in their memory/ucode/ scripts:
- ENABLE/DISABLE: Toggle debug mode
- BREAK: Set/remove/list breakpoints
- STEP: Execute one line
- CONTINUE: Resume execution
- INSPECT: View variable values
- STACK: Show call stack
- TRACE: Toggle trace logging
- STATUS: Show debug state

Note: This is for debugging uPY scripts, NOT for core file protection.
See DEV MODE ON for core system file editing (master user only).

Usage:
    DEV ENABLE                         # Enable debugging
    DEV BREAK 10                       # Set breakpoint at line 10
    DEV BREAK 15 "counter > 5"         # Conditional breakpoint
    DEV STEP                           # Execute next line
    DEV CONTINUE                       # Resume until next breakpoint
    DEV INSPECT counter                # Show variable value
    DEV STACK                          # Show call stack
    DEV TRACE ON                       # Enable trace logging
    DEV STATUS                         # Show debug state
    DEV DISABLE                        # Disable debugging
"""

from pathlib import Path
from typing import Optional
from core.services.debug_engine import DebugEngine
from core.services.unified_logger import UnifiedLogger
from core.commands.handler_utils import HandlerUtils


class DevModeHandler:
    """Handler for DEV MODE debugging commands."""

    def __init__(self):
        """Initialize DEV MODE handler with debug engine."""
        self.config = HandlerUtils.get_config()
        self.logger = UnifiedLogger()
        self.debug_engine = DebugEngine(self.logger)
        from core.utils.paths import PATHS
        self.state_file = PATHS.MEMORY_SYSTEM / "debug_state.json"

        # Load saved state if exists
        if self.state_file.exists():
            self.debug_engine.load_state(self.state_file)

    def handle(self, args: list) -> str:
        """
        Route DEV MODE commands to appropriate handlers.

        Args:
            args: Command arguments (e.g., ['MODE', 'ENABLE'] or ['BREAK', '10'])

        Returns:
            Command result message
        """
        if not args:
            return self._show_help()

        # Handle "DEV MODE" prefix
        if args[0].upper() == 'MODE':
            args = args[1:]
            if not args:
                return self._show_help()

        command = args[0].upper()

        # Route to command handlers
        if command in ['ON', 'OFF']:
            # Redirect to environment handler for DEV MODE ON/OFF (core protection)
            return (
                f"💡 For core file editing, use: DEV MODE {command}\n"
                f"   (This enables master user access to core/knowledge/extensions)\n\n"
                f"For uPY script debugging, use:\n"
                f"  DEV ENABLE  - Start debugging your scripts\n"
                f"  DEV BREAK   - Set breakpoints\n"
                f"  DEV STEP    - Step through code"
            )
        elif command == 'ENABLE':
            return self._handle_enable()
        elif command == 'DISABLE':
            return self._handle_disable()
        elif command == 'STATUS':
            return self._handle_status()
        elif command in ['BREAK', 'BREAKPOINT', 'BP']:
            return self._handle_break(args[1:])
        elif command == 'STEP':
            return self._handle_step()
        elif command in ['CONTINUE', 'CONT', 'C']:
            return self._handle_continue()
        elif command in ['INSPECT', 'PRINT', 'P']:
            return self._handle_inspect(args[1:])
        elif command in ['STACK', 'BACKTRACE', 'BT']:
            return self._handle_stack()
        elif command == 'TRACE':
            return self._handle_trace(args[1:])
        elif command == 'WATCH':
            return self._handle_watch(args[1:])
        elif command == 'HELP':
            return self._show_help()
        else:
            return f"❌ Unknown DEV MODE command: {command}\nUse 'DEV HELP' for usage."

    def _handle_enable(self) -> str:
        """Enable debug mode for uPY script debugging."""
        self.debug_engine.enable()
        self._save_state()

        return """✅ uPY Debugger ENABLED

Debug features active for your scripts in memory/ucode/:
  • Breakpoints will pause execution
  • #BREAK directives will be honored
  • Variable inspection available
  • Call stack tracking enabled

Next steps:
  1. Set breakpoints: DEV BREAK <line> [condition]
  2. Run your script: ./start_udos.sh memory/ucode/sandbox/myscript.upy
  3. Use DEV STEP / DEV CONTINUE when paused

Use 'DEV STATUS' to see current state.

Note: This is for debugging YOUR scripts, not for core file editing.
      For core file access, use: DEV MODE ON"""

    def _handle_disable(self) -> str:
        """Disable debug mode."""
        self.debug_engine.disable()
        self._save_state()

        return """✅ uPY Debugger DISABLED

All debugging features deactivated:
  • Breakpoints will be ignored
  • #BREAK directives skipped
  • Trace logging stopped

Breakpoints are preserved and will be active when you re-enable debugging."""

    def _handle_status(self) -> str:
        """Show current debug state."""
        status = self.debug_engine.get_status()

        # Build status display
        lines = []
        lines.append("╔════════════════════════════════════════════════════════════╗")
        lines.append("║ uPY Debugger Status                                        ║")
        lines.append("╠════════════════════════════════════════════════════════════╣")

        # Mode status
        mode = "🟢 ENABLED" if status['enabled'] else "🔴 DISABLED"
        lines.append(f"║ Debug Mode:        {mode:<40} ║")

        # Execution state
        exec_state = "⏸️  PAUSED" if status['paused'] else "▶️  RUNNING"
        if status['step_mode']:
            exec_state = "👣 STEPPING"
        lines.append(f"║ Execution:         {exec_state:<40} ║")

        # Current position
        if status['current_line'] > 0:
            lines.append(f"║ Current Line:      {status['current_line']:<40} ║")
            if status['current_script']:
                script = status['current_script'][:38]
                lines.append(f"║ Current Script:    {script:<40} ║")

        lines.append("╠════════════════════════════════════════════════════════════╣")

        # Breakpoints
        bp_count = status['breakpoints']
        lines.append(f"║ Breakpoints:       {bp_count} set{'':<36} ║")

        if status['breakpoint_list']:
            for bp in status['breakpoint_list'][:5]:  # Show max 5
                line_num = bp['line']
                enabled = "✓" if bp['enabled'] else "✗"
                hits = bp['hit_count']
                cond = f" if {bp['condition'][:20]}" if bp['condition'] else ""
                bp_str = f"  {enabled} Line {line_num} (hits: {hits}){cond}"
                lines.append(f"║ {bp_str:<58} ║")

            if len(status['breakpoint_list']) > 5:
                remaining = len(status['breakpoint_list']) - 5
                lines.append(f"║   ... and {remaining} more{'':<42} ║")

        lines.append("╠════════════════════════════════════════════════════════════╣")

        # Call stack
        stack_depth = status['call_stack_depth']
        lines.append(f"║ Call Stack Depth:  {stack_depth}{'':<39} ║")

        # Watched variables
        watch_count = len(status['watched_variables'])
        if watch_count > 0:
            lines.append(f"║ Watched Variables: {watch_count}{'':<39} ║")
            for var in status['watched_variables'][:3]:
                lines.append(f"║   • {var:<54} ║")

        # Trace logging
        trace = "ON" if status['trace_enabled'] else "OFF"
        lines.append(f"║ Trace Logging:     {trace:<40} ║")

        lines.append("╚════════════════════════════════════════════════════════════╝")

        # Add helpful hints
        if not status['enabled']:
            lines.append("\n💡 Enable debugging: DEV ENABLE")
            lines.append("💡 For core file editing: DEV MODE ON")
        elif bp_count == 0:
            lines.append("\n💡 Set a breakpoint: DEV BREAK <line_number>")

        return "\n".join(lines)

    def _handle_break(self, args: list) -> str:
        """
        Handle breakpoint commands.

        Args:
            args: Subcommand arguments

        Formats:
            DEV BREAK <line>              # Set breakpoint
            DEV BREAK <line> <condition>  # Conditional breakpoint
            DEV BREAK LIST                # List all breakpoints
            DEV BREAK CLEAR               # Clear all breakpoints
            DEV BREAK REMOVE <line>       # Remove specific breakpoint
            DEV BREAK TOGGLE <line>       # Enable/disable breakpoint
        """
        if not args:
            return self._list_breakpoints()

        subcommand = args[0].upper()

        # List breakpoints
        if subcommand in ['LIST', 'LS', 'L']:
            return self._list_breakpoints()

        # Clear all breakpoints
        if subcommand in ['CLEAR', 'CLEARALL']:
            self.debug_engine.clear_all_breakpoints()
            self._save_state()
            return "✅ All breakpoints cleared"

        # Remove specific breakpoint
        if subcommand in ['REMOVE', 'DELETE', 'RM']:
            if len(args) < 2:
                return "❌ Usage: DEV BREAK REMOVE <line>"

            try:
                line = int(args[1])
                if self.debug_engine.remove_breakpoint(line):
                    self._save_state()
                    return f"✅ Breakpoint removed from line {line}"
                else:
                    return f"❌ No breakpoint at line {line}"
            except ValueError:
                return f"❌ Invalid line number: {args[1]}"

        # Toggle breakpoint
        if subcommand in ['TOGGLE', 'T']:
            if len(args) < 2:
                return "❌ Usage: DEV BREAK TOGGLE <line>"

            try:
                line = int(args[1])
                if self.debug_engine.toggle_breakpoint(line):
                    bp = self.debug_engine.breakpoints.get(line)
                    state = "enabled" if bp.enabled else "disabled"
                    self._save_state()
                    return f"✅ Breakpoint at line {line} {state}"
                else:
                    return f"❌ No breakpoint at line {line}"
            except ValueError:
                return f"❌ Invalid line number: {args[1]}"

        # Set breakpoint (default action)
        try:
            line = int(args[0])

            # Check for condition (remaining args)
            condition = None
            if len(args) > 1:
                condition = " ".join(args[1:])

            if self.debug_engine.set_breakpoint(line, condition):
                self._save_state()
                cond_str = f" (condition: {condition})" if condition else ""
                return f"✅ Breakpoint set at line {line}{cond_str}"
            else:
                return f"❌ Failed to set breakpoint at line {line}"
        except ValueError:
            return f"❌ Invalid line number: {args[0]}"

    def _list_breakpoints(self) -> str:
        """List all breakpoints."""
        status = self.debug_engine.get_status()

        if not status['breakpoint_list']:
            return "No breakpoints set.\n\n💡 Set a breakpoint: DEV BREAK <line>"

        lines = []
        lines.append("Breakpoints:")
        lines.append("─" * 60)

        for bp in sorted(status['breakpoint_list'], key=lambda x: x['line']):
            enabled = "✓" if bp['enabled'] else "✗"
            line_num = bp['line']
            hits = bp['hit_count']

            line_str = f"[{enabled}] Line {line_num:>4}  (hit {hits} times)"

            if bp['condition']:
                line_str += f"\n     Condition: {bp['condition']}"

            lines.append(line_str)

        return "\n".join(lines)

    def _handle_step(self) -> str:
        """Execute one line and pause."""
        if not self.debug_engine.enabled:
            return "❌ Debug mode not enabled. Use 'DEV MODE ENABLE' first."

        if not self.debug_engine.paused:
            return "⚠️  Not currently paused. Use this command when execution is paused at a breakpoint."

        self.debug_engine.step()
        return "👣 Stepping to next line..."

    def _handle_continue(self) -> str:
        """Resume execution until next breakpoint."""
        if not self.debug_engine.enabled:
            return "❌ Debug mode not enabled. Use 'DEV MODE ENABLE' first."

        if not self.debug_engine.paused:
            return "⚠️  Not currently paused. Execution will continue normally."

        self.debug_engine.continue_execution()
        return "▶️  Continuing execution until next breakpoint..."

    def _handle_inspect(self, args: list) -> str:
        """
        Inspect variable value.

        Args:
            args: Variable name(s) to inspect

        Returns:
            Variable value(s) or error message
        """
        if not args:
            return "❌ Usage: DEV INSPECT <variable_name>\n\nExample: DEV INSPECT counter"

        if not self.debug_engine.enabled:
            return "❌ Debug mode not enabled. Use 'DEV MODE ENABLE' first."

        if not self.debug_engine.paused:
            return "⚠️  Can only inspect variables when paused at a breakpoint."

        var_name = args[0]
        value = self.debug_engine.inspect_variable(var_name)

        if value is None:
            return f"❌ Variable '{var_name}' not found in current scope"

        # Format value nicely
        if isinstance(value, dict):
            import json
            value_str = json.dumps(value, indent=2)
        elif isinstance(value, list):
            value_str = f"[{', '.join(str(v) for v in value)}]"
        else:
            value_str = str(value)

        return f"{var_name} = {value_str}"

    def _handle_stack(self) -> str:
        """Show call stack."""
        if not self.debug_engine.enabled:
            return "❌ Debug mode not enabled. Use 'DEV MODE ENABLE' first."

        stack = self.debug_engine.get_call_stack()

        if not stack:
            return "Call stack is empty (no execution in progress)"

        lines = []
        lines.append("Call Stack:")
        lines.append("─" * 60)

        for i, frame in enumerate(reversed(stack)):
            depth = len(stack) - i - 1
            script = frame['script']
            line = frame['line']
            func = frame['function']
            var_count = frame['variables_count']

            lines.append(f"#{depth:>2} {func} at {script}:{line}")
            lines.append(f"    ({var_count} variables in scope)")

        return "\n".join(lines)

    def _handle_trace(self, args: list) -> str:
        """
        Toggle trace logging.

        Args:
            args: ['ON'] or ['OFF']
        """
        if not args:
            status = "ON" if self.debug_engine.trace_enabled else "OFF"
            return f"Trace logging is currently: {status}\n\nUsage: DEV TRACE ON|OFF"

        mode = args[0].upper()

        if mode == 'ON':
            self.debug_engine.enable_trace()
            self._save_state()
            return "✅ Trace logging ENABLED\n\nAll line executions will be logged to debug.log"
        elif mode == 'OFF':
            self.debug_engine.disable_trace()
            self._save_state()
            return "✅ Trace logging DISABLED"
        else:
            return f"❌ Invalid option: {mode}\n\nUsage: DEV TRACE ON|OFF"

    def _handle_watch(self, args: list) -> str:
        """
        Manage variable watch list.

        Args:
            args: Subcommand and variable name

        Formats:
            DEV WATCH <var>        # Add variable to watch list
            DEV WATCH LIST         # List watched variables
            DEV WATCH REMOVE <var> # Remove from watch list
            DEV WATCH CLEAR        # Clear all watches
        """
        if not args:
            # Show current watches
            watches = self.debug_engine.watch_vars
            if not watches:
                return "No variables being watched.\n\n💡 Add a watch: DEV WATCH <variable_name>"

            lines = ["Watched Variables:"]
            for var in watches:
                value = self.debug_engine.inspect_variable(var)
                lines.append(f"  • {var} = {value}")

            return "\n".join(lines)

        subcommand = args[0].upper()

        if subcommand == 'LIST':
            return self._handle_watch([])  # Recursive call to show list

        if subcommand == 'CLEAR':
            self.debug_engine.watch_vars.clear()
            self._save_state()
            return "✅ All watches cleared"

        if subcommand in ['REMOVE', 'DELETE', 'RM']:
            if len(args) < 2:
                return "❌ Usage: DEV WATCH REMOVE <variable_name>"

            var_name = args[1]
            self.debug_engine.remove_watch(var_name)
            self._save_state()
            return f"✅ Removed watch: {var_name}"

        # Default: add watch
        var_name = args[0]
        self.debug_engine.add_watch(var_name)
        self._save_state()
        return f"✅ Added watch: {var_name}"

    def _save_state(self):
        """Save debug state to persistent storage."""
        self.debug_engine.save_state(self.state_file)

    def _show_help(self) -> str:
        """Show DEV MODE help."""
        return """DEV MODE - Interactive Debugging for uPY Scripts

COMMANDS:
  DEV MODE ENABLE              Enable debug mode
  DEV MODE DISABLE             Disable debug mode
  DEV MODE STATUS              Show debug state

BREAKPOINTS:
  DEV BREAK <line>             Set breakpoint at line
  DEV BREAK <line> <condition> Set conditional breakpoint
  DEV BREAK LIST               List all breakpoints
  DEV BREAK REMOVE <line>      Remove breakpoint
  DEV BREAK TOGGLE <line>      Enable/disable breakpoint
  DEV BREAK CLEAR              Clear all breakpoints

EXECUTION CONTROL:
  DEV STEP                     Execute one line and pause
  DEV CONTINUE                 Resume until next breakpoint

INSPECTION:
  DEV INSPECT <variable>       Show variable value
  DEV STACK                    Show call stack
  DEV WATCH <variable>         Add variable to watch list
  DEV WATCH LIST               Show watched variables
  DEV WATCH REMOVE <variable>  Remove from watch list

LOGGING:
  DEV TRACE ON                 Enable trace logging
  DEV TRACE OFF                Disable trace logging

EXAMPLES:
  DEV MODE ENABLE              # Start debugging
  DEV BREAK 25                 # Pause at line 25
  DEV BREAK 30 "count > 10"    # Conditional breakpoint
  # Run your script - it will pause at line 25
  DEV INSPECT counter          # View counter value
  DEV STEP                     # Execute next line
  DEV CONTINUE                 # Resume execution

TIPS:
  • Use #BREAK in .upy scripts to pause at that line
  • Breakpoints persist across sessions
  • Trace logging writes to memory/logs/debug.log
  • Watch variables are evaluated at each pause

For more details, see: wiki/DEV-MODE-Guide.md"""


# Convenience function for command routing
def handle_dev_mode(args: list) -> str:
    """
    Handle DEV MODE commands.

    Args:
        args: Command arguments

    Returns:
        Command result message
    """
    handler = DevModeHandler()
    return handler.handle(args)
