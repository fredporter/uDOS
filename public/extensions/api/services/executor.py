"""
Command Executor Service
========================

Core command execution for uDOS API.
Provides init_udos_systems() and execute_command() used by all routes.
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

# Project root - server.py is at extensions/api/server.py
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# API logger
api_logger = logging.getLogger("uDOS.API")

# Try to import uDOS core modules
try:
    from core_beta.interpreters.uDOS_parser import Parser
    from core_beta.uDOS_commands import CommandHandler
    from core_beta.services.uDOS_grid import Grid
    from core_beta.services.logging_manager import get_logger, LogSource
    from core_beta.utils.files import WorkspaceManager
    from core_beta.services.history_manager import ActionHistory
    from core_beta.services.user_manager import UserManager
    from core_beta.ui.tui_controller import TUIController
    from core_beta.config import Config

    # Modular services
    from core_beta.services.streaming_service import (
        WebSocketStreamingService,
        StreamEvent,
        create_socketio_handlers,
        get_streaming_service,
    )
    from core_beta.services.predictor_service import PredictorService, get_predictor_service
    from core_beta.services.debug_panel_service import (
        DebugPanelService,
        LogLevel,
        get_debug_panel_service,
    )
    from core_beta.services.file_picker_service import (
        FilePickerService,
        get_file_picker_service,
    )
    from core_beta.services.menu_service import MenuService, get_menu_service
    from core_beta.services.settings_sync import SettingsSync, get_settings_sync
    from core_beta.services.map_data_bridge import MapDataBridge, get_map_data_bridge
    from core_beta.services.dashboard_service import (
        DashboardDataService,
        get_dashboard_service,
    )
    from core_beta.services.extension_registry import (
        ExtensionRegistry,
        get_extension_registry,
    )

    UDOS_AVAILABLE = True
    STREAMING_AVAILABLE = True
except ImportError as e:
    UDOS_AVAILABLE = False
    STREAMING_AVAILABLE = False
    print(f"⚠️  uDOS core modules not available - running in standalone mode")
    print(f"Import error: {e}")


# Global uDOS instances (initialized on first request)
_instances = {
    "parser": None,
    "command_handler": None,
    "grid": None,
    "logger": None,
    "workspace_manager": None,
    "command_history": None,
    "user_manager": None,
    "tui_controller": None,
}

# Modular services
_services = {
    "streaming": None,
    "predictor": None,
    "debug_panel": None,
    "file_picker": None,
    "menu": None,
    "settings_sync": None,
    "map_data_bridge": None,
    "dashboard": None,
    "extension_registry": None,
}


def get_project_root() -> Path:
    """Get the project root path."""
    return PROJECT_ROOT


def get_api_logger():
    """Get the API logger instance."""
    return api_logger


def get_services() -> Dict:
    """Get all modular services. Call init_udos_systems() first."""
    return _services.copy()


def get_instances() -> Dict:
    """Get all uDOS core instances. Call init_udos_systems() first."""
    return _instances.copy()


def init_udos_systems() -> bool:
    """
    Initialize uDOS systems on first API call.

    Returns:
        True if initialization successful, False otherwise.
    """
    global _instances, _services

    if not UDOS_AVAILABLE:
        api_logger.warning(
            "uDOS core modules not available - running in standalone mode"
        )
        return False

    if _instances["parser"] is None:
        try:
            api_logger.info("Initializing uDOS systems...")

            _instances["parser"] = Parser()
            _instances["grid"] = Grid()
            _instances["logger"] = get_logger("api-session", source=LogSource.API)
            _instances["workspace_manager"] = WorkspaceManager()
            _instances["command_history"] = ActionHistory()
            _instances["user_manager"] = UserManager()

            # CommandHandler parameters match uDOS_main.py
            _instances["command_handler"] = CommandHandler(
                history=_instances["command_history"],
                connection=None,  # API doesn't need connection monitoring
                viewport=None,  # API doesn't have viewport
                user_manager=_instances["user_manager"],
                command_history=_instances["command_history"],
                logger=_instances["logger"],
            )

            # Initialize TUI controller for API access
            config_dict = {
                "keypad_enabled": False,  # Controlled by API
                "preserve_scroll": True,
            }
            _instances["tui_controller"] = TUIController(
                config=config_dict, viewport=None
            )
            api_logger.info("TUI controller initialized")

            # Initialize modular services
            if STREAMING_AVAILABLE:
                _services["streaming"] = get_streaming_service()
                api_logger.info("WebSocket streaming service initialized")

                _services["predictor"] = get_predictor_service()
                api_logger.info("Predictor service initialized")

                _services["debug_panel"] = get_debug_panel_service()
                api_logger.info("Debug panel service initialized")

                _services["file_picker"] = get_file_picker_service()
                api_logger.info("File picker service initialized")

                _services["menu"] = get_menu_service()
                api_logger.info("Menu service initialized")

                _services["settings_sync"] = get_settings_sync()
                api_logger.info("Settings sync service initialized")

                _services["map_data_bridge"] = get_map_data_bridge()
                api_logger.info("Map data bridge initialized")

                _services["dashboard"] = get_dashboard_service()
                api_logger.info("Dashboard data service initialized")

                _services["extension_registry"] = get_extension_registry()
                api_logger.info("Extension registry initialized")

            api_logger.info("uDOS systems initialized successfully")
            return True
        except Exception as e:
            api_logger.error(f"Failed to initialize uDOS: {e}", exc_info=True)
            print(f"❌ Failed to initialize uDOS: {e}")
            return False

    return True


def execute_command(command_str: str, bypass_filter: bool = False) -> Dict:
    """
    Execute a uDOS command and return structured result.

    Args:
        command_str: Command string (e.g., "HELP", "FILE LIST")
        bypass_filter: If True, skip command filter check (internal use only)

    Returns:
        Dict with status, output, and metadata
    """
    api_logger.info(f"Executing command: {command_str}")

    # Check command filter (Dev Mode boundary)
    if not bypass_filter:
        try:
            from core_beta.security.command_filter import check_api_command

            allowed, error_msg = check_api_command(command_str)
            if not allowed:
                api_logger.warning(
                    f"Command blocked by filter: {command_str} - {error_msg}"
                )
                return {
                    "status": "blocked",
                    "command": command_str,
                    "message": error_msg,
                    "output": "",
                    "hint": "This command requires TUI access. Run uDOS in terminal mode.",
                }
        except ImportError:
            api_logger.warning("Command filter not available - allowing command")

    if not init_udos_systems():
        api_logger.warning(
            f"Command execution failed - uDOS systems not available: {command_str}"
        )
        return {
            "status": "error",
            "message": "uDOS systems not available",
            "output": "",
        }

    try:
        parser = _instances["parser"]
        command_handler = _instances["command_handler"]
        grid = _instances["grid"]
        logger = _instances["logger"]
        command_history = _instances["command_history"]

        # Parse and execute command
        ucode = parser.parse(command_str)
        result = command_handler.handle_command(ucode, grid, parser)

        # Log command
        logger.info(f"API_COMMAND: {command_str}")
        command_history.record_action("command", {"command": command_str})

        api_logger.info(f"Command executed successfully: {command_str}")
        api_logger.debug(f"Command result: {result}")

        return {
            "status": "success",
            "command": command_str,
            "output": result or "",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        if _instances["logger"]:
            _instances["logger"].error(f"API_ERROR: {command_str}: {e}")
        api_logger.error(f"Command execution error: {command_str} - {e}", exc_info=True)
        return {
            "status": "error",
            "command": command_str,
            "message": str(e),
            "output": "",
        }
