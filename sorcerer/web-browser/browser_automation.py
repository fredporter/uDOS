#!/usr/bin/env python3
"""
uDOS Sorcerer - Web Browser Automation Module
Integration with SimpleBrowser.NET concepts for Python

Features:
- Web scraping and data extraction
- Browser automation for testing
- Page interaction and form filling
- Screenshot capture
- Session management
"""

import requests
import json
import time
import os
import sys
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional, Any
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class uDOSBrowserSorcerer:
    """
    Advanced web browser automation and scraping for uDOS
    Inspired by SimpleBrowser.NET but built for Python/uDOS ecosystem
    """
    
    def __init__(self, headless=True, timeout=10):
        self.headless = headless
        self.timeout = timeout
        self.driver = None
        self.session_data = {}
        self.scraped_data = []
        self.screenshots_dir = "/Users/agentdigital/uDOS/sorcerer/web-browser/screenshots"
        self.data_dir = "/Users/agentdigital/uDOS/sorcerer/web-browser/data"
        
        # Ensure directories exist
        os.makedirs(self.screenshots_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.setup_driver()
    
    def setup_driver(self):
        """Initialize Chrome WebDriver with uDOS-optimized settings"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=uDOS-Sorcerer-Browser/1.3")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(self.timeout)
            print("🔮 uDOS Browser Sorcerer initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing browser: {e}")
            self.driver = None
    
    def navigate(self, url: str) -> bool:
        """Navigate to a URL"""
        if not self.driver:
            print("❌ Browser not initialized")
            return False
        
        try:
            print(f"🌐 Navigating to: {url}")
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, self.timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            print(f"✅ Successfully loaded: {self.driver.title}")
            return True
        except TimeoutException:
            print(f"⏰ Timeout loading {url}")
            return False
        except Exception as e:
            print(f"❌ Error navigating to {url}: {e}")
            return False
    
    def scrape_data(self, selectors: Dict[str, str]) -> Dict[str, Any]:
        """
        Scrape data using CSS selectors
        selectors: Dict mapping field names to CSS selectors
        """
        if not self.driver:
            return {}
        
        scraped = {
            "url": self.driver.current_url,
            "title": self.driver.title,
            "timestamp": time.time(),
            "data": {}
        }
        
        for field, selector in selectors.items():
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    if len(elements) == 1:
                        scraped["data"][field] = elements[0].text.strip()
                    else:
                        scraped["data"][field] = [el.text.strip() for el in elements]
                else:
                    scraped["data"][field] = None
                    print(f"⚠️ No elements found for selector: {selector}")
            except Exception as e:
                print(f"❌ Error scraping {field}: {e}")
                scraped["data"][field] = None
        
        self.scraped_data.append(scraped)
        return scraped
    
    def fill_form(self, form_data: Dict[str, str]) -> bool:
        """
        Fill form fields
        form_data: Dict mapping field selectors to values
        """
        if not self.driver:
            return False
        
        try:
            for selector, value in form_data.items():
                element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                
                # Clear and fill
                element.clear()
                element.send_keys(value)
                print(f"✅ Filled field {selector} with: {value}")
            
            return True
        except Exception as e:
            print(f"❌ Error filling form: {e}")
            return False
    
    def click_element(self, selector: str) -> bool:
        """Click an element by CSS selector"""
        if not self.driver:
            return False
        
        try:
            element = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            element.click()
            print(f"✅ Clicked element: {selector}")
            return True
        except Exception as e:
            print(f"❌ Error clicking {selector}: {e}")
            return False
    
    def capture_screenshot(self, filename: Optional[str] = None) -> str:
        """Capture screenshot of current page"""
        if not self.driver:
            return ""
        
        if not filename:
            timestamp = int(time.time())
            filename = f"screenshot_{timestamp}.png"
        
        filepath = os.path.join(self.screenshots_dir, filename)
        
        try:
            self.driver.save_screenshot(filepath)
            print(f"📸 Screenshot saved: {filepath}")
            return filepath
        except Exception as e:
            print(f"❌ Error capturing screenshot: {e}")
            return ""
    
    def execute_script(self, script: str) -> Any:
        """Execute JavaScript in the browser"""
        if not self.driver:
            return None
        
        try:
            result = self.driver.execute_script(script)
            print(f"✅ Executed script successfully")
            return result
        except Exception as e:
            print(f"❌ Error executing script: {e}")
            return None
    
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
    
    def get_page_info(self) -> Dict[str, Any]:
        """Get comprehensive page information"""
        if not self.driver:
            return {}
        
        try:
            info = {
                "url": self.driver.current_url,
                "title": self.driver.title,
                "page_source_length": len(self.driver.page_source),
                "cookies": self.driver.get_cookies(),
                "window_size": self.driver.get_window_size(),
                "current_window_handle": self.driver.current_window_handle,
                "window_handles": self.driver.window_handles
            }
            
            # Get additional info via JavaScript
            js_info = self.driver.execute_script("""
                return {
                    userAgent: navigator.userAgent,
                    url: window.location.href,
                    domain: window.location.hostname,
                    protocol: window.location.protocol,
                    viewport: {
                        width: window.innerWidth,
                        height: window.innerHeight
                    },
                    scroll: {
                        x: window.pageXOffset,
                        y: window.pageYOffset
                    },
                    loadTime: performance.timing.loadEventEnd - performance.timing.navigationStart
                };
            """)
            
            info.update(js_info)
            return info
            
        except Exception as e:
            print(f"❌ Error getting page info: {e}")
            return {}
    
    def close(self):
        """Close browser and cleanup"""
        if self.driver:
            self.driver.quit()
            print("🔮 Browser Sorcerer session ended")

def main():
    """CLI interface for browser automation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="uDOS Browser Sorcerer - Web Automation")
    parser.add_argument("command", choices=["navigate", "scrape", "screenshot", "info", "test"])
    parser.add_argument("--url", help="Target URL")
    parser.add_argument("--headless", action="store_true", default=True, help="Run in headless mode")
    parser.add_argument("--timeout", type=int, default=10, help="Page load timeout")
    parser.add_argument("--selectors", help="JSON string of CSS selectors for scraping")
    parser.add_argument("--output", help="Output filename")
    
    args = parser.parse_args()
    
    # Initialize browser
    browser = uDOSBrowserSorcerer(headless=args.headless, timeout=args.timeout)
    
    try:
        if args.command == "navigate":
            if not args.url:
                print("❌ URL required for navigation")
                return
            browser.navigate(args.url)
            
        elif args.command == "scrape":
            if not args.url or not args.selectors:
                print("❌ URL and selectors required for scraping")
                return
            
            browser.navigate(args.url)
            selectors = json.loads(args.selectors)
            data = browser.scrape_data(selectors)
            
            print(f"📊 Scraped data:")
            print(json.dumps(data, indent=2))
            
            if args.output:
                browser.save_data(args.output)
            
        elif args.command == "screenshot":
            if not args.url:
                print("❌ URL required for screenshot")
                return
            
            browser.navigate(args.url)
            browser.capture_screenshot(args.output)
            
        elif args.command == "info":
            if not args.url:
                print("❌ URL required for page info")
                return
            
            browser.navigate(args.url)
            info = browser.get_page_info()
            print(json.dumps(info, indent=2))
            
        elif args.command == "test":
            # Test uDOS interface
            print("🧪 Testing uDOS interface...")
            if browser.navigate("http://localhost:8080"):
                browser.capture_screenshot("udos_test.png")
                
                # Test emoji clicking
                browser.click_element(".emoji-icon[title='GHOST']")
                time.sleep(1)
                browser.capture_screenshot("udos_ghost_clicked.png")
                
                print("✅ uDOS interface test completed")
            
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        browser.close()

if __name__ == "__main__":
    main()
