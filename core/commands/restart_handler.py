"""
Unified Restart Handler - RESTART command combines RELOAD, REBOOT, and system restart

Commands:
    RESTART                    # Full restart (reload + repair + reboot)
    RESTART --reload-only      # Hot reload handlers only
    RESTART --repair           # Run repair checks (no reload)
    RESTART --full             # Full system restart
    RESTART --confirm          # Skip confirmations (use with caution)
    RESTART --help             # Show help

Options:
    --reload-only    Just hot reload handlers (development)
    --repair         Run repair without reboot
    --full           Complete system restart (everything)
    --confirm        Skip confirmation prompts
    --help           Show this help

Examples:
    RESTART                    # Default: hot reload + repair check
    RESTART --reload-only      # Just reload handlers
    RESTART --full --confirm   # Full restart without prompts
    RESTART --repair           # Repair without reload

Aliases:
    RELOAD                     # Equivalent to RESTART --reload-only
    REBOOT                     # Equivalent to RESTART --repair
    RESTART [options]          # Full unified restart

Author: uDOS Engineering
Version: v1.0.0
Date: 2026-01-28
"""

from .base import BaseCommandHandler
import sys
import time
from pathlib import Path


class RestartHandler(BaseCommandHandler):
    """Unified restart/reload/reboot handler."""
    
    def handle(self, command, params, grid, parser):
        """Handle RESTART, RELOAD (alias), REBOOT (alias) commands.
        
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
        
        # Parse parameters
        reload_only = False
        repair_only = False
        full = False
        skip_confirm = False
        show_help = False
        
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
        
        # Handle help
        if show_help:
            return self._show_help(command)
        
        # Determine mode
        if command.upper() == "RELOAD":
            reload_only = True
        elif command.upper() == "REBOOT":
            repair_only = True
        
        # Default mode if no flags
        if not reload_only and not repair_only and not full:
            reload_only = True
            repair_only = True
        
        # Log the action
        unified.log_core(
            category='restart',
            message=f'Restart initiated by {user.username if user else "unknown"}',
            metadata={
                'command': command,
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

RESTART is the unified restart/reload/reboot command. It combines:
  • RELOAD   - Hot reload handlers
  • REBOOT   - Repair and reboot
  • RESTART  - Full restart sequence

SYNTAX:
  RESTART [OPTIONS]

OPTIONS:
  --reload-only    Just hot reload handlers (development)
  --repair         Run repair without reload
  --full           Complete system restart
  --confirm        Skip confirmation prompts
  --help           Show this help

ALIASES:
  RELOAD           = RESTART --reload-only
  REBOOT           = RESTART --repair
  
EXAMPLES:
  RESTART                    # Hot reload + repair (default)
  RESTART --reload-only      # Just reload handlers
  RESTART --full             # Full system restart
  RESTART --confirm          # Auto-proceed without prompts
  RESTART --help             # Show this help

WHAT EACH DOES:

  RELOAD / RESTART --reload-only
    • Hot reloads Python handlers
    • Preserves REPL state
    • No system changes
    • Safe for development

  REBOOT / RESTART --repair
    • Runs system repair checks
    • Fixes broken state
    • May clean old files
    • Requires repair permission

  RESTART --full
    • Everything: reload + repair
    • Complete fresh start
    • Longest operation
    • Requires admin or full permission

PERMISSIONS:
  • RELOAD     - All users
  • REPAIR     - User+ role
  • FULL       - Admin only

STATUS:
  Type 'STATUS' to check system health before restart.
  Type 'LOGS' to view what's happening.
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
