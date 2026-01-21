"""
RSS Feed generation for Binder markdown content.

Generates RSS 2.0 and JSON Feed formats from markdown files
in a binder, extracting frontmatter metadata and previews.

Module: core.binder.feed
Version: 1.0.0 (v1.0.6.0)
"""

from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from enum import Enum
import re
import json
from xml.etree.ElementTree import Element, SubElement, tostring


class FeedFormat(Enum):
    """Feed format options."""

    RSS_2_0 = "rss_2_0"
    JSON_FEED = "json_feed"


@dataclass
class FrontmatterData:
    """Extracted frontmatter from markdown file."""

    title: str
    date: Optional[datetime] = None
    author: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    description: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary, handling datetime serialization."""
        data = asdict(self)
        if self.date:
            data["date"] = self.date.isoformat()
        return data


@dataclass
class FeedItem:
    """RSS feed item representing a markdown file."""

    title: str
    url: str
    content_preview: str
    date: datetime
    author: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    guid: Optional[str] = None

    def __post_init__(self):
        """Generate GUID from URL if not provided."""
        if not self.guid:
            self.guid = f"binder-{hash(self.url) % (2**31)}"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        if self.date:
            data["date"] = self.date.isoformat()
        return data


class FrontmatterExtractor:
    """Extract frontmatter metadata from markdown files."""

    # Regex pattern for frontmatter block
    FRONTMATTER_PATTERN = re.compile(
        r"^---\s*\n(.*?)\n---\s*\n", re.MULTILINE | re.DOTALL
    )

    @staticmethod
    def extract(md_path: Path) -> tuple[FrontmatterData, str]:
        """
        Extract frontmatter and content from markdown file.

        Args:
            md_path: Path to markdown file

        Returns:
            Tuple of (FrontmatterData, remaining_content)

        Raises:
            ValueError: If file not readable or invalid frontmatter
        """
        try:
            content = md_path.read_text(encoding="utf-8")
        except Exception as e:
            raise ValueError(f"Cannot read {md_path}: {e}")

        # Extract frontmatter block
        match = FrontmatterExtractor.FRONTMATTER_PATTERN.match(content)

        if not match:
            # No frontmatter, use defaults
            return (
                FrontmatterData(
                    title=md_path.stem.replace("-", " ").title(),
                ),
                content,
            )

        frontmatter_text = match.group(1)
        remaining_content = content[match.end() :]

        # Parse YAML-style frontmatter
        metadata = FrontmatterExtractor._parse_yaml(frontmatter_text)

        # Extract fields
        title = metadata.get("title", md_path.stem.replace("-", " ").title())
        date = FrontmatterExtractor._parse_date(metadata.get("date"))
        author = metadata.get("author")
        tags = metadata.get("tags", [])
        description = metadata.get("description")

        # Ensure tags is a list
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",")]
        elif not isinstance(tags, list):
            tags = []

        return (
            FrontmatterData(
                title=title,
                date=date,
                author=author,
                tags=tags,
                description=description,
            ),
            remaining_content,
        )

    @staticmethod
    def _parse_yaml(yaml_text: str) -> Dict[str, any]:
        """
        Parse simple YAML-style frontmatter.

        Supports: key: value, key: [item1, item2], key: value with spaces
        """
        data = {}

        for line in yaml_text.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if ":" not in line:
                continue

            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()

            # Parse array format [item1, item2]
            if value.startswith("[") and value.endswith("]"):
                items = value[1:-1].split(",")
                value = [item.strip().strip("'\"") for item in items]
            # Remove quotes
            elif value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]

            data[key] = value

        return data

    @staticmethod
    def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
        """Parse ISO date string to datetime."""
        if not date_str:
            return None

        date_str = date_str.strip()

        # Try ISO format first
        formats = [
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return None


class ContentPreview:
    """Extract text preview from markdown content."""

    @staticmethod
    def generate(content: str, max_length: int = 200) -> str:
        """
        Generate plain text preview from markdown content.

        Removes markdown syntax and extracts first N characters.

        Args:
            content: Markdown content
            max_length: Maximum preview length (default 200)

        Returns:
            Plain text preview
        """
        # Remove markdown syntax
        text = ContentPreview._strip_markdown(content)

        # Trim to max length
        if len(text) > max_length:
            text = text[:max_length].rsplit(" ", 1)[0] + "..."

        return text.strip()

    @staticmethod
    def _strip_markdown(text: str) -> str:
        """Remove markdown formatting from text."""
        # Remove code blocks (must be before inline code)
        text = re.sub(r"```[\s\S]*?```", "", text)

        # Remove links [text](url) -> text
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)

        # Remove bold/italic (must preserve content)
        # **text** or __text__ -> text
        text = re.sub(r"\*\*([^\*]+)\*\*", r"\1", text)
        text = re.sub(r"__([^_]+)__", r"\1", text)
        # *text* or _text_ -> text (but be careful not to match single char)
        text = re.sub(r"\*([^\*]+)\*", r"\1", text)
        text = re.sub(r"_([^_]+)_", r"\1", text)

        # Remove inline code `text` -> text
        text = re.sub(r"`([^`]+)`", r"\1", text)

        # Remove headers # text -> text (but preserve the text content)
        text = re.sub(r"^#+\s+", "", text, flags=re.MULTILINE)

        # Remove lists
        text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
        text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)

        # Remove HTML
        text = re.sub(r"<[^>]+>", "", text)

        # Clean whitespace
        text = re.sub(r"\s+", " ", text)

        return text.strip()


class BinderFeed:
    """Generate RSS feeds from binder markdown files."""

    def __init__(self, binder_path: Path, base_url: str = ""):
        """
        Initialize feed generator.

        Args:
            binder_path: Path to binder folder
            base_url: Base URL for feed items (optional, for absolute URLs)
        """
        self.binder_path = Path(binder_path)
        self.base_url = base_url

        if not self.binder_path.is_dir():
            raise ValueError(f"Binder path not found: {binder_path}")

    def scan_files(self, pattern: str = "*.md") -> List[FeedItem]:
        """
        Scan binder for markdown files and extract feed items.

        Args:
            pattern: Glob pattern for files (default "*.md")

        Returns:
            List of FeedItem objects, sorted by date (newest first)
        """
        items = []

        # Search in all subdirectories
        for md_file in self.binder_path.rglob(pattern):
            # Skip hidden files and system files
            if md_file.name.startswith("."):
                continue

            try:
                frontmatter, content = FrontmatterExtractor.extract(md_file)

                # Generate preview
                preview = ContentPreview.generate(content)

                # Calculate relative URL
                rel_path = md_file.relative_to(self.binder_path)
                if self.base_url:
                    url = f"{self.base_url}/{rel_path.as_posix()}"
                else:
                    url = rel_path.as_posix()

                # Create feed item
                item = FeedItem(
                    title=frontmatter.title,
                    url=url,
                    content_preview=preview,
                    date=frontmatter.date or datetime.now(),
                    author=frontmatter.author,
                    tags=frontmatter.tags,
                )

                items.append(item)

            except Exception as e:
                # Skip files with errors
                continue

        # Sort by date, newest first
        items.sort(key=lambda x: x.date, reverse=True)

        return items

    def generate_rss(self, items: Optional[List[FeedItem]] = None) -> str:
        """
        Generate RSS 2.0 XML feed.

        Args:
            items: List of FeedItem objects (scans if not provided)

        Returns:
            RSS 2.0 XML string
        """
        if items is None:
            items = self.scan_files()

        # Create root elements
        rss = Element("rss", attrib={"version": "2.0"})
        channel = SubElement(rss, "channel")

        # Channel metadata
        SubElement(channel, "title").text = f"Binder: {self.binder_path.name}"
        SubElement(channel, "link").text = self.base_url or "."
        SubElement(channel, "description").text = (
            f"Feed from binder {self.binder_path.name}"
        )
        SubElement(channel, "language").text = "en-us"

        # Update time
        if items:
            SubElement(channel, "lastBuildDate").text = self._format_rss_date(
                items[0].date
            )

        # Add items
        for item in items:
            item_elem = SubElement(channel, "item")

            SubElement(item_elem, "title").text = item.title
            SubElement(item_elem, "link").text = item.url
            SubElement(item_elem, "guid").text = item.guid
            SubElement(item_elem, "description").text = item.content_preview
            SubElement(item_elem, "pubDate").text = self._format_rss_date(item.date)

            if item.author:
                SubElement(item_elem, "author").text = item.author

            if item.tags:
                for tag in item.tags:
                    SubElement(item_elem, "category").text = tag

        # Convert to string
        xml_bytes = tostring(rss, encoding="utf-8")
        return xml_bytes.decode("utf-8")

    def generate_json(self, items: Optional[List[FeedItem]] = None) -> Dict:
        """
        Generate JSON Feed v1.1 format.

        Args:
            items: List of FeedItem objects (scans if not provided)

        Returns:
            JSON Feed dictionary
        """
        if items is None:
            items = self.scan_files()

        feed = {
            "version": "https://jsonfeed.org/version/1.1",
            "title": f"Binder: {self.binder_path.name}",
            "home_page_url": self.base_url or ".",
            "feed_url": f"{self.base_url}/feed.json" if self.base_url else "feed.json",
            "description": f"Feed from binder {self.binder_path.name}",
            "items": [],
        }

        for item in items:
            feed_item = {
                "id": item.guid,
                "title": item.title,
                "url": item.url,
                "summary": item.content_preview,
                "date_published": item.date.isoformat(),
            }

            if item.author:
                feed_item["author"] = {"name": item.author}

            if item.tags:
                feed_item["tags"] = item.tags

            feed["items"].append(feed_item)

        return feed

    def save_feed(
        self, format: FeedFormat = FeedFormat.RSS_2_0, filename: Optional[str] = None
    ) -> Path:
        """
        Generate and save feed to binder folder.

        Args:
            format: Feed format (RSS_2_0 or JSON_FEED)
            filename: Output filename (optional, uses default)

        Returns:
            Path to saved feed file
        """
        items = self.scan_files()

        if format == FeedFormat.RSS_2_0:
            content = self.generate_rss(items)
            if not filename:
                filename = "feed.xml"
        else:  # JSON_FEED
            content_dict = self.generate_json(items)
            content = json.dumps(content_dict, indent=2, ensure_ascii=False)
            if not filename:
                filename = "feed.json"

        # Save to binder folder
        feed_path = self.binder_path / filename

        try:
            if format == FeedFormat.RSS_2_0:
                feed_path.write_text(content, encoding="utf-8")
            else:
                feed_path.write_text(content, encoding="utf-8")
        except Exception as e:
            raise ValueError(f"Cannot write feed to {feed_path}: {e}")

        return feed_path

    @staticmethod
    def _format_rss_date(dt: datetime) -> str:
        """Format datetime for RSS 2.0 (RFC 822)."""
        # RSS date format: Mon, 17 Jan 2026 12:30:00 +0000
        return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")
