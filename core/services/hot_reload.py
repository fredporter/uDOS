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
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from datetime import datetime

import sys
import importlib
import threading
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
    from core.services.logging_manager import get_logger, DevTrace
    logger = get_logger("hot-reload")
except ImportError:
    import logging
    logger = logging.getLogger("hot-reload")


class HandlerReloadEvent(FileSystemEventHandler):
    """File system event handler for Python files."""
    
    def __init__(self, reload_callback: Callable[[str], None]):
        """Initialize event handler.
        
        Args:
            reload_callback: Function to call with filepath on change
        """
        self.reload_callback = reload_callback
        self.last_modified: Dict[str, float] = {}
    
    def on_modified(self, event):
        """Handle file modification event."""
        if event.is_directory:
            return
        
        filepath = event.src_path
        if not filepath.endswith('.py'):
            return
        
        # Debounce: ignore if modified less than 1 second ago
        now = datetime.now().timestamp()
        last = self.last_modified.get(filepath, 0)
        if now - last < 1.0:
            return
        
        self.last_modified[filepath] = now
        self.reload_callback(filepath)


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
            event_handler = HandlerReloadEvent(self._on_file_changed)
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
            
            # Check if module exists
            if module_name not in sys.modules:
                logger.warning(f"[LOCAL] Module not loaded: {module_name}")
                return False
            
            # Reload module
            module = sys.modules[module_name]
            importlib.reload(module)
            
            # Find handler class (assume CapitalCase from snake_case)
            # e.g., map_handler -> MapHandler
            class_name = self._guess_handler_class(handler_name)
            
            if not hasattr(module, class_name):
                logger.warning(f"[LOCAL] Handler class not found: {class_name}")
                return False
            
            handler_class = getattr(module, class_name)
            
            # Re-instantiate handler
            new_handler = handler_class()
            
            # Update dispatcher (preserve old handler reference if in use)
            self._update_dispatcher(class_name, new_handler)
            
            logger.info(f"[LOCAL] ✓ Reloaded {class_name}")
            return True
        
        except Exception as e:
            logger.error(f"[LOCAL] Failed to reload {handler_name}: {e}")
            return False
    
    def _guess_handler_class(self, module_name: str) -> str:
        """Guess handler class name from module name.
        
        Args:
            module_name: Module name (e.g., 'map_handler')
        
        Returns:
            Class name (e.g., 'MapHandler')
        """
        # Convert snake_case to PascalCase
        parts = module_name.split('_')
        return ''.join(word.capitalize() for word in parts)
    
    def _update_dispatcher(self, class_name: str, new_handler: Any) -> None:
        """Update dispatcher with new handler instance.
        
        Args:
            class_name: Handler class name
            new_handler: New handler instance
        """
        # Map class name to command name
        # MapHandler -> MAP, FindHandler -> FIND, etc.
        command_name = class_name.replace('Handler', '').upper()
        
        if command_name in self.dispatcher.handlers:
            self.dispatcher.handlers[command_name] = new_handler
            logger.info(f"[LOCAL] Updated dispatcher: {command_name}")
        else:
            # Try common aliases
            for cmd in self.dispatcher.handlers:
                if cmd.startswith(command_name):
                    self.dispatcher.handlers[cmd] = new_handler
                    logger.info(f"[LOCAL] Updated dispatcher: {cmd}")
                    break
    
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
