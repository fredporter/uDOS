#!/usr/bin/env python3
"""
uDOS Port Manager - Bulletproof Port Management
Handles port conflicts, cleanup, self-healing, and process tracking
"""

import socket
import psutil
import os
import signal
import time
import logging
from typing import Optional, List, Dict
from pathlib import Path

logger = logging.getLogger('uDOS.PortManager')


class PortManager:
    """Manages ports with auto-detection, cleanup, and self-healing"""

    def __init__(self, log_dir: Optional[Path] = None):
        self.log_dir = log_dir or Path(__file__).parent.parent.parent.parent / 'memory' / 'logs'
        self.active_servers = {}  # port -> process info

    def is_port_available(self, port: int) -> bool:
        """Check if port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('127.0.0.1', port))
                return True
        except OSError:
            return False

    def find_process_using_port(self, port: int) -> Optional[Dict]:
        """Find process using a specific port"""
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    try:
                        proc = psutil.Process(conn.pid)
                        return {
                            'pid': conn.pid,
                            'name': proc.name(),
                            'cmdline': ' '.join(proc.cmdline()),
                            'create_time': proc.create_time()
                        }
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        return None
        except Exception as e:
            logger.error(f"Error finding process on port {port}: {e}")
        return None

    def kill_process_on_port(self, port: int, force: bool = False) -> bool:
        """Kill process using specified port"""
        proc_info = self.find_process_using_port(port)

        if not proc_info:
            logger.debug(f"No process found on port {port}")
            return True

        pid = proc_info['pid']
        logger.info(f"Found process {pid} ({proc_info['name']}) on port {port}")

        try:
            # Try graceful shutdown first
            if not force:
                os.kill(pid, signal.SIGTERM)
                logger.info(f"Sent SIGTERM to process {pid}")

                # Wait up to 5 seconds for graceful shutdown
                for _ in range(50):
                    time.sleep(0.1)
                    if self.is_port_available(port):
                        logger.info(f"Process {pid} terminated gracefully")
                        return True

            # Force kill if still running
            os.kill(pid, signal.SIGKILL)
            logger.warning(f"Force killed process {pid}")
            time.sleep(0.5)
            return self.is_port_available(port)

        except ProcessLookupError:
            logger.info(f"Process {pid} already terminated")
            return True
        except PermissionError:
            logger.error(f"Permission denied killing process {pid}")
            return False
        except Exception as e:
            logger.error(f"Error killing process on port {port}: {e}")
            return False

    def cleanup_port(self, port: int, max_retries: int = 3) -> bool:
        """Cleanup port with retries and self-healing"""
        logger.info(f"Cleaning up port {port}...")

        for attempt in range(max_retries):
            if self.is_port_available(port):
                logger.info(f"Port {port} is now available")
                return True

            logger.warning(f"Port {port} in use, attempt {attempt + 1}/{max_retries}")

            # Kill process using port
            if self.kill_process_on_port(port, force=(attempt > 0)):
                return True

            time.sleep(1)

        logger.error(f"Failed to cleanup port {port} after {max_retries} attempts")
        return False

    def find_available_port(self, preferred: int, range_size: int = 10) -> Optional[int]:
        """Find available port, starting with preferred"""
        if self.is_port_available(preferred):
            return preferred

        logger.warning(f"Port {preferred} unavailable, searching nearby...")

        for offset in range(1, range_size):
            port = preferred + offset
            if self.is_port_available(port):
                logger.info(f"Found alternative port: {port}")
                return port

        return None

    def register_server(self, port: int, name: str, pid: Optional[int] = None):
        """Register active server"""
        self.active_servers[port] = {
            'name': name,
            'pid': pid or os.getpid(),
            'start_time': time.time()
        }
        logger.info(f"Registered server '{name}' on port {port}")

    def unregister_server(self, port: int):
        """Unregister server"""
        if port in self.active_servers:
            name = self.active_servers[port]['name']
            del self.active_servers[port]
            logger.info(f"Unregistered server '{name}' from port {port}")

    def cleanup_all_registered(self):
        """Cleanup all registered servers"""
        logger.info("Cleaning up all registered servers...")
        for port in list(self.active_servers.keys()):
            self.cleanup_port(port)
            self.unregister_server(port)

    def health_check(self, port: int) -> bool:
        """Check if server on port is healthy"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                result = s.connect_ex(('127.0.0.1', port))
                return result == 0
        except Exception:
            return False

    def get_status(self) -> Dict:
        """Get status of all registered servers"""
        status = {}
        for port, info in self.active_servers.items():
            status[port] = {
                **info,
                'healthy': self.health_check(port),
                'uptime': time.time() - info['start_time']
            }
        return status


# Singleton instance
_port_manager = None

def get_port_manager() -> PortManager:
    """Get singleton PortManager instance"""
    global _port_manager
    if _port_manager is None:
        _port_manager = PortManager()
    return _port_manager
