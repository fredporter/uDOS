"""
Vibe User Service

Manages user accounts, roles, permissions, and identity.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from core.services.logging_manager import get_logger
from core.services.persistence_service import get_persistence_service


@dataclass
class User:
    """User representation."""
    id: str
    username: str
    email: str
    role: str  # "admin", "user", "guest"
    created: str
    last_login: Optional[str] = None
    is_active: bool = True


class VibeUserService:
    """Manage user accounts and permissions."""

    _DATA_FILE = "users"

    def __init__(self):
        """Initialize user service."""
        self.logger = get_logger("vibe-user-service")
        self.persistence_service = get_persistence_service()
        self.users: Dict[str, User] = {}
        self._load_users()

    def _load_users(self) -> None:
        """Load users from persistent storage."""
        self.logger.debug("Loading users from persistence...")
        data = self.persistence_service.read_data(self._DATA_FILE)
        if data and "users" in data:
            self.users = {
                user_id: User(**user_data)
                for user_id, user_data in data["users"].items()
            }
            self.logger.info(f"Loaded {len(self.users)} users.")
        else:
            self.logger.warning("No persistent user data found.")

    def _save_users(self) -> None:
        """Save users to persistent storage."""
        self.logger.debug("Saving users to persistence...")
        data = {
            "users": {
                user_id: asdict(user) for user_id, user in self.users.items()
            }
        }
        self.persistence_service.write_data(self._DATA_FILE, data)

    def list_users(self) -> Dict[str, Any]:
        """List all users."""
        users = [asdict(u) for u in self.users.values()]
        return {
            "status": "success",
            "users": users,
            "count": len(users),
        }

    def add_user(
        self,
        username: str,
        email: str,
        role: str = "user",
    ) -> Dict[str, Any]:
        """
        Create a new user account.

        Args:
            username: Username
            email: Email address
            role: User role (admin|user|guest)

        Returns:
            Dict with success status and user ID
        """
        if username in self.users:
            return {
                "status": "error",
                "message": f"User already exists: {username}",
            }

        user_id = username
        now = datetime.now().isoformat()

        user = User(
            id=user_id,
            username=username,
            email=email,
            role=role,
            created=now
        )

        self.users[user_id] = user
        self._save_users()
        self.logger.info(f"Created user: {username}")

        return {
            "status": "success",
            "message": f"User created: {username}",
            "user": asdict(user),
        }

    def remove_user(self, username: str) -> Dict[str, Any]:
        """
        Delete a user account.

        Args:
            username: Username to delete

        Returns:
            Dict with success status
        """
        if username not in self.users:
            return {
                "status": "error",
                "message": f"User not found: {username}",
            }

        del self.users[username]
        self._save_users()
        self.logger.info(f"Removed user: {username}")

        return {
            "status": "success",
            "message": f"User removed: {username}",
        }

    def update_user(
        self,
        username: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Update user profile.

        Args:
            username: Username
            **kwargs: Fields to update (email, role, is_active)

        Returns:
            Dict with success status and updated user
        """
        if username not in self.users:
            return {
                "status": "error",
                "message": f"User not found: {username}",
            }

        user = self.users[username]

        if "email" in kwargs:
            user.email = kwargs["email"]
        if "role" in kwargs:
            user.role = kwargs["role"]
        if "is_active" in kwargs:
            user.is_active = kwargs["is_active"]

        self._save_users()
        self.logger.info(f"Updated user: {username}")

        return {
            "status": "success",
            "message": f"User updated: {username}",
            "user": asdict(user),
        }


# Global singleton
_user_service: Optional[VibeUserService] = None


def get_user_service() -> VibeUserService:
    """Get or create the global user service."""
    global _user_service
    if _user_service is None:
        _user_service = VibeUserService()
    return _user_service
