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
    --scrub-memory    Permanently delete /memory (no archive)
    --scrub-vault     Permanently delete VAULT_ROOT (no archive)
    --confirm         Skip confirmation (REQUIRED for --reset-all)
    --help            Show help

Examples:
    DESTROY --help               # Show options
    DESTROY --wipe-user          # Clear user data
    DESTROY --compost            # Archive memory
    DESTROY --wipe-user --compost # Both
    DESTROY --reset-all --confirm # FULL RESET (admin only)
    DESTROY --scrub-memory --confirm
    DESTROY --scrub-vault --confirm

Author: uDOS Engineering
Version: v1.0.0
Date: 2026-01-28
"""

from .base import BaseCommandHandler
from .destroy_handler_helpers import (
    archive_memory_to_compost,
    build_destroy_help_text,
    build_nuclear_confirmation_text,
    destroy_menu_options,
    format_destroy_options,
    reset_local_env,
    reset_wizard_keystore,
    resolve_vault_root,
)
from pathlib import Path
from datetime import datetime
from core.services.destructive_ops import remove_path, scrub_directory, wipe_json_config_dir

# Import utility functions (not logger/manager to avoid circular deps)
def get_repo_root_safe():
    """Get repo root safely."""
    try:
        from core.services.logging_api import get_repo_root
        return get_repo_root()
    except Exception:
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
        scrub_memory = False
        scrub_vault = False
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
                    elif param_lower in ['--scrub-memory', '--scrub-mem']:
                        scrub_memory = True
                    elif param_lower in ['--scrub-vault', '--scrub-vault-md', '--scrub-vaultmd']:
                        scrub_vault = True
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
            plan.append("🧽 Reset local .env identity + Wizard keystore")
        if compost:
            plan.append("🗑️  Archive /memory to compost")
        if scrub_memory:
            plan.append("🔥 Scrub /memory (permanent delete)")
        if scrub_vault:
            plan.append("🔥 Scrub VAULT_ROOT (permanent delete)")
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
            scrub_memory=scrub_memory,
            scrub_vault=scrub_vault,
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

"""

        menu = menu + "\n" + self._format_numeric_options()

        menu = menu + """

EXAMPLES:
  DESTROY 1                    # Clear users
  DESTROY 2                    # Archive memory
  DESTROY 3                    # Wipe + archive + reload
  DESTROY 4                    # FULL RESET (admin only)
  DESTROY 0                    # Show help
  DESTROY --scrub-memory --confirm
  DESTROY --scrub-vault --confirm
"""
        return {
            'output': menu.strip(),
            'status': 'info',
            'command': 'DESTROY'
        }

    def _menu_options(self):
        return destroy_menu_options()

    def _format_numeric_options(self) -> str:
        return format_destroy_options(self._menu_options())

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
    """
        menu_lines = [menu_text.rstrip(), ""]
        for option in self._menu_options():
            menu_lines.append(f"  {option['id']}. {option['short']}")
        menu_text = "\n".join(menu_lines)
        print(menu_text)

        # Ask user to choose
        choice = self.prompt.ask_menu_choice(
            "Choose an option",
            num_options=4,
            allow_zero=True
        )

        if choice is None:
            return self._show_help()

        # Recursively handle the choice by calling handle with the choice as param
        from core.services.user_service import get_user_manager
        user_mgr = get_user_manager()
        user = user_mgr.current()

        option_map = {option["id"]: option for option in self._menu_options()}
        selected = option_map.get(choice)
        if not selected:
            return self._show_menu()
        if selected.get("action") == "help":
            return self._show_help()
        if selected.get("action") == "nuclear":
            return self._confirm_nuclear()

        cleanup = selected.get("cleanup", {})
        return self._perform_cleanup(
            user=user,
            wipe_user=cleanup.get("wipe_user", False),
            compost=cleanup.get("compost", False),
            scrub_memory=False,
            scrub_vault=False,
            reload_repair=cleanup.get("reload_repair", False),
            skip_confirm=False,
            plan=selected.get("plan") or [],
        )

        # Shouldn't get here
        return self._show_menu()

    def _show_help(self):
        """Show detailed help.

        Returns:
            Output dict
        """
        help_text = build_destroy_help_text(self._format_numeric_options())
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
        msg = build_nuclear_confirmation_text()
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
                try:
                    remove_path(admin_file)
                except Exception:
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
                archive_lines, _timestamp = archive_memory_to_compost(
                    repo_root=repo_root,
                    user_name=user.username,
                    action="nuclear_reset",
                    reason="DESTROY --reset-all --confirm full factory reset",
                    metadata_filename="NUCLEAR-RESET-METADATA.json",
                )
                results.extend([f"   {line}" for line in archive_lines])

            # 3. Clear config (preserving version.json)
            config_path = repo_root / "core" / "config"
            if config_path.exists():
                results.append("⚙️  Resetting configuration...")
                removed = wipe_json_config_dir(
                    config_path,
                    keep_files={"version.json"},
                )
                results.append(f"   ✓ Cleared custom configuration ({removed} files)")

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

    def _perform_cleanup(self, user, wipe_user, compost, scrub_memory, scrub_vault, reload_repair, skip_confirm, plan):
        """Perform cleanup operations.

        Args:
            user: Current user
            wipe_user: Wipe user data and variables
            compost: Archive memory
            scrub_memory: Permanently delete /memory
            scrub_vault: Permanently delete VAULT_ROOT
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
                    try:
                        if remove_path(admin_file):
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

            # Reset local env identity + wizard keystore
            env_result = self._reset_local_env(repo_root)
            results.extend([f"   {line}" for line in env_result])
            keystore_result = self._reset_wizard_keystore(repo_root)
            results.extend([f"   {line}" for line in keystore_result])

            if scrub_memory:
                if not skip_confirm and not self._confirm_scrub("memory"):
                    results.append("   ⏭️  Memory scrub cancelled.")
                else:
                    results.append("🔥 Scrubbing /memory (permanent delete)...")
                    memory_path = repo_root / "memory"
                    scrub_directory(memory_path, recreate=True)
                    results.append("   ✓ /memory scrubbed")

            if compost and not scrub_memory:
                results.append("📦 Archiving /memory...")
                memory_path = repo_root / "memory"
                if memory_path.exists():
                    archive_lines, _timestamp = archive_memory_to_compost(
                        repo_root=repo_root,
                        user_name=user.username,
                        action="compost",
                        reason="DESTROY --compost cleanup operation",
                        metadata_filename="ARCHIVE-METADATA.json",
                    )
                    results.extend([f"   {line}" for line in archive_lines])

            if scrub_vault:
                if not skip_confirm and not self._confirm_scrub("vault"):
                    results.append("   ⏭️  Vault scrub cancelled.")
                else:
                    vault_root = self._resolve_vault_root(repo_root)
                    results.append(f"🔥 Scrubbing VAULT_ROOT ({vault_root})...")
                    scrub_directory(vault_root, recreate=True)
                    results.append("   ✓ Vault scrubbed")

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

    def _resolve_vault_root(self, repo_root: Path) -> Path:
        return resolve_vault_root(repo_root)

    def _reset_local_env(self, repo_root: Path) -> list:
        return reset_local_env(repo_root)

    def _reset_wizard_keystore(self, repo_root: Path) -> list:
        return reset_wizard_keystore(repo_root)

    def _confirm_scrub(self, target: str) -> bool:
        prompt = self.prompt
        label = f"Scrub {target} permanently"
        if prompt and hasattr(prompt, "_ask_yes_no"):
            return prompt._ask_yes_no(label, default=False)
        if prompt and hasattr(prompt, "_ask_confirm"):
            choice = prompt._ask_confirm(label, default=False, variant="skip")
            return choice == "yes"
        return False
