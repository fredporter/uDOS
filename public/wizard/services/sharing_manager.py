"""
POKE Online - Sharing Manager v1.1.7

File and folder sharing system for uDOS with permission management.
Enables secure sharing of content via tunnels with access controls.

Features:
- File and folder sharing with permissions
- Token-based access control
- Share expiration and revocation
- Activity logging and analytics
- Integration with tunnel manager

Author: uDOS Core Team
License: MIT
"""

import os
import json
import uuid
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

# uDOS imports
from wizard.services.logging_manager import get_logger


class SharePermission(Enum):
    """Share permission levels."""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"


@dataclass
class ShareInfo:
    """Information about a shared resource."""
    id: str
    token: str
    path: str
    share_type: str  # 'file' or 'folder'
    permissions: Set[SharePermission]
    owner: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    description: str = ""
    password_protected: bool = False

    def __post_init__(self):
        if isinstance(self.permissions, list):
            self.permissions = set(SharePermission(p) for p in self.permissions)

    def is_expired(self) -> bool:
        """Check if share has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def can_access(self, permission: SharePermission) -> bool:
        """Check if share allows specific permission."""
        if self.is_expired():
            return False
        return permission in self.permissions

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['permissions'] = [p.value for p in self.permissions]
        data['created_at'] = self.created_at.isoformat()
        data['expires_at'] = self.expires_at.isoformat() if self.expires_at else None
        data['last_accessed'] = self.last_accessed.isoformat() if self.last_accessed else None
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ShareInfo':
        """Create ShareInfo from dictionary."""
        data = data.copy()
        data['permissions'] = set(SharePermission(p) for p in data['permissions'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data['expires_at']:
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        if data['last_accessed']:
            data['last_accessed'] = datetime.fromisoformat(data['last_accessed'])
        return cls(**data)


class SharingManager:
    """
    Manages file and folder sharing for POKE Online.

    Features:
    - Create and manage shares
    - Token-based access control
    - Permission management
    - Share expiration and cleanup
    - Activity tracking
    """

    def __init__(self, project_root: Path = None):
        """Initialize sharing manager."""
        self.logger = get_logger('extension-poke-sharing')

        if project_root is None:
            project_root = Path(__file__).parent.parent.parent.parent

        self.project_root = Path(project_root)
        self.shares_file = self.project_root / "memory" / "shared" / "public" / "poke_shares.json"
        self.shares: Dict[str, ShareInfo] = {}

        # Create directories
        self.shares_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing shares
        self._load_shares()

        self.logger.info("Sharing manager initialized")

    def _load_shares(self):
        """Load shares from file."""
        try:
            if self.shares_file.exists():
                with open(self.shares_file, 'r') as f:
                    data = json.load(f)
                    self.shares = {
                        share_id: ShareInfo.from_dict(share_data)
                        for share_id, share_data in data.items()
                    }
                self.logger.debug(f"Loaded {len(self.shares)} shares")
        except Exception as e:
            self.logger.error(f"Error loading shares: {e}")
            self.shares = {}

    def _save_shares(self):
        """Save shares to file."""
        try:
            data = {
                share_id: share.to_dict()
                for share_id, share in self.shares.items()
            }
            with open(self.shares_file, 'w') as f:
                json.dump(data, f, indent=2)
            self.logger.debug(f"Saved {len(self.shares)} shares")
        except Exception as e:
            self.logger.error(f"Error saving shares: {e}")

    def _generate_token(self) -> str:
        """Generate secure share token."""
        return str(uuid.uuid4()).replace('-', '')[:16]

    def _validate_path(self, path: str) -> Path:
        """Validate and resolve share path."""
        # Convert to Path and resolve
        share_path = Path(path).resolve()

        # Must be within project root
        try:
            share_path.relative_to(self.project_root)
        except ValueError:
            raise ValueError(f"Path must be within project directory: {path}")

        # Path must exist
        if not share_path.exists():
            raise ValueError(f"Path does not exist: {path}")

        return share_path

    def create_share(self,
                    path: str,
                    permissions: List[str],
                    expires_hours: Optional[int] = None,
                    description: str = "",
                    password: Optional[str] = None) -> ShareInfo:
        """
        Create a new share.

        Args:
            path: Path to file or folder to share
            permissions: List of permissions ('read', 'write', 'execute')
            expires_hours: Hours until expiration (None = no expiration)
            description: Optional description
            password: Optional password protection

        Returns:
            ShareInfo object
        """
        # Validate path
        validated_path = self._validate_path(path)

        # Parse permissions
        perm_set = set()
        for perm in permissions:
            try:
                perm_set.add(SharePermission(perm.lower()))
            except ValueError:
                raise ValueError(f"Invalid permission: {perm}")

        if not perm_set:
            perm_set.add(SharePermission.READ)  # Default to read

        # Create share
        share_id = f"share_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        token = self._generate_token()

        expires_at = None
        if expires_hours is not None:
            expires_at = datetime.now() + timedelta(hours=expires_hours)

        share_type = "folder" if validated_path.is_dir() else "file"

        share = ShareInfo(
            id=share_id,
            token=token,
            path=str(validated_path),
            share_type=share_type,
            permissions=perm_set,
            owner="current_user",  # TODO: Get from config
            created_at=datetime.now(),
            expires_at=expires_at,
            description=description,
            password_protected=bool(password)
        )

        # Store share
        self.shares[share_id] = share
        self._save_shares()

        self.logger.info(f"Created {share_type} share: {share_id} -> {path}")
        return share

    def get_share(self, share_id: str) -> Optional[ShareInfo]:
        """Get share by ID."""
        return self.shares.get(share_id)

    def get_share_by_token(self, token: str) -> Optional[ShareInfo]:
        """Get share by access token."""
        for share in self.shares.values():
            if share.token == token:
                return share
        return None

    def revoke_share(self, share_id: str) -> bool:
        """Revoke a share."""
        if share_id in self.shares:
            share = self.shares[share_id]
            del self.shares[share_id]
            self._save_shares()
            self.logger.info(f"Revoked share: {share_id}")
            return True
        return False

    def list_shares(self, include_expired: bool = False) -> List[ShareInfo]:
        """List all shares."""
        shares = list(self.shares.values())

        if not include_expired:
            shares = [s for s in shares if not s.is_expired()]

        # Sort by creation time (newest first)
        shares.sort(key=lambda s: s.created_at, reverse=True)
        return shares

    def access_share(self, token: str, permission: str = "read") -> Optional[ShareInfo]:
        """
        Access a share (increments access count).

        Args:
            token: Share access token
            permission: Required permission

        Returns:
            ShareInfo if access granted, None otherwise
        """
        share = self.get_share_by_token(token)

        if not share:
            self.logger.warning(f"Share not found for token: {token[:8]}...")
            return None

        # Check expiration
        if share.is_expired():
            self.logger.warning(f"Expired share accessed: {share.id}")
            return None

        # Check permission
        try:
            required_perm = SharePermission(permission.lower())
            if not share.can_access(required_perm):
                self.logger.warning(f"Insufficient permission for share {share.id}: {permission}")
                return None
        except ValueError:
            self.logger.error(f"Invalid permission requested: {permission}")
            return None

        # Update access stats
        share.access_count += 1
        share.last_accessed = datetime.now()
        self._save_shares()

        self.logger.info(f"Share accessed: {share.id} ({permission})")
        return share

    def cleanup_expired_shares(self) -> int:
        """Remove expired shares."""
        expired_ids = []

        for share_id, share in self.shares.items():
            if share.is_expired():
                expired_ids.append(share_id)

        for share_id in expired_ids:
            del self.shares[share_id]
            self.logger.info(f"Cleaned up expired share: {share_id}")

        if expired_ids:
            self._save_shares()

        return len(expired_ids)

    def get_share_stats(self) -> Dict[str, Any]:
        """Get sharing statistics."""
        total_shares = len(self.shares)
        active_shares = len([s for s in self.shares.values() if not s.is_expired()])
        expired_shares = total_shares - active_shares

        total_accesses = sum(s.access_count for s in self.shares.values())

        shares_by_type = {}
        for share in self.shares.values():
            shares_by_type[share.share_type] = shares_by_type.get(share.share_type, 0) + 1

        return {
            'total_shares': total_shares,
            'active_shares': active_shares,
            'expired_shares': expired_shares,
            'total_accesses': total_accesses,
            'shares_by_type': shares_by_type
        }

    def generate_share_url(self, share: ShareInfo, base_url: str) -> str:
        """Generate public URL for accessing share."""
        return f"{base_url.rstrip('/')}/share/{share.token}"


def create_sharing_manager(project_root: Path = None) -> SharingManager:
    """Create sharing manager instance."""
    return SharingManager(project_root)
