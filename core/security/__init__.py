"""
uDOS Security System - Core Module

Provides role-based access control, command-based I/O security,
and audit logging for v1.1.0 stable release.

Author: uDOS Development Team
Version: v1.1.0
Date: November 17, 2025
"""

__version__ = "1.1.0"
__all__ = [
    "Role",
    "UserRole",
    "PermissionManager",
    "SecurityContext",
    "CommandIOSecurity",
    "AuditLogger",
    "RateLimiter",
    "InstallationType"
]

# Re-export core security components
try:
    from .roles import Role, UserRole
    from .permissions import PermissionManager
    from .context import SecurityContext
    from .command_io import CommandIOSecurity
    from .audit import AuditLogger
    from .rate_limiter import RateLimiter
    from .installation import InstallationType
except ImportError:
    # Modules not yet implemented - will be added in Phase 1-3
    pass
