#!/usr/bin/env python3
"""
uDOS Sorcerer - Web Browser Command Integration
Integrates web scraping capabilities with uDOS command system
"""

import json
import os
import sys
from typing import Dict, List, Any
from simple_scraper import uDOSWebScraper

class uDOSSorcererCommands:
    """Command handlers for uDOS web browser integration"""
    
    def __init__(self):
        self.scraper = uDOSWebScraper()
        self.commands = {
            "web.scrape": self.cmd_scrape,
            "web.links": self.cmd_links,
            "web.images": self.cmd_images,
            "web.metadata": self.cmd_metadata,
            "web.download": self.cmd_download,
            "web.api": self.cmd_api,
            "web.test": self.cmd_test,
            "web.help": self.cmd_help
        }
    
    def execute(self, command: str, args: List[str] = None) -> Dict[str, Any]:
        """Execute a web command and return formatted result"""
        if args is None:
            args = []
        
        if command not in self.commands:
            return {
                "success": False,
                "error": f"Unknown command: {command}",
                "available_commands": list(self.commands.keys())
            }
        
        try:
            return self.commands[command](args)
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": command,
                "args": args
            }
    
    def cmd_scrape(self, args: List[str]) -> Dict[str, Any]:
        """Scrape elements from a webpage"""
        if len(args) < 2:
            return {
                "success": False,
                "error": "Usage: web.scrape <url> <selectors_json>",
                "example": 'web.scrape "https://example.com" \'{"title": "h1", "links": "a"}\''
            }
        
        url = args[0]
        try:
            selectors = json.loads(args[1])
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Invalid JSON in selectors parameter"
            }
        
        data = self.scraper.scrape_elements(url, selectors)
        return {
            "success": True,
            "command": "scrape",
            "url": url,
            "data": data
        }
    
    def cmd_links(self, args: List[str]) -> Dict[str, Any]:
        """Extract all links from a webpage"""
        if len(args) < 1:
            return {
                "success": False,
                "error": "Usage: web.links <url> [filter_pattern]"
            }
        
        url = args[0]
        filter_pattern = args[1] if len(args) > 1 else None
        
        links = self.scraper.scrape_links(url, filter_pattern)
        return {
            "success": True,
            "command": "links",
            "url": url,
            "filter": filter_pattern,
            "links": links,
            "count": len(links)
        }
    
    def cmd_images(self, args: List[str]) -> Dict[str, Any]:
        """Extract all images from a webpage"""
        if len(args) < 1:
            return {
                "success": False,
                "error": "Usage: web.images <url>"
            }
        
        url = args[0]
        images = self.scraper.scrape_images(url)
        return {
            "success": True,
            "command": "images",
            "url": url,
            "images": images,
            "count": len(images)
        }
    
    def cmd_metadata(self, args: List[str]) -> Dict[str, Any]:
        """Get webpage metadata"""
        if len(args) < 1:
            return {
                "success": False,
                "error": "Usage: web.metadata <url>"
            }
        
        url = args[0]
        metadata = self.scraper.get_page_metadata(url)
        return {
            "success": True,
            "command": "metadata",
            "metadata": metadata
        }
    
    def cmd_download(self, args: List[str]) -> Dict[str, Any]:
        """Download a file from URL"""
        if len(args) < 1:
            return {
                "success": False,
                "error": "Usage: web.download <url> [filename]"
            }
        
        url = args[0]
        filename = args[1] if len(args) > 1 else None
        
        filepath = self.scraper.download_file(url, filename)
        return {
            "success": bool(filepath),
            "command": "download",
            "url": url,
            "filepath": filepath
        }
    
    def cmd_api(self, args: List[str]) -> Dict[str, Any]:
        """Make API request"""
        if len(args) < 1:
            return {
                "success": False,
                "error": "Usage: web.api <url> [method] [data_json]"
            }
        
        url = args[0]
        method = args[1] if len(args) > 1 else "GET"
        data = None
        
        if len(args) > 2:
            try:
                data = json.loads(args[2])
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "error": "Invalid JSON in data parameter"
                }
        
        result = self.scraper.api_request(url, method, data)
        return {
            "success": result is not None,
            "command": "api",
            "url": url,
            "method": method,
            "response": result
        }
    
    def cmd_test(self, args: List[str]) -> Dict[str, Any]:
        """Test web scraping with example sites"""
        test_results = []
        
        # Test 1: Basic page scraping
        print("🧪 Testing basic page scraping...")
        try:
            data = self.scraper.scrape_elements("https://httpbin.org/html", {
                "title": "h1",
                "paragraph": "p"
            })
            test_results.append({
                "test": "basic_scraping",
                "success": bool(data.get("data")),
                "url": "https://httpbin.org/html"
            })
        except Exception as e:
            test_results.append({
                "test": "basic_scraping",
                "success": False,
                "error": str(e)
            })
        
        # Test 2: API request
        print("🧪 Testing API request...")
        try:
            api_data = self.scraper.api_request("https://httpbin.org/json")
            test_results.append({
                "test": "api_request",
                "success": api_data is not None,
                "url": "https://httpbin.org/json"
            })
        except Exception as e:
            test_results.append({
                "test": "api_request",
                "success": False,
                "error": str(e)
            })
        
        # Test 3: Links extraction
        print("🧪 Testing links extraction...")
        try:
            links = self.scraper.scrape_links("https://httpbin.org/links/10/0")
            test_results.append({
                "test": "links_extraction",
                "success": len(links) > 0,
                "links_found": len(links)
            })
        except Exception as e:
            test_results.append({
                "test": "links_extraction",
                "success": False,
                "error": str(e)
            })
        
        return {
            "success": True,
            "command": "test",
            "results": test_results,
            "passed": sum(1 for r in test_results if r.get("success", False)),
            "total": len(test_results)
        }
    
    def cmd_help(self, args: List[str]) -> Dict[str, Any]:
        """Show help for web commands"""
        help_text = {
            "web.scrape": "Scrape elements using CSS selectors: web.scrape <url> <selectors_json>",
            "web.links": "Extract all links: web.links <url> [filter_pattern]",
            "web.images": "Extract all images: web.images <url>",
            "web.metadata": "Get page metadata: web.metadata <url>",
            "web.download": "Download file: web.download <url> [filename]",
            "web.api": "Make API request: web.api <url> [method] [data_json]",
            "web.test": "Run test suite: web.test",
            "web.help": "Show this help: web.help"
        }
        
        return {
            "success": True,
            "command": "help",
            "commands": help_text,
            "examples": {
                "scrape_example": 'web.scrape "https://example.com" \'{"title": "h1", "description": "meta[name=description]"}\'',
                "links_example": 'web.links "https://github.com" ".*\\.py$"',
                "api_example": 'web.api "https://api.github.com/users/octocat"'
            }
        }

def main():
    """CLI interface for command testing"""
    if len(sys.argv) < 2:
        print("Usage: python web_commands.py <command> [args...]")
        print("Commands: web.scrape, web.links, web.images, web.metadata, web.download, web.api, web.test, web.help")
        return
    
    commander = uDOSSorcererCommands()
    command = sys.argv[1]
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    
    result = commander.execute(command, args)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
