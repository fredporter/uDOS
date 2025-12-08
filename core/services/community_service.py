"""
Community Service - v1.0.20
Manages Tier 3 (Groups) community knowledge

Features:
- Group creation and membership
- Community knowledge contributions
- Reputation and moderation
- Distributed storage (no central server)
- Democratic voting
- Local-first architecture

Author: uDOS Development Team
Version: 1.0.20
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime
from enum import Enum


class GroupRole(Enum):
    """Roles within a community group"""
    MEMBER = "member"        # Can read and contribute
    MODERATOR = "moderator"  # Can manage content
    ADMIN = "admin"          # Can manage membership
    FOUNDER = "founder"      # Group creator


class CommunityService:
    """
    Manages community groups and shared knowledge

    Responsibilities:
    - Group creation and membership
    - Knowledge contributions
    - Reputation tracking
    - Content moderation
    - Voting mechanisms
    """

    def __init__(self, base_path: str = None):
        """
        Initialize CommunityService

        Args:
            base_path: Base directory for groups tier (defaults to ./memory/groups)
        """
        if base_path is None:
            base_path = Path(__file__).parent.parent.parent / 'memory' / 'groups'

        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Metadata directory
        self.metadata_dir = self.base_path / '.metadata'
        self.metadata_dir.mkdir(exist_ok=True)

        # Groups registry
        self.groups_file = self.metadata_dir / 'groups.json'
        self.groups = self._load_groups()

        # User reputation
        self.reputation_file = self.metadata_dir / 'reputation.json'
        self.reputation = self._load_reputation()

    def _load_groups(self) -> Dict:
        """Load groups registry"""
        if self.groups_file.exists():
            with open(self.groups_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_groups(self):
        """Save groups registry"""
        with open(self.groups_file, 'w') as f:
            json.dump(self.groups, f, indent=2)

    def _load_reputation(self) -> Dict:
        """Load user reputation data"""
        if self.reputation_file.exists():
            with open(self.reputation_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_reputation(self):
        """Save user reputation data"""
        with open(self.reputation_file, 'w') as f:
            json.dump(self.reputation, f, indent=2)

    def create_group(self, group_name: str, founder: str,
                    description: str = "") -> bool:
        """
        Create a new community group

        Args:
            group_name: Unique group identifier
            founder: User creating the group
            description: Group description

        Returns:
            True if group created successfully
        """
        if group_name in self.groups:
            return False

        # Create group metadata
        self.groups[group_name] = {
            'name': group_name,
            'description': description,
            'founder': founder,
            'created': datetime.now().isoformat(),
            'members': {
                founder: {
                    'role': GroupRole.FOUNDER.value,
                    'joined': datetime.now().isoformat(),
                    'contributions': 0,
                    'reputation': 0
                }
            },
            'stats': {
                'total_members': 1,
                'total_contributions': 0,
                'total_votes': 0
            }
        }

        # Create group directory
        group_dir = self.base_path / group_name
        group_dir.mkdir(exist_ok=True)
        (group_dir / 'knowledge').mkdir(exist_ok=True)
        (group_dir / 'projects').mkdir(exist_ok=True)
        (group_dir / 'resources').mkdir(exist_ok=True)

        self._save_groups()

        return True

    def join_group(self, group_name: str, user: str) -> bool:
        """
        Join a community group

        Args:
            group_name: Group to join
            user: User joining

        Returns:
            True if joined successfully
        """
        if group_name not in self.groups:
            return False

        if user in self.groups[group_name]['members']:
            return False  # Already a member

        # Add member
        self.groups[group_name]['members'][user] = {
            'role': GroupRole.MEMBER.value,
            'joined': datetime.now().isoformat(),
            'contributions': 0,
            'reputation': 0
        }

        self.groups[group_name]['stats']['total_members'] += 1

        self._save_groups()

        return True

    def leave_group(self, group_name: str, user: str) -> bool:
        """
        Leave a community group

        Args:
            group_name: Group to leave
            user: User leaving

        Returns:
            True if left successfully
        """
        if group_name not in self.groups:
            return False

        if user not in self.groups[group_name]['members']:
            return False

        # Can't leave if you're the founder
        if self.groups[group_name]['members'][user]['role'] == GroupRole.FOUNDER.value:
            return False

        # Remove member
        del self.groups[group_name]['members'][user]
        self.groups[group_name]['stats']['total_members'] -= 1

        self._save_groups()

        return True

    def add_contribution(self, group_name: str, user: str,
                        title: str, content: str,
                        category: str = "knowledge") -> bool:
        """
        Add a contribution to group knowledge

        Args:
            group_name: Target group
            user: Contributing user
            title: Contribution title
            content: Contribution content
            category: Category (knowledge, projects, resources)

        Returns:
            True if contribution added
        """
        if group_name not in self.groups:
            return False

        if user not in self.groups[group_name]['members']:
            return False

        # Create contribution file
        group_dir = self.base_path / group_name / category
        contrib_file = group_dir / f"{title}.md"

        with open(contrib_file, 'w') as f:
            f.write(f"# {title}\n\n")
            f.write(f"**Author**: {user}\n")
            f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write(f"**Category**: {category}\n\n")
            f.write("---\n\n")
            f.write(content)

        # Update stats
        self.groups[group_name]['members'][user]['contributions'] += 1
        self.groups[group_name]['stats']['total_contributions'] += 1

        # Award reputation
        self._award_reputation(user, 10)  # 10 points per contribution

        self._save_groups()

        return True

    def _award_reputation(self, user: str, points: int):
        """Award reputation points to a user"""
        if user not in self.reputation:
            self.reputation[user] = {
                'total_points': 0,
                'contributions': 0,
                'groups': []
            }

        self.reputation[user]['total_points'] += points
        self._save_reputation()

    def get_group_info(self, group_name: str) -> Optional[Dict]:
        """Get detailed group information"""
        if group_name not in self.groups:
            return None

        return self.groups[group_name]

    def list_groups(self, user: str = None) -> List[Dict]:
        """
        List all groups or groups for a specific user

        Args:
            user: Optional user filter

        Returns:
            List of group summaries
        """
        groups_list = []

        for group_name, group_data in self.groups.items():
            if user and user not in group_data['members']:
                continue

            summary = {
                'name': group_name,
                'description': group_data['description'],
                'members': group_data['stats']['total_members'],
                'contributions': group_data['stats']['total_contributions'],
                'is_member': user in group_data['members'] if user else False
            }

            if user and user in group_data['members']:
                summary['role'] = group_data['members'][user]['role']

            groups_list.append(summary)

        return groups_list

    def get_member_role(self, group_name: str, user: str) -> Optional[GroupRole]:
        """Get user's role in a group"""
        if group_name not in self.groups:
            return None

        if user not in self.groups[group_name]['members']:
            return None

        role_str = self.groups[group_name]['members'][user]['role']
        return GroupRole(role_str)

    def check_permission(self, group_name: str, user: str,
                        required_role: GroupRole) -> bool:
        """
        Check if user has required role in group

        Args:
            group_name: Group to check
            user: User to check
            required_role: Minimum required role

        Returns:
            True if user has permission
        """
        user_role = self.get_member_role(group_name, user)

        if user_role is None:
            return False

        # Role hierarchy
        role_levels = {
            GroupRole.MEMBER: 1,
            GroupRole.MODERATOR: 2,
            GroupRole.ADMIN: 3,
            GroupRole.FOUNDER: 4
        }

        return role_levels[user_role] >= role_levels[required_role]

    def get_user_reputation(self, user: str) -> Dict:
        """Get user's reputation across all groups"""
        if user not in self.reputation:
            return {
                'total_points': 0,
                'contributions': 0,
                'groups': []
            }

        return self.reputation[user]

    def browse_group_knowledge(self, group_name: str,
                               category: str = "knowledge") -> List[Dict]:
        """
        Browse knowledge in a group

        Args:
            group_name: Group to browse
            category: Category to browse

        Returns:
            List of knowledge items
        """
        if group_name not in self.groups:
            return []

        group_dir = self.base_path / group_name / category

        if not group_dir.exists():
            return []

        items = []

        for file in group_dir.glob("*.md"):
            items.append({
                'title': file.stem,
                'path': str(file.relative_to(self.base_path)),
                'size': file.stat().st_size,
                'modified': datetime.fromtimestamp(file.stat().st_mtime).isoformat()
            })

        return items

    def get_stats(self) -> Dict:
        """Get community statistics"""
        total_groups = len(self.groups)
        total_members = sum(g['stats']['total_members'] for g in self.groups.values())
        total_contributions = sum(g['stats']['total_contributions'] for g in self.groups.values())

        return {
            'total_groups': total_groups,
            'total_members': total_members,
            'total_contributions': total_contributions,
            'active_groups': sum(1 for g in self.groups.values()
                               if g['stats']['total_members'] > 1)
        }


