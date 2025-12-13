"""
uDOS v1.3 - Handler Utilities
Common utilities for all command handlers to reduce duplication.
"""

from typing import Optional, Any
from pathlib import Path


class HandlerUtils:
    """Shared utilities for command handlers."""
    
    _config_cache = None
    _logger_cache = None
    
    @classmethod
    def get_config(cls):
        """Get shared Config instance (cached)."""
        if cls._config_cache is None:
            from core.config import Config
            cls._config_cache = Config()
        return cls._config_cache
    
    @classmethod
    def get_logger(cls, name: str = 'uDOS'):
        """Get shared logger instance (cached)."""
        if cls._logger_cache is None:
            import logging
            cls._logger_cache = logging.getLogger(name)
        return cls._logger_cache
    
    @staticmethod
    def validate_file_exists(filepath: str) -> tuple[bool, Optional[str]]:
        """
        Validate file exists and is accessible.
        
        Returns:
            (success: bool, error_message: Optional[str])
        """
        try:
            path = Path(filepath)
            if not path.exists():
                return False, f"File not found: {filepath}"
            if not path.is_file():
                return False, f"Not a file: {filepath}"
            if not path.stat().st_size > 0:
                return False, f"File is empty: {filepath}"
            return True, None
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def validate_directory(dirpath: str, create: bool = False) -> tuple[bool, Optional[str]]:
        """
        Validate directory exists (optionally create).
        
        Args:
            dirpath: Directory path to validate
            create: If True, create directory if it doesn't exist
            
        Returns:
            (success: bool, error_message: Optional[str])
        """
        try:
            path = Path(dirpath)
            if not path.exists():
                if create:
                    path.mkdir(parents=True, exist_ok=True)
                    return True, None
                return False, f"Directory not found: {dirpath}"
            if not path.is_dir():
                return False, f"Not a directory: {dirpath}"
            return True, None
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def format_error(error: str, hint: Optional[str] = None) -> str:
        """
        Format error message consistently.
        
        Args:
            error: Error message
            hint: Optional hint for the user
            
        Returns:
            Formatted error string
        """
        msg = f"❌ {error}"
        if hint:
            msg += f"\n💡 {hint}"
        return msg
    
    @staticmethod
    def format_success(message: str, details: Optional[str] = None) -> str:
        """
        Format success message consistently.
        
        Args:
            message: Success message
            details: Optional details
            
        Returns:
            Formatted success string
        """
        msg = f"✅ {message}"
        if details:
            msg += f"\n   {details}"
        return msg
    
    @staticmethod
    def parse_flags(params: list[str]) -> tuple[list[str], dict[str, Any]]:
        """
        Parse command parameters into args and flags.
        
        Args:
            params: List of parameters like ['arg1', '--flag', 'value', '--bool-flag']
            
        Returns:
            (args: list, flags: dict)
            
        Example:
            ['file.txt', '--format', 'json', '--verbose']
            → (['file.txt'], {'format': 'json', 'verbose': True})
        """
        args = []
        flags = {}
        
        i = 0
        while i < len(params):
            param = params[i]
            
            if param.startswith('--'):
                # Flag found
                flag_name = param[2:].lower().replace('-', '_')
                
                # Check if next param is a value (doesn't start with --)
                if i + 1 < len(params) and not params[i + 1].startswith('--'):
                    flags[flag_name] = params[i + 1]
                    i += 2
                else:
                    # Boolean flag
                    flags[flag_name] = True
                    i += 1
            else:
                # Regular argument
                args.append(param)
                i += 1
        
        return args, flags
    
    @staticmethod
    def format_table(headers: list[str], rows: list[list[str]], 
                     align: Optional[list[str]] = None) -> str:
        """
        Format data as aligned table.
        
        Args:
            headers: Column headers
            rows: List of row data
            align: Optional alignment per column ('left'|'right'|'center')
            
        Returns:
            Formatted table string
        """
        if not rows:
            return ""
        
        # Calculate column widths
        widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                widths[i] = max(widths[i], len(str(cell)))
        
        # Default alignment
        if align is None:
            align = ['left'] * len(headers)
        
        # Format functions
        def format_cell(text, width, alignment):
            if alignment == 'right':
                return str(text).rjust(width)
            elif alignment == 'center':
                return str(text).center(width)
            else:
                return str(text).ljust(width)
        
        # Build table
        lines = []
        
        # Header
        header_line = "  ".join(
            format_cell(h, w, a) 
            for h, w, a in zip(headers, widths, align)
        )
        lines.append(header_line)
        lines.append("─" * len(header_line))
        
        # Rows
        for row in rows:
            row_line = "  ".join(
                format_cell(cell, w, a)
                for cell, w, a in zip(row, widths, align)
            )
            lines.append(row_line)
        
        return "\n".join(lines)
    
    @staticmethod
    def truncate_string(text: str, max_length: int, 
                       suffix: str = "...") -> str:
        """
        Truncate string to max length with suffix.
        
        Args:
            text: String to truncate
            max_length: Maximum length
            suffix: Suffix to add if truncated
            
        Returns:
            Truncated string
        """
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
