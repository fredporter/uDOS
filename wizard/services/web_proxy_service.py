"""Web proxy service wrapper for Wizard."""

from __future__ import annotations

from typing import Any, Dict, Optional

from wizard.tools.web_proxy import WebProxy, FetchOptions


class WebProxyService:
    """Expose web proxy fetch for API handlers."""

    def __init__(self, logger=None):
        self._proxy = WebProxy(logger=logger)

    def _build_options(self, options: Optional[Dict[str, Any]]) -> FetchOptions:
        options = options or {}
        return FetchOptions(
            timeout=int(options.get("timeout", FetchOptions.timeout)),
            max_size=int(options.get("max_size", FetchOptions.max_size)),
            format=str(options.get("format", FetchOptions.format)),
            include_images=bool(options.get("include_images", False)),
            follow_redirects=bool(options.get("follow_redirects", True)),
            user_agent=str(options.get("user_agent", FetchOptions.user_agent)),
        )

    async def fetch_url(self, url: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        from fastapi import HTTPException

        if not url or not isinstance(url, str):
            raise HTTPException(
                status_code=400, detail="URL required and must be a string"
            )

        url = url.strip()
        if len(url) > 2048:
            raise HTTPException(
                status_code=400, detail="URL too long (max 2048 chars)"
            )

        if not url.startswith(("http://", "https://")):
            raise HTTPException(
                status_code=400, detail="Only HTTP/HTTPS URLs allowed"
            )

        result = await self._proxy.fetch(url, self._build_options(options))
        payload = {
            "success": result.success,
            "url": result.url,
            "status_code": result.status_code,
            "content_type": result.content_type,
            "content": result.content,
            "title": result.title,
            "error": result.error,
            "cached": result.cached,
            "fetch_time_ms": result.fetch_time_ms,
        }
        return payload
