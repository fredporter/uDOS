"""
MIGRATE command handler - Manage SQLite migration for location data.

Provides commands to check migration status, trigger migration, and manage
the transition from JSON to SQLite for location data.

Commands:
  MIGRATE              - Show current status and migration options
  MIGRATE check        - Check if migration is needed
  MIGRATE status       - Show detailed migration status
  MIGRATE perform      - Perform migration (with backup)
  MIGRATE perform --no-backup - Perform migration without backup
  MIGRATE rollback     - Rollback to JSON backend (delete .db)
"""

from typing import Dict, List, Optional
from .base import BaseCommandHandler
from core.services.location_migration_service import LocationMigrator
from core.services.logging_api import get_logger

logger = get_logger("migrate_handler")


class MigrateHandler(BaseCommandHandler):
    """Handler for MIGRATE command - Manage SQLite migration."""

    def handle(self, command: str, params: List[str], grid, parser) -> Dict:
        """
        Handle MIGRATE command.

        Args:
            command: "MIGRATE"
            params: [subcommand] [options]
                    - (empty) -> show status and options
                    - check -> check if migration needed
                    - status -> show detailed status
                    - perform -> perform migration
                    - perform --no-backup -> migrate without backup
                    - rollback -> rollback to JSON
            grid: TUI grid
            parser: Command parser

        Returns:
            Dict with status and migration information
        """
        try:
            migrator = LocationMigrator()
        except Exception as e:
            logger.error(f"[LOCAL] Failed to initialize LocationMigrator: {e}")
            return {
                "status": "error",
                "message": f"Failed to initialize migration service: {e}",
            }

        # Default: show status
        if not params:
            return self._show_status(migrator)

        subcommand = params[0].lower()

        if subcommand == "check":
            return self._check_migration(migrator)
        elif subcommand == "status":
            return self._show_detailed_status(migrator)
        elif subcommand == "perform":
            backup = "--no-backup" not in params
            return self._perform_migration(migrator, backup)
        elif subcommand == "rollback":
            return self._rollback_migration(migrator)
        else:
            return {
                "status": "error",
                "message": f"Unknown MIGRATE subcommand: {subcommand}",
                "usage": "MIGRATE [check|status|perform|rollback]",
            }

    def _show_status(self, migrator: LocationMigrator) -> Dict:
        """Show current migration status."""
        status = migrator.get_migration_status()

        # Format output
        lines = [
            "━" * 60,
            "Location Data Migration Status",
            "━" * 60,
            "",
            f"Backend:               {status['backend']}",
            f"Should migrate:        {'Yes' if status['should_migrate'] else 'No'}",
            f"Reason:                {status['reason']}",
            "",
        ]

        if status["json_exists"]:
            lines.extend([
                f"JSON File:             {status['json_size_kb']:.1f} KB ({status['json_records']} records)",
                f"  Size threshold:      {status['size_threshold_kb']} KB",
                f"  Record threshold:    {status['record_threshold']} records",
            ])

        if status["db_exists"]:
            lines.extend([
                f"SQLite Database:       {status['db_records']} records",
            ])

        lines.extend([
            "",
            "Available commands:",
            "  MIGRATE check        - Check if migration is needed",
            "  MIGRATE status       - Show this detailed status",
            "  MIGRATE perform      - Perform migration (with backup)",
            "  MIGRATE rollback     - Rollback to JSON backend",
        ])

        output = "\n".join(lines)

        logger.info(f"[LOCAL] Migration status checked: {status['backend']}")

        return {
            "status": "success",
            "message": "Migration status displayed",
            "output": output,
            **status,
        }

    def _check_migration(self, migrator: LocationMigrator) -> Dict:
        """Check if migration is needed."""
        should_migrate, reason = migrator.should_migrate()

        output = "\n".join([
            "━" * 60,
            "Migration Check",
            "━" * 60,
            "",
            f"Migration needed:      {'YES' if should_migrate else 'NO'}",
            f"Reason:                {reason}",
            "",
        ])

        if should_migrate:
            output += "To perform migration: MIGRATE perform\n"

        logger.info(f"[LOCAL] Migration check: {should_migrate} - {reason}")

        return {
            "status": "success",
            "message": "Migration check completed",
            "output": output,
            "should_migrate": should_migrate,
            "reason": reason,
        }

    def _show_detailed_status(self, migrator: LocationMigrator) -> Dict:
        """Show detailed migration status."""
        status = migrator.get_migration_status()

        lines = [
            "━" * 60,
            "Detailed Migration Status",
            "━" * 60,
            "",
            "Current Backend:",
            f"  {status['backend']}",
            "",
            "JSON Backend (locations.json):",
            f"  Exists:         {status['json_exists']}",
            f"  Size:           {status['json_size_kb']:.1f} KB",
            f"  Records:        {status['json_records']}",
            "",
            "SQLite Backend (locations.db):",
            f"  Exists:         {status['db_exists']}",
            f"  Records:        {status['db_records']}",
            "",
            "Migration Configuration:",
            f"  Size threshold: {status['size_threshold_kb']} KB",
            f"  Record threshold: {status['record_threshold']} records",
            "",
            "Migration Status:",
            f"  Needed:         {'Yes' if status['should_migrate'] else 'No'}",
            f"  Reason:         {status['reason']}",
            "",
        ]

        output = "\n".join(lines)

        return {
            "status": "success",
            "message": "Detailed status displayed",
            "output": output,
            **status,
        }

    def _perform_migration(self, migrator: LocationMigrator, backup: bool = True) -> Dict:
        """Perform migration from JSON to SQLite."""
        # Check if migration is needed
        should_migrate, reason = migrator.should_migrate()
        if not should_migrate:
            return {
                "status": "cancelled",
                "message": f"Migration not needed: {reason}",
            }

        # Perform migration
        lines = [
            "━" * 60,
            "Performing Location Data Migration",
            "━" * 60,
            "",
        ]

        if backup:
            lines.append("Creating backup... ")

        result = migrator.perform_migration(backup=backup)

        if result["success"]:
            lines.extend([
                f"✅ Migration completed successfully!",
                "",
                f"Locations migrated:    {result['locations_migrated']}",
                f"Timezones migrated:    {result['timezones_migrated']}",
                f"Connections migrated:  {result['connections_migrated']}",
                f"Tiles migrated:        {result['tiles_migrated']}",
                f"User additions:        {result['user_additions_migrated']}",
                "",
                "JSON backend is preserved for rollback.",
                "To rollback: MIGRATE rollback",
            ])
            logger.info(f"[LOCAL] Migration performed successfully: {result['locations_migrated']} locations")
        else:
            lines.extend([
                f"❌ Migration failed!",
                f"Error: {result['message']}",
            ])
            logger.error(f"[LOCAL] Migration failed: {result['message']}")

        output = "\n".join(lines)

        return {
            "status": "success" if result["success"] else "error",
            "message": result["message"],
            "output": output,
            **result,
        }

    def _rollback_migration(self, migrator: LocationMigrator) -> Dict:
        """Rollback to JSON backend by deleting SQLite database."""
        status = migrator.get_migration_status()

        if not status["db_exists"]:
            return {
                "status": "cancelled",
                "message": "SQLite database does not exist. Nothing to rollback.",
            }

        # Delete database
        success = migrator.delete_database()

        if success:
            output = "\n".join([
                "━" * 60,
                "Migration Rollback",
                "━" * 60,
                "",
                "✅ Rollback completed successfully!",
                "",
                "SQLite database has been deleted.",
                "JSON backend is now active.",
                "",
                "To migrate again: MIGRATE perform",
            ])
            logger.info("[LOCAL] Migration rollback completed")
        else:
            output = "Failed to delete SQLite database."
            logger.error("[LOCAL] Migration rollback failed")

        return {
            "status": "success" if success else "error",
            "message": "Rollback completed" if success else "Rollback failed",
            "output": output,
        }
