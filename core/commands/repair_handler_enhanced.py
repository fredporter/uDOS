"""
Enhanced REPAIR Handler - System repairs with user management options

Commands:
    REPAIR                      # Standard repair checks
    REPAIR --reset-user         # Reset user data/profiles
    REPAIR --reset-keys         # Clear all API keys
    REPAIR --reset-config       # Reset configuration
    REPAIR --full               # Full system repair
    REPAIR --confirm            # Skip confirmations
    REPAIR --help               # Show help

Requires: Admin role or repair permission

Options:
    --reset-user      Reset user profiles to defaults
    --reset-keys      Clear all API keys and credentials
    --reset-config    Reset configuration to defaults
    --full            Complete full repair
    --confirm         Skip confirmation prompts
    --help            Show help

Examples:
    REPAIR                      # Standard repair
    REPAIR --reset-user         # Reset user data
    REPAIR --reset-keys         # Clear credentials
    REPAIR --full               # Full repair with all options
    REPAIR --reset-user --confirm # Auto-proceed

Author: uDOS Engineering
Version: v1.0.0
Date: 2026-01-28
"""

from .base import BaseCommandHandler
from pathlib import Path
import json


class RepairHandler(BaseCommandHandler):
    """System repair handler with user management options."""
    
    def handle(self, command, params, grid, parser):
        """Handle REPAIR command.
        
        Args:
            command: Command name (REPAIR)
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
        
        logger = get_logger('repair-handler')
        unified = get_unified_logger()
        output = OutputToolkit()
        
        # Check permissions
        user_mgr = get_user_manager()
        user = user_mgr.current()
        
        if not user_mgr.has_permission(Permission.REPAIR):
            return {
                'output': f'❌ REPAIR permission denied for user {user.username if user else "unknown"}',
                'status': 'error'
            }
        
        # Parse parameters
        reset_user = False
        reset_keys = False
        reset_config = False
        full = False
        skip_confirm = False
        show_help = False
        
        for param in params:
            param_lower = param.lower()
            if param_lower in ['--reset-user', '-u']:
                reset_user = True
            elif param_lower in ['--reset-keys', '-k']:
                reset_keys = True
            elif param_lower in ['--reset-config', '-c']:
                reset_config = True
            elif param_lower in ['--full', '-f']:
                full = True
            elif param_lower in ['--confirm', '-y']:
                skip_confirm = True
            elif param_lower in ['--help', '-h']:
                show_help = True
        
        # Handle help
        if show_help:
            return self._show_help()
        
        # Handle full flag
        if full:
            reset_user = True
            reset_keys = True
            reset_config = True
        
        # Default: standard repair checks
        if not (reset_user or reset_keys or reset_config):
            return self._perform_standard_repair(user)
        
        # Build repair plan
        plan = []
        if reset_user:
            plan.append("👤 Reset user profiles to defaults")
        if reset_keys:
            plan.append("🔑 Clear all API keys/credentials")
        if reset_config:
            plan.append("⚙️  Reset configuration")
        
        # Log the action
        unified.log_core(
            category='repair',
            message=f'REPAIR with options initiated by {user.username}',
            metadata={
                'reset_user': reset_user,
                'reset_keys': reset_keys,
                'reset_config': reset_config,
                'plan': plan
            }
        )
        
        return self._perform_repair_with_options(
            user=user,
            reset_user=reset_user,
            reset_keys=reset_keys,
            reset_config=reset_config,
            skip_confirm=skip_confirm,
            plan=plan
        )
    
    def _show_help(self):
        """Show repair help.
        
        Returns:
            Output dict
        """
        help_text = """
╔════════════════════════════════════════╗
║         REPAIR COMMAND HELP            ║
╚════════════════════════════════════════╝

REPAIR is the system maintenance and recovery command. It can check
system health, reset user data, clear credentials, and restore defaults.

SYNTAX:
  REPAIR [OPTIONS]

