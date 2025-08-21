#!/usr/bin/env python3
"""
uDOS Viewport Manager
Multi-mode Chromium viewport management system for uDOS
"""

import os
import sys
import json
import subprocess
import time
import psutil
import signal
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from threading import Thread, Lock

# Add uCORE to path
UDOS_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(UDOS_ROOT / "uCORE" / "core"))

@dataclass
class ViewportConfig:
    """Viewport configuration"""
    id: str
    mode: str
    viewport_type: str
    url: str
    width: int = 1024
    height: int = 768
    x: int = 0
    y: int = 0
    user_data_dir: Optional[str] = None
    extensions: List[str] = None
    flags: List[str] = None
    pid: Optional[int] = None
    
    def __post_init__(self):
        if self.extensions is None:
            self.extensions = []
        if self.flags is None:
            self.flags = []

class ViewportManager:
    """Manages Chromium viewports for different uDOS modes"""
    
    def __init__(self):
        self.udos_root = UDOS_ROOT
        self.viewports_dir = self.udos_root / "uMEMORY" / "viewports"
        self.config_file = self.viewports_dir / "active_viewports.json"
        self.viewports: Dict[str, ViewportConfig] = {}
        self.lock = Lock()
        
        # Ensure directories exist
        self.viewports_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing viewports
        self.load_viewports()
        
        # Mode-specific configurations
        self.mode_configs = {
            "wizard": {
                "default_type": "development",
                "allowed_types": ["development", "documentation", "debug"],
                "default_flags": ["--disable-web-security", "--enable-emoji"],
                "max_viewports": 3,
                "markdown_preview": True
            },
            "dev": {
                "default_type": "development", 
                "allowed_types": ["development", "terminal", "debug", "logs"],
                "default_flags": ["--disable-web-security", "--remote-debugging-port=9222", "--enable-emoji"],
                "max_viewports": 4,
                "markdown_preview": True
            },
            "tomb": {
                "default_type": "monitoring",
                "allowed_types": ["monitoring", "logs", "dashboard"],
                "default_flags": ["--private", "--minimal-ui"],
                "max_viewports": 2,
                "markdown_preview": False
            },
            "imp": {
                "default_type": "terminal",
                "allowed_types": ["terminal", "development", "debug"],
                "default_flags": ["--disable-background-timer-throttling", "--enable-emoji"],
                "max_viewports": 3,
                "markdown_preview": True
            },
            "sorcerer": {
                "default_type": "administration",
                "allowed_types": ["administration", "monitoring", "dashboard", "logs"],
                "default_flags": ["--enable-logging", "--minimal-ui", "--enable-emoji"],
                "max_viewports": 4,
                "markdown_preview": True
            },
            "drone": {
                "default_type": "monitoring",
                "allowed_types": ["monitoring", "terminal"],
                "default_flags": ["--headless", "--disable-gpu"],
                "max_viewports": 1,
                "markdown_preview": False
            },
            "ghost": {
                "default_type": "monitoring",
                "allowed_types": ["monitoring", "logs"],
                "default_flags": ["--private", "--headless"],
                "max_viewports": 2,
                "markdown_preview": False
            },
            "admin": {
                "default_type": "administration",
                "allowed_types": ["administration", "monitoring", "development", "dashboard", "logs"],
                "default_flags": ["--remote-debugging-port=9223", "--enable-emoji"],
                "max_viewports": 4,
                "markdown_preview": True
            }
        }
    
    def load_viewports(self):
        """Load active viewports from config file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    for viewport_data in data.get('viewports', []):
                        viewport = ViewportConfig(**viewport_data)
                        # Check if process is still running
                        if viewport.pid and self.is_process_running(viewport.pid):
                            self.viewports[viewport.id] = viewport
                        else:
                            print(f"🔄 Viewport {viewport.id} no longer running, removing from config")
        except Exception as e:
            print(f"⚠️  Error loading viewports: {e}")
    
    def save_viewports(self):
        """Save active viewports to config file"""
        try:
            data = {
                'viewports': [asdict(viewport) for viewport in self.viewports.values()],
                'updated': time.time()
            }
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠️  Error saving viewports: {e}")
    
    def is_process_running(self, pid: int) -> bool:
        """Check if a process is still running"""
        try:
            return psutil.pid_exists(pid) and psutil.Process(pid).is_running()
        except:
            return False
    
    def get_chromium_command(self) -> str:
        """Find available lightweight/minimal browser command"""
        
        # On macOS, prefer default system browser
        if os.path.exists('/usr/bin/open'):
            print(f"🎯 Using default system browser")
            return 'default'
        
        # Prioritize minimal browsers over Chromium
        commands = [
            # Minimal WebKit browsers (preferred)
            'surf',                    # Suckless minimal browser
            'luakit',                  # Lightweight WebKit browser  
            'uzbl-browser',            # Minimal webkit browser
            'qutebrowser',             # Vim-like minimal browser
            'nyxt',                    # Lisp-based extensible browser
            
            # GTK/WebKit browsers
            'epiphany',                # GNOME Web (minimal)
            'midori',                  # Lightweight GTK browser
            'otter-browser',           # Qt-based lightweight browser
            
            # Terminal-based browsers (ultra minimal)
            'w3m',                     # Terminal web browser
            'lynx',                    # Text-based browser
            'links',                   # Text-based browser
            'elinks',                  # Enhanced links
            
            # Electron-based minimal browsers
            'min',                     # Minimal browser
            'brave-browser',           # Privacy-focused
            
            # macOS minimal browsers
            '/Applications/Safari.app/Contents/MacOS/Safari',  # Safari (minimal UI possible)
            '/Applications/Orion.app/Contents/MacOS/Orion',    # Orion (WebKit-based)
            '/Applications/SigmaOS.app/Contents/MacOS/SigmaOS', # SigmaOS (minimal)
            
            # Fallback to Chromium/Chrome (least preferred)
            'chromium-browser',
            'google-chrome',
            'google-chrome-stable', 
            'chromium',
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            '/Applications/Chromium.app/Contents/MacOS/Chromium',
            'chrome'
        ]
        
        for cmd in commands:
            try:
                if os.path.exists(cmd):
                    print(f"🎯 Found browser: {cmd}")
                    return cmd
                subprocess.run(['which', cmd], capture_output=True, check=True)
                print(f"🎯 Found browser: {cmd}")
                return cmd
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        raise RuntimeError("No suitable browser found. Install surf, luakit, qutebrowser, or another minimal browser")
    
    def get_udos_display_size(self, mode: str, viewport_type: str):
        """Get uDOS recommended display sizes based on mode and type"""
        # uDOS Display Size Recommendations (from display.sh)
        size_configs = {
            'compact': {'width': 1024, 'height': 576},      # 80x24 equivalent
            'standard': {'width': 1440, 'height': 900},     # 120x30 equivalent  
            'wide': {'width': 1680, 'height': 1050},        # 140x35 equivalent
            'coding': {'width': 1440, 'height': 1500},      # 120x50 equivalent
            'dashboard': {'width': 1920, 'height': 1200},   # 160x40 equivalent
        }
        
        # Mode-specific size preferences
        mode_sizes = {
            'wizard': 'standard',     # Balanced for development
            'sorcerer': 'wide',       # Spacious for administration
            'imp': 'coding',          # Tall for script editing
            'tomb': 'standard',       # Balanced for archiving
            'drone': 'compact',       # Minimal for automation
            'ghost': 'compact',       # Minimal for monitoring
            'dev': 'coding',          # Tall for development
            'admin': 'dashboard'      # Wide for system monitoring
        }
        
        # Type-specific adjustments
        if viewport_type in ['terminal', 'debug']:
            size_key = 'coding'  # Prefer tall windows
        elif viewport_type in ['dashboard', 'monitoring']:
            size_key = 'dashboard'  # Prefer wide windows
        else:
            size_key = mode_sizes.get(mode, 'standard')
            
        return size_configs[size_key]
    
    def get_minimal_browser_flags(self, browser_name: str, viewport_type: str, mode: str) -> list:
        """Get minimal UI flags for different browsers - command controlled"""
        
        # Ultra-minimal configurations by browser type
        minimal_configs = {
            # Suckless/Terminal browsers (ultra minimal)
            'surf': ['-i', '-p', '-s'],  # inspector, private, minimal
            'luakit': ['-U', 'uDOS-Minimal/1.0'],
            'uzbl-browser': ['--config-file=/dev/null'],
            'lynx': ['-accept_all_cookies', '-display_charset=utf-8', '-useragent=uDOS-Minimal'],
            'links': ['-g', '-no-connect-timeout', '10'],
            'w3m': ['-graph', '-T', 'text/html'],
            'elinks': ['-no-home', '-auto-submit', '0'],
            
            # Minimal GUI browsers
            'qutebrowser': [
                '--set', 'tabs.show', 'never',
                '--set', 'statusbar.show', 'never', 
                '--set', 'downloads.location.prompt', 'false',
                '--set', 'content.headers.user_agent', 'uDOS-Minimal/1.0',
                '--set', 'scrolling.bar', 'never',
                '--set', 'completion.show', 'never'
            ],
            'midori': ['--inprivate', '--app'],
            'epiphany': ['--application-mode', '--private-instance'],
            'otter-browser': ['--private-session', '--no-extensions'],
            'nyxt': ['--no-socket', '--eval', '(define-configuration buffer ((style-mode-line :none)))'],
            
            # macOS minimal browsers
            'safari': ['--private'],
            'orion': ['--minimal-ui'],
            'sigmaos': ['--minimal'],
            
            # Fallback Chromium/Chrome with maximum minimalism
            'chromium': [
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--hide-crash-restore-bubble',
                '--no-first-run',
                '--no-default-browser-check',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-notifications',
                '--disable-infobars',
                '--hide-scrollbars'
            ],
            'chrome': [
                '--disable-web-security',
                '--no-first-run',
                '--no-default-browser-check',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-notifications',
                '--disable-infobars',
                '--hide-scrollbars'
            ]
        }
        
        # Mode-specific minimal modifications
        mode_modifications = {
            'drone': ['--headless'] if any(x in browser_name for x in ['chromium', 'chrome']) else [],
            'ghost': ['--incognito'] if any(x in browser_name for x in ['chromium', 'chrome']) else [],
            'tomb': ['--disable-javascript'] if 'security' in viewport_type else [],
            'dev': ['--remote-debugging-port=9222'] if any(x in browser_name for x in ['chromium', 'chrome']) else []
        }
        
        # Get base minimal flags
        base_flags = []
        for browser_key in minimal_configs:
            if browser_key in browser_name:
                base_flags = minimal_configs[browser_key]
                break
        
        # Add mode-specific flags
        mode_flags = mode_modifications.get(mode, [])
        
        return base_flags + mode_flags
    
    def create_viewport(self, mode: str, viewport_type: str = None, url: str = None, 
                       width: int = None, height: int = None, 
                       viewport_id: str = None) -> ViewportConfig:
        """Create a new viewport for the specified mode - SINGLE WINDOW MODE"""
        
        if mode not in self.mode_configs:
            raise ValueError(f"Unknown mode: {mode}")
        
        mode_config = self.mode_configs[mode]
        
        # SINGLE WINDOW ENFORCEMENT: Close all existing viewports first
        if self.viewports:
            print(f"🔄 Single window mode: Closing {len(self.viewports)} existing viewport(s)")
            existing_ids = list(self.viewports.keys())
            for existing_id in existing_ids:
                self.close_viewport(existing_id)
            print(f"✅ All existing viewports closed")
        
        # Set defaults
        if viewport_type is None:
            viewport_type = mode_config['default_type']
        elif viewport_type not in mode_config['allowed_types']:
            raise ValueError(f"Viewport type {viewport_type} not allowed for mode {mode}")
        
        # Use uDOS display size settings if not specified
        if width is None or height is None:
            udos_size = self.get_udos_display_size(mode, viewport_type)
            width = width or udos_size['width']
            height = height or udos_size['height']
            print(f"📐 Using uDOS display size: {width}x{height} (mode: {mode}, type: {viewport_type})")
        
        if url is None:
            url = f"http://localhost:8080/?mode={mode}&type={viewport_type}"
        
        if viewport_id is None:
            viewport_id = f"{mode}_{viewport_type}_{int(time.time())}"
        
        # Create user data directory
        user_data_dir = self.viewports_dir / f"userdata_{viewport_id}"
        user_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Single window mode - always use center position
        x = 100  # Center position instead of cascading
        y = 100  # Center position instead of cascading
        
        # Create viewport config
        viewport = ViewportConfig(
            id=viewport_id,
            mode=mode,
            viewport_type=viewport_type,
            url=url,
            width=width,
            height=height,
            x=x,
            y=y,
            user_data_dir=str(user_data_dir),
            flags=mode_config['default_flags'].copy()
        )
        
        # Launch browser with minimal UI
        try:
            browser_cmd = self.get_chromium_command()
            
            # Handle default browser case
            if browser_cmd == 'default':
                browser_name = 'default'
            else:
                browser_name = os.path.basename(browser_cmd).lower()
            
            # Get minimal UI flags based on browser type
            minimal_flags = self.get_minimal_browser_flags(browser_name, viewport_type, mode)
            
            cmd = [browser_cmd] + minimal_flags
            
            # Add browser-specific launch arguments
            if 'surf' in browser_name:
                cmd.extend(['-g', f"{width}x{height}+{x}+{y}", url])
            elif 'qutebrowser' in browser_name:
                cmd.extend(['--target', 'window', url])
            elif 'luakit' in browser_name:
                cmd.extend(['-g', f"{width}x{height}+{x}+{y}", url])
            elif any(term in browser_name for term in ['lynx', 'links', 'w3m', 'elinks']):
                cmd.append(url)
            elif 'default' in browser_name or 'safari' in browser_name:
                # Use default system browser with open command (no --new to prevent multiple windows)
                cmd = ['open', url]
            else:
                # Standard browser (Chrome, Chromium, etc.)
                cmd.extend([
                    f"--user-data-dir={user_data_dir}",
                    f"--window-size={width},{height}",
                    f"--window-position={x},{y}",
                    url
                ])
            
            print(f"🚀 Launching minimal viewport: {browser_name}")
            print(f"🔧 Command: {' '.join(cmd)}")
            process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            viewport.pid = process.pid
            
            # Store viewport
            self.viewports[viewport_id] = viewport
            self.save_viewports()
            
            print(f"✅ Viewport '{viewport_id}' created for mode '{mode}' (PID: {process.pid})")
            return viewport
            
        except Exception as e:
            print(f"❌ Failed to create viewport: {e}")
            raise
    
    def close_viewport(self, viewport_id: str) -> bool:
        """Close a specific viewport"""
        if viewport_id not in self.viewports:
            print(f"⚠️  Viewport '{viewport_id}' not found")
            return False
        
        viewport = self.viewports[viewport_id]
        
        try:
            if viewport.pid and self.is_process_running(viewport.pid):
                os.kill(viewport.pid, signal.SIGTERM)
                time.sleep(1)
                
                # Force kill if still running
                if self.is_process_running(viewport.pid):
                    os.kill(viewport.pid, signal.SIGKILL)
            
            # Clean up user data directory
            if viewport.user_data_dir and os.path.exists(viewport.user_data_dir):
                import shutil
                shutil.rmtree(viewport.user_data_dir, ignore_errors=True)
            
            # Remove from config
            with self.lock:
                del self.viewports[viewport_id]
                self.save_viewports()
            
            print(f"✅ Viewport '{viewport_id}' closed")
            return True
            
        except Exception as e:
            print(f"❌ Error closing viewport '{viewport_id}': {e}")
            return False
    
    def close_mode_viewports(self, mode: str) -> int:
        """Close all viewports for a specific mode"""
        mode_viewports = [v.id for v in self.viewports.values() if v.mode == mode]
        closed_count = 0
        
        for viewport_id in mode_viewports:
            if self.close_viewport(viewport_id):
                closed_count += 1
        
        print(f"🔄 Closed {closed_count} viewports for mode '{mode}'")
        return closed_count
    
    def list_viewports(self, mode: str = None) -> List[ViewportConfig]:
        """List active viewports, optionally filtered by mode"""
        if mode:
            return [v for v in self.viewports.values() if v.mode == mode]
        return list(self.viewports.values())
    
    def cleanup_dead_viewports(self) -> int:
        """Clean up viewports with dead processes"""
        dead_viewports = []
        
        for viewport_id, viewport in self.viewports.items():
            if viewport.pid and not self.is_process_running(viewport.pid):
                dead_viewports.append(viewport_id)
        
        for viewport_id in dead_viewports:
            print(f"🧹 Cleaning up dead viewport: {viewport_id}")
            with self.lock:
                del self.viewports[viewport_id]
        
        if dead_viewports:
            self.save_viewports()
        
        return len(dead_viewports)

def main():
    """CLI interface for viewport manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description='uDOS Viewport Manager')
    parser.add_argument('action', choices=['create', 'close', 'list', 'cleanup', 'close-mode'],
                       help='Action to perform')
    parser.add_argument('--mode', required=False, help='User mode (wizard, dev, tomb, etc.)')
    parser.add_argument('--type', help='Viewport type (development, monitoring, etc.)')
    parser.add_argument('--url', help='URL to open')
    parser.add_argument('--width', type=int, default=1024, help='Window width')
    parser.add_argument('--height', type=int, default=768, help='Window height')
    parser.add_argument('--id', help='Viewport ID for close action')
    
    args = parser.parse_args()
    
    manager = ViewportManager()
    
    if args.action == 'create':
        if not args.mode:
            print("❌ Mode is required for create action")
            sys.exit(1)
        
        try:
            viewport = manager.create_viewport(
                mode=args.mode,
                viewport_type=args.type,
                url=args.url,
                width=args.width,
                height=args.height
            )
            print(f"📋 Viewport ID: {viewport.id}")
            print(f"🌐 URL: {viewport.url}")
            print(f"📱 Dimensions: {viewport.width}x{viewport.height}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    elif args.action == 'close':
        if not args.id:
            print("❌ Viewport ID is required for close action")
            sys.exit(1)
        
        if not manager.close_viewport(args.id):
            sys.exit(1)
    
    elif args.action == 'close-mode':
        if not args.mode:
            print("❌ Mode is required for close-mode action")
            sys.exit(1)
        
        count = manager.close_mode_viewports(args.mode)
        if count == 0:
            print(f"ℹ️  No viewports found for mode '{args.mode}'")
    
    elif args.action == 'list':
        viewports = manager.list_viewports(args.mode)
        
        if not viewports:
            mode_filter = f" for mode '{args.mode}'" if args.mode else ""
            print(f"ℹ️  No active viewports{mode_filter}")
        else:
            print("📊 Active Viewports:")
            print("-" * 80)
            for viewport in viewports:
                status = "🟢 Running" if manager.is_process_running(viewport.pid) else "🔴 Dead"
                print(f"🆔 {viewport.id}")
                print(f"   Mode: {viewport.mode} | Type: {viewport.viewport_type}")
                print(f"   URL: {viewport.url}")
                print(f"   PID: {viewport.pid} | Status: {status}")
                print(f"   Size: {viewport.width}x{viewport.height} at ({viewport.x},{viewport.y})")
                print("-" * 80)
    
    elif args.action == 'cleanup':
        count = manager.cleanup_dead_viewports()
        print(f"🧹 Cleaned up {count} dead viewports")

if __name__ == '__main__':
    main()
