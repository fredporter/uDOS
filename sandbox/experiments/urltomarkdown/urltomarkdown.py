#!/usr/bin/env python3
"""
Simple URL to Markdown converter for uDOS
Uses requests and html2text for conversion
"""

import sys
import requests
import html2text
from urllib.parse import urlparse
import re

def clean_filename(text):
    """Clean text for use as filename"""
    # Remove invalid characters
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', text)
    # Remove multiple underscores
    cleaned = re.sub(r'_+', '_', cleaned)
    # Remove leading/trailing underscores
    cleaned = cleaned.strip('_')
    return cleaned if cleaned else 'untitled'

def url_to_markdown(url, custom_title=None):
    """Convert URL to markdown"""
    try:
        # Make request with headers to avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Initialize html2text converter
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        h.body_width = 0
        
        # Convert HTML to markdown
        markdown_content = h.handle(response.text)
        
        # Add metadata header
        title = custom_title if custom_title else extract_title(response.text)
        
        from datetime import datetime
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        header = f"""---
source: {url}
title: {title}
converted: {timestamp}
tool: uDOS urltomarkdown
---

"""
        
        return header + markdown_content
        
    except Exception as e:
        raise Exception(f"Failed to convert URL: {str(e)}")

def extract_title(html_content):
    """Extract title from HTML content"""
    import re
    title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
    if title_match:
        title = title_match.group(1).strip()
        # Clean up title
        title = re.sub(r'\s+', ' ', title)
        return title
    return "Untitled"

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python3 urltomarkdown.py <URL>", file=sys.stderr)
        sys.exit(1)
    
    url = sys.argv[1]
    custom_title = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        markdown = url_to_markdown(url, custom_title)
        print(markdown)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
