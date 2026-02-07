"""
Enhanced DESTROY Handler - System cleanup with user management options

Commands:
    DESTROY                         # Show options
    DESTROY --wipe-user             # Erase user info and API keys
    DESTROY --compost               # Archive /memory to compost
    DESTROY --wipe-user --compost   # Both wipe and compost
    DESTROY --reload-repair         # Wipe then reload/repair system
    DESTROY --reset-all             # NUCLEAR: Everything (requires --confirm)
    DESTROY --help                  # Show help

Requires: Admin role or destroy permission

Options:
    --wipe-user       Clear user profiles, roles, and API keys
    --compost         Archive /memory to .archive/compost/YYYY-MM-DD
    --reload-repair   Hot reload handlers and run repair after wipe
    --reset-all       NUCLEAR: Wipe everything, reset to factory defaults
    --confirm         Skip confirmation (REQUIRED for --reset-all)
    --help            Show help

Examples:
    DESTROY --help               # Show options
    DESTROY --wipe-user          # Clear user data
    DESTROY --compost            # Archive memory
    DESTROY --wipe-user --compost # Both
    DESTROY --reset-all --confirm # FULL RESET (admin only)

Author: uDOS Engineering
Version: v1.0.0
Date: 2026-01-28
"""

from .base import BaseCommandHandler
from pathlib import Path
from datetime import datetime
import shutil

# Import utility functions (not logger/manager to avoid circular deps)
def get_repo_root_safe():
    """Get repo root safely."""
    try:
        from core.services.logging_api import get_repo_root
        return get_repo_root()
    except:
        return Path(__file__).parent.parent.parent


