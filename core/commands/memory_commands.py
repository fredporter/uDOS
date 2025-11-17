"""
Memory Command Handler - v1.0.20
Unified interface for 4-Tier Memory System

Commands:
  MEMORY STATUS - Show all tier statistics
  MEMORY SEARCH <query> - Search across all accessible tiers
  MEMORY LIST <tier> [path] - List files in a tier
  MEMORY HEALTH - Verify tier integrity
  MEMORY TIERS - Display tier information

Author: uDOS Development Team
Version: 1.0.20
"""

from typing import Dict, List, Optional
from core.services.memory_manager import MemoryManager, MemoryTier


class MemoryCommandHandler:
    """Handler for MEMORY commands"""

    def __init__(self):
        """Initialize MemoryCommandHandler"""
        self.manager = MemoryManager()
        self.user_id = "owner"  # TODO: Get from session/auth system

    def handle(self, command: str, args: List[str]) -> str:
        """
        Route MEMORY commands to appropriate handlers

        Args:
            command: Subcommand (STATUS, SEARCH, etc.)
            args: Command arguments

        Returns:
            Formatted response string
        """
        if not command or command.upper() == "HELP":
            return self._help()

        command = command.upper()

        handlers = {
            'STATUS': self._status,
            'STATS': self._status,  # Alias
            'SEARCH': self._search,
            'FIND': self._search,   # Alias
            'LIST': self._list,
            'LS': self._list,       # Alias
            'HEALTH': self._health,
            'CHECK': self._health,  # Alias
            'TIERS': self._tiers,
            'INFO': self._tiers,    # Alias
        }

        handler = handlers.get(command)
        if handler:
            return handler(args)
        else:
            return f"❌ Unknown MEMORY command: {command}\n\nType 'MEMORY HELP' for usage."

    def _help(self) -> str:
        """Display MEMORY command help"""
        return """
🧠 MEMORY - 4-Tier Knowledge Management System

TIER OVERVIEW:
  🔒 Tier 1: PRIVATE   - Personal encrypted data (never shared)
  🤝 Tier 2: SHARED    - Explicitly shared with trusted contacts
  👥 Tier 3: GROUPS    - Community knowledge pools
  🌍 Tier 4: PUBLIC    - Global knowledge bank (read-only)

COMMANDS:
  MEMORY STATUS              Show statistics for all tiers
  MEMORY SEARCH <query>      Search across all accessible tiers
  MEMORY LIST <tier> [path]  List files in a specific tier
  MEMORY HEALTH              Verify integrity of all tiers
  MEMORY TIERS               Display tier information

TIER-SPECIFIC COMMANDS:
  PRIVATE <subcommand>       Manage Tier 1 (encrypted personal data)
  SHARED <subcommand>        Manage Tier 2 (shared knowledge)
  COMMUNITY <subcommand>     Manage Tier 3 (group knowledge)
  KNOWLEDGE <subcommand>     Access Tier 4 (global knowledge bank)

EXAMPLES:
  MEMORY STATUS              # View all tier statistics
  MEMORY SEARCH recipes      # Find "recipes" across all tiers
  MEMORY LIST private        # List private tier files
  MEMORY HEALTH              # Check tier integrity

For tier-specific help:
  PRIVATE HELP
  SHARED HELP
  COMMUNITY HELP
  KNOWLEDGE HELP
"""

    def _status(self, args: List[str]) -> str:
        """Display memory statistics for all tiers"""
        stats = self.manager.get_all_stats()

        output = ["🧠 Memory System Status"]
        output.append("=" * 60)
        output.append(f"\n📍 Base Path: {stats['base_path']}")
        output.append(f"📊 Total Files: {stats['total_files']}")
        output.append(f"💾 Total Size: {stats['total_size_mb']} MB")
        output.append(f"🕐 Timestamp: {stats['timestamp']}")

        output.append("\n📁 Tier Statistics:")
        output.append("-" * 60)

        tier_icons = {
            'private': '🔒',
            'shared': '🤝',
            'groups': '👥',
            'public': '🌍'
        }

        for tier_name, tier_stats in stats['tiers'].items():
            icon = tier_icons.get(tier_name, '📂')
            output.append(f"\n{icon} {tier_name.upper()}")
            output.append(f"  Files: {tier_stats['file_count']}")
            output.append(f"  Size: {tier_stats['total_size_mb']} MB")
            if tier_stats['last_modified']:
                output.append(f"  Last Modified: {tier_stats['last_modified']}")
            else:
                output.append(f"  Last Modified: Never")

        output.append("\n" + "=" * 60)
        output.append("\nℹ️  Use 'MEMORY LIST <tier>' to browse tier contents")

        return "\n".join(output)

    def _search(self, args: List[str]) -> str:
        """Search across all accessible tiers"""
        if not args:
            return "❌ Usage: MEMORY SEARCH <query>"

        query = " ".join(args)
        results = self.manager.search_all_tiers(query, self.user_id)

        output = [f"🔍 Searching for: '{query}'"]
        output.append("=" * 60)

        total_found = 0

        tier_icons = {
            'private': '🔒',
            'shared': '🤝',
            'groups': '👥',
            'public': '🌍'
        }

        for tier_name, tier_data in results.items():
            icon = tier_icons.get(tier_name, '📂')

            if not tier_data['access']:
                output.append(f"\n{icon} {tier_name.upper()}: 🔐 Access Denied")
                continue

            count = tier_data['count']
            total_found += count

            if count == 0:
                output.append(f"\n{icon} {tier_name.upper()}: No matches")
                continue

            output.append(f"\n{icon} {tier_name.upper()}: {count} matches")

            for result in tier_data['results'][:5]:  # Show first 5
                output.append(f"  📄 {result['path']}")
                output.append(f"     Size: {result['size']} bytes | Modified: {result['modified']}")

            if count > 5:
                output.append(f"  ... and {count - 5} more")

        output.append("\n" + "=" * 60)
        output.append(f"\n✅ Found {total_found} total matches")

        return "\n".join(output)

    def _list(self, args: List[str]) -> str:
        """List files in a specific tier"""
        if not args:
            return "❌ Usage: MEMORY LIST <tier> [path]\n   Tiers: private, shared, groups, public"

        tier_name = args[0].lower()
        path = args[1] if len(args) > 1 else ""

        # Parse tier
        try:
            tier = MemoryTier(tier_name)
        except ValueError:
            return f"❌ Unknown tier: {tier_name}\n   Valid tiers: private, shared, groups, public"

        # Check access
        if not self.manager.check_tier_access(tier, self.user_id):
            return f"🔐 Access denied to {tier_name} tier"

        # List files
        files = self.manager.list_files(tier, path)

        tier_icons = {
            'private': '🔒',
            'shared': '🤝',
            'groups': '👥',
            'public': '🌍'
        }

        icon = tier_icons.get(tier_name, '📂')

        output = [f"{icon} {tier_name.upper()} Tier"]
        if path:
            output.append(f"📁 Path: {path}")
        output.append("=" * 60)

        if not files:
            output.append("\n📭 No files found")
        else:
            output.append(f"\n📊 {len(files)} items\n")

            for file in files:
                if file['is_dir']:
                    output.append(f"📁 {file['name']}/")
                else:
                    size_kb = file['size'] / 1024
                    output.append(f"📄 {file['name']} ({size_kb:.1f} KB)")

        output.append("\n" + "=" * 60)

        return "\n".join(output)

    def _health(self, args: List[str]) -> str:
        """Verify integrity of all memory tiers"""
        health = self.manager.verify_all_tiers()

        output = ["🏥 Memory System Health Check"]
        output.append("=" * 60)
        output.append(f"\n🕐 Checked: {health['timestamp']}")

        status_icon = "✅" if health['overall_health'] else "⚠️"
        status_text = "HEALTHY" if health['overall_health'] else "ISSUES FOUND"
        output.append(f"{status_icon} Overall Status: {status_text}")

        output.append("\n📋 Tier Status:")
        output.append("-" * 60)

        tier_icons = {
            'private': '🔒',
            'shared': '🤝',
            'groups': '👥',
            'public': '🌍'
        }

        for tier_name, tier_health in health['tiers'].items():
            icon = tier_icons.get(tier_name, '📂')
            status = "✅ OK" if tier_health['healthy'] else f"⚠️  {len(tier_health['issues'])} issues"

            output.append(f"\n{icon} {tier_name.upper()}: {status}")

            if not tier_health['healthy']:
                for issue in tier_health['issues']:
                    output.append(f"   • {issue}")

        output.append("\n" + "=" * 60)

        if health['overall_health']:
            output.append("\n✅ All tiers are healthy and properly configured")
        else:
            output.append("\n⚠️  Some tiers need attention")

        return "\n".join(output)

    def _tiers(self, args: List[str]) -> str:
        """Display information about memory tiers"""
        return """
🧠 4-Tier Memory System

TIER 1: 🔒 PRIVATE (Personal Encrypted)
├─ Privacy: Maximum - Never shared
├─ Encryption: AES-256 automatic
├─ Access: Device owner only
├─ Sync: Never synced to other devices
└─ Use: Personal journals, credentials, private data

TIER 2: 🤝 SHARED (Explicitly Shared)
├─ Privacy: Selective - Explicit sharing only
├─ Encryption: Optional per-file
├─ Access: You choose specific people
├─ Sync: Local P2P only (no cloud)
└─ Use: Collaboration, shared projects, trusted contacts

TIER 3: 👥 GROUPS (Community Knowledge)
├─ Privacy: Community - Group members only
├─ Encryption: Transport encryption
├─ Access: All group members
├─ Sync: Distributed across member devices
└─ Use: Local communities, skill groups, barter networks

TIER 4: 🌍 PUBLIC (Global Knowledge Bank)
├─ Privacy: Public - Available to all
├─ Encryption: None (public knowledge)
├─ Access: Read-only for all users
├─ Sync: Distributed with uDOS releases
└─ Use: Survival guides, technical knowledge, skills

COMMANDS BY TIER:
  PRIVATE       - Manage Tier 1 encrypted storage
  SHARED        - Manage Tier 2 sharing
  COMMUNITY     - Manage Tier 3 groups
  KNOWLEDGE     - Access Tier 4 global bank

Cross-tier operations:
  MEMORY STATUS     - View all tier statistics
  MEMORY SEARCH     - Search across accessible tiers
  MEMORY LIST       - Browse tier contents
  MEMORY HEALTH     - Verify tier integrity
"""


def main():
    """Test MemoryCommandHandler"""
    handler = MemoryCommandHandler()

    print("\n" + "=" * 60)
    print("Testing MEMORY Commands")
    print("=" * 60 + "\n")

    # Test commands
    commands = [
        ("HELP", []),
        ("STATUS", []),
        ("HEALTH", []),
        ("TIERS", []),
        ("LIST", ["private"]),
    ]

    for cmd, args in commands:
        print(f"\n>>> MEMORY {cmd} {' '.join(args)}")
        print("-" * 60)
        result = handler.handle(cmd, args)
        print(result)
        print()


if __name__ == "__main__":
    main()
