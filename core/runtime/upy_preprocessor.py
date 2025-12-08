"""
.upy Preprocessor for uDOS

Processes .upy files as valid Python 3 scripts with uDOS extensions.
Handles variable expansion, command translation, and runtime integration.
"""

import ast
import re
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path


class UPYSyntaxError(Exception):
    """Raised when .upy file has syntax errors"""
    def __init__(self, message: str, line: int = 0, column: int = 0):
        self.line = line
        self.column = column
        super().__init__(f"{message} (line {line}, column {column})")


class UPYPreprocessor:
    """
    Preprocessor for .upy (uDOS Python) files.

    .upy files are valid Python 3 scripts that use uDOS conventions:
    - UPPERCASE-HYPHEN command names
    - $UPPERCASE-HYPHEN variable syntax
    - Special comment directives for uDOS runtime

    The preprocessor validates syntax and prepares files for execution.
    """

    def __init__(self, variable_manager=None):
        """
        Initialize preprocessor.

        Args:
            variable_manager: Variable manager for runtime value lookups
        """
        self.variable_manager = variable_manager
        self.variables: Dict[str, Any] = {}

    def validate_python(self, content: str) -> bool:
        """
        Validate that content is valid Python 3.

        Args:
            content: File content

        Returns:
            True if valid Python

        Raises:
            UPYSyntaxError: If syntax is invalid
        """
        try:
            ast.parse(content)
            return True
        except SyntaxError as e:
            raise UPYSyntaxError(
                f"Invalid Python syntax: {e.msg}",
                line=e.lineno or 0,
                column=e.offset or 0
            )

    def extract_variables(self, content: str) -> List[str]:
        """
        Extract all $VARIABLE references from content.

        Args:
            content: File content

        Returns:
            List of variable names (without $)
        """
        # Pattern: $UPPERCASE-HYPHEN (letters, hyphens, must have hyphen)
        pattern = r'\$([A-Z]+(?:-[A-Z]+)+)'
        matches = re.findall(pattern, content)
        return list(set(matches))  # Unique variables

    def validate_variable_names(self, variables: List[str]) -> List[str]:
        """
        Validate variable names follow UPPERCASE-HYPHEN convention.

        Args:
            variables: List of variable names (without $)

        Returns:
            List of invalid variable names
        """
        invalid = []
        pattern = r'^[A-Z]+(-[A-Z]+)+$'

        for var in variables:
            if not re.match(pattern, var):
                invalid.append(var)

        return invalid

    def expand_variables(self, content: str, context: Dict[str, Any] = None) -> str:
        """
        Expand $VARIABLE references to runtime values.

        Args:
            content: File content with $VARIABLE syntax
            context: Variable context (overrides variable_manager)

        Returns:
            Content with variables expanded
        """
        # Use provided context or variable manager
        values = context or {}

        if not context and self.variable_manager:
            # Get all variables from manager
            variables = self.extract_variables(content)
            for var in variables:
                value = self.variable_manager.get_variable(var)
                if value is not None:
                    values[var] = value

        # Replace $VARIABLE with value
        def replace_var(match):
            var_name = match.group(1)
            value = values.get(var_name, f"${var_name}")  # Keep $ if not found

            # Convert value to string representation
            if isinstance(value, str):
                return f'"{value}"'
            else:
                return str(value)

        pattern = r'\$([A-Z]+(?:-[A-Z]+)+)'
        return re.sub(pattern, replace_var, content)

    def preprocess(self, filepath: Path, context: Dict[str, Any] = None) -> str:
        """
        Preprocess a .upy file.

        Args:
            filepath: Path to .upy file
            context: Variable context

        Returns:
            Preprocessed content ready for execution

        Raises:
            UPYSyntaxError: If file has syntax errors
            FileNotFoundError: If file doesn't exist
        """
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        # Read file
        content = filepath.read_text(encoding='utf-8')

        # Extract and validate variables FIRST (before Python validation)
        variables = self.extract_variables(content)
        invalid_vars = self.validate_variable_names(variables)

        if invalid_vars:
            raise UPYSyntaxError(
                f"Invalid variable names (must be UPPERCASE-HYPHEN): {', '.join(invalid_vars)}",
                line=0
            )

        # Expand variables BEFORE validating Python
        processed = self.expand_variables(content, context)

        # Now validate Python syntax (after variable expansion)
        self.validate_python(processed)

        return processed

    def load_and_execute(
        self,
        filepath: Path,
        context: Dict[str, Any] = None,
        globals_dict: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Load and execute a .upy file.

        Args:
            filepath: Path to .upy file
            context: Variable context for expansion
            globals_dict: Global namespace for execution

        Returns:
            Execution namespace (locals)

        Raises:
            UPYSyntaxError: If file has syntax errors
            Exception: If execution fails
        """
        # Preprocess file
        processed = self.preprocess(filepath, context)

        # Prepare execution namespace
        exec_globals = globals_dict or {}
        exec_locals = {}

        # Execute
        try:
            exec(processed, exec_globals, exec_locals)
        except Exception as e:
            raise UPYSyntaxError(
                f"Execution error: {e}",
                line=0
            )

        return exec_locals

    @staticmethod
    def is_valid_upy_file(filepath: Path) -> bool:
        """
        Check if file is a valid .upy file.

        Args:
            filepath: Path to check

        Returns:
            True if file exists and has .upy extension
        """
        return filepath.exists() and filepath.suffix == '.upy'

    @staticmethod
    def validate_command_name(name: str) -> bool:
        """
        Validate command name follows UPPERCASE-HYPHEN convention.

        Args:
            name: Command name to validate

        Returns:
            True if valid
        """
        pattern = r'^[A-Z]+(-[A-Z]+)+$'
        return bool(re.match(pattern, name))

    def get_metadata(self, filepath: Path) -> Dict[str, Any]:
        """
        Extract metadata from .upy file header comments.

        Looks for special comment directives:
        # @NAME: Script Name
        # @DESCRIPTION: Script description
        # @AUTHOR: Author name
        # @VERSION: 1.0.0
        # @REQUIRES: variable1, variable2

        Args:
            filepath: Path to .upy file

        Returns:
            Metadata dictionary
        """
        if not filepath.exists():
            return {}

        content = filepath.read_text(encoding='utf-8')
        metadata = {}

        # Extract metadata directives
        pattern = r'#\s*@(\w+):\s*(.+)'
        for match in re.finditer(pattern, content):
            key = match.group(1).lower()
            value = match.group(2).strip()

            # Handle comma-separated values
            if key == 'requires':
                value = [v.strip() for v in value.split(',')]

            metadata[key] = value

        return metadata
