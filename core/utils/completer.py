# uDOS v1.0.0 - Smart Context-Aware Completer

from prompt_toolkit.completion import Completer, Completion, PathCompleter
from prompt_toolkit.document import Document
from pathlib import Path
import os

class uDOSCompleter(Completer):
    """
    Context-aware completer for uDOS commands.
    Switches between command completion, file path completion, and panel name completion
    based on the current input context.
    """

    def __init__(self, parser, grid):
        self.parser = parser
        self.grid = grid
        self.command_names = parser.get_command_names()
        self.path_completer = PathCompleter(expanduser=True)
        self.root = Path.cwd()

        # Commands that expect file paths
        self.file_commands = ['LOAD', 'SAVE', 'RUN', 'EDIT', 'CATALOG', 'SHOW']

        # Commands that expect panel names
        self.panel_commands = ['ANALYZE', 'GRID PANEL CREATE', 'GRID PANEL DELETE',
                               'GRID PANEL SELECT']

        # Allowed directories for file operations
        self.allowed_dirs = ['sandbox', 'memory']

        # File type icons
        self.file_icons = {
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

    def get_completions(self, document, complete_event):
        """
        Generate completions based on the current context.
        """
        text = document.text_before_cursor
        words = text.split()

        # If empty, suggest nothing
        if not words:
            return

        # Single word without space = command completion
        if len(words) == 1 and not text.endswith(' '):
            word = words[0].upper()
            for cmd in self.command_names:
                if cmd.upper().startswith(word):
                    yield Completion(
                        cmd,
                        start_position=-len(word),
                        display=cmd,
                        display_meta='command'
                    )
            return

        # Check if we're in a multi-word command like "GRID PANEL"
        elif len(words) >= 1:
            # Try to match multi-word commands
            partial_cmd = ' '.join(words).upper()

            # Check if this looks like a file path command
            if any(text.upper().startswith(cmd) for cmd in self.file_commands):
                # Extract the partial path being typed
                if '"' in text:
                    # Inside quotes
                    last_quote = text.rfind('"')
                    partial_path = text[last_quote + 1:]
                elif len(words) > 1:
                    # After command, get the last word (partial path)
                    partial_path = words[-1]
                else:
                    # Just the command with trailing space
                    partial_path = ''

                # Use custom file completer for sandbox/ and memory/
                for completion in self._get_file_completions(partial_path):
                    yield completion

            # Check if this is a panel command
            elif any(partial_cmd.startswith(cmd) for cmd in self.panel_commands):
                # Suggest panel names
                if '"' in text or text.endswith(' '):
                    # Get current panels
                    panels = self.grid.get_panel_names()

                    # Extract partial panel name
                    if '"' in text:
                        last_quote = text.rfind('"')
                        partial_panel = text[last_quote + 1:]
                    else:
                        partial_panel = ''

                    for panel in panels:
                        if panel.startswith(partial_panel):
                            yield Completion(
                                panel,
                                start_position=-len(partial_panel),
                                display=f'"{panel}"',
                                display_meta='panel'
                            )

            # Continue suggesting multi-word commands
            else:
                for cmd in self.command_names:
                    if cmd.upper().startswith(partial_cmd) and cmd.upper() != partial_cmd:
                        # Suggest the rest of the command
                        remaining = cmd[len(partial_cmd):].lstrip()
                        if remaining:
                            yield Completion(
                                remaining,
                                start_position=0,
                                display=cmd,
                                display_meta='command'
                            )

    def _get_file_completions(self, partial_path):
        """
        Get file completions for sandbox/ and memory/ directories.

        Args:
            partial_path: Partial path typed by user

        Yields:
            Completion objects
        """
        # Determine which directory to search
        search_dir = None
        relative_path = ''

        if partial_path.startswith('sandbox/') or partial_path.startswith('sandbox\\'):
            search_dir = 'sandbox'
            relative_path = partial_path[8:]  # Remove 'sandbox/'
        elif partial_path.startswith('memory/') or partial_path.startswith('memory\\'):
            search_dir = 'memory'
            relative_path = partial_path[7:]  # Remove 'memory/'
        elif partial_path.lower().startswith('s') and 'sandbox'.startswith(partial_path.lower()):
            # Typing 's', 'sa', 'san', etc. - suggest 'sandbox/'
            yield Completion(
                'sandbox/',
                start_position=-len(partial_path),
                display='📁 sandbox/',
                display_meta='directory'
            )
        elif partial_path.lower().startswith('m') and 'memory'.startswith(partial_path.lower()):
            # Typing 'm', 'me', 'mem', etc. - suggest 'memory/'
            yield Completion(
                'memory/',
                start_position=-len(partial_path),
                display='📁 memory/',
                display_meta='directory'
            )
        elif not partial_path:
            # No path typed - suggest both directories
            yield Completion(
                'sandbox/',
                start_position=0,
                display='📁 sandbox/',
                display_meta='directory'
            )
            yield Completion(
                'memory/',
                start_position=0,
                display='📁 memory/',
                display_meta='directory'
            )
            return
        else:
            # Unknown path
            return

        # If we determined a search_dir, list its contents
        if not search_dir:
            return

        base_dir = self.root / search_dir

        if not base_dir.exists():
            return

        # Find matching files and directories
        try:
            if relative_path:
                # Search within subdirectory
                search_path = base_dir / relative_path
                if search_path.is_dir():
                    items = list(search_path.iterdir())
                else:
                    # Partial filename - search parent directory
                    parent = search_path.parent
                    name_part = search_path.name
                    if parent.exists():
                        items = [p for p in parent.iterdir()
                                if p.name.lower().startswith(name_part.lower())]
                    else:
                        items = []
            else:
                # List root of search_dir
                items = list(base_dir.iterdir())

            # Sort: directories first, then files
            items.sort(key=lambda p: (not p.is_dir(), p.name.lower()))

            for item in items:
                icon = self._get_file_icon(item)
                meta = self._get_file_meta(item)

                # Build the relative path from search_dir
                try:
                    rel_from_base = item.relative_to(base_dir)
                    if item.is_dir():
                        completion_text = f"{search_dir}/{rel_from_base}/"
                        display_text = f"{icon} {item.name}/"
                    else:
                        completion_text = f"{search_dir}/{rel_from_base}"
                        display_text = f"{icon} {item.name}"

                    yield Completion(
                        completion_text,
                        start_position=-len(partial_path),
                        display=display_text,
                        display_meta=meta
                    )
                except ValueError:
                    continue

        except PermissionError:
            pass

    def _get_file_icon(self, path):
        """Get icon for file type."""
        if path.is_dir():
            return self.file_icons['directory']

        suffix = path.suffix.lower()
        return self.file_icons.get(suffix, self.file_icons['default'])

    def _get_file_meta(self, path):
        """Get file metadata for display."""
        if path.is_file():
            size = path.stat().st_size
            return self._format_size(size)
        elif path.is_dir():
            try:
                count = len(list(path.iterdir()))
                return f"{count} items"
            except PermissionError:
                return "dir"
        return ""

    def _format_size(self, size):
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
