"""
POKE Online - Group Manager v1.1.7

Collaboration group management for uDOS POKE extension.
Enables users to create groups, invite members, and coordinate shared work.

Features:
- Group creation and management
- Member invitation and management
- Shared workspace coordination
- Activity tracking
- Simple chat functionality

Author: uDOS Core Team
License: MIT
"""

import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

# uDOS imports
from core.services.logging_manager import get_logger


class MemberRole(Enum):
    """Group member roles."""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    GUEST = "guest"


@dataclass
class GroupMember:
    """Information about a group member."""
    user_id: str
    username: str
    role: MemberRole
    joined_at: datetime
    last_active: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'role': self.role.value,
            'joined_at': self.joined_at.isoformat(),
            'last_active': self.last_active.isoformat() if self.last_active else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GroupMember':
        """Create GroupMember from dictionary."""
        return cls(
            user_id=data['user_id'],
            username=data['username'],
            role=MemberRole(data['role']),
            joined_at=datetime.fromisoformat(data['joined_at']),
            last_active=datetime.fromisoformat(data['last_active']) if data.get('last_active') else None
        )


@dataclass
class GroupInfo:
    """Information about a collaboration group."""
    id: str
    name: str
    description: str
    owner: str
    created_at: datetime
    private: bool = False
    max_members: int = 10
    invite_code: Optional[str] = None
    expires_at: Optional[datetime] = None
    workspace_path: Optional[str] = None

    def __post_init__(self):
        if self.invite_code is None:
            self.invite_code = str(uuid.uuid4())[:12]

    def is_expired(self) -> bool:
        """Check if group has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'owner': self.owner,
            'created_at': self.created_at.isoformat(),
            'private': self.private,
            'max_members': self.max_members,
            'invite_code': self.invite_code,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'workspace_path': self.workspace_path
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GroupInfo':
        """Create GroupInfo from dictionary."""
        data = data.copy()
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('expires_at'):
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        return cls(**data)


class GroupManager:
    """
    Manages collaboration groups for POKE Online.

    Features:
    - Create and manage groups
    - Member invitation and management
    - Activity tracking
    - Shared workspaces
    """

    def __init__(self, project_root: Path = None):
        """Initialize group manager."""
        self.logger = get_logger('extension-poke-groups')

        if project_root is None:
            project_root = Path(__file__).parent.parent.parent.parent

        self.project_root = Path(project_root)
        self.groups_file = self.project_root / "sandbox" / "user" / "poke_groups.json"
        self.members_file = self.project_root / "sandbox" / "user" / "poke_members.json"

        self.groups: Dict[str, GroupInfo] = {}
        self.members: Dict[str, List[GroupMember]] = {}  # group_id -> members

        # Create directories
        self.groups_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing data
        self._load_data()

        self.logger.info("Group manager initialized")

    def _load_data(self):
        """Load groups and members from files."""
        try:
            # Load groups
            if self.groups_file.exists():
                with open(self.groups_file, 'r') as f:
                    data = json.load(f)
                    self.groups = {
                        group_id: GroupInfo.from_dict(group_data)
                        for group_id, group_data in data.items()
                    }

            # Load members
            if self.members_file.exists():
                with open(self.members_file, 'r') as f:
                    data = json.load(f)
                    self.members = {
                        group_id: [GroupMember.from_dict(m) for m in members_data]
                        for group_id, members_data in data.items()
                    }

            self.logger.debug(f"Loaded {len(self.groups)} groups")

        except Exception as e:
            self.logger.error(f"Error loading group data: {e}")
            self.groups = {}
            self.members = {}

    def _save_data(self):
        """Save groups and members to files."""
        try:
            # Save groups
            groups_data = {
                group_id: group.to_dict()
                for group_id, group in self.groups.items()
            }
            with open(self.groups_file, 'w') as f:
                json.dump(groups_data, f, indent=2)

            # Save members
            members_data = {
                group_id: [m.to_dict() for m in members]
                for group_id, members in self.members.items()
            }
            with open(self.members_file, 'w') as f:
                json.dump(members_data, f, indent=2)

            self.logger.debug(f"Saved {len(self.groups)} groups")

        except Exception as e:
            self.logger.error(f"Error saving group data: {e}")

    def create_group(self,
                    name: str,
                    description: str = "",
                    private: bool = False,
                    expires_hours: Optional[int] = None,
                    max_members: int = 10) -> GroupInfo:
        """
        Create a new collaboration group.

        Args:
            name: Group name
            description: Group description
            private: Whether group is private (invite-only)
            expires_hours: Hours until expiration (None = no expiration)
            max_members: Maximum number of members

        Returns:
            GroupInfo object
        """
        group_id = f"group_{int(time.time())}_{uuid.uuid4().hex[:8]}"

        expires_at = None
        if expires_hours is not None:
            expires_at = datetime.now() + timedelta(hours=expires_hours)

        # Create shared workspace directory
        workspace_path = self.project_root / "sandbox" / "groups" / group_id
        workspace_path.mkdir(parents=True, exist_ok=True)

        group = GroupInfo(
            id=group_id,
            name=name,
            description=description,
            owner="current_user",  # TODO: Get from config
            created_at=datetime.now(),
            private=private,
            max_members=max_members,
            expires_at=expires_at,
            workspace_path=str(workspace_path)
        )

        # Add creator as owner
        owner_member = GroupMember(
            user_id="current_user",
            username="current_user",
            role=MemberRole.OWNER,
            joined_at=datetime.now(),
            last_active=datetime.now()
        )

        # Store data
        self.groups[group_id] = group
        self.members[group_id] = [owner_member]
        self._save_data()

        self.logger.info(f"Created group: {group_id} ({name})")
        return group

    def get_group(self, group_id: str) -> Optional[GroupInfo]:
        """Get group by ID."""
        return self.groups.get(group_id)

    def get_group_by_invite_code(self, invite_code: str) -> Optional[GroupInfo]:
        """Get group by invite code."""
        for group in self.groups.values():
            if group.invite_code == invite_code:
                return group
        return None

    def join_group(self, invite_code: str, user_id: str = "current_user", username: str = "current_user") -> bool:
        """
        Join a group using invite code.

        Args:
            invite_code: Group invite code
            user_id: User ID joining
            username: Username joining

        Returns:
            True if joined successfully
        """
        group = self.get_group_by_invite_code(invite_code)

        if not group:
            self.logger.warning(f"Group not found for invite code: {invite_code}")
            return False

        if group.is_expired():
            self.logger.warning(f"Expired group join attempt: {group.id}")
            return False

        # Check if already member
        group_members = self.members.get(group.id, [])
        for member in group_members:
            if member.user_id == user_id:
                self.logger.info(f"User {user_id} already member of group {group.id}")
                return True

        # Check member limit
        if len(group_members) >= group.max_members:
            self.logger.warning(f"Group {group.id} at member limit")
            return False

        # Add member
        new_member = GroupMember(
            user_id=user_id,
            username=username,
            role=MemberRole.MEMBER,
            joined_at=datetime.now(),
            last_active=datetime.now()
        )

        group_members.append(new_member)
        self.members[group.id] = group_members
        self._save_data()

        self.logger.info(f"User {user_id} joined group {group.id}")
        return True

    def leave_group(self, group_id: str, user_id: str = "current_user") -> bool:
        """Leave a group."""
        if group_id not in self.members:
            return False

        group_members = self.members[group_id]

        # Find and remove member
        for i, member in enumerate(group_members):
            if member.user_id == user_id:
                del group_members[i]
                self._save_data()
                self.logger.info(f"User {user_id} left group {group_id}")

                # If owner left and members remain, promote first admin/member to owner
                if member.role == MemberRole.OWNER and group_members:
                    # Find first admin, or first member if no admin
                    new_owner = next((m for m in group_members if m.role == MemberRole.ADMIN),
                                   group_members[0] if group_members else None)
                    if new_owner:
                        new_owner.role = MemberRole.OWNER
                        if group_id in self.groups:
                            self.groups[group_id].owner = new_owner.user_id
                        self.logger.info(f"Promoted {new_owner.user_id} to owner of group {group_id}")

                # If no members left, delete group
                if not group_members:
                    self.delete_group(group_id)

                return True

        return False

    def delete_group(self, group_id: str) -> bool:
        """Delete a group and its workspace."""
        if group_id in self.groups:
            group = self.groups[group_id]

            # Clean up workspace directory
            if group.workspace_path:
                import shutil
                workspace_path = Path(group.workspace_path)
                if workspace_path.exists():
                    try:
                        shutil.rmtree(workspace_path)
                        self.logger.info(f"Deleted workspace for group {group_id}")
                    except Exception as e:
                        self.logger.error(f"Error deleting workspace: {e}")

            # Remove from storage
            del self.groups[group_id]
            if group_id in self.members:
                del self.members[group_id]

            self._save_data()
            self.logger.info(f"Deleted group: {group_id}")
            return True

        return False

    def list_user_groups(self, user_id: str = "current_user") -> List[Dict[str, Any]]:
        """List groups for a user."""
        user_groups = []

        for group_id, group in self.groups.items():
            if group.is_expired():
                continue

            # Check if user is member
            group_members = self.members.get(group_id, [])
            user_member = next((m for m in group_members if m.user_id == user_id), None)

            if user_member:
                user_groups.append({
                    'group': group,
                    'member_info': user_member,
                    'member_count': len(group_members)
                })

        # Sort by join date (newest first)
        user_groups.sort(key=lambda x: x['member_info'].joined_at, reverse=True)
        return user_groups

    def get_group_members(self, group_id: str) -> List[GroupMember]:
        """Get members of a group."""
        return self.members.get(group_id, [])

    def cleanup_expired_groups(self) -> int:
        """Remove expired groups."""
        expired_ids = []

        for group_id, group in self.groups.items():
            if group.is_expired():
                expired_ids.append(group_id)

        for group_id in expired_ids:
            self.delete_group(group_id)

        return len(expired_ids)

    def get_group_stats(self) -> Dict[str, Any]:
        """Get group statistics."""
        total_groups = len(self.groups)
        active_groups = len([g for g in self.groups.values() if not g.is_expired()])
        expired_groups = total_groups - active_groups

        total_members = sum(len(members) for members in self.members.values())

        private_groups = len([g for g in self.groups.values() if g.private])
        public_groups = total_groups - private_groups

        return {
            'total_groups': total_groups,
            'active_groups': active_groups,
            'expired_groups': expired_groups,
            'total_members': total_members,
            'private_groups': private_groups,
            'public_groups': public_groups
        }


def create_group_manager(project_root: Path = None) -> GroupManager:
    """Create group manager instance."""
    return GroupManager(project_root)
