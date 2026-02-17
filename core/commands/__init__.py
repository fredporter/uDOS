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
    elif name == "AnchorHandler":
        from .anchor_handler import AnchorHandler

        return AnchorHandler
    elif name == "GridHandler":
        from .grid_handler import GridHandler

        return GridHandler
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
    elif name == "HealthHandler":
        from .health_handler import HealthHandler

        return HealthHandler
    elif name == "VerifyHandler":
        from .verify_handler import VerifyHandler

        return VerifyHandler
    elif name == "RepairHandler":
        from .repair_handler import RepairHandler

        return RepairHandler
    elif name == "SonicHandler":
        from .sonic_handler import SonicHandler

        return SonicHandler
    elif name == "MusicHandler":
        from .music_handler import MusicHandler

        return MusicHandler
    elif name == "SchedulerHandler":
        from .scheduler_handler import SchedulerHandler

        return SchedulerHandler
    elif name == "ScriptHandler":
        from .script_handler import ScriptHandler

        return ScriptHandler
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
    elif name == "BinderHandler":
        from .binder_handler import BinderHandler

        return BinderHandler
    elif name == "RunHandler":
        from .run_handler import RunHandler

        return RunHandler
    elif name == "ReadHandler":
        from .read_handler import ReadHandler

        return ReadHandler
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
    elif name == "TokenHandler":
        from .token_handler import TokenHandler

        return TokenHandler
    elif name == "GhostHandler":
        from .ghost_handler import GhostHandler

        return GhostHandler
    elif name == "LogsHandler":
        from .logs_handler import LogsHandler

        return LogsHandler
    elif name == "RestartHandler":
        from .restart_handler import RestartHandler

        return RestartHandler
    elif name == "DestroyHandler":
        from .destroy_handler import DestroyHandler

        return DestroyHandler
    elif name == "UserHandler":
        from .user_handler import UserHandler

        return UserHandler
    elif name == "GameplayHandler":
        from .gameplay_handler import GameplayHandler

        return GameplayHandler
    elif name == "PlayHandler":
        from .play_handler import PlayHandler

        return PlayHandler
    elif name == "RuleHandler":
        from .rule_handler import RuleHandler

        return RuleHandler
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
    elif name == "ViewportHandler":
        from .viewport_handler import ViewportHandler

        return ViewportHandler
    elif name == "DrawHandler":
        from .draw_handler import DrawHandler

        return DrawHandler
    elif name == "WorkspaceHandler":
        from .workspace_handler import WorkspaceHandler

        return WorkspaceHandler
    elif name == "WizardHandler":
        from .wizard_handler import WizardHandler

        return WizardHandler
    elif name == "EmpireHandler":
        from .empire_handler import EmpireHandler

        return EmpireHandler
    elif name == "InteractiveMenuMixin":
        from .interactive_menu_mixin import InteractiveMenuMixin

        return InteractiveMenuMixin
    # Integration handlers (library-backed)
    elif name == "AIHandler":
        from .ai_handler import AIHandler

        return AIHandler
    elif name == "HomeHandler":
        from .home_handler import HomeHandler

        return HomeHandler
    elif name == "ExportHandler":
        from .export_handler import ExportHandler

        return ExportHandler
    elif name == "MeshHandler":
        from .mesh_handler import MeshHandler

        return MeshHandler
    elif name == "OkfixHandler":
        from .okfix_handler import OkfixHandler

        return OkfixHandler
    elif name == "WebHandler":
        from .web_handler import WebHandler

        return WebHandler
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "BaseCommandHandler",
    # Location commands
    "MapHandler",
    "AnchorHandler",
    "GridHandler",
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
    "SchedulerHandler",
    "ScriptHandler",
    "HealthHandler",
    "VerifyHandler",
    "RepairHandler",
    "SonicHandler",
    "MusicHandler",
    "DevModeHandler",
    "LogsHandler",
    "HotkeyHandler",
    "RestartHandler",
    "DestroyHandler",
    "UserHandler",
    "UndoHandler",
    "MigrateHandler",
    "SeedHandler",
    "GameplayHandler",
    "PlayHandler",
    "RuleHandler",
    # NPC & Dialogue commands
    "NPCHandler",
    "DialogueEngine",
    "DialogueTree",
    "DialogueNode",
    "TalkHandler",
    # Wizard commands
    "ConfigHandler",
    "WizardHandler",
    "EmpireHandler",
    "EmpireHandler",
    "BinderHandler",
    "RunHandler",
    "ReadHandler",
    "StoryHandler",
    "FileEditorHandler",
    "FileHandler",  # Phase 2: Workspace picker integration
    "MaintenanceHandler",
    "SetupHandler",
    "UIDHandler",
    "TokenHandler",
    "GhostHandler",
    "ViewportHandler",
    "DrawHandler",
    "WorkspaceHandler",
    # UI Mixins
    "InteractiveMenuMixin",
    # Integration handlers (library-backed)
    "AIHandler",
    "HomeHandler",
    "ExportHandler",
    "MeshHandler",
    "OkfixHandler",
    "WebHandler",
]
