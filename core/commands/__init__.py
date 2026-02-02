"""
uDOS Command Handlers

Location-based and game state command handlers for TUI integration.
"""

# Delay imports to avoid circular dependencies during module initialization
# Handlers can be imported when actually needed (lazy loading)


def __getattr__(name):
    """Lazy load handlers to avoid circular imports."""
    if name == "BaseCommandHandler":
        from .base import BaseCommandHandler

        return BaseCommandHandler
    elif name == "MapHandler":
        from .map_handler import MapHandler

        return MapHandler
    elif name == "PanelHandler":
        from .panel_handler import PanelHandler

        return PanelHandler
    elif name == "GotoHandler":
        from .goto_handler import GotoHandler

        return GotoHandler
    elif name == "FindHandler":
        from .find_handler import FindHandler

        return FindHandler
    elif name == "TellHandler":
        from .tell_handler import TellHandler

        return TellHandler
    elif name == "BagHandler":
        from .bag_handler import BagHandler

        return BagHandler
    elif name == "GrabHandler":
        from .grab_handler import GrabHandler

        return GrabHandler
    elif name == "SpawnHandler":
        from .spawn_handler import SpawnHandler

        return SpawnHandler
    elif name == "SaveHandler":
        from .save_load_handlers import SaveHandler

        return SaveHandler
    elif name == "LoadHandler":
        from .save_load_handlers import LoadHandler

        return LoadHandler
    elif name == "HelpHandler":
        from .help_handler import HelpHandler

        return HelpHandler
    elif name == "ShakedownHandler":
        from .shakedown_handler import ShakedownHandler

        return ShakedownHandler
    elif name == "RepairHandler":
        from .repair_handler import RepairHandler

        return RepairHandler
    elif name == "PatternHandler":
        from .pattern_handler import PatternHandler

        return PatternHandler
    elif name == "IntegrationHandler":
        from .integration_handler import IntegrationHandler

        return IntegrationHandler
    elif name == "DevModeHandler":
        from .dev_mode_handler import DevModeHandler

        return DevModeHandler
    elif name == "NPCHandler":
        from .npc_handler import NPCHandler

        return NPCHandler
    elif name == "DialogueEngine":
        from .dialogue_engine import DialogueEngine

        return DialogueEngine
    elif name == "DialogueTree":
        from .dialogue_engine import DialogueTree

        return DialogueTree
    elif name == "DialogueNode":
        from .dialogue_engine import DialogueNode

        return DialogueNode
    elif name == "TalkHandler":
        from .talk_handler import TalkHandler

        return TalkHandler
    elif name == "ConfigHandler":
        from .config_handler import ConfigHandler

        return ConfigHandler
    elif name == "ProviderHandler":
        from .provider_handler import ProviderHandler

        return ProviderHandler
    elif name == "BinderHandler":
        from .binder_handler import BinderHandler

        return BinderHandler
    elif name == "RunHandler":
        from .run_handler import RunHandler

        return RunHandler
    elif name == "DatasetHandler":
        from .dataset_handler import DatasetHandler

        return DatasetHandler
    elif name == "FileEditorHandler":
        from .file_editor_handler import FileEditorHandler

        return FileEditorHandler
    elif name == "MaintenanceHandler":
        from .maintenance_handler import MaintenanceHandler

        return MaintenanceHandler
    elif name == "StoryHandler":
        from .story_handler import StoryHandler

        return StoryHandler
    elif name == "SetupHandler":
        from .setup_handler import SetupHandler

        return SetupHandler
    elif name == "UIDHandler":
        from .uid_handler import UIDHandler

        return UIDHandler
    elif name == "LogsHandler":
        from .logs_handler import LogsHandler

        return LogsHandler
    elif name == "ReloadHandler":
        from .reload_handler import ReloadHandler

        return ReloadHandler
    elif name == "RestartHandler":
        from .restart_handler import RestartHandler

        return RestartHandler
    elif name == "DestroyHandler":
        from .destroy_handler import DestroyHandler

        return DestroyHandler
    elif name == "UserHandler":
        from .user_handler import UserHandler

        return UserHandler
    elif name == "UndoHandler":
        from .undo_handler import UndoHandler

        return UndoHandler
    elif name == "MigrateHandler":
        from .migrate_handler import MigrateHandler

        return MigrateHandler
    elif name == "SeedHandler":
        from .seed_handler import SeedHandler

        return SeedHandler
    elif name == "HotkeyHandler":
        from .hotkey_handler import HotkeyHandler

        return HotkeyHandler
    elif name == "FileHandler":
        from .file_handler import FileHandler

        return FileHandler
    elif name == "WizardHandler":
        from .wizard_handler import WizardHandler

        return WizardHandler
    elif name == "InteractiveMenuMixin":
        from .interactive_menu_mixin import InteractiveMenuMixin

        return InteractiveMenuMixin
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


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
    "IntegrationHandler",
    "ShakedownHandler",
    "RepairHandler",
    "PatternHandler",
    "DevModeHandler",
    "LogsHandler",
    "HotkeyHandler",
    "ReloadHandler",
    "RestartHandler",
    "DestroyHandler",
    "UserHandler",
    "UndoHandler",
    "MigrateHandler",
    "SeedHandler",
    # NPC & Dialogue commands
    "NPCHandler",
    "DialogueEngine",
    "DialogueTree",
    "DialogueNode",
    "TalkHandler",
    # Wizard commands
    "ConfigHandler",
    "ProviderHandler",
    "WizardHandler",
    "BinderHandler",
    "RunHandler",
    "StoryHandler",
    "DatasetHandler",
    "FileEditorHandler",
    "FileHandler",  # Phase 2: Workspace picker integration
    "MaintenanceHandler",
    "SetupHandler",
    "UIDHandler",
    # UI Mixins
    "InteractiveMenuMixin",
]
