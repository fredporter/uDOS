"""
uDOS v1.0.29 - Input Manager
Unified input system for all uDOS commands with smart prompts and validation
"""

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.styles import Style
from typing import List, Optional, Any, Dict
from pathlib import Path
import json


class PathValidator(Validator):
    """Validator for file paths"""

    def __init__(self, must_exist: bool = False):
        self.must_exist = must_exist

    def validate(self, document):
        text = document.text
        if self.must_exist and text:
            path = Path(text)
            if not path.exists():
                raise ValidationError(message=f"Path does not exist: {text}")


class RequiredValidator(Validator):
    """Validator for required fields"""

    def validate(self, document):
        text = document.text.strip()
        if not text:
            raise ValidationError(message="This field is required")


class InputManager:
    """
    Unified input system for all uDOS commands.
    Provides consistent, theme-aware prompts with validation and smart defaults.
    """

    def __init__(self, theme: str = 'dungeon'):
        """
        Initialize input manager with theme-aware styling.

        Args:
            theme: Theme name for prompt styling
        """
        self.theme = theme
        self.style = self._create_style()

    def _create_style(self) -> Style:
        """Create prompt_toolkit style based on theme"""
        # Theme-aware color schemes
        theme_colors = {
            'dungeon': {
                'prompt': '#00ff00',      # Green
                'input': '#00ff00',       # Green
                'default': '#888888',     # Gray
            },
            'hacker': {
                'prompt': '#00ff00',      # Matrix green
                'input': '#00ff00',
                'default': '#00aa00',
            },
            'galaxy': {
                'prompt': '#00ffff',      # Cyan
                'input': '#ffffff',       # White
                'default': '#888888',
            },
            'foundation': {
                'prompt': '#ffaa00',      # Orange
                'input': '#ffffff',
                'default': '#888888',
            },
        }

        colors = theme_colors.get(self.theme, theme_colors['dungeon'])

        return Style.from_dict({
            'prompt': colors['prompt'],
            'input': colors['input'],
            'default': colors['default'],
        })

    def prompt_user(self,
                   message: str,
                   default: Optional[str] = None,
                   required: bool = False,
                   validator: Optional[Validator] = None,
                   multiline: bool = False) -> str:
        """
        Prompt user for text input with validation.

        Args:
            message: Prompt message to display
            default: Default value (shown in brackets)
            required: Whether input is required (cannot be empty)
            validator: Custom validator instance
            multiline: Allow multiline input

        Returns:
            User input string

        Example:
            name = input_mgr.prompt_user("Enter your name", required=True)
            path = input_mgr.prompt_user("File path", default="./data")
        """
        # Build prompt text
        prompt_text = f"{message}"
        if default:
            prompt_text += f" [{default}]"
        prompt_text += ": "

        # Set up validation
        if required and not validator:
            validator = RequiredValidator()

        try:
            result = prompt(
                prompt_text,
                default=default or '',
                validator=validator,
                validate_while_typing=False,
                multiline=multiline,
                style=self.style
            )

            # Return default if empty and default provided
            if not result.strip() and default:
                return default

            return result.strip()

        except (KeyboardInterrupt, EOFError):
            # User cancelled - return default or empty
            return default or ''

    def prompt_choice(self,
                     message: str,
                     choices: List[str],
                     default: Optional[str] = None,
                     allow_custom: bool = False) -> str:
        """
        Prompt user to select from a list of choices with autocomplete.
        Now uses unified selector (v1.1.0) for enhanced cross-platform UX.

        Args:
            message: Prompt message
            choices: List of valid choices
            default: Default choice
            allow_custom: Allow user to enter custom value not in choices

        Returns:
            Selected choice

        Example:
            theme = input_mgr.prompt_choice(
                "Select theme",
                choices=["dungeon", "hacker", "galaxy"],
                default="dungeon"
            )
        """
        # Try unified selector first (v1.1.0)
        try:
            from core.ui.unified_selector import select_single

            # Find default index
            default_index = 0
            if default and default in choices:
                default_index = choices.index(default)

            result = select_single(
                title=message,
                items=choices,
                default_index=default_index
            )

            if result:
                return result

            # If cancelled and allow_custom, fall through to text input
            if not allow_custom:
                return default or choices[0]

        except (ImportError, Exception) as e:
            # Fallback to legacy mode if unified selector unavailable
            print(f"⚠️  Using legacy input mode")

        # Legacy text-based mode (fallback)
        # Display choices
        print(f"\n{message}")
        for i, choice in enumerate(choices, 1):
            marker = "→" if choice == default else " "
            print(f"  {marker} {i}. {choice}")

        if allow_custom:
            print(f"  Or enter custom value")

        # Create completer for choices
        completer = WordCompleter(
            choices,
            ignore_case=True,
            sentence=True
        )

        # Build prompt
        prompt_text = "\nYour choice"
        if default:
            prompt_text += f" [{default}]"
        prompt_text += ": "

        while True:
            try:
                result = prompt(
                    prompt_text,
                    completer=completer,
                    complete_while_typing=True,
                    style=self.style
                )

                result = result.strip()

                # Handle empty input - use default
                if not result and default:
                    return default

                # Handle numeric selection
                if result.isdigit():
                    idx = int(result) - 1
                    if 0 <= idx < len(choices):
                        return choices[idx]
                    else:
                        print(f"❌ Invalid selection: {result}")
                        continue

                # Handle text selection
                if result.lower() in [c.lower() for c in choices]:
                    # Find exact match (case-insensitive)
                    for choice in choices:
                        if choice.lower() == result.lower():
                            return choice

                # Custom value allowed?
                if allow_custom and result:
                    return result

                # Invalid choice
                if result:
                    print(f"❌ Invalid choice: {result}")
                    print(f"   Please select from: {', '.join(choices)}")

            except (KeyboardInterrupt, EOFError):
                return default or ''

    def prompt_confirm(self,
                      message: str,
                      default: bool = True) -> bool:
        """
        Prompt user for yes/no confirmation.

        Args:
            message: Confirmation message
            default: Default value (True = yes, False = no)

        Returns:
            True for yes, False for no

        Example:
            if input_mgr.prompt_confirm("Continue?", default=True):
                # User said yes
        """
        default_text = "Y/n" if default else "y/N"
        prompt_text = f"{message} [{default_text}]: "

        try:
            result = prompt(prompt_text, style=self.style)
            result = result.strip().lower()

            if not result:
                return default

            return result in ['y', 'yes', 'true', '1']

        except (KeyboardInterrupt, EOFError):
            return default

    def prompt_file(self,
                   message: str = "Select a file",
                   starting_path: str = ".",
                   must_exist: bool = True,
                   file_type: Optional[str] = None) -> str:
        """
        Prompt user for file path with validation.

        Args:
            message: Prompt message (default: "Select a file")
            starting_path: Initial directory to search
            must_exist: Whether file must exist
            file_type: Filter by file extension (e.g., ".md", ".py")

        Returns:
            Selected file path

        Example:
            file = input_mgr.prompt_file(
                "Select file to edit",
                starting_path="knowledge",
                file_type=".md"
            )
        """
        # Get list of matching files
        path = Path(starting_path)
        if path.is_file():
            files = [str(path)]
        else:
            # Handle multiple file types for content files
            if file_type == "all" or file_type is None:
                # Search for common content file types
                patterns = ["**/*.md", "**/*.uscript", "**/*.txt", "**/*.json"]
            elif isinstance(file_type, list):
                patterns = [f"**/*{ext}" for ext in file_type]
            else:
                patterns = [f"**/*{file_type}"]

            files = []
            for pattern in patterns:
                for f in path.glob(pattern):
                    if f.is_file() and not any(part.startswith('.') for part in f.parts):
                        # Create relative path for display
                        try:
                            rel_path = f.relative_to(path)
                            files.append((str(f), str(rel_path)))
                        except ValueError:
                            files.append((str(f), f.name))

            # Sort by relative path and limit
            files = sorted(files, key=lambda x: x[1])[:100]  # Increased limit to 100

        if not files and must_exist:
            print(f"⚠️  No files found in {starting_path}")

            # Offer to browse other folders
            from core.ui.knowledge_file_picker import KnowledgeFilePicker
            picker = KnowledgeFilePicker()

            # Check if folder shortcuts are available
            if hasattr(picker, 'folder_shortcuts') and picker.folder_shortcuts:
                browse = self.prompt_confirm(
                    "Would you like to browse other folders?",
                    default=True
                )

                if browse:
                    folder = picker.pick_folder("Select folder to browse")
                    if folder and folder.exists():
                        # Recursively call with new folder
                        return self.prompt_file(
                            message=message,
                            starting_path=str(folder),
                            must_exist=must_exist,
                            file_type=file_type
                        )

            return ""

        # If files is a list of tuples, extract for display
        if files and isinstance(files[0], tuple):
            file_display_map = {rel: abs_path for abs_path, rel in files}
            file_choices = [rel for _, rel in files]
        else:
            # Legacy format - single strings
            file_display_map = {f: f for f in files}
            file_choices = files

        # For many files, use prompt_choice which handles large lists better
        if len(file_choices) > 10:
            print(f"\n📁 Found {len(file_choices)} file(s) in {starting_path}")

            # Use prompt_choice with autocomplete for large file lists
            selected = self.prompt_choice(
                message=message,
                choices=file_choices,
                default=file_choices[0] if file_choices else None,
                allow_custom=False
            )

            if not selected:
                return ""

            # Map back to absolute path
            if selected in file_display_map:
                return file_display_map[selected]
            return selected

        # For fewer files, show numbered list with prompt
        if file_choices:
            print(f"\n📁 Found {len(file_choices)} file(s) in {starting_path}")
            for i, file_choice in enumerate(file_choices, 1):
                print(f"  {i}. {file_choice}")
            print(f"\n💡 Type a number (1-{len(file_choices)}) or filename")
            print()

        # Create file completer with relative paths for display
        completer = WordCompleter(
            file_choices,
            ignore_case=True,
            sentence=True
        )

        prompt_text = f"{message}: "

        result = prompt(
            prompt_text,
            completer=completer,
            validate_while_typing=False
        ).strip()

        # Handle numeric selection
        if result.isdigit():
            idx = int(result) - 1
            if 0 <= idx < len(file_choices):
                selected_file = file_choices[idx]
                if selected_file in file_display_map:
                    return file_display_map[selected_file]
                return selected_file
            else:
                print(f"❌ Invalid number. Please choose 1-{len(file_choices)}")
                return ""

        # Handle filename selection
        if result in file_display_map:
            return file_display_map[result]

        return result

    def prompt_text(self,
                   message: str,
                   multiline: bool = False,
                   default: str = "") -> str:
        """
        Prompt user for text input (single or multi-line).

        Args:
            message: Prompt message
            multiline: Allow multiline input (Ctrl+D or Esc+Enter to finish)
            default: Default text

        Returns:
            User input text

        Example:
            notes = input_mgr.prompt_text(
                "Enter notes",
                multiline=True
            )
        """
        if multiline:
            print(f"{message} (Ctrl+D or Meta+Enter when done):")

        return self.prompt_user(
            message if not multiline else "",
            default=default,
            multiline=multiline
        )

    def get_field(self,
                 data: Dict[str, Any],
                 field_path: str,
                 default: Any = None) -> Any:
        """
        Get nested field from dictionary using dot notation.

        Args:
            data: Dictionary to search
            field_path: Dot-separated field path (e.g., "STORY.USER_NAME")
            default: Default value if field not found

        Returns:
            Field value or default

        Example:
            name = input_mgr.get_field(story_data, "STORY.USER_NAME", "adventurer")
            theme = input_mgr.get_field(story_data, "STORY.THEME", "dungeon")
        """
        try:
            parts = field_path.split('.')
            current = data

            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return default

            return current if current is not None else default

        except (KeyError, TypeError, AttributeError):
            return default

    def set_field(self,
                 data: Dict[str, Any],
                 field_path: str,
                 value: Any) -> Dict[str, Any]:
        """
        Set nested field in dictionary using dot notation.
        Creates intermediate dictionaries as needed.

        Args:
            data: Dictionary to modify
            field_path: Dot-separated field path
            value: Value to set

        Returns:
            Modified dictionary

        Example:
            story = input_mgr.set_field(story, "STORY.USER_NAME", "Fred")
            story = input_mgr.set_field(story, "OPTIONS.THEME", "hacker")
        """
        parts = field_path.split('.')
        current = data

        # Navigate to parent, creating dicts as needed
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]

        # Set final value
        current[parts[-1]] = value

        return data


def create_input_manager(theme: str = 'dungeon') -> InputManager:
    """
    Factory function to create InputManager instance.

    Args:
        theme: Theme name for styling

    Returns:
        InputManager instance

    Example:
        input_mgr = create_input_manager('dungeon')
    """
    return InputManager(theme=theme)
