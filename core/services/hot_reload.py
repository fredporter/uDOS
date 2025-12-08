"""
Hot Reload System (v1.2.19)

Detect file changes and auto-reload commands without restart.
Background file watcher for development workflow.
"""

from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
import time
import importlib
import sys
from threading import Thread, Lock


class FileWatcher:
    """Watch files for changes"""
    
    def __init__(self, paths: List[Path], callback: Callable[[Path], None]):
        self.paths = paths
        self.callback = callback
        self.file_mtimes: Dict[Path, float] = {}
        self.running = False
        self.thread: Optional[Thread] = None
        
        # Initialize modification times
        self._scan_files()
    
    def _scan_files(self):
        """Scan all files and record modification times"""
        for path in self.paths:
            if path.is_file():
                try:
                    self.file_mtimes[path] = path.stat().st_mtime
                except:
                    pass
            elif path.is_dir():
                # Recursively scan directory
                for file_path in path.rglob('*.py'):
                    try:
                        self.file_mtimes[file_path] = file_path.stat().st_mtime
                    except:
                        pass
    
    def _check_changes(self):
        """Check for file changes"""
        changed_files = []
        
        for file_path, old_mtime in list(self.file_mtimes.items()):
            try:
                if file_path.exists():
                    new_mtime = file_path.stat().st_mtime
                    if new_mtime > old_mtime:
                        changed_files.append(file_path)
                        self.file_mtimes[file_path] = new_mtime
            except:
                pass
        
        # Check for new files
        self._scan_files()
        
        return changed_files
    
    def start(self):
        """Start watching for changes"""
        if self.running:
            return
        
        self.running = True
        self.thread = Thread(target=self._watch_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop watching"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
    
    def _watch_loop(self):
        """Main watch loop"""
        while self.running:
            changed = self._check_changes()
            for file_path in changed:
                try:
                    self.callback(file_path)
                except Exception:
                    pass
            
            time.sleep(1.0)  # Check every second


class HotReloadSystem:
    """
    Hot reload system for development.
    
    Features:
    - Detect file changes
    - Auto-reload modified commands
    - Restart servers without exit
    - Change notifications
    """
    
    def __init__(self):
        """Initialize hot reload system"""
        from core.utils.paths import PATHS
        self.project_root = PATHS.PROJECT_ROOT
        
        # Watch paths
        self.watch_paths = [
            PATHS.CORE / 'commands',
            PATHS.CORE / 'services',
            PATHS.CORE / 'ui',
            PATHS.EXTENSIONS / 'core',
        ]
        
        # State
        self.enabled = False
        self.watcher: Optional[FileWatcher] = None
        self.reload_lock = Lock()
        self.reload_count = 0
        self.last_reload: Optional[str] = None
        self.notifications: List[str] = []
        
    def enable(self):
        """Enable hot reload"""
        if self.enabled:
            return
        
        self.enabled = True
        self.watcher = FileWatcher(self.watch_paths, self._on_file_changed)
        self.watcher.start()
        
        self._add_notification("Hot reload enabled")
    
    def disable(self):
        """Disable hot reload"""
        if not self.enabled:
            return
        
        self.enabled = False
        if self.watcher:
            self.watcher.stop()
            self.watcher = None
        
        self._add_notification("Hot reload disabled")
    
    def _on_file_changed(self, file_path: Path):
        """Handle file change event"""
        with self.reload_lock:
            # Determine what to reload based on file path
            relative = file_path.relative_to(self.project_root)
            
            if 'commands' in str(relative):
                self._reload_command_handler(file_path)
            elif 'services' in str(relative):
                self._reload_service(file_path)
            elif 'ui' in str(relative):
                self._reload_ui_component(file_path)
            
            self.reload_count += 1
            self.last_reload = str(relative)
            
            # Notify
            self._add_notification(f"Reloaded: {relative}")
    
    def _reload_command_handler(self, file_path: Path):
        """Reload a command handler module"""
        try:
            # Convert path to module name
            relative = file_path.relative_to(self.project_root)
            module_path = str(relative).replace('/', '.').replace('.py', '')
            
            # Reload module
            if module_path in sys.modules:
                importlib.reload(sys.modules[module_path])
        except Exception as e:
            self._add_notification(f"Reload failed: {e}")
    
    def _reload_service(self, file_path: Path):
        """Reload a service module"""
        try:
            relative = file_path.relative_to(self.project_root)
            module_path = str(relative).replace('/', '.').replace('.py', '')
            
            if module_path in sys.modules:
                importlib.reload(sys.modules[module_path])
        except Exception as e:
            self._add_notification(f"Reload failed: {e}")
    
    def _reload_ui_component(self, file_path: Path):
        """Reload a UI component"""
        try:
            relative = file_path.relative_to(self.project_root)
            module_path = str(relative).replace('/', '.').replace('.py', '')
            
            if module_path in sys.modules:
                importlib.reload(sys.modules[module_path])
        except Exception as e:
            self._add_notification(f"Reload failed: {e}")
    
    def _add_notification(self, message: str):
        """Add a notification"""
        from datetime import datetime
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.notifications.append(f"[{timestamp}] {message}")
        
        # Keep only last 20 notifications
        if len(self.notifications) > 20:
            self.notifications = self.notifications[-20:]
    
    def get_notifications(self, count: int = 10) -> List[str]:
        """Get recent notifications"""
        return self.notifications[-count:]
    
    def clear_notifications(self):
        """Clear all notifications"""
        self.notifications = []
    
    def get_status(self) -> Dict[str, Any]:
        """Get hot reload status"""
        return {
            'enabled': self.enabled,
            'watch_paths': [str(p) for p in self.watch_paths],
            'reload_count': self.reload_count,
            'last_reload': self.last_reload,
            'notifications': len(self.notifications)
        }
    
    def get_summary(self) -> str:
        """Get status summary for display"""
        if not self.enabled:
            return "Hot Reload: DISABLED"
        
        status = f"Hot Reload: ACTIVE ({self.reload_count} reloads)"
        if self.last_reload:
            status += f" | Last: {self.last_reload}"
        
        return status


# Global instance
_hot_reload: Optional[HotReloadSystem] = None


def get_hot_reload() -> HotReloadSystem:
    """Get global HotReloadSystem instance"""
    global _hot_reload
    if _hot_reload is None:
        _hot_reload = HotReloadSystem()
    return _hot_reload
