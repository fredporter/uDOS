"""
MIGRATE Command Handler - Trigger and manage SQLite migration
Part of Phase 8: Location data SQLite migration

Usage:
  MIGRATE                        # Show migration status
  MIGRATE check                  # Check if migration is needed
  MIGRATE perform                # Perform migration (with backup)
  MIGRATE perform --no-backup    # Perform migration without backup
  MIGRATE status                 # Show detailed status
"""

from typing import Dict, Any
from pathlib import Path

from core.commands.base import BaseCommandHandler
from core.services.logging_manager import get_logger
from core.services.location_migration_service import LocationMigrator

logger = get_logger("migrate-handler")


class MigrateHandler(BaseCommandHandler):
    """Handler for location data migration commands."""

    def __init__(self):
        super().__init__(
            command_name="MIGRATE",
            description="Manage location data SQLite migration",
            usage_examples=[
                "MIGRATE",
                "MIGRATE check",
                "MIGRATE perform",
                "MIGRATE perform --no-backup",
                "MIGRATE status",
            ],
        )

        # Initialize migrator with default path
        project_root = Path(__file__).parent.parent.parent
        data_dir = project_root / "memory" / "bank" / "locations"
        self.migrator = LocationMigrator(data_dir)

        logger.debug("[LOCAL] MigrateHandler initialized")

    def execute(self, args: list, context: Dict = None) -> str:
        """
        Execute MIGRATE command.

        Args:
            args: Command arguments
            context: Execution context (optional)

        Returns:
            Command output as string
        """
        if not args:
            # No args: show help and status
            return self._show_help_and_status()

        subcommand = args[0].lower()

        if subcommand == "help":
            return self._show_help()
        elif subcommand == "check":
            return self._check_migration()
        elif subcommand == "status":
            return self._show_detailed_status()
        elif subcommand == "perform":
            backup = "--no-backup" not in args
            return self._perform_migration(backup=backup)
        else:
            return f"❌ Unknown subcommand: {subcommand}\n\n{self._show_help()}"

    def _show_help(self) -> str:
        """Show command help."""
        return """
╔════════════════════════════════════════════════════════════════╗
║                    MIGRATE Command Help                        ║
╚════════════════════════════════════════════════════════════════╝

Phase 8: SQLite Migration for Location Data

When locations.json exceeds 500KB or 1000 records, uDOS automatically
migrates to SQLite for better performance. Use this command to check
status and manually trigger migration.

USAGE:
  MIGRATE                        Show status
  MIGRATE check                  Check if migration is needed
  MIGRATE perform                Perform migration (with backup)
  MIGRATE perform --no-backup    Perform migration without backup
  MIGRATE status                 Show detailed status

MIGRATION THRESHOLDS:
  • File size: 500KB
  • Record count: 1000 locations

WHAT GETS MIGRATED:
  • locations.json → locations.db
  • timezones.json → timezones table
  • user-locations.json → user_additions table
  • Connections and tiles data

BACKUP:
  By default, JSON files are backed up to memory/bank/locations/backups/
  before migration. Use --no-backup to skip.

EXAMPLES:
  MIGRATE                        # Quick status check
  MIGRATE check                  # Detailed migration assessment
  MIGRATE perform                # Migrate with backup
"""

    def _show_help_and_status(self) -> str:
        """Show help and current status."""
        status = self.migrator.get_migration_status()

        output = [
            "╔════════════════════════════════════════════════════════════════╗",
            "║              Location Data Migration Status                    ║",
            "╚════════════════════════════════════════════════════════════════╝",
            "",
        ]

        # Current backend
        if status["db_exists"]:
            output.append("✅ SQLite Backend: ACTIVE")
            output.append(f"   Database: {self.migrator.db_path.name}")
            output.append(f"   Locations: {status['db_stats'].get('locations', 0)}")
            output.append(f"   Timezones: {status['db_stats'].get('timezones', 0)}")
            output.append(f"   Connections: {status['db_stats'].get('connections', 0)}")
        else:
            output.append("📄 JSON Backend: ACTIVE")
            output.append(f"   File: {self.migrator.json_path.name}")
            output.append(f"   Size: {status['file_size_kb']}KB")
            output.append(f"   Records: {status['record_count']}")

        output.append("")

        # Migration status
        if status["should_migrate"]:
            output.append("⚠️  MIGRATION RECOMMENDED")
            output.append(f"   Reason: {status['reason']}")
            output.append("")
            output.append("Run: MIGRATE perform")
        else:
            output.append("✅ No migration needed")
            output.append(f"   {status['reason']}")

        output.append("")
        output.append("Type 'MIGRATE help' for more options")

        return "\n".join(output)

    def _check_migration(self) -> str:
        """Check if migration is needed."""
        should_migrate, reason = self.migrator.should_migrate()
        status = self.migrator.get_migration_status()

        output = [
            "╔════════════════════════════════════════════════════════════════╗",
            "║              Migration Assessment                              ║",
            "╚════════════════════════════════════════════════════════════════╝",
            "",
        ]

        # Thresholds
        output.append("Migration Thresholds:")
        output.append(f"  • File size: {LocationMigrator.SIZE_THRESHOLD_KB}KB")
        output.append(f"  • Record count: {LocationMigrator.RECORD_THRESHOLD}")
        output.append("")

        # Current stats
        output.append("Current Data:")
        output.append(f"  • File size: {status['file_size_kb']}KB")
        output.append(f"  • Record count: {status['record_count']}")
        output.append("")

        # Decision
        if should_migrate:
            output.append("⚠️  MIGRATION RECOMMENDED")
            output.append(f"   {reason}")
            output.append("")
            output.append("Run: MIGRATE perform")
        else:
            output.append("✅ No migration needed")
            output.append(f"   {reason}")

        return "\n".join(output)

    def _show_detailed_status(self) -> str:
        """Show detailed migration status."""
        status = self.migrator.get_migration_status()

        output = [
            "╔════════════════════════════════════════════════════════════════╗",
            "║              Detailed Migration Status                         ║",
            "╚════════════════════════════════════════════════════════════════╝",
            "",
        ]

        # File status
        output.append("JSON Backend:")
        output.append(f"  Path: {self.migrator.json_path}")
        output.append(f"  Exists: {'Yes' if status['json_exists'] else 'No'}")
        if status["json_exists"]:
            output.append(f"  Size: {status['file_size_kb']}KB")
            output.append(f"  Records: {status['record_count']}")
        output.append("")

        # Database status
        output.append("SQLite Backend:")
        output.append(f"  Path: {self.migrator.db_path}")
        output.append(f"  Exists: {'Yes' if status['db_exists'] else 'No'}")
        if status["db_exists"]:
            output.append(f"  Locations: {status['db_stats'].get('locations', 0)}")
            output.append(f"  Timezones: {status['db_stats'].get('timezones', 0)}")
            output.append(f"  Connections: {status['db_stats'].get('connections', 0)}")
            output.append(
                f"  User Additions: {status['db_stats'].get('user_additions', 0)}"
            )
        output.append("")

        # Migration assessment
        output.append("Migration Assessment:")
        output.append(
            f"  Should migrate: {'Yes' if status['should_migrate'] else 'No'}"
        )
        output.append(f"  Reason: {status['reason']}")

        return "\n".join(output)

    def _perform_migration(self, backup: bool = True) -> str:
        """
        Perform migration.

        Args:
            backup: Create backup before migration
        """
        logger.info("[LOCAL] Starting manual migration...")

        output = [
            "╔════════════════════════════════════════════════════════════════╗",
            "║              Location Data Migration                           ║",
            "╚════════════════════════════════════════════════════════════════╝",
            "",
        ]

        # Check if already migrated
        if self.migrator.db_path.exists():
            output.append("⚠️  SQLite database already exists!")
            output.append(f"   {self.migrator.db_path}")
            output.append("")
            output.append("Migration already completed. No action needed.")
            return "\n".join(output)

        # Check if should migrate
        should_migrate, reason = self.migrator.should_migrate()
        if not should_migrate:
            output.append("ℹ️  Migration not recommended")
            output.append(f"   {reason}")
            output.append("")
            output.append("To force migration anyway, manual intervention required.")
            return "\n".join(output)

        # Perform migration
        output.append("🚀 Starting migration...")
        output.append(f"   Backup: {'Enabled' if backup else 'Disabled'}")
        output.append("")

        stats = self.migrator.perform_migration(backup=backup)

        if stats["success"]:
            output.append("✅ Migration completed successfully!")
            output.append("")
            output.append("Results:")
            output.append(f"  • Locations migrated: {stats['locations_migrated']}")
            output.append(f"  • Timezones migrated: {stats['timezones_migrated']}")
            output.append(f"  • Connections created: {stats['connections_migrated']}")
            output.append(
                f"  • User locations migrated: {stats['user_locations_migrated']}"
            )
            output.append(
                f"  • Backup created: {'Yes' if stats['backup_created'] else 'No'}"
            )
            output.append("")
            output.append(f"Database: {self.migrator.db_path}")

            if backup:
                output.append("")
                output.append("Original JSON files backed up to:")
                output.append(f"  {self.migrator.data_dir / 'backups'}")
        else:
            output.append("❌ Migration failed!")
            output.append(f"   Error: {stats.get('error', 'Unknown error')}")
            output.append("")
            output.append("Check logs for details:")
            output.append("  memory/logs/session-commands-*.log")

        return "\n".join(output)


def main():
    """Test handler."""
    handler = MigrateHandler()

    # Test commands
    print(handler.execute([]))
    print("\n" + "=" * 60 + "\n")
    print(handler.execute(["check"]))


if __name__ == "__main__":
    main()
