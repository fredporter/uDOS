"""
uDOS Command Handlers

Location-based and game state command handlers for TUI integration.
"""

from .base import BaseCommandHandler
from .map_handler import MapHandler
from .panel_handler import PanelHandler
from .goto_handler import GotoHandler
from .find_handler import FindHandler
from .tell_handler import TellHandler
from .bag_handler import BagHandler
from .grab_handler import GrabHandler
from .spawn_handler import SpawnHandler
from .save_load_handlers import SaveHandler, LoadHandler
from .help_handler import HelpHandler
from .shakedown_handler import ShakedownHandler
from .repair_handler import RepairHandler
from .dev_mode_handler import DevModeHandler
from .npc_handler import NPCHandler
from .dialogue_engine import DialogueEngine, DialogueTree, DialogueNode
from .talk_handler import TalkHandler
from .config_handler import ConfigHandler
from .provider_handler import ProviderHandler

__all__ = [
    "BaseCommandHandler",
    # Location commands
    "MapHandler",
    "PanelHandler",
    "GotoHandler",
    "FindHandler",
    "TellHandler",
    # Game state commands
    "BagHandler",
    "GrabHandler",
    "SpawnHandler",
    "SaveHandler",
    "LoadHandler",
    # System commands
    "HelpHandler",
    "ShakedownHandler",
    "RepairHandler",
    "DevModeHandler",
    # NPC & Dialogue commands
    "NPCHandler",
    "DialogueEngine",
    "DialogueTree",
    "DialogueNode",
    "TalkHandler",
    # Wizard commands
    "ConfigHandler",
    "ProviderHandler",
]
