"""
URL to Markdown Service
=======================

Converts web pages to Markdown format using the url-to-markdown library.
Part of Wizard Server's web capabilities (Wizard-only, requires internet access).

Example:
    service = URLToMarkdownService()
    output_path = await service.convert("https://example.com", "example")
"""

import asyncio
import subprocess
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime
from wizard.services.logging_manager import get_logging_manager
from wizard.services.path_utils import get_repo_root


class URLToMarkdownService:
    """Convert URLs to Markdown format."""

    def __init__(self):
        self.logger = get_logging_manager().get_logger("url-to-markdown")
        self.repo_root = get_repo_root()
        self.library_path = self.repo_root / "library" / "url-to-markdown"
        self.outbox_path = self.repo_root / "memory" / "sandbox" / "outbox"
        self.outbox_path.mkdir(parents=True, exist_ok=True)

    def _get_safe_filename(self, url: str) -> str:
        """Extract a safe filename from URL."""
        # Remove protocol
        if "://" in url:
            url = url.split("://", 1)[1]
        
        # Remove trailing slash
        url = url.rstrip("/")
        
        # Use domain name or first part
        parts = url.split("/")[0].split(".")
        
        # Try to use meaningful domain part
        if len(parts) >= 2:
            # Use second-to-last part (e.g., "github" from "github.com")
            filename = parts[-2]
        else:
            # Fallback to full domain
            filename = url.split("/")[0].replace(".", "-")
        
        # Clean up invalid characters
        filename = "".join(c if c.isalnum() or c in "-_" else "" for c in filename)
        
        return filename or "webpage"

    async def convert_with_python(self, url: str, filename: Optional[str] = None) -> Tuple[bool, Path, str]:
        """
        Convert URL to Markdown using Python approach (requests + beautifulsoup4 + html2text).
        
        Args:
            url: The URL to convert
            filename: Optional filename without extension
            
        Returns:
            (success, output_path, message)
        """
        try:
            # Try to import required libraries
            import requests
            import html2text
            from bs4 import BeautifulSoup
        except ImportError as e:
            error_msg = f"Missing dependency: {e}. Install: pip install requests beautifulsoup4 html2text"
            self.logger.warning(f"[WIZ] {error_msg}")
            return False, None, error_msg

        try:
            self.logger.info(f"[WIZ] Converting URL to Markdown: {url}")
            
            # Fetch the page
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Convert to Markdown
            converter = html2text.HTML2Text()
            converter.ignore_links = False
            converter.ignore_images = False
            converter.body_width = 0  # Don't wrap lines
            
            markdown_content = converter.handle(str(soup))
            
            # Generate filename
            if not filename:
                filename = self._get_safe_filename(url)
            
            output_path = self.outbox_path / f"{filename}.md"
            
            # Add metadata header
            timestamp = datetime.now().isoformat()
            metadata = f"""---
title: {filename}
source_url: {url}
converted_at: {timestamp}
format: url-to-markdown
---

"""
            
            # Write file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(metadata)
                f.write(markdown_content)
            
            success_msg = f"✅ Converted and saved to {output_path.relative_to(self.repo_root)}"
            self.logger.info(f"[WIZ] {success_msg}")
            
            return True, output_path, success_msg
            
        except requests.RequestException as e:
            error_msg = f"Failed to fetch URL: {e}"
            self.logger.error(f"[WIZ] {error_msg}")
            return False, None, error_msg
        except Exception as e:
            error_msg = f"Conversion error: {e}"
            self.logger.error(f"[WIZ] {error_msg}")
            return False, None, error_msg

    async def convert_with_npm(self, url: str, filename: Optional[str] = None) -> Tuple[bool, Path, str]:
        """
        Convert URL to Markdown using the npm url-to-markdown package.
        Requires: npm install -g url-to-markdown
        
        Args:
            url: The URL to convert
            filename: Optional filename without extension
            
        Returns:
            (success, output_path, message)
        """
        try:
            # Check if npm package is available
            result = subprocess.run(
                ["which", "url-to-markdown"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                # Try using npx
                self.logger.info("[WIZ] url-to-markdown not in PATH, trying npx")
                command = ["npx", "url-to-markdown"]
            else:
                command = ["url-to-markdown"]
            
            # Generate filename
            if not filename:
                filename = self._get_safe_filename(url)
            
            output_path = self.outbox_path / f"{filename}.md"
            
            self.logger.info(f"[WIZ] Converting URL with npm: {url}")
            
            # Run conversion
            result = subprocess.run(
                command + [url],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                error_msg = f"npm conversion failed: {result.stderr}"
                self.logger.error(f"[WIZ] {error_msg}")
                return False, None, error_msg
            
            # Write markdown content
            markdown_content = result.stdout
            
            # Add metadata header
            timestamp = datetime.now().isoformat()
            metadata = f"""---
title: {filename}
source_url: {url}
converted_at: {timestamp}
format: url-to-markdown (npm)
---

"""
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(metadata)
                f.write(markdown_content)
            
            success_msg = f"✅ Converted and saved to {output_path.relative_to(self.repo_root)}"
            self.logger.info(f"[WIZ] {success_msg}")
            
            return True, output_path, success_msg
            
        except subprocess.TimeoutExpired:
            error_msg = "Conversion timeout (>30s)"
            self.logger.error(f"[WIZ] {error_msg}")
            return False, None, error_msg
        except Exception as e:
            error_msg = f"npm conversion error: {e}"
            self.logger.error(f"[WIZ] {error_msg}")
            return False, None, error_msg

    async def convert(self, url: str, filename: Optional[str] = None) -> Tuple[bool, Optional[Path], str]:
        """
        Convert URL to Markdown using available method.
        Tries Python approach first (requests/beautifulsoup/html2text),
        then falls back to npm package if available.
        
        Args:
            url: The URL to convert
            filename: Optional filename without extension
            
        Returns:
            (success, output_path, message)
        """
        # Validate URL
        url = url.strip()
        if not url.startswith(("http://", "https://")):
            return False, None, "URL must start with http:// or https://"
        
        # Try Python approach first (more reliable, offline-capable after install)
        success, output_path, message = await self.convert_with_python(url, filename)
        
        if success:
            return success, output_path, message
        
        # Fall back to npm if Python approach failed
        self.logger.info("[WIZ] Falling back to npm approach")
        return await self.convert_with_npm(url, filename)


# Singleton instance
_service: Optional[URLToMarkdownService] = None


def get_url_to_markdown_service() -> URLToMarkdownService:
    """Get or create URL to Markdown service instance."""
    global _service
    if _service is None:
        _service = URLToMarkdownService()
    return _service
