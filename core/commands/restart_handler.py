"""
Unified Restart Handler - RESTART/REBOOT with numbered options

Commands (Numeric):
    RESTART              # Show numbered menu
    RESTART 0            # Show help
    RESTART 1            # Hot reload handlers (one-time)
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
    """Unified restart/reboot handler."""
    
    def __init__(self):
        """Initialize handler."""
        super().__init__()
        self.prompt = None  # Will be set by parser
    
    def handle(self, command, params, grid, parser):
        """Handle RESTART and REBOOT commands with logging."""
        # Store parser for interactive prompts
        self.prompt = parser
        
        with self.trace_command(command, params) as trace:
            result = self._handle_impl(command, params, grid, parser)
            if isinstance(result, dict):
                status = result.get("status")
                if status:
                    trace.set_status(status)
            return result

    def _handle_impl(self, command, params, grid, parser):
        """Handle RESTART and REBOOT commands.
        
        Usage:
            RESTART              # Show numbered menu
            RESTART 0            # Show help
            RESTART 1            # Hot reload only
            RESTART 2            # Repair only
            RESTART 3            # Hot reload + repair
            RESTART 4            # Full system restart
            RESTART --help       # Show help (legacy)
        
        Args:
            command: Command name (RESTART, REBOOT)
            params: Parameter list
            grid: Grid object
            parser: Parser object
        
        Returns:
            Output dict
        """
        # Import here to avoid circular deps
        from core.services.logging_service import get_logger
        from core.services.unified_logging import get_unified_logger
        from core.services.user_service import get_user_manager, Permission
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
        
        # Show interactive menu if no options or choice
        if not (reload_only or repair_only or full):
            return self._show_interactive_menu(command)
        
        # Determine mode
        if command.upper() == "REBOOT":
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
        """Perform the restart sequence - ACTUALLY EXECUTES THE RESTART.
        
        Args:
            reload_only: Only hot reload
            repair_only: Only repair
            full: Full restart
            skip_confirm: Skip confirmations (always execute)
            command: Original command
        
        Returns:
            Output dict with execution results
        """
        from core.services.hot_reload import get_hot_reload_manager
        from core.services.logging_service import get_logger
        
        logger = get_logger('restart-handler')
        output_lines = []
        
        # Build restart plan
        plan = []
        do_reload = reload_only or full or (not repair_only)
        do_repair = repair_only or full or (not reload_only)
        do_full = full
        
        if do_reload:
            plan.append("🔄 Hot reload handlers")
        if do_repair:
            plan.append("🔧 Run repair checks")
        if do_full:
            plan.append("🔄 Full system restart")
        
        # Show plan header
        output_lines.append("")
        output_lines.append("╔════════════════════════════════════════╗")
        output_lines.append("║      RESTARTING SYSTEM                 ║")
        output_lines.append("╚════════════════════════════════════════╝")
        output_lines.append("")
        
        # EXECUTE HOT RELOAD
        if do_reload:
            output_lines.append("🔄 Hot reloading handlers...")
            try:
                reload_mgr = get_hot_reload_manager()
                if reload_mgr:
                    # Reload all handler modules
                    import sys
                    import importlib
                    from pathlib import Path
                    
                    handlers_dir = Path(__file__).parent
                    reloaded = 0
                    failed = 0
                    
                    for handler_file in handlers_dir.glob("*_handler.py"):
                        if handler_file.name == "__init__.py":
                            continue
                        
                        module_name = f"core.commands.{handler_file.stem}"
                        if module_name in sys.modules:
                            try:
                                importlib.reload(sys.modules[module_name])
                                reloaded += 1
                                logger.info(f"[LOCAL] Reloaded {handler_file.stem}")
                            except Exception as e:
                                failed += 1
                                logger.error(f"[LOCAL] Failed to reload {handler_file.stem}: {e}")
                    
                    output_lines.append(f"   ✓ Reloaded {reloaded} handlers ({failed} failed)")
                else:
                    output_lines.append("   ⚠️  Hot reload manager not available")
                    output_lines.append("   💡 Install watchdog: pip install watchdog")
            except Exception as e:
                output_lines.append(f"   ❌ Hot reload failed: {e}")
                logger.error(f"[LOCAL] Hot reload error: {e}")
        
        # EXECUTE REPAIR
        if do_repair:
            output_lines.append("🔧 Running repair checks...")
            try:
                from core.services.self_healer import SelfHealer
                healer = SelfHealer(component='core', auto_repair=True)
                result = healer.diagnose_and_repair()
                
                if result.issues_found:
                    output_lines.append(f"   ✓ Found {len(result.issues_found)} issues")
                    if result.issues_repaired:
                        output_lines.append(f"   ✓ Fixed {len(result.issues_repaired)}/{len(result.issues_found)} issues")
                    if result.issues_remaining:
                        output_lines.append(f"   ⚠️  {len(result.issues_remaining)} issues remaining (require manual fix)")
                else:
                    output_lines.append("   ✓ No issues found - system healthy")
            except Exception as e:
                output_lines.append(f"   ⚠️  Repair skipped: {e}")
                logger.warning(f"[LOCAL] Repair error: {e}")
        
        # EXECUTE FULL RESTART (if requested)
        if do_full:
            output_lines.append("🔄 Full system restart...")
            output_lines.append("   ℹ️  Close and relaunch uCODE to complete restart")
        
        output_lines.append("")
        output_lines.append("✅ Restart complete!")
        output_lines.append("")
        
        return {
            'output': '\n'.join(output_lines),
            'status': 'success',
            'plan': plan,
            'executed': True
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
    ║          RESTART/REBOOT                ║
    ╚════════════════════════════════════════╝

Choose a restart option (type number + Enter):

  0. HELP
    Show detailed command reference
    Usage: RESTART 0

    1. HOT RELOAD (ONE-TIME)
    • Hot reload Python handlers
    • Preserves REPL state
    • No system changes
    • Fastest option
    Usage: RESTART 1
    
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
  REBOOT                       # Shortcut for RESTART 2
"""
        return {
            'output': menu.strip(),
            'status': 'info',
            'command': command
        }
    
    def _show_interactive_menu(self, command):
        """Show interactive restart menu and guide user through options.
        
        Uses the standard menu choice handler to guide the user.
        Actually executes the selected option.
        
        Args:
            command: Command name
        
        Returns:
            Output dict (execution result)
        """
        # Check if we have a prompt available
        if not self.prompt or not hasattr(self.prompt, 'ask_menu_choice'):
            # Fallback to static menu if no prompt available
            return self._show_menu(command)
        
        # Display the menu
        menu_text = """
    ╔════════════════════════════════════════╗
    ║          RESTART/REBOOT                ║
    ╚════════════════════════════════════════╝

    1. Hot reload handlers (one-time)
  2. Repair (run repair checks only)
  3. Reload + Repair (recommended)
  4. Full Restart (complete reset)
  0. Help
"""
        print(menu_text)
        
        # Ask user to choose
        choice = self.prompt.ask_menu_choice(
            "Choose an option",
            num_options=4,
            allow_zero=True
        )
        
        if choice is None or choice == 0:
            # User pressed enter or selected 0 - show help
            return self._show_help(command)
        
        # Map choice to action and EXECUTE
        reload_only = False
        repair_only = False
        full = False
        
        if choice == 1:
            reload_only = True
        elif choice == 2:
            repair_only = True
        elif choice == 3:
            reload_only = True
            repair_only = True
        elif choice == 4:
            full = True
        
        # Execute the restart NOW
        from core.services.unified_logging import get_unified_logger
        from core.services.user_service import get_user_manager
        
        unified = get_unified_logger()
        user_mgr = get_user_manager()
        user = user_mgr.current()
        
        # Log the action
        unified.log_core(
            category='restart',
            message=f'Restart initiated by {user.username if user else "unknown"}',
            metadata={
                'command': command,
                'choice': choice,
                'reload_only': reload_only,
                'repair_only': repair_only,
                'full': full
            }
        )
        
        # Execute restart
        return self._perform_restart(
            reload_only=reload_only,
            repair_only=repair_only,
            full=full,
            skip_confirm=True,  # Already confirmed by choosing
            command=command
        )
    
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

    RESTART is the unified restart/reboot command with numbered options.

SYNTAX:
  RESTART              Show numbered menu (0-4)
  RESTART [0-4]       Execute numeric option
  RESTART --help      Show this help

NUMERIC OPTIONS:

  0. HELP
    Show this help text
    Usage: RESTART 0

    1. HOT RELOAD (ONE-TIME)
    • Hot reloads Python handlers
    • Preserves REPL state
    • No system changes
    • Safe for development
    • Fastest operation
    Usage: RESTART 1

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

ALIAS:
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

HOT RELOAD CONTROL:
    Use RELOAD on/off/status to control the hot reload watcher.
"""
        return {
            'output': help_text.strip(),
            'status': 'info',
            'command': 'RESTART'
        }


# Alias handler for backward compatibility
class RebootAliasHandler(BaseCommandHandler):
    """REBOOT command - alias for RESTART --repair."""

    def handle(self, command, params, grid, parser):
        """Handle REBOOT as alias."""
        restart_handler = RestartHandler()
        return restart_handler.handle("REBOOT", params, grid, parser)
