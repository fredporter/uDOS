"""
Hot Reload Service - Auto-reload handlers on file changes

Monitors core/commands/ for changes and reloads handlers without restarting TUI.
Preserves REPL state and command history.

Usage:
    from core.services.hot_reload import HotReloadManager

    reload_mgr = HotReloadManager(dispatcher)
    reload_mgr.start()  # Start watching

    # Handlers auto-reload on save
    # REPL continues running

    reload_mgr.stop()   # Stop watching

Dependencies:
    pip install watchdog

Author: uDOS Engineering
Version: v1.0.0
Date: 2026-01-28
"""

import sys
import importlib
import threading
import os
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from datetime import datetime

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    FileSystemEventHandler = object  # Dummy base class

from core.services.unified_logging import get_unified_logger, LogLevel

try:
    from core.services.logging_service import get_logger, DevTrace
    logger = get_logger("hot-reload")
except ImportError:
    import logging
    logger = logging.getLogger("hot-reload")


def _guess_handler_class(module_name: str) -> str:
    """Convert a module name (snake_case) into a handler class name (PascalCase)."""
    parts = module_name.split('_')
    return ''.join(word.capitalize() for word in parts)


def _command_name_from_class(class_name: str) -> str:
    """Derive the canonical command name from a handler class."""
    return class_name.replace('Handler', '').upper()


COMMANDS_DIR = Path(__file__).resolve().parent.parent / "commands"


def _should_reload_file(
    filepath: str,
    reload_state: Dict[str, Dict[str, float]],
    cooldown: float = 0.5,
    stability_delay: float = 0.3,
) -> bool:
    """Debounce file reload requests using cooldown + stability checks."""
    if not os.path.exists(filepath):
        return False

    try:
        stat = os.stat(filepath)
    except OSError:
        return False

    if stat.st_size == 0:
        logger.debug("[LOCAL] Skipping reload for %s: file empty", Path(filepath).name)
        return False

    now = datetime.now().timestamp()
    entry = reload_state.get(filepath, {})
    last_mtime = entry.get("mtime")
    last_size = entry.get("size")

    if last_mtime != stat.st_mtime or last_size != stat.st_size:
        entry.update(
            {
                "mtime": stat.st_mtime,
                "size": stat.st_size,
                "updated_at": now,
            }
        )
        reload_state[filepath] = entry
        logger.debug("[LOCAL] Hot reload awaiting stable write for %s", Path(filepath).name)
        return False

    stable_since = now - entry.get("updated_at", now)
    if stable_since < stability_delay:
        logger.debug(
            "[LOCAL] Hot reload waiting %.2fs stability for %s",
            stability_delay - stable_since,
            Path(filepath).name,
        )
        return False

    last_reload = entry.get("last_reload", 0.0)
    if now - last_reload < cooldown:
        logger.debug(
            "[LOCAL] Hot reload cooldown %.2fs remaining for %s",
            cooldown - (now - last_reload),
            Path(filepath).name,
        )
        return False

    entry["last_reload"] = now
    entry["updated_at"] = now
    reload_state[filepath] = entry
    return True


def reload_all_handlers(
    logger: Optional[Any] = None,
    dispatcher: Optional[Any] = None,
) -> Dict[str, int]:
    """Reload every command handler module; returns reload/fail counts."""
    log = logger or globals().get("logger")
    reloaded = 0
    failed = 0

    for handler_file in sorted(COMMANDS_DIR.glob("*_handler.py")):
        if handler_file.name == "__init__.py":
            continue
        module_name = f"core.commands.{handler_file.stem}"
        try:
            if module_name in sys.modules:
                module = importlib.reload(sys.modules[module_name])
            else:
                module = importlib.import_module(module_name)

            success = True
            if dispatcher is not None:
                class_name = _guess_handler_class(handler_file.stem)
                if not hasattr(module, class_name):
                    success = False
                    if log:
                        log.warning(f"Handler class not found: {class_name}")
                else:
                    handler_class = getattr(module, class_name)
                    try:
                        new_handler = handler_class()
                    except Exception as exc:
                        success = False
                        if log:
                            log.warning(f"Failed to init {class_name}: {exc}")
                    else:
                        command_name = _command_name_from_class(class_name)
                        updated = False
                        for cmd in list(dispatcher.handlers.keys()):
                            if cmd == command_name or cmd.startswith(command_name):
                                dispatcher.handlers[cmd] = new_handler
                                updated = True
                        if not updated:
                            success = False
                            if log:
                                log.warning(f"Dispatcher did not contain {command_name} to update")

            if success:
                reloaded += 1
                if log:
                    log.debug(f"Reloaded handler module: {module_name}")
            else:
                failed += 1
        except Exception as exc:
            failed += 1
            if log:
                log.warning(f"Failed to reload {module_name}: {exc}")

    return {"reloaded": reloaded, "failed": failed}



