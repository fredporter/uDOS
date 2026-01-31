"""
User Management Service - Roles, permissions, authentication

Manages user identities, roles (admin/user/guest), and permissions.
Integrates with setup profiles and provides permission checking.

Usage:
    from core.services.user_service import get_user_manager
    
    users = get_user_manager()
    
    # Get current user
    current = users.current()
    
    # Check permission
    if users.has_permission('admin'):
        # Do admin thing
    
    # List all users
    users.list_users()
    
    # Switch user
    users.switch_user('admin')

Author: uDOS Engineering
Version: v1.0.0
Date: 2026-01-28
"""

import json
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class UserRole(Enum):
    """User roles with permission levels."""
    ADMIN = "admin"       # Full access
    USER = "user"         # Normal access
    GUEST = "guest"       # Read-only access


class Permission(Enum):
    """Permission types."""
    # System
    ADMIN = "admin"             # All permissions
    REPAIR = "repair"           # Run repair/maintenance
    CONFIG = "config"           # Modify configuration
    DESTROY = "destroy"         # Wipe/reset system
    
    # Data
    READ = "read"               # Read files/data
    WRITE = "write"             # Write files/data
    DELETE = "delete"           # Delete files/data
    
    # Development
    DEV_MODE = "dev_mode"       # Access dev mode
    HOT_RELOAD = "hot_reload"   # Use hot reload
    DEBUG = "debug"              # Access debug features
    
    # Network
    WIZARD = "wizard"           # Access Wizard features
    PLUGIN = "plugin"           # Install plugins
    WEB = "web"                 # Web access


