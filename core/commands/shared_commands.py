"""
Shared Command Handler - v1.0.20
Tier 2: Explicitly shared knowledge

Commands:
  SHARED GRANT <file> <user> [permission] [expires]
  SHARED REVOKE <file> <user>
  SHARED LIST [user]
  SHARED SHOW <file>
  SHARED LOGS [file] [user]
  SHARED STATUS

Author: uDOS Development Team
Version: 1.0.20
"""

from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta
from core.services.sharing_service import SharingService, SharePermission
from core.services.memory_manager import MemoryManager, MemoryTier


class SharedCommandHandler:
    """Handler for SHARED (Tier 2) commands"""

    def __init__(self):
        """Initialize SharedCommandHandler"""
        self.memory_manager = MemoryManager()
        self.sharing_service = SharingService()
        self.shared_path = self.memory_manager.get_tier_path(MemoryTier.SHARED)
        self.current_user = "owner"  # TODO: Get from session/auth

    def handle(self, command: str, args: List[str]) -> str:
        """
        Route SHARED commands to appropriate handlers

        Args:
            command: Subcommand (GRANT, REVOKE, etc.)
            args: Command arguments

        Returns:
            Formatted response string
        """
        if not command or command.upper() == "HELP":
            return self._help()

        command = command.upper()

        handlers = {
            'GRANT': self._grant,
            'SHARE': self._grant,     # Alias
            'REVOKE': self._revoke,
            'UNSHARE': self._revoke,  # Alias
            'LIST': self._list,
            'LS': self._list,         # Alias
            'SHOW': self._show,
            'INFO': self._show,       # Alias
            'LOGS': self._logs,
            'HISTORY': self._logs,    # Alias
            'STATUS': self._status,
            'STATS': self._status,    # Alias
            'CLEANUP': self._cleanup,
        }

        handler = handlers.get(command)
        if handler:
            return handler(args)
        else:
            return f"❌ Unknown SHARED command: {command}\n\nType 'SHARED HELP' for usage."

    def _help(self) -> str:
        """Display SHARED command help"""
        return """
🤝 SHARED - Tier 2: Explicitly Shared Knowledge

SHARING MODEL:
  • Selective - Choose exactly what and with whom
  • Permission levels - READ, EDIT, FULL control
  • Revocable - Unshare at any time
  • Time-limited - Set expiration dates
  • Logged - Complete audit trail
  • Local P2P - No cloud, device-to-device only

COMMANDS:
  SHARED GRANT <file> <user> [perm] [exp]    Grant access to file
  SHARED REVOKE <file> <user>                Revoke access
  SHARED LIST [user]                         List shared files
  SHARED SHOW <file>                         Show file permissions
  SHARED LOGS [file] [user]                  View access logs
  SHARED STATUS                              Sharing statistics
  SHARED CLEANUP                             Remove expired shares

PERMISSION LEVELS:
  READ  - View file only
  EDIT  - View and modify file
  FULL  - View, modify, and manage sharing

EXAMPLES:
  # Grant read access
  SHARED GRANT project.md alice@device1 READ

  # Grant edit access for 7 days
  SHARED GRANT notes.md bob@device2 EDIT 7d

  # Revoke access
  SHARED REVOKE project.md alice@device1

  # List all shared files
  SHARED LIST

  # Show who has access to a file
  SHARED SHOW project.md

  # View access logs
  SHARED LOGS project.md

TIME FORMATS:
  7d   - 7 days
  2w   - 2 weeks
  1m   - 1 month
  24h  - 24 hours

WHAT TO SHARE:
  ✅ Project collaboration data
  ✅ Shared task lists and workflows
  ✅ Community event planning
  ✅ Barter offers and requests
  ✅ Teaching materials
  ✅ Group adventure scripts

SECURITY NOTES:
  • Only share with trusted contacts
  • Revoke access when no longer needed
  • Review logs regularly
  • Set expiration dates for temporary shares
  • Local network only - no cloud storage
"""

    def _parse_expiration(self, exp_str: str) -> Optional[datetime]:
        """Parse expiration string (e.g., '7d', '2w', '1m')"""
        if not exp_str:
            return None

        try:
            amount = int(exp_str[:-1])
            unit = exp_str[-1].lower()

            if unit == 'h':
                delta = timedelta(hours=amount)
            elif unit == 'd':
                delta = timedelta(days=amount)
            elif unit == 'w':
                delta = timedelta(weeks=amount)
            elif unit == 'm':
                delta = timedelta(days=amount * 30)
            else:
                return None

            return datetime.now() + delta
        except (ValueError, IndexError):
            return None

    def _grant(self, args: List[str]) -> str:
        """Grant access to a file"""
        if len(args) < 2:
            return "❌ Usage: SHARED GRANT <file> <user> [permission] [expiration]"

        filename = args[0]
        user = args[1]
        permission = SharePermission.READ  # Default
        expires = None

        # Parse optional permission
        if len(args) >= 3:
            perm_str = args[2].upper()
            try:
                permission = SharePermission(perm_str.lower())
            except ValueError:
                return f"❌ Invalid permission: {perm_str}\n   Valid: READ, EDIT, FULL"

        # Parse optional expiration
        if len(args) >= 4:
            expires = self._parse_expiration(args[3])
            if expires is None:
                return f"❌ Invalid expiration format: {args[3]}\n   Use: 7d, 2w, 1m, 24h"

        # Check if file exists
        file_path = self.shared_path / filename
        if not file_path.exists():
            return f"❌ File not found in shared tier: {filename}"

        # Grant access
        success = self.sharing_service.grant_access(
            filename, user, permission, expires
        )

        if not success:
            return "❌ Failed to grant access"

        # Format response
        output = [f"✅ Access granted to {user}"]
        output.append("")
        output.append(f"📄 File: {filename}")
        output.append(f"👤 User: {user}")
        output.append(f"🔑 Permission: {permission.value.upper()}")

        if expires:
            output.append(f"⏰ Expires: {expires.strftime('%Y-%m-%d %H:%M')}")
        else:
            output.append(f"⏰ Expires: Never")

        output.append("")
        output.append(f"The user can now access this file with {permission.value} permissions.")

        return "\n".join(output)

    def _revoke(self, args: List[str]) -> str:
        """Revoke access to a file"""
        if len(args) < 2:
            return "❌ Usage: SHARED REVOKE <file> <user>"

        filename = args[0]
        user = args[1]

        # Revoke access
        success = self.sharing_service.revoke_access(filename, user)

        if not success:
            return f"❌ No access to revoke for {user} on {filename}"

        return f"""
✅ Access revoked

📄 File: {filename}
👤 User: {user}

The user no longer has access to this file.
"""

    def _list(self, args: List[str]) -> str:
        """List shared files"""
        user = args[0] if args else self.current_user

        # Get files for user
        files = self.sharing_service.get_user_files(user)

        output = ["🤝 Shared Files"]
        if user != self.current_user:
            output.append(f"👤 User: {user}")
        output.append("=" * 60)

        if not files:
            output.append("\n📭 No shared files")
        else:
            output.append(f"\n📊 {len(files)} shared files\n")

            for filename in files:
                perms = self.sharing_service.get_file_permissions(filename)

                # Count users with access
                user_count = len(perms['permissions'])

                # Check if file exists
                file_path = self.shared_path / filename
                if file_path.exists():
                    size_kb = file_path.stat().st_size / 1024
                    output.append(f"📄 {filename} ({size_kb:.1f} KB)")
                else:
                    output.append(f"📄 {filename} (file missing)")

                output.append(f"   Shared with {user_count} user(s)")

        output.append("\n" + "=" * 60)
        output.append("\nℹ️  Use 'SHARED SHOW <file>' for details")

        return "\n".join(output)

    def _show(self, args: List[str]) -> str:
        """Show file permissions"""
        if not args:
            return "❌ Usage: SHARED SHOW <file>"

        filename = args[0]
        perms = self.sharing_service.get_file_permissions(filename)

        if not perms['permissions'] and 'owner' not in perms:
            return f"❌ File not found or not shared: {filename}"

        output = [f"🤝 Sharing Details: {filename}"]
        output.append("=" * 60)

        # Owner
        output.append(f"\n👑 Owner: {perms.get('owner', 'unknown')}")
        if 'created' in perms:
            output.append(f"📅 Created: {perms['created']}")

        # Permissions
        if perms['permissions']:
            output.append(f"\n👥 Shared with {len(perms['permissions'])} user(s):\n")

            for user, perm in perms['permissions'].items():
                level = perm['level'].upper()
                granted = perm['granted']

                output.append(f"  👤 {user}")
                output.append(f"     Permission: {level}")
                output.append(f"     Granted: {granted}")

                if perm['expires']:
                    expires = datetime.fromisoformat(perm['expires'])
                    now = datetime.now()

                    if now > expires:
                        output.append(f"     Expires: {perm['expires']} ⚠️  EXPIRED")
                    else:
                        time_left = expires - now
                        days_left = time_left.days
                        output.append(f"     Expires: {perm['expires']} ({days_left}d left)")
                else:
                    output.append(f"     Expires: Never")

                output.append("")
        else:
            output.append(f"\n📭 Not currently shared with anyone")

        output.append("=" * 60)

        return "\n".join(output)

    def _logs(self, args: List[str]) -> str:
        """View access logs"""
        file_filter = args[0] if args else None
        user_filter = args[1] if len(args) > 1 else None

        logs = self.sharing_service.get_access_logs(
            file_path=file_filter,
            user=user_filter,
            limit=50
        )

        output = ["📋 Access Logs"]
        if file_filter:
            output.append(f"📄 File: {file_filter}")
        if user_filter:
            output.append(f"👤 User: {user_filter}")
        output.append("=" * 60)

        if not logs:
            output.append("\n📭 No access logs found")
        else:
            output.append(f"\n📊 Showing {len(logs)} recent events\n")

            for log in logs:
                timestamp = log['timestamp'].split('T')[0] + ' ' + log['timestamp'].split('T')[1][:8]
                action = log['action'].ljust(8)
                user = log['user'].ljust(20)
                file = log['file']

                output.append(f"{timestamp} | {action} | {user} | {file}")
                if log['details']:
                    output.append(f"  └─ {log['details']}")

        output.append("\n" + "=" * 60)

        return "\n".join(output)

    def _status(self, args: List[str]) -> str:
        """Show sharing statistics"""
        stats = self.sharing_service.get_stats()
        tier_stats = self.memory_manager.get_tier_stats(MemoryTier.SHARED)

        output = ["🤝 Shared Tier Status"]
        output.append("=" * 60)

        # File statistics
        output.append(f"\n📊 Statistics:")
        output.append(f"  Total Files: {tier_stats['file_count']}")
        output.append(f"  Total Size: {tier_stats['total_size_mb']} MB")
        if tier_stats['last_modified']:
            output.append(f"  Last Modified: {tier_stats['last_modified']}")

        # Sharing statistics
        output.append(f"\n🔗 Sharing:")
        output.append(f"  Files Shared: {stats['total_files']}")
        output.append(f"  Total Permissions: {stats['total_permissions']}")

        output.append(f"\n🔑 By Permission Level:")
        for level, count in stats['by_level'].items():
            if count > 0:
                output.append(f"  {level.upper()}: {count}")

        if stats['expired'] > 0:
            output.append(f"\n⚠️  Expired Permissions: {stats['expired']}")
            output.append(f"   Use 'SHARED CLEANUP' to remove")

        output.append("\n" + "=" * 60)

        return "\n".join(output)

    def _cleanup(self, args: List[str]) -> str:
        """Remove expired permissions"""
        removed = self.sharing_service.cleanup_expired()

        if removed == 0:
            return "✅ No expired permissions to clean up"

        return f"""
✅ Cleanup complete

🗑️  Removed {removed} expired permission(s)

All active permissions are now up to date.
"""


def main():
    """Test SharedCommandHandler"""
    handler = SharedCommandHandler()

    print("\n" + "=" * 60)
    print("Testing SHARED Commands")
    print("=" * 60 + "\n")

    # Test commands
    print(handler.handle("HELP", [])[:500] + "...")
    print("\n" + "=" * 60 + "\n")
    print(handler.handle("STATUS", []))


if __name__ == "__main__":
    main()
