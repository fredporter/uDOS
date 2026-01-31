"""
Enhanced Prompt with 2-Line Context Display
============================================

Provides rich input prompts with:
- Line 1: Current value/predictive text
- Line 2: Help context/syntax/options
- Standardized [1|0|Yes|No|OK|Cancel] confirmations

Author: uDOS Engineering
Version: v1.0.0
Date: 2026-01-30
"""

from typing import Optional, List, Dict, Any, Tuple
from .smart_prompt import SmartPrompt


class EnhancedPrompt(SmartPrompt):
    """Enhanced prompt with 2-line context display."""

    def __init__(self, registry=None):
        """Initialize enhanced prompt."""
        super().__init__(registry=registry)
        self.show_context = True
        self.show_predictions = True

    def ask_with_context(
        self,
        prompt_text: str,
        current_value: Optional[str] = None,
        help_text: Optional[str] = None,
        predictions: Optional[List[str]] = None,
        default: str = "",
    ) -> str:
        """
        Ask for input with 2-line context display.

        Line 1: Shows current value or predictions
        Line 2: Shows help context/syntax/options

        Args:
            prompt_text: Main prompt question
            current_value: Current/previous value to display
            help_text: Help context or syntax hints
            predictions: List of prediction suggestions
            default: Default value if Enter is pressed

        Returns:
            User input string
        """
        # Display context lines if enabled
        if self.show_context:
            # Line 1: Current value or predictions
            if current_value:
                print(f"  ╭─ Current: {current_value}")
            elif predictions and self.show_predictions:
                pred_display = ", ".join(predictions[:3])
                if len(predictions) > 3:
                    pred_display += f" (+{len(predictions) - 3} more)"
                print(f"  ╭─ Suggestions: {pred_display}")
            else:
                print(f"  ╭─ ...")

            # Line 2: Help text
            if help_text:
                print(f"  ╰─ {help_text}")
            else:
                print(f"  ╰─ Enter your input")

        # Get input using standard method
        return self.ask(prompt_text, default=default)

    def ask_confirmation(
        self,
        question: str,
        default: bool = False,
        help_text: Optional[str] = None,
        context: Optional[str] = None,
    ) -> bool:
        """
        Ask a confirmation question with standardized format.

        Format: [1|0|Yes|No|OK|Cancel]
        Mappings:
          - 1, y, yes, ok, Enter (if default=True) → True
          - 0, n, no, x, Enter (if default=False) → False

        Args:
            question: Question to ask
            default: Default answer (True=Yes, False=No)
            help_text: Help text for line 2
            context: Context for line 1

        Returns:
            True for yes/ok, False for no/cancel
        """
        # Display context lines
        if self.show_context:
            # Line 1: Context or current state
            if context:
                print(f"  ╭─ {context}")
            else:
                print(f"  ╭─ Please confirm your choice")

            # Line 2: Help text with format
            if help_text:
                print(f"  ╰─ {help_text}")
            else:
                print(f"  ╰─ [1|0|Yes|No|OK|Cancel]")

        # Build prompt
        default_str = "Yes" if default else "No"
        prompt_text = f"{question}? [{default_str.upper()}] "

        # Get response
        response = self.ask(prompt_text, default="").strip().lower()

        # Empty = default
        if response == "":
            return default

        # Map inputs to boolean
        if response in ["1", "y", "yes", "ok"]:
            return True
        elif response in ["0", "n", "no", "x", "cancel"]:
            return False
        else:
            # Invalid - show error and retry
            print("  ❌ Please enter: 1 (Yes), 0 (No), Yes, No, OK, or Cancel")
            return self.ask_confirmation(question, default, help_text, context)

    def ask_menu(
        self,
        title: str,
        options: List[str],
        help_text: Optional[str] = None,
        allow_cancel: bool = True,
    ) -> Optional[int]:
        """
        Ask user to select from a numbered menu.

        Args:
            title: Menu title
            options: List of menu options
            help_text: Help text for line 2
            allow_cancel: Allow 0 for cancel/exit

        Returns:
            Selected index (1-based), or None if cancelled
        """
        # Display menu
        print(f"\n{title}")
        for idx, option in enumerate(options, 1):
            print(f"  {idx}. {option}")

        # Display context lines
        if self.show_context:
            # Line 1: Show valid range
            range_display = f"1-{len(options)}" + (" or 0 to cancel" if allow_cancel else "")
            print(f"\n  ╭─ Valid choices: {range_display}")

            # Line 2: Help text
            if help_text:
                print(f"  ╰─ {help_text}")
            else:
                print(f"  ╰─ Enter number and press Enter")

        # Get choice
        choice = self.ask_menu_choice(
            "Choose an option",
            num_options=len(options),
            allow_zero=allow_cancel,
        )

        return choice

    def ask_variable(
        self,
        var_name: str,
        current_value: Optional[str] = None,
        var_type: str = "text",
        help_text: Optional[str] = None,
        required: bool = False,
    ) -> Optional[str]:
        """
        Ask for a variable value with context display.

        Args:
            var_name: Variable name
            current_value: Current value if any
            var_type: Variable type (text, number, path, url, etc.)
            help_text: Help text
            required: Is this variable required?

        Returns:
            User input or None if cancelled (when not required)
        """
        # Display context lines
        if self.show_context:
            # Line 1: Current value
            if current_value:
                print(f"  ╭─ Current: {current_value}")
            else:
                print(f"  ╭─ Not set")

            # Line 2: Help text with type and requirement
            help_display = help_text or f"Enter {var_type} value"
            if required:
                help_display += " (required)"
            else:
                help_display += " (optional, Enter to skip)"
            print(f"  ╰─ {help_display}")

        # Build prompt
        prompt_text = f"{var_name} > "

        # Get input
        response = self.ask(prompt_text, default=current_value or "").strip()

        # Validate if required
        if required and not response:
            print("  ❌ This field is required")
            return self.ask_variable(
                var_name, current_value, var_type, help_text, required
            )

        return response if response else None

    def ask_story_field(
        self,
        field: Dict[str, Any],
        previous_value: Optional[str] = None,
    ) -> Optional[str]:
        """
        Ask for a story form field with full context display.

        Args:
            field: Field definition dict with name, label, type, etc.
            previous_value: Previous value if editing

        Returns:
            User response or None
        """
        name = field.get("name", "")
        label = field.get("label", name)
        field_type = field.get("type", "text")
        required = field.get("required", False)
        placeholder = field.get("placeholder", "")
        options = field.get("options", [])
        validation = field.get("validation", None)  # name, username, date, etc.

        # Handle select/menu type
        if field_type == "select" and options:
            help_text = "Choose from the options above"
            if previous_value:
                help_text += f" (current: {previous_value})"

            choice = self.ask_menu(
                title=f"\n{label}:",
                options=options,
                help_text=help_text,
                allow_cancel=not required,
            )

            if choice and 1 <= choice <= len(options):
                return options[choice - 1]
            elif not required:
                return None
            else:
                return self.ask_story_field(field, previous_value)

        # Handle checkbox (yes/no) type
        elif field_type == "checkbox":
            context = f"Current: {previous_value}" if previous_value else "Not set"
            help_text = "Answer with 1 (Yes), 0 (No), or Yes/No/OK"

            result = self.ask_confirmation(
                question=label,
                default=previous_value == "yes" if previous_value else False,
                help_text=help_text,
                context=context,
            )

            return "yes" if result else "no"

        # Handle text/textarea type
        else:
            help_text = placeholder or f"Enter {field_type} value"
            
            # Get input with validation loop
            while True:
                value = self.ask_variable(
                    var_name=label,
                    current_value=previous_value,
                    var_type=field_type,
                    help_text=help_text,
                    required=required,
                )
                
                # Validate based on field validation type
                if value and validation:
                    is_valid, error = self._validate_field_value(value, validation)
                    if not is_valid:
                        print(f"  ❌ {error}")
                        continue
                
                return value

    def _validate_field_value(self, value: str, validation_type: str) -> Tuple[bool, str]:
        """
        Validate a field value based on validation type.

        Args:
            value: Value to validate
            validation_type: Type of validation (name, username, date, etc.)

        Returns:
            Tuple of (is_valid, error_message)
        """
        if validation_type == "name":
            from core.services.name_validator import validate_name
            return validate_name(value)
        
        elif validation_type == "username":
            from core.services.name_validator import validate_username
            return validate_username(value)
        
        elif validation_type == "date":
            from datetime import datetime
            try:
                datetime.strptime(value, "%Y-%m-%d")
                return True, ""
            except ValueError:
                return False, "Date must be in YYYY-MM-DD format"
        
        elif validation_type == "text":
            if not value.strip():
                return False, "Cannot be blank"
            return True, ""
        
        else:
            # Unknown validation type, pass through
            return True, ""

    def toggle_context_display(self, enabled: bool = None) -> bool:
        """
        Toggle context display on/off.

        Args:
            enabled: Enable (True) or disable (False), or toggle if None

        Returns:
            New state
        """
        if enabled is None:
            self.show_context = not self.show_context
        else:
            self.show_context = enabled
        return self.show_context

    def toggle_predictions(self, enabled: bool = None) -> bool:
        """
        Toggle prediction display on/off.

        Args:
            enabled: Enable (True) or disable (False), or toggle if None

        Returns:
            New state
        """
        if enabled is None:
            self.show_predictions = not self.show_predictions
        else:
            self.show_predictions = enabled
        return self.show_predictions
