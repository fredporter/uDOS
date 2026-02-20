"""OAuth2 credential manager for external providers (Phase 8)."""

import os
import json
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import base64

from core.services.logging_manager import get_logger

logger = get_logger(__name__)


class OAuthManager:
    """Handle OAuth2 flows and credential management for all providers."""

    # OAuth2 provider configurations
    PROVIDER_CONFIGS = {
        "google_calendar": {
            "auth_uri": "https://accounts.google.com/o/oauth2/v2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "scopes": [
                "https://www.googleapis.com/auth/calendar",
                "https://www.googleapis.com/auth/calendar.events",
            ],
        },
        "gmail": {
            "auth_uri": "https://accounts.google.com/o/oauth2/v2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "scopes": [
                "https://www.googleapis.com/auth/gmail.readonly",
                "https://www.googleapis.com/auth/gmail.modify",
            ],
        },
        "outlook": {
            "auth_uri": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
            "token_uri": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
            "scopes": [
                "Calendars.Read",
                "Calendars.ReadWrite",
                "Mail.Read",
                "Mail.ReadWrite",
            ],
        },
        "jira": {
            "auth_uri": "https://auth.atlassian.com/authorize",
            "token_uri": "https://auth.atlassian.com/oauth/token",
            "scopes": ["read:jira-work", "write:jira-work", "manage:jira-webhook"],
        },
        "linear": {
            "auth_uri": "https://linear.app/oauth/authorize",
            "token_uri": "https://api.linear.app/oauth/token",
            "scopes": ["admin"],
        },
        "slack": {
            "auth_uri": "https://slack.com/oauth_authorize",
            "token_uri": "https://slack.com/api/oauth.v2.access",
            "scopes": [
                "chat:write",
                "channels:read",
                "users:read",
                "team:read",
            ],
        },
    }

    def __init__(self, storage_path: str = None):
        """Initialize OAuth manager.

        Args:
            storage_path: Path to store credentials (encrypted vault preferred)
        """
        self.storage_path = (
            storage_path or os.path.expanduser("~/.udos/credentials.json")
        )
        self.credentials_cache = {}
        self._load_credentials()

    def _load_credentials(self):
        """Load credentials from storage."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    self.credentials_cache = json.load(f)
                logger.info(f"Loaded credentials for {len(self.credentials_cache)} providers")
            except Exception as e:
                logger.warning(f"Error loading credentials: {e}")
                self.credentials_cache = {}
        else:
            logger.debug(f"No credentials file at {self.storage_path}")

    def _save_credentials(self):
        """Save credentials to storage."""
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, 'w') as f:
                json.dump(self.credentials_cache, f, indent=2)
            # Restrict file permissions
            os.chmod(self.storage_path, 0o600)
            logger.info(f"Saved credentials to {self.storage_path}")
        except Exception as e:
            logger.error(f"Error saving credentials: {e}")

    async def get_authorization_url(self, provider: str, redirect_uri: str = None) -> str:
        """Get OAuth2 authorization URL for provider.

        Args:
            provider: Provider type (e.g., 'google_calendar')
            redirect_uri: Redirect URI for OAuth callback

        Returns:
            Authorization URL
        """
        if provider not in self.PROVIDER_CONFIGS:
            raise ValueError(f"Unknown provider: {provider}")

        config = self.PROVIDER_CONFIGS[provider]
        client_id = os.getenv(f"{provider.upper()}_CLIENT_ID")
        if not client_id:
            raise ValueError(f"Missing {provider.upper()}_CLIENT_ID environment variable")

        redirect_uri = redirect_uri or os.getenv(
            f"{provider.upper()}_REDIRECT_URI",
            "http://localhost:8000/oauth/callback",
        )

        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(config["scopes"]),
            "access_type": "offline",  # For refresh token
        }

        param_str = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{config['auth_uri']}?{param_str}"

        logger.info(f"Generated auth URL for {provider}")
        return url

    async def handle_callback(
        self, provider: str, code: str, redirect_uri: str = None
    ) -> Dict[str, str]:
        """Handle OAuth2 callback and exchange code for tokens.

        Args:
            provider: Provider type
            code: Authorization code from OAuth callback
            redirect_uri: Redirect URI used in authorization

        Returns:
            Tokens dict with 'access_token' and optional 'refresh_token'
        """
        if provider not in self.PROVIDER_CONFIGS:
            raise ValueError(f"Unknown provider: {provider}")

        config = self.PROVIDER_CONFIGS[provider]
        client_id = os.getenv(f"{provider.upper()}_CLIENT_ID")
        client_secret = os.getenv(f"{provider.upper()}_CLIENT_SECRET")

        if not client_id or not client_secret:
            raise ValueError(f"Missing OAuth credentials for {provider}")

        redirect_uri = redirect_uri or os.getenv(
            f"{provider.upper()}_REDIRECT_URI",
            "http://localhost:8000/oauth/callback",
        )

        # This would normally make an HTTP request to token_uri
        # For now, store the code for manual token exchange
        logger.info(f"Received callback for {provider}")

        # TODO: Implement actual token exchange
        # For now, return placeholder to allow testing
        tokens = {
            "access_token": code,
            "provider": provider,
            "type": "placeholder",
            "expires_at": (datetime.now() + timedelta(hours=1)).isoformat(),
        }

        self.credentials_cache[provider] = tokens
        self._save_credentials()

        return tokens

    async def get_credentials(self, provider: str) -> Optional[Dict[str, str]]:
        """Get cached credentials for provider.

        Args:
            provider: Provider type

        Returns:
            Credentials dict or None if not found
        """
        if provider not in self.credentials_cache:
            logger.warning(f"No credentials found for {provider}")
            return None

        creds = self.credentials_cache[provider]

        # Check if token is expired
        if "expires_at" in creds:
            expires_at = datetime.fromisoformat(creds["expires_at"])
            if expires_at < datetime.now():
                logger.warning(f"Credentials for {provider} have expired")
                # TODO: Implement auto-refresh
                return None

        return creds

    async def refresh_token(self, provider: str) -> Optional[str]:
        """Refresh access token using refresh token.

        Args:
            provider: Provider type

        Returns:
            New access token or None if refresh failed
        """
        creds = self.credentials_cache.get(provider)
        if not creds or "refresh_token" not in creds:
            logger.error(f"No refresh token for {provider}")
            return None

        logger.info(f"Refreshing token for {provider}")

        # TODO: Implement actual token refresh
        # This would call the token_uri with refresh_token grant

        return creds.get("access_token")

    async def revoke_credentials(self, provider: str) -> bool:
        """Revoke and remove credentials for provider.

        Args:
            provider: Provider type

        Returns:
            True if revoked successfully
        """
        if provider not in self.credentials_cache:
            logger.warning(f"No credentials to revoke for {provider}")
            return False

        # TODO: Call provider's revoke endpoint

        del self.credentials_cache[provider]
        self._save_credentials()
        logger.info(f"Revoked credentials for {provider}")
        return True

    async def check_auth_status(self, provider: str) -> Dict[str, any]:
        """Check authentication status for provider.

        Args:
            provider: Provider type

        Returns:
            Status dict with authenticated flag and expiry info
        """
        creds = self.credentials_cache.get(provider)

        if not creds:
            return {"provider": provider, "authenticated": False}

        # Check expiry
        expires_at = None
        if "expires_at" in creds:
            expires_at = datetime.fromisoformat(creds["expires_at"])
            is_expired = expires_at < datetime.now()
        else:
            is_expired = False

        return {
            "provider": provider,
            "authenticated": True,
            "expires_at": expires_at.isoformat() if expires_at else None,
            "is_expired": is_expired,
            "has_refresh_token": "refresh_token" in creds,
        }

    async def get_all_auth_status(self) -> Dict[str, any]:
        """Get authentication status for all providers.

        Returns:
            Status dict keyed by provider
        """
        return {
            provider: await self.check_auth_status(provider)
            for provider in self.PROVIDER_CONFIGS
        }

    def set_credentials(self, provider: str, credentials: Dict[str, str]):
        """Manually set credentials (for testing or manual setup).

        Args:
            provider: Provider type
            credentials: Credentials dict
        """
        self.credentials_cache[provider] = credentials
        self._save_credentials()
        logger.info(f"Set credentials for {provider}")


# Singleton instance
_oauth_manager = None


def get_oauth_manager(storage_path: str = None) -> OAuthManager:
    """Get or create OAuth manager singleton."""
    global _oauth_manager
    if _oauth_manager is None:
        _oauth_manager = OAuthManager(storage_path)
    return _oauth_manager