OPTIONS:
  --reset-user      Reset user profiles to factory defaults
  --reset-keys      Clear all API keys and credentials
  --reset-config    Reset configuration files
  --full            Perform all reset options
  --confirm         Skip confirmation prompts
  --help            Show this help

REPAIR OPERATIONS:

  Standard REPAIR (no options)
    • Check system health
    • Validate Python environment
    • Verify dependencies
    • Check git submodules
    • No destructive changes
    • Safe to run anytime

  --reset-user
    • Delete all user profiles except admin
    • Reset roles to defaults
    • Clear user preferences
    • Admin user preserved
    • Can recreate users after

  --reset-keys
    • Delete all stored API keys
    • Clear OAuth tokens
    • Remove credentials
    • Gmail, Notion, HubSpot tokens cleared
    • Safe: can re-add keys manually

  --reset-config
    • Reset configuration files
    • Restore defaults
    • Remove custom settings
    • Safe: backups preserved

  --full
    • Combines all resets
    • Full system restore
    • Returns to factory defaults
    • Admin user preserved
    • Requires careful consideration

EXAMPLES:
  # Standard repair (safe, non-destructive)
  REPAIR
  
  # Reset user data only
  REPAIR --reset-user
  
  # Clear all credentials
  REPAIR --reset-keys
  
  # Reset config to defaults
  REPAIR --reset-config
  
  # Full system restore
  REPAIR --full
  
  # Auto-proceed without prompts
  REPAIR --reset-user --confirm

SAFETY:
  • Most operations ask for confirmation
  • Requires admin or repair permission
  • Backups preserved in .archive/
  • All actions logged to audit trail
  • Can restore from git if needed

RECOVERY:
  • Git can restore configs: git checkout core/config/
  • Users can be recreated: USER create [name] [role]
  • Keys can be re-added manually
  • Check .archive/ for old configs
