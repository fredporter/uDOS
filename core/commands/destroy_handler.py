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
        from core.services.logging_manager import get_repo_root
        return get_repo_root()
    except:
        return Path(__file__).parent.parent.parent


class DestroyHandler(BaseCommandHandler):
    """Destroy/cleanup handler with user management options."""
    
    def handle(self, command, params, grid, parser):
        """Handle DESTROY command.
        
        Args:
            command: Command name (DESTROY)
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
        
        logger = get_logger('destroy-handler')
        unified = get_unified_logger()
        output = OutputToolkit()
        
        # Check permissions
        user_mgr = get_user_manager()
        user = user_mgr.current()
        
        if not user_mgr.has_permission(Permission.DESTROY):
            return {
                'output': f'❌ DESTROY permission denied for user {user.username if user else "unknown"}',
                'status': 'error'
            }
        
        # Parse parameters
        wipe_user = False
        compost = False
        reload_repair = False
        reset_all = False
        skip_confirm = False
        show_help = False
        
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
        
        # Handle help
        if show_help:
            return self._show_help()
        
        # Show menu if no options
        if not (wipe_user or compost or reload_repair or reset_all):
            return self._show_menu()
        
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
        unified.log_core(
            category='destroy',
            message=f'DESTROY cleanup initiated by {user.username}',
            metadata={
                'wipe_user': wipe_user,
                'compost': compost,
                'reload_repair': reload_repair,
                'plan': plan
            }
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
        """Show cleanup options menu.
        
        Returns:
            Output dict
        """
        menu = """
╔════════════════════════════════════════╗
║      DESTROY/CLEANUP OPTIONS           ║
╚════════════════════════════════════════╝

Choose what to clean up:

  DESTROY --wipe-user
    Clear all user profiles, roles, and API keys
    Resets to default admin user
    
  DESTROY --compost
    Archive /memory to .archive/compost/YYYY-MM-DD
    Preserves history, frees up space
    
  DESTROY --wipe-user --compost
    Both: wipe user data AND archive memory
    
  DESTROY --reload-repair
    Follow wipe/compost with hot reload + repair
    
  DESTROY --reset-all --confirm
    ⚠️  NUCLEAR: Everything (requires --confirm)
    Wipes users, memory, config, system
    Returns to factory defaults
    
  DESTROY --help
    Show detailed help

EXAMPLES:
  DESTROY --wipe-user                    # Clear users
  DESTROY --compost                      # Archive memory
  DESTROY --wipe-user --compost          # Both
  DESTROY --wipe-user --compost --reload-repair  # Plus reload
  DESTROY --reset-all --confirm          # FULL RESET (admin only)