@dataclass
class User:
    """User profile."""
    username: str
    role: UserRole
    created: str
    last_login: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dict."""
        return {
            "username": self.username,
            "role": self.role.value,
            "created": self.created,
            "last_login": self.last_login
        }


class UserManager:
    """Manages user identities and permissions."""
    
    # Default role permissions
    ROLE_PERMISSIONS = {
        UserRole.ADMIN: [
            Permission.ADMIN,
            Permission.REPAIR,
            Permission.CONFIG,
            Permission.DESTROY,
            Permission.READ,
            Permission.WRITE,
            Permission.DELETE,
            Permission.DEV_MODE,
            Permission.HOT_RELOAD,
            Permission.DEBUG,
            Permission.WIZARD,
            Permission.PLUGIN,
            Permission.WEB,
        ],
        UserRole.USER: [
            Permission.READ,
            Permission.WRITE,
            Permission.DELETE,
            Permission.HOT_RELOAD,
            Permission.WIZARD,
            Permission.PLUGIN,
        ],
        UserRole.GUEST: [
            Permission.READ,
        ]
    }
    
    def __init__(self, state_dir: Optional[Path] = None):
        """Initialize user manager.
        
        Args:
            state_dir: Directory for user state (default: memory/private)
        """
        if state_dir is None:
            from core.services.logging_service import get_repo_root
            state_dir = Path(get_repo_root()) / "memory" / "private"
        
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        self.users_file = self.state_dir / "users.json"
        self.current_user_file = self.state_dir / "current_user.txt"
        
        self.users: Dict[str, User] = {}
        self.current_username: Optional[str] = None
        
        self._load()
        self._ensure_default_user()
    
    def _load(self) -> None:
        """Load users from file."""
        if self.users_file.exists():
            try:
                with open(self.users_file, "r") as f:
                    data = json.load(f)
                    for username, user_dict in data.items():
                        self.users[username] = User(
                            username=user_dict["username"],
                            role=UserRole(user_dict["role"]),
                            created=user_dict["created"],
                            last_login=user_dict.get("last_login")
                        )
            except Exception as e:
                print(f"Error loading users: {e}")
        
        if self.current_user_file.exists():
            try:
                self.current_username = self.current_user_file.read_text().strip()
            except Exception as e:
                print(f"Error loading current user: {e}")
    
    def _save(self) -> None:
        """Save users to file."""
        try:
            with open(self.users_file, "w") as f:
                data = {u.username: u.to_dict() for u in self.users.values()}
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving users: {e}")
    
    def _save_current(self) -> None:
        """Save current user."""
        try:
            if self.current_username:
                self.current_user_file.write_text(self.current_username)
        except Exception as e:
            print(f"Error saving current user: {e}")
    
    def _ensure_default_user(self) -> None:
        """Ensure default ghost user exists when no users present.
        
        When user variables are destroyed/reset, the system defaults to
        ghost mode (demo/test) and prompts the user to run SETUP to exit.
        """
        from datetime import datetime
        
        if not self.users:
            # Create default ghost user for demo/test mode
            ghost = User(
                username="ghost",
                role=UserRole.GUEST,
                created=datetime.now().isoformat()
            )
            self.users["ghost"] = ghost
            self.current_username = "ghost"
            self._save()
            self._save_current()
    
    def current(self) -> Optional[User]:
        """Get current user.
        
        Returns:
            Current User or None
        """
        if self.current_username is None:
            return None
        return self.users.get(self.current_username)
    
    def create_user(self, username: str, role: UserRole = UserRole.USER) -> Tuple[bool, str]:
        """Create new user.
        
        Args:
            username: New username
            role: User role (default: USER)
        
        Returns:
            Tuple of (success, message)
        """
        from datetime import datetime
        from core.services.name_validator import validate_username
        
        # Validate username
        is_valid, error = validate_username(username)
        if not is_valid:
            return False, error
        
        if username in self.users:
            return False, f"User {username} already exists"
        
        user = User(
            username=username,
            role=role,
            created=datetime.now().isoformat()
        )
        self.users[username] = user
        self._save()
        return True, f"Created user {username} with role {role.value}"
    
    def delete_user(self, username: str) -> Tuple[bool, str]:
        """Delete user.
        
        Args:
            username: Username to delete
        
        Returns:
            Tuple of (success, message)
        """
        if username == "admin" and len(self.users) == 1:
            return False, "Cannot delete last admin user"
        
        if username not in self.users:
            return False, f"User {username} not found"
        
        del self.users[username]
        
        if self.current_username == username:
            self.current_username = "admin"
            self._save_current()
        
        self._save()
        return True, f"Deleted user {username}"
    
    def switch_user(self, username: str) -> Tuple[bool, str]:
        """Switch to different user.
        
        Args:
            username: Username to switch to
        
        Returns:
            Tuple of (success, message)
        """
        if username not in self.users:
            return False, f"User {username} not found"
        
        from datetime import datetime
        
        self.current_username = username
        user = self.users[username]
        user.last_login = datetime.now().isoformat()
        
        self._save()
        self._save_current()
        return True, f"Switched to user {username}"
    
    def set_role(self, username: str, role: UserRole) -> Tuple[bool, str]:
        """Set user role.
        
        Args:
            username: Username
            role: New role
        
        Returns:
            Tuple of (success, message)
        """
        if username not in self.users:
            return False, f"User {username} not found"
        
        self.users[username].role = role
        self._save()
        return True, f"Set {username} role to {role.value}"
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if current user has permission.
        
        Args:
            permission: Permission to check
        
        Returns:
            True if user has permission
        """
        user = self.current()
        if user is None:
            return False
        
        perms = self.ROLE_PERMISSIONS.get(user.role, [])
        return permission in perms
    
    def list_users(self) -> List[Dict]:
        """List all users.
        
        Returns:
            List of user dicts
        """
        return [u.to_dict() for u in self.users.values()]
    
    def get_user_perms(self, username: str) -> List[str]:
        """Get permissions for user.
        
        Args:
            username: Username
        
        Returns:
            List of permission names
        """
        if username not in self.users:
            return []
        
        user = self.users[username]
        perms = self.ROLE_PERMISSIONS.get(user.role, [])
        return [p.value for p in perms]


# Global instance
_user_manager: Optional[UserManager] = None


def get_user_manager() -> UserManager:
    """Get global user manager instance."""
    global _user_manager
    if _user_manager is None:
        _user_manager = UserManager()
    return _user_manager
