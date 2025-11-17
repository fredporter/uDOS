"""
Role-Based Access Control (RBAC) System for uDOS v1.1.0

Defines user roles with hierarchical permissions:
- USER: Standard operations
- POWER: Extended capabilities
- WIZARD: Developer access
- ROOT: Emergency access only

Author: uDOS Development Team
Date: November 17, 2025
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Set, Optional
from datetime import datetime


class Role(Enum):
    """User role definitions with hierarchy"""
    USER = "user"           # Default role - standard operations
    POWER = "power"         # Advanced user - extended capabilities
    WIZARD = "wizard"       # Developer - full dev access
    ROOT = "root"           # System - emergency access only

    def __lt__(self, other):
        """Enable role hierarchy comparison"""
        if not isinstance(other, Role):
            return NotImplemented
        hierarchy = {
            Role.USER: 0,
            Role.POWER: 1,
            Role.WIZARD: 2,
            Role.ROOT: 3
        }
        return hierarchy[self] < hierarchy[other]

    def __le__(self, other):
        return self < other or self == other

    def __gt__(self, other):
        if not isinstance(other, Role):
            return NotImplemented
        return not self <= other

    def __ge__(self, other):
        return not self < other

    @property
    def description(self) -> str:
        """Get role description"""
        descriptions = {
            Role.USER: "Standard uDOS operations",
            Role.POWER: "Extended capabilities for advanced users",
            Role.WIZARD: "Full development access (VSCode/Copilot)",
            Role.ROOT: "Emergency system access only"
        }
        return descriptions[self]


@dataclass
class RolePermissions:
    """Permissions granted to a specific role"""
    role: Role

    # Command permissions
    allowed_commands: Set[str] = field(default_factory=set)
    denied_commands: Set[str] = field(default_factory=set)

    # File system permissions
    read_paths: Set[str] = field(default_factory=set)
    write_paths: Set[str] = field(default_factory=set)
    execute_paths: Set[str] = field(default_factory=set)

    # API/Web access
    api_enabled: bool = False
    web_enabled: bool = False
    api_rate_limit: int = 0          # Requests per day (0 = unlimited)
    web_rate_limit: int = 0          # Requests per hour (0 = unlimited)
    api_cost_limit: float = 0.0      # USD per month (0 = unlimited)

    # Extension permissions
    install_verified_extensions: bool = False
    install_unverified_extensions: bool = False
    develop_extensions: bool = False

    # Git operations
    git_enabled: bool = False

    # Sandbox access
    sandbox_access: bool = False

    # Debug operations
    debug_enabled: bool = False

    def inherits_from(self, other: 'RolePermissions') -> None:
        """Inherit permissions from another role"""
        # Ensure sets are being used
        if not isinstance(self.allowed_commands, set):
            self.allowed_commands = set(self.allowed_commands)
        if not isinstance(self.read_paths, set):
            self.read_paths = set(self.read_paths)
        if not isinstance(self.write_paths, set):
            self.write_paths = set(self.write_paths)
        if not isinstance(self.execute_paths, set):
            self.execute_paths = set(self.execute_paths)

        # Now perform union
        self.allowed_commands = self.allowed_commands.union(other.allowed_commands)
        self.read_paths = self.read_paths.union(other.read_paths)
        self.write_paths = self.write_paths.union(other.write_paths)
        self.execute_paths = self.execute_paths.union(other.execute_paths)

        # Inherit boolean flags (use OR logic - more permissive)
        self.api_enabled = self.api_enabled or other.api_enabled
        self.web_enabled = self.web_enabled or other.web_enabled
        self.sandbox_access = self.sandbox_access or other.sandbox_access
        self.git_enabled = self.git_enabled or other.git_enabled
        self.debug_enabled = self.debug_enabled or other.debug_enabled

        # Inherit limits (use max - more permissive)
        if other.api_rate_limit > self.api_rate_limit:
            self.api_rate_limit = other.api_rate_limit
        if other.web_rate_limit > self.web_rate_limit:
            self.web_rate_limit = other.web_rate_limit
        if other.api_cost_limit > self.api_cost_limit:
            self.api_cost_limit = other.api_cost_limit


class RoleDefinitions:
    """Centralized role permission definitions"""

    @staticmethod
    def get_user_permissions() -> RolePermissions:
        """Get USER role permissions"""
        return RolePermissions(
            role=Role.USER,
            allowed_commands={
                # Read-only commands
                'HELP', 'STATUS', 'LIST', 'VIEW', 'DOCS', 'LEARN',
                'KNOWLEDGE', 'MAP', 'TILE', 'VIEWPORT', 'PALETTE',
                'GUIDE', 'DIAGRAM', 'HANDBOOK', 'MANUAL', 'EXAMPLE',
                'SHOW', 'GRID', 'LEVEL',
                # Script execution
                'RUN',
                # Private memory
                'MEMORY',
                # System info
                'VERSION', 'CONFIG'
            },
            read_paths={
                'KNOWLEDGE/', 'docs/', 'wiki/', 'examples/',
                'MEMORY/PRIVATE/', 'MEMORY/SHARED/', 'MEMORY/COMMUNITY/',
                'extensions/bundled/'
            },
            write_paths={
                'MEMORY/PRIVATE/'
            },
            execute_paths={
                'scripts/', 'MEMORY/PRIVATE/'
            },
            api_enabled=False,
            web_enabled=False,
            sandbox_access=False,
            git_enabled=False,
            debug_enabled=False
        )

    @staticmethod
    def get_power_permissions() -> RolePermissions:
        """Get POWER role permissions (inherits from USER)"""
        power = RolePermissions(
            role=Role.POWER,
            allowed_commands={
                # Additional commands beyond USER
                'API', 'ASSIST', 'OK',
                'WEB', 'FETCH', 'CRAWL',
                'EDIT', 'SAVE',
                'INSTALL',  # Verified extensions only
                'EXTENSION'
            },
            read_paths={
                # Same as USER
            },
            write_paths={
                'MEMORY/', 'sandbox/'
            },
            execute_paths={
                'sandbox/'
            },
            api_enabled=True,
            web_enabled=True,
            api_rate_limit=100,      # 100 API calls per day
            web_rate_limit=50,       # 50 web requests per hour
            api_cost_limit=5.0,      # $5 USD per month
            install_verified_extensions=True,
            sandbox_access=True
        )

        # Inherit USER permissions
        user = RoleDefinitions.get_user_permissions()
        power.inherits_from(user)

        return power

    @staticmethod
    def get_wizard_permissions() -> RolePermissions:
        """Get WIZARD role permissions (inherits from POWER)"""
        wizard = RolePermissions(
            role=Role.WIZARD,
            allowed_commands={
                # Additional commands beyond POWER
                'GIT', 'CLONE', 'PULL', 'PUSH', 'COMMIT', 'BRANCH',
                'DEBUG', 'BREAK', 'STEP', 'INSPECT', 'WATCH',
                'POKE',
                'PROMPT', 'OFFLINE'
            },
            read_paths={
                'core/', 'extensions/core/'  # Read-only core access
            },
            write_paths={
                # Same as POWER
            },
            execute_paths={
                # Same as POWER
            },
            api_rate_limit=500,      # 500 API calls per day
            web_rate_limit=200,      # 200 web requests per hour
            api_cost_limit=20.0,     # $20 USD per month
            install_unverified_extensions=True,
            develop_extensions=True,
            git_enabled=True,
            debug_enabled=True
        )

        # Inherit POWER permissions
        power = RoleDefinitions.get_power_permissions()
        wizard.inherits_from(power)

        return wizard

    @staticmethod
    def get_root_permissions() -> RolePermissions:
        """Get ROOT role permissions (unrestricted)"""
        return RolePermissions(
            role=Role.ROOT,
            allowed_commands={'*'},   # All commands allowed
            read_paths={'*'},         # All paths readable
            write_paths={'*'},        # All paths writable
            execute_paths={'*'},      # All paths executable
            api_enabled=True,
            web_enabled=True,
            api_rate_limit=0,        # Unlimited
            web_rate_limit=0,        # Unlimited
            api_cost_limit=0.0,      # Unlimited
            install_verified_extensions=True,
            install_unverified_extensions=True,
            develop_extensions=True,
            sandbox_access=True,
            git_enabled=True,
            debug_enabled=True
        )

    @staticmethod
    def get_permissions(role: Role) -> RolePermissions:
        """Get permissions for a specific role"""
        if role == Role.USER:
            return RoleDefinitions.get_user_permissions()
        elif role == Role.POWER:
            return RoleDefinitions.get_power_permissions()
        elif role == Role.WIZARD:
            return RoleDefinitions.get_wizard_permissions()
        elif role == Role.ROOT:
            return RoleDefinitions.get_root_permissions()
        else:
            raise ValueError(f"Unknown role: {role}")


@dataclass
class UserRole:
    """User role with metadata"""
    username: str
    role: Role
    assigned_at: datetime
    assigned_by: Optional[str] = None
    expires_at: Optional[datetime] = None
    session_timeout: int = 3600  # seconds (1 hour default)

    def is_expired(self) -> bool:
        """Check if role assignment has expired"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def get_permissions(self) -> RolePermissions:
        """Get permissions for this user's role"""
        return RoleDefinitions.get_permissions(self.role)

    def can_execute_command(self, command: str) -> bool:
        """Check if user can execute a command"""
        if self.is_expired():
            return False

        perms = self.get_permissions()

        # ROOT can execute anything
        if '*' in perms.allowed_commands:
            return True

        # Check if command is explicitly allowed
        if command.upper() in perms.allowed_commands:
            return True

        # Check if command is explicitly denied
        if command.upper() in perms.denied_commands:
            return False

        return False

    def can_access_path(self, path: str, access_type: str = 'read') -> bool:
        """Check if user can access a file path"""
        if self.is_expired():
            return False

        perms = self.get_permissions()

        # ROOT can access anything
        if '*' in perms.read_paths:
            return True

        # Normalize path
        path = path.strip().rstrip('/')

        # Check appropriate permission set
        if access_type == 'read':
            allowed_paths = perms.read_paths
        elif access_type == 'write':
            allowed_paths = perms.write_paths
        elif access_type == 'execute':
            allowed_paths = perms.execute_paths
        else:
            return False

        # Check if path or any parent directory is in allowed paths
        for allowed in allowed_paths:
            if path.startswith(allowed.rstrip('/')):
                return True

        return False

    def requires_2fa(self) -> bool:
        """Check if this role requires 2FA"""
        return self.role == Role.ROOT

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'username': self.username,
            'role': self.role.value,
            'assigned_at': self.assigned_at.isoformat(),
            'assigned_by': self.assigned_by,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'session_timeout': self.session_timeout
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'UserRole':
        """Create UserRole from dictionary"""
        return cls(
            username=data['username'],
            role=Role(data['role']),
            assigned_at=datetime.fromisoformat(data['assigned_at']),
            assigned_by=data.get('assigned_by'),
            expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None,
            session_timeout=data.get('session_timeout', 3600)
        )


