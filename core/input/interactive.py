"""
uDOS Interactive Command System v1.1.0
Provides smart prompts, file pickers, and option selectors for commands
Now using unified selector with cross-platform compatibility
"""

import os
from typing import List, Optional, Callable
from pathlib import Path


class InteractivePrompt:
    """Smart interactive prompts for command parameters"""

    def __init__(self, use_arrow_keys: bool = True):
        """
        Initialize interactive prompt.

        Args:
            use_arrow_keys: Use arrow-key navigation (default: True)
        """
        self.history = []
        self.use_arrow_keys = use_arrow_keys

    def ask_choice(self, prompt: str = "", choices: List[str] = None, default: Optional[str] = None, message: Optional[str] = None) -> str:
        """
        Present a list of choices and get user selection

        Args:
            prompt: Question to ask
            choices: List of valid options
            default: Default choice if user presses enter
            message: Optional additional message (ignored, kept for compatibility)

        Returns:
            Selected choice
        """
        # Use unified selector (v1.1.0) if enabled
        if self.use_arrow_keys:
            try:
                from core.ui.unified_selector import select_single

                # Find default index
                default_index = 0
                if default and default in choices:
                    default_index = choices.index(default)

                result = select_single(
                    title=prompt or "Select Option",
                    items=choices,
                    default_index=default_index
                )

                if result:  # If not cancelled
                    return result
                # Fall through to text mode if cancelled
            except (ImportError, Exception) as e:
                # Fall back to text mode if selector fails
                print(f"⚠️  Selector unavailable ({e}), using text mode")
                pass

        # Text-based fallback mode
        print(f"\n{prompt}")
        for i, choice in enumerate(choices, 1):
            marker = "→" if default and choice == default else " "
            print(f"  {marker} {i}. {choice}")

        if default:
            print(f"\nPress Enter for default [{default}], or choose 1-{len(choices)}")
        else:
            print(f"\nChoose 1-{len(choices)}")

        while True:
            try:
                response = input("🌀 ").strip()

                # Empty response = default
                if not response and default:
                    return default

                # Numeric selection
                if response.isdigit():
                    idx = int(response) - 1
                    if 0 <= idx < len(choices):
                        return choices[idx]

                # Text match (case-insensitive)
                for choice in choices:
                    if response.lower() == choice.lower():
                        return choice

                print(f"❌ Invalid choice. Please enter 1-{len(choices)} or a valid option name.")

            except (KeyboardInterrupt, EOFError):
                print("\n❌ Cancelled")
                return ""

    def ask_text(self, prompt: str, default: Optional[str] = None,
                 validator: Optional[Callable] = None) -> str:
        """
        Ask for text input with optional validation

        Args:
            prompt: Question to ask
            default: Default value
            validator: Function to validate input (returns True if valid)

        Returns:
            User input
        """
        default_msg = f" [{default}]" if default else ""
        print(f"\n{prompt}{default_msg}")

        while True:
            try:
                response = input("🌀 ").strip()

                if not response and default:
                    response = default

                if validator and not validator(response):
                    print("❌ Invalid input. Please try again.")
                    continue

                return response

            except (KeyboardInterrupt, EOFError):
                print("\n❌ Cancelled")
                return ""

    def ask_yes_no(self, prompt: str, default: bool = True) -> bool:
        """
        Ask a yes/no question

        Args:
            prompt: Question to ask
            default: Default answer

        Returns:
            True for yes, False for no
        """
        default_str = "Y/n" if default else "y/N"
        print(f"\n{prompt} [{default_str}]")

        try:
            response = input("🌀 ").strip().lower()

            if not response:
                return default

            return response in ['y', 'yes', 'true', '1']

        except (KeyboardInterrupt, EOFError):
            print("\n❌ Cancelled")
            return False

    def ask_file(self, prompt: str, extension: Optional[str] = None,
                 directory: Optional[str] = None) -> str:
        """
        Smart file picker with directory browsing

        Args:
            prompt: Question to ask
            extension: Filter by file extension (e.g., '.md', '.py')
            directory: Starting directory

        Returns:
            Selected file path
        """
        current_dir = Path(directory) if directory else Path.cwd()

        while True:
            print(f"\n{prompt}")
            print(f"📁 Current: {current_dir}")
            print()

            # List directories and files
            items = []

            # Add parent directory option
            if current_dir != current_dir.parent:
                items.append(("📁 ..", current_dir.parent, True))

            # Add subdirectories
            try:
                for item in sorted(current_dir.iterdir()):
                    if item.is_dir() and not item.name.startswith('.'):
                        items.append((f"📁 {item.name}/", item, True))
            except PermissionError:
                pass

            # Add files
            try:
                for item in sorted(current_dir.iterdir()):
                    if item.is_file():
                        if extension and not item.name.endswith(extension):
                            continue
                        if item.name.startswith('.'):
                            continue
                        items.append((f"📄 {item.name}", item, False))
            except PermissionError:
                pass

            # Display options
            for i, (label, path, is_dir) in enumerate(items, 1):
                print(f"  {i}. {label}")

            print("\n  Type number to select, 'q' to cancel, or path directly")

            try:
                response = input("🌀 ").strip()

                if response.lower() == 'q':
                    return ""

                # Direct path input
                if '/' in response or '\\' in response:
                    path = Path(response)
                    if path.exists():
                        if path.is_file():
                            return str(path)
                        else:
                            current_dir = path
                            continue

                # Numeric selection
                if response.isdigit():
                    idx = int(response) - 1
                    if 0 <= idx < len(items):
                        label, path, is_dir = items[idx]
                        if is_dir:
                            current_dir = path
                        else:
                            return str(path)

                print("❌ Invalid selection")

            except (KeyboardInterrupt, EOFError):
                print("\n❌ Cancelled")
                return ""


