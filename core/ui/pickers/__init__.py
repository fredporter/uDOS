"""
UI Pickers Package - Interactive selection components

v1.1.0: Now includes UnifiedSelector for cross-platform compatibility.
Legacy OptionSelector and EnhancedFilePicker retained for backward compatibility.
"""

from .file_picker import FilePicker
from .knowledge_file_picker import KnowledgeFilePicker
from .option_selector import OptionSelector, EnhancedFilePicker

# v1.1.0: Import unified selector
try:
    from ..unified_selector import (
        UnifiedSelector,
        select_single,
        select_multiple,
        select_file,
        select_with_search
    )
    __all__ = [
        'FilePicker', 'KnowledgeFilePicker',
        'OptionSelector', 'EnhancedFilePicker',  # Legacy (deprecated)
        'UnifiedSelector', 'select_single', 'select_multiple',  # v1.1.0
        'select_file', 'select_with_search'
    ]
except ImportError:
    # Fallback if unified_selector not available
    __all__ = ['FilePicker', 'KnowledgeFilePicker', 'OptionSelector', 'EnhancedFilePicker']

