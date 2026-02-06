#!/usr/bin/env python3
"""
Web Service - Local web server for localhost-only web interfaces

Provides local web UI (localhost only) that works alongside MeshCore
mesh networking and optional cloud services.

Features:
- Local web server (localhost only)
- REST API endpoints
- WebSocket streaming
- Dashboard UI

Clear Separation:
- MeshCore: Local device mesh (NO internet required)
- Cloud: Remote sync/backup/sharing (requires internet)
- Web: Local web UI (localhost only, this module)

Version: v1.3.0
Author: Fred Porter
Date: December 24, 2025
"""

import json
import time
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class WebServerState(Enum):
    """Web server states."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    ERROR = "error"


@dataclass
class WebConfig:
    """Web server configuration."""
    enabled: bool = False
    host: str = "127.0.0.1"  # Localhost only by default
    port: int = 5000
    auto_start: bool = False
    api_enabled: bool = True
    websocket_enabled: bool = True


class WebService:
    """
    Local web server service.

    Provides web interfaces on localhost only.
    Does NOT require internet connection.
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize web service.

        Args:
            config_dir: Directory for web configuration
        """
        if config_dir is None:
            config_dir = Path(__file__).parent.parent.parent / "memory" / "system"

        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Configuration
        self.config = WebConfig()
        self._load_config()

        # State
        self.state = WebServerState.STOPPED
        self._running = False
        self._server = None

        # Statistics
        self.stats = {
            'requests_served': 0,
            'active_connections': 0,
            'uptime_seconds': 0.0,
            'start_time': 0.0
        }

        # Threading
        self._server_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        # Event callbacks
        self._event_callbacks: Dict[str, List[Callable]] = {
            'started': [],
            'stopped': [],
            'request': [],
            'error': []
        }

    def _load_config(self) -> None:
        """Load web configuration."""
        config_file = self.config_dir / "web_config.json"

        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    data = json.load(f)
                    self.config = WebConfig(**data)
            except Exception as e:
                print(f"Warning: Failed to load web config: {e}")

    def _save_config(self) -> None:
        """Save web configuration."""
        config_file = self.config_dir / "web_config.json"

        try:
            data = {
                'enabled': self.config.enabled,
                'host': self.config.host,
                'port': self.config.port,
                'auto_start': self.config.auto_start,
                'api_enabled': self.config.api_enabled,
                'websocket_enabled': self.config.websocket_enabled
            }
            with open(config_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save web config: {e}")

    # ─────────────────────────────────────────────────────────────
    # Service Lifecycle
    # ─────────────────────────────────────────────────────────────

    def start(self, port: Optional[int] = None) -> bool:
        """
        Start web server.

        Args:
            port: Optional port override

        Returns:
            True if started successfully
        """
        if self._running:
            return True

        if port:
            self.config.port = port

        self._set_state(WebServerState.STARTING)

        try:
            # Start server thread
            self._running = True
            self.stats['start_time'] = time.time()

            self._server_thread = threading.Thread(target=self._run_server, daemon=True)
            self._server_thread.start()

            # Give it a moment to start
            time.sleep(0.5)

            if self._running:
                self._set_state(WebServerState.RUNNING)
                self._emit_event('started', {
                    'host': self.config.host,
                    'port': self.config.port
                })
                return True
            else:
                self._set_state(WebServerState.ERROR)
                return False

        except Exception as e:
            self._set_state(WebServerState.ERROR)
            self._emit_event('error', {'error': str(e)})
            return False

    def stop(self) -> bool:
        """
        Stop web server.

        Returns:
            True if stopped successfully
        """
        if not self._running:
            return True

        self._running = False
        self._save_config()

        # Stop server
        if self._server:
            try:
                # TODO: Implement graceful shutdown
                pass
            except Exception:
                pass

        # Wait for thread
        if self._server_thread and self._server_thread.is_alive():
            self._server_thread.join(timeout=5.0)

        self._set_state(WebServerState.STOPPED)
        self._emit_event('stopped', {})

        return True

    def _run_server(self) -> None:
        """Run web server (called in thread)."""
        # TODO: Implement actual web server using Flask/FastAPI
        # For now, just keep the thread alive

        while self._running:
            time.sleep(1.0)
            self.stats['uptime_seconds'] = time.time() - self.stats['start_time']

    def _set_state(self, new_state: WebServerState) -> None:
        """Update server state."""
        self.state = new_state

    # ─────────────────────────────────────────────────────────────
    # Event System
    # ─────────────────────────────────────────────────────────────

    def on(self, event: str, callback: Callable[[Dict], None]) -> None:
        """Register event callback."""
        if event in self._event_callbacks:
            self._event_callbacks[event].append(callback)

    def off(self, event: str, callback: Callable[[Dict], None]) -> None:
        """Unregister event callback."""
        if event in self._event_callbacks and callback in self._event_callbacks[event]:
            self._event_callbacks[event].remove(callback)

    def _emit_event(self, event: str, data: Dict) -> None:
        """Emit event to callbacks."""
        for callback in self._event_callbacks.get(event, []):
            try:
                callback(data)
            except Exception as e:
                print(f"Warning: Event callback error: {e}")

    # ─────────────────────────────────────────────────────────────
    # Status & Configuration
    # ─────────────────────────────────────────────────────────────

    def get_status(self) -> Dict[str, Any]:
        """Get service status."""
        self.stats['uptime_seconds'] = time.time() - self.stats['start_time'] if self._running else 0.0

        return {
            'state': self.state.value,
            'host': self.config.host,
            'port': self.config.port,
            'url': f"http://{self.config.host}:{self.config.port}" if self._running else None,
            'stats': {
                'requests_served': self.stats['requests_served'],
                'active_connections': self.stats['active_connections'],
                'uptime_seconds': self.stats['uptime_seconds']
            }
        }

    def configure(self, **kwargs) -> None:
        """Update configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        self._save_config()


# Singleton instance
_service_instance: Optional[WebService] = None


def get_web_service() -> WebService:
    """Get or create the web service singleton."""
    global _service_instance

    if _service_instance is None:
        _service_instance = WebService()

    return _service_instance
