"""
Community Command Handler - v1.0.20
Tier 3: Community group knowledge

Commands:
  COMMUNITY CREATE <name> [description]
  COMMUNITY JOIN <name>
  COMMUNITY LEAVE <name>
  COMMUNITY LIST
  COMMUNITY INFO <name>
  COMMUNITY ADD <group> <title> [category]
  COMMUNITY BROWSE <group> [category]
  COMMUNITY MEMBERS <group>
  COMMUNITY STATUS

Author: uDOS Development Team
Version: 1.0.20
"""

from pathlib import Path
from typing import List
from core.services.community_service import CommunityService, GroupRole
from core.services.memory_manager import MemoryManager, MemoryTier


class CommunityCommandHandler:
    """Handler for COMMUNITY (Tier 3) commands"""

    def __init__(self):
        """Initialize CommunityCommandHandler"""
        self.memory_manager = MemoryManager()
        self.community_service = CommunityService()
        self.groups_path = self.memory_manager.get_tier_path(MemoryTier.GROUPS)
        # Get user from config or use placeholder
        try:
            from core.config import Config
            config = Config()
            self.current_user = config.get('current_user', 'owner@localhost')
        except:
            self.current_user = "owner@localhost"

    def handle(self, command: str, args: List[str]) -> str:
        """
        Route COMMUNITY commands to appropriate handlers

        Args:
            command: Subcommand (CREATE, JOIN, etc.)
            args: Command arguments

        Returns:
            Formatted response string
        """
        if not command or command.upper() == "HELP":
            return self._help()

        command = command.upper()

        handlers = {
            'CREATE': self._create,
            'NEW': self._create,       # Alias
            'JOIN': self._join,
            'LEAVE': self._leave,
            'QUIT': self._leave,       # Alias
            'LIST': self._list,
            'LS': self._list,          # Alias
            'INFO': self._info,
            'SHOW': self._info,        # Alias
            'ADD': self._add,
            'CONTRIBUTE': self._add,   # Alias
            'BROWSE': self._browse,
            'VIEW': self._browse,      # Alias
            'MEMBERS': self._members,
            'STATUS': self._status,
            'STATS': self._status,     # Alias
        }

        handler = handlers.get(command)
        if handler:
            return handler(args)
        else:
            return f"❌ Unknown COMMUNITY command: {command}\n\nType 'COMMUNITY HELP' for usage."

    def _help(self) -> str:
        """Display COMMUNITY command help"""
        return """
👥 COMMUNITY - Tier 3: Community Group Knowledge

COMMUNITY MODEL:
  • Membership-based - Join communities of interest
  • Contribution system - Add to group knowledge
  • Reputation tracking - Recognition for contributions
  • Community moderation - Group-managed quality
  • Local-first - Data stays with members
  • No central server - Distributed across devices
  • Democratic - Voting on content and decisions

COMMANDS:
  COMMUNITY CREATE <name> [desc]     Create new group
  COMMUNITY JOIN <name>              Join a group
  COMMUNITY LEAVE <name>             Leave a group
  COMMUNITY LIST                     List all groups
  COMMUNITY INFO <name>              Group details
  COMMUNITY ADD <group> <title>      Contribute knowledge
  COMMUNITY BROWSE <group> [cat]     Browse group knowledge
  COMMUNITY MEMBERS <group>          List group members
  COMMUNITY STATUS                   Community statistics

GROUP TYPES:
  • Local neighborhood groups
  • Skill-sharing circles (permaculture, first aid, mechanics)
  • Barter networks
  • Survival communities
  • Project teams
  • Learning groups

ROLES:
  FOUNDER    - Group creator (full control)
  ADMIN      - Manage membership and settings
  MODERATOR  - Manage content quality
  MEMBER     - Read and contribute

EXAMPLES:
  # Create a new group
  COMMUNITY CREATE local-gardeners "Community gardening"

  # Join a group
  COMMUNITY JOIN local-gardeners

  # Contribute knowledge
  COMMUNITY ADD local-gardeners seed-saving

  # Browse group knowledge
  COMMUNITY BROWSE local-gardeners

  # View group info
  COMMUNITY INFO local-gardeners

CATEGORIES:
  knowledge  - Guides, tutorials, how-tos
  projects   - Collaborative projects
  resources  - Shared resources and tools

REPUTATION:
  • Earn points for contributions
  • 10 points per knowledge contribution
  • Reputation visible to group members
  • Higher reputation = trusted contributor
"""

    def _create(self, args: List[str]) -> str:
        """Create a new community group"""
        if not args:
            return "❌ Usage: COMMUNITY CREATE <name> [description]"

        group_name = args[0]
        description = " ".join(args[1:]) if len(args) > 1 else ""

        # Create group
        success = self.community_service.create_group(
            group_name, self.current_user, description
        )

        if not success:
            return f"❌ Group already exists: {group_name}"

        return f"""
✅ Community group created!

👥 Group: {group_name}
📝 Description: {description if description else "(none)"}
👑 Founder: {self.current_user}
📅 Created: {self.community_service.groups[group_name]['created'][:10]}

You are now the founder of this group.
Use 'COMMUNITY ADD {group_name} <title>' to contribute knowledge.
"""

    def _join(self, args: List[str]) -> str:
        """Join a community group"""
        if not args:
            return "❌ Usage: COMMUNITY JOIN <name>"

        group_name = args[0]

        # Join group
        success = self.community_service.join_group(group_name, self.current_user)

        if not success:
            if group_name not in self.community_service.groups:
                return f"❌ Group not found: {group_name}"
            else:
                return f"ℹ️  You are already a member of {group_name}"

        group_info = self.community_service.get_group_info(group_name)

        return f"""
✅ Joined community group!

👥 Group: {group_name}
📝 Description: {group_info['description']}
👤 Members: {group_info['stats']['total_members']}
📚 Contributions: {group_info['stats']['total_contributions']}

You can now contribute and access group knowledge.
Use 'COMMUNITY BROWSE {group_name}' to explore.
"""

    def _leave(self, args: List[str]) -> str:
        """Leave a community group"""
        if not args:
            return "❌ Usage: COMMUNITY LEAVE <name>"

        group_name = args[0]

        # Leave group
        success = self.community_service.leave_group(group_name, self.current_user)

        if not success:
            if group_name not in self.community_service.groups:
                return f"❌ Group not found: {group_name}"
            elif self.current_user not in self.community_service.groups[group_name]['members']:
                return f"ℹ️  You are not a member of {group_name}"
            else:
                return f"❌ Founders cannot leave their own groups"

        return f"""
✅ Left community group

👥 Group: {group_name}

You are no longer a member of this group.
"""

    def _list(self, args: List[str]) -> str:
        """List all groups or user's groups"""
        show_all = len(args) > 0 and args[0].upper() == "ALL"

        groups = self.community_service.list_groups(
            None if show_all else self.current_user
        )

        output = ["👥 Community Groups"]
        if not show_all:
            output.append(f"📊 Your groups")
        output.append("=" * 60)

        if not groups:
            output.append("\n📭 No groups found")
            if not show_all:
                output.append("\nUse 'COMMUNITY LIST ALL' to see all groups")
        else:
            output.append(f"\n📊 {len(groups)} group(s)\n")

            for group in groups:
                icon = "👑" if group.get('role') == 'founder' else "👤" if group.get('is_member') else "👥"

                output.append(f"{icon} {group['name']}")
                if group['description']:
                    output.append(f"   {group['description']}")
                output.append(f"   Members: {group['members']} | "
                            f"Contributions: {group['contributions']}")

                if group.get('is_member'):
                    role = group.get('role', 'member').upper()
                    output.append(f"   Your role: {role}")

                output.append("")

        output.append("=" * 60)
        output.append("\nℹ️  Use 'COMMUNITY INFO <name>' for details")

        return "\n".join(output)

    def _info(self, args: List[str]) -> str:
        """Show group information"""
        if not args:
            return "❌ Usage: COMMUNITY INFO <name>"

        group_name = args[0]
        group_info = self.community_service.get_group_info(group_name)

        if not group_info:
            return f"❌ Group not found: {group_name}"

        output = [f"👥 {group_name}"]
        output.append("=" * 60)

        # Basic info
        output.append(f"\n📝 Description: {group_info['description'] if group_info['description'] else '(none)'}")
        output.append(f"👑 Founder: {group_info['founder']}")
        output.append(f"📅 Created: {group_info['created'][:10]}")

        # Statistics
        stats = group_info['stats']
        output.append(f"\n📊 Statistics:")
        output.append(f"  Members: {stats['total_members']}")
        output.append(f"  Contributions: {stats['total_contributions']}")
        output.append(f"  Votes: {stats['total_votes']}")

        # Your membership
        if self.current_user in group_info['members']:
            member_data = group_info['members'][self.current_user]
            output.append(f"\n👤 Your Membership:")
            output.append(f"  Role: {member_data['role'].upper()}")
            output.append(f"  Joined: {member_data['joined'][:10]}")
            output.append(f"  Contributions: {member_data['contributions']}")
            output.append(f"  Reputation: {member_data['reputation']}")
        else:
            output.append(f"\nℹ️  You are not a member of this group")
            output.append(f"   Use 'COMMUNITY JOIN {group_name}' to join")

        output.append("\n" + "=" * 60)

        return "\n".join(output)

    def _add(self, args: List[str]) -> str:
        """Add contribution to group"""
        if len(args) < 2:
            return "❌ Usage: COMMUNITY ADD <group> <title> [category]"

        group_name = args[0]
        title = args[1]
        category = args[2] if len(args) > 2 else "knowledge"

        # Check membership
        if group_name not in self.community_service.groups:
            return f"❌ Group not found: {group_name}"

        if self.current_user not in self.community_service.groups[group_name]['members']:
            return f"❌ You must be a member of {group_name} to contribute"

        # Get content (in real implementation, this would open editor)
        print(f"\n📝 Enter contribution content (end with empty line):")
        lines = []
        while True:
            try:
                line = input()
                if not line:
                    break
                lines.append(line)
            except EOFError:
                break

        content = "\n".join(lines) if lines else "Contribution content goes here..."

        # Add contribution
        success = self.community_service.add_contribution(
            group_name, self.current_user, title, content, category
        )

        if not success:
            return "❌ Failed to add contribution"

        return f"""
✅ Contribution added!

👥 Group: {group_name}
📄 Title: {title}
📁 Category: {category}
💰 Reputation: +10 points

Your contribution is now available to all group members.
"""

    def _browse(self, args: List[str]) -> str:
        """Browse group knowledge"""
        if not args:
            return "❌ Usage: COMMUNITY BROWSE <group> [category]"

        group_name = args[0]
        category = args[1] if len(args) > 1 else "knowledge"

        # Check membership
        if group_name not in self.community_service.groups:
            return f"❌ Group not found: {group_name}"

        if self.current_user not in self.community_service.groups[group_name]['members']:
            return f"❌ You must be a member of {group_name} to browse"

        # Browse knowledge
        items = self.community_service.browse_group_knowledge(group_name, category)

        output = [f"📚 {group_name} - {category}"]
        output.append("=" * 60)

        if not items:
            output.append(f"\n📭 No {category} items yet")
            output.append(f"\nUse 'COMMUNITY ADD {group_name} <title> {category}' to contribute")
        else:
            output.append(f"\n📊 {len(items)} item(s)\n")

            for item in items:
                size_kb = item['size'] / 1024
                output.append(f"📄 {item['title']}")
                output.append(f"   Size: {size_kb:.1f} KB | Modified: {item['modified'][:10]}")

        output.append("\n" + "=" * 60)

        return "\n".join(output)

    def _members(self, args: List[str]) -> str:
        """List group members"""
        if not args:
            return "❌ Usage: COMMUNITY MEMBERS <group>"

        group_name = args[0]
        group_info = self.community_service.get_group_info(group_name)

        if not group_info:
            return f"❌ Group not found: {group_name}"

        output = [f"👥 {group_name} - Members"]
        output.append("=" * 60)

        members = group_info['members']
        output.append(f"\n📊 {len(members)} member(s)\n")

        # Sort by role
        role_order = {'founder': 0, 'admin': 1, 'moderator': 2, 'member': 3}
        sorted_members = sorted(members.items(),
                               key=lambda x: role_order.get(x[1]['role'], 4))

        for user, data in sorted_members:
            role_icons = {
                'founder': '👑',
                'admin': '⚡',
                'moderator': '🛡️',
                'member': '👤'
            }
            icon = role_icons.get(data['role'], '👤')

            output.append(f"{icon} {user} ({data['role'].upper()})")
            output.append(f"   Joined: {data['joined'][:10]} | "
                        f"Contributions: {data['contributions']} | "
                        f"Reputation: {data['reputation']}")

        output.append("\n" + "=" * 60)

        return "\n".join(output)

    def _status(self, args: List[str]) -> str:
        """Show community statistics"""
        stats = self.community_service.get_stats()
        tier_stats = self.memory_manager.get_tier_stats(MemoryTier.GROUPS)

        # User reputation
        user_rep = self.community_service.get_user_reputation(self.current_user)

        output = ["👥 Community Status"]
        output.append("=" * 60)

        # Tier statistics
        output.append(f"\n📊 Tier Statistics:")
        output.append(f"  Total Files: {tier_stats['file_count']}")
        output.append(f"  Total Size: {tier_stats['total_size_mb']} MB")

        # Community statistics
        output.append(f"\n🌍 Community:")
        output.append(f"  Total Groups: {stats['total_groups']}")
        output.append(f"  Active Groups: {stats['active_groups']}")
        output.append(f"  Total Members: {stats['total_members']}")
        output.append(f"  Total Contributions: {stats['total_contributions']}")

        # User statistics
        output.append(f"\n👤 Your Stats:")
        output.append(f"  Reputation: {user_rep['total_points']} points")
        output.append(f"  Contributions: {user_rep['contributions']}")

        # List user's groups
        user_groups = self.community_service.list_groups(self.current_user)
        output.append(f"  Groups: {len(user_groups)}")

        output.append("\n" + "=" * 60)

        return "\n".join(output)


def main():
    """Test CommunityCommandHandler"""
    handler = CommunityCommandHandler()

    print("\n" + "=" * 60)
    print("Testing COMMUNITY Commands")
    print("=" * 60 + "\n")

    print(handler.handle("HELP", [])[:500] + "...")
    print("\n" + "=" * 60 + "\n")
    print(handler.handle("STATUS", []))


if __name__ == "__main__":
    main()
