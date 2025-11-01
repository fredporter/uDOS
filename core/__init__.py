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

# Services
from .services.history_manager import ActionHistory
from .services.connection_manager import ConnectionMonitor
from .services.user_manager import UserManager
from .services.map_engine import MapEngine

# Utils
from .utils.viewport import ViewportDetector
from .utils.viewport_viz import ViewportVisualizer
from .utils.completer import uDOSCompleter
from .utils.setup import SystemSetup
from .utils.ucode import UCodeInterpreter

# Display
from .uDOS_splash import print_splash_screen
from .uDOS_prompt import SmartPrompt
from .uDOS_offline import OfflineEngine

__all__ = [
    'main',
    'CommandHandler',
    'Parser',
    'Grid',
    'Logger',
    'ActionHistory',
    'SystemHealth',
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