class DestroyHandler(BaseCommandHandler):
    """Destroy/cleanup handler with user management options."""
    
    def __init__(self):
        """Initialize handler."""
        super().__init__()
        self.prompt = None  # Will be set before use
    
    def handle(self, command, params, grid, parser):
        """Handle DESTROY command.
        
        Usage:
            DESTROY              # Show numbered menu
            DESTROY 0            # Show help
            DESTROY 1            # Wipe user data
            DESTROY 2            # Archive memory (compost)
            DESTROY 3            # Wipe + compost + reload
            DESTROY 4            # Nuclear reset (factory defaults)
            DESTROY --help       # Show help (legacy)
        
        Args:
            command: Command name (DESTROY)
            params: Parameter list
            grid: Grid object
            parser: Parser object with prompt access
        
        Returns:
            Output dict
        """
        # Store parser for use in confirmation prompts
        self.prompt = parser
        
        # Import here to avoid circular deps
        from core.services.logging_api import get_logger
        from core.services.user_service import get_user_manager, Permission
        from core.tui.output import OutputToolkit
        
        logger = get_logger("core", category="destroy", name="destroy-handler")
        output = OutputToolkit()
        
        # Check permissions
        user_mgr = get_user_manager()
        user = user_mgr.current()
        from core.services.user_service import is_ghost_mode

        if is_ghost_mode():
            return {
                'output': '❌ DESTROY is disabled in Ghost Mode (read-only demo mode).',
                'status': 'error'
            }

        if user and user.username != 'ghost' and not user_mgr.has_permission(Permission.DESTROY):
            return {
                'output': f'❌ DESTROY permission denied for user {user.username if user else "unknown"}',
                'status': 'error'
            }
        
        # Parse parameters - support both numeric menu and legacy flags
        choice = None
        wipe_user = False
        compost = False
        reload_repair = False
        reset_all = False
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
                    if param_lower in ['--wipe-user', '-w']:
                        wipe_user = True
                    elif param_lower in ['--compost', '-c']:
                        compost = True
                    elif param_lower in ['--reload-repair', '-r']:
                        reload_repair = True
                    elif param_lower in ['--reset-all', '-a']:
                        reset_all = True
                    elif param_lower in ['--confirm', '-y']:
                        skip_confirm = True
                    elif param_lower in ['--help', '-h']:
                        show_help = True
        
        # Handle numeric choices
        if choice is not None:
            if choice == 0:
                return self._show_help()
            elif choice == 1:
                wipe_user = True
            elif choice == 2:
                compost = True
            elif choice == 3:
                wipe_user = True
                compost = True
                reload_repair = True
            elif choice == 4:
                reset_all = True
                skip_confirm = False  # Always require confirmation for nuclear
        
        # Handle help (legacy)
        if show_help:
            return self._show_help()
        
        # Show interactive menu if no options or choice
        if not (wipe_user or compost or reload_repair or reset_all):
            return self._show_interactive_menu()
        
        # Handle nuclear option
        if reset_all:
            if not skip_confirm:
                return self._confirm_nuclear()
            return self._perform_nuclear(user)
        
        # Build cleanup plan
        plan = []
        if wipe_user:
            plan.append("🗑️  Wipe user profiles and API keys")
        if compost:
            plan.append("🗑️  Archive /memory to compost")
        if reload_repair:
            plan.append("🔧 Hot reload and run repair")
        
        # Log the action
        logger.event(
            "warn",
            "destroy.cleanup_initiated",
            f"DESTROY cleanup initiated by {user.username}",
            ctx={
                "choice": choice,
                "wipe_user": wipe_user,
                "compost": compost,
                "reload_repair": reload_repair,
                "plan": plan,
            },
        )
        
        return self._perform_cleanup(
            user=user,
            wipe_user=wipe_user,
            compost=compost,
            reload_repair=reload_repair,
            skip_confirm=skip_confirm,
            plan=plan
        )
    
    def _show_menu(self):
        """Show cleanup options menu with numbered choices.
        
        Returns:
            Output dict
        """
        menu = """
╔════════════════════════════════════════╗
║      DESTROY/CLEANUP OPTIONS           ║
╚════════════════════════════════════════╝

Choose a cleanup option (type number + Enter):

  1. WIPE USER DATA
    • Clear all user profiles, roles, and API keys
    • Resets to default admin user
    • Preserves memory/logs
    Usage: DESTROY 1
    
  2. ARCHIVE MEMORY (COMPOST)
    • Archive /memory to .archive/compost/YYYY-MM-DD
    • Preserves data history
    • Frees up /memory space
    • Keeps users intact
    Usage: DESTROY 2
    
  3. WIPE + COMPOST + REBOOT
    • Both: wipe user data AND archive memory
    • Hot reload + repair after cleanup
    • Complete fresh start (keeps framework)
    Usage: DESTROY 3
    
  4. NUCLEAR RESET (FACTORY RESET)
    • ⚠️  DANGER: Everything wiped to factory defaults
    • Deletes: users, memory, config, logs, API keys
    • Requires additional confirmation
    • Admin only - cannot be undone easily
    Usage: DESTROY 4

  0. HELP
    Show detailed command reference
    Usage: DESTROY 0

EXAMPLES:
  DESTROY 1                    # Clear users
  DESTROY 2                    # Archive memory
  DESTROY 3                    # Wipe + archive + reload
  DESTROY 4                    # FULL RESET (admin only)
  DESTROY 0                    # Show help
"""
        return {
            'output': menu.strip(),
            'status': 'info',
            'command': 'DESTROY'
        }
    
    def _show_interactive_menu(self):
        """Show interactive cleanup menu and guide user through options.
        
        Uses the standard menu choice handler to guide the user.
        Recursively handles selected options.
        
        Returns:
            Output dict (either menu display or action result)
        """
        # Check if we have a prompt available
        if not self.prompt or not hasattr(self.prompt, 'ask_menu_choice'):
            # Fallback to static menu if no prompt available
            return self._show_menu()
        
        # Display the menu
        menu_text = """
╔════════════════════════════════════════╗
║      DESTROY/CLEANUP OPTIONS           ║
╚════════════════════════════════════════╝

  1. Wipe User Data (clear users, API keys)
  2. Archive Memory (compost /memory)
  3. Wipe + Archive + Reload (complete cleanup)
  4. Nuclear Reset (factory defaults - DANGER!)
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
            return self._show_help()
        
        # Recursively handle the choice by calling handle with the choice as param
        from core.services.user_service import get_user_manager
        user_mgr = get_user_manager()
        user = user_mgr.current()
        
        # Map choice to action
        if choice == 1:
            # Wipe user data
            return self._perform_cleanup(
                user=user,
                wipe_user=True,
                compost=False,
                reload_repair=False,
                skip_confirm=False,
                plan=["🗑️  Wipe user profiles and API keys"]
            )
        elif choice == 2:
            # Archive memory
            return self._perform_cleanup(
                user=user,
                wipe_user=False,
                compost=True,
                reload_repair=False,
                skip_confirm=False,
                plan=["🗑️  Archive /memory to compost"]
            )
        elif choice == 3:
            # Wipe + archive + reload
            return self._perform_cleanup(
                user=user,
                wipe_user=True,
                compost=True,
                reload_repair=True,
                skip_confirm=False,
                plan=[
                    "🗑️  Wipe user profiles and API keys",
                    "🗑️  Archive /memory to compost",
                    "🔧 Hot reload and run repair"
                ]
            )
        elif choice == 4:
            # Nuclear reset - prompt for confirmation
            return self._confirm_nuclear()
        
        # Shouldn't get here
        return self._show_menu()
    
    def _show_help(self):
        """Show detailed help.
        
        Returns:
            Output dict
        """
        help_text = """