class HandlerReloadEvent(FileSystemEventHandler):
    """File system event handler for Python files."""

    def __init__(self, reload_callback: Callable[[str], None], delete_callback: Optional[Callable[[str], None]] = None):
        """Initialize event handler.

        Args:
            reload_callback: Function to call with filepath on change
            delete_callback: Optional function to call on delete
        """
        self.reload_callback = reload_callback
        self.delete_callback = delete_callback
        self.reload_state: Dict[str, Dict[str, float]] = {}

    def on_modified(self, event):
        """Handle file modification event."""
        if event.is_directory:
            return

        filepath = event.src_path
        if not filepath.endswith('.py'):
            return

        if not _should_reload_file(filepath, self.reload_state):
            return
        try:
            self.reload_callback(filepath)
        except Exception as exc:
            logger.error("[LOCAL] Hot reload callback error for %s: %s", Path(filepath).name, exc)

    def on_created(self, event):
        """Handle new file creation event."""
        if event.is_directory:
            return

        filepath = event.src_path
        if not filepath.endswith('.py'):
            return

        if not _should_reload_file(filepath, self.reload_state):
            return
        try:
            self.reload_callback(filepath)
        except Exception as exc:
            logger.error("[LOCAL] Hot reload callback error for %s: %s", Path(filepath).name, exc)

    def on_moved(self, event):
        """Handle file move/rename event."""
        if event.is_directory:
            return

        filepath = getattr(event, 'dest_path', None) or event.src_path
        if not filepath.endswith('.py'):
            return

        if not _should_reload_file(filepath, self.reload_state):
            return
        try:
            self.reload_callback(filepath)
        except Exception as exc:
            logger.error("[LOCAL] Hot reload callback error for %s: %s", Path(filepath).name, exc)

    def on_deleted(self, event):
        """Handle file deletion event."""
        if event.is_directory:
            return

        filepath = event.src_path
        if not filepath.endswith('.py'):
            return

        self.reload_state.pop(filepath, None)
        if self.delete_callback:
            self.delete_callback(filepath)


