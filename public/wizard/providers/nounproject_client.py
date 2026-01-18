"""
Noun Project Client - Icon Library API
=======================================

Provider client for The Noun Project icon library API.
Search and download icons with ASCII art conversion support.

API: https://api.thenounproject.com/v2
Auth: OAuth 1.0a (requires API key + secret)

Alpha v1.0.0.20
"""

import time
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path

from .base_provider import (
    BaseProvider,
    ProviderConfig,
    ProviderStatus,
    ProviderError,
    AuthenticationError,
    RateLimitError,
)

# API limits
RATE_LIMIT_RPM = 100  # Requests per minute
DAILY_LIMIT = 5000  # Free tier daily limit


@dataclass
class NounProjectConfig(ProviderConfig):
    """Noun Project configuration."""

    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    default_format: str = "svg"  # svg or png
    default_size: int = 128  # PNG size
    cache_enabled: bool = True
    cache_dir: str = "memory/cache/icons"
    max_results: int = 20


@dataclass
class IconResult:
    """Icon search result."""

    id: int
    term: str
    preview_url: str
    attribution: str
    attribution_required: bool
    collections: List[str] = field(default_factory=list)


class NounProjectClient(BaseProvider):
    """
    Noun Project API client for icon library access.

    Usage:
        config = NounProjectConfig(
            name="nounproject",
            api_key="your-key",
            api_secret="your-secret"
        )
        client = NounProjectClient(config)
        await client.authenticate()

        icons = await client.search("computer")
        icon_data = await client.download(icons[0].id, format="svg")
    """

    API_BASE = "https://api.thenounproject.com/v2"

    def __init__(self, config: NounProjectConfig = None):
        """Initialize Noun Project client."""
        if config is None:
            config = NounProjectConfig(name="nounproject")

        # Try to get credentials from environment
        if not config.api_key:
            import os

            config.api_key = os.environ.get("NOUNPROJECT_API_KEY")
            config.api_secret = os.environ.get("NOUNPROJECT_API_SECRET")

        super().__init__(config)
        self.config: NounProjectConfig = config
        self._daily_requests = 0
        self._last_reset = time.time()
        self._cache: Dict[str, Any] = {}

        # Ensure cache directory exists
        if config.cache_enabled:
            Path(config.cache_dir).mkdir(parents=True, exist_ok=True)

    async def authenticate(self) -> bool:
        """
        Verify API credentials are valid.

        Returns:
            True if authentication successful
        """
        if not self.config.api_key or not self.config.api_secret:
            self.status = ProviderStatus.AUTH_REQUIRED
            raise AuthenticationError(
                "NOUNPROJECT_API_KEY and NOUNPROJECT_API_SECRET not configured"
            )

        try:
            # Test authentication with a minimal request
            response = await self._make_request("GET", "/icon/1")

            if "icon" in response or "id" in response:
                self.status = ProviderStatus.READY
                return True
            else:
                self.status = ProviderStatus.ERROR
                return False

        except AuthenticationError:
            raise
        except Exception as e:
            self.status = ProviderStatus.ERROR
            raise AuthenticationError(f"Authentication failed: {str(e)}")

    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a generic request.

        Args:
            request: Request with 'action' and params

        Returns:
            Response dictionary
        """
        action = request.get("action", "search")

        if action == "search":
            return await self.search(
                term=request.get("term", ""),
                limit=request.get("limit", self.config.max_results),
            )
        elif action == "get":
            return await self.get_icon(icon_id=request.get("id"))
        elif action == "download":
            return await self.download(
                icon_id=request.get("id"),
                format=request.get("format", self.config.default_format),
                size=request.get("size", self.config.default_size),
            )
        elif action == "collection":
            return await self.get_collection(slug=request.get("slug"))
        elif action == "collections":
            return await self.list_collections()
        elif action == "recent":
            return await self.get_recent_downloads()
        elif action == "ascii":
            return await self.get_ascii(
                icon_id=request.get("id"),
                width=request.get("width", 40),
            )
        else:
            raise ProviderError(f"Unknown action: {action}")

    def get_status(self) -> Dict[str, Any]:
        """Get provider status."""
        return {
            "provider": "nounproject",
            "status": self.status.value,
            "available": self.is_available(),
            "configured": bool(self.config.api_key and self.config.api_secret),
            "limits": {
                "requests_today": self._daily_requests,
                "daily_limit": DAILY_LIMIT,
                "remaining": DAILY_LIMIT - self._daily_requests,
            },
            "cache": {
                "enabled": self.config.cache_enabled,
                "items": len(self._cache),
            },
        }

    async def search(
        self,
        term: str,
        limit: int = None,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Search for icons by term.

        Args:
            term: Search term
            limit: Maximum results
            offset: Result offset for pagination

        Returns:
            Search results with icon metadata
        """
        if not self.is_available():
            raise ProviderError("Provider not ready. Call authenticate() first.")

        limit = limit or self.config.max_results

        # Check cache
        cache_key = f"search:{term}:{limit}:{offset}"
        if self.config.cache_enabled and cache_key in self._cache:
            return self._cache[cache_key]

        response = await self._make_request(
            "GET",
            "/icon",
            params={"query": term, "limit": limit, "offset": offset},
        )

        icons = []
        for icon_data in response.get("icons", []):
            icons.append(
                {
                    "id": icon_data.get("id"),
                    "term": icon_data.get("term", term),
                    "preview_url": icon_data.get("thumbnail_url", ""),
                    "attribution": icon_data.get("attribution", ""),
                    "attribution_required": icon_data.get(
                        "license_description", ""
                    ).lower()
                    != "public domain",
                    "uploader": icon_data.get("uploader", {}).get("name", ""),
                }
            )

        result = {
            "term": term,
            "count": len(icons),
            "total": response.get("total", len(icons)),
            "icons": icons,
        }

        # Cache results
        if self.config.cache_enabled:
            self._cache[cache_key] = result

        return result

    async def get_icon(self, icon_id: int) -> Dict[str, Any]:
        """
        Get detailed information about an icon.

        Args:
            icon_id: Icon ID

        Returns:
            Icon metadata
        """
        if not self.is_available():
            raise ProviderError("Provider not ready. Call authenticate() first.")

        cache_key = f"icon:{icon_id}"
        if self.config.cache_enabled and cache_key in self._cache:
            return self._cache[cache_key]

        response = await self._make_request("GET", f"/icon/{icon_id}")

        result = {
            "id": response.get("id"),
            "term": response.get("term", ""),
            "preview_url": response.get("thumbnail_url", ""),
            "icon_url": response.get("icon_url", ""),
            "attribution": response.get("attribution", ""),
            "license": response.get("license_description", ""),
            "uploader": response.get("uploader", {}).get("name", ""),
            "collections": [c.get("name") for c in response.get("collections", [])],
            "tags": response.get("tags", []),
        }

        if self.config.cache_enabled:
            self._cache[cache_key] = result

        return result

    async def download(
        self,
        icon_id: int,
        format: str = None,
        size: int = None,
    ) -> Dict[str, Any]:
        """
        Download icon file.

        Args:
            icon_id: Icon ID
            format: 'svg' or 'png'
            size: PNG size (ignored for SVG)

        Returns:
            Icon data with file path or content
        """
        if not self.is_available():
            raise ProviderError("Provider not ready. Call authenticate() first.")

        format = format or self.config.default_format
        size = size or self.config.default_size

        # Get icon info first
        icon_info = await self.get_icon(icon_id)

        # Check cache for downloaded file
        cache_path = Path(self.config.cache_dir) / f"{icon_id}.{format}"
        if self.config.cache_enabled and cache_path.exists():
            return {
                "id": icon_id,
                "format": format,
                "path": str(cache_path),
                "cached": True,
                "attribution": icon_info.get("attribution", ""),
            }

        # Download the icon
        icon_url = icon_info.get("icon_url", "")
        if not icon_url:
            raise ProviderError(f"No download URL for icon {icon_id}")

        # The actual download would require fetching from icon_url
        # For now, return the URL info
        return {
            "id": icon_id,
            "format": format,
            "url": icon_url,
            "size": size if format == "png" else None,
            "cached": False,
            "attribution": icon_info.get("attribution", ""),
            "note": "Use URL to download icon file",
        }

    async def get_collection(self, slug: str) -> Dict[str, Any]:
        """
        Get icons from a collection.

        Args:
            slug: Collection slug/identifier

        Returns:
            Collection info with icons
        """
        if not self.is_available():
            raise ProviderError("Provider not ready. Call authenticate() first.")

        response = await self._make_request("GET", f"/collection/{slug}")

        icons = []
        for icon_data in response.get("icons", []):
            icons.append(
                {
                    "id": icon_data.get("id"),
                    "term": icon_data.get("term", ""),
                    "preview_url": icon_data.get("thumbnail_url", ""),
                }
            )

        return {
            "slug": slug,
            "name": response.get("name", slug),
            "description": response.get("description", ""),
            "icon_count": len(icons),
            "icons": icons,
        }

    async def list_collections(self, limit: int = 20) -> Dict[str, Any]:
        """
        List available icon collections.

        Args:
            limit: Maximum collections to return

        Returns:
            List of collections
        """
        if not self.is_available():
            raise ProviderError("Provider not ready. Call authenticate() first.")

        response = await self._make_request(
            "GET", "/collections", params={"limit": limit}
        )

        collections = []
        for coll in response.get("collections", []):
            collections.append(
                {
                    "slug": coll.get("slug", ""),
                    "name": coll.get("name", ""),
                    "icon_count": coll.get("icon_count", 0),
                }
            )

        return {
            "count": len(collections),
            "collections": collections,
        }

    async def get_recent_downloads(self) -> Dict[str, Any]:
        """
        Get recently downloaded icons from cache.

        Returns:
            List of recent downloads
        """
        cache_path = Path(self.config.cache_dir)
        if not cache_path.exists():
            return {"count": 0, "icons": []}

        # List cached files by modification time
        files = sorted(
            cache_path.glob("*.*"),
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )[:20]

        icons = []
        for f in files:
            icon_id = f.stem
            icons.append(
                {
                    "id": icon_id,
                    "format": f.suffix[1:],
                    "path": str(f),
                    "size": f.stat().st_size,
                }
            )

        return {"count": len(icons), "icons": icons}

    async def get_ascii(self, icon_id: int, width: int = 40) -> Dict[str, Any]:
        """
        Convert icon to ASCII art for TUI display.

        Args:
            icon_id: Icon ID
            width: Output width in characters

        Returns:
            ASCII art representation
        """
        # This would integrate with image_teletext converter
        # For now, return placeholder
        icon_info = await self.get_icon(icon_id)

        return {
            "id": icon_id,
            "term": icon_info.get("term", ""),
            "width": width,
            "ascii": f"[ASCII art for icon {icon_id} - requires image_teletext converter]",
            "note": "Use image_teletext.py to convert downloaded icon to ASCII",
        }

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Make OAuth 1.0a signed request to Noun Project API."""
        import aiohttp
        from urllib.parse import urlencode

        # Check rate limits
        self._check_daily_limit()

        if not self._check_rate_limit():
            raise RateLimitError("Rate limit exceeded. Please wait.")

        url = f"{self.API_BASE}{endpoint}"
        if params:
            url += "?" + urlencode(params)

        # OAuth 1.0a signature
        timestamp = str(int(time.time()))
        nonce = hashlib.md5(f"{timestamp}{self.config.api_key}".encode()).hexdigest()

        oauth_params = {
            "oauth_consumer_key": self.config.api_key,
            "oauth_nonce": nonce,
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": timestamp,
            "oauth_version": "1.0",
        }

        # Create signature base string
        all_params = {**(params or {}), **oauth_params}
        sorted_params = "&".join(f"{k}={v}" for k, v in sorted(all_params.items()))
        base_string = f"{method}&{self._percent_encode(url.split('?')[0])}&{self._percent_encode(sorted_params)}"

        # Sign with HMAC-SHA1
        import hmac
        import base64

        signing_key = f"{self._percent_encode(self.config.api_secret)}&"
        signature = base64.b64encode(
            hmac.new(
                signing_key.encode(),
                base_string.encode(),
                hashlib.sha1,
            ).digest()
        ).decode()

        oauth_params["oauth_signature"] = signature

        # Build Authorization header
        auth_header = "OAuth " + ", ".join(
            f'{k}="{self._percent_encode(str(v))}"' for k, v in oauth_params.items()
        )

        headers = {"Authorization": auth_header}

        self._request_count += 1
        self._daily_requests += 1
        self._last_request_time = time.time()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds),
                ) as response:
                    if response.status == 401:
                        raise AuthenticationError("Invalid API credentials")
                    elif response.status == 429:
                        raise RateLimitError("API rate limit exceeded")
                    elif response.status == 404:
                        raise ProviderError("Resource not found")
                    elif response.status != 200:
                        text = await response.text()
                        raise ProviderError(f"API error {response.status}: {text}")

                    return await response.json()

        except aiohttp.ClientError as e:
            raise ProviderError(f"Network error: {str(e)}")

    def _percent_encode(self, s: str) -> str:
        """RFC 3986 percent encoding."""
        from urllib.parse import quote

        return quote(str(s), safe="")

    def _check_daily_limit(self):
        """Check and reset daily limit if needed."""
        current_time = time.time()

        # Reset daily counter after 24 hours
        if current_time - self._last_reset > 86400:
            self._daily_requests = 0
            self._last_reset = current_time

        if self._daily_requests >= DAILY_LIMIT:
            raise RateLimitError(
                f"Daily limit of {DAILY_LIMIT} requests exceeded. Resets in "
                f"{int(86400 - (current_time - self._last_reset))} seconds."
            )


# Convenience function
def get_nounproject_client(
    api_key: str = None,
    api_secret: str = None,
) -> NounProjectClient:
    """
    Get a configured Noun Project client.

    Args:
        api_key: Optional API key (uses env var if not provided)
        api_secret: Optional API secret (uses env var if not provided)

    Returns:
        NounProjectClient instance
    """
    config = NounProjectConfig(
        name="nounproject",
        api_key=api_key,
        api_secret=api_secret,
    )
    return NounProjectClient(config)


__all__ = [
    "NounProjectClient",
    "NounProjectConfig",
    "IconResult",
    "get_nounproject_client",
]
