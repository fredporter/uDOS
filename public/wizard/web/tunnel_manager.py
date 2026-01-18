"""
POKE Online - Tunnel Manager v1.1.7

Secure tunneling service for uDOS using ngrok or cloudflared.
Enables sharing uDOS instances while maintaining security and privacy.

Features:
- Multiple tunnel providers (ngrok, cloudflared)
- Automatic tunnel lifecycle management
- Security controls and rate limiting
- Integration with uDOS logging system

Author: uDOS Core Team
License: MIT
"""

import os
import json
import time
import subprocess
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from urllib.parse import urlparse

# uDOS imports
from core.services.logging_manager import get_logger


@dataclass
class TunnelInfo:
    """Information about an active tunnel."""
    id: str
    provider: str  # 'ngrok' or 'cloudflared'
    local_port: int
    public_url: str
    subdomain: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime = None
    status: str = "active"  # active, expired, closed
    traffic_bytes: int = 0

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def is_expired(self) -> bool:
        """Check if tunnel has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def time_remaining(self) -> Optional[timedelta]:
        """Get time remaining before expiration."""
        if self.expires_at is None:
            return None
        remaining = self.expires_at - datetime.now()
        return remaining if remaining.total_seconds() > 0 else timedelta(0)


class TunnelProvider:
    """Base class for tunnel providers."""

    def __init__(self, logger):
        self.logger = logger
        self.name = "base"

    def is_available(self) -> bool:
        """Check if provider is available on system."""
        raise NotImplementedError

    def create_tunnel(self, port: int, subdomain: str = None, **kwargs) -> TunnelInfo:
        """Create a new tunnel."""
        raise NotImplementedError

    def close_tunnel(self, tunnel_id: str) -> bool:
        """Close an existing tunnel."""
        raise NotImplementedError

    def get_tunnel_info(self, tunnel_id: str) -> Optional[TunnelInfo]:
        """Get information about a tunnel."""
        raise NotImplementedError


class NgrokProvider(TunnelProvider):
    """Ngrok tunnel provider."""

    def __init__(self, logger):
        super().__init__(logger)
        self.name = "ngrok"
        self._processes = {}  # tunnel_id -> subprocess
        self._auth_token = os.getenv('NGROK_AUTH_TOKEN')

    def is_available(self) -> bool:
        """Check if ngrok is available."""
        try:
            # Check if ngrok binary exists
            result = subprocess.run(['ngrok', 'version'],
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def create_tunnel(self, port: int, subdomain: str = None, **kwargs) -> TunnelInfo:
        """Create ngrok tunnel."""
        if not self.is_available():
            raise RuntimeError("ngrok not available")

        tunnel_id = f"ngrok_{int(time.time())}"

        # Build ngrok command
        cmd = ['ngrok', 'http', str(port), '--log=stdout']

        if subdomain and self._auth_token:
            cmd.extend(['--subdomain', subdomain])

        if self._auth_token:
            cmd.extend(['--authtoken', self._auth_token])

        # Start ngrok process
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait for tunnel to establish (parse output for URL)
            public_url = self._wait_for_tunnel_url(process, timeout=30)

            if not public_url:
                process.terminate()
                raise RuntimeError("Failed to establish ngrok tunnel")

            # Store process
            self._processes[tunnel_id] = process

            # Create tunnel info
            expires_at = datetime.now() + timedelta(hours=kwargs.get('expires', 24))

            tunnel = TunnelInfo(
                id=tunnel_id,
                provider='ngrok',
                local_port=port,
                public_url=public_url,
                subdomain=subdomain,
                expires_at=expires_at,
                status='active'
            )

            self.logger.info(f"Created ngrok tunnel: {public_url} -> localhost:{port}")
            return tunnel

        except Exception as e:
            self.logger.error(f"Failed to create ngrok tunnel: {e}")
            raise

    def _wait_for_tunnel_url(self, process, timeout=30) -> Optional[str]:
        """Wait for ngrok to output the public URL."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            if process.poll() is not None:
                # Process ended unexpectedly
                return None

            # Try to get ngrok status via API (more reliable)
            try:
                import requests
                resp = requests.get('http://127.0.0.1:4040/api/tunnels', timeout=2)
                if resp.status_code == 200:
                    tunnels = resp.json().get('tunnels', [])
                    if tunnels:
                        return tunnels[0]['public_url']
            except:
                pass

            time.sleep(0.5)

        return None

    def close_tunnel(self, tunnel_id: str) -> bool:
        """Close ngrok tunnel."""
        if tunnel_id in self._processes:
            process = self._processes[tunnel_id]
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

            del self._processes[tunnel_id]
            self.logger.info(f"Closed ngrok tunnel: {tunnel_id}")
            return True

        return False

    def get_tunnel_info(self, tunnel_id: str) -> Optional[TunnelInfo]:
        """Get ngrok tunnel information."""
        # This would need to query ngrok API or maintain state
        # Simplified implementation
        return None


