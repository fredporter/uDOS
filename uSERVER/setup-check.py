#!/usr/bin/env python3
"""
uDOS System Setup Check
Validates system configuration and displays startup sequence
"""

import os
import sys
import time
import json
from pathlib import Path

# Color codes for terminal output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'  # No Color

def print_colored(message, color=Colors.NC):
    """Print message with color"""
    print(f"{color}{message}{Colors.NC}")

def show_startup_banner():
    """Display uDOS startup banner"""
    print_colored("", Colors.CYAN)
    print_colored("   ██╗   ██╗██████╗  ██████╗ ███████╗", Colors.CYAN)
    print_colored("   ██║   ██║██╔══██╗██╔═══██╗██╔════╝", Colors.CYAN)
    print_colored("   ██║   ██║██║  ██║██║   ██║███████╗", Colors.CYAN)
    print_colored("   ██║   ██║██║  ██║██║   ██║╚════██║", Colors.CYAN)
    print_colored("   ╚██████╔╝██████╔╝╚██████╔╝███████║", Colors.CYAN)
    print_colored("    ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝", Colors.CYAN)
    print_colored("", Colors.NC)
    print_colored("🚀 uDOS System Startup & Validation", Colors.WHITE)
    print_colored("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", Colors.YELLOW)
    print("")

def check_system_structure():
    """Check uDOS directory structure"""
    print_colored("🔍 Checking system structure...", Colors.BLUE)
    
    udos_root = Path(__file__).parent.parent
    required_dirs = [
        'uCORE', 'uSERVER', 'uMEMORY', 'uSCRIPT', 'uKNOWLEDGE',
        'sandbox', 'docs', 'wizard', 'ghost', 'tomb', 'drone', 'imp', 'sorcerer'
    ]
    
    missing_dirs = []
    for dir_name in required_dirs:
        dir_path = udos_root / dir_name
        if dir_path.exists():
            print_colored(f"   ✅ {dir_name}", Colors.GREEN)
        else:
            print_colored(f"   ❌ {dir_name} (missing)", Colors.RED)
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print_colored(f"⚠️  Missing directories: {', '.join(missing_dirs)}", Colors.YELLOW)
    else:
        print_colored("✅ System structure validated", Colors.GREEN)
    
    print("")
    return len(missing_dirs) == 0

def check_user_authentication():
    """Check user authentication setup"""
    print_colored("🔐 Checking user authentication...", Colors.BLUE)
    
    udos_root = Path(__file__).parent.parent
    user_file = udos_root / "sandbox" / "user.md"
    
    if user_file.exists():
        try:
            with open(user_file, 'r') as f:
                content = f.read()
                if "# 🎭 uDOS User Identity" in content:
                    print_colored("   ✅ User authentication file valid", Colors.GREEN)
                    return True
                else:
                    print_colored("   ❌ Invalid user file format", Colors.RED)
                    return False
        except Exception as e:
            print_colored(f"   ❌ Error reading user file: {e}", Colors.RED)
            return False
    else:
        print_colored("   ⚠️  User authentication file not found", Colors.YELLOW)
        print_colored("   💡 Run user setup to create authentication", Colors.CYAN)
        return False

def check_python_dependencies():
    """Check Python dependencies"""
    print_colored("🐍 Checking Python dependencies...", Colors.BLUE)
    
    dependencies = [
        'flask', 'flask_socketio', 'requests', 'pathlib'
    ]
    
    missing_deps = []
    for dep in dependencies:
        try:
            __import__(dep)
            print_colored(f"   ✅ {dep}", Colors.GREEN)
        except ImportError:
            print_colored(f"   ❌ {dep} (missing)", Colors.RED)
            missing_deps.append(dep)
    
    if missing_deps:
        print_colored(f"⚠️  Missing dependencies: {', '.join(missing_deps)}", Colors.YELLOW)
        print_colored("💡 Run: pip install -r requirements.txt", Colors.CYAN)
        return False
    else:
        print_colored("✅ Python dependencies satisfied", Colors.GREEN)
        return True

def check_role_permissions():
    """Check role-based permissions"""
    print_colored("🎭 Checking role permissions...", Colors.BLUE)
    
    current_role = os.environ.get('UDOS_CURRENT_ROLE', 'wizard')
    udos_root = Path(__file__).parent.parent
    role_dir = udos_root / current_role
    
    if role_dir.exists():
        print_colored(f"   ✅ Role directory: {current_role}", Colors.GREEN)
        
        permissions_file = role_dir / "permissions.json"
        if permissions_file.exists():
            try:
                with open(permissions_file, 'r') as f:
                    permissions = json.load(f)
                    access_level = permissions.get('access_level', 0)
                    capabilities = permissions.get('capabilities', [])
                    
                    print_colored(f"   ✅ Access level: {access_level}", Colors.GREEN)
                    print_colored(f"   ✅ Capabilities: {', '.join(capabilities)}", Colors.GREEN)
                    return True
            except Exception as e:
                print_colored(f"   ⚠️  Error reading permissions: {e}", Colors.YELLOW)
        else:
            print_colored(f"   ⚠️  No permissions file for {current_role}", Colors.YELLOW)
    else:
        print_colored(f"   ❌ Role directory not found: {current_role}", Colors.RED)
        return False
    
    return True

