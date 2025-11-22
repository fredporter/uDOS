"""
uDOS Core Modules

This package contains all the core Python modules that power uDOS.
"""

# Core components
from .uDOS_main import main
from .uDOS_commands import CommandHandler
from .uDOS_parser import Parser
from .uDOS_grid import Grid
from .uDOS_logger import Logger
from .config import get_config, Config

# Theme system
from .theme import load_theme, ThemeManager

# Knowledge system
from .knowledge import get_knowledge_manager, MemoryManager

# Input/Output
from .output import print_splash_screen
from .interpreters import UCodeInterpreter, OfflineEngine

# Services
from .services.history_manager import ActionHistory
from .services.history import CommandHistory
from .services.connection_manager import ConnectionMonitor
from .services.user_manager import UserManager
# Map engine moved to extensions - import only when needed

# Utils
from .utils.viewport import ViewportDetector
from .utils.viewport_viz import ViewportVisualizer
from .utils.completer import uDOSCompleter
from .utils.setup import SystemSetup

# Display (moved to input/prompts)
from .input.prompts.smart_prompt import SmartPrompt

__all__ = [
    'main',
    'CommandHandler',
    'Parser',
    'Grid',
    'Logger',
    'get_config',
    'Config',
    'load_theme',
    'ThemeManager',
    'get_knowledge_manager',
    'MemoryManager',
    'ActionHistory',
    'CommandHistory',
    'ConnectionMonitor',
    'ViewportDetector',
    'ViewportVisualizer',
    'UserManager',
    'SmartPrompt',
    'uDOSCompleter',
    'SystemSetup',
    'print_splash_screen',
    'UCodeInterpreter',
    'OfflineEngine',
    'MapEngine',
]