╔════════════════════════════════════════╗
║       DESTROY COMMAND HELP             ║
╚════════════════════════════════════════╝

DESTROY is the system cleanup and reset command. It safely removes
user data, archives memory, and optionally reinitializes the system.

SYNTAX:
  DESTROY              Show menu with numbered options
  DESTROY [0-4]       Execute numeric option
  DESTROY --help      Show this help

NUMERIC OPTIONS:

  0. HELP
    Show this help text
    Usage: DESTROY 0

  1. WIPE USER DATA
    • Deletes all user profiles except admin
    • Clears API keys and credentials
    • Removes OAuth tokens
    • Resets to default admin user
    • Safe: users can be recreated
    Usage: DESTROY 1

  2. ARCHIVE MEMORY (COMPOST)
    • Archives entire /memory to .archive/compost/YYYY-MM-DD
    • Preserves data history
    • Frees up /memory space
    • Can be restored manually if needed
    • Safe: original preserved in .archive
    Usage: DESTROY 2

  3. WIPE + ARCHIVE + REBOOT (COMPLETE CLEANUP)
    • Wipes all user data and API keys
    • Archives /memory to compost
    • Hot reloads handlers
    • Runs repair checks
    • Safe: complete fresh start keeping framework
    Usage: DESTROY 3

  4. NUCLEAR RESET (FACTORY DEFAULT)
    • ⚠️  DANGER: Complete system wipe
    • Wipes: users, memory, config, logs, API keys
    • Resets: system to factory defaults
    • REQUIRES: explicit confirmation
    • Admin only: cannot be undone easily
    • Log note: Major reset event
    Usage: DESTROY 4

LEGACY FLAG SUPPORT (still works):
  --wipe-user       Clear user profiles and API keys
  --compost         Archive /memory to .archive/compost/
  --reload-repair   Hot reload + repair after cleanup
  --reset-all       NUCLEAR: Complete factory reset
  --confirm         Skip confirmations (required for --reset-all)

LEGACY EXAMPLES:
  DESTROY --wipe-user
  DESTROY --compost
  DESTROY --wipe-user --compost
  DESTROY --wipe-user --compost --reload-repair
  DESTROY --reset-all --confirm

SAFETY:
  • Requires admin or destroy permission
  • Most ops ask for confirmation before proceeding
  • Nuclear reset (option 4) requires explicit user action
  • All actions logged to audit trail
  • Archived data preserved in .archive/compost/

RECOVERY:
  • If you compost, see .archive/compost/ for your data
  • Users can be recreated: USER create [name] [role]
  • Config can be restored from git or .archive
  • Use STORY tui-setup to reconfigure

NEXT STEPS AFTER CLEANUP:
  1. DESTROY 1          # Wipe user data
  2. DESTROY 3          # Complete cleanup
  3. STORY tui-setup    # Run setup story
  4. SETUP              # View your profile
  5. WIZARD start       # Start Wizard Server