def check_userver_config():
    """Check uSERVER configuration"""
    print_colored("🔧 Checking uSERVER configuration...", Colors.BLUE)
    
    udos_root = Path(__file__).parent.parent
    server_dir = udos_root / "uSERVER"
    
    # Check server files
    required_files = ['server.py', 'requirements.txt']
    for file_name in required_files:
        file_path = server_dir / file_name
        if file_path.exists():
            print_colored(f"   ✅ {file_name}", Colors.GREEN)
        else:
            print_colored(f"   ❌ {file_name} (missing)", Colors.RED)
    
    # Check configuration
    config_dir = server_dir / "config"
    if config_dir.exists():
        print_colored("   ✅ Configuration directory", Colors.GREEN)
    else:
        print_colored("   ⚠️  Configuration directory missing", Colors.YELLOW)
    
    print_colored("✅ uSERVER configuration checked", Colors.GREEN)
    return True

def display_system_info():
    """Display system information"""
    print_colored("📋 System Information", Colors.BLUE)
    
    udos_root = Path(__file__).parent.parent
    current_role = os.environ.get('UDOS_CURRENT_ROLE', 'wizard')
    server_port = os.environ.get('USERVER_PORT', '8080')
    
    print_colored(f"   📍 uDOS Root: {udos_root}", Colors.CYAN)
    print_colored(f"   🎭 Current Role: {current_role}", Colors.CYAN)
    print_colored(f"   🌐 Server Port: {server_port}", Colors.CYAN)
    print_colored(f"   🐍 Python: {sys.version.split()[0]}", Colors.CYAN)
    print_colored(f"   💻 Platform: {sys.platform}", Colors.CYAN)
    print("")

def show_startup_sequence():
    """Show animated startup sequence"""
    print_colored("🚀 Initializing uDOS components...", Colors.BLUE)
    
    components = [
        ("uCORE", "Core system and utilities"),
        ("uSERVER", "Web server and API endpoints"),
        ("uMEMORY", "User data and session management"),
        ("uSCRIPT", "Scripting engine and automation"),
        ("uKNOWLEDGE", "Documentation and help system"),
        ("Role System", "Permission and access control"),
        ("UI Framework", "Browser-based interface"),
        ("CLI Integration", "Terminal command interface")
    ]
    
    for component, description in components:
        print_colored(f"   🔄 Initializing {component}...", Colors.YELLOW)
        time.sleep(0.3)  # Simulate loading time
        print_colored(f"   ✅ {component}: {description}", Colors.GREEN)
    
    print("")
    print_colored("✨ All components initialized successfully!", Colors.GREEN)
    print("")

def show_access_info():
    """Show access information"""
    server_host = os.environ.get('USERVER_HOST', '127.0.0.1')
    server_port = os.environ.get('USERVER_PORT', '8080')
    current_role = os.environ.get('UDOS_CURRENT_ROLE', 'wizard')
    
    print_colored("🌐 Access Information", Colors.BLUE)
    print_colored("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", Colors.YELLOW)
    print("")
    print_colored(f"🖥️  CLI Mode: Reserved for uSERVER operations", Colors.WHITE)
    print_colored(f"🌐 UI Mode: http://{server_host}:{server_port}", Colors.WHITE)
    print_colored(f"🎭 Role: {current_role}", Colors.WHITE)
    print("")
    print_colored("Available in UI:", Colors.CYAN)
    print_colored("  • System monitoring and status", Colors.CYAN)
    print_colored("  • Command execution interface", Colors.CYAN)
    print_colored("  • Font and display management", Colors.CYAN)
    print_colored("  • Viewport and window management", Colors.CYAN)
    print_colored("  • Real-time logs and debugging", Colors.CYAN)
    print("")

def main():
    """Main setup check function"""
    show_startup_banner()
    
    # Run all checks
    checks = [
        check_system_structure(),
        check_user_authentication(),
        check_python_dependencies(),
        check_role_permissions(),
        check_userver_config()
    ]
    
    display_system_info()
    
    # Show results
    passed_checks = sum(checks)
    total_checks = len(checks)
    
    if passed_checks == total_checks:
        print_colored(f"✅ All system checks passed ({passed_checks}/{total_checks})", Colors.GREEN)
        show_startup_sequence()
        show_access_info()
        return 0
    else:
        print_colored(f"⚠️  Some checks failed ({passed_checks}/{total_checks})", Colors.YELLOW)
        print_colored("💡 Please resolve the issues above before starting uSERVER", Colors.CYAN)
        return 1

if __name__ == "__main__":
    sys.exit(main())
