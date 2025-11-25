"""
uDOS Session Manager - Workspace state persistence and session management.

This module provides comprehensive session management with workspace state
persistence, session save/restore, bookmarks, and automatic recovery.

Author: uDOS Development Team
Version: 1.0.6
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class SessionType(Enum):
    """Types of sessions."""
    MANUAL = "manual"        # Manually saved sessions
    AUTOMATIC = "automatic"  # Auto-saved sessions
    CHECKPOINT = "checkpoint"  # Checkpoint sessions
    BACKUP = "backup"        # Backup sessions


@dataclass
class SessionInfo:
    """Session information structure."""
    session_id: str
    name: str
    session_type: SessionType
    created_at: datetime
    last_accessed: datetime
    description: str
    workspace_state: Dict[str, Any]
    environment_state: Dict[str, Any]
    command_history: List[str]
    bookmarks: Dict[str, str]
    active_files: List[str]
    current_directory: str
    grid_state: Optional[Dict[str, Any]] = None
    theme_settings: Optional[Dict[str, Any]] = None
    custom_settings: Optional[Dict[str, Any]] = None


class SessionManager:
    """Comprehensive session management for uDOS workspaces."""

    def __init__(self, root_dir: Optional[Path] = None):
        """Initialize session manager."""
        self.root_dir = Path(root_dir) if root_dir else Path.cwd()
        self.sessions_dir = self.root_dir / "memory" / "sessions"
        self.auto_save_dir = self.sessions_dir / "auto"
        self.manual_save_dir = self.sessions_dir / "manual"
        self.checkpoint_dir = self.sessions_dir / "checkpoints"
        self.backup_dir = self.sessions_dir / "backups"

        # Configuration
        self.config_file = self.sessions_dir / "session_config.json"
        self.current_session_file = self.sessions_dir / "current_session.json"

        # State tracking
        self.current_session: Optional[SessionInfo] = None
        self.auto_save_enabled = True
        self.auto_save_interval = 300  # 5 minutes
        self.max_auto_saves = 10
        self.max_checkpoints = 5
        self.max_backups = 20

        # Initialize directories and config
        self._init_directories()
        self._load_config()
        self._load_current_session()

    def _init_directories(self):
        """Create session directories if they don't exist."""
        for directory in [self.sessions_dir, self.auto_save_dir,
                         self.manual_save_dir, self.checkpoint_dir, self.backup_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def _load_config(self):
        """Load session manager configuration."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.auto_save_enabled = config.get('auto_save_enabled', True)
                    self.auto_save_interval = config.get('auto_save_interval', 300)
                    self.max_auto_saves = config.get('max_auto_saves', 10)
                    self.max_checkpoints = config.get('max_checkpoints', 5)
                    self.max_backups = config.get('max_backups', 20)
            except (json.JSONDecodeError, KeyError):
                pass  # Use defaults

    def _save_config(self):
        """Save session manager configuration."""
        config = {
            'auto_save_enabled': self.auto_save_enabled,
            'auto_save_interval': self.auto_save_interval,
            'max_auto_saves': self.max_auto_saves,
            'max_checkpoints': self.max_checkpoints,
            'max_backups': self.max_backups
        }

        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception:
            pass  # Fail silently

    def _load_current_session(self):
        """Load information about the current session."""
        if self.current_session_file.exists():
            try:
                with open(self.current_session_file, 'r') as f:
                    data = json.load(f)
                    # Load the referenced session
                    session_id = data.get('session_id')
                    if session_id:
                        self.current_session = self.load_session(session_id)
            except (json.JSONDecodeError, KeyError):
                pass

    def _save_current_session_ref(self):
        """Save reference to current session."""
        if self.current_session:
            data = {
                'session_id': self.current_session.session_id,
                'last_updated': datetime.now().isoformat()
            }

            try:
                with open(self.current_session_file, 'w') as f:
                    json.dump(data, f, indent=2)
            except Exception:
                pass

    def create_session(self, name: str, description: str = "",
                      session_type: SessionType = SessionType.MANUAL) -> str:
        """
        Create a new session with current workspace state.

        Args:
            name: Session name
            description: Session description
            session_type: Type of session

        Returns:
            Session ID
        """
        session_id = f"{session_type.value}_{int(time.time())}_{name}"
        current_time = datetime.now()

        # Capture current workspace state
        workspace_state = self._capture_workspace_state()
        environment_state = self._capture_environment_state()
        command_history = self._get_recent_command_history()
        bookmarks = self._get_current_bookmarks()
        active_files = self._get_active_files()
        current_directory = str(Path.cwd())

        # Create session info
        session_info = SessionInfo(
            session_id=session_id,
            name=name,
            session_type=session_type,
            created_at=current_time,
            last_accessed=current_time,
            description=description,
            workspace_state=workspace_state,
            environment_state=environment_state,
            command_history=command_history,
            bookmarks=bookmarks,
            active_files=active_files,
            current_directory=current_directory,
            grid_state=self._capture_grid_state(),
            theme_settings=self._capture_theme_settings(),
            custom_settings=self._capture_custom_settings()
        )

        # Save session
        self._save_session(session_info)

        # Update current session reference
        self.current_session = session_info
        self._save_current_session_ref()

        return session_id

    def save_session(self, session_id: Optional[str] = None, name: Optional[str] = None,
                    description: Optional[str] = None) -> bool:
        """
        Save current workspace state to a session.

        Args:
            session_id: Existing session ID to update, or None to create new
            name: Session name (for new sessions)
            description: Session description

        Returns:
            True if successful
        """
        try:
            if session_id:
                # Update existing session
                session_info = self.load_session(session_id)
                if not session_info:
                    return False

                # Update with current state
                session_info.last_accessed = datetime.now()
                session_info.workspace_state = self._capture_workspace_state()
                session_info.environment_state = self._capture_environment_state()
                session_info.command_history = self._get_recent_command_history()
                session_info.active_files = self._get_active_files()
                session_info.current_directory = str(Path.cwd())
                session_info.grid_state = self._capture_grid_state()
                session_info.theme_settings = self._capture_theme_settings()

                if description:
                    session_info.description = description

                self._save_session(session_info)
                return True
            else:
                # Create new session
                if not name:
                    name = f"Session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

                self.create_session(name, description or "Manual session save")
                return True

        except Exception:
            return False

    def load_session(self, session_id: str) -> Optional[SessionInfo]:
        """
        Load a session by ID.

        Args:
            session_id: Session ID to load

        Returns:
            SessionInfo if found, None otherwise
        """
        # Try different session directories
        for directory in [self.manual_save_dir, self.auto_save_dir,
                         self.checkpoint_dir, self.backup_dir]:
            session_file = directory / f"{session_id}.json"
            if session_file.exists():
                try:
                    with open(session_file, 'r') as f:
                        data = json.load(f)
                        # Convert datetime strings back to datetime objects
                        data['created_at'] = datetime.fromisoformat(data['created_at'])
                        data['last_accessed'] = datetime.fromisoformat(data['last_accessed'])
                        data['session_type'] = SessionType(data['session_type'])

                        return SessionInfo(**data)
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue

        return None

    def restore_session(self, session_id: str) -> bool:
        """
        Restore workspace state from a session.

        Args:
            session_id: Session ID to restore

        Returns:
            True if successful
        """
        session_info = self.load_session(session_id)
        if not session_info:
            return False

        try:
            # Create backup of current state first
            self.create_checkpoint("Before session restore")

            # Restore workspace state
            self._restore_workspace_state(session_info.workspace_state)
            self._restore_environment_state(session_info.environment_state)
            self._restore_bookmarks(session_info.bookmarks)

            # Change to session directory
            if os.path.exists(session_info.current_directory):
                os.chdir(session_info.current_directory)

            # Update current session reference
            session_info.last_accessed = datetime.now()
            self.current_session = session_info
            self._save_current_session_ref()
            self._save_session(session_info)

            return True

        except Exception:
            return False

    def list_sessions(self, session_type: Optional[SessionType] = None) -> List[SessionInfo]:
        """
        List all available sessions.

        Args:
            session_type: Filter by session type, or None for all

        Returns:
            List of SessionInfo objects
        """
        sessions = []

        # Search all session directories
        for directory in [self.manual_save_dir, self.auto_save_dir,
                         self.checkpoint_dir, self.backup_dir]:
            if directory.exists():
                for session_file in directory.glob("*.json"):
                    try:
                        with open(session_file, 'r') as f:
                            data = json.load(f)
                            data['created_at'] = datetime.fromisoformat(data['created_at'])
                            data['last_accessed'] = datetime.fromisoformat(data['last_accessed'])
                            data['session_type'] = SessionType(data['session_type'])

                            session_info = SessionInfo(**data)

                            # Filter by type if specified
                            if session_type is None or session_info.session_type == session_type:
                                sessions.append(session_info)

                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue

        # Sort by last accessed time (most recent first)
        sessions.sort(key=lambda x: x.last_accessed, reverse=True)
        return sessions

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session ID to delete

        Returns:
            True if successful
        """
        # Search for session file in all directories
        for directory in [self.manual_save_dir, self.auto_save_dir,
                         self.checkpoint_dir, self.backup_dir]:
            session_file = directory / f"{session_id}.json"
            if session_file.exists():
                try:
                    session_file.unlink()

                    # Clear current session reference if it was this session
                    if self.current_session and self.current_session.session_id == session_id:
                        self.current_session = None
                        if self.current_session_file.exists():
                            self.current_session_file.unlink()

                    return True
                except OSError:
                    return False

        return False

    def create_checkpoint(self, description: str = "") -> str:
        """
        Create a checkpoint of current state.

        Args:
            description: Checkpoint description

        Returns:
            Checkpoint session ID
        """
        checkpoint_name = f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session_id = self.create_session(
            checkpoint_name,
            description or "Automatic checkpoint",
            SessionType.CHECKPOINT
        )

        # Clean up old checkpoints
        self._cleanup_old_sessions(SessionType.CHECKPOINT, self.max_checkpoints)

        return session_id

    def auto_save(self) -> Optional[str]:
        """
        Perform automatic session save.

        Returns:
            Auto-save session ID if successful, None otherwise
        """
        if not self.auto_save_enabled:
            return None

        auto_save_name = f"autosave_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session_id = self.create_session(
            auto_save_name,
            "Automatic session save",
            SessionType.AUTOMATIC
        )

        # Clean up old auto-saves
        self._cleanup_old_sessions(SessionType.AUTOMATIC, self.max_auto_saves)

        return session_id

    def export_session(self, session_id: str, export_path: Path) -> bool:
        """
        Export a session to a file.

        Args:
            session_id: Session ID to export
            export_path: Path to export file

        Returns:
            True if successful
        """
        session_info = self.load_session(session_id)
        if not session_info:
            return False

        try:
            # Convert session to exportable format
            export_data = asdict(session_info)
            export_data['created_at'] = session_info.created_at.isoformat()
            export_data['last_accessed'] = session_info.last_accessed.isoformat()
            export_data['session_type'] = session_info.session_type.value
            export_data['export_metadata'] = {
                'exported_at': datetime.now().isoformat(),
                'udos_version': '1.0.6',
                'export_format_version': '1.0'
            }

            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)

            return True

        except Exception:
            return False

    def import_session(self, import_path: Path, new_name: Optional[str] = None) -> Optional[str]:
        """
        Import a session from a file.

        Args:
            import_path: Path to import file
            new_name: Optional new name for imported session

        Returns:
            New session ID if successful, None otherwise
        """
        try:
            with open(import_path, 'r') as f:
                data = json.load(f)

            # Validate import format
            if 'export_metadata' not in data:
                return None

            # Create new session ID to avoid conflicts
            original_name = data.get('name', 'imported_session')
            new_session_name = new_name or f"imported_{original_name}"
            new_session_id = f"manual_{int(time.time())}_{new_session_name}"

            # Update session data
            data['session_id'] = new_session_id
            data['name'] = new_session_name
            data['session_type'] = SessionType.MANUAL.value
            data['created_at'] = datetime.now().isoformat()
            data['last_accessed'] = datetime.now().isoformat()

            # Remove export metadata
            del data['export_metadata']

            # Convert back to SessionInfo
            data['created_at'] = datetime.fromisoformat(data['created_at'])
            data['last_accessed'] = datetime.fromisoformat(data['last_accessed'])
            data['session_type'] = SessionType(data['session_type'])

            session_info = SessionInfo(**data)
            self._save_session(session_info)

            return new_session_id

        except Exception:
            return None

    def _save_session(self, session_info: SessionInfo):
        """Save session to appropriate directory."""
        if session_info.session_type == SessionType.MANUAL:
            directory = self.manual_save_dir
        elif session_info.session_type == SessionType.AUTOMATIC:
            directory = self.auto_save_dir
        elif session_info.session_type == SessionType.CHECKPOINT:
            directory = self.checkpoint_dir
        else:  # BACKUP
            directory = self.backup_dir

        session_file = directory / f"{session_info.session_id}.json"

        # Convert to JSON serializable format
        data = asdict(session_info)
        data['created_at'] = session_info.created_at.isoformat()
        data['last_accessed'] = session_info.last_accessed.isoformat()
        data['session_type'] = session_info.session_type.value

        with open(session_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _cleanup_old_sessions(self, session_type: SessionType, max_count: int):
        """Clean up old sessions of a specific type."""
        sessions = self.list_sessions(session_type)

        if len(sessions) > max_count:
            # Keep the most recent ones, delete the rest
            sessions_to_delete = sessions[max_count:]
            for session in sessions_to_delete:
                self.delete_session(session.session_id)

    def _capture_workspace_state(self) -> Dict[str, Any]:
        """Capture current workspace state."""
        # This would integrate with actual uDOS components
        return {
            'workspace_files': [],  # List of open/active files
            'project_settings': {},  # Project-specific settings
            'extension_state': {},   # Extension states
            'user_preferences': {}   # User preferences
        }

    def _capture_environment_state(self) -> Dict[str, Any]:
        """Capture current environment state."""
        return {
            'environment_variables': dict(os.environ),
            'python_path': os.getcwd(),
            'system_info': {
                'platform': os.name,
                'cwd': str(Path.cwd())
            }
        }

    def _get_recent_command_history(self) -> List[str]:
        """Get recent command history."""
        try:
            from core.services.history import CommandHistory
            history = CommandHistory()
            recent_commands = history.get_recent_commands(50)
            return [cmd.command for cmd in recent_commands]
        except (ImportError, AttributeError, IOError):
            return []

    def _get_current_bookmarks(self) -> Dict[str, str]:
        """Get current bookmarks."""
        try:
            from core.utils.smart_picker import SmartFilePicker
            picker = SmartFilePicker()
            return picker.bookmarks.copy()
        except (ImportError, AttributeError):
            return {}

    def _get_active_files(self) -> List[str]:
        """Get list of currently active/open files."""
        # This would integrate with file manager or editor state
        return []

    def _capture_grid_state(self) -> Optional[Dict[str, Any]]:
        """Capture current grid state."""
        # This would integrate with the grid system
        return None

    def _capture_theme_settings(self) -> Optional[Dict[str, Any]]:
        """Capture current theme settings."""
        try:
            from core.theme_manager import ThemeManager
            theme_manager = ThemeManager()
            return {
                'current_mode': theme_manager.current_mode.value,
                'accessibility_mode': theme_manager.accessibility_mode,
                'high_contrast_mode': theme_manager.high_contrast_mode,
                'colorblind_mode': theme_manager.colorblind_mode
            }
        except:
            return None

    def _capture_custom_settings(self) -> Optional[Dict[str, Any]]:
        """Capture custom user settings."""
        return {}

    def _restore_workspace_state(self, workspace_state: Dict[str, Any]):
        """Restore workspace state."""
        # Implementation would restore actual workspace state
        pass

    def _restore_environment_state(self, environment_state: Dict[str, Any]):
        """Restore environment state."""
        # Implementation would restore environment variables and settings
        pass

    def _restore_bookmarks(self, bookmarks: Dict[str, str]):
        """Restore bookmarks."""
        try:
            from core.utils.smart_picker import SmartFilePicker
            picker = SmartFilePicker()
            picker.bookmarks.update(bookmarks)
            picker._save_bookmarks()
        except:
            pass


# Global session manager instance
session_manager = SessionManager()
