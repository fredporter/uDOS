"""
Sync Manager for uDOS v1.2.9

Coordinates synchronization operations between local and cloud storage.
Provides scheduling, background sync, and sync history management.

Features:
- Automatic sync scheduling
- Background sync operations
- Sync history and rollback
- Bandwidth optimization
- Error recovery and retry logic

Author: @fredporter
Version: 1.2.9
Date: December 2025
"""

import json
import time
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from threading import Thread, Lock
from enum import Enum

from core.services.sync_engine import get_sync_engine, ConflictStrategy


class SyncMode(Enum):
    """Sync operation modes."""
    MANUAL = "manual"
    AUTO = "auto"
    SCHEDULED = "scheduled"


class SyncManager:
    """
    High-level sync coordination and management.
    
    Handles:
    - Sync scheduling and automation
    - History tracking
    - Background operations
    - Settings management
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize sync manager.
        
        Args:
            project_root: Project root path
        """
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.engine = get_sync_engine()
        
        # Settings storage
        self.settings_dir = self.project_root / "memory" / "system" / "sync"
        self.settings_dir.mkdir(parents=True, exist_ok=True)
        self.settings_file = self.settings_dir / "sync_settings.json"
        self.history_file = self.settings_dir / "sync_history.json"
        
        # Load settings
        self.settings = self._load_settings()
        self.history = self._load_history()
        
        # Background sync
        self._sync_lock = Lock()
        self._background_thread: Optional[Thread] = None
        self._should_stop = False
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load sync settings."""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            'enabled': False,
            'mode': SyncMode.MANUAL.value,
            'auto_interval': 300,  # 5 minutes
            'conflict_strategy': ConflictStrategy.NEWEST_WINS.value,
            'max_history': 50
        }
    
    def _save_settings(self) -> None:
        """Save sync settings."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save settings: {e}")
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """Load sync history."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return []
    
    def _save_history(self) -> None:
        """Save sync history."""
        try:
            # Limit history size
            max_history = self.settings.get('max_history', 50)
            if len(self.history) > max_history:
                self.history = self.history[-max_history:]
            
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Failed to save history: {e}")
    
    def _add_history_entry(self, result: Dict[str, Any]) -> None:
        """
        Add entry to sync history.
        
        Args:
            result: Sync result dictionary
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'success': result.get('success', False),
            'stats': result.get('stats', {}),
            'errors': result.get('errors', [])
        }
        self.history.append(entry)
        self._save_history()
    
    def enable(self, mode: SyncMode = SyncMode.AUTO) -> None:
        """
        Enable automatic sync.
        
        Args:
            mode: Sync mode (AUTO or SCHEDULED)
        """
        self.settings['enabled'] = True
        self.settings['mode'] = mode.value
        self._save_settings()
        
        if mode == SyncMode.AUTO:
            self._start_background_sync()
    
    def disable(self) -> None:
        """Disable automatic sync."""
        self.settings['enabled'] = False
        self._save_settings()
        self._stop_background_sync()
    
    def set_interval(self, seconds: int) -> None:
        """
        Set auto-sync interval.
        
        Args:
            seconds: Interval in seconds (minimum 60)
        """
        self.settings['auto_interval'] = max(60, seconds)
        self._save_settings()
    
    def set_conflict_strategy(self, strategy: ConflictStrategy) -> None:
        """
        Set default conflict resolution strategy.
        
        Args:
            strategy: Conflict resolution strategy
        """
        self.settings['conflict_strategy'] = strategy.value
        self._save_settings()
        
        # Update engine metadata
        self.engine.metadata['conflict_strategy'] = strategy.value
        self.engine._save_metadata()
    
    def sync_now(self) -> Dict[str, Any]:
        """
        Perform immediate sync operation.
        
        Returns:
            Sync result dictionary
        """
        with self._sync_lock:
            strategy = ConflictStrategy(self.settings.get('conflict_strategy', 'newest-wins'))
            result = self.engine.sync_all(strategy)
            self._add_history_entry(result)
            return result
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current sync status.
        
        Returns:
            Status dictionary with settings, last sync, stats
        """
        last_sync_time = self.engine.metadata.get('last_sync')
        last_entry = self.history[-1] if self.history else None
        
        # Calculate time since last sync
        time_since_sync = None
        if last_sync_time:
            try:
                last_sync_dt = datetime.fromisoformat(last_sync_time)
                delta = datetime.now() - last_sync_dt
                time_since_sync = str(delta).split('.')[0]  # Remove microseconds
            except Exception:
                pass
        
        return {
            'enabled': self.settings['enabled'],
            'mode': self.settings['mode'],
            'interval': self.settings['auto_interval'],
            'conflict_strategy': self.settings['conflict_strategy'],
            'last_sync': last_sync_time,
            'time_since_sync': time_since_sync,
            'last_stats': last_entry.get('stats') if last_entry else {},
            'background_running': self._background_thread is not None and self._background_thread.is_alive(),
            'total_syncs': len(self.history)
        }
    
    def get_changes(self) -> Dict[str, List]:
        """
        Get pending changes without syncing.
        
        Returns:
            Changes dictionary from sync engine
        """
        return self.engine.detect_changes()
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent sync history.
        
        Args:
            limit: Number of entries to return
            
        Returns:
            List of history entries (most recent first)
        """
        return list(reversed(self.history[-limit:]))
    
    def rollback(self, timestamp: Optional[str] = None) -> Dict[str, Any]:
        """
        Rollback to previous sync state.
        
        Args:
            timestamp: Specific timestamp to rollback to (defaults to last sync)
            
        Returns:
            Rollback result
        """
        # Find target history entry
        target_entry = None
        if timestamp:
            for entry in reversed(self.history):
                if entry['timestamp'] == timestamp:
                    target_entry = entry
                    break
        else:
            # Use last successful sync
            for entry in reversed(self.history):
                if entry.get('success'):
                    target_entry = entry
                    break
        
        if not target_entry:
            return {
                'success': False,
                'error': 'No valid sync state found for rollback'
            }
        
        # For now, rollback means re-downloading all from cloud
        # In future, could use versioned backups
        return {
            'success': False,
            'error': 'Rollback not yet implemented',
            'target': target_entry['timestamp']
        }
    
    def _start_background_sync(self) -> None:
        """Start background sync thread."""
        if self._background_thread and self._background_thread.is_alive():
            return
        
        self._should_stop = False
        self._background_thread = Thread(target=self._background_sync_loop, daemon=True)
        self._background_thread.start()
    
    def _stop_background_sync(self) -> None:
        """Stop background sync thread."""
        self._should_stop = True
        if self._background_thread:
            self._background_thread.join(timeout=5)
    
    def _background_sync_loop(self) -> None:
        """Background sync loop (runs in separate thread)."""
        interval = self.settings.get('auto_interval', 300)
        
        while not self._should_stop:
            try:
                # Wait for interval (check stop flag every second)
                for _ in range(interval):
                    if self._should_stop:
                        return
                    time.sleep(1)
                
                # Perform sync
                if self.settings.get('enabled'):
                    self.sync_now()
                
            except Exception as e:
                print(f"Background sync error: {e}")
                # Continue loop even on error
    
    def cleanup(self) -> None:
        """Cleanup resources (call on shutdown)."""
        self._stop_background_sync()


# Singleton instance
_sync_manager_instance = None

def get_sync_manager() -> SyncManager:
    """Get singleton sync manager instance."""
    global _sync_manager_instance
    if _sync_manager_instance is None:
        _sync_manager_instance = SyncManager()
    return _sync_manager_instance
