"""
Empire Server TUI - Text User Interface

Simple interactive terminal interface for Empire CRM.
"""

import sys
from pathlib import Path

# Add parent repo root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dev.empire.empire import Empire


class EmpireServerTUI:
    """Terminal UI for Empire CRM."""

    def __init__(self):
        """Initialize Empire TUI."""
        self.empire = Empire()
        self.running = True

    def print_header(self):
        """Print welcome header."""
        print("\n" + "=" * 70)
        print("🏛️  EMPIRE SERVER - Business Intelligence & CRM")
        print("=" * 70)
        print("\nCommands:")
        print("  status   - Show system status")
        print("  contacts - List contacts")
        print("  help     - Show help")
        print("  exit     - Exit program\n")

    def cmd_status(self):
        """Show system status."""
        print("\n📊 Empire Server Status:")
        print(f"   Database: {self.empire.db.db_path}")
        print(f"   Version: 1.0.1")
        print(f"   Status: ✓ Online\n")

    def cmd_contacts(self):
        """Show contacts."""
        print("\n👥 Contacts:")
        try:
            # Try to query directly from database
            cursor = self.empire.db.conn.cursor()
            cursor.execute(
                "SELECT person_id, full_name, primary_email FROM people LIMIT 10"
            )
            rows = cursor.fetchall()

            if rows:
                for row in rows:
                    name = dict(row).get("full_name", "Unknown")
                    email = dict(row).get("primary_email", "")
                    print(f"   • {name} ({email})")
            else:
                print("   (no contacts yet)\n")
        except Exception as e:
            print(f"   Note: {e.__class__.__name__}\n")

    def cmd_help(self):
        """Show help."""
        print("\n" + "=" * 70)
        print("EMPIRE SERVER - Help")
        print("=" * 70)
        print(
            """
Features:
  • Contact Management (local SQLite)
  • HubSpot CRM Sync (bidirectional)
  • Gmail contact extraction
  • Google Business Profile integration
  • Entity resolution and enrichment

Commands:
  status   - Show system status
  contacts - List contacts
  help     - Show this help
  exit     - Exit program

Database: memory/bank/user/contacts.db
"""
        )

    def run(self):
        """Run interactive TUI."""
        self.print_header()

        while self.running:
            try:
                cmd = input("empire> ").strip().lower()

                if not cmd:
                    continue

                if cmd == "exit" or cmd == "quit":
                    self.running = False
                    print("\n✓ Empire Server stopped\n")

                elif cmd == "status":
                    self.cmd_status()

                elif cmd == "contacts":
                    self.cmd_contacts()

                elif cmd == "help" or cmd == "?":
                    self.cmd_help()

                else:
                    print(f"Unknown command: {cmd}\n")

            except KeyboardInterrupt:
                print("\n\n✓ Empire Server stopped\n")
                self.running = False
            except Exception as e:
                print(f"Error: {e}\n")


if __name__ == "__main__":
    tui = EmpireServerTUI()
    tui.run()
