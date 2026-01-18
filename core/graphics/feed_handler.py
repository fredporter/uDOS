"""
Feed Handler

Handle RSS/JSON feeds for uDOS:
- Generate feeds from local content
- Parse incoming feeds from Wizard
- Compile/transform feed data
- Send feeds back to Wizard
"""

from typing import List, Dict, Optional
from datetime import datetime
import json


class FeedHandler:
    """Handle feed generation and consumption"""

    FEED_TYPES = ["rss", "json", "atom"]

    def __init__(self):
        self.feeds = []

    def generate_rss(
        self, items: List[Dict], title: str, description: str, link: str
    ) -> str:
        """Generate RSS 2.0 feed from items

        Items should have: title, description, link, pubDate
        """
        now = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

        rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{self._escape_xml(title)}</title>
    <description>{self._escape_xml(description)}</description>
    <link>{self._escape_xml(link)}</link>
    <lastBuildDate>{now}</lastBuildDate>
    <generator>uDOS Core Feed Handler v1.0.0</generator>
"""

        for item in items:
            rss += self._generate_rss_item(item)

        rss += """  </channel>
</rss>
"""
        return rss

    def _generate_rss_item(self, item: Dict) -> str:
        """Generate single RSS item"""
        title = item.get("title", "Untitled")
        description = item.get("description", "")
        link = item.get("link", "")
        pub_date = item.get(
            "pubDate", datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        )

        item_xml = f"""    <item>
      <title>{self._escape_xml(title)}</title>
      <description>{self._escape_xml(description)}</description>
      <link>{self._escape_xml(link)}</link>
      <pubDate>{pub_date}</pubDate>
    </item>
"""
        return item_xml

    def generate_json_feed(
        self, items: List[Dict], title: str, description: str, home_page_url: str
    ) -> str:
        """Generate JSON Feed v1.1

        Items should have: title, content_text or content_html, url, date_published
        """
        feed = {
            "version": "https://jsonfeed.org/version/1.1",
            "title": title,
            "description": description,
            "home_page_url": home_page_url,
            "items": [],
        }

        for item in items:
            feed_item = {
                "id": item.get("id", item.get("url", "")),
                "title": item.get("title", "Untitled"),
                "url": item.get("url", ""),
            }

            if "content_text" in item:
                feed_item["content_text"] = item["content_text"]
            if "content_html" in item:
                feed_item["content_html"] = item["content_html"]
            if "date_published" in item:
                feed_item["date_published"] = item["date_published"]

            feed["items"].append(feed_item)

        return json.dumps(feed, indent=2)

    def parse_rss(self, rss_xml: str) -> Dict:
        """Parse RSS feed (simplified parser)"""
        # This is a simplified parser - production would use xml.etree or feedparser
        import re

        feed_data = {"type": "rss", "items": []}

        # Extract title
        title_match = re.search(r"<title>([^<]+)</title>", rss_xml)
        if title_match:
            feed_data["title"] = title_match.group(1)

        # Extract items
        item_pattern = r"<item>(.*?)</item>"
        for item_match in re.finditer(item_pattern, rss_xml, re.DOTALL):
            item_xml = item_match.group(1)

            item = {}
            for field in ["title", "description", "link", "pubDate"]:
                field_match = re.search(f"<{field}>([^<]+)</{field}>", item_xml)
                if field_match:
                    item[field] = field_match.group(1)

            feed_data["items"].append(item)

        return feed_data

    def parse_json_feed(self, json_str: str) -> Dict:
        """Parse JSON Feed"""
        try:
            feed = json.loads(json_str)
            return {
                "type": "json",
                "title": feed.get("title", ""),
                "description": feed.get("description", ""),
                "items": feed.get("items", []),
            }
        except json.JSONDecodeError as e:
            return {"type": "json", "error": str(e), "items": []}

    def compile_feed(self, source_files: List[str], output_format: str = "rss") -> str:
        """Compile feed from multiple markdown files

        This would scan frontmatter and generate feed items
        """
        items = []

        # Placeholder - would read actual files
        for i, filepath in enumerate(source_files):
            items.append(
                {
                    "title": f"Item {i+1}",
                    "description": f"Content from {filepath}",
                    "link": f"file://{filepath}",
                    "pubDate": datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"),
                }
            )

        if output_format == "rss":
            return self.generate_rss(
                items,
                title="uDOS Feed",
                description="Auto-generated feed from uDOS Core",
                link="udos://feed/compiled",
            )
        elif output_format == "json":
            return self.generate_json_feed(
                items,
                title="uDOS Feed",
                description="Auto-generated feed from uDOS Core",
                home_page_url="udos://feed/compiled",
            )
        else:
            raise ValueError(f"Unsupported format: {output_format}")

    def _escape_xml(self, text: str) -> str:
        """Escape XML special characters"""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )


if __name__ == "__main__":
    # Demo feed generation
    handler = FeedHandler()

    items = [
        {
            "title": "First Post",
            "description": "This is the first post",
            "link": "https://example.com/first",
            "pubDate": "Mon, 18 Jan 2026 12:00:00 GMT",
        },
        {
            "title": "Second Post",
            "description": "This is the second post",
            "link": "https://example.com/second",
            "pubDate": "Mon, 18 Jan 2026 13:00:00 GMT",
        },
    ]

    print("=== RSS Feed ===\n")
    rss = handler.generate_rss(items, "Test Feed", "A test feed", "https://example.com")
    print(rss[:500] + "...\n")

    print("\n=== JSON Feed ===\n")
    json_feed = handler.generate_json_feed(
        [
            {"title": i["title"], "content_text": i["description"], "url": i["link"]}
            for i in items
        ],
        "Test Feed",
        "A test feed",
        "https://example.com",
    )
    print(json_feed[:500] + "...")