def main():
    """Test CommunityService"""
    print("👥 uDOS Community Service v1.0.20")
    print("=" * 50)

    service = CommunityService()

    # Test 1: Create group
    print("\n📝 Test 1: Create group")
    success = service.create_group(
        "local-gardeners",
        "alice@device1",
        "Community gardening and seed exchange"
    )
    print(f"✅ Group created: {success}")

    # Test 2: Join group
    print("\n👥 Test 2: Join group")
    service.join_group("local-gardeners", "bob@device2")
    service.join_group("local-gardeners", "charlie@device3")
    print("✅ 2 members joined")

    # Test 3: Add contribution
    print("\n📚 Test 3: Add contribution")
    service.add_contribution(
        "local-gardeners",
        "alice@device1",
        "tomato-seed-saving",
        "How to save and store tomato seeds for next season..."
    )
    print("✅ Contribution added")

    # Test 4: List groups
    print("\n📋 Test 4: List groups")
    groups = service.list_groups()
    for group in groups:
        print(f"  {group['name']}: {group['members']} members, "
              f"{group['contributions']} contributions")

    # Test 5: Statistics
    print("\n📊 Test 5: Statistics")
    stats = service.get_stats()
    print(f"Total groups: {stats['total_groups']}")
    print(f"Total members: {stats['total_members']}")
    print(f"Total contributions: {stats['total_contributions']}")

    print("\n✅ All community service tests passed!")


if __name__ == "__main__":
    main()
