"""
uCODE Package - Scripting Language for uDOS
"""

# Make validator optional (requires yaml dependency)
try:
    from .validator import UCodeValidator, UCodeParser, CommandRegistry, ValidationError
    __all__ = ['UCodeValidator', 'UCodeParser', 'CommandRegistry', 'ValidationError']
except ImportError:
    # yaml not installed - validator unavailable
    __all__ = []
