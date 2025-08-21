#!/usr/bin/env python3
"""
uDOS Sorcerer - Simple Web Scraper
Lightweight web scraping without browser dependencies
Based on SimpleBrowser.NET concepts
"""

import requests
import json
import time
import os
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
import re

class uDOSWebScraper:
    """
    Simple web scraper for uDOS - no browser required
    Perfect for basic web scraping and API interactions
    """
    
    def __init__(self, timeout=10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'uDOS-Sorcerer-Scraper/1.3 (Universal Development Operating System)'
        })
        self.scraped_data = []
        self.data_dir = "/Users/agentdigital/uDOS/sorcerer/web-browser/scraped_data"
        
        os.makedirs(self.data_dir, exist_ok=True)
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a web page"""
        try:
            print(f"🌐 Fetching: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            print(f"✅ Successfully fetched: {soup.title.string if soup.title else 'No title'}")
            return soup
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching {url}: {e}")
            return None
    
    def scrape_elements(self, url: str, selectors: Dict[str, str]) -> Dict[str, Any]:
        """
        Scrape specific elements using CSS selectors
        selectors: Dict mapping field names to CSS selectors
        """
        soup = self.fetch_page(url)
        if not soup:
            return {}
        
        scraped = {
            "url": url,
            "title": soup.title.string if soup.title else "No title",
            "timestamp": time.time(),
            "data": {}
        }
        
        for field, selector in selectors.items():
            try:
                elements = soup.select(selector)
                if elements:
                    if len(elements) == 1:
                        scraped["data"][field] = elements[0].get_text(strip=True)
                    else:
                        scraped["data"][field] = [el.get_text(strip=True) for el in elements]
                else:
                    scraped["data"][field] = None
                    print(f"⚠️ No elements found for selector: {selector}")
            except Exception as e:
                print(f"❌ Error scraping {field}: {e}")
                scraped["data"][field] = None
        
        self.scraped_data.append(scraped)
        return scraped
    
    def scrape_links(self, url: str, filter_pattern: Optional[str] = None) -> List[str]:
        """Extract all links from a page"""
        soup = self.fetch_page(url)
        if not soup:
            return []
        
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Convert relative URLs to absolute
            if href.startswith('/'):
                href = urljoin(url, href)
            elif not href.startswith(('http://', 'https://')):
                href = urljoin(url, href)
            
            # Apply filter if provided
            if filter_pattern:
                if re.search(filter_pattern, href):
                    links.append(href)
            else:
                links.append(href)
        
        print(f"🔗 Found {len(links)} links")
        return list(set(links))  # Remove duplicates
    
    def scrape_images(self, url: str) -> List[Dict[str, str]]:
        """Extract all images from a page"""
        soup = self.fetch_page(url)
        if not soup:
            return []
        
        images = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src:
                # Convert relative URLs to absolute
                if src.startswith('/'):
                    src = urljoin(url, src)
                elif not src.startswith(('http://', 'https://')):
                    src = urljoin(url, src)
                
                images.append({
                    'src': src,
                    'alt': img.get('alt', ''),
                    'title': img.get('title', ''),
                    'width': img.get('width', ''),
                    'height': img.get('height', '')
                })
        
        print(f"🖼️ Found {len(images)} images")
        return images
    
    def post_form(self, url: str, form_data: Dict[str, str]) -> Optional[BeautifulSoup]:
        """Submit a form via POST"""
        try:
            print(f"📤 Posting form to: {url}")
            response = self.session.post(url, data=form_data, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            print(f"✅ Form submitted successfully")
            return soup
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error posting form: {e}")
            return None
    
    def api_request(self, url: str, method: str = 'GET', data: Optional[Dict] = None) -> Optional[Dict]:
        """Make API requests and return JSON response"""
        try:
            print(f"🔌 API {method} request to: {url}")
            
            if method.upper() == 'GET':
                response = self.session.get(url, timeout=self.timeout)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, timeout=self.timeout)
            else:
                response = self.session.request(method, url, json=data, timeout=self.timeout)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"❌ API request error: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            return None
    
    def download_file(self, url: str, filename: Optional[str] = None) -> str:
        """Download a file from URL"""
        try:
            if not filename:
                filename = os.path.basename(urlparse(url).path) or 'downloaded_file'
            
            filepath = os.path.join(self.data_dir, filename)
            
            print(f"⬇️ Downloading: {url}")
            response = self.session.get(url, timeout=self.timeout, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✅ Downloaded: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Download error: {e}")
            return ""
    
    def save_data(self, filename: Optional[str] = None) -> str:
        """Save scraped data to JSON file"""
        if not filename:
            timestamp = int(time.time())
            filename = f"scraped_data_{timestamp}.json"
        
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(self.scraped_data, f, indent=2)
            print(f"💾 Data saved: {filepath}")
            return filepath
        except Exception as e:
            print(f"❌ Error saving data: {e}")
            return ""
    
    def get_page_metadata(self, url: str) -> Dict[str, Any]:
        """Extract page metadata (title, description, keywords, etc.)"""
        soup = self.fetch_page(url)
        if not soup:
            return {}
        
        metadata = {
            "url": url,
            "title": soup.title.string if soup.title else "",
            "description": "",
            "keywords": "",
            "author": "",
            "lang": soup.get('lang', ''),
            "meta_tags": {},
            "headings": {},
            "links_count": len(soup.find_all('a')),
            "images_count": len(soup.find_all('img')),
            "forms_count": len(soup.find_all('form'))
        }
        
        # Extract meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name', '').lower()
            content = meta.get('content', '')
            
            if name == 'description':
                metadata["description"] = content
            elif name == 'keywords':
                metadata["keywords"] = content
            elif name == 'author':
                metadata["author"] = content
            elif name:
                metadata["meta_tags"][name] = content
        
        # Extract headings
        for level in range(1, 7):
            headings = [h.get_text(strip=True) for h in soup.find_all(f'h{level}')]
            if headings:
                metadata["headings"][f'h{level}'] = headings
        
        return metadata

def main():
    """CLI interface for web scraping"""
    import argparse
    
    parser = argparse.ArgumentParser(description="uDOS Web Scraper - Simple scraping without browser")
    parser.add_argument("command", choices=["scrape", "links", "images", "metadata", "download", "api"])
    parser.add_argument("--url", required=True, help="Target URL")
    parser.add_argument("--selectors", help="JSON string of CSS selectors for scraping")
    parser.add_argument("--output", help="Output filename")
    parser.add_argument("--filter", help="Filter pattern for links")
    parser.add_argument("--method", default="GET", help="HTTP method for API requests")
    parser.add_argument("--data", help="JSON data for API requests")
    
    args = parser.parse_args()
    
    scraper = uDOSWebScraper()
    
    try:
        if args.command == "scrape":
            if not args.selectors:
                print("❌ Selectors required for scraping")
                return
            
            selectors = json.loads(args.selectors)
            data = scraper.scrape_elements(args.url, selectors)
            print(json.dumps(data, indent=2))
            
            if args.output:
                scraper.save_data(args.output)
        
        elif args.command == "links":
            links = scraper.scrape_links(args.url, args.filter)
            for link in links:
                print(link)
        
        elif args.command == "images":
            images = scraper.scrape_images(args.url)
            print(json.dumps(images, indent=2))
        
        elif args.command == "metadata":
            metadata = scraper.get_page_metadata(args.url)
            print(json.dumps(metadata, indent=2))
        
        elif args.command == "download":
            scraper.download_file(args.url, args.output)
        
        elif args.command == "api":
            data = json.loads(args.data) if args.data else None
            result = scraper.api_request(args.url, args.method, data)
            if result:
                print(json.dumps(result, indent=2))
    
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