class CloudflaredProvider(TunnelProvider):
    """Cloudflared tunnel provider."""

    def __init__(self, logger):
        super().__init__(logger)
        self.name = "cloudflared"
        self._processes = {}

    def is_available(self) -> bool:
        """Check if cloudflared is available."""
        try:
            result = subprocess.run(['cloudflared', '--version'],
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def create_tunnel(self, port: int, subdomain: str = None, **kwargs) -> TunnelInfo:
        """Create cloudflared tunnel."""
        if not self.is_available():
            raise RuntimeError("cloudflared not available")

        tunnel_id = f"cf_{int(time.time())}"

        # Build cloudflared command
        cmd = ['cloudflared', 'tunnel', '--url', f'http://localhost:{port}']

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait for tunnel URL (cloudflared prints to stderr)
            public_url = self._wait_for_cf_url(process, timeout=30)

            if not public_url:
                process.terminate()
                raise RuntimeError("Failed to establish cloudflared tunnel")

            self._processes[tunnel_id] = process

            expires_at = datetime.now() + timedelta(hours=kwargs.get('expires', 24))

            tunnel = TunnelInfo(
                id=tunnel_id,
                provider='cloudflared',
                local_port=port,
                public_url=public_url,
                expires_at=expires_at,
                status='active'
            )

            self.logger.info(f"Created cloudflared tunnel: {public_url} -> localhost:{port}")
            return tunnel

        except Exception as e:
            self.logger.error(f"Failed to create cloudflared tunnel: {e}")
            raise

    def _wait_for_cf_url(self, process, timeout=30) -> Optional[str]:
        """Wait for cloudflared to output the public URL."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            if process.poll() is not None:
                return None

            # Cloudflared outputs URL to stderr
            try:
                line = process.stderr.readline()
                if line and 'https://' in line and 'trycloudflare.com' in line:
                    # Extract URL from log line
                    import re
                    url_match = re.search(r'https://[a-zA-Z0-9.-]+\.trycloudflare\.com', line)
                    if url_match:
                        return url_match.group(0)
            except:
                pass

            time.sleep(0.1)

        return None

    def close_tunnel(self, tunnel_id: str) -> bool:
        """Close cloudflared tunnel."""
        if tunnel_id in self._processes:
            process = self._processes[tunnel_id]
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

            del self._processes[tunnel_id]
            self.logger.info(f"Closed cloudflared tunnel: {tunnel_id}")
            return True

        return False

    def get_tunnel_info(self, tunnel_id: str) -> Optional[TunnelInfo]:
        """Get cloudflared tunnel information."""
        return None


class TunnelManager:
    """
    Tunnel Manager for POKE Online Extension

    Manages secure tunnels using multiple providers (ngrok, cloudflared).
    Provides lifecycle management, security controls, and monitoring.
    """

    def __init__(self, config_dir: str = None):
        from core.utils.paths import PATHS
        if config_dir is None:
            config_dir = str(PATHS.MEMORY_BANK / "system")
        """
        Initialize tunnel manager.

        Args:
            config_dir: Directory for storing tunnel configuration
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Set up logging
        self.logger = get_logger('extension-poke-online')

        # State management
        self.tunnels: Dict[str, TunnelInfo] = {}
        self.state_file = self.config_dir / "poke_tunnels.json"

        # Initialize providers
        self.providers = {
            'ngrok': NgrokProvider(self.logger),
            'cloudflared': CloudflaredProvider(self.logger)
        }

        # Configuration
        self.config = {
            'max_concurrent_tunnels': 3,
            'default_lifetime_hours': 24,
            'cleanup_interval_minutes': 15,
            'preferred_provider': 'ngrok'  # or 'cloudflared'
        }

        # Load existing tunnels
        self._load_tunnels()

        # Start cleanup thread
        self._start_cleanup_thread()

        self.logger.info("Tunnel manager initialized")

    def _load_tunnels(self):
        """Load tunnel state from disk."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)

                for tunnel_data in data.get('tunnels', []):
                    # Convert datetime strings back to objects
                    if tunnel_data.get('created_at'):
                        tunnel_data['created_at'] = datetime.fromisoformat(tunnel_data['created_at'])
                    if tunnel_data.get('expires_at'):
                        tunnel_data['expires_at'] = datetime.fromisoformat(tunnel_data['expires_at'])

                    tunnel = TunnelInfo(**tunnel_data)
                    self.tunnels[tunnel.id] = tunnel

                self.logger.info(f"Loaded {len(self.tunnels)} tunnels from state")

            except Exception as e:
                self.logger.error(f"Failed to load tunnel state: {e}")

    def _save_tunnels(self):
        """Save tunnel state to disk."""
        try:
            tunnels_data = []
            for tunnel in self.tunnels.values():
                data = asdict(tunnel)
                # Convert datetime objects to strings
                if data.get('created_at'):
                    data['created_at'] = data['created_at'].isoformat()
                if data.get('expires_at'):
                    data['expires_at'] = data['expires_at'].isoformat()
                tunnels_data.append(data)

            with open(self.state_file, 'w') as f:
                json.dump({'tunnels': tunnels_data}, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to save tunnel state: {e}")

    def _start_cleanup_thread(self):
        """Start background thread for tunnel cleanup."""
        def cleanup_worker():
            while True:
                try:
                    self._cleanup_expired_tunnels()
                    time.sleep(self.config['cleanup_interval_minutes'] * 60)
                except Exception as e:
                    self.logger.error(f"Cleanup thread error: {e}")
                    time.sleep(60)  # Wait before retrying

        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
        self.logger.info("Cleanup thread started")

    def _cleanup_expired_tunnels(self):
        """Clean up expired tunnels."""
        expired_tunnels = []

        for tunnel_id, tunnel in self.tunnels.items():
            if tunnel.is_expired() or tunnel.status != 'active':
                expired_tunnels.append(tunnel_id)

        for tunnel_id in expired_tunnels:
            self.close_tunnel(tunnel_id)

    def get_available_providers(self) -> List[str]:
        """Get list of available tunnel providers."""
        available = []
        for name, provider in self.providers.items():
            if provider.is_available():
                available.append(name)

        return available

    def create_tunnel(self, port: int, provider: str = None,
                     subdomain: str = None, expires_hours: int = None,
                     **kwargs) -> TunnelInfo:
        """
        Create a new tunnel.

        Args:
            port: Local port to tunnel
            provider: Tunnel provider ('ngrok' or 'cloudflared')
            subdomain: Requested subdomain (if supported)
            expires_hours: Hours until tunnel expires

        Returns:
            TunnelInfo object for the created tunnel
        """
        # Check tunnel limits
        active_tunnels = [t for t in self.tunnels.values() if t.status == 'active']
        if len(active_tunnels) >= self.config['max_concurrent_tunnels']:
            raise RuntimeError(f"Maximum concurrent tunnels ({self.config['max_concurrent_tunnels']}) reached")

        # Select provider
        if provider is None:
            provider = self.config['preferred_provider']

        if provider not in self.providers:
            raise ValueError(f"Unknown provider: {provider}")

        provider_instance = self.providers[provider]
        if not provider_instance.is_available():
            raise RuntimeError(f"Provider {provider} not available")

        # Set expiration
        if expires_hours is None:
            expires_hours = self.config['default_lifetime_hours']

        # Create tunnel
        try:
            tunnel = provider_instance.create_tunnel(
                port=port,
                subdomain=subdomain,
                expires=expires_hours,
                **kwargs
            )

            # Store tunnel
            self.tunnels[tunnel.id] = tunnel
            self._save_tunnels()

            self.logger.info(f"Created tunnel {tunnel.id}: {tunnel.public_url}")
            return tunnel

        except Exception as e:
            self.logger.error(f"Failed to create tunnel: {e}")
            raise

    def close_tunnel(self, tunnel_id: str) -> bool:
        """Close a tunnel."""
        if tunnel_id not in self.tunnels:
            return False

        tunnel = self.tunnels[tunnel_id]
        provider_instance = self.providers.get(tunnel.provider)

        if provider_instance:
            provider_instance.close_tunnel(tunnel_id)

        # Update tunnel status
        tunnel.status = 'closed'
        self._save_tunnels()

        self.logger.info(f"Closed tunnel {tunnel_id}")
        return True

    def list_tunnels(self) -> List[TunnelInfo]:
        """Get list of all tunnels."""
        return list(self.tunnels.values())

    def get_tunnel(self, tunnel_id: str) -> Optional[TunnelInfo]:
        """Get specific tunnel information."""
        return self.tunnels.get(tunnel_id)

    def get_status(self) -> Dict[str, Any]:
        """Get overall tunnel manager status."""
        active_tunnels = [t for t in self.tunnels.values() if t.status == 'active']

        return {
            'total_tunnels': len(self.tunnels),
            'active_tunnels': len(active_tunnels),
            'available_providers': self.get_available_providers(),
            'config': self.config,
            'tunnels': [asdict(t) for t in active_tunnels]
        }


# Convenience function for creating tunnel manager
def create_tunnel_manager() -> TunnelManager:
    """Create and return tunnel manager instance."""
    return TunnelManager()


if __name__ == "__main__":
    # Test tunnel manager
    manager = TunnelManager()

    print("Available providers:", manager.get_available_providers())
    print("Status:", manager.get_status())

    # Example: Create tunnel (requires ngrok/cloudflared)
    # tunnel = manager.create_tunnel(5000, provider='ngrok')
    # print(f"Created tunnel: {tunnel.public_url}")