class RoleManager:
    """Manages user role assignments and transitions"""

    def __init__(self):
        self.roles: dict[str, UserRole] = {}
        self.default_role = Role.USER

    def assign_role(self, username: str, role: Role, assigned_by: Optional[str] = None,
                   expires_at: Optional[datetime] = None) -> UserRole:
        """Assign a role to a user"""
        user_role = UserRole(
            username=username,
            role=role,
            assigned_at=datetime.now(),
            assigned_by=assigned_by,
            expires_at=expires_at
        )
        self.roles[username] = user_role
        return user_role

    def get_role(self, username: str) -> UserRole:
        """Get user's current role"""
        if username in self.roles:
            user_role = self.roles[username]
            if not user_role.is_expired():
                return user_role

        # Return default role if no assignment or expired
        return UserRole(
            username=username,
            role=self.default_role,
            assigned_at=datetime.now()
        )

    def elevate_temporarily(self, username: str, target_role: Role,
                          duration_seconds: int = 300) -> UserRole:
        """Temporarily elevate user to higher role (sudo-like)"""
        from datetime import timedelta

        current_role = self.get_role(username)

        # Can't elevate to same or lower role
        if target_role <= current_role.role:
            raise ValueError(f"Cannot elevate from {current_role.role} to {target_role}")

        # Can't elevate to ROOT without proper authentication
        if target_role == Role.ROOT:
            raise PermissionError("ROOT elevation requires 2FA authentication")

        expires_at = datetime.now() + timedelta(seconds=duration_seconds)
        return self.assign_role(username, target_role, assigned_by=username, expires_at=expires_at)

    def revoke_role(self, username: str) -> None:
        """Revoke user's role assignment (revert to default)"""
        if username in self.roles:
            del self.roles[username]

    def list_roles(self) -> List[UserRole]:
        """List all role assignments"""
        return list(self.roles.values())

    def get_role_hierarchy(self) -> List[Role]:
        """Get roles in hierarchical order"""
        return [Role.USER, Role.POWER, Role.WIZARD, Role.ROOT]


# Singleton instance
_role_manager = None

def get_role_manager() -> RoleManager:
    """Get global role manager instance"""
    global _role_manager
    if _role_manager is None:
        _role_manager = RoleManager()
    return _role_manager
