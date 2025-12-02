"""
Checklist Command Handler

Interactive checklist management with progress tracking, completion status,
and guide integration. Supports JSON-based checklists with nested items.

Commands:
    CHECKLIST LIST [category]
    CHECKLIST LOAD <id>
    CHECKLIST COMPLETE <id> <item_id>
    CHECKLIST UNCOMPLETE <id> <item_id>
    CHECKLIST STATUS <id>
    CHECKLIST PROGRESS [category]
    CHECKLIST RESET <id>

Author: uDOS Team
Version: 1.1.14
"""

from core.services.checklist_manager import ChecklistManager
from core.theme_manager import get_color


class ChecklistHandler:
    """Handle checklist-related commands."""

    def __init__(self, config=None):
        """Initialize handler with config."""
        self.config = config
        self.manager = ChecklistManager(config)

    def handle(self, command: str, args: list) -> str:
        """Route checklist commands to appropriate handlers.

        Args:
            command: The command verb (after CHECKLIST)
            args: Command arguments

        Returns:
            Formatted response string
        """
        command = command.upper()

        if command == "LIST":
            return self.list_checklists(args)
        elif command == "LOAD":
            return self.load_checklist(args)
        elif command == "COMPLETE":
            return self.complete_item(args)
        elif command == "UNCOMPLETE":
            return self.uncomplete_item(args)
        elif command == "STATUS":
            return self.show_status(args)
        elif command == "PROGRESS":
            return self.show_progress(args)
        elif command == "RESET":
            return self.reset_progress(args)
        else:
            return self.show_help()

    def list_checklists(self, args: list) -> str:
        """List available checklists.

        Args:
            args: Optional category filter

        Returns:
            Formatted list of checklists
        """
        category = args[0] if args else None
        checklists = self.manager.list_checklists(category)

        if not checklists:
            msg = "No checklists found"
            if category:
                msg += f" in category '{category}'"
            return f"{get_color('WARNING')}{msg}{get_color('ENDC')}"

        output = [f"\n{get_color('HEADER')}Available Checklists{get_color('ENDC')}"]
        if category:
            output[0] += f" ({category})"
        output.append("=" * 60)

        # Group by category
        by_category = {}
        for checklist in checklists:
            cat = checklist["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(checklist)

        for cat in sorted(by_category.keys()):
            output.append(f"\n{get_color('BOLD')}{cat.upper()}{get_color('ENDC')}")
            for checklist in by_category[cat]:
                # Progress indicator
                progress = checklist["progress"]
                if progress["total"] > 0:
                    pct = progress["percentage"]
                    bar = self._make_progress_bar(pct, width=20)
                    status = f"{bar} {pct}%"
                else:
                    status = "Not started"

                output.append(
                    f"  {get_color('OKBLUE')}{checklist['id']:<30}{get_color('ENDC')} "
                    f"{checklist['title']:<30} {status}"
                )

        output.append("\n" + "=" * 60)
        output.append(f"Total: {len(checklists)} checklist(s)")
        output.append(f"\nUse: {get_color('OKGREEN')}CHECKLIST LOAD <id>{get_color('ENDC')} to view details")

        return "\n".join(output)

    def load_checklist(self, args: list) -> str:
        """Load and display a checklist.

        Args:
            args: [checklist_id]

        Returns:
            Formatted checklist with completion status
        """
        if not args:
            return f"{get_color('FAIL')}Error: Checklist ID required{get_color('ENDC')}\nUsage: CHECKLIST LOAD <id>"

        checklist_id = args[0]
        checklist = self.manager.load_checklist(checklist_id)

        if not checklist:
            return f"{get_color('FAIL')}Error: Checklist '{checklist_id}' not found{get_color('ENDC')}"

        progress = self.manager.get_progress(checklist_id)

        output = [
            f"\n{get_color('HEADER')}{checklist['title']}{get_color('ENDC')}",
            "=" * 60,
            f"ID: {checklist['id']}",
            f"Category: {checklist.get('category', 'unknown')}",
        ]

        if checklist.get("description"):
            output.append(f"Description: {checklist['description']}")

        if checklist.get("difficulty"):
            output.append(f"Difficulty: {checklist['difficulty']}")

        if checklist.get("estimated_time"):
            output.append(f"Est. Time: {checklist['estimated_time']}")

        # Progress
        if progress["total"] > 0:
            pct = progress["percentage"]
            bar = self._make_progress_bar(pct, width=40)
            output.append(f"\nProgress: {bar} {pct}% ({len(progress['completed'])}/{progress['total']})")

        output.append("\n" + "=" * 60)
        output.append(f"{get_color('BOLD')}ITEMS{get_color('ENDC')}\n")

        # Display items
        for item in checklist["items"]:
            output.append(self._format_item(item, checklist_id, indent=0))

        output.append("\n" + "=" * 60)
        output.append(f"Use: {get_color('OKGREEN')}CHECKLIST COMPLETE {checklist_id} <item_id>{get_color('ENDC')} to mark items")

        return "\n".join(output)

    def _format_item(self, item: dict, checklist_id: str, indent: int = 0) -> str:
        """Format a checklist item with completion status.

        Args:
            item: Item data
            checklist_id: Parent checklist ID
            indent: Indentation level

        Returns:
            Formatted item string
        """
        prefix = "  " * indent
        completed = self.manager.is_completed(checklist_id, item["id"])
        checkbox = f"{get_color('OKGREEN')}[✓]{get_color('ENDC')}" if completed else "[ ]"

        optional_tag = f" {get_color('WARNING')}(optional){get_color('ENDC')}" if item.get("optional") else ""
        priority_tag = ""
        if item.get("priority") == "critical":
            priority_tag = f" {get_color('FAIL')}[!]{get_color('ENDC')}"

        quantity = ""
        if item.get("quantity"):
            unit = item.get("unit", "")
            quantity = f" ({item['quantity']} {unit})"

        lines = [f"{prefix}{checkbox} {item['text']}{quantity}{optional_tag}{priority_tag}"]

        if item.get("notes"):
            lines.append(f"{prefix}    {get_color('OKCYAN')}Note: {item['notes']}{get_color('ENDC')}")

        # Subitems
        if item.get("subitems"):
            for subitem in item["subitems"]:
                lines.append(self._format_item(subitem, checklist_id, indent + 1))

        return "\n".join(lines)

    def complete_item(self, args: list) -> str:
        """Mark a checklist item as completed.

        Args:
            args: [checklist_id, item_id]

        Returns:
            Success/error message
        """
        if len(args) < 2:
            return f"{get_color('FAIL')}Error: Checklist ID and item ID required{get_color('ENDC')}\nUsage: CHECKLIST COMPLETE <checklist_id> <item_id>"

        checklist_id, item_id = args[0], args[1]

        # Verify checklist exists
        if not self.manager.load_checklist(checklist_id):
            return f"{get_color('FAIL')}Error: Checklist '{checklist_id}' not found{get_color('ENDC')}"

        if self.manager.complete_item(checklist_id, item_id):
            progress = self.manager.get_progress(checklist_id)
            return (
                f"{get_color('OKGREEN')}✓ Item '{item_id}' marked complete{get_color('ENDC')}\n"
                f"Progress: {progress['percentage']}% ({len(progress['completed'])}/{progress['total']})"
            )

        return f"{get_color('FAIL')}Error: Could not complete item{get_color('ENDC')}"

    def uncomplete_item(self, args: list) -> str:
        """Unmark a checklist item as completed.

        Args:
            args: [checklist_id, item_id]

        Returns:
            Success/error message
        """
        if len(args) < 2:
            return f"{get_color('FAIL')}Error: Checklist ID and item ID required{get_color('ENDC')}\nUsage: CHECKLIST UNCOMPLETE <checklist_id> <item_id>"

        checklist_id, item_id = args[0], args[1]

        if self.manager.uncomplete_item(checklist_id, item_id):
            progress = self.manager.get_progress(checklist_id)
            return (
                f"{get_color('WARNING')}Item '{item_id}' unmarked{get_color('ENDC')}\n"
                f"Progress: {progress['percentage']}% ({len(progress['completed'])}/{progress['total']})"
            )

        return f"{get_color('FAIL')}Error: Could not uncomplete item{get_color('ENDC')}"

    def show_status(self, args: list) -> str:
        """Show detailed status for a checklist.

        Args:
            args: [checklist_id]

        Returns:
            Formatted status report
        """
        if not args:
            return f"{get_color('FAIL')}Error: Checklist ID required{get_color('ENDC')}\nUsage: CHECKLIST STATUS <id>"

        checklist_id = args[0]
        checklist = self.manager.load_checklist(checklist_id)

        if not checklist:
            return f"{get_color('FAIL')}Error: Checklist '{checklist_id}' not found{get_color('ENDC')}"

        progress = self.manager.get_progress(checklist_id)

        output = [
            f"\n{get_color('HEADER')}Checklist Status: {checklist['title']}{get_color('ENDC')}",
            "=" * 60,
        ]

        if progress["started"]:
            output.append(f"Started: {progress['started'][:10]}")
        if progress["last_updated"]:
            output.append(f"Last Updated: {progress['last_updated'][:10]}")

        pct = progress["percentage"]
        bar = self._make_progress_bar(pct, width=40)
        output.append(f"\nProgress: {bar} {pct}%")
        output.append(f"Completed: {len(progress['completed'])}/{progress['total']} items")

        if pct == 100:
            output.append(f"\n{get_color('OKGREEN')}✓ CHECKLIST COMPLETE!{get_color('ENDC')}")

        return "\n".join(output)

    def show_progress(self, args: list) -> str:
        """Show progress summary for all or filtered checklists.

        Args:
            args: Optional category filter

        Returns:
            Formatted progress summary
        """
        category = args[0] if args else None
        checklists = self.manager.list_checklists(category)

        output = [f"\n{get_color('HEADER')}Checklist Progress Summary{get_color('ENDC')}"]
        if category:
            output[0] += f" ({category})"
        output.append("=" * 60)

        in_progress = [c for c in checklists if 0 < c["progress"]["percentage"] < 100]
        completed = [c for c in checklists if c["progress"]["percentage"] == 100]
        not_started = [c for c in checklists if c["progress"]["percentage"] == 0]

        output.append(f"\n{get_color('OKGREEN')}Completed: {len(completed)}{get_color('ENDC')}")
        for c in completed:
            output.append(f"  ✓ {c['title']}")

        output.append(f"\n{get_color('WARNING')}In Progress: {len(in_progress)}{get_color('ENDC')}")
        for c in in_progress:
            pct = c["progress"]["percentage"]
            bar = self._make_progress_bar(pct, width=20)
            output.append(f"  {bar} {pct}% - {c['title']}")

        output.append(f"\n{get_color('OKCYAN')}Not Started: {len(not_started)}{get_color('ENDC')}")

        return "\n".join(output)

    def reset_progress(self, args: list) -> str:
        """Reset progress for a checklist.

        Args:
            args: [checklist_id]

        Returns:
            Success/error message
        """
        if not args:
            return f"{get_color('FAIL')}Error: Checklist ID required{get_color('ENDC')}\nUsage: CHECKLIST RESET <id>"

        checklist_id = args[0]

        if self.manager.reset_progress(checklist_id):
            return f"{get_color('WARNING')}Progress reset for checklist '{checklist_id}'{get_color('ENDC')}"

        return f"{get_color('FAIL')}Error: Could not reset progress{get_color('ENDC')}"

    def _make_progress_bar(self, percentage: float, width: int = 20) -> str:
        """Create a text progress bar.

        Args:
            percentage: Completion percentage (0-100)
            width: Bar width in characters

        Returns:
            Formatted progress bar
        """
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"

    def show_help(self) -> str:
        """Show checklist command help."""
        return f"""
{get_color('HEADER')}CHECKLIST Commands{get_color('ENDC')}
{'=' * 60}

{get_color('BOLD')}Viewing{get_color('ENDC')}
  CHECKLIST LIST [category]        - List available checklists
  CHECKLIST LOAD <id>              - Display checklist with items
  CHECKLIST STATUS <id>            - Show completion status
  CHECKLIST PROGRESS [category]    - Summary of all checklists

{get_color('BOLD')}Managing{get_color('ENDC')}
  CHECKLIST COMPLETE <id> <item>   - Mark item complete
  CHECKLIST UNCOMPLETE <id> <item> - Unmark item
  CHECKLIST RESET <id>             - Reset all progress

{get_color('BOLD')}Categories{get_color('ENDC')}
  emergency, daily, weekly, monthly, project, maintenance,
  setup, preparation, inventory

{get_color('BOLD')}Examples{get_color('ENDC')}
  CHECKLIST LIST emergency
  CHECKLIST LOAD 72-hour-bug-out-bag
  CHECKLIST COMPLETE 72-hour-bug-out-bag water_supply
  CHECKLIST STATUS 72-hour-bug-out-bag
"""
