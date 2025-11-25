"""
uDOS Tree Generator
Generates repository structure visualization respecting .gitignore and hidden folders
"""

import os
import pathlib
import json
from typing import List, Set, Dict, Any, Tuple




class TreeGenerator:
    """Generates file tree structure respecting .gitignore rules."""

    def __init__(self, root_path: str = ".", target_folder: str = None, max_depth: int = 5):
        self.root_path = pathlib.Path(root_path).resolve()
        self.target_folder = target_folder  # Optional: sandbox, memory, knowledge, history, core, wiki, extensions, examples
        self.max_depth = max_depth  # Maximum recursion depth
        self.ignored_patterns = self._load_gitignore()
        self.hidden_folders = {'.git', '.vscode', '__pycache__', '.pytest_cache', '.mypy_cache'}

    def _load_gitignore(self) -> Set[str]:
        """Load patterns from .gitignore file."""
        ignored = set()
        gitignore_path = self.root_path / '.gitignore'

        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line and not line.startswith('#'):
                        # Remove trailing slashes
                        pattern = line.rstrip('/')
                        ignored.add(pattern)

        return ignored

    def _should_ignore(self, path: pathlib.Path, relative_path: str) -> bool:
        """Check if path should be ignored based on .gitignore and hidden rules."""
        # Ignore hidden system folders
        for part in path.parts:
            if part in self.hidden_folders:
                return True

        # Check .gitignore patterns
        for pattern in self.ignored_patterns:
            # Handle wildcards
            if '*' in pattern:
                # Simple wildcard matching
                if pattern.startswith('*'):
                    if relative_path.endswith(pattern[1:]):
                        return True
                elif pattern.endswith('*'):
                    if relative_path.startswith(pattern[:-1]):
                        return True
                elif pattern.endswith('/*'):
                    # Directory pattern
                    dir_pattern = pattern[:-2]
                    if relative_path.startswith(dir_pattern + '/'):
                        return True
            else:
                # Exact match or directory match
                if relative_path == pattern:
                    return True
                if relative_path.startswith(pattern + '/'):
                    return True
                # Check if any parent directory matches
                if '/' in relative_path:
                    parts = relative_path.split('/')
                    if pattern in parts:
                        return True

        return False

    def generate_tree(self) -> List[str]:
        """Generate tree structure as list of lines."""
        lines = []

        # If target_folder is specified, only show that folder
        if self.target_folder:
            target_path = self.root_path / self.target_folder
            if not target_path.exists() or not target_path.is_dir():
                lines.append(f"❌ Folder '{self.target_folder}/' not found")
                return lines

            lines.append(f"{self.target_folder}/")
            starting_path = target_path
            starting_depth = 0
        else:
            lines.append(f"{self.root_path.name}/")
            starting_path = self.root_path
            starting_depth = 0

        def walk_directory(directory: pathlib.Path, prefix: str = "", depth: int = 0):
            """Recursively walk directory and build tree."""
            if depth >= self.max_depth:
                return

            try:
                entries = sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name))
            except PermissionError:
                return

            # Filter out ignored entries
            visible_entries = []
            for entry in entries:
                relative_path = str(entry.relative_to(self.root_path))
                if not self._should_ignore(entry, relative_path):
                    visible_entries.append(entry)

            for i, entry in enumerate(visible_entries):
                is_last = (i == len(visible_entries) - 1)

                # Determine tree characters
                if is_last:
                    connector = "└── "
                    extension = "    "
                else:
                    connector = "├── "
                    extension = "│   "

                # Add entry
                if entry.is_dir():
                    lines.append(f"{prefix}{connector}{entry.name}/")
                    # Recurse into directory
                    walk_directory(entry, prefix + extension, depth + 1)
                else:
                    lines.append(f"{prefix}{connector}{entry.name}")

        walk_directory(starting_path, "", starting_depth)
        return lines

    def _build_tree_dict(self, directory: pathlib.Path, depth: int = 0) -> Dict[str, Any]:
        """Build tree structure as nested dictionary for JSON/XML output."""
        if depth >= self.max_depth:
            return {}

        result = {
            "name": directory.name,
            "type": "directory",
            "children": []
        }

        try:
            entries = sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name))
        except PermissionError:
            return result

        for entry in entries:
            relative_path = str(entry.relative_to(self.root_path))
            if self._should_ignore(entry, relative_path):
                continue

            if entry.is_dir():
                child = self._build_tree_dict(entry, depth + 1)
                result["children"].append(child)
            else:
                result["children"].append({
                    "name": entry.name,
                    "type": "file"
                })

        return result

    def generate_json(self) -> str:
        """Generate tree structure as JSON."""
        if self.target_folder:
            target_path = self.root_path / self.target_folder
            if not target_path.exists() or not target_path.is_dir():
                return json.dumps({"error": f"Folder '{self.target_folder}/' not found"}, indent=2)
            starting_path = target_path
        else:
            starting_path = self.root_path

        tree_dict = self._build_tree_dict(starting_path)
        return json.dumps(tree_dict, indent=2)

    def generate_xml(self) -> str:
        """Generate tree structure as XML."""
        if self.target_folder:
            target_path = self.root_path / self.target_folder
            if not target_path.exists() or not target_path.is_dir():
                return f"<error>Folder '{self.target_folder}/' not found</error>"
            starting_path = target_path
        else:
            starting_path = self.root_path

        def dict_to_xml(data: Dict[str, Any], indent: int = 0) -> str:
            """Convert dictionary to XML."""
            xml = " " * indent + f"<{data['type']} name=\"{data['name']}\">\n"
            for child in data.get("children", []):
                xml += dict_to_xml(child, indent + 2)
            xml += " " * indent + f"</{data['type']}>\n"
            return xml

        tree_dict = self._build_tree_dict(starting_path)
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + dict_to_xml(tree_dict)

    def save_to_file(self, output_file: str = "dev/docs/structure.txt") -> str:
        """Generate tree and save to file."""
        tree_lines = self.generate_tree()
        output_path = self.root_path / output_file

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(tree_lines))
            f.write('\n')

        return str(output_path)

    def get_tree_string(self) -> str:
        """Get tree as a single string."""
        tree_lines = self.generate_tree()
        return '\n'.join(tree_lines)



def generate_repository_tree(root_path: str = ".", output_file: str = "dev/docs/structure.txt", target_folder: str = None, max_depth: int = 5, output_format: str = "text") -> Tuple[str, str]:
    """
    Generate repository tree structure.

    Args:
        root_path: Root directory to analyze
        output_file: Output filename
        target_folder: Optional specific folder to show (sandbox, memory, knowledge, history, core, wiki, extensions, examples)
        max_depth: Maximum recursion depth (default: 5)
        output_format: Output format - "text", "json", or "xml" (default: "text")

    Returns:
        Tuple of (tree_string, output_file_path)
    """
    generator = TreeGenerator(root_path, target_folder=target_folder, max_depth=max_depth)

    if output_format.lower() == "json":
        tree_string = generator.generate_json()
    elif output_format.lower() == "xml":
        tree_string = generator.generate_xml()
    else:
        tree_string = generator.get_tree_string()

    output_path = generator.save_to_file(output_file)

    return tree_string, output_path


if __name__ == "__main__":
    # Test the tree generator
    tree_str, file_path = generate_repository_tree()
    print(tree_str)
    print(f"\n✅ Tree saved to: {file_path}")
