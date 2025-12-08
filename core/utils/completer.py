# uDOS v1.0.6 - Advanced Context-Aware Completer with Intelligent Suggestions

from prompt_toolkit.completion import Completer, Completion, PathCompleter
from prompt_toolkit.document import Document
from pathlib import Path
import os
import difflib
from typing import List, Optional, Tuple


class AdvancedCompleter(Completer):
    """
    Advanced context-aware completer for uDOS commands with intelligent suggestions,
    fuzzy matching, and command history integration.
    """

    def __init__(self, parser, grid, command_history=None):
        self.parser = parser
        self.grid = grid
        self.command_history = command_history
        self.command_names = parser.get_command_names()
        self.path_completer = PathCompleter(expanduser=True)
        self.root = Path.cwd()

        # Commands that expect file paths
        self.file_commands = ['LOAD', 'SAVE', 'RUN', 'EDIT', 'CATALOG', 'SHOW']

        # Commands that expect panel names
        self.panel_commands = ['ANALYZE', 'GRID PANEL CREATE', 'GRID PANEL DELETE',
                               'GRID PANEL SELECT']

        # Enhanced: Smart parameter completion definitions
        self.output_subcommands = ['START', 'STOP', 'STATUS', 'LIST', 'HEALTH', 'RESTART']
        self.output_servers = ['typo', 'dashboard', 'terminal', 'teletext', 'desktop', 'font-editor', 'cmd']

        self.map_subcommands = ['STATUS', 'VIEW', 'LAYER', 'GOTO', 'LOCATE', 'MOVE']
        self.map_layers = ['SURFACE', 'CLOUD-OC', 'SATELLITE-OC', 'DUNGEON-1']

        self.file_subcommands = ['NEW', 'DELETE', 'COPY', 'MOVE', 'RENAME', 'SHOW', 'EDIT', 'RUN']

        self.history_subcommands = ['SEARCH', 'STATS', 'CLEAR', 'EXPORT', 'RECENT']

        # Allowed directories for file operations
        self.allowed_dirs = ['sandbox', 'memory']

        # File type icons
        self.file_icons = {
            '.py': '🐍',
            '.upy': '📜',
            '.usc': '📜',
            '.md': '📝',
            '.txt': '📄',
            '.json': '⚙️',
            '.log': '📋',
            '.UDO': '🔧',
            'directory': '📁',
            'default': '📄'
        }

        # Fuzzy matching threshold
        self.fuzzy_threshold = 0.6

    def get_completions(self, document, complete_event):
        """
        Generate completions based on the current context with advanced intelligence.
        """
        text = document.text_before_cursor
        words = text.split()

        # If empty, suggest recent commands from history
        if not words:
            yield from self._get_recent_command_suggestions()
            return

        # Single word without space = command completion with fuzzy matching
        if len(words) == 1 and not text.endswith(' '):
            word = words[0].upper()
            yield from self._get_command_completions(word)
            return

        # Multi-word context - enhanced parameter completion
        if len(words) >= 1:
            command = words[0].upper()

            # Enhanced OUTPUT command completion
            if command == 'OUTPUT':
                yield from self._complete_output_command(words, text)

            # Enhanced MAP command completion
            elif command == 'MAP':
                yield from self._complete_map_command(words, text)

            # Enhanced FILE command completion
            elif command == 'FILE':
                yield from self._complete_file_command(words, text)

            # Enhanced HISTORY command completion
            elif command == 'HISTORY':
                yield from self._complete_history_command(words, text)

            # File path commands
            elif command in self.file_commands:
                yield from self._complete_file_paths(words, text)

            # Panel commands
            elif any(' '.join(words).upper().startswith(cmd) for cmd in self.panel_commands):
                yield from self._complete_panel_names(words, text)

            # General multi-word command completion
            else:
                yield from self._complete_multiword_commands(words, text)

    def _get_recent_command_suggestions(self):
        """Get recent command suggestions from command history."""
        if not self.command_history:
            return []

        try:
            recent_commands = self.command_history.get_suggestions('', limit=8)
            for i, cmd in enumerate(recent_commands):
                yield Completion(
                    cmd,
                    start_position=0,
                    display=f"📋 {cmd}",
                    display_meta=f"recent #{i+1}"
                )
        except:
            pass  # Graceful fallback if history unavailable

    def _get_command_completions(self, partial_cmd: str):
        """Enhanced command completion with fuzzy matching."""
        exact_matches = []
        fuzzy_matches = []

        for cmd in self.command_names:
            cmd_upper = cmd.upper()

            # Exact prefix match (highest priority)
            if cmd_upper.startswith(partial_cmd):
                exact_matches.append((cmd, 1.0))
            # Fuzzy match
            else:
                similarity = difflib.SequenceMatcher(None, partial_cmd, cmd_upper).ratio()
                if similarity >= self.fuzzy_threshold:
                    fuzzy_matches.append((cmd, similarity))

        # Sort fuzzy matches by similarity
        fuzzy_matches.sort(key=lambda x: x[1], reverse=True)

        # Yield exact matches first
        for cmd, score in exact_matches:
            yield Completion(
                cmd,
                start_position=-len(partial_cmd),
                display=cmd,
                display_meta='command'
            )

        # Then fuzzy matches with similarity scores
        for cmd, score in fuzzy_matches[:5]:  # Limit fuzzy results
            yield Completion(
                cmd,
                start_position=-len(partial_cmd),
                display=f"{cmd} ~{score:.0%}",
                display_meta=f'fuzzy match'
            )

    def _complete_output_command(self, words: List[str], text: str):
        """Smart completion for OUTPUT commands."""
        if len(words) == 1 or (len(words) == 2 and not text.endswith(' ')):
            # Suggest OUTPUT subcommands
            partial = words[1] if len(words) == 2 else ''
            for subcmd in self.output_subcommands:
                if subcmd.startswith(partial.upper()):
                    help_text = self._get_output_help(subcmd)
                    yield Completion(
                        subcmd,
                        start_position=-len(partial),
                        display=f"⚙️ OUTPUT {subcmd}",
                        display_meta=help_text
                    )

        elif len(words) >= 2:
            subcmd = words[1].upper()

            # Server-specific completions
            if subcmd in ['START', 'STOP', 'STATUS'] and (len(words) == 2 or not text.endswith(' ')):
                partial = words[2] if len(words) == 3 else ''
                for server in self.output_servers:
                    if server.startswith(partial.lower()):
                        yield Completion(
                            server,
                            start_position=-len(partial),
                            display=f"🌐 {server}",
                            display_meta='web server'
                        )

            # Port number suggestions for START command
            elif subcmd == 'START' and len(words) >= 3 and '--port' in text:
                common_ports = ['3000', '8000', '8080', '5000', '9000']
                for port in common_ports:
                    yield Completion(
                        port,
                        start_position=0,
                        display=f":{port}",
                        display_meta='common port'
                    )

    def _complete_map_command(self, words: List[str], text: str):
        """Smart completion for MAP commands."""
        if len(words) == 1 or (len(words) == 2 and not text.endswith(' ')):
            partial = words[1] if len(words) == 2 else ''
            for subcmd in self.map_subcommands:
                if subcmd.startswith(partial.upper()):
                    help_text = self._get_map_help(subcmd)
                    yield Completion(
                        subcmd,
                        start_position=-len(partial),
                        display=f"🗺️ MAP {subcmd}",
                        display_meta=help_text
                    )

        elif len(words) >= 2:
            subcmd = words[1].upper()

            # Layer completions
            if subcmd == 'LAYER' and (len(words) == 2 or not text.endswith(' ')):
                partial = words[2] if len(words) == 3 else ''
                for layer in self.map_layers:
                    if layer.startswith(partial.upper()):
                        yield Completion(
                            layer,
                            start_position=-len(partial),
                            display=f"🌍 {layer}",
                            display_meta='map layer'
                        )

    def _complete_file_command(self, words: List[str], text: str):
        """Smart completion for FILE commands."""
        if len(words) == 1 or (len(words) == 2 and not text.endswith(' ')):
            partial = words[1] if len(words) == 2 else ''
            for subcmd in self.file_subcommands:
                if subcmd.startswith(partial.upper()):
                    help_text = self._get_file_help(subcmd)
                    yield Completion(
                        subcmd,
                        start_position=-len(partial),
                        display=f"📁 FILE {subcmd}",
                        display_meta=help_text
                    )

    def _complete_history_command(self, words: List[str], text: str):
        """Smart completion for HISTORY commands."""
        if len(words) == 1 or (len(words) == 2 and not text.endswith(' ')):
            partial = words[1] if len(words) == 2 else ''
            for subcmd in self.history_subcommands:
                if subcmd.startswith(partial.upper()):
                    help_text = self._get_history_help(subcmd)
                    yield Completion(
                        subcmd,
                        start_position=-len(partial),
                        display=f"📜 HISTORY {subcmd}",
                        display_meta=help_text
                    )

    def _complete_file_paths(self, words: List[str], text: str):
        """Enhanced file path completion."""
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

        # Use enhanced file completer
        yield from self._get_file_completions(partial_path)

    def _complete_panel_names(self, words: List[str], text: str):
        """Smart completion for panel names."""
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
                    display=f'📋 "{panel}"',
                    display_meta='panel'
                )

    def _complete_multiword_commands(self, words: List[str], text: str):
        """Enhanced multi-word command completion."""
        partial_cmd = ' '.join(words).upper()

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

    def _get_output_help(self, subcmd: str) -> str:
        """Get help text for OUTPUT subcommands."""
        help_texts = {
            'START': 'Start a web server',
            'STOP': 'Stop a running server',
            'STATUS': 'Show server status',
            'LIST': 'List available servers',
            'HEALTH': 'Check server health',
            'RESTART': 'Restart a server'
        }
        return help_texts.get(subcmd, 'Server management')

    def _get_map_help(self, subcmd: str) -> str:
        """Get help text for MAP subcommands."""
        help_texts = {
            'STATUS': 'Show current location',
            'VIEW': 'View area around you',
            'LAYER': 'Switch map layer',
            'GOTO': 'Navigate to location',
            'LOCATE': 'Find coordinates',
            'MOVE': 'Move to new position'
        }
        return help_texts.get(subcmd, 'Map navigation')

    def _get_file_help(self, subcmd: str) -> str:
        """Get help text for FILE subcommands."""
        help_texts = {
            'NEW': 'Create new file',
            'DELETE': 'Delete file',
            'COPY': 'Copy file',
            'MOVE': 'Move file',
            'RENAME': 'Rename file',
            'SHOW': 'Display file',
            'EDIT': 'Edit file',
            'RUN': 'Execute file'
        }
        return help_texts.get(subcmd, 'File operation')

    def _get_history_help(self, subcmd: str) -> str:
        """Get help text for HISTORY subcommands."""
        help_texts = {
            'SEARCH': 'Search command history',
            'STATS': 'Show usage statistics',
            'CLEAR': 'Clear old commands',
            'EXPORT': 'Export to file',
            'RECENT': 'Show recent commands'
        }
        return help_texts.get(subcmd, 'History management')

    def _get_file_completions(self, partial_path):
        """
        Get file completions for memory/ directory (sandbox deprecated).

        Args:
            partial_path: Partial path typed by user

        Yields:
            Completion objects
        """
        # Determine which directory to search
        search_dir = None
        relative_path = ''

        if partial_path.startswith('sandbox/') or partial_path.startswith('sandbox\\'):
            # Sandbox deprecated - redirect to memory
            yield Completion(
                'memory/',
                start_position=-len(partial_path),
                display='📁 memory/ (sandbox deprecated)',
                display_meta='use memory/ instead'
            )
            return
        elif partial_path.startswith('memory/') or partial_path.startswith('memory\\'):
            search_dir = 'memory'
            relative_path = partial_path[7:]  # Remove 'memory/'
        elif partial_path.lower().startswith('s') and 'sandbox'.startswith(partial_path.lower()):
            # Typing 's', 'sa', 'san', etc. - suggest memory instead
            yield Completion(
                'memory/',
                start_position=-len(partial_path),
                display='📁 memory/ (not sandbox)',
                display_meta='sandbox deprecated'
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
            # No path typed - suggest memory directory
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


# Backward compatibility alias
uDOSCompleter = AdvancedCompleter