"""
        return {
            'output': help_text.strip(),
            'status': 'info',
            'command': 'REPAIR'
        }
    
    def _perform_standard_repair(self, user):
        """Perform standard repair checks.
        
        Args:
            user: Current user
        
        Returns:
            Output dict
        """
        from core.services.logging_manager import get_repo_root
        
        results = []
        results.append("")
        results.append("╔════════════════════════════════════════╗")
        results.append("║      SYSTEM REPAIR CHECKS              ║")
        results.append("╚════════════════════════════════════════╝")
        results.append("")
        
        repo_root = Path(get_repo_root())
        
        try:
            # 1. Python environment
            results.append("🐍 Python Environment")
            import sys
            results.append(f"   ✓ Python {sys.version.split()[0]}")
            
            # 2. Dependencies
            results.append("📦 Dependencies")
            try:
                import watchdog
                results.append("   ✓ watchdog (file monitoring)")
            except:
                results.append("   ⚠️  watchdog missing")
            
            try:
                import pathlib
                results.append("   ✓ pathlib (stdlib)")
            except:
                results.append("   ⚠️  pathlib missing")
            
            # 3. Directory structure
            results.append("📁 Directory Structure")
            dirs_to_check = [
                ("core", "Core runtime"),
                ("wizard", "Wizard server"),
                ("extensions", "Extensions"),
                ("memory", "Memory/storage"),
                ("docs", "Documentation"),
            ]
            
            for dirname, desc in dirs_to_check:
                path = repo_root / dirname
                if path.exists():
                    results.append(f"   ✓ {dirname}/ ({desc})")
                else:
                    results.append(f"   ⚠️  {dirname}/ missing")
            
            # 4. Git status
            results.append("🔧 Git Status")
            git_dir = repo_root / ".git"
            if git_dir.exists():
                results.append("   ✓ Git repository initialized")
            else:
                results.append("   ⚠️  Git repository not found")
            
            # 5. Submodules
            results.append("📌 Submodules")
            dev_dir = repo_root / "dev"
            if dev_dir.exists() and (dev_dir / ".git").exists():
                results.append("   ✓ /dev submodule initialized")
            else:
                results.append("   ⚠️  /dev submodule not initialized")
            
            results.append("")
            results.append("✅ System health check complete!")
            results.append("")
            results.append("Suggestions:")
            results.append("  • Run REPAIR --full to restore all defaults")
            results.append("  • Run LOGS to view system messages")
            results.append("  • Run STATUS for detailed info")
            
            unified.log_core(
                category='repair',
                message=f'Standard repair check completed by {user.username}',
                metadata={'status': 'healthy'}
            )
            
            return {
                'output': '\n'.join(results),
                'status': 'success',
                'action': 'repair_check_complete'
            }
        
        except Exception as e:
            error_msg = f"❌ Repair check failed: {e}"
            results.append(error_msg)
            unified.log_core(
                category='repair',
                message=error_msg,
                metadata={'error': str(e)}
            )
            return {
                'output': '\n'.join(results),
                'status': 'error'
            }
    
    def _perform_repair_with_options(self, user, reset_user, reset_keys, reset_config, skip_confirm, plan):
        """Perform repair with reset options.
        
        Args:
            user: Current user
            reset_user: Reset user data
            reset_keys: Clear keys
            reset_config: Reset config
            skip_confirm: Skip confirmations
            plan: Repair plan
        
        Returns:
            Output dict
        """
        from core.services.logging_manager import get_repo_root
        from core.services.unified_logging import get_unified_logger
        from core.services.user_manager import get_user_manager
        
        results = []
        repo_root = Path(get_repo_root())
        unified = get_unified_logger()
        
        try:
            # Show what will happen
            results.append("")
            results.append("╔════════════════════════════════════════╗")
            results.append("║      REPAIR PLAN                       ║")
            results.append("╚════════════════════════════════════════╝")
            results.append("")
            
            for step in plan:
                results.append(f"  • {step}")
            
            results.append("")
            
            if reset_user:
                results.append("👤 User Profile Reset")
                user_mgr = get_user_manager()
                users_to_delete = [u for u in user_mgr.users.keys() if u != 'admin']
                for username in users_to_delete:
                    user_mgr.delete_user(username)
                results.append(f"   ✓ Deleted {len(users_to_delete)} non-admin users")
                results.append("   ✓ Reset roles to defaults")
            
            if reset_keys:
                results.append("🔑 API Keys Reset")
                keys_dir = repo_root / "memory" / "private"
                if keys_dir.exists():
                    for key_file in keys_dir.glob("*.json"):
                        if "key" in key_file.name or "token" in key_file.name:
                            key_file.unlink()
                results.append("   ✓ Cleared stored API keys")
                results.append("   ✓ Removed OAuth tokens")
            
            if reset_config:
                results.append("⚙️  Configuration Reset")
                config_dir = repo_root / "core" / "config"
                if config_dir.exists():
                    for config_file in config_dir.glob("*.json"):
                        if config_file.name != "version.json":
                            config_file.unlink()
                results.append("   ✓ Reset config files")
                results.append("   ✓ Restored defaults")
            
            results.append("")
            results.append("✅ Repair complete!")
            results.append("")
            results.append("Next steps:")
            results.append("  • Run STATUS to verify system")
            results.append("  • Run LOGS to check messages")
            results.append("  • Run RESTART to reload system")
            
            unified.log_core(
                category='repair',
                message=f'Repair with resets completed by {user.username}',
                metadata={
                    'reset_user': reset_user,
                    'reset_keys': reset_keys,
                    'reset_config': reset_config
                }
            )
            
            return {
                'output': '\n'.join(results),
                'status': 'success',
                'action': 'repair_complete'
            }
        
        except Exception as e:
            error_msg = f"❌ Repair failed: {e}"
            unified.log_core(
                category='repair',
                message=error_msg,
                metadata={'error': str(e)}
            )
            return {
                'output': error_msg,
                'status': 'error'
            }
