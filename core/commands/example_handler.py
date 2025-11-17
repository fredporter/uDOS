"""
EXAMPLE Command Handler - v1.0.22
Example code library manager

Commands:
  EXAMPLE
  EXAMPLE LIST
  EXAMPLE <name>
  EXAMPLE RUN <name>
  EXAMPLE SAVE <name>

Author: uDOS Development Team
Version: 1.0.22
"""

from pathlib import Path
from typing import List, Dict, Optional
import json


class ExampleHandler:
    """Handler for EXAMPLE commands - example library"""

    def __init__(self, viewport=None, logger=None):
        """Initialize ExampleHandler"""
        self.viewport = viewport
        self.logger = logger
        self.examples_path = Path("examples")
        self.memory_path = Path("memory/modules")

        # Example index
        self.examples = self._build_index()

    def handle(self, command: str, args: List[str]) -> str:
        """Route EXAMPLE commands to appropriate handlers"""

        if not command or command == "HELP":
            return self._show_help()

        if command == "LIST":
            return self._list_examples()

        if command == "RUN":
            if not args:
                return "❌ Usage: EXAMPLE RUN <name>"
            name = args[0]
            return self._run_example(name)

        if command == "SAVE":
            if not args:
                return "❌ Usage: EXAMPLE SAVE <name>"
            name = args[0]
            return self._save_example(name)

        if command == "INFO":
            if not args:
                return "❌ Usage: EXAMPLE INFO <name>"
            name = args[0]
            return self._show_info(name)

        # Show specific example
        name = command.lower()
        return self._show_example(name)

    def _build_index(self) -> Dict[str, Dict]:
        """Build example index"""
        index = {}

        if not self.examples_path.exists():
            return index

        # Index .uscript files
        for script in self.examples_path.rglob("*.uscript"):
            name = script.stem.lower()
            index[name] = {
                "name": script.stem,
                "path": script,
                "type": "uCODE Script",
                "category": self._categorize(script)
            }

        # Index .py examples
        for py_file in self.examples_path.rglob("*.py"):
            if py_file.stem not in ["__init__", "test_"]:
                name = py_file.stem.lower()
                index[name] = {
                    "name": py_file.stem,
                    "path": py_file,
                    "type": "Python Script",
                    "category": self._categorize(py_file)
                }

        # Index .txt examples
        for txt_file in self.examples_path.rglob("*.txt"):
            name = txt_file.stem.lower()
            index[name] = {
                "name": txt_file.stem,
                "path": txt_file,
                "type": "Text Example",
                "category": self._categorize(txt_file)
            }

        return index

    def _categorize(self, path: Path) -> str:
        """Categorize example by path or name"""
        path_str = str(path).lower()

        if "extension" in path_str:
            return "Extensions"
        elif "teletext" in path_str or "block" in path_str:
            return "Graphics"
        elif "automation" in path_str or "task" in path_str:
            return "Automation"
        elif "dashboard" in path_str or "screen" in path_str:
            return "UI"
        elif "advanced" in path_str:
            return "Advanced"
        elif "simple" in path_str or "hello" in path_str:
            return "Getting Started"
        else:
            return "General"

    def _show_help(self) -> str:
        """Display EXAMPLE command help"""
        return """
┌─────────────────────────────────────────────────────────────────┐
│  EXAMPLE - Code Example Library                                │
└─────────────────────────────────────────────────────────────────┘

💡 Browse and run example code

USAGE:
  EXAMPLE                Show example home
  EXAMPLE LIST           List all examples
  EXAMPLE <name>         Show example code
  EXAMPLE RUN <name>     Run example (if executable)
  EXAMPLE INFO <name>    Show example details
  EXAMPLE SAVE <name>    Save to your library

EXAMPLES:
  EXAMPLE LIST                   # List all examples
  EXAMPLE hello-automation       # Show example
  EXAMPLE RUN simple-setup       # Run uCODE script
  EXAMPLE SAVE task-manager      # Save to library

CATEGORIES:
  • Getting Started    Simple introductory examples
  • Automation         Task automation scripts
  • Graphics           Grid, panels, teletext
  • UI                 Dashboard and display examples
  • Extensions         Extension development
  • Advanced           Complex features

RUNNING EXAMPLES:
  • .uscript files run as uCODE scripts
  • .py files are displayed (not executed)
  • .txt files show text output examples

See also: GUIDE, HANDBOOK, LIBRARY
"""

    def _list_examples(self) -> str:
        """List all examples"""
        if not self.examples:
            return "\n❌ No examples found\n"

        output = ["", "💡 Available Examples", "═" * 60, ""]

        # Group by category
        categories = {}
        for ex_data in self.examples.values():
            cat = ex_data.get("category", "General")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(ex_data)

        for category, examples in sorted(categories.items()):
            output.append(f"▸ {category}")
            output.append("─" * 60)
            for ex in sorted(examples, key=lambda x: x['name']):
                output.append(f"  • {ex['name']:<30} ({ex['type']})")
            output.append("")

        output.append(f"Total: {len(self.examples)} examples")
        output.append("")
        output.append("Usage: EXAMPLE <name> to view")

        return "\n".join(output)

    def _show_example(self, name: str) -> str:
        """Show specific example"""

        if name not in self.examples:
            # Try partial match
            matches = [k for k in self.examples.keys() if name in k]
            if not matches:
                return f"\n❌ Example '{name}' not found\n\nUse 'EXAMPLE LIST' to see all\n"
            if len(matches) == 1:
                name = matches[0]
            else:
                output = [f"\n💡 Multiple matches for '{name}':", ""]
                for match in matches:
                    output.append(f"  • {match}")
                output.append("")
                output.append("Please be more specific")
                return "\n".join(output)

        ex_data = self.examples[name]

        try:
            content = ex_data['path'].read_text()

            output = ["", "═" * 60]
            output.append(f"  {ex_data['name']} - {ex_data['type']}")
            output.append("═" * 60)
            output.append("")
            output.append(content)
            output.append("")
            output.append("─" * 60)

            if ex_data['type'] == "uCODE Script":
                output.append("Run with: EXAMPLE RUN " + name)
            else:
                output.append("View: EXAMPLE INFO " + name)

            output.append("")

            return "\n".join(output)

        except Exception as e:
            return f"\n❌ Error reading example: {e}\n"

    def _run_example(self, name: str) -> str:
        """Run example (if executable)"""

        if name not in self.examples:
            return f"\n❌ Example '{name}' not found\n"

        ex_data = self.examples[name]

        if ex_data['type'] != "uCODE Script":
            return f"\n❌ Cannot run {ex_data['type']}\n\nOnly .uscript files can be executed\n"

        # Return instruction to run via uCODE interpreter
        return f"""
To run this example:

  RUN {ex_data['path']}

Or load in editor:

  EDIT {ex_data['path']}

Note: EXAMPLE RUN integration with uCODE interpreter
      will be available in the next update.
"""

    def _save_example(self, name: str) -> str:
        """Save example to user library"""

        if name not in self.examples:
            return f"\n❌ Example '{name}' not found\n"

        ex_data = self.examples[name]

        # Save to memory/modules
        dest_path = self.memory_path / ex_data['path'].name

        try:
            self.memory_path.mkdir(parents=True, exist_ok=True)

            # Copy file
            content = ex_data['path'].read_text()
            dest_path.write_text(content)

            # Save metadata
            meta_path = self.memory_path / f"{ex_data['path'].stem}.meta.json"
            metadata = {
                "name": ex_data['name'],
                "type": ex_data['type'],
                "category": ex_data['category'],
                "source": str(ex_data['path']),
                "saved_from": "example_library"
            }
            meta_path.write_text(json.dumps(metadata, indent=2))

            return f"""
✅ Example saved to library

  Location: {dest_path}
  Type: {ex_data['type']}
  Category: {ex_data['category']}

View your saved examples:

  FILES {self.memory_path}
"""

        except Exception as e:
            return f"\n❌ Error saving example: {e}\n"

    def _show_info(self, name: str) -> str:
        """Show example details"""

        if name not in self.examples:
            return f"\n❌ Example '{name}' not found\n"

        ex_data = self.examples[name]

        output = ["", "═" * 60]
        output.append(f"  {ex_data['name']}")
        output.append("═" * 60)
        output.append("")
        output.append(f"Type:     {ex_data['type']}")
        output.append(f"Category: {ex_data['category']}")
        output.append(f"Path:     {ex_data['path']}")
        output.append("")

        # File stats
        try:
            stat = ex_data['path'].stat()
            size = stat.st_size
            output.append(f"Size:     {size} bytes")

            # Count lines
            lines = ex_data['path'].read_text().count('\n')
            output.append(f"Lines:    {lines}")
        except Exception:
            pass

        output.append("")
        output.append("Commands:")
        output.append(f"  EXAMPLE {name}           # View code")
        if ex_data['type'] == "uCODE Script":
            output.append(f"  EXAMPLE RUN {name}       # Execute")
        output.append(f"  EXAMPLE SAVE {name}      # Save to library")
        output.append("")

        return "\n".join(output)


def create_handler(viewport=None, logger=None):
    """Factory function to create handler"""
    return ExampleHandler(viewport=viewport, logger=logger)
