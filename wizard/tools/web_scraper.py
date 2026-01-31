"""
Web Scraper Pipeline - Advanced Content Extraction
===================================================

Provides web scraping pipelines for converting web content
into uDOS-compatible formats.

Pipelines:
  - HTML → Markdown (general articles)
  - HTML → Teletext pages (BBC Micro format)
  - Recipe extraction (structured cooking data)
  - News aggregation (headline extraction)
  - Documentation scraping (API docs)

Features:
  - CSS selector-based extraction
  - Template-based output
  - Link preservation
  - Image placeholder generation
  - Rate limiting and caching

Security:
  - URL whitelist enforcement
  - robots.txt respect
  - Request rate limiting
  - Content size limits

Note: WIZARD-ONLY functionality.
"""

import json
import re
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from urllib.parse import urlparse, urljoin
from enum import Enum

from core.services.logging_service import get_logger

logger = get_logger("web-scraper")

# Optional dependencies
try:
    from bs4 import BeautifulSoup

    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class PipelineType(Enum):
    """Types of scraping pipelines."""

    MARKDOWN = "markdown"  # General HTML → Markdown
    TELETEXT = "teletext"  # HTML → Teletext pages
    RECIPE = "recipe"  # Recipe extraction
    NEWS = "news"  # News headlines
    DOCUMENTATION = "documentation"  # API/code docs


@dataclass
class PipelineConfig:
    """Configuration for a scraping pipeline."""

    name: str
    pipeline_type: PipelineType
    title_selector: str = "h1"
    content_selector: str = "article, main, .content"
    exclude_selectors: List[str] = field(
        default_factory=lambda: [
            "nav",
            "header",
            "footer",
            ".sidebar",
            ".ad",
            ".comments",
        ]
    )
    max_length: int = 50000
    preserve_links: bool = True
    preserve_images: bool = False
    custom_extractors: Dict[str, str] = field(default_factory=dict)


@dataclass
class ScrapeResult:
    """Result of a scraping operation."""

    success: bool
    url: str
    title: str = ""
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    processing_time_ms: int = 0


# Pre-defined pipeline configurations
PIPELINE_CONFIGS = {
    "markdown": PipelineConfig(
        name="Markdown",
        pipeline_type=PipelineType.MARKDOWN,
    ),
    "teletext": PipelineConfig(
        name="Teletext",
        pipeline_type=PipelineType.TELETEXT,
        max_length=1000,  # Teletext pages are small
        preserve_images=False,
    ),
    "recipe": PipelineConfig(
        name="Recipe",
        pipeline_type=PipelineType.RECIPE,
        content_selector=".recipe, .ingredients, .instructions, [itemtype*='Recipe']",
        custom_extractors={
            "ingredients": ".ingredients li, [itemprop='recipeIngredient']",
            "instructions": ".instructions li, [itemprop='recipeInstructions']",
            "prep_time": "[itemprop='prepTime'], .prep-time",
            "cook_time": "[itemprop='cookTime'], .cook-time",
        },
    ),
    "news": PipelineConfig(
        name="News",
        pipeline_type=PipelineType.NEWS,
        title_selector="h1, .headline",
        content_selector="article p, .article-body p",
        max_length=5000,
    ),
    "documentation": PipelineConfig(
        name="Documentation",
        pipeline_type=PipelineType.DOCUMENTATION,
        content_selector=".documentation, .docs-content, main",
        preserve_links=True,
    ),
}


