"""
uDOS v1.0.31 - Enhanced File Picker

File picker specifically for knowledge and memory workspaces.
Shows .md and .uscript files with teletext UI.

Features:
- Browse /knowledge and /memory directories
- Filter by file type (.md, .uscript)
- Teletext-style visual interface
- Keyboard navigation (1-9, arrows)
- Search/filter support
- Standardized input interface (v1.0.31)

Version: 1.0.31
"""

import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from core.ui.teletext_prompt import TeletextPromptStyle, TeletextBlocks
from core.services.standardized_input import StandardizedInput


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
        self.si = StandardizedInput()  # Standardized input v1.0.31

        # Folder shortcuts for quick navigation
        self.folder_shortcuts = {
            'sandbox': self.base_path / 'memory' / 'sandbox',
            'knowledge': self.base_path / 'knowledge',
            'public': self.base_path / 'memory' / 'public',
            'private': self.base_path / 'memory' / 'private',
            'groups': self.base_path / 'memory' / 'groups',
            'shared': self.base_path / 'memory' / 'shared',
            'planet': self.base_path / 'memory' / 'planet',
            'user': self.base_path / 'memory' / 'user',
            'memory': self.base_path / 'memory'
        }

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

    def _get_files_in_folder(
        self,
        folder: Path,
        file_types: List[str] = None,
        recursive: bool = True
    ) -> List[Dict]:
        """
        Get files from a specific folder.

        Args:
            folder: Folder path
            file_types: List of extensions to include
            recursive: Search subdirectories

        Returns:
            List of file info dictionaries
        """
        if file_types is None:
            file_types = ['.md', '.uscript']

        if not folder.exists():
            return []

        files = []

        try:
            # Use glob for recursive search
            if recursive:
                for ext in file_types:
                    for file_path in folder.rglob(f'*{ext}'):
                        if file_path.is_file():
                            files.append({
                                'name': file_path.name,
                                'path': str(file_path),
                                'relative_path': str(file_path.relative_to(folder)),
                                'size': file_path.stat().st_size,
                                'type': file_path.suffix,
                                'is_dir': False
                            })
            else:
                for ext in file_types:
                    for file_path in folder.glob(f'*{ext}'):
                        if file_path.is_file():
                            files.append({
                                'name': file_path.name,
                                'path': str(file_path),
                                'relative_path': file_path.name,
                                'size': file_path.stat().st_size,
                                'type': file_path.suffix,
                                'is_dir': False
                            })
        except PermissionError:
            pass

        return sorted(files, key=lambda x: x['name'])

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
        file_types: List[str] = None,
        show_workspace_selector: bool = True
    ) -> Optional[str]:
        """
        Interactive file picker.

        Args:
            workspace: 'knowledge', 'memory', 'both', or 'folder' (prompts for folder selection)
            prompt: Prompt message
            file_types: File types to show
            show_workspace_selector: Show folder/workspace selector first

        Returns:
            Selected file path or None if cancelled
        """
        if file_types is None:
            file_types = ['.md', '.uscript']

        # Show workspace/folder selector if requested
        if show_workspace_selector and workspace in ['both', 'folder']:
            folder = self.pick_folder(
                prompt="📁 Select workspace folder",
                include_custom=False
            )

            if not folder:
                return None

            # Search files in selected folder
            files = self._get_files_in_folder(folder, file_types)
            workspace_display = folder.name.title()

            for f in files:
                f['workspace'] = str(folder.relative_to(self.base_path))
        else:
            # Original behavior - get files from workspace
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
            self.si.input_text("Press ENTER to continue", default="")
            return None

        # Convert files to simple list of names for StandardizedInput
        file_options = []
        file_descriptions = []
        for f in files:
            name = f['name']
            rel_path = f['relative_path']
            workspace_tag = f'[{f["workspace"]}]'
            file_options.append(f"{name}")
            file_descriptions.append(f"{workspace_tag} {rel_path}")

        # Use standardized input for file selection
        idx, selected_name = self.si.select_option(
            prompt,
            file_options[:9],  # Limit to 9 for numbered selection
            descriptions=file_descriptions[:9] if file_descriptions else None,
            show_numbers=True,
            allow_filter=False
        )

        if idx == -1 or idx >= len(files):
            return None

        return files[idx]['path']

    def pick_folder(
        self,
        prompt: str = "Select a folder",
        include_custom: bool = True
    ) -> Optional[Path]:
        """
        Interactive folder picker using shortcuts.

        Args:
            prompt: Prompt message
            include_custom: Allow custom folder path input

        Returns:
            Selected folder path or None if cancelled
        """
        # Create folder options
        folder_options = []
        folder_paths = []

        for name, path in sorted(self.folder_shortcuts.items()):
            # Check if folder exists
            exists_marker = "✓" if path.exists() else "✗"
            rel_path = path.relative_to(self.base_path) if path.is_relative_to(self.base_path) else path

            folder_options.append(f"{name}")
            folder_paths.append(path)

        if include_custom:
            folder_options.append("Custom path...")

        # Use standardized input for folder selection
        idx, selected_name = self.si.select_option(
            prompt,
            folder_options,
            descriptions=[str(p.relative_to(self.base_path)) if p.is_relative_to(self.base_path) else str(p)
                         for p in folder_paths] + (["Enter custom folder path"] if include_custom else []),
            show_numbers=True,
            allow_filter=False
        )

        if idx == -1:
            return None

        # Handle custom path
        if include_custom and idx == len(folder_paths):
            custom_path = self.si.input_text("Enter folder path", default="")
            if custom_path:
                path = Path(custom_path)
                if not path.is_absolute():
                    path = self.base_path / path
                return path
            return None

        return folder_paths[idx]

    def pick_file_from_folder(
        self,
        folder: Optional[Path] = None,
        prompt: str = "Select a file",
        file_types: List[str] = None
    ) -> Optional[str]:
        """
        Pick a file from a specific folder.

        Args:
            folder: Folder to browse (None to pick folder first)
            prompt: Prompt message
            file_types: File types to show

        Returns:
            Selected file path or None if cancelled
        """
        # Pick folder if not provided
        if folder is None:
            folder = self.pick_folder("Select folder to browse")
            if folder is None:
                return None

        if file_types is None:
            file_types = ['.md', '.uscript']

        if not folder.exists():
            print(f"⚠️  Folder does not exist: {folder}")
            return None

        # Get files from folder
        files = []
        try:
            for item in sorted(folder.iterdir()):
                if item.is_file() and item.suffix in file_types:
                    files.append({
                        'name': item.name,
                        'path': str(item),
                        'relative_path': item.name,
                        'size': item.stat().st_size,
                        'type': item.suffix,
                        'is_dir': False
                    })
        except PermissionError:
            print(f"⚠️  Permission denied: {folder}")
            return None

        if not files:
            print(f"⚠️  No files found in {folder}")
            return None

        # Use standardized input for file selection
        file_options = [f['name'] for f in files]
        file_descriptions = [f"{f['type']} - {f['size']} bytes" for f in files]

        idx, selected_name = self.si.select_option(
            f"{prompt} ({folder.name})",
            file_options[:20],  # Limit to 20 files
            descriptions=file_descriptions[:20] if file_descriptions else None,
            show_numbers=True,
            allow_filter=False
        )

        if idx == -1 or idx >= len(files):
            return None

        return files[idx]['path']


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