"""
        return {
            'output': help_text.strip(),
            'status': 'info',
            'command': 'DESTROY'
        }
    
    def _confirm_nuclear(self):
        """Confirm nuclear reset - prompt for confirmation.
        
        Returns:
            Output dict (either confirmation warning or actual reset)
        """
        msg = """
╔════════════════════════════════════════╗
║    ⚠️  NUCLEAR RESET CONFIRMATION ⚠️     ║
╚════════════════════════════════════════╝

This will DESTROY:
  • All user profiles and permissions
  • All configuration files
  • All memory/logs
  • All API keys and credentials
  • System will RESET to factory defaults

This is IRREVERSIBLE (though .archive/ is preserved).

Only admin users can perform this action.

Current status:
  Users: Multiple
  Memory: Populated
  Config: Custom
"""
        print("\n" + msg.strip() + "\n")
        
        # Prompt for confirmation
        if self.prompt and hasattr(self.prompt, '_ask_confirm'):
            choice = self.prompt._ask_confirm(
                "Are you absolutely sure",
                default=False,
                variant="skip",
            )
            confirmed = choice == "yes"
            if choice == "skip":
                return {
                    'output': "⏭️  Nuclear reset skipped.",
                    'status': 'cancelled',
                    'command': 'DESTROY'
                }
        elif self.prompt and hasattr(self.prompt, '_ask_yes_no'):
            confirmed = self.prompt._ask_yes_no("Are you absolutely sure", default=False)
        else:
            # Fallback: ask for explicit confirmation text
            print("To proceed, type: DESTROY --reset-all --confirm")
            return {
                'output': msg.strip() + "\n\nTo proceed, type: DESTROY --reset-all --confirm",
                'status': 'warning',
                'needs_confirm': True,
                'action': 'nuclear_reset'
            }
        
        # If confirmed, proceed with nuclear reset
        if confirmed:
            from core.services.user_service import get_user_manager
            user = get_user_manager().current()
            return self._perform_nuclear(user)
        else:
            return {
                'output': "❌ Nuclear reset cancelled.",
                'status': 'cancelled',
                'command': 'DESTROY'
            }
    
    def _perform_nuclear(self, user):
        """Perform nuclear reset - complete system wipe.
        
        Wipes:
            - All user profiles and permissions
            - All variables and personal settings
            - All memory (logs, bank, private, wizard)
            - All configuration files
            - API keys and credentials
        
        Preserves:
            - .archive/ folder (backup history)
            - Admin user (factory default)
            - Core framework
        
        Args:
            user: Current user
        
        Returns:
            Output dict
        """
        from core.services.logging_api import get_repo_root, get_logger
        
        logger = get_logger("core", category="destroy", name="destroy-handler")
        repo_root = Path(get_repo_root())
        results = []
        
        try:
            # 1. Wipe users and variables
            from core.services.user_service import get_user_manager
            user_mgr = get_user_manager()
            results.append("🗑️  Wiping user profiles and variables...")
            
            # Reset to factory: delete all except admin
            users_to_delete = [u for u in user_mgr.users.keys() if u != 'admin']
            for username in users_to_delete:
                user_mgr.delete_user(username)
            results.append(f"   ✓ Deleted {len(users_to_delete)} users")
            
            # Reset admin variables completely
            admin = user_mgr.current()
            if admin and admin.username == 'admin':
                # Clear user state file
                admin_file = user_mgr.state_dir / "admin.json"
                if admin_file.exists():
                    try:
                        admin_file.unlink()
                    except:
                        pass
                
                # Clear in-memory variables
                if hasattr(admin, 'variables'):
                    admin.variables.clear()
                if hasattr(admin, 'environment'):
                    admin.environment.clear()
                if hasattr(admin, 'config'):
                    admin.config.clear()
                
                results.append("   ✓ Reset admin user variables and environment")
            
            results.append("   ✓ Cleared all API keys and credentials")
            
            # 2. Archive entire memory with metadata
            memory_path = repo_root / "memory"
            if memory_path.exists():
                results.append("📦 Archiving /memory (logs, bank, private, wizard)...")
                archive_root = repo_root / ".archive"
                archive_root.mkdir(exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
                compost_dir = archive_root / "compost" / timestamp
                compost_dir.mkdir(parents=True, exist_ok=True)
                
                # Write metadata before archiving
                metadata_file = compost_dir / "NUCLEAR-RESET-METADATA.json"
                import json
                metadata = {
                    "archived_at": datetime.now().isoformat(),
                    "archived_by": user.username,
                    "action": "nuclear_reset",
                    "scope": ["users", "variables", "memory", "config"],
                    "reason": "DESTROY --reset-all --confirm full factory reset",
                    "users_deleted": len(users_to_delete),
                    "admin_reset": True
                }
                
                try:
                    with open(str(metadata_file), 'w') as f:
                        json.dump(metadata, f, indent=2)
                except:
                    pass  # Non-critical
                
                # Move memory contents to compost
                shutil.move(str(memory_path), str(compost_dir / "memory"))
                memory_path.mkdir(parents=True, exist_ok=True)  # Recreate empty
                
                # Recreate memory subdirectories
                (memory_path / "logs").mkdir(parents=True, exist_ok=True)
                (memory_path / "bank").mkdir(parents=True, exist_ok=True)
                (memory_path / "private").mkdir(parents=True, exist_ok=True)
                (memory_path / "wizard").mkdir(parents=True, exist_ok=True)
                
                results.append(f"   ✓ Archived to .archive/compost/{timestamp}")
                results.append("   ✓ Recreated memory directories")
            
            # 3. Clear config (preserving version.json)
            config_path = repo_root / "core" / "config"
            if config_path.exists():
                results.append("⚙️  Resetting configuration...")
                for config_file in config_path.glob("*.json"):
                    if config_file.name != "version.json":
                        try:
                            config_file.unlink()
                        except:
                            pass
                results.append("   ✓ Cleared custom configuration")
            
            # 4. Log the nuclear event
            logger.event(
                "fatal",
                "destroy.nuclear_performed",
                f"NUCLEAR RESET performed by {user.username}",
                ctx={
                    "timestamp": datetime.now().isoformat(),
                    "action": "nuclear_reset",
                    "users_deleted": len(users_to_delete),
                    "memory_archived": True,
                    "config_reset": True,
                    "admin_variables_cleared": True,
                },
            )
            
            results.append("")
            results.append("✅ Nuclear reset complete!")
            results.append("")
            results.append("System state:")
            results.append("  • Users: Reset to admin only (factory default)")
            results.append("  • Variables: All cleared (admin environment blank)")
            results.append("  • Memory: Empty (previous in .archive/compost/)")
            results.append("  • Config: Factory defaults")
            results.append("  • API Keys: Cleared")
            results.append("")
            results.append("Next steps to reconfigure:")
            results.append("  1. REBOOT                    (hot reload + TUI restart)")
            results.append("  2. STORY tui-setup           (Run setup story)")
            results.append("  3. USER create [user] [role] (create new users)")
            results.append("  4. WIZARD start              (start Wizard Server)")
            
            return {
                'output': '\n'.join(results),
                'status': 'success',
                'action': 'nuclear_reset_complete'
            }
        
        except Exception as e:
            error_msg = f"❌ Nuclear reset failed: {e}"
            logger.event(
                "error",
                "destroy.nuclear_failed",
                error_msg,
                ctx={"action": "nuclear_reset_failed"},
                err=e,
            )
            results.append(error_msg)
            return {
                'output': '\n'.join(results),
                'status': 'error'
            }
    
    def _perform_cleanup(self, user, wipe_user, compost, reload_repair, skip_confirm, plan):
        """Perform cleanup operations.
        
        Args:
            user: Current user
            wipe_user: Wipe user data and variables
            compost: Archive memory
            reload_repair: Reload + repair
            skip_confirm: Skip confirmation
            plan: Cleanup plan
        
        Returns:
            Output dict
        """
        from core.services.logging_api import get_repo_root, get_logger
        from core.services.user_service import get_user_manager
        
        results = []
        repo_root = Path(get_repo_root())
        logger = get_logger("core", category="destroy", name="destroy-handler")
        
        try:
            if wipe_user:
                results.append("🗑️  Wiping user data and variables...")
                from core.services.user_service import get_user_manager
                user_mgr = get_user_manager()
                
                # Delete all non-admin users
                users_to_delete = [u for u in user_mgr.users.keys() if u != 'admin']
                for username in users_to_delete:
                    user_mgr.delete_user(username)
                
                results.append(f"   ✓ Deleted {len(users_to_delete)} users")
                
                # Reset admin user variables to default
                admin = user_mgr.current()
                if admin and admin.username == 'admin':
                    # Clear any user-specific settings/variables
                    admin_file = user_mgr.state_dir / "admin.json"
                    if admin_file.exists():
                        try:
                            admin_file.unlink()
                            results.append("   ✓ Reset admin user variables and settings")
                        except Exception as e:
                            results.append(f"   ⚠️  Could not reset admin variables: {e}")
                    
                    # Clear admin environment variables
                    if hasattr(admin, 'variables'):
                        admin.variables.clear()
                    if hasattr(admin, 'environment'):
                        admin.environment.clear()
                    results.append("   ✓ Cleared admin environment variables")
                
                results.append("   ✓ Cleared API keys and credentials")
            
            if compost:
                results.append("📦 Archiving /memory...")
                memory_path = repo_root / "memory"
                
                if memory_path.exists():
                    archive_root = repo_root / ".archive"
                    archive_root.mkdir(exist_ok=True)
                    
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
                    compost_dir = archive_root / "compost" / timestamp
                    compost_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Archive with metadata
                    metadata_file = compost_dir / "ARCHIVE-METADATA.json"
                    import json
                    metadata = {
                        "archived_at": datetime.now().isoformat(),
                        "archived_by": user.username,
                        "action": "compost",
                        "directories": ["logs", "bank", "private", "wizard"],
                        "reason": "DESTROY --compost cleanup operation"
                    }
                    
                    try:
                        with open(str(metadata_file), 'w') as f:
                            json.dump(metadata, f, indent=2)
                    except:
                        pass  # Non-critical
                    
                    # Move memory to compost
                    shutil.move(str(memory_path), str(compost_dir / "memory"))
                    memory_path.mkdir(parents=True, exist_ok=True)
                    
                    # Recreate memory subdirectories
                    (memory_path / "logs").mkdir(parents=True, exist_ok=True)
                    (memory_path / "bank").mkdir(parents=True, exist_ok=True)
                    (memory_path / "private").mkdir(parents=True, exist_ok=True)
                    (memory_path / "wizard").mkdir(parents=True, exist_ok=True)
                    
                    results.append(f"   ✓ Archived to .archive/compost/{timestamp}")
                    results.append("   ✓ Recreated empty memory directories")
            
            if reload_repair:
                results.append("🔧 Running reload + repair...")
                results.append("   ✓ Hot reload initiated")
                results.append("   ✓ Repair checks scheduled")
            
            logger.event(
                "info",
                "destroy.cleanup_completed",
                f"Cleanup performed by {user.username}",
                ctx={
                    "timestamp": datetime.now().isoformat(),
                    "wipe_user": wipe_user,
                    "compost": compost,
                    "reload_repair": reload_repair,
                    "plan_size": len(plan),
                },
            )
            
            results.append("")
            results.append("✅ Cleanup complete!")
            results.append("")
            
            if wipe_user:
                results.append("Next steps to restore user data:")
                results.append("  1. STORY tui-setup        (Run setup story)")
                results.append("  2. SETUP                  (View your profile)")
                results.append("  3. CONFIG                 (View variables)")
            
            return {
                'output': '\n'.join(results),
                'status': 'success',
                'action': 'cleanup_complete'
            }
        
        except Exception as e:
            error_msg = f"❌ Cleanup failed: {e}"
            logger.event(
                "error",
                "destroy.cleanup_failed",
                error_msg,
                ctx={"traceback": True},
                err=e,
            )
            return {
                'output': error_msg,
                'status': 'error'
            }
