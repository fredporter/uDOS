"""Dev Mode tool user service."""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from hashlib import pbkdf2_hmac
import hmac
import secrets

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
    password_hash: Optional[str] = None
    password_salt: Optional[str] = None
    failed_attempts: int = 0


class DevModeToolUserService:
    """Manage user accounts and permissions."""

    _DATA_FILE = "users"

    def __init__(self):
        """Initialize user service."""
        self.logger = get_logger("dev-mode-tool-user-service")
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
        users = [self._public_user(u) for u in self.users.values()]
        return {
            "status": "success",
            "users": users,
            "count": len(users),
        }

    @staticmethod
    def _public_user(user: User) -> Dict[str, Any]:
        """Return safe user payload without credential material."""
        payload = asdict(user)
        payload.pop("password_hash", None)
        payload.pop("password_salt", None)
        return payload

    @staticmethod
    def _derive_password_hash(password: str, salt_hex: str) -> str:
        """Derive deterministic password hash using PBKDF2-HMAC-SHA256."""
        digest = pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            120_000,
        )
        return digest.hex()

    def add_user(
        self,
        username: str,
        email: str,
        role: str = "user",
        password: Optional[str] = None,
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
        salt = secrets.token_hex(16) if password else None

        user = User(
            id=user_id,
            username=username,
            email=email,
            role=role,
            created=now,
            password_salt=salt,
            password_hash=self._derive_password_hash(password, salt) if password and salt else None,
        )

        self.users[user_id] = user
        self._save_users()
        self.logger.info(f"Created user: {username}")

        return {
            "status": "success",
            "message": f"User created: {username}",
            "user": self._public_user(user),
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
        if "password" in kwargs and kwargs["password"]:
            salt = secrets.token_hex(16)
            user.password_salt = salt
            user.password_hash = self._derive_password_hash(kwargs["password"], salt)
            user.failed_attempts = 0

        self._save_users()
        self.logger.info(f"Updated user: {username}")

        return {
            "status": "success",
            "message": f"User updated: {username}",
            "user": self._public_user(user),
        }

    def authenticate(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user credentials against local user backend."""
        user = self.users.get(username)
        if not user:
            return {"status": "error", "message": "Authentication failed"}
        if not user.is_active:
            return {"status": "error", "message": f"User is inactive: {username}"}
        if not user.password_hash or not user.password_salt:
            return {"status": "error", "message": f"Password not configured for user: {username}"}

        derived = self._derive_password_hash(password, user.password_salt)
        if not hmac.compare_digest(derived, user.password_hash):
            user.failed_attempts += 1
            self._save_users()
            return {"status": "error", "message": "Authentication failed"}

        user.failed_attempts = 0
        user.last_login = datetime.now().isoformat()
        self._save_users()
        return {
            "status": "success",
            "message": f"Authenticated: {username}",
            "user": self._public_user(user),
        }


# Global singleton
VibeUserService = DevModeToolUserService

_user_service: Optional[DevModeToolUserService] = None


def get_user_service() -> DevModeToolUserService:
    """Get or create the global user service."""
    global _user_service
    if _user_service is None:
        _user_service = DevModeToolUserService()
    return _user_service