class HotReloadManager:
    """Manages hot reload of command handlers."""

    def __init__(self, dispatcher: Any, enabled: bool = True):
        """Initialize hot reload manager.

        Args:
            dispatcher: CommandDispatcher instance
            enabled: Enable hot reload (default: True)
        """
        self.dispatcher = dispatcher
        self.enabled = enabled and WATCHDOG_AVAILABLE
        self.observer: Optional[Observer] = None
        self.watch_dir = Path(__file__).parent.parent / "commands"
        self.reload_count = 0
        self.failed_reloads = 0

        self.unified = get_unified_logger()

        if not WATCHDOG_AVAILABLE:
            logger.warning("[LOCAL] Hot reload disabled: watchdog not installed")
            logger.warning("[LOCAL] Install with: pip install watchdog")

    def start(self) -> bool:
        """Start watching for file changes.

        Returns:
            True if started successfully, False otherwise
        """
        if not self.enabled:
            logger.info("[LOCAL] Hot reload not enabled")
            return False

        if self.observer is not None:
            logger.warning("[LOCAL] Hot reload already running")
            return False

        try:
            event_handler = HandlerReloadEvent(self._on_file_changed, self._on_file_deleted)
            self.observer = Observer()
            self.observer.schedule(event_handler, str(self.watch_dir), recursive=False)
            self.observer.start()

            logger.info(f"[LOCAL] Hot reload started: watching {self.watch_dir}")
            self.unified.log_core(
                'hot-reload',
                f'Started watching {self.watch_dir}',
                level=LogLevel.INFO,
                watch_dir=str(self.watch_dir)
            )
            return True

        except Exception as e:
            logger.error(f"[LOCAL] Failed to start hot reload: {e}")
            self.unified.log_core(
                'hot-reload',
                f'Failed to start: {e}',
                level=LogLevel.ERROR
            )
            return False

    def stop(self) -> None:
        """Stop watching for file changes."""
        if self.observer is None:
            return

        self.observer.stop()
        self.observer.join()
        self.observer = None

        logger.info("[LOCAL] Hot reload stopped")
        self.unified.log_core(
            'hot-reload',
            f'Stopped. Reloaded {self.reload_count} times, {self.failed_reloads} failures',
            level=LogLevel.INFO,
            reload_count=self.reload_count,
            failed_count=self.failed_reloads
        )

    def _on_file_changed(self, filepath: str) -> None:
        """Handle file change event.

        Args:
            filepath: Path to changed file
        """
        path = Path(filepath)
        handler_name = path.stem  # e.g., 'map_handler' from 'map_handler.py'

        logger.info(f"[LOCAL] File changed: {path.name}")

        # Start dev trace for reload operation
        trace = DevTrace('hot-reload', enabled=True)

        with trace.span('reload_handler', {'file': path.name, 'handler': handler_name}):
            success = self._reload_handler(path, handler_name)

        trace.log(
            f"Reload {'SUCCESS' if success else 'FAILED'}: {path.name}",
            level="INFO" if success else "ERROR",
            metadata={'handler': handler_name}
        )
        trace.save()

        if success:
            self.reload_count += 1
            self.unified.log_core(
                'hot-reload',
                f'Reloaded {path.name}',
                level=LogLevel.INFO,
                handler=handler_name,
                reload_count=self.reload_count
            )
        else:
            self.failed_reloads += 1

    def _reload_handler(self, filepath: Path, handler_name: str) -> bool:
        """Reload a specific handler.

        Args:
            filepath: Path to handler file
            handler_name: Handler module name

        Returns:
            True if reload successful, False otherwise
        """
        try:
            # Construct module path
            module_name = f"core.commands.{handler_name}"
            if module_name not in sys.modules:
                try:
                    module = importlib.import_module(module_name)
                    logger.info(f"[LOCAL] Imported new handler module: {module_name}")
                except Exception as exc:
                    logger.warning(f"[LOCAL] Module not loaded: {module_name} ({exc})")
                    return False
            else:
                module = sys.modules[module_name]

            importlib.reload(module)

            if not hasattr(module, _guess_handler_class(handler_name)):
                logger.warning(f"[LOCAL] Handler class not found: {_guess_handler_class(handler_name)}")
                return False

            class_name = _guess_handler_class(handler_name)
            handler_class = getattr(module, class_name)
            new_handler = handler_class()
            self._update_dispatcher(class_name, new_handler)
            logger.info(f"[LOCAL] ✓ Reloaded {class_name}")
            return True

        except Exception as e:
            logger.error(f"[LOCAL] Failed to reload {handler_name}: {e}")
            return False

    def _on_file_deleted(self, filepath: str) -> None:
        """Handle handler deletion by removing from dispatcher."""
        path = Path(filepath)
        handler_name = path.stem
        class_name = _guess_handler_class(handler_name)
        command_name = _command_name_from_class(class_name)

        removed = False
        for cmd in list(self._dispatcher_aliases(command_name)):
            if cmd in self.dispatcher.handlers:
                self.dispatcher.handlers.pop(cmd, None)
                removed = True

        if removed:
            logger.info(f"[LOCAL] Removed dispatcher handlers for {command_name}")
            self.unified.log_core(
                'hot-reload',
                f'Removed handler {command_name}',
                level=LogLevel.INFO,
                handler=handler_name
            )
        else:
            logger.warning(f"[LOCAL] No dispatcher handlers found for {command_name}")

    def _update_dispatcher(self, class_name: str, new_handler: Any) -> None:
        """Update dispatcher with new handler instance.

        Args:
            class_name: Handler class name
            new_handler: New handler instance
        """
        command_name = _command_name_from_class(class_name)
        updated = False

        for cmd in self._dispatcher_aliases(command_name):
            if cmd in self.dispatcher.handlers:
                self.dispatcher.handlers[cmd] = new_handler
                logger.info(f"[LOCAL] Updated dispatcher: {cmd}")
                updated = True

        if not updated:
            logger.warning(f"[LOCAL] Dispatcher did not contain {command_name} to update")

    def _dispatcher_aliases(self, command_name: str):
        """Generate command names that should map back to a handler."""
        yield command_name
        for cmd in self.dispatcher.handlers:
            if cmd.startswith(command_name) and cmd != command_name:
                yield cmd

    def stats(self) -> Dict[str, Any]:
        """Get hot reload statistics.

        Returns:
            Dict with stats
        """
        return {
            "enabled": self.enabled,
            "running": self.observer is not None,
            "watch_dir": str(self.watch_dir),
            "reload_count": self.reload_count,
            "failed_count": self.failed_reloads,
            "success_rate": (
                (self.reload_count / (self.reload_count + self.failed_reloads) * 100)
                if (self.reload_count + self.failed_reloads) > 0
                else 0.0
            )
        }


# Global instance
_hot_reload_manager: Optional[HotReloadManager] = None


def get_hot_reload_manager() -> Optional[HotReloadManager]:
    """Get global hot reload manager instance."""
    return _hot_reload_manager


def init_hot_reload(dispatcher: Any, enabled: bool = True) -> HotReloadManager:
    """Initialize hot reload manager.

    Args:
        dispatcher: CommandDispatcher instance
        enabled: Enable hot reload

    Returns:
        HotReloadManager instance
    """
    global _hot_reload_manager
    _hot_reload_manager = HotReloadManager(dispatcher, enabled=enabled)
    return _hot_reload_manager