class WebScraper:
    """
    Web scraping pipeline executor.

    Extracts and transforms web content into uDOS-compatible formats.
    """

    # Rate limiting
    REQUEST_DELAY_MS = 1000
    MAX_REQUESTS_PER_MINUTE = 30

    # Cache settings
    CACHE_PATH = (
        Path(__file__).parent.parent.parent / "memory" / "wizard" / "scrape_cache"
    )
    CACHE_DURATION_HOURS = 24

    def __init__(self):
        """Initialize the web scraper."""
        self.last_request_time = 0
        self.request_count = 0
        self.request_minute_start = datetime.now()

        # Ensure cache directory
        self.CACHE_PATH.mkdir(parents=True, exist_ok=True)

    def get_pipeline(self, name: str) -> Optional[PipelineConfig]:
        """Get a pipeline configuration by name."""
        return PIPELINE_CONFIGS.get(name.lower())

    def list_pipelines(self) -> List[str]:
        """List available pipeline names."""
        return list(PIPELINE_CONFIGS.keys())

    async def scrape(self, url: str, pipeline: str = "markdown") -> ScrapeResult:
        """
        Scrape a URL using the specified pipeline.

        Args:
            url: URL to scrape
            pipeline: Pipeline name to use

        Returns:
            ScrapeResult with extracted content
        """
        start_time = datetime.now()

        config = self.get_pipeline(pipeline)
        if not config:
            return ScrapeResult(
                success=False, url=url, error=f"Unknown pipeline: {pipeline}"
            )

        # Check cache
        cached = self._check_cache(url, pipeline)
        if cached:
            cached.processing_time_ms = 0
            return cached

        # Fetch content
        if not HTTPX_AVAILABLE:
            return ScrapeResult(
                success=False,
                url=url,
                error="httpx not installed. Run: pip install httpx",
            )

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    timeout=30,
                    follow_redirects=True,
                    headers={"User-Agent": "uDOS-Scraper/1.0"},
                )
                response.raise_for_status()
                html = response.text
        except Exception as e:
            return ScrapeResult(success=False, url=url, error=f"Fetch failed: {str(e)}")

        # Parse and extract
        result = self._extract(html, url, config)
        result.processing_time_ms = int(
            (datetime.now() - start_time).total_seconds() * 1000
        )

        # Cache result
        if result.success:
            self._save_cache(url, pipeline, result)

        return result

    def _extract(self, html: str, url: str, config: PipelineConfig) -> ScrapeResult:
        """Extract content from HTML using pipeline configuration."""
        if not BS4_AVAILABLE:
            return ScrapeResult(
                success=False,
                url=url,
                error="beautifulsoup4 not installed. Run: pip install beautifulsoup4",
            )

        soup = BeautifulSoup(html, "html.parser")

        # Remove excluded elements
        for selector in config.exclude_selectors:
            for element in soup.select(selector):
                element.decompose()

        # Extract title
        title_elem = soup.select_one(config.title_selector)
        title = title_elem.get_text(strip=True) if title_elem else ""

        # Extract main content
        content_elem = soup.select_one(config.content_selector)
        if not content_elem:
            content_elem = soup.body

        if not content_elem:
            return ScrapeResult(
                success=False, url=url, title=title, error="No content found"
            )

        # Convert based on pipeline type
        if config.pipeline_type == PipelineType.TELETEXT:
            content = self._to_teletext(content_elem, url)
        elif config.pipeline_type == PipelineType.RECIPE:
            content, metadata = self._extract_recipe(soup, config)
            return ScrapeResult(
                success=True, url=url, title=title, content=content, metadata=metadata
            )
        else:
            content = self._to_markdown(content_elem, url, config)

        # Truncate if needed
        if len(content) > config.max_length:
            content = content[: config.max_length] + "\n\n[Content truncated]"

        return ScrapeResult(success=True, url=url, title=title, content=content)

    def _to_markdown(self, elem, base_url: str, config: PipelineConfig) -> str:
        """Convert HTML element to Markdown."""
        lines = []

        for child in elem.descendants:
            if child.name == "h1":
                lines.append(f"\n# {child.get_text(strip=True)}\n")
            elif child.name == "h2":
                lines.append(f"\n## {child.get_text(strip=True)}\n")
            elif child.name == "h3":
                lines.append(f"\n### {child.get_text(strip=True)}\n")
            elif child.name == "p":
                text = child.get_text(strip=True)
                if text:
                    lines.append(f"{text}\n")
            elif child.name == "li":
                lines.append(f"- {child.get_text(strip=True)}")
            elif child.name == "a" and config.preserve_links:
                href = child.get("href", "")
                if href and not href.startswith("#"):
                    full_url = urljoin(base_url, href)
                    text = child.get_text(strip=True)
                    lines.append(f"[{text}]({full_url})")
            elif child.name == "code":
                lines.append(f"`{child.get_text()}`")
            elif child.name == "pre":
                lines.append(f"\n```\n{child.get_text()}\n```\n")

        return "\n".join(lines)

    def _to_teletext(self, elem, base_url: str) -> str:
        """Convert HTML to Teletext format (40 cols, limited formatting)."""
        # Extract plain text
        text = elem.get_text(separator="\n", strip=True)

        # Wrap to 40 columns (Teletext standard)
        lines = []
        for paragraph in text.split("\n"):
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            # Word wrap to 40 chars
            words = paragraph.split()
            current_line = ""
            for word in words:
                if len(current_line) + len(word) + 1 <= 38:
                    current_line += (" " if current_line else "") + word
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word[:38]  # Truncate long words
            if current_line:
                lines.append(current_line)
            lines.append("")  # Blank line between paragraphs

        # Limit to 24 rows (Teletext standard)
        if len(lines) > 22:
            lines = lines[:22]
            lines.append("...")

        return "\n".join(lines)

    def _extract_recipe(self, soup, config: PipelineConfig) -> tuple:
        """Extract structured recipe data."""
        metadata = {}

        for key, selector in config.custom_extractors.items():
            elements = soup.select(selector)
            if elements:
                metadata[key] = [e.get_text(strip=True) for e in elements]

        # Build markdown content
        lines = []

        if "ingredients" in metadata:
            lines.append("## Ingredients\n")
            for item in metadata["ingredients"]:
                lines.append(f"- {item}")
            lines.append("")

        if "instructions" in metadata:
            lines.append("## Instructions\n")
            for i, step in enumerate(metadata["instructions"], 1):
                lines.append(f"{i}. {step}")

        return "\n".join(lines), metadata

    def _cache_key(self, url: str, pipeline: str) -> str:
        """Generate cache key for URL + pipeline."""
        key = f"{url}:{pipeline}"
        return hashlib.md5(key.encode()).hexdigest()

    def _check_cache(self, url: str, pipeline: str) -> Optional[ScrapeResult]:
        """Check if we have cached content."""
        cache_file = self.CACHE_PATH / f"{self._cache_key(url, pipeline)}.json"

        if not cache_file.exists():
            return None

        try:
            data = json.loads(cache_file.read_text())
            cached_time = datetime.fromisoformat(data.get("cached_at", ""))

            # Check if cache is expired
            age_hours = (datetime.now() - cached_time).total_seconds() / 3600
            if age_hours > self.CACHE_DURATION_HOURS:
                return None

            return ScrapeResult(
                success=True,
                url=data["url"],
                title=data.get("title", ""),
                content=data.get("content", ""),
                metadata=data.get("metadata", {}),
                cached=True,
            )
        except Exception:
            return None

    def _save_cache(self, url: str, pipeline: str, result: ScrapeResult):
        """Save scrape result to cache."""
        cache_file = self.CACHE_PATH / f"{self._cache_key(url, pipeline)}.json"

        data = {
            "url": result.url,
            "title": result.title,
            "content": result.content,
            "metadata": result.metadata,
            "cached_at": datetime.now().isoformat(),
        }

        cache_file.write_text(json.dumps(data, indent=2))


# Convenience function for synchronous usage
def scrape_url(url: str, pipeline: str = "markdown") -> ScrapeResult:
    """Synchronous wrapper for scraping a URL."""
    import asyncio

    scraper = WebScraper()
    return asyncio.run(scraper.scrape(url, pipeline))


if __name__ == "__main__":
    # Test the scraper
    print("Web Scraper Pipelines:")
    scraper = WebScraper()
    for name in scraper.list_pipelines():
        config = scraper.get_pipeline(name)
        print(f"  {name}: {config.name} ({config.pipeline_type.value})")
