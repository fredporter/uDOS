"""
uDOS TREE Command Handler

Generates directory tree structures and saves them to structure.txt files.

Commands:
- TREE: Update all structure files and show root tree
- MEMORY TREE: Show memory tree
- KNOWLEDGE TREE: Show knowledge tree

Files created:
- structure.txt (root - excludes /knowledge, respects .gitignore)
- memory/structure.txt (excludes memory/logs)
- knowledge/structure.txt (full knowledge tree)

Version: 1.1.0 (Added pager support for long trees)
"""

import os
from pathlib import Path
from typing import List, Set, Optional, Dict
import fnmatch
from core.utils.pager import page_output
from core.utils.paths import PATHS


class TreeHandler:
    """Handler for TREE command - generates directory structure files."""

    def __init__(self):
        self.base_path = Path.cwd()
        self.gitignore_patterns = self._load_gitignore()

    def _load_gitignore(self) -> List[str]:
        """Load patterns from .gitignore file."""
        gitignore_path = self.base_path / '.gitignore'
        patterns = []

        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line and not line.startswith('#'):
                        patterns.append(line)

        return patterns

    def _should_ignore(self, path: Path, base: Path, additional_excludes: Set[str] = None) -> bool:
        """
        Check if path should be ignored based on .gitignore and additional excludes.

        Args:
            path: Path to check
            base: Base directory for relative path calculation
            additional_excludes: Additional folder names to exclude

        Returns:
            True if path should be ignored
        """
        if additional_excludes is None:
            additional_excludes = set()

        # Get relative path
        try:
            rel_path = path.relative_to(base)
        except ValueError:
            return False

        # Check if any parent folder is in excludes
        for part in rel_path.parts:
            if part in additional_excludes:
                return True

        # Check gitignore patterns
        rel_path_str = str(rel_path)
        for pattern in self.gitignore_patterns:
            # Handle directory patterns
            if pattern.endswith('/'):
                dir_pattern = pattern.rstrip('/')
                if fnmatch.fnmatch(rel_path_str, dir_pattern) or \
                   fnmatch.fnmatch(rel_path_str, f'{dir_pattern}/*') or \
                   fnmatch.fnmatch(path.name, dir_pattern):
                    return True
            else:
                # File or directory pattern
                if fnmatch.fnmatch(rel_path_str, pattern) or \
                   fnmatch.fnmatch(path.name, pattern):
                    return True

        return False

    def _generate_tree(
        self,
        directory: Path,
        prefix: str = "",
        is_last: bool = True,
        exclude_folders: Set[str] = None,
        max_depth: int = 10,
        current_depth: int = 0,
        depth_limits: Dict[str, int] = None,
        respect_gitignore: bool = True
    ) -> List[str]:
        """
        Generate tree structure recursively.

        Args:
            directory: Directory to scan
            prefix: Prefix for tree formatting
            is_last: Whether this is the last item in parent
            exclude_folders: Folder names to exclude
            max_depth: Maximum recursion depth
            current_depth: Current recursion depth
            depth_limits: Dict of folder names to depth limits (relative to that folder)
            respect_gitignore: Whether to respect .gitignore patterns

        Returns:
            List of formatted tree lines
        """
        if exclude_folders is None:
            exclude_folders = set()

        if depth_limits is None:
            depth_limits = {}

        if current_depth >= max_depth:
            return []

        lines = []

        try:
            # Get all items in directory
            items = sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))

            # Filter out ignored items
            if respect_gitignore:
                items = [
                    item for item in items
                    if not self._should_ignore(item, directory.parent if current_depth == 0 else self.base_path, exclude_folders)
                ]
            else:
                # Only filter by exclude_folders, not gitignore
                items = [
                    item for item in items
                    if not (item.is_dir() and item.name in (exclude_folders or set()))
                ]

            for i, item in enumerate(items):
                is_last_item = (i == len(items) - 1)

                # Tree characters
                connector = "└── " if is_last_item else "├── "
                extension = "    " if is_last_item else "│   "

                # Add item to tree
                item_name = item.name + ("/" if item.is_dir() else "")
                lines.append(f"{prefix}{connector}{item_name}")

                # Recurse into directories
                if item.is_dir():
                    # Check if this folder has a specific depth limit
                    folder_depth_limit = max_depth
                    next_depth = current_depth + 1

                    for limit_folder, limit_depth in depth_limits.items():
                        if item.name == limit_folder:
                            # This folder has a depth limit - reset depth counter for this branch
                            folder_depth_limit = limit_depth
                            next_depth = 0
                            break

                    sub_lines = self._generate_tree(
                        item,
                        prefix + extension,
                        is_last_item,
                        exclude_folders,
                        folder_depth_limit,
                        next_depth,
                        depth_limits,
                        respect_gitignore
                    )
                    lines.extend(sub_lines)

        except PermissionError:
            pass  # Skip directories we can't access

        return lines

    def generate_root_tree(self) -> str:
        """
        Generate root directory tree.
        Excludes: /dev, /wiki, __pycache__, .git, .vscode, node_modules
        Applies depth limit of 3 for /extensions folder.
        Applies depth limit of 1 for /knowledge folder (subfolders only).
        Respects .gitignore patterns.
        """
        exclude_folders = {'__pycache__', '.git', '.vscode', 'node_modules', 'dev', 'wiki'}
        depth_limits = {'extensions': 3, 'knowledge': 1}

        lines = [f"{self.base_path.name}/"]
        lines.extend(self._generate_tree(
            self.base_path,
            prefix="",
            exclude_folders=exclude_folders,
            max_depth=8,
            depth_limits=depth_limits
        ))

        return "\n".join(lines)

    def generate_memory_tree(self) -> str:
        """Generate memory directory tree (excludes memory/logs)."""
        memory_path = self.base_path / 'memory'

        if not memory_path.exists():
            return "❌ memory/ directory not found"

        exclude_folders = {'logs', '__pycache__'}

        lines = [str(PATHS.MEMORY.relative_to(PATHS.ROOT)) + "/"]
        lines.extend(self._generate_tree(
            memory_path,
            prefix="",
            exclude_folders=exclude_folders,
            max_depth=8,
            respect_gitignore=False
        ))

        return "\n".join(lines)

    def generate_knowledge_tree(self) -> str:
        """Generate knowledge directory tree (full tree)."""
        knowledge_path = self.base_path / 'knowledge'

        if not knowledge_path.exists():
            return "❌ knowledge/ directory not found"

        exclude_folders = {'__pycache__'}

        lines = ["knowledge/"]
        lines.extend(self._generate_tree(
            knowledge_path,
            prefix="",
            exclude_folders=exclude_folders,
            max_depth=8,
            respect_gitignore=False
        ))

        return "\n".join(lines)

    def save_structure_files(self) -> dict:
        """
        Generate and save all three structure.txt files.

        Returns:
            Dictionary with status for each file
        """
        results = {}

        # Root structure.txt
        try:
            root_tree = self.generate_root_tree()
            root_file = self.base_path / 'structure.txt'
            root_file.write_text(root_tree, encoding='utf-8')
            results['root'] = f"✅ {root_file}"
        except Exception as e:
            results['root'] = f"❌ Error: {e}"

        # memory/structure.txt
        try:
            memory_tree = self.generate_memory_tree()
            memory_file = self.base_path / 'memory' / 'structure.txt'
            memory_file.parent.mkdir(exist_ok=True)
            memory_file.write_text(memory_tree, encoding='utf-8')
            results['memory'] = f"✅ {memory_file}"
        except Exception as e:
            results['memory'] = f"❌ Error: {e}"

        # knowledge/structure.txt
        try:
            knowledge_tree = self.generate_knowledge_tree()
            knowledge_file = self.base_path / 'knowledge' / 'structure.txt'
            knowledge_file.parent.mkdir(exist_ok=True)
            knowledge_file.write_text(knowledge_tree, encoding='utf-8')
            results['knowledge'] = f"✅ {knowledge_file}"
        except Exception as e:
            results['knowledge'] = f"❌ Error: {e}"

        return results

    def handle(self, params):
        """
        Handle TREE command.

        Args:
            params: Command parameters

        Returns:
            Formatted output
        """
        # Check for subcommands
        if params and len(params) > 0:
            subcommand = params[0].upper()

            if subcommand == 'MEMORY':
                # MEMORY TREE - show memory tree
                tree = self.generate_memory_tree()
                output = f"\n{tree}\n\n💡 Saved to: memory/structure.txt"

                # Use pager if output is long
                lines = output.split('\n')
                if len(lines) > 20:
                    page_output(output, title="Memory Tree")
                    return ""  # Empty string since pager already displayed
                return output

            elif subcommand == 'KNOWLEDGE':
                # KNOWLEDGE TREE - show knowledge tree
                tree = self.generate_knowledge_tree()
                output = f"\n{tree}\n\n💡 Saved to: knowledge/structure.txt"

                # Use pager if output is long
                lines = output.split('\n')
                if len(lines) > 20:
                    page_output(output, title="Knowledge Tree")
                    return ""  # Empty string since pager already displayed
                return output

        # TREE - update all files and show root tree (FULL, not truncated)
        results = self.save_structure_files()
        root_tree = self.generate_root_tree()

        output = []
        output.append("📁 Directory Structure Updated\n")
        output.append("=" * 70)
        output.append("")

        for name, result in results.items():
            output.append(result)

        output.append("")
        output.append("=" * 70)
        output.append("Root Structure (Full Tree):")
        output.append("=" * 70)
        output.append("")
        output.append(root_tree)  # Show FULL tree, no truncation
        output.append("")
        output.append("=" * 70)
        output.append("💡 Use: MEMORY TREE or KNOWLEDGE TREE to view those trees")

        full_output = "\n".join(output)

        # Use pager if output is long
        lines = full_output.split('\n')
        if len(lines) > 20:
            page_output(full_output, title="Directory Tree")
            return ""  # Empty string since pager already displayed

        return full_output
