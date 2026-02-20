"""Stdlib-only HTTP utilities for core boundary compliance.

Provides HTTP client functions using only Python stdlib (urllib).
Replaces external dependency on 'requests' library.

Policy: Core module must remain stdlib-only to ensure portability and minimal dependencies.
Wizard services can use requests; core services must use only urllib from stdlib.
"""

from __future__ import annotations

import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from pathlib import Path

from core.services.logging_api import get_logger

logger = get_logger("core-stdlib-http")


class HTTPError(Exception):
    """HTTP request failed."""

    def __init__(self, code: int, message: str, response_text: str = ""):
        self.code = code
        self.message = message
        self.response_text = response_text
        super().__init__(f"HTTP {code}: {message}")


def http_get(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 5,
    verify_ssl: bool = True,
) -> Dict[str, Any]:
    """
    Perform HTTP GET request using stdlib urllib.

    Args:
        url: URL to request
        headers: Optional dict of HTTP headers
        timeout: Request timeout in seconds
        verify_ssl: Whether to verify SSL certificates (always True for stdlib)

    Returns:
        Dict with 'status_code', 'headers', 'text', 'json' (if JSON response)

    Raises:
        HTTPError: If request fails or returns error status code
    """
    try:
        req = urllib.request.Request(url, method="GET")
        if headers:
            for key, value in headers.items():
                req.add_header(key, value)

        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            result = {
                "status_code": response.status,
                "headers": dict(response.headers),
                "text": body,
            }

            # Try to parse as JSON
            try:
                result["json"] = json.loads(body)
            except json.JSONDecodeError:
                pass

            return result

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        logger.warning(f"HTTP GET {url} returned {e.code}: {body[:200]}")
        raise HTTPError(e.code, f"HTTP {e.code}", body)
    except urllib.error.URLError as e:
        logger.error(f"HTTP GET {url} failed: {e.reason}")
        raise HTTPError(0, str(e.reason))
    except Exception as e:
        logger.error(f"HTTP GET {url} error: {e}")
        raise HTTPError(0, str(e))


def http_post(
    url: str,
    data: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 5,
    verify_ssl: bool = True,
) -> Dict[str, Any]:
    """
    Perform HTTP POST request using stdlib urllib.

    Args:
        url: URL to request
        data: Optional form-encoded data dict
        json_data: Optional JSON data dict (takes precedence over data)
        headers: Optional dict of HTTP headers
        timeout: Request timeout in seconds
        verify_ssl: Whether to verify SSL certificates (always True for stdlib)

    Returns:
        Dict with 'status_code', 'headers', 'text', 'json' (if JSON response)

    Raises:
        HTTPError: If request fails or returns error status code
    """
    try:
        if headers is None:
            headers = {}

        # Prepare request body
        body_bytes = None
        if json_data is not None:
            body_bytes = json.dumps(json_data).encode("utf-8")
            headers["Content-Type"] = "application/json"
        elif data is not None:
            from urllib.parse import urlencode

            body_bytes = urlencode(data).encode("utf-8")
            headers["Content-Type"] = "application/x-www-form-urlencoded"

        req = urllib.request.Request(url, data=body_bytes, method="POST")
        for key, value in headers.items():
            req.add_header(key, value)

        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            result = {
                "status_code": response.status,
                "headers": dict(response.headers),
                "text": body,
            }

            # Try to parse as JSON
            try:
                result["json"] = json.loads(body)
            except json.JSONDecodeError:
                pass

            return result

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        logger.warning(f"HTTP POST {url} returned {e.code}: {body[:200]}")
        raise HTTPError(e.code, f"HTTP {e.code}", body)
    except urllib.error.URLError as e:
        logger.error(f"HTTP POST {url} failed: {e.reason}")
        raise HTTPError(0, str(e.reason))
    except Exception as e:
        logger.error(f"HTTP POST {url} error: {e}")
        raise HTTPError(0, str(e))


def http_put(
    url: str,
    data: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 5,
) -> Dict[str, Any]:
    """Perform HTTP PUT request using stdlib urllib."""
    try:
        if headers is None:
            headers = {}

        body_bytes = None
        if json_data is not None:
            body_bytes = json.dumps(json_data).encode("utf-8")
            headers["Content-Type"] = "application/json"
        elif data is not None:
            from urllib.parse import urlencode

            body_bytes = urlencode(data).encode("utf-8")
            headers["Content-Type"] = "application/x-www-form-urlencoded"

        req = urllib.request.Request(url, data=body_bytes, method="PUT")
        for key, value in headers.items():
            req.add_header(key, value)

        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            result = {
                "status_code": response.status,
                "headers": dict(response.headers),
                "text": body,
            }

            try:
                result["json"] = json.loads(body)
            except json.JSONDecodeError:
                pass

            return result

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        logger.warning(f"HTTP PUT {url} returned {e.code}: {body[:200]}")
        raise HTTPError(e.code, f"HTTP {e.code}", body)
    except urllib.error.URLError as e:
        logger.error(f"HTTP PUT {url} failed: {e.reason}")
        raise HTTPError(0, str(e.reason))
    except Exception as e:
        logger.error(f"HTTP PUT {url} error: {e}")
        raise HTTPError(0, str(e))


def http_delete(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 5,
) -> Dict[str, Any]:
    """Perform HTTP DELETE request using stdlib urllib."""
    try:
        req = urllib.request.Request(url, method="DELETE")
        if headers:
            for key, value in headers.items():
                req.add_header(key, value)

        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            result = {
                "status_code": response.status,
                "headers": dict(response.headers),
                "text": body,
            }

            try:
                result["json"] = json.loads(body)
            except json.JSONDecodeError:
                pass

            return result

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        logger.warning(f"HTTP DELETE {url} returned {e.code}: {body[:200]}")
        raise HTTPError(e.code, f"HTTP {e.code}", body)
    except urllib.error.URLError as e:
        logger.error(f"HTTP DELETE {url} failed: {e.reason}")
        raise HTTPError(0, str(e.reason))
    except Exception as e:
        logger.error(f"HTTP DELETE {url} error: {e}")
        raise HTTPError(0, str(e))
