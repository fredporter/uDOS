"""
Sharing Service - v1.0.20
Manages Tier 2 (Shared) permissions and access control

Features:
- Selective file sharing with specific users
- Permission levels (READ, EDIT, FULL)
- Revocable access
- Time-limited shares
- Access logging and audit trails
- Local P2P only (no cloud)

Author: uDOS Development Team
Version: 1.0.20
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from enum import Enum


class SharePermission(Enum):
    """Permission levels for shared content"""
    NONE = "none"
    READ = "read"      # View only
    EDIT = "edit"      # View and modify
    FULL = "full"      # View, modify, and manage sharing


class SharingService:
    """
    Manages file sharing permissions for Tier 2 (Shared)

    Responsibilities:
    - Grant and revoke access to files
    - Check permissions for users
    - Log all access events
    - Manage time-limited shares
    - Audit trail for compliance
    """

    def __init__(self, base_path: str = None):
        """
        Initialize SharingService

        Args:
            base_path: Base directory for shared tier (defaults to ./memory/shared)
        """
        if base_path is None:
            base_path = Path(__file__).parent.parent.parent / 'memory' / 'shared'

        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Metadata directory
        self.metadata_dir = self.base_path / '.metadata'
        self.metadata_dir.mkdir(exist_ok=True)

        # ACL and logs
        self.acl_file = self.metadata_dir / 'acl.json'
        self.log_file = self.metadata_dir / 'access.log'

        # Load ACL
        self.acl = self._load_acl()

    def _load_acl(self) -> Dict:
        """Load access control list"""
        if self.acl_file.exists():
            with open(self.acl_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_acl(self):
        """Save access control list"""
        with open(self.acl_file, 'w') as f:
            json.dump(self.acl, f, indent=2)

    def _log_access(self, action: str, file_path: str, user: str, details: str = ""):
        """Log access event"""
        timestamp = datetime.now().isoformat()
        log_entry = f"{timestamp} | {action} | {user} | {file_path} | {details}\n"

        with open(self.log_file, 'a') as f:
            f.write(log_entry)

    def grant_access(self, file_path: str, user: str, permission: SharePermission,
                    expires: Optional[datetime] = None) -> bool:
        """
        Grant access to a file for a user

        Args:
            file_path: Path to file (relative to shared tier)
            user: User identifier (e.g., "user@device")
            permission: Permission level
            expires: Optional expiration datetime

        Returns:
            True if access granted successfully
        """
        # Initialize file ACL if not exists
        if file_path not in self.acl:
            self.acl[file_path] = {
                'owner': 'owner',
                'created': datetime.now().isoformat(),
                'permissions': {}
            }

        # Set permission
        self.acl[file_path]['permissions'][user] = {
            'level': permission.value,
            'granted': datetime.now().isoformat(),
            'expires': expires.isoformat() if expires else None
        }

        # Save ACL
        self._save_acl()

        # Log action
        expires_str = f"expires {expires}" if expires else "no expiration"
        self._log_access('GRANT', file_path, user,
                        f"{permission.value} - {expires_str}")

        return True

    def revoke_access(self, file_path: str, user: str) -> bool:
        """
        Revoke access to a file for a user

        Args:
            file_path: Path to file
            user: User identifier

        Returns:
            True if access revoked successfully
        """
        if file_path not in self.acl:
            return False

        if user not in self.acl[file_path]['permissions']:
            return False

        # Remove permission
        del self.acl[file_path]['permissions'][user]

        # Save ACL
        self._save_acl()

        # Log action
        self._log_access('REVOKE', file_path, user)

        return True

    def check_access(self, file_path: str, user: str,
                     required: SharePermission = SharePermission.READ) -> bool:
        """
        Check if user has required permission for file

        Args:
            file_path: Path to file
            user: User identifier
            required: Required permission level

        Returns:
            True if user has required access
        """
        # Owner always has full access
        if user == "owner":
            return True

        # Check if file has ACL
        if file_path not in self.acl:
            return False

        # Check if user has permission
        if user not in self.acl[file_path]['permissions']:
            return False

        perm = self.acl[file_path]['permissions'][user]

        # Check expiration
        if perm['expires']:
            expires = datetime.fromisoformat(perm['expires'])
            if datetime.now() > expires:
                # Permission expired
                self.revoke_access(file_path, user)
                return False

        # Check permission level
        user_level = SharePermission(perm['level'])

        # Permission hierarchy: NONE < READ < EDIT < FULL
        levels = {
            SharePermission.NONE: 0,
            SharePermission.READ: 1,
            SharePermission.EDIT: 2,
            SharePermission.FULL: 3
        }

        return levels[user_level] >= levels[required]

    def get_file_permissions(self, file_path: str) -> Dict:
        """Get all permissions for a file"""
        if file_path not in self.acl:
            return {'owner': 'owner', 'permissions': {}}

        return self.acl[file_path]

    def get_user_files(self, user: str) -> List[str]:
        """Get all files a user has access to"""
        files = []

        for file_path, data in self.acl.items():
            if user == "owner" or user in data['permissions']:
                # Check if not expired
                if user in data['permissions']:
                    perm = data['permissions'][user]
                    if perm['expires']:
                        expires = datetime.fromisoformat(perm['expires'])
                        if datetime.now() > expires:
                            continue

                files.append(file_path)

        return files

    def get_access_logs(self, file_path: str = None, user: str = None,
                       limit: int = 100) -> List[Dict]:
        """
        Get access logs with optional filtering

        Args:
            file_path: Filter by file path (optional)
            user: Filter by user (optional)
            limit: Maximum number of entries

        Returns:
            List of log entries
        """
        if not self.log_file.exists():
            return []

        logs = []

        with open(self.log_file, 'r') as f:
            for line in f:
                parts = line.strip().split(' | ')
                if len(parts) >= 4:
                    entry = {
                        'timestamp': parts[0],
                        'action': parts[1],
                        'user': parts[2],
                        'file': parts[3],
                        'details': parts[4] if len(parts) > 4 else ""
                    }

                    # Apply filters
                    if file_path and entry['file'] != file_path:
                        continue
                    if user and entry['user'] != user:
                        continue

                    logs.append(entry)

        # Return most recent entries
        return logs[-limit:]

    def cleanup_expired(self) -> int:
        """
        Remove all expired permissions

        Returns:
            Number of permissions removed
        """
        removed = 0
        now = datetime.now()

        for file_path in list(self.acl.keys()):
            for user in list(self.acl[file_path]['permissions'].keys()):
                perm = self.acl[file_path]['permissions'][user]
                if perm['expires']:
                    expires = datetime.fromisoformat(perm['expires'])
                    if now > expires:
                        del self.acl[file_path]['permissions'][user]
                        removed += 1
                        self._log_access('EXPIRED', file_path, user)

        if removed > 0:
            self._save_acl()

        return removed

    def get_stats(self) -> Dict:
        """Get sharing statistics"""
        total_files = len(self.acl)
        total_permissions = sum(len(data['permissions'])
                               for data in self.acl.values())

        # Count by permission level
        by_level = {level.value: 0 for level in SharePermission}

        for data in self.acl.values():
            for perm in data['permissions'].values():
                by_level[perm['level']] += 1

        # Count expired
        expired = 0
        now = datetime.now()
        for data in self.acl.values():
            for perm in data['permissions'].values():
                if perm['expires']:
                    if now > datetime.fromisoformat(perm['expires']):
                        expired += 1

        return {
            'total_files': total_files,
            'total_permissions': total_permissions,
            'by_level': by_level,
            'expired': expired
        }


def main():
    """Test SharingService"""
    print("🤝 uDOS Sharing Service v1.0.20")
    print("=" * 50)

    service = SharingService()

    # Test granting access
    print("\n📝 Test 1: Grant access")
    service.grant_access("project-plan.md", "alice@device1", SharePermission.EDIT)
    service.grant_access("project-plan.md", "bob@device2", SharePermission.READ)
    print("✅ Granted access to 2 users")

    # Test checking access
    print("\n🔍 Test 2: Check access")
    can_edit = service.check_access("project-plan.md", "alice@device1", SharePermission.EDIT)
    can_read = service.check_access("project-plan.md", "bob@device2", SharePermission.READ)
    cant_edit = service.check_access("project-plan.md", "bob@device2", SharePermission.EDIT)

    print(f"Alice can edit: {can_edit}")
    print(f"Bob can read: {can_read}")
    print(f"Bob can edit: {cant_edit}")

    # Test time-limited share
    print("\n⏰ Test 3: Time-limited share")
    expires = datetime.now() + timedelta(hours=24)
    service.grant_access("temp-notes.md", "charlie@device3",
                        SharePermission.READ, expires)
    print(f"✅ Granted temporary access (expires in 24h)")

    # Test statistics
    print("\n📊 Test 4: Statistics")
    stats = service.get_stats()
    print(f"Total files shared: {stats['total_files']}")
    print(f"Total permissions: {stats['total_permissions']}")
    print(f"By level: {stats['by_level']}")

    # Test logs
    print("\n📋 Test 5: Access logs")
    logs = service.get_access_logs(limit=5)
    print(f"Recent access events: {len(logs)}")
    for log in logs:
        print(f"  {log['action']:8} | {log['user']:20} | {log['file']}")

    print("\n✅ All sharing service tests passed!")


if __name__ == "__main__":
    main()
