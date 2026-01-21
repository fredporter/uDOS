"""
OAuth Connection Manager
========================

Unified OAuth/API connection management for the Wizard Server.
Handles OAuth flows, token refresh, and encrypted credential storage
for multiple services.

Supported Providers:
- Google (Gmail, Calendar, Drive, YouTube)
- GitHub
- Spotify
- Discord
- Notion
- Custom OAuth2 providers

Security:
- Tokens encrypted at rest using Fernet
- Refresh tokens auto-renewed
- Wizard Server only (never on mesh devices)

Version: 1.0.0
Alpha: v1.0.2.1+
"""

import json
import os
import secrets
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from urllib.parse import urlencode, parse_qs, urlparse

from wizard.services.logging_manager import get_logger

logger = get_logger("oauth-manager")

# Optional crypto import
try:
    from cryptography.fernet import Fernet

    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    logger.warning("[OAUTH] cryptography not installed - tokens stored unencrypted")

# Optional httpx for async requests
try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class OAuthProvider(Enum):
    """Supported OAuth providers."""

    GOOGLE = "google"
    GITHUB = "github"
    SPOTIFY = "spotify"
    DISCORD = "discord"
    NOTION = "notion"
    CUSTOM = "custom"


class ConnectionStatus(Enum):
    """Connection status states."""

    NOT_CONFIGURED = "not_configured"
    PENDING_AUTH = "pending_auth"
    CONNECTED = "connected"
    EXPIRED = "expired"
    ERROR = "error"


@dataclass
class OAuthConfig:
    """Configuration for an OAuth provider."""

    provider: OAuthProvider
    client_id: str
    client_secret: str
    scopes: List[str]

    # OAuth endpoints
    auth_url: str
    token_url: str

    # Optional
    redirect_uri: str = "http://localhost:8765/oauth/callback"
    extra_params: Dict[str, str] = field(default_factory=dict)

    # Provider-specific
    api_base_url: str = ""


@dataclass
class OAuthToken:
    """OAuth token storage."""

    provider: OAuthProvider
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[float] = None
    scopes: List[str] = field(default_factory=list)
    token_type: str = "Bearer"

    # Metadata
    created_at: float = field(default_factory=time.time)
    last_refresh: Optional[float] = None
    user_info: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        if not self.expires_at:
            return False
        return time.time() >= self.expires_at - 60  # 60s buffer

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "provider": self.provider.value,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at,
            "scopes": self.scopes,
            "token_type": self.token_type,
            "created_at": self.created_at,
            "last_refresh": self.last_refresh,
            "user_info": self.user_info,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OAuthToken":
        """Create from dictionary."""
        return cls(
            provider=OAuthProvider(data["provider"]),
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            expires_at=data.get("expires_at"),
            scopes=data.get("scopes", []),
            token_type=data.get("token_type", "Bearer"),
            created_at=data.get("created_at", time.time()),
            last_refresh=data.get("last_refresh"),
            user_info=data.get("user_info", {}),
        )


@dataclass
class Connection:
    """A connected service."""

    provider: OAuthProvider
    status: ConnectionStatus
    token: Optional[OAuthToken] = None
    error_message: Optional[str] = None
    last_used: Optional[float] = None

    @property
    def display_name(self) -> str:
        """Get display name for provider."""
        names = {
            OAuthProvider.GOOGLE: "Google",
            OAuthProvider.GITHUB: "GitHub",
            OAuthProvider.SPOTIFY: "Spotify",
            OAuthProvider.DISCORD: "Discord",
            OAuthProvider.NOTION: "Notion",
            OAuthProvider.CUSTOM: "Custom",
        }
        return names.get(self.provider, self.provider.value)

    @property
    def user_display(self) -> str:
        """Get user display (email/username)."""
        if self.token and self.token.user_info:
            return (
                self.token.user_info.get("email")
                or self.token.user_info.get("login")
                or self.token.user_info.get("display_name")
                or "Connected"
            )
        return "Unknown"


