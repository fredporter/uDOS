#!/usr/bin/env python3
"""
uDOS Universal Code Interface - Startup System
Comprehensive boot sequence for the BBC Mode 7 interface
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

class uDOSStartup:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent.parent.parent
        self.ui_path = Path(__file__).parent
        self.config_file = self.ui_path / 'config' / 'startup.json'
        self.log_file = self.ui_path / 'logs' / f'startup-{datetime.now().strftime("%Y%m%d-%H%M%S")}.log'
        
        self.startup_config = {
            'display': {
                'default_width': 800,
                'default_height': 600,
                'aspect_ratio': 1.3,
                'font': 'MODE7GX3',
                'theme': 'BBC_MODE7'
            },
            'required_folders': [
                'static',
                'static/fonts',
                'config',
                'logs',
                'cache',
                'temp'
            ],
            'required_files': [
                'index.html',
                'server.py',
                'static/style.css',
                'static/fonts.css',
                'static/app.js'
            ],
            'system_checks': {
                'python_version': '3.8',
                'required_modules': ['flask', 'flask_socketio'],
                'memory_min': 100,  # MB
                'disk_space_min': 50  # MB
            }
        }
    
    def log(self, message, level='INFO'):
        """Log startup messages"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        
        # Ensure logs directory exists
        self.log_file.parent.mkdir(exist_ok=True)
        
        with open(self.log_file, 'a') as f:
            f.write(log_entry + '\n')
    
    def create_required_folders(self):
        """Create all required folders for uDOS UI"""
        self.log("🗂️  Creating required folder structure...")
        
        for folder in self.startup_config['required_folders']:
            folder_path = self.ui_path / folder
            if not folder_path.exists():
                folder_path.mkdir(parents=True, exist_ok=True)
                self.log(f"   Created: {folder}")
            else:
                self.log(f"   Exists: {folder}")
        
        return True
    
    def check_required_files(self):
        """Check for required system files"""
        self.log("📄 Checking required files...")
        missing_files = []
        
        for file_path in self.startup_config['required_files']:
            full_path = self.ui_path / file_path
            if not full_path.exists():
                missing_files.append(file_path)
                self.log(f"   Missing: {file_path}", 'ERROR')
            else:
                self.log(f"   Found: {file_path}")
        
        if missing_files:
            self.log(f"❌ Missing {len(missing_files)} required files", 'ERROR')
            return False
        
        self.log("✅ All required files present")
        return True
    
    def check_python_version(self):
        """Check Python version compatibility"""
        self.log("🐍 Checking Python version...")
        
        required_version = tuple(map(int, self.startup_config['system_checks']['python_version'].split('.')))
        current_version = sys.version_info[:2]
        
        if current_version >= required_version:
            self.log(f"   Python {'.'.join(map(str, current_version))} ✅")
            return True
        else:
            self.log(f"   Python {'.'.join(map(str, current_version))} < {self.startup_config['system_checks']['python_version']} ❌", 'ERROR')
            return False
    
    def check_required_modules(self):
        """Check for required Python modules"""
        self.log("📦 Checking required Python modules...")
        missing_modules = []
        
        for module in self.startup_config['system_checks']['required_modules']:
            try:
                __import__(module)
                self.log(f"   {module} ✅")
            except ImportError:
                missing_modules.append(module)
                self.log(f"   {module} ❌", 'ERROR')
        
        if missing_modules:
            self.log(f"❌ Missing modules: {', '.join(missing_modules)}", 'ERROR')
            self.log("Install with: pip install " + ' '.join(missing_modules))
            return False
        
        self.log("✅ All required modules available")
        return True
    
    def check_system_resources(self):
        """Check system memory and disk space"""
        self.log("💾 Checking system resources...")
        
        try:
            # Check available memory (basic check)
            import psutil
            memory = psutil.virtual_memory()
            available_mb = memory.available / (1024 * 1024)
            
            if available_mb >= self.startup_config['system_checks']['memory_min']:
                self.log(f"   Memory: {available_mb:.0f}MB available ✅")
            else:
                self.log(f"   Memory: {available_mb:.0f}MB < {self.startup_config['system_checks']['memory_min']}MB ❌", 'WARNING')
            
            # Check disk space
            disk = psutil.disk_usage(str(self.ui_path))
            free_mb = disk.free / (1024 * 1024)
            
            if free_mb >= self.startup_config['system_checks']['disk_space_min']:
                self.log(f"   Disk: {free_mb:.0f}MB free ✅")
            else:
                self.log(f"   Disk: {free_mb:.0f}MB < {self.startup_config['system_checks']['disk_space_min']}MB ❌", 'WARNING')
            
            return True
            
        except ImportError:
            self.log("   psutil not available, skipping resource check", 'WARNING')
            return True
        except Exception as e:
            self.log(f"   Resource check error: {e}", 'WARNING')
            return True
    
    def detect_display_settings(self):
        """Detect optimal display settings"""
        self.log("🖥️  Detecting display settings...")
        
        display_config = self.startup_config['display'].copy()
        
        try:
            # Try to detect screen resolution on macOS
            result = subprocess.run(['system_profiler', 'SPDisplaysDataType'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                output = result.stdout
                if 'Resolution:' in output:
                    # Extract resolution info
                    for line in output.split('\n'):
                        if 'Resolution:' in line:
                            self.log(f"   Detected: {line.strip()}")
                            break
            
            # Adjust for BBC Mode 7 aspect ratio
            optimal_width = min(display_config['default_width'], 800)
            optimal_height = int(optimal_width / display_config['aspect_ratio'])
            
            display_config['optimal_width'] = optimal_width
            display_config['optimal_height'] = optimal_height
            
            self.log(f"   Optimal size: {optimal_width}x{optimal_height}")
            self.log(f"   Aspect ratio: 1:{display_config['aspect_ratio']}")
            
        except Exception as e:
            self.log(f"   Display detection error: {e}", 'WARNING')
            self.log("   Using default settings")
        
        return display_config
    
    def check_font_availability(self):
        """Check BBC Mode 7 font availability"""
        self.log("🔤 Checking font availability...")
        
        font_files = [
            'MODE7GX3.woff2',
            'MODE7GX3.woff',
            'MODE7GX3.ttf',
            'MODE7GX0.woff2',
            'MODE7GX2.woff2'
        ]
        
        fonts_dir = self.ui_path / 'static' / 'fonts'
        available_fonts = []
        
        for font_file in font_files:
            font_path = fonts_dir / font_file
            if font_path.exists():
                available_fonts.append(font_file)
                self.log(f"   {font_file} ✅")
            else:
                self.log(f"   {font_file} ❌")
        
        if available_fonts:
            self.log(f"✅ {len(available_fonts)} BBC Mode 7 fonts available")
            return True
        else:
            self.log("❌ No BBC Mode 7 fonts found", 'ERROR')
            return False
    
    def create_startup_config(self, display_config):
        """Create startup configuration file"""
        self.log("⚙️  Creating startup configuration...")
        
        config = {
            'startup_time': datetime.now().isoformat(),
            'display': display_config,
            'system_info': {
                'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                'platform': sys.platform,
                'ui_path': str(self.ui_path),
                'base_path': str(self.base_path)
            },
            'features': {
                'whirlwind_mode': True,
                'smart_terminal': True,
                'command_history': True,
                'auto_complete': True,
                'real_time_updates': True
            }
        }
        
        # Ensure config directory exists
        self.config_file.parent.mkdir(exist_ok=True)
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        self.log(f"   Config saved: {self.config_file}")
        return config
    
    def run_startup_sequence(self):
        """Run complete startup sequence"""
        self.log("=" * 60)
        self.log("🚀 uDOS Universal Code Interface - Startup Sequence")
        self.log("📺 BBC Mode 7 Enhanced Edition")
        self.log("=" * 60)
        
        start_time = time.time()
        
        # Phase 1: System Checks
        self.log("\n🔍 PHASE 1: System Requirements")
        checks_passed = 0
        total_checks = 4
        
        if self.check_python_version():
            checks_passed += 1
        
        if self.check_required_modules():
            checks_passed += 1
        
        if self.check_system_resources():
            checks_passed += 1
        
        if self.check_font_availability():
            checks_passed += 1
        
        self.log(f"   System checks: {checks_passed}/{total_checks} passed")
        
        # Phase 2: File System Setup
        self.log("\n🗂️  PHASE 2: File System Setup")
        if not self.create_required_folders():
            self.log("❌ Folder creation failed", 'ERROR')
            return False
        
        if not self.check_required_files():
            self.log("❌ Required files missing", 'ERROR')
            return False
        
        # Phase 3: Configuration
        self.log("\n⚙️  PHASE 3: Configuration")
        display_config = self.detect_display_settings()
        startup_config = self.create_startup_config(display_config)
        
        # Phase 4: Final Preparation
        self.log("\n🎯 PHASE 4: Final Preparation")
        self.log("   Clearing temporary files...")
        temp_dir = self.ui_path / 'temp'
        if temp_dir.exists():
            for temp_file in temp_dir.glob('*'):
                try:
                    temp_file.unlink()
                except:
                    pass
        
        self.log("   Initializing cache...")
        cache_dir = self.ui_path / 'cache'
        cache_dir.mkdir(exist_ok=True)
        
        # Startup Complete
        elapsed = time.time() - start_time
        self.log(f"\n✅ STARTUP COMPLETE ({elapsed:.2f}s)")
        self.log("=" * 60)
        self.log("🌟 uDOS Universal Code Interface Ready")
        self.log("⚡ Whirlwind mode available")
        self.log("📖 Type HELP for command list")
        self.log("🎨 BBC Mode 7 with authentic 1:1.3 aspect ratio")
        self.log("=" * 60)
        
        return startup_config

def main():
    """Main startup function"""
    startup = uDOSStartup()
    config = startup.run_startup_sequence()
    
    if config:
        return config
    else:
        print("❌ Startup failed - check logs for details")
        sys.exit(1)

if __name__ == '__main__':
    main()