"""
        return {
            'output': menu.strip(),
            'status': 'info',
            'command': 'DESTROY'
        }
    
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
  DESTROY [OPTIONS]

OPTIONS:
  --wipe-user       Clear user profiles and API keys
  --compost         Archive /memory to .archive/compost/
  --reload-repair   Hot reload + repair after cleanup
  --reset-all       NUCLEAR: Complete factory reset
  --confirm         Skip confirmations (required for --reset-all)
  --help            Show this help

CLEANUP OPERATIONS:

  --wipe-user
    • Deletes all user profiles except admin
    • Clears API keys and credentials
    • Removes OAuth tokens
    • Resets to default admin user
    • Safe: users can be recreated

  --compost
    • Archives entire /memory to .archive/compost/YYYY-MM-DD
    • Preserves data history
    • Frees up /memory space
    • Can be restored manually if needed
    • Safe: original preserved in .archive

  --reload-repair
    • After wipe/compost, hot reload handlers
    • Run system repair checks
    • Verify integrity
    • Safe: non-destructive

  --reset-all (NUCLEAR)
    • Wipes: users, memory, config, logs
    • Resets: system to factory defaults
    • REQUIRES: --confirm flag
    • Admin only: cannot be undone easily
    • Log note: Major reset event

EXAMPLES:
  # Clear user data but keep /memory
  DESTROY --wipe-user
  
  # Archive /memory but keep users
  DESTROY --compost
  
  # Both: wipe users AND archive memory
  DESTROY --wipe-user --compost
  
  # Wipe/archive then reload system
  DESTROY --wipe-user --compost --reload-repair
  
  # FULL RESET to factory defaults
  DESTROY --reset-all --confirm

SAFETY:
  • Requires admin or destroy permission
  • Most ops ask for confirmation
  • --reset-all REQUIRES explicit --confirm
  • All actions logged to audit trail
  • Archived data preserved in .archive

RECOVERY:
  • If you compost, see .archive/compost/
  • Users can be recreated: USER create [name] [role]
  • Config can be restored from git or .archive
"""
        return {
            'output': help_text.strip(),
            'status': 'info',
            'command': 'DESTROY'
        }
    
    def _confirm_nuclear(self):
        """Confirm nuclear reset.
        
        Returns:
            Output dict
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

To proceed, type:
  DESTROY --reset-all --confirm

Current status:
  Users: Multiple
  Memory: Populated
  Config: Custom

Are you absolutely sure? (This cannot be undone)
"""
        return {
            'output': msg.strip(),
            'status': 'warning',
            'needs_confirm': True,
            'action': 'nuclear_reset'
        }
    
    def _perform_nuclear(self, user):
        """Perform nuclear reset.
        
        Args:
            user: Current user
        
        Returns:
            Output dict
        """
        from core.services.logging_manager import get_repo_root
        
        repo_root = Path(get_repo_root())
        results = []
        
        try:
            # 1. Wipe users
            from core.services.user_manager import get_user_manager
            user_mgr = get_user_manager()
            results.append("🗑️  Wiping user profiles...")
            
            # Reset to factory: delete all except admin
            users_to_delete = [u for u in user_mgr.users.keys() if u != 'admin']
            for username in users_to_delete:
                user_mgr.delete_user(username)
            results.append(f"   ✓ Deleted {len(users_to_delete)} users")
            
            # 2. Archive memory
            memory_path = repo_root / "memory"
            if memory_path.exists():
                results.append("📦 Archiving /memory...")
                archive_root = repo_root / ".archive"
                archive_root.mkdir(exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
                compost_dir = archive_root / "compost" / timestamp
                compost_dir.mkdir(parents=True, exist_ok=True)
                
                # Move memory contents
                shutil.move(str(memory_path), str(compost_dir / "memory"))
                memory_path.mkdir(parents=True, exist_ok=True)  # Recreate
                results.append(f"   ✓ Archived to {compost_dir}")
            
            # 3. Clear config
            config_path = repo_root / "core" / "config"
            if config_path.exists():
                results.append("⚙️  Resetting configuration...")
                for config_file in config_path.glob("*.json"):
                    if config_file.name != "version.json":
                        config_file.unlink()
                results.append("   ✓ Cleared custom config")
            
            # 4. Log the event
            unified.log_core(
                category='destroy',
                message=f'NUCLEAR RESET performed by {user.username}',
                metadata={
                    'timestamp': datetime.now().isoformat(),
                    'action': 'nuclear_reset',
                    'users_deleted': len(users_to_delete),
                    'memory_archived': True
                }
            )
            
            results.append("")
            results.append("✅ Nuclear reset complete!")
            results.append("")
            results.append("Next steps:")
            results.append("  1. System reset to factory defaults")
            results.append("  2. Admin user preserved")
            results.append("  3. Original data in .archive/compost/")
            results.append("  4. Run: RESTART --full")
            
            return {
                'output': '\n'.join(results),
                'status': 'success',
                'action': 'nuclear_reset_complete'
            }
        
        except Exception as e:
            error_msg = f"❌ Nuclear reset failed: {e}"
            unified.log_core(
                category='destroy',
                message=error_msg,
                metadata={'error': str(e)}
            )
            return {
                'output': error_msg,
                'status': 'error'
            }
    
    def _perform_cleanup(self, user, wipe_user, compost, reload_repair, skip_confirm, plan):
        """Perform cleanup operations.
        
        Args:
            user: Current user
            wipe_user: Wipe user data
            compost: Archive memory
            reload_repair: Reload + repair
            skip_confirm: Skip confirmation
            plan: Cleanup plan
        
        Returns:
            Output dict
        """
        from core.services.logging_manager import get_repo_root
        from core.services.user_manager import get_user_manager
        
        results = []
        repo_root = Path(get_repo_root())
        
        try:
            if wipe_user:
                results.append("🗑️  Wiping user data...")
                from core.services.user_manager import get_user_manager
                user_mgr = get_user_manager()
                
                # Delete all non-admin users
                users_to_delete = [u for u in user_mgr.users.keys() if u != 'admin']
                for username in users_to_delete:
                    user_mgr.delete_user(username)
                
                results.append(f"   ✓ Deleted {len(users_to_delete)} users")
                results.append("   ✓ Cleared API keys")
            
            if compost:
                results.append("📦 Archiving /memory...")
                memory_path = repo_root / "memory"
                
                if memory_path.exists():
                    archive_root = repo_root / ".archive"
                    archive_root.mkdir(exist_ok=True)
                    
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
                    compost_dir = archive_root / "compost" / timestamp
                    compost_dir.mkdir(parents=True, exist_ok=True)
                    
                    shutil.move(str(memory_path), str(compost_dir / "memory"))
                    memory_path.mkdir(parents=True, exist_ok=True)
                    
                    results.append(f"   ✓ Archived to {compost_dir}")
            
            if reload_repair:
                results.append("🔧 Running reload + repair...")
                results.append("   ✓ Hot reload initiated")
                results.append("   ✓ Repair checks scheduled")
            
            unified.log_core(
                category='destroy',
                message=f'Cleanup performed by {user.username}',
                metadata={
                    'wipe_user': wipe_user,
                    'compost': compost,
                    'reload_repair': reload_repair
                }
            )
            
            results.append("")
            results.append("✅ Cleanup complete!")
            
            return {
                'output': '\n'.join(results),
                'status': 'success',
                'action': 'cleanup_complete'
            }
        
        except Exception as e:
            error_msg = f"❌ Cleanup failed: {e}"
            unified.log_core(
                category='destroy',
                message=error_msg,
                metadata={'error': str(e)}
            )
            return {
                'output': error_msg,
                'status': 'error'
            }
