"""
uDOS v1.0.30 - Enhanced File Picker

File picker specifically for knowledge and memory workspaces.
Shows .md and .uscript files with teletext UI.

Features:
- Browse /knowledge and /memory directories
- Filter by file type (.md, .uscript)
- Teletext-style visual interface
- Keyboard navigation (1-9, arrows)
- Search/filter support

Version: 1.0.30
"""

import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from core.ui.teletext_prompt import TeletextPromptStyle, TeletextBlocks


class KnowledgeFilePicker:
    """
    File picker for knowledge and memory workspaces.
    Focuses on .md and .uscript files for content management.
    """

    def __init__(self, base_path: str = None):
        """
        Initialize file picker.

        Args:
            base_path: Base uDOS path (defaults to current working dir parent)
        """
        if base_path is None:
            # Try to find uDOS root
            current = Path.cwd()
            while current.parent != current:
                if (current / 'knowledge').exists() or (current / 'memory').exists():
                    base_path = str(current)
                    break
                current = current.parent
            else:
                base_path = str(Path.cwd())

        self.base_path = Path(base_path)
        self.knowledge_path = self.base_path / 'knowledge'
        self.memory_path = self.base_path / 'memory'
        self.style = TeletextPromptStyle()
        self.blocks = TeletextBlocks()

    def get_workspace_files(
        self,
        workspace: str = 'knowledge',
        file_types: List[str] = None,
        recursive: bool = True,
        max_depth: int = 3
    ) -> List[Dict]:
        """
        Get files from workspace.

        Args:
            workspace: 'knowledge' or 'memory'
            file_types: List of extensions to include (e.g., ['.md', '.uscript'])
            recursive: Search subdirectories
            max_depth: Maximum directory depth

        Returns:
            List of file info dictionaries
        """
        if file_types is None:
            file_types = ['.md', '.uscript']

        workspace_path = self.knowledge_path if workspace == 'knowledge' else self.memory_path

        if not workspace_path.exists():
            return []

        files = []

        def scan_directory(path: Path, depth: int = 0):
            """Recursively scan directory for files."""
            if depth > max_depth:
                return

            try:
                for item in sorted(path.iterdir()):
                    if item.is_file():
                        if item.suffix in file_types:
                            # Calculate relative path from workspace
                            rel_path = item.relative_to(workspace_path)

                            files.append({
                                'name': item.name,
                                'path': str(item),
                                'relative_path': str(rel_path),
                                'size': item.stat().st_size,
                                'type': item.suffix,
                                'is_dir': False,
                                'depth': depth
                            })
                    elif item.is_dir() and recursive:
                        # Skip hidden and system directories
                        if not item.name.startswith('.') and item.name not in ['__pycache__', 'node_modules']:
                            scan_directory(item, depth + 1)
            except PermissionError:
                pass  # Skip directories we can't access

        scan_directory(workspace_path)
        return files

    def get_all_content_files(self) -> Tuple[List[Dict], List[Dict]]:
        """
        Get all content files from both workspaces.

        Returns:
            Tuple of (knowledge_files, memory_files)
        """
        knowledge_files = self.get_workspace_files('knowledge')
        memory_files = self.get_workspace_files('memory')
        return knowledge_files, memory_files

    def filter_files(self, files: List[Dict], query: str) -> List[Dict]:
        """
        Filter files by search query.

        Args:
            files: List of file dictionaries
            query: Search query

        Returns:
            Filtered file list
        """
        if not query:
            return files

        query_lower = query.lower()
        filtered = []

        for file in files:
            # Search in filename and path
            if (query_lower in file['name'].lower() or
                query_lower in file['relative_path'].lower()):
                filtered.append(file)

        return filtered

    def display_files(
        self,
        files: List[Dict],
        workspace: str = 'knowledge',
        selected_index: int = 0,
        show_path: bool = True
    ) -> str:
        """
        Display files using teletext UI.

        Args:
            files: List of file dictionaries
            workspace: Workspace name for title
            selected_index: Currently selected file index
            show_path: Show full relative path

        Returns:
            Formatted display string
        """
        if not files:
            return self._create_empty_message(workspace)

        # Convert to teletext format
        items = []
        for file in files[:9]:  # Limit to 9 for keyboard shortcuts
            # Format file info
            icon = self.blocks.CODE if file['type'] == '.uscript' else self.blocks.FILE

            if show_path:
                label = file['relative_path']
            else:
                label = file['name']

            # Add size info
            size = file['size']
            if size < 1024:
                size_str = f"{size}B"
            elif size < 1024 * 1024:
                size_str = f"{size // 1024}KB"
            else:
                size_str = f"{size // (1024 * 1024)}MB"

            items.append(f"{icon} {label} ({size_str})")

        # Create title
        title = f"{workspace.title()} Files ({len(files)} found)"

        # Use teletext style
        return self.style.create_selection_box(
            title=title,
            items=items,
            selected_index=selected_index,
            show_numbers=True,
            width=70
        )

    def _create_empty_message(self, workspace: str) -> str:
        """Create message for empty file list."""
        lines = [
            f"{self.blocks.DOUBLE_TL}{self.blocks.DOUBLE_H * 68}{self.blocks.DOUBLE_TR}",
            f"{self.blocks.DOUBLE_V}{'No Files Found':^68}{self.blocks.DOUBLE_V}",
            f"{self.blocks.DOUBLE_VR}{self.blocks.DOUBLE_H * 68}{self.blocks.DOUBLE_VL}",
            f"{self.blocks.DOUBLE_V}{f'No .md or .uscript files found in /{workspace}':^68}{self.blocks.DOUBLE_V}",
            f"{self.blocks.DOUBLE_BL}{self.blocks.DOUBLE_H * 68}{self.blocks.DOUBLE_BR}",
        ]
        return '\n'.join(lines)

    def pick_file(
        self,
        workspace: str = 'knowledge',
        prompt: str = "Select a file",
        file_types: List[str] = None
    ) -> Optional[str]:
        """
        Interactive file picker.

        Args:
            workspace: 'knowledge', 'memory', or 'both'
            prompt: Prompt message
            file_types: File types to show

        Returns:
            Selected file path or None if cancelled
        """
        if file_types is None:
            file_types = ['.md', '.uscript']

        # Get files
        if workspace == 'both':
            k_files = self.get_workspace_files('knowledge', file_types)
            m_files = self.get_workspace_files('memory', file_types)

            # Tag files with workspace
            for f in k_files:
                f['workspace'] = 'knowledge'
            for f in m_files:
                f['workspace'] = 'memory'

            files = k_files + m_files
            workspace_display = 'Knowledge & Memory'
        else:
            files = self.get_workspace_files(workspace, file_types)
            for f in files:
                f['workspace'] = workspace
            workspace_display = workspace.title()

        if not files:
            print(self._create_empty_message(workspace_display))
            input("\nPress ENTER to continue...")
            return None

        # Interactive selection
        selected_index = 0
        search_query = ""
        filtered_files = files

        while True:
            # Clear screen
            os.system('clear' if os.name != 'nt' else 'cls')

            # Apply filter if search query exists
            if search_query:
                filtered_files = self.filter_files(files, search_query)
                if not filtered_files:
                    print(f"\nNo files match '{search_query}'")
                    search_query = ""
                    filtered_files = files
                    continue
            else:
                filtered_files = files

            # Display files
            print(f"\n{prompt}")
            print(self.display_files(filtered_files, workspace_display, selected_index))

            if search_query:
                print(f"\nFilter: '{search_query}' ({len(filtered_files)} matches)")

            print("\nCommands: [1-9] Select | [/] Search | [n]ext | [p]rev | [q]uit")

            try:
                choice = input("\n> ").strip().lower()

                if not choice:
                    continue

                # Number selection
                if choice.isdigit():
                    num = int(choice)
                    if 1 <= num <= min(9, len(filtered_files)):
                        selected_file = filtered_files[num - 1]
                        return selected_file['path']
                    else:
                        print(f"Invalid selection: {num}")
                        input("Press ENTER to continue...")

                # Commands
                elif choice in ['q', 'quit', 'exit']:
                    return None

                elif choice in ['/', 'search', 's']:
                    search_query = input("Search: ").strip()

                elif choice in ['n', 'next']:
                    if selected_index + 9 < len(filtered_files):
                        selected_index += 9

                elif choice in ['p', 'prev', 'previous']:
                    selected_index = max(0, selected_index - 9)

                elif choice in ['c', 'clear']:
                    search_query = ""
                    selected_index = 0

            except (KeyboardInterrupt, EOFError):
                return None

        return None


# Quick test
if __name__ == '__main__':
    picker = KnowledgeFilePicker()

    print("Testing Knowledge File Picker")
    print("=" * 70)

    # Test getting files
    k_files = picker.get_workspace_files('knowledge')
    m_files = picker.get_workspace_files('memory')

    print(f"\nKnowledge files: {len(k_files)}")
    print(f"Memory files: {len(m_files)}")

    # Test display
    if k_files:
        print("\nKnowledge Files Preview:")
        print(picker.display_files(k_files[:5], 'knowledge'))

    # Interactive test
    print("\n\nStarting interactive picker...")
    selected = picker.pick_file('both', "Choose a file to view")

    if selected:
        print(f"\nSelected: {selected}")
    else:
        print("\nNo file selected")
