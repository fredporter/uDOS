"""
USER Handler - User profile and permission management

Commands:
    USER                        # Show current user
    USER list                   # List all users
    USER create [name] [role]   # Create new user
    USER delete [name]          # Delete user
    USER switch [name]          # Switch to user
    USER role [name] [role]     # Change user role
    USER perms [name]           # Show user permissions
    USER current                # Show current user details
    USER help                   # Show help

User Roles:
    admin  - Full access (all permissions)
    user   - Normal access (most features)
    guest  - Read-only access

Examples:
    USER                        # Show current user
    USER list                   # List all users
    USER create alice user      # Create alice with user role
    USER switch alice           # Switch to alice
    USER role alice admin       # Promote alice to admin
    USER perms alice            # Show alice's permissions
    USER delete alice           # Delete alice
    USER help                   # Show help

Author: uDOS Engineering
Version: v1.0.0
Date: 2026-01-28
"""

from .base import BaseCommandHandler
from datetime import datetime


class UserHandler(BaseCommandHandler):
    """User profile and permission management."""
    
    def handle(self, command, params, grid, parser):
        """Handle USER command.
        
        Args:
            command: Command name (USER)
            params: Parameter list [subcommand, ...]
            grid: Grid object
            parser: Parser object
        
        Returns:
            Output dict
        """
        from core.services.user_service import get_user_manager
        # No params: show current user
        if not params:
            return self._show_current_user()
        
        subcommand = params[0].lower()
        subparams = params[1:] if len(params) > 1 else []
        
        # Route to subcommand
        if subcommand == "list":
            return self._list_users()
        elif subcommand == "create":
            return self._create_user(subparams)
        elif subcommand == "delete":
            return self._delete_user(subparams)
        elif subcommand == "switch":
            return self._switch_user(subparams)
        elif subcommand == "role":
            return self._set_role(subparams)
        elif subcommand == "perms":
            return self._show_perms(subparams)
        elif subcommand == "current":
            return self._show_current_user()
        elif subcommand in ["help", "-h", "--help", "?"]:
            return self._show_help()
        else:
            return {
                'output': f'Unknown subcommand: {subcommand}\nType: USER help',
                'status': 'error'
            }
    
    def _show_current_user(self):
        """Show current user info.
        
        Returns:
            Output dict
        """
        from core.services.user_service import get_user_manager
        from core.tui.output import OutputToolkit
        
        user_mgr = get_user_manager()
        user = user_mgr.current()
        
        if not user:
            return {
                'output': '❌ No current user',
                'status': 'error'
            }
        
        # Get permissions
        perms = user_mgr.ROLE_PERMISSIONS.get(user.role, [])
        perm_names = [p.value for p in perms]
        
        output_text = f"""
╔════════════════════════════════════════╗
║      CURRENT USER                      ║
╚════════════════════════════════════════╝

User:       {user.username}
Role:       {user.role.value}
Created:    {user.created}
Last Login: {user.last_login or 'Never'}

Permissions ({len(perm_names)}):
"""
        for perm in perm_names[:8]:  # Show first 8
            output_text += f"  • {perm}\n"
        
        if len(perm_names) > 8:
            output_text += f"  ... and {len(perm_names) - 8} more\n"
        
        output_text += """
Commands:
  USER list              - List all users
  USER switch [name]     - Switch to another user
  USER perms             - Show all permissions
  USER help              - Show detailed help
"""
        return {
            'output': output_text.strip(),
            'status': 'info',
            'user': user.username
        }
    
    def _list_users(self):
        """List all users.
        
        Returns:
            Output dict
        """
        from core.services.user_service import get_user_manager
        
        user_mgr = get_user_manager()
        users = user_mgr.list_users()
        current = user_mgr.current()
        
        output_text = """
╔════════════════════════════════════════╗
║      USER LIST                         ║
╚════════════════════════════════════════╝

"""
        for user_data in users:
            marker = "→ " if user_data["username"] == current.username else "  "
            output_text += f"{marker}{user_data['username']:15} {user_data['role']:8} ({user_data['created'][:10]})\n"
        
        output_text += f"""
Total: {len(users)} users

Commands:
  USER create [name] [role]  - Create new user
  USER delete [name]         - Delete user
  USER switch [name]         - Switch to user
  USER role [name] [role]    - Change role
  USER perms [name]          - Show permissions
"""
        return {
            'output': output_text.strip(),
            'status': 'info',
            'user_count': len(users)
        }
    
    def _create_user(self, params):
        """Create new user.
        
        Args:
            params: [username, role]
        
        Returns:
            Output dict
        """
        if len(params) < 1:
            return {
                'output': 'Syntax: USER create [name] [role]\nRole defaults to "user"',
                'status': 'error'
            }
        
        username = params[0]
        role_str = params[1].lower() if len(params) > 1 else "user"
        
        # Validate role
        try:
            role = UserRole(role_str)
        except ValueError:
            return {
                'output': f'Invalid role: {role_str}\nValid roles: admin, user, guest',
                'status': 'error'
            }
        
        # Check permissions
        user_mgr = get_user_manager()
        if not user_mgr.has_permission(Permission.ADMIN):
            return {
                'output': '❌ Only admin users can create other users',
                'status': 'error'
            }
        
        success, msg = user_mgr.create_user(username, role)
        
        if success:
            unified.log_core(
                category='users',
                message=f'User {username} created with role {role.value}',
                metadata={'username': username, 'role': role.value}
            )
            return {
                'output': f'✅ {msg}',
                'status': 'success',
                'user': username
            }
        else:
            return {
                'output': f'❌ {msg}',
                'status': 'error'
            }
    
    def _delete_user(self, params):
        """Delete user.
        
        Args:
            params: [username]
        
        Returns:
            Output dict
        """
        if not params:
            return {
                'output': 'Syntax: USER delete [name]',
                'status': 'error'
            }
        
        username = params[0]
        
        # Check permissions
        user_mgr = get_user_manager()
        if not user_mgr.has_permission(Permission.ADMIN):
            return {
                'output': '❌ Only admin users can delete other users',
                'status': 'error'
            }
        
        success, msg = user_mgr.delete_user(username)
        
        if success:
            unified.log_core(
                category='users',
                message=f'User {username} deleted',
                metadata={'username': username}
            )
            return {
                'output': f'✅ {msg}',
                'status': 'success'
            }
        else:
            return {
                'output': f'❌ {msg}',
                'status': 'error'
            }
    
    def _switch_user(self, params):
        """Switch to user.
        
        Args:
            params: [username]
        
        Returns:
            Output dict
        """
        if not params:
            return {
                'output': 'Syntax: USER switch [name]',
                'status': 'error'
            }
        
        username = params[0]
        user_mgr = get_user_manager()
        
        success, msg = user_mgr.switch_user(username)
        
        if success:
            unified.log_core(
                category='users',
                message=f'Switched to user {username}',
                metadata={'username': username}
            )
            return {
                'output': f'✅ {msg}',
                'status': 'success',
                'user': username
            }
        else:
            return {
                'output': f'❌ {msg}',
                'status': 'error'
            }
    
    def _set_role(self, params):
        """Set user role.
        
        Args:
            params: [username, role]
        
        Returns:
            Output dict
        """
        if len(params) < 2:
            return {
                'output': 'Syntax: USER role [name] [role]\nRoles: admin, user, guest',
                'status': 'error'
            }
        
        username = params[0]
        role_str = params[1].lower()
        
        # Validate role
        try:
            role = UserRole(role_str)
        except ValueError:
            return {
                'output': f'Invalid role: {role_str}\nValid roles: admin, user, guest',
                'status': 'error'
            }
        
        # Check permissions
        user_mgr = get_user_manager()
        if not user_mgr.has_permission(Permission.ADMIN):
            return {
                'output': '❌ Only admin users can change roles',
                'status': 'error'
            }
        
        success, msg = user_mgr.set_role(username, role)
        
        if success:
            unified.log_core(
                category='users',
                message=f'User {username} role set to {role.value}',
                metadata={'username': username, 'role': role.value}
            )
            return {
                'output': f'✅ {msg}',
                'status': 'success'
            }
        else:
            return {
                'output': f'❌ {msg}',
                'status': 'error'
            }
    
    def _show_perms(self, params):
        """Show user permissions.
        
        Args:
            params: [username] or empty for current user
        
        Returns:
            Output dict
        """
        user_mgr = get_user_manager()
        
        if params:
            username = params[0]
            perms = user_mgr.get_user_perms(username)
            title = f"Permissions for {username}"
        else:
            user = user_mgr.current()
            username = user.username
            perms = user_mgr.get_user_perms(username)
            title = f"Permissions for {username} (current)"
        
        output_text = f"""
╔════════════════════════════════════════╗
║      {title:38} ║
╚════════════════════════════════════════╝

"""
        if not perms:
            output_text += "No permissions\n"
        else:
            # Group permissions
            system_perms = [p for p in perms if any(x in p for x in ['admin', 'repair', 'config', 'destroy'])]
            data_perms = [p for p in perms if any(x in p for x in ['read', 'write', 'delete'])]
            dev_perms = [p for p in perms if any(x in p for x in ['dev_mode', 'hot_reload', 'debug'])]
            network_perms = [p for p in perms if any(x in p for x in ['wizard', 'plugin', 'web'])]
            
            if system_perms:
                output_text += "System:\n"
                for p in system_perms:
                    output_text += f"  • {p}\n"
            
            if data_perms:
                output_text += "Data:\n"
                for p in data_perms:
                    output_text += f"  • {p}\n"
            
            if dev_perms:
                output_text += "Development:\n"
                for p in dev_perms:
                    output_text += f"  • {p}\n"
            
            if network_perms:
                output_text += "Network:\n"
                for p in network_perms:
                    output_text += f"  • {p}\n"
        
        output_text += f"""
Total: {len(perms)} permissions

Commands:
  USER role [name] [role]    - Change role
  USER list                  - List all users
  USER help                  - Show help
"""
        return {
            'output': output_text.strip(),
            'status': 'info'
        }
    
    def _show_help(self):
        """Show help.
        
        Returns:
            Output dict
        """
        help_text = """
╔════════════════════════════════════════╗
║        USER COMMAND HELP               ║
╚════════════════════════════════════════╝

USER manages user profiles, roles, and permissions in uDOS.

SYNTAX:
  USER [subcommand] [params]

SUBCOMMANDS:

  USER (no params)
    Show current user and permissions

  USER list
    List all users with their roles

  USER create [name] [role]
    Create new user
    Roles: admin | user | guest
    Example: USER create alice user

  USER delete [name]
    Delete a user
    Example: USER delete alice

  USER switch [name]
    Switch to another user
    Example: USER switch alice

  USER role [name] [role]
    Change user role
    Example: USER role alice admin

  USER perms [name]
    Show user permissions
    Example: USER perms alice

  USER current
    Show current user details

  USER help
    Show this help

ROLES:

  admin
    • Full system access
    • Can create/delete users
    • Can change roles
    • Can REPAIR, DESTROY, REBOOT
    • Can access DEV MODE
    • Default: factory admin user

  user
    • Normal access
    • Read/write files
    • Can use REBOOT
    • Can create plugins
    • Cannot modify system config
    • Cannot create/delete users

  guest
    • Read-only access
    • Can view logs
    • Can view status
    • Cannot modify anything

EXAMPLES:
  # Show current user
  USER

  # List all users
  USER list

  # Create new user
  USER create developer user
  USER create admin2 admin

  # Switch to another user
  USER switch developer

  # Promote user to admin
  USER role developer admin

  # Show developer's permissions
  USER perms developer

  # Delete a user
  USER delete guest1

PERMISSIONS:
  Users inherit permissions based on their role.

  Admin permissions:
    admin, repair, config, destroy, read, write, delete,
    dev_mode, hot_reload, debug, wizard, plugin, web

  User permissions:
    read, write, delete, hot_reload, wizard, plugin

  Guest permissions:
    read

SECURITY:
  • All user operations logged
  • Only admin can create/delete users
  • Only admin can change roles
  • Admin user cannot be deleted
  • Switch requires user to exist
  • Roles enforce permissions automatically
"""
        return {
            'output': help_text.strip(),
            'status': 'info'
        }