# Pre-configured OAuth endpoints
PROVIDER_CONFIGS = {
    OAuthProvider.GOOGLE: {
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "api_base_url": "https://www.googleapis.com",
        "user_info_url": "https://www.googleapis.com/oauth2/v2/userinfo",
        "default_scopes": [
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
        ],
        "extra_params": {"access_type": "offline", "prompt": "consent"},
    },
    OAuthProvider.GITHUB: {
        "auth_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "api_base_url": "https://api.github.com",
        "user_info_url": "https://api.github.com/user",
        "default_scopes": ["read:user", "user:email"],
    },
    OAuthProvider.SPOTIFY: {
        "auth_url": "https://accounts.spotify.com/authorize",
        "token_url": "https://accounts.spotify.com/api/token",
        "api_base_url": "https://api.spotify.com/v1",
        "user_info_url": "https://api.spotify.com/v1/me",
        "default_scopes": ["user-read-private", "user-read-email"],
    },
    OAuthProvider.DISCORD: {
        "auth_url": "https://discord.com/api/oauth2/authorize",
        "token_url": "https://discord.com/api/oauth2/token",
        "api_base_url": "https://discord.com/api/v10",
        "user_info_url": "https://discord.com/api/v10/users/@me",
        "default_scopes": ["identify", "email"],
    },
    OAuthProvider.NOTION: {
        "auth_url": "https://api.notion.com/v1/oauth/authorize",
        "token_url": "https://api.notion.com/v1/oauth/token",
        "api_base_url": "https://api.notion.com/v1",
        "default_scopes": [],  # Notion uses workspace permissions
    },
}


