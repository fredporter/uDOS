# uDOS v1.0.0 - Interactive File Picker

from pathlib import Path
from prompt_toolkit.shortcuts import radiolist_dialog
from prompt_toolkit.styles import Style


class FilePicker:
    """
    Interactive file picker for RUN, SHOW, EDIT commands.
    Limited to sandbox/ and memory/ directories.
    """

    ALLOWED_DIRS = ['sandbox', 'memory']

    # File type icons
    ICONS = {
        '.py': '🐍',
        '.uscript': '📜',
        '.usc': '📜',
        '.md': '📝',
        '.txt': '📄',
        '.json': '⚙️',
        '.log': '📋',
        '.UDO': '🔧',
        'directory': '📁',
        'default': '📄'
    }

    def __init__(self, root_dir=None):
        """
        Initialize file picker.

        Args:
            root_dir: Root directory path (defaults to current directory)
        """
        self.root = Path(root_dir) if root_dir else Path.cwd()

    def pick_file(self, directory='sandbox', title='Select File',
                  file_patterns=None, include_dirs=False):
        """
        Show interactive file picker dialog.

        Args:
            directory: Directory to browse ('sandbox' or 'memory')
            title: Dialog title
            file_patterns: List of glob patterns (e.g., ['*.py', '*.uscript'])
            include_dirs: Whether to include directories in selection

        Returns:
            Path object if file selected, None if cancelled
        """
        if directory not in self.ALLOWED_DIRS:
            raise ValueError(f"Directory must be one of {self.ALLOWED_DIRS}")

        # Find files
        files = self._find_files(directory, file_patterns, include_dirs)

        if not files:
            return None

        # Build choices for radiolist
        choices = []
        for file_path in files:
            icon = self._get_icon(file_path)
            display = self._format_display(file_path)
            choices.append((str(file_path), f"{icon} {display}"))

        # Show dialog
        result = radiolist_dialog(
            title=title,
            text=f"Choose from {directory}/",
            values=choices,
            style=self._get_dialog_style()
        ).run()

        return Path(result) if result else None

    def pick_script(self, directory='sandbox'):
        """
        Pick a script file (.uscript, .usc, .py).

        Args:
            directory: Directory to browse

        Returns:
            Path object if selected, None if cancelled
        """
        return self.pick_file(
            directory=directory,
            title='Run Script',
            file_patterns=['*.uscript', '*.usc', '*.py']
        )

    def pick_document(self, directory='sandbox'):
        """
        Pick a document file (.md, .txt).

        Args:
            directory: Directory to browse

        Returns:
            Path object if selected, None if cancelled
        """
        return self.pick_file(
            directory=directory,
            title='Select Document',
            file_patterns=['*.md', '*.txt', '*.UDO']
        )

    def pick_any(self, directory='sandbox'):
        """
        Pick any file.

        Args:
            directory: Directory to browse

        Returns:
            Path object if selected, None if cancelled
        """
        return self.pick_file(
            directory=directory,
            title='Select File',
            file_patterns=None
        )

    def _find_files(self, directory, patterns=None, include_dirs=False):
        """
        Find files matching patterns in directory.

        Args:
            directory: Directory name
            patterns: List of glob patterns or None for all files
            include_dirs: Include subdirectories

        Returns:
            Sorted list of Path objects
        """
        dir_path = self.root / directory

        if not dir_path.exists():
            return []

        files = []

        if patterns:
            # Find files matching specific patterns
            for pattern in patterns:
                files.extend(dir_path.rglob(pattern))
        else:
            # Find all files
            for item in dir_path.rglob('*'):
                if item.is_file():
                    files.append(item)
                elif include_dirs and item.is_dir():
                    files.append(item)

        # Sort by name
        return sorted(files, key=lambda p: p.name.lower())

    def _get_icon(self, path):
        """
        Get icon for file type.

        Args:
            path: Path object

        Returns:
            Icon string
        """
        if path.is_dir():
            return self.ICONS['directory']

        suffix = path.suffix.lower()
        return self.ICONS.get(suffix, self.ICONS['default'])

    def _format_display(self, path):
        """
        Format file path for display.

        Args:
            path: Path object

        Returns:
            Formatted string with metadata
        """
        # Get relative path from root
        try:
            rel_path = path.relative_to(self.root)
        except ValueError:
            rel_path = path

        # Add metadata
        if path.is_file():
            size = path.stat().st_size
            size_str = self._format_size(size)
            return f"{rel_path} ({size_str})"
        elif path.is_dir():
            try:
                count = len(list(path.iterdir()))
                return f"{rel_path}/ ({count} items)"
            except PermissionError:
                return f"{rel_path}/"

        return str(rel_path)

    def _format_size(self, size):
        """
        Format file size in human-readable format.

        Args:
            size: Size in bytes

        Returns:
            Formatted string (e.g., "2.3 KB")
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def _get_dialog_style(self):
        """
        Get prompt_toolkit style for dialogs.

        Returns:
            Style object
        """
        return Style.from_dict({
            'dialog': 'bg:#1e1e1e',
            'dialog frame.label': 'bg:#00aaff #000000',
            'dialog.body': 'bg:#1e1e1e #ffffff',
            'dialog shadow': 'bg:#000000',
            'radio-list': 'bg:#1e1e1e',
            'radio-checked': '#00ff00',
            'radio': '#888888',
        })

    def list_files(self, directory='sandbox', patterns=None):
        """
        List files without interactive selection.

        Args:
            directory: Directory name
            patterns: File patterns to match

        Returns:
            List of Path objects
        """
        if directory not in self.ALLOWED_DIRS:
            return []

        return self._find_files(directory, patterns)

    def get_file_info(self, file_path):
        """
        Get detailed file information.

        Args:
            file_path: Path to file

        Returns:
            Dict with file metadata
        """
        path = Path(file_path)

        if not path.exists():
            return None

        stat = path.stat()

        return {
            'name': path.name,
            'path': str(path),
            'size': stat.st_size,
            'size_formatted': self._format_size(stat.st_size),
            'modified': stat.st_mtime,
            'is_file': path.is_file(),
            'is_dir': path.is_dir(),
            'extension': path.suffix,
            'icon': self._get_icon(path)
        }
