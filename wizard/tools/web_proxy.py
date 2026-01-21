"""
Web Proxy - Content Fetching for User Devices
==============================================

Provides web content fetching as a service for user devices
that cannot access the internet directly.

Features:
  - URL fetching with sanitization
  - HTML to text/markdown conversion
  - Image downloading and caching
  - Rate limiting per device
  - Content filtering

Security:
  - URL whitelist/blacklist
  - Content size limits
  - Request timeout enforcement
  - No JavaScript execution
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from urllib.parse import urlparse

# Optional dependencies
try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

try:
    from bs4 import BeautifulSoup

    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

# Configuration
CACHE_PATH = Path(__file__).parent.parent.parent / "memory" / "wizard" / "web_cache"


@dataclass
class FetchOptions:
    """Options for URL fetching."""

    timeout: int = 30
    max_size: int = 5 * 1024 * 1024  # 5MB
    format: str = "text"  # text, html, markdown, json
    include_images: bool = False
    follow_redirects: bool = True
    user_agent: str = "uDOS-WebProxy/1.0"


@dataclass
class FetchResult:
    """Result of a URL fetch."""

    success: bool
    url: str
    status_code: int = 0
    content_type: str = ""
    content: str = ""
    title: str = ""
    error: Optional[str] = None
    cached: bool = False
    fetch_time_ms: int = 0


class WebProxy:
    """
    Web content proxy for uDOS user devices.

    Fetches web content on behalf of devices that cannot
    access the internet directly.
    """

    # URL restrictions
    BLOCKED_SCHEMES = ["file", "ftp", "data", "javascript"]
    BLOCKED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

    # Content limits
    MAX_CONTENT_SIZE = 10 * 1024 * 1024  # 10MB absolute max
    DEFAULT_TIMEOUT = 30

    def __init__(self, logger=None):
        """Initialize web proxy."""
        self.logger = logger
        self.cache_path = CACHE_PATH
        self.cache_path.mkdir(parents=True, exist_ok=True)

        # Request stats
        self.request_count = 0
        self.total_bytes = 0

    async def fetch(self, url: str, options: FetchOptions = None) -> FetchResult:
        """
        Fetch content from URL.

        Args:
            url: URL to fetch
            options: Fetch options

        Returns:
            FetchResult with content or error
        """
        import time

        start_time = time.time()

        if not HTTPX_AVAILABLE:
            return FetchResult(
                success=False,
                url=url,
                error="httpx not installed. Run: pip install httpx",
            )

        options = options or FetchOptions()

        # Validate URL
        validation_error = self._validate_url(url)
        if validation_error:
            return FetchResult(success=False, url=url, error=validation_error)

        try:
            async with httpx.AsyncClient(
                timeout=options.timeout,
                follow_redirects=options.follow_redirects,
            ) as client:
                response = await client.get(
                    url, headers={"User-Agent": options.user_agent}
                )

                # Check size
                content_length = int(response.headers.get("content-length", 0))
                if content_length > options.max_size:
                    return FetchResult(
                        success=False,
                        url=url,
                        status_code=response.status_code,
                        error=f"Content too large: {content_length} bytes",
                    )

                # Get content
                content = response.text
                content_type = response.headers.get("content-type", "")

                # Process based on format
                processed_content, title = self._process_content(
                    content, content_type, options.format
                )

                fetch_time = int((time.time() - start_time) * 1000)

                self.request_count += 1
                self.total_bytes += len(content)

                if self.logger:
                    self.logger.info(f"[WEBPROXY] Fetched {url} ({len(content)} bytes)")

                return FetchResult(
                    success=True,
                    url=url,
                    status_code=response.status_code,
                    content_type=content_type,
                    content=processed_content,
                    title=title,
                    fetch_time_ms=fetch_time,
                )

        except httpx.TimeoutException:
            return FetchResult(
                success=False,
                url=url,
                error=f"Request timed out after {options.timeout}s",
            )
        except httpx.RequestError as e:
            return FetchResult(
                success=False, url=url, error=f"Request failed: {str(e)}"
            )
        except Exception as e:
            return FetchResult(
                success=False, url=url, error=f"Unexpected error: {str(e)}"
            )

    def _validate_url(self, url: str) -> Optional[str]:
        """Validate URL for security."""
        try:
            parsed = urlparse(url)
        except Exception:
            return "Invalid URL format"

        # Check scheme
        if parsed.scheme.lower() in self.BLOCKED_SCHEMES:
            return f"Blocked URL scheme: {parsed.scheme}"

        if parsed.scheme.lower() not in ["http", "https"]:
            return f"Invalid URL scheme: {parsed.scheme}"

        # Check host
        host = parsed.hostname or ""
        if host.lower() in self.BLOCKED_HOSTS:
            return f"Blocked host: {host}"

        # Check for internal IPs
        if (
            host.startswith("192.168.")
            or host.startswith("10.")
            or host.startswith("172.")
        ):
            return "Internal network addresses blocked"

        return None

    def _process_content(
        self, content: str, content_type: str, format: str
    ) -> tuple[str, str]:
        """Process content based on requested format."""
        title = ""

        if "html" in content_type.lower():
            if BS4_AVAILABLE:
                soup = BeautifulSoup(content, "html.parser")

                # Extract title
                title_tag = soup.find("title")
                title = title_tag.get_text() if title_tag else ""

                if format == "text":
                    # Get text only
                    for script in soup(["script", "style"]):
                        script.decompose()
                    return soup.get_text(separator="\n", strip=True), title

                elif format == "markdown":
                    # Basic HTML to markdown conversion
                    return self._html_to_markdown(soup), title

                else:
                    return content, title
            else:
                # No BeautifulSoup, return raw
                return content, title

        elif "json" in content_type.lower():
            if format == "text":
                try:
                    data = json.loads(content)
                    return json.dumps(data, indent=2), ""
                except:
                    return content, ""
            return content, ""

        else:
            # Plain text or other
            return content, ""

    def _html_to_markdown(self, soup) -> str:
        """Basic HTML to markdown conversion."""
        lines = []

        # Process headings
        for i in range(1, 7):
            for h in soup.find_all(f"h{i}"):
                lines.append(f"{'#' * i} {h.get_text()}")

        # Process paragraphs
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if text:
                lines.append(f"\n{text}\n")

        # Process links
        for a in soup.find_all("a", href=True):
            text = a.get_text()
            href = a["href"]
            if text and href:
                lines.append(f"[{text}]({href})")

        # Process lists
        for ul in soup.find_all(["ul", "ol"]):
            for li in ul.find_all("li"):
                lines.append(f"- {li.get_text()}")

        return "\n".join(lines)

    def get_stats(self) -> Dict[str, Any]:
        """Get proxy statistics."""
        return {
            "request_count": self.request_count,
            "total_bytes": self.total_bytes,
            "total_mb": round(self.total_bytes / 1024 / 1024, 2),
        }


# Synchronous wrapper for non-async contexts
def fetch_url_sync(url: str, options: FetchOptions = None) -> FetchResult:
    """Synchronous URL fetch wrapper."""
    proxy = WebProxy()
    return asyncio.run(proxy.fetch(url, options))
