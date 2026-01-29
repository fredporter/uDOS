"""
Unified Restart Handler - RESTART/RELOAD/REBOOT with numbered options

Commands (Numeric):
    RESTART              # Show numbered menu
    RESTART 0            # Show help
    RESTART 1            # Hot reload handlers (RELOAD)
    RESTART 2            # Repair checks (REBOOT)
    RESTART 3            # Hot reload + repair (default)
    RESTART 4            # Full system restart
    
Commands (Legacy Flags - still supported):
    RESTART --reload-only      # Hot reload handlers only
    RESTART --repair           # Run repair checks (no reload)
    RESTART --full             # Full system restart
    RESTART --confirm          # Skip confirmations
    RESTART --help             # Show help

Aliases:
    RELOAD                     # Equivalent to RESTART 1
    REBOOT                     # Equivalent to RESTART 2

Author: uDOS Engineering
Version: v2.0.0 (Numeric Options)
Date: 2026-01-30
"""

from .base import BaseCommandHandler
from .handler_logging_mixin import HandlerLoggingMixin
import sys
import time
from pathlib import Path


class RestartHandler(BaseCommandHandler, HandlerLoggingMixin):
    """Unified restart/reload/reboot handler."""
    
    def handle(self, command, params, grid, parser):
        """Handle RESTART, RELOAD (alias), REBOOT (alias) commands with logging.
        """
        with self.trace_command(command, params) as trace:
            result = self._handle_impl(command, params, grid, parser)
            if isinstance(result, dict):
                status = result.get("status")
                if status:
                    trace.set_status(status)
            return result

    def _handle_impl(self, command, params, grid, parser):
        """Handle RESTART, RELOAD (alias), REBOOT (alias) commands.
        
        Usage:
            RESTART              # Show numbered menu
            RESTART 0            # Show help
            RESTART 1            # Hot reload only
            RESTART 2            # Repair only
            RESTART 3            # Hot reload + repair
            RESTART 4            # Full system restart
            RESTART --help       # Show help (legacy)
        
        Args:
            command: Command name (RESTART, RELOAD, REBOOT)
            params: Parameter list
            grid: Grid object
            parser: Parser object
        
        Returns:
            Output dict
        """
        # Import here to avoid circular deps
        from core.services.logging_manager import get_logger
        from core.services.unified_logging import get_unified_logger
        from core.services.user_manager import get_user_manager, Permission
        from core.tui.output import OutputToolkit
        
        logger = get_logger('restart-handler')
        unified = get_unified_logger()
        output = OutputToolkit()
        user_mgr = get_user_manager()
        user = user_mgr.current()
        
        # Parse parameters - support both numeric menu and legacy flags
        choice = None
        reload_only = False
        repair_only = False
        full = False
        skip_confirm = False
        show_help = False
        
        # Parse first parameter for numeric choice or flags
        if params:
            first_param = params[0].lower()
            
            # Check for numeric choice (0-4)
            if first_param in ['0', '1', '2', '3', '4']:
                choice = int(first_param)
            else:
                # Legacy flag support
                for param in params:
                    param_lower = param.lower()
                    if param_lower in ['--reload-only', '-r']:
                        reload_only = True
                    elif param_lower in ['--repair', '-p']:
                        repair_only = True
                    elif param_lower in ['--full', '-f']:
                        full = True
                    elif param_lower in ['--confirm', '-y']:
                        skip_confirm = True
                    elif param_lower in ['--help', '-h']:
                        show_help = True
        
        # Handle numeric choices
        if choice is not None:
            if choice == 0:
                return self._show_help(command)
            elif choice == 1:
                reload_only = True
            elif choice == 2:
                repair_only = True
            elif choice == 3:
                reload_only = True
                repair_only = True
            elif choice == 4:
                full = True
        
        # Handle help (legacy)
        if show_help:
            return self._show_help(command)
        
        # Show menu if no options or choice
        if not (reload_only or repair_only or full):
            return self._show_menu(command)
        
        # Determine mode
        if command.upper() == "RELOAD":
            reload_only = True
        elif command.upper() == "REBOOT":
            repair_only = True
        
        # Log the action
        unified.log_core(
            category='restart',
            message=f'Restart initiated by {user.username if user else "unknown"}',
            metadata={
                'command': command,
                'choice': choice,
                'reload_only': reload_only,
                'repair_only': repair_only,
                'full': full,
                'skip_confirm': skip_confirm
            }
        )
        
        return self._perform_restart(
            reload_only=reload_only,
            repair_only=repair_only,
            full=full,
            skip_confirm=skip_confirm,
            command=command
        )
    
    def _perform_restart(self, reload_only, repair_only, full, skip_confirm, command):
        """Perform the restart sequence.
        
        Args:
            reload_only: Only hot reload
            repair_only: Only repair
            full: Full restart
            skip_confirm: Skip confirmations
            command: Original command
        
        Returns:
            Output dict
        """
        output_lines = []
        
        # Build restart plan
        plan = []
        if reload_only or (not repair_only and not full):
            plan.append("🔄 Hot reload handlers")
        if repair_only or (not reload_only and not full):
            plan.append("🔧 Run repair checks")
        if full:
            plan.append("🔄 Hot reload handlers")
            plan.append("🔧 Run repair checks")
            plan.append("🔄 Full system restart")
        
        if not plan:
            plan = ["🔄 Hot reload handlers", "🔧 Run repair checks"]
        
        # Show plan
        output_lines.append("")
        output_lines.append("╔════════════════════════════════════════╗")
        output_lines.append("║      RESTART PLAN                      ║")
        output_lines.append("╚════════════════════════════════════════╝")
        output_lines.append("")
        
        for i, step in enumerate(plan, 1):
            output_lines.append(f"  {i}. {step}")
        
        output_lines.append("")
        
        # Confirm
        if not skip_confirm:
            output_lines.append("Are you sure? This will:")
            for step in plan:
                output_lines.append(f"  • {step}")
            output_lines.append("")
            output_lines.append("Type YES to proceed, or anything else to cancel.")
            output_lines.append("")
        
        return {
            'output': '\n'.join(output_lines),
            'status': 'info',
            'plan': plan,
            'skip_confirm': skip_confirm,
            'needs_confirm': not skip_confirm
        }
    
    def _show_menu(self, command):
        """Show numbered menu options.
        
        Args:
            command: Command name
        
        Returns:
            Output dict
        """
        menu = f"""
╔════════════════════════════════════════╗
║       RESTART/RELOAD/REBOOT            ║
╚════════════════════════════════════════╝

Choose a restart option (type number + Enter):

  0. HELP
    Show detailed command reference
    Usage: RESTART 0

  1. RELOAD (HOT RELOAD ONLY)
    • Hot reload Python handlers
    • Preserves REPL state
    • No system changes
    • Fastest option
    Usage: RESTART 1 (or RELOAD)
    
  2. REBOOT (REPAIR ONLY)
    • Run system repair checks
    • Fix broken state
    • Clean up old files
    • No handler reload
    Usage: RESTART 2 (or REBOOT)
    
  3. HOT RELOAD + REPAIR (DEFAULT)
    • Hot reload handlers
    • Run repair checks
    • Safe and thorough
    • Recommended default
    Usage: RESTART 3 (or just RESTART)
    
  4. FULL SYSTEM RESTART
    • Everything: reload + repair + restart
    • Complete fresh start
    • Longest operation
    • Requires admin
    Usage: RESTART 4

EXAMPLES:
  RESTART 1                    # Just reload
  RESTART 2                    # Just repair
  RESTART 3                    # Reload + repair (default)
  RESTART 4                    # Full restart
  RELOAD                       # Shortcut for RESTART 1
  REBOOT                       # Shortcut for RESTART 2
"""
        return {
            'output': menu.strip(),
            'status': 'info',
            'command': command
        }
    
    def _show_help(self, command):
        """Show help for restart command.
        
        Args:
            command: Command name
        
        Returns:
            Output dict
        """
        help_text = """
╔════════════════════════════════════════╗
║        RESTART COMMAND HELP            ║
╚════════════════════════════════════════╝

RESTART is the unified restart/reload/reboot command with numbered options.

SYNTAX:
  RESTART              Show numbered menu (0-4)
  RESTART [0-4]       Execute numeric option
  RESTART --help      Show this help

NUMERIC OPTIONS:

  0. HELP
    Show this help text
    Usage: RESTART 0

  1. RELOAD (HOT RELOAD ONLY)
    • Hot reloads Python handlers
    • Preserves REPL state
    • No system changes
    • Safe for development
    • Fastest operation
    Usage: RESTART 1 (or RELOAD)

  2. REBOOT (REPAIR ONLY)
    • Runs system repair checks
    • Fixes broken state
    • May clean old files
    • No handler reload
    • Requires repair permission
    Usage: RESTART 2 (or REBOOT)

  3. HOT RELOAD + REPAIR (DEFAULT)
    • Hot reloads Python handlers
    • Runs system repair checks
    • Safe and thorough
    • Recommended default
    • Most common use case
    Usage: RESTART 3 (or just RESTART)

  4. FULL SYSTEM RESTART
    • Everything: reload + repair + system restart
    • Complete fresh start
    • Longest operation
    • Requires admin role
    • Use when system is stuck
    Usage: RESTART 4

ALIASES:
  RELOAD           = RESTART 1 (hot reload only)
  REBOOT           = RESTART 2 (repair only)

LEGACY FLAG SUPPORT (still works):
  --reload-only    Hot reload handlers only
  --repair         Run repair without reload
  --full           Complete system restart
  --confirm        Skip confirmation prompts

LEGACY EXAMPLES:
  RESTART --reload-only
  RESTART --repair
  RESTART --full --confirm

PERMISSIONS:
  • RELOAD (1)      - All users
  • REPAIR (2)      - User+ role
  • DEFAULT (3)     - User+ role
  • FULL (4)        - Admin only

EXAMPLES:
  RESTART              # Show menu
  RESTART 1            # Just reload handlers
  RESTART 2            # Just repair checks
  RESTART 3            # Reload + repair (safest)
  RESTART 4            # Full system restart
  RELOAD               # Shortcut for RESTART 1
  REBOOT               # Shortcut for RESTART 2

WHAT'S HAPPENING:

  When you choose an option, the system will:
    1. Show a restart plan
    2. Ask for confirmation (unless --confirm used)
    3. Execute the selected operations
    4. Log the action to audit trail
    5. Return to prompt

STATUS:
  Type 'STATUS' to check system health before restart.
  Type 'LOGS' to view restart operations.
  Type 'SHAKEDOWN' to diagnose issues before repair.
"""
        return {
            'output': help_text.strip(),
            'status': 'info',
            'command': 'RESTART'
        }



# Alias handlers for backward compatibility
class ReloadAliasHandler(BaseCommandHandler):
    """RELOAD command - alias for RESTART --reload-only."""
    
    def handle(self, command, params, grid, parser):
        """Handle RELOAD as alias."""
        restart_handler = RestartHandler()
        return restart_handler.handle('RELOAD', params, grid, parser)


class RebootAliasHandler(BaseCommandHandler):
    """REBOOT command - alias for RESTART --repair."""
    
    def handle(self, command, params, grid, parser):
        """Handle REBOOT as alias."""
        restart_handler = RestartHandler()
        return restart_handler.handle('REBOOT', params, grid, parser)
