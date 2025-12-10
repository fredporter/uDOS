"""
uDOS v1.0.19 - Smart Autocomplete Service
Intelligent command, option, and argument suggestions for enhanced CLI experience
"""

import difflib
from typing import List, Tuple, Optional, Dict
from pathlib import Path


class AutocompleteService:
    """
    Smart autocomplete with fuzzy matching for commands, options, and arguments.
    Provides sub-50ms response time for instant suggestions.
    """

    def __init__(self, command_handler=None):
        """
        Initialize autocomplete service.

        Args:
            command_handler: Main CommandHandler instance for command metadata
        """
        self.command_handler = command_handler
        self._command_cache = {}
        self._option_cache = {}
        self._build_command_cache()

    def _build_command_cache(self):
        """Build command and option cache for fast lookups from commands.json."""
        import json
        from pathlib import Path
        
        # Load commands from commands.json
        try:
            commands_file = Path(__file__).parent.parent / 'data' / 'commands.json'
            with open(commands_file) as f:
                commands_data = json.load(f)
            
            # Build cache from loaded commands
            for cmd in commands_data.get('COMMANDS', []):
                cmd_name = cmd['NAME']
                description = cmd.get('DESCRIPTION', '').split('.')[0]  # First sentence
                syntax = cmd.get('SYNTAX', f"{cmd_name}")
                examples = cmd.get('EXAMPLES', [])
                subcommands = cmd.get('SUBCOMMANDS', {})
                
                # Extract options from SUBCOMMANDS first (preferred)
                options = []
                option_details = {}
                
                if subcommands:
                    for subcmd, subcmd_desc in subcommands.items():
                        # Clean up subcommand name (remove <> and parameter placeholders)
                        clean_subcmd = subcmd.strip('<>').split()[0].upper()
                        if clean_subcmd and clean_subcmd not in ['NAME', 'DESC', 'TOPIC', 'QUESTION']:
                            options.append(clean_subcmd)
                            option_details[clean_subcmd] = subcmd_desc
                
                # Fallback: Extract options from syntax if no SUBCOMMANDS
                if not options and '|' in syntax:
                    # Parse options from syntax alternatives
                    parts = syntax.split('|')
                    for part in parts:
                        words = part.strip().split()
                        if len(words) > 1 and words[0] == cmd_name:
                            option = words[1].strip('<>"[]')
                            if option and option.upper() not in ['<DESC>', '<TOPIC>', '<QUESTION>', '<NAME>']:
                                options.append(option.upper())
                
                self._command_cache[cmd_name] = {
                    'description': description[:60],  # Limit description length
                    'options': list(set(options)),  # Remove duplicates
                    'option_details': option_details,  # Store option descriptions
                    'usage': syntax.split('|')[0].strip(),  # First syntax variant
                    'examples': examples[:3]  # First 3 examples
                }
            
            print(f"✅ Loaded {len(self._command_cache)} commands from commands.json")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not load commands.json: {e}")
            print("   Using fallback command cache...")
            self._build_fallback_cache()
    
    def _build_fallback_cache(self):
        """Fallback command cache if commands.json fails to load."""
        # System commands
        system_commands = {
            'HELP': {
                'description': 'Display help information',
                'options': ['SEARCH', 'CATEGORY', 'RECENT', 'STATS', 'SESSION'],
                'usage': 'HELP [command]'
            },
            'STATUS': {
                'description': 'Show system status',
                'options': [],
                'usage': 'STATUS'
            },
            'REPAIR': {
                'description': 'Repair system issues',
                'options': [],
                'usage': 'REPAIR'
            },
            'CLEAR': {
                'description': 'Clear screen',
                'options': ['ALL', 'BUFFER', 'LAST', 'GRID', 'LOGS', 'HISTORY'],
                'usage': 'CLEAR [option]'
            },
            'BLANK': {
                'description': 'Clear screen (alias)',
                'options': ['ALL', 'BUFFER', 'LAST'],
                'usage': 'BLANK [option]'
            },
            'THEME': {
                'description': 'Manage color themes',
                'options': ['LIST', 'SET', 'INFO', 'ACCESSIBILITY', 'CONTRAST'],
                'usage': 'THEME <option>'
            },
            'PALETTE': {
                'description': 'Show color palette',
                'options': [],
                'usage': 'PALETTE'
            },
            'VIEWPORT': {
                'description': 'Adjust viewport settings',
                'options': [],
                'usage': 'VIEWPORT [width] [height]'
            },
            'CONFIG': {
                'description': 'Show configuration',
                'options': [],
                'usage': 'CONFIG'
            },
            'SETTINGS': {
                'description': 'Manage user settings',
                'options': [],
                'usage': 'SETTINGS'
            },
            'HISTORY': {
                'description': 'Command history',
                'options': ['SEARCH', 'STATS', 'CLEAR', 'EXPORT', 'RECENT'],
                'usage': 'HISTORY [option]'
            },
            'REBOOT': {
                'description': 'Restart uDOS',
                'options': [],
                'usage': 'REBOOT'
            },
            'DASHBOARD': {
                'description': 'Launch dashboard',
                'options': ['CLI', 'WEB'],
                'usage': 'DASHBOARD [mode]'
            },
            'DEBUG': {
                'description': 'Enter debug mode',
                'options': ['STATUS', 'HELP'],
                'usage': 'DEBUG [option]'
            },
            'BREAK': {
                'description': 'Set breakpoint',
                'options': ['CLEAR', 'LIST'],
                'usage': 'BREAK [line]'
            },
            'STEP': {
                'description': 'Step through code',
                'options': ['INTO', 'OUT'],
                'usage': 'STEP [option]'
            },
            'CONTINUE': {
                'description': 'Continue execution',
                'options': [],
                'usage': 'CONTINUE'
            },
            'INSPECT': {
                'description': 'Inspect variables',
                'options': [],
                'usage': 'INSPECT [variable]'
            },
            'WATCH': {
                'description': 'Watch expressions',
                'options': ['LIST', 'CLEAR'],
                'usage': 'WATCH [expression]'
            },
            'STACK': {
                'description': 'Show call stack',
                'options': [],
                'usage': 'STACK'
            },
            'PROFILE': {
                'description': 'Performance profiling',
                'options': [],
                'usage': 'PROFILE'
            },
        }

        # File commands
        file_commands = {
            'FILE': {
                'description': 'File operations',
                'options': ['LIST', 'NEW', 'DELETE', 'COPY', 'MOVE', 'RENAME',
                           'SHOW', 'EDIT', 'RUN', 'PICK', 'RECENT', 'PREVIEW', 'INFO'],
                'usage': 'FILE <operation> [args]'
            },
            'LIST': {
                'description': 'List files',
                'options': [],
                'usage': 'LIST [path]'
            },
            'EDIT': {
                'description': 'Edit file',
                'options': [],
                'usage': 'EDIT <filename>'
            },
            'RUN': {
                'description': 'Run script',
                'options': [],
                'usage': 'RUN <script>'
            },
            'PICK': {
                'description': 'Interactive file picker',
                'options': [],
                'usage': 'PICK [pattern]'
            },
        }

        # Map commands
        map_commands = {
            'MAP': {
                'description': 'Map navigation',
                'options': ['STATUS', 'VIEW', 'CELL', 'CITIES', 'METRO', 'NAVIGATE',
                           'LOCATE', 'LAYERS', 'GOTO', 'TELETEXT', 'WEB'],
                'usage': 'MAP <option> [args]'
            },
        }

        # Assistant commands
        assistant_commands = {
            'ASK': {
                'description': 'Ask AI assistant',
                'options': [],
                'usage': 'ASK <question>'
            },
            'ANALYZE': {
                'description': 'Analyze code/content',
                'options': [],
                'usage': 'ANALYZE <target>'
            },
        }

        # v1.0.18 Game/XP commands
        game_commands = {
            'XP': {
                'description': 'Experience system',
                'options': ['STATUS', 'GAIN', 'HISTORY', 'LEADERBOARD'],
                'usage': 'XP [option]'
            },
            'INVENTORY': {
                'description': 'Manage inventory',
                'options': ['LIST', 'ADD', 'REMOVE', 'USE'],
                'usage': 'INVENTORY [option]'
            },
            'BARTER': {
                'description': 'Trading system',
                'options': ['OFFER', 'REQUEST', 'ACCEPT', 'HISTORY'],
                'usage': 'BARTER [option]'
            },
            'SURVIVAL': {
                'description': 'Survival metrics',
                'options': ['STATUS', 'UPDATE', 'HISTORY'],
                'usage': 'SURVIVAL [option]'
            },
            'SCENARIO': {
                'description': 'Adventure scenarios',
                'options': ['LIST', 'START', 'STATUS', 'PLAY'],
                'usage': 'SCENARIO [option]'
            },
            'KNOWLEDGE': {
                'description': 'Knowledge base',
                'options': ['SEARCH', 'LIST', 'VIEW'],
                'usage': 'KNOWLEDGE [option]'
            },
        }

        # Combine all commands
        self._command_cache = {
            **system_commands,
            **file_commands,
            **map_commands,
            **assistant_commands,
            **game_commands
        }
        print(f"✅ Using fallback cache with {len(self._command_cache)} commands")

    def get_command_suggestions(self, partial: str, max_results: int = 10) -> List[Dict]:
        """
        Get command suggestions based on partial input.

        Args:
            partial: Partial command string
            max_results: Maximum number of suggestions

        Returns:
            List of suggestion dictionaries with command, description, score
        """
        if not partial:
            # Return most common commands when empty
            return [
                {'command': 'HELP', 'description': 'Display help information', 'score': 1.0},
                {'command': 'FILE', 'description': 'File operations', 'score': 1.0},
                {'command': 'MAP', 'description': 'Map navigation', 'score': 1.0},
                {'command': 'XP', 'description': 'Experience system', 'score': 1.0},
                {'command': 'STATUS', 'description': 'Show system status', 'score': 1.0},
            ]

        partial_upper = partial.upper()
        suggestions = []

        # Exact prefix matches (highest priority)
        for cmd, meta in self._command_cache.items():
            if cmd.startswith(partial_upper):
                suggestions.append({
                    'command': cmd,
                    'description': meta['description'],
                    'usage': meta.get('usage', ''),
                    'score': 1.0,
                    'match_type': 'prefix'
                })

        # Fuzzy matches (lower priority)
        if len(suggestions) < max_results:
            for cmd, meta in self._command_cache.items():
                if cmd not in [s['command'] for s in suggestions]:
                    ratio = self._fuzzy_score(partial_upper, cmd)
                    if ratio >= 0.6:  # Threshold for fuzzy matches
                        suggestions.append({
                            'command': cmd,
                            'description': meta['description'],
                            'usage': meta.get('usage', ''),
                            'score': ratio * 0.8,  # Slightly lower score for fuzzy
                            'match_type': 'fuzzy'
                        })

        # Sort by score and limit results
        suggestions.sort(key=lambda x: x['score'], reverse=True)
        return suggestions[:max_results]

    def get_option_suggestions(self, command: str, partial: str = '', max_results: int = 10) -> List[Dict]:
        """
        Get option/subcommand suggestions for a command.

        Args:
            command: Main command (e.g., 'THEME', 'HELP')
            partial: Partial option string
            max_results: Maximum number of suggestions

        Returns:
            List of option suggestion dictionaries with descriptions
        """
        command_upper = command.upper()
        if command_upper not in self._command_cache:
            return []

        options = self._command_cache[command_upper].get('options', [])
        option_details = self._command_cache[command_upper].get('option_details', {})
        
        if not options:
            return []

        # Option descriptions (common patterns as fallback)
        default_descriptions = {
            'LIST': 'Show all available items',
            'NEW': 'Create new item',
            'DELETE': 'Remove item',
            'SET': 'Set or change value',
            'GET': 'Retrieve value',
            'INFO': 'Show detailed information',
            'HELP': 'Show help for this command',
            'SEARCH': 'Search for items',
            'STATS': 'Show statistics',
            'CLEAR': 'Clear or reset',
            'EXPORT': 'Export data',
            'IMPORT': 'Import data',
            'RECENT': 'Show recent items',
            'ALL': 'Apply to all items',
            'EDIT': 'Edit item',
            'SHOW': 'Display item',
            'HIDE': 'Hide item',
            'ENABLE': 'Enable feature',
            'DISABLE': 'Disable feature',
            'STATUS': 'Show current status',
            'RUN': 'Execute or run',
            'COPY': 'Copy item',
            'MOVE': 'Move item',
            'RENAME': 'Rename item',
        }

        if not partial:
            # Return all options when no partial
            return [{
                'option': opt,
                'command': command_upper,
                'description': option_details.get(opt, default_descriptions.get(opt, f'{command_upper} {opt.lower()}')),
                'score': 1.0
            } for opt in options]

        partial_upper = partial.upper()
        suggestions = []

        # Exact prefix matches
        for opt in options:
            if opt.startswith(partial_upper):
                suggestions.append({
                    'option': opt,
                    'command': command_upper,
                    'description': option_details.get(opt, default_descriptions.get(opt, f'{command_upper} {opt.lower()}')),
                    'score': 1.0,
                    'match_type': 'prefix'
                })

        # Fuzzy matches
        if len(suggestions) < max_results:
            for opt in options:
                if opt not in [s['option'] for s in suggestions]:
                    ratio = self._fuzzy_score(partial_upper, opt)
                    if ratio >= 0.6:
                        suggestions.append({
                            'option': opt,
                            'command': command_upper,
                            'description': option_details.get(opt, default_descriptions.get(opt, f'{command_upper} {opt.lower()}')),
                            'score': ratio * 0.8,
                            'match_type': 'fuzzy'
                        })

        suggestions.sort(key=lambda x: x['score'], reverse=True)
        return suggestions[:max_results]

    def get_argument_suggestions(self, command: str, option: str = '', context: str = '') -> List[Dict]:
        """
        Get argument suggestions based on command and context.

        Args:
            command: Main command
            option: Subcommand/option
            context: Current argument context

        Returns:
            List of argument suggestions
        """
        command_upper = command.upper()

        # File path suggestions
        if command_upper in ['EDIT', 'RUN', 'SHOW', 'DELETE', 'COPY', 'MOVE']:
            return self._get_file_path_suggestions(context)

        # Theme suggestions
        if command_upper == 'THEME' and option.upper() == 'SET':
            return [
                {'argument': 'dungeon', 'type': 'theme'},
                {'argument': 'hacker', 'type': 'theme'},
                {'argument': 'apocalypse', 'type': 'theme'},
                {'argument': 'teletext', 'type': 'theme'},
            ]

        # Map cell references
        if command_upper == 'MAP' and option.upper() in ['GOTO', 'CELL']:
            return [
                {'argument': 'A1', 'type': 'cell_ref', 'description': 'NW corner'},
                {'argument': 'T135', 'type': 'cell_ref', 'description': 'Center'},
                {'argument': 'RL270', 'type': 'cell_ref', 'description': 'SE corner'},
            ]

        return []

    def _get_file_path_suggestions(self, partial_path: str) -> List[Dict]:
        """
        Get file path suggestions based on partial path.

        Args:
            partial_path: Partial file path

        Returns:
            List of file path suggestions
        """
        try:
            if not partial_path:
                # Suggest common directories
                return [
                    {'argument': 'memory/', 'type': 'directory'},
                    {'argument': 'memory/', 'type': 'directory'},
                    {'argument': 'scripts/', 'type': 'directory'},
                ]

            path = Path(partial_path)
            if partial_path.endswith('/') or path.is_dir():
                # List directory contents
                search_dir = path if path.is_dir() else path.parent
                suggestions = []
                for item in sorted(search_dir.iterdir()):
                    suggestions.append({
                        'argument': str(item),
                        'type': 'directory' if item.is_dir() else 'file',
                        'size': item.stat().st_size if item.is_file() else None
                    })
                return suggestions[:10]
            else:
                # Match files in parent directory
                parent = path.parent if path.parent.exists() else Path('.')
                name_part = path.name
                suggestions = []
                for item in parent.iterdir():
                    if item.name.startswith(name_part):
                        suggestions.append({
                            'argument': str(item),
                            'type': 'directory' if item.is_dir() else 'file',
                            'score': 1.0
                        })
                return suggestions[:10]

        except Exception:
            return []

    def _fuzzy_score(self, pattern: str, text: str) -> float:
        """
        Calculate fuzzy match score using difflib.

        Args:
            pattern: Search pattern
            text: Text to match against

        Returns:
            Score between 0.0 and 1.0
        """
        return difflib.SequenceMatcher(None, pattern, text).ratio()

    def format_suggestion(self, suggestion: Dict, index: int, is_selected: bool = False) -> str:
        """
        Format a suggestion for display in CLI.

        Args:
            suggestion: Suggestion dictionary
            index: Suggestion index
            is_selected: Whether this suggestion is selected

        Returns:
            Formatted suggestion string
        """
        marker = '→' if is_selected else ' '

        if 'command' in suggestion:
            # Command suggestion
            cmd = suggestion['command']
            desc = suggestion.get('description', '')
            score_bar = '█' * int(suggestion['score'] * 10)
            return f"{marker} {index}. {cmd:<15} {score_bar:<10} {desc}"

        elif 'option' in suggestion:
            # Option suggestion
            opt = suggestion['option']
            cmd = suggestion.get('command', '')
            return f"{marker} {index}. {cmd} {opt}"

        elif 'argument' in suggestion:
            # Argument suggestion
            arg = suggestion['argument']
            arg_type = suggestion.get('type', 'value')
            icon = '📁' if arg_type == 'directory' else '📄' if arg_type == 'file' else '💡'
            return f"{marker} {index}. {icon} {arg}"

        return f"{marker} {index}. {suggestion}"