class SmartCommandHandler:
    """Enhances commands with interactive prompts"""

    def __init__(self, command_handler=None):
        self.prompt = InteractivePrompt()
        self.command_handler = command_handler

    def handle_output_smart(self, params: List[str]) -> str:
        """
        Smart OUTPUT command with interactive prompts

        Args:
            params: Parsed parameters from command

        Returns:
            Command result string
        """
        subcommand = params[0].upper() if params else ''

        # No subcommand? Ask for it
        if not subcommand:
            subcommand = self.prompt.ask_choice(
                "What would you like to do with output interfaces?",
                choices=['START', 'STOP', 'STATUS', 'LIST'],
                default='STATUS'
            )

            if not subcommand:
                return "❌ Cancelled"

            # Update params
            params = [subcommand] + params[1:] if len(params) > 1 else [subcommand]

        # Handle START subcommand with prompts
        if subcommand == 'START':
            interface = params[1] if len(params) > 1 else ''

            # No interface specified? Ask for it
            if not interface:
                available = ['typo', 'cmd', 'markdown-viewer', 'font-editor', 'dashboard']
                interface = self.prompt.ask_choice(
                    "Which output interface would you like to start?",
                    choices=available,
                    default='markdown-viewer'
                )

                if not interface:
                    return "❌ Cancelled"

                # Update params
                params = [subcommand, interface] + params[2:] if len(params) > 2 else [subcommand, interface]

            # Ask about port if not specified
            has_port = any('--port' in str(p) for p in params)
            if not has_port:
                use_custom_port = self.prompt.ask_yes_no(
                    "Use custom port? (default will be used otherwise)",
                    default=False
                )

                if use_custom_port:
                    port_input = self.prompt.ask_text(
                        "Port number?",
                        default="8080",
                        validator=lambda x: x.isdigit() and 1024 <= int(x) <= 65535
                    )
                    if port_input:
                        params.append(f"--port={port_input}")

            # Ask about browser if not specified
            has_no_browser = '--no-browser' in params
            if not has_no_browser:
                open_browser = self.prompt.ask_yes_no(
                    "Open browser automatically?",
                    default=True
                )

                if not open_browser:
                    params.append('--no-browser')

        # Call the original handler with updated params
        if self.command_handler:
            return self.command_handler.handle_output(params)
        else:
            return f"[SYSTEM|OUTPUT*{'*'.join(params)}]"

    def handle_edit_smart(self, params: List[str]) -> str:
        """
        Smart EDIT command with file picker

        Args:
            params: Parsed parameters from command

        Returns:
            Command result string
        """
        filename = params[0] if params else ''

        # No file specified? Show picker
        if not filename:
            filename = self.prompt.ask_file(
                "Which file would you like to edit?",
                directory=os.getcwd()
            )

            if not filename:
                return "❌ Cancelled"

        # Call original handler
        if self.command_handler:
            return self.command_handler.handle_edit(filename)
        else:
            return f"[FILE|EDIT*{filename}]"

    def handle_load_smart(self, params: List[str]) -> str:
        """
        Smart LOAD command with file picker

        Args:
            params: Parsed parameters from command

        Returns:
            Command result string
        """
        filename = params[0] if params else ''
        panel = params[1] if len(params) > 1 else ''

        # No file specified? Show picker
        if not filename:
            filename = self.prompt.ask_file(
                "Which file would you like to load?",
                extension='.md',
                directory=os.getcwd()
            )

            if not filename:
                return "❌ Cancelled"

        # Ask which panel if not specified
        if not panel:
            panel = self.prompt.ask_choice(
                "Load into which panel?",
                choices=['MAIN', 'LEFT', 'RIGHT', 'TOP', 'BOTTOM'],
                default='MAIN'
            )

            if not panel:
                return "❌ Cancelled"

        # Call original handler
        if self.command_handler:
            # This would need to be adapted based on actual command handler interface
            return f"[FILE|LOAD*{filename}*{panel}]"
        else:
            return f"[FILE|LOAD*{filename}*{panel}]"