class OAuthConnectionManager:
    """
    Manages OAuth connections for the Wizard Server.

    Wizard Server only - never runs on mesh devices.
    """

    CONFIG_DIR = Path(__file__).parent.parent / "config"
    TOKENS_FILE = CONFIG_DIR / "oauth_tokens.json"
    ENCRYPTION_KEY_FILE = CONFIG_DIR / ".oauth_key"

    def __init__(self):
        """Initialize OAuth manager."""
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        # Encryption key
        self._encryption_key: Optional[bytes] = None
        self._fernet: Optional[Any] = None
        self._load_or_create_key()

        # Provider configs (loaded from config/oauth_providers.json)
        self._configs: Dict[OAuthProvider, OAuthConfig] = {}

        # Active tokens
        self._tokens: Dict[OAuthProvider, OAuthToken] = {}

        # Pending auth states (for CSRF protection)
        self._pending_states: Dict[str, Dict[str, Any]] = {}

        # Load existing tokens
        self._load_tokens()
        self._load_configs()

        logger.info(f"[WIZ] OAuthManager: {len(self._tokens)} connections loaded")

    def _load_or_create_key(self):
        """Load or create encryption key."""
        if not CRYPTO_AVAILABLE:
            return

        if self.ENCRYPTION_KEY_FILE.exists():
            self._encryption_key = self.ENCRYPTION_KEY_FILE.read_bytes()
        else:
            self._encryption_key = Fernet.generate_key()
            self.ENCRYPTION_KEY_FILE.write_bytes(self._encryption_key)
            self.ENCRYPTION_KEY_FILE.chmod(0o600)  # Owner read/write only

        self._fernet = Fernet(self._encryption_key)

    def _encrypt(self, data: str) -> str:
        """Encrypt data."""
        if not self._fernet:
            return data
        return self._fernet.encrypt(data.encode()).decode()

    def _decrypt(self, data: str) -> str:
        """Decrypt data."""
        if not self._fernet:
            return data
        return self._fernet.decrypt(data.encode()).decode()

    def _load_tokens(self):
        """Load tokens from encrypted storage."""
        if not self.TOKENS_FILE.exists():
            return

        try:
            encrypted_data = self.TOKENS_FILE.read_text()
            decrypted = self._decrypt(encrypted_data)
            data = json.loads(decrypted)

            for provider_str, token_data in data.get("tokens", {}).items():
                provider = OAuthProvider(provider_str)
                self._tokens[provider] = OAuthToken.from_dict(token_data)

        except Exception as e:
            logger.error(f"[WIZ] Failed to load OAuth tokens: {e}")

    def _save_tokens(self):
        """Save tokens to encrypted storage."""
        data = {
            "version": "1.0.0",
            "updated_at": datetime.now().isoformat(),
            "tokens": {
                provider.value: token.to_dict()
                for provider, token in self._tokens.items()
            },
        }

        encrypted = self._encrypt(json.dumps(data))
        self.TOKENS_FILE.write_text(encrypted)
        self.TOKENS_FILE.chmod(0o600)

    def _load_configs(self):
        """Load provider configurations."""
        config_file = self.CONFIG_DIR / "oauth_providers.json"

        if config_file.exists():
            try:
                data = json.loads(config_file.read_text())
                for provider_str, config_data in data.items():
                    provider = OAuthProvider(provider_str)
                    defaults = PROVIDER_CONFIGS.get(provider, {})

                    self._configs[provider] = OAuthConfig(
                        provider=provider,
                        client_id=config_data.get("client_id", ""),
                        client_secret=config_data.get("client_secret", ""),
                        scopes=config_data.get(
                            "scopes", defaults.get("default_scopes", [])
                        ),
                        auth_url=config_data.get(
                            "auth_url", defaults.get("auth_url", "")
                        ),
                        token_url=config_data.get(
                            "token_url", defaults.get("token_url", "")
                        ),
                        redirect_uri=config_data.get(
                            "redirect_uri", "http://localhost:8765/oauth/callback"
                        ),
                        api_base_url=config_data.get(
                            "api_base_url", defaults.get("api_base_url", "")
                        ),
                        extra_params=config_data.get(
                            "extra_params", defaults.get("extra_params", {})
                        ),
                    )
            except Exception as e:
                logger.error(f"[WIZ] Failed to load OAuth configs: {e}")

    # === Public API ===

    def get_connection(self, provider: OAuthProvider) -> Connection:
        """Get connection status for a provider."""
        config = self._configs.get(provider)
        token = self._tokens.get(provider)

        if not config or not config.client_id:
            return Connection(
                provider=provider,
                status=ConnectionStatus.NOT_CONFIGURED,
            )

        if not token:
            return Connection(
                provider=provider,
                status=ConnectionStatus.PENDING_AUTH,
            )

        if token.is_expired:
            return Connection(
                provider=provider,
                status=ConnectionStatus.EXPIRED,
                token=token,
            )

        return Connection(
            provider=provider,
            status=ConnectionStatus.CONNECTED,
            token=token,
        )

    def get_all_connections(self) -> Dict[str, Connection]:
        """Get all configured connections."""
        connections = {}

        for provider in OAuthProvider:
            if provider != OAuthProvider.CUSTOM:
                conn = self.get_connection(provider)
                connections[provider.value] = conn

        return connections

    def get_auth_url(
        self, provider: OAuthProvider, extra_scopes: List[str] = None
    ) -> Optional[str]:
        """
        Generate OAuth authorization URL.

        Args:
            provider: OAuth provider
            extra_scopes: Additional scopes to request

        Returns:
            Authorization URL or None if not configured
        """
        config = self._configs.get(provider)
        if not config or not config.client_id:
            return None

        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        self._pending_states[state] = {
            "provider": provider.value,
            "created_at": time.time(),
            "extra_scopes": extra_scopes or [],
        }

        # Build scopes
        scopes = list(config.scopes)
        if extra_scopes:
            scopes.extend(extra_scopes)

        # Build URL
        params = {
            "client_id": config.client_id,
            "redirect_uri": config.redirect_uri,
            "response_type": "code",
            "scope": " ".join(scopes),
            "state": state,
            **config.extra_params,
        }

        return f"{config.auth_url}?{urlencode(params)}"

    async def handle_callback(
        self,
        code: str,
        state: str,
    ) -> Connection:
        """
        Handle OAuth callback with authorization code.

        Args:
            code: Authorization code from provider
            state: State parameter for CSRF validation

        Returns:
            Updated Connection status
        """
        # Validate state
        if state not in self._pending_states:
            raise ValueError("Invalid state parameter - possible CSRF attack")

        pending = self._pending_states.pop(state)
        provider = OAuthProvider(pending["provider"])
        config = self._configs.get(provider)

        if not config:
            raise ValueError(f"Provider {provider.value} not configured")

        # Exchange code for token
        token_data = await self._exchange_code(config, code)

        # Create token object
        token = OAuthToken(
            provider=provider,
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            expires_at=time.time() + token_data.get("expires_in", 3600),
            scopes=token_data.get("scope", "").split(),
            token_type=token_data.get("token_type", "Bearer"),
        )

        # Fetch user info
        try:
            token.user_info = await self._fetch_user_info(provider, token)
        except Exception as e:
            logger.warning(f"[WIZ] Failed to fetch user info: {e}")

        # Store token
        self._tokens[provider] = token
        self._save_tokens()

        logger.info(
            f"[WIZ] Connected: {provider.value} ({token.user_info.get('email', 'unknown')})"
        )

        return Connection(
            provider=provider,
            status=ConnectionStatus.CONNECTED,
            token=token,
        )

    async def refresh_token(self, provider: OAuthProvider) -> bool:
        """
        Refresh an expired token.

        Args:
            provider: Provider to refresh

        Returns:
            True if refresh successful
        """
        token = self._tokens.get(provider)
        config = self._configs.get(provider)

        if not token or not token.refresh_token or not config:
            return False

        try:
            token_data = await self._refresh_token(config, token.refresh_token)

            token.access_token = token_data["access_token"]
            token.expires_at = time.time() + token_data.get("expires_in", 3600)
            token.last_refresh = time.time()

            if "refresh_token" in token_data:
                token.refresh_token = token_data["refresh_token"]

            self._save_tokens()
            logger.info(f"[WIZ] Refreshed token: {provider.value}")
            return True

        except Exception as e:
            logger.error(f"[WIZ] Token refresh failed for {provider.value}: {e}")
            return False

    async def disconnect(self, provider: OAuthProvider) -> bool:
        """
        Disconnect/revoke a provider.

        Args:
            provider: Provider to disconnect

        Returns:
            True if disconnected
        """
        if provider in self._tokens:
            del self._tokens[provider]
            self._save_tokens()
            logger.info(f"[WIZ] Disconnected: {provider.value}")
            return True
        return False

    def get_access_token(self, provider: OAuthProvider) -> Optional[str]:
        """
        Get access token for a provider.

        Auto-refreshes if expired.

        Args:
            provider: Provider to get token for

        Returns:
            Access token or None
        """
        token = self._tokens.get(provider)
        if not token:
            return None

        if token.is_expired and token.refresh_token:
            # Run refresh synchronously (for non-async contexts)
            import asyncio

            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Already in async context
                    return token.access_token  # Return potentially expired token
                loop.run_until_complete(self.refresh_token(provider))
            except Exception:
                pass

        return token.access_token

    # === Helper Methods ===

    async def _exchange_code(self, config: OAuthConfig, code: str) -> Dict[str, Any]:
        """Exchange authorization code for tokens."""
        if not HTTPX_AVAILABLE:
            raise RuntimeError("httpx not installed for OAuth")

        data = {
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": config.redirect_uri,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                config.token_url,
                data=data,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            return response.json()

    async def _refresh_token(
        self, config: OAuthConfig, refresh_token: str
    ) -> Dict[str, Any]:
        """Refresh access token."""
        if not HTTPX_AVAILABLE:
            raise RuntimeError("httpx not installed for OAuth")

        data = {
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                config.token_url,
                data=data,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            return response.json()

    async def _fetch_user_info(
        self, provider: OAuthProvider, token: OAuthToken
    ) -> Dict[str, Any]:
        """Fetch user info from provider."""
        if not HTTPX_AVAILABLE:
            return {}

        provider_info = PROVIDER_CONFIGS.get(provider, {})
        user_info_url = provider_info.get("user_info_url")

        if not user_info_url:
            return {}

        async with httpx.AsyncClient() as client:
            response = await client.get(
                user_info_url,
                headers={
                    "Authorization": f"{token.token_type} {token.access_token}",
                    "Accept": "application/json",
                },
            )
            response.raise_for_status()
            return response.json()


# Singleton
_oauth_manager: Optional[OAuthConnectionManager] = None


def get_oauth_manager() -> OAuthConnectionManager:
    """Get or create OAuth manager singleton."""
    global _oauth_manager
    if _oauth_manager is None:
        _oauth_manager = OAuthConnectionManager()
    return _oauth_manager


# Convenience functions
def get_google_token() -> Optional[str]:
    """Get Google access token."""
    return get_oauth_manager().get_access_token(OAuthProvider.GOOGLE)


def get_github_token() -> Optional[str]:
    """Get GitHub access token."""
    return get_oauth_manager().get_access_token(OAuthProvider.GITHUB)


def get_spotify_token() -> Optional[str]:
    """Get Spotify access token."""
    return get_oauth_manager().get_access_token(OAuthProvider.SPOTIFY)


def list_connections() -> Dict[str, Dict[str, Any]]:
    """List all connections with status."""
    manager = get_oauth_manager()
    connections = manager.get_all_connections()

    return {
        name: {
            "status": conn.status.value,
            "user": conn.user_display,
            "provider": conn.display_name,
        }
        for name, conn in connections.items()
    }
