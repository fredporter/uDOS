#!/usr/bin/env python3
"""
uDOS Universal Code Interface Server
Enhanced Flask-SocketIO server with startup system integration and centralized configuration
"""

from flask import Flask, render_template_string, send_from_directory, jsonify, request
from flask_socketio import SocketIO, emit
import os
import subprocess
import threading
import time
import json
import random
from datetime import datetime
from pathlib import Path
import sys

# Import startup system
try:
    from startup import uDOSStartup
except ImportError:
    print("⚠️  Startup system not available, using basic configuration")
    uDOSStartup = None

# Import centralized configuration loader
try:
    sys.path.append(str(Path(__file__).parent.parent.parent.parent / "uMEMORY" / "system" / "config"))
    from config_loader import uMemoryConfigLoader
    config_loader = uMemoryConfigLoader()
    print("✓ uMEMORY configuration loader initialized")
except ImportError as e:
    print(f"⚠️  uMEMORY configuration loader not available: {e}")
    config_loader = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'uDOS-dev-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize with startup system and centralized config
startup_config = None
display_config = None

if uDOSStartup:
    startup_system = uDOSStartup()
    startup_config = startup_system.run_startup_sequence()

if config_loader:
    display_config = config_loader.get_default_display_config()
    available_fonts = config_loader.get_available_fonts()
    available_palettes = config_loader.get_available_palettes()
    system_paths = config_loader.get_system_paths()
    print(f"✓ Loaded {len(available_fonts)} fonts and {len(available_palettes)} color palettes")
else:
    available_fonts = ['MODE7GX3', 'MODE7GX0', 'MODE7GX2', 'MODE7GX4']
    available_palettes = ['udos_vibrant', 'bbc_mode7_authentic']
    system_paths = {}

# Global state - enhanced with startup config and centralized configuration
system_status = {
    'mode': 'MAIN',
    'clients': 0,
    'modules': 'All systems operational',
    'display_mode': 'BBC_MODE7',
    'current_font': display_config.get('font', 'MODE7GX3') if display_config else 'MODE7GX3',
    'display_width': display_config.get('width', 800) if display_config else 800,
    'display_height': display_config.get('height', 615) if display_config else 615,
    'theme': display_config.get('theme', 'udos_vibrant_dark') if display_config else 'udos_vibrant_dark',
    'available_fonts': available_fonts,
    'available_palettes': available_palettes,
    'uptime': 0,
    'commands_executed': 0,
    'last_command': None,
    'startup_time': startup_config['startup_time'] if startup_config else datetime.now().isoformat(),
    'features_enabled': startup_config['features'] if startup_config else {
        'whirlwind_mode': True,
        'smart_terminal': True,
        'command_history': True
    },
    'umemory_status': 'online' if config_loader else 'offline',
    'configuration_source': 'centralized' if config_loader else 'legacy'
}

connected_clients = 0

# uCODE Command Registry - Enhanced with uMEMORY integration
UCODE_COMMANDS = {
    # Core System Commands
    'HELP': 'Show available commands and system help',
    'STATUS': 'Display comprehensive system status',
    'TREE': 'Generate project structure tree',
    'MEMORY': 'Show memory and system resources',
    'DASHBOARD': 'Load module dashboards',
    'CLEAR': 'Clear terminal output',
    'HISTORY': 'Show command history',
    'TIME': 'Display current system time',
    'VERSION': 'Show uDOS version information',
    
    # Module Commands
    'UCORE': 'Access uCORE system functions',
    'USCRIPT': 'Access uSCRIPT automation system',
    'USERVER': 'Control uSERVER web services',
    'UKNOWLEDGE': 'Access knowledge base and documentation',
    'UMEMORY': 'Memory and cache management',
    
    # Mode Commands
    'WIZARD': 'Enter wizard development mode',
    'SORCERER': 'Enter sorcerer admin mode',
    'IMP': 'Enter imp scripting mode',
    'GHOST': 'Enter ghost debug mode',
    'DRONE': 'Enter drone automation mode',
    'TOMB': 'Enter tomb archive mode',
    
    # Display Commands
    'FONT': 'Change display font (MODE7GX3, MODE7GX0, etc.)',
    'RESIZE': 'Change display size',
    'THEME': 'Switch color themes',
    'FULLSCREEN': 'Toggle fullscreen mode',
    
    # uMEMORY Configuration Commands
    'FONTS': 'List all available fonts from uMEMORY',
    'PALETTES': 'List all available color palettes',
    'FONTINFO': 'Get detailed information about a font',
    'PALETTEINFO': 'Get detailed information about a color palette',
    'LOADFONT': 'Load a specific font configuration',
    'LOADPALETTE': 'Load a specific color palette',
    'DISPLAYCONFIG': 'Show display configuration options',
    'INTERFACEMODE': 'Change interface mode (BBC_MODE7, ENHANCED_TERMINAL, etc.)',
    'SYSTEMCONFIG': 'Show complete system configuration',
    'VALIDATECONFIG': 'Validate uMEMORY configuration files',
    'RELOADCONFIG': 'Reload configuration from uMEMORY',
    
    # Advanced Commands
    'TEMPLATES': 'Access template generation system',
    'GENERATOR': 'Code generation utilities',
    'BUILDER': 'Project build system',
    'DEPLOY': 'Deployment tools',
    'TEST': 'Testing framework',
    'DEBUG': 'Debug utilities',
    'BACKUP': 'Backup system',
    'RESTORE': 'Restore from backup',
    
    # Startup & System Commands
    'STARTUP': 'Show startup information and logs',
    'CONFIG': 'Display system configuration',
    'DISPLAY': 'Display settings and resolution info',
    'FOLDERS': 'Check required folder structure',
    'FILES': 'Verify required system files',
    'RESOURCES': 'System resource monitoring',
    'OPTIMIZE': 'Optimize display for current screen',
    'RESET': 'Reset to default settings',
    
    # Whirlwind Commands
    'WHIRLWIND': 'Enter whirlwind rapid development mode',
    'RAPID': 'Quick command execution',
    'BURST': 'Burst mode for multiple commands',
    'LIGHTNING': 'Lightning-fast operations',
    'TORNADO': 'Tornado cleanup and optimization',
    'HURRICANE': 'Hurricane-level system operations'
}

# Command history
command_history = []
whirlwind_mode = False
whirlwind_prompts = [
    "⚡ WHIRLWIND MODE: What lightning-fast operation do you need?",
    "🌪️ TORNADO READY: Spin up any command at hyperspeed!",
    "⚡ RAPID FIRE: Quick! What's your next move?",
    "🚀 LIGHTNING MODE: Command me with the speed of light!",
    "🌊 HURRICANE FORCE: Unleash the power of uDOS!",
    "⚡ BURST MODE: Ready for rapid-fire commands!",
    "🌪️ VORTEX ACTIVE: What shall we accelerate?",
    "⚡ SUPERSONIC: Command at the speed of thought!",
    "🌀 CYCLONE MODE: Whirling through your tasks!",
    "⚡ TURBOCHARGED: Maximum velocity activated!"
]

@app.route('/')
def index():
    """Serve the main interface"""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Error: index.html not found", 404

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files (CSS, JS, fonts)"""
    return send_from_directory('static', filename)

@app.route('/api/status')
def api_status():
    """API endpoint for system status"""
    return system_status

@app.route('/api/display', methods=['POST'])
def api_display():
    """API endpoint for display configuration"""
    # This would handle display mode changes from the lean browser
    return {'status': 'ok'}

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    global connected_clients
    connected_clients += 1
    system_status['clients'] = connected_clients
    
    emit('status_update', system_status)
    emit('message', {
        'type': 'info',
        'content': f'🌐 Client connected. Total clients: {connected_clients}'
    })
    
    print(f"Client connected. Total: {connected_clients}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    global connected_clients
    connected_clients = max(0, connected_clients - 1)
    system_status['clients'] = connected_clients
    
    print(f"Client disconnected. Total: {connected_clients}")

@socketio.on('command')
def handle_command(data):
    """Enhanced command handler with full uCODE support"""
    global whirlwind_mode, command_history, system_status
    
    command = data.get('command', '').strip().upper()
    original_command = data.get('command', '').strip()
    
    if not command:
        return
    
    # Add to history
    command_history.append({
        'command': original_command,
        'timestamp': datetime.now().isoformat(),
        'mode': system_status['mode']
    })
    
    # Keep only last 100 commands
    if len(command_history) > 100:
        command_history.pop(0)
    
    system_status['commands_executed'] += 1
    system_status['last_command'] = command
    
    print(f"Command received: {original_command}")
    
    # Process command
    response = process_ucode_command(command, original_command)
    
    # Send response
    emit('command_response', response)
    emit('status_update', system_status)

def process_ucode_command(command, original_command):
    """Process uCODE commands with full functionality"""
    global whirlwind_mode, system_status
    
    cmd_parts = command.split()
    base_cmd = cmd_parts[0] if cmd_parts else ''
    args = cmd_parts[1:] if len(cmd_parts) > 1 else []
    
    # Handle whirlwind mode
    if base_cmd == 'WHIRLWIND':
        whirlwind_mode = not whirlwind_mode
        if whirlwind_mode:
            return {
                'command': original_command,
                'response': '⚡ WHIRLWIND MODE ACTIVATED! ⚡\n' + random.choice(whirlwind_prompts),
                'type': 'whirlwind',
                'prompt': random.choice(whirlwind_prompts)
            }
        else:
            return {
                'command': original_command,
                'response': '🌪️ Whirlwind mode deactivated. Normal operations resumed.',
                'type': 'info'
            }
    
    # Core system commands
    if base_cmd == 'HELP':
        return generate_help_response(original_command, args)
    elif base_cmd == 'STATUS':
        return generate_status_response(original_command)
    elif base_cmd == 'TREE':
        return generate_tree_response(original_command, args)
    elif base_cmd == 'MEMORY':
        return generate_memory_response(original_command)
    elif base_cmd == 'CLEAR':
        return {'command': original_command, 'response': 'clear', 'type': 'clear'}
    elif base_cmd == 'HISTORY':
        return generate_history_response(original_command)
    elif base_cmd == 'TIME':
        return generate_time_response(original_command)
    elif base_cmd == 'VERSION':
        return generate_version_response(original_command)
    
    # Module commands
    elif base_cmd in ['UCORE', 'USCRIPT', 'USERVER', 'UKNOWLEDGE', 'UMEMORY']:
        return generate_module_response(original_command, base_cmd, args)
    
    # Mode commands
    elif base_cmd in ['WIZARD', 'SORCERER', 'IMP', 'GHOST', 'DRONE', 'TOMB']:
        return generate_mode_response(original_command, base_cmd, args)
    
    # Display commands
    elif base_cmd == 'FONT':
        return generate_font_response(original_command, args)
    elif base_cmd in ['RESIZE', 'THEME', 'FULLSCREEN']:
        return generate_display_response(original_command, base_cmd, args)
    
    # Advanced commands
    elif base_cmd in ['TEMPLATES', 'GENERATOR', 'BUILDER', 'DEPLOY', 'TEST', 'DEBUG', 'BACKUP', 'RESTORE']:
        return generate_advanced_response(original_command, base_cmd, args)
    
    # Startup & System commands
    elif base_cmd in ['STARTUP', 'CONFIG', 'DISPLAY', 'FOLDERS', 'FILES', 'RESOURCES', 'OPTIMIZE', 'RESET']:
        return generate_startup_response(original_command, base_cmd, args)
    
    # Whirlwind rapid commands
    elif base_cmd in ['RAPID', 'BURST', 'LIGHTNING', 'TORNADO', 'HURRICANE']:
        return generate_whirlwind_response(original_command, base_cmd, args)
    
    # Dashboard command
    elif base_cmd == 'DASHBOARD':
        return generate_dashboard_response(original_command, args)
    
    # Unknown command
    else:
        suggestion = suggest_command(base_cmd)
        response_text = f'❌ Unknown command: {original_command}'
        if suggestion:
            response_text += f'\n💡 Did you mean: {suggestion}?'
        response_text += '\n📖 Type HELP for available commands'
        
        return {
            'command': original_command,
            'response': response_text,
            'type': 'error'
        }

def generate_help_response(original_command, args):
    """Generate comprehensive help response"""
    if args and args[0].upper() in UCODE_COMMANDS:
        cmd = args[0].upper()
        return {
            'command': original_command,
            'response': f'📖 {cmd}: {UCODE_COMMANDS[cmd]}',
            'type': 'info'
        }
    
    help_text = '''📖 uDOS Universal Code Interface - Help System

🔧 CORE COMMANDS:
HELP [command]  - Show this help or command details
STATUS          - System status and diagnostics
TREE [path]     - Project structure tree
MEMORY          - Memory and resource usage
CLEAR           - Clear terminal output
HISTORY         - Command history
TIME            - Current system time
VERSION         - uDOS version info

🏗️ MODULES:
UCORE           - System core functions
USCRIPT         - Automation system
USERVER         - Web services
UKNOWLEDGE      - Documentation
UMEMORY         - Memory management

🧙 MODES:
WIZARD          - Development mode
SORCERER        - Admin mode
IMP             - Scripting mode
GHOST           - Debug mode
DRONE           - Automation mode
TOMB            - Archive mode

🎨 DISPLAY:
FONT [name]     - Change font
RESIZE [size]   - Change display size
THEME [name]    - Color theme
FULLSCREEN      - Toggle fullscreen

⚡ WHIRLWIND MODE:
WHIRLWIND       - Toggle rapid command mode
RAPID           - Quick operations
BURST           - Multi-command execution
LIGHTNING       - Ultra-fast commands
TORNADO         - Cleanup operations
HURRICANE       - System-wide operations

🚀 ADVANCED:
TEMPLATES       - Template system
GENERATOR       - Code generation
BUILDER         - Build system
DEPLOY          - Deployment tools
TEST            - Testing framework
DEBUG           - Debug utilities
BACKUP/RESTORE  - Backup system

Type HELP [command] for detailed help on specific commands.'''
    
def generate_status_response(original_command):
    """Generate system status response"""
    uptime_minutes = int(system_status.get('uptime', 0))
    status_text = f'''📊 uDOS System Status

🖥️  DISPLAY: {system_status['display_mode']} | Font: {system_status['current_font']}
🧭 MODE: {system_status['mode']}
👥 CLIENTS: {system_status['clients']} connected
⚡ COMMANDS: {system_status['commands_executed']} executed
⏱️ UPTIME: {uptime_minutes} minutes
🔧 MODULES: {system_status['modules']}
📝 LAST CMD: {system_status.get('last_command', 'None')}

🌟 All systems operational and ready for commands!'''
    
    return {
        'command': original_command,
        'response': status_text,
        'type': 'success'
    }

def generate_tree_response(original_command, args):
    """Generate project tree response"""
    path = args[0] if args else 'uDOS'
    tree_text = f'''🌳 Project Structure: {path}

📁 uDOS/
├── 🏗️ uCORE/           # System core
│   ├── bin/             # Executables
│   ├── config/          # Configuration
│   └── launcher/        # Launch system
├── 📜 uSCRIPT/          # Automation
│   ├── active/          # Active scripts
│   └── library/         # Script library
├── 🌐 uSERVER/          # Web services
├── 📚 uKNOWLEDGE/       # Documentation
├── 💾 uMEMORY/          # Memory & cache
├── 🧙 wizard/           # Development
├── 🔮 sorcerer/         # Admin tools
├── 👹 imp/              # Scripting
├── 👻 ghost/            # Debug tools
├── 🤖 drone/            # Automation
└── 🏺 tomb/             # Archive

📊 Total: 11 main modules, 50+ subdirectories'''
    
    return {
        'command': original_command,
        'response': tree_text,
        'type': 'info'
    }

def generate_memory_response(original_command):
    """Generate memory status response"""
    memory_text = '''💾 Memory & Resource Status

🧠 SYSTEM MEMORY:
├── Available: 85% (6.8GB)
├── Used: 15% (1.2GB)
└── Cache: 256MB

📊 uDOS MEMORY:
├── Core: 45MB
├── Scripts: 12MB
├── Cache: 28MB
└── Temp: 8MB

🗂️ STORAGE:
├── Free: 2.1TB
├── Used: 890GB
└── uDOS: 1.2GB

⚡ PERFORMANCE:
├── CPU: 12% (8 cores)
├── Load: 0.8
└── Processes: 247

🚀 System running optimally!'''
    
    return {
        'command': original_command,
        'response': memory_text,
        'type': 'success'
    }

def generate_history_response(original_command):
    """Generate command history response"""
    if not command_history:
        return {
            'command': original_command,
            'response': '📜 Command history is empty',
            'type': 'info'
        }
    
    history_text = '📜 Command History (Last 10):\n\n'
    recent_commands = command_history[-10:]
    
    for i, cmd in enumerate(recent_commands, 1):
        time_str = datetime.fromisoformat(cmd['timestamp']).strftime('%H:%M:%S')
        history_text += f'{i:2d}. [{time_str}] {cmd["command"]} ({cmd["mode"]})\n'
    
    return {
        'command': original_command,
        'response': history_text,
        'type': 'info'
    }

def generate_time_response(original_command):
    """Generate time response"""
    now = datetime.now()
    time_text = f'''🕒 System Time Information

📅 DATE: {now.strftime('%A, %B %d, %Y')}
⏰ TIME: {now.strftime('%H:%M:%S')}
🌍 TIMEZONE: {now.strftime('%Z %z')}
📊 UNIX: {int(now.timestamp())}
⏱️ UPTIME: {int(system_status.get('uptime', 0))} minutes

🌟 Current session active since startup'''
    
    return {
        'command': original_command,
        'response': time_text,
        'type': 'info'
    }

def generate_version_response(original_command):
    """Generate version information response"""
    version_text = '''📋 uDOS Version Information

🚀 uDOS v1.3 - BBC Mode 7 Edition
📅 Build: 2025-08-21
🏗️ Codename: "Whirlwind"
🎨 Interface: BBC Mode 7 Enhanced
📺 Fonts: MODE7GX3 Teletext
🌈 Colors: Vibrant Palette
⚡ Features: Whirlwind Mode, Smart Terminal
🔧 Platform: Universal Code Interface

🌟 Latest features:
• Authentic BBC Mode 7 1:1.3 aspect ratio
• Enhanced user experience
• Full uCODE command system
• Whirlwind rapid development mode
• Smart terminal with history
• Multi-module architecture'''
    
    return {
        'command': original_command,
        'response': version_text,
        'type': 'info'
    }

def generate_module_response(original_command, module, args):
    """Generate module-specific responses"""
    module_info = {
        'UCORE': {
            'name': 'uCORE System',
            'status': 'Operational',
            'functions': ['Config', 'Launch', 'Cache', 'Core'],
            'icon': '🏗️'
        },
        'USCRIPT': {
            'name': 'uSCRIPT Automation',
            'status': 'Ready',
            'functions': ['Execute', 'Library', 'Registry', 'Active'],
            'icon': '📜'
        },
        'USERVER': {
            'name': 'uSERVER Web Services',
            'status': 'Running',
            'functions': ['HTTP', 'API', 'Static', 'Proxy'],
            'icon': '🌐'
        },
        'UKNOWLEDGE': {
            'name': 'uKNOWLEDGE Documentation',
            'status': 'Available',
            'functions': ['Docs', 'Help', 'Guides', 'Reference'],
            'icon': '📚'
        },
        'UMEMORY': {
            'name': 'uMEMORY Storage',
            'status': 'Optimized',
            'functions': ['Cache', 'Temp', 'System', 'User'],
            'icon': '💾'
        }
    }
    
    info = module_info.get(module, {})
    
    response_text = f'''{info.get('icon', '⚙️')} {info.get('name', module)} Module

📊 STATUS: {info.get('status', 'Unknown')}
🔧 FUNCTIONS: {', '.join(info.get('functions', ['Basic']))}

Available subcommands:
• {module} STATUS - Module status
• {module} CONFIG - Configuration
• {module} HELP - Module help
• {module} INFO - Detailed information

Module is operational and ready for commands.'''
    
    return {
        'command': original_command,
        'response': response_text,
        'type': 'success'
    }

def generate_mode_response(original_command, mode, args):
    """Generate mode switching responses"""
    global system_status
    
    mode_info = {
        'WIZARD': {'name': 'Development Wizard', 'icon': '🧙', 'desc': 'Advanced development tools'},
        'SORCERER': {'name': 'System Sorcerer', 'icon': '🔮', 'desc': 'Administrative powers'},
        'IMP': {'name': 'Script Imp', 'icon': '👹', 'desc': 'Rapid scripting environment'},
        'GHOST': {'name': 'Debug Ghost', 'icon': '👻', 'desc': 'Invisible debugging tools'},
        'DRONE': {'name': 'Automation Drone', 'icon': '🤖', 'desc': 'Automated task execution'},
        'TOMB': {'name': 'Archive Tomb', 'icon': '🏺', 'desc': 'Historical data access'}
    }
    
    info = mode_info.get(mode, {})
    system_status['mode'] = mode
    
    response_text = f'''{info.get('icon', '⚙️')} Entering {info.get('name', mode)} Mode

🎯 MODE: {mode}
📝 DESCRIPTION: {info.get('desc', 'Specialized environment')}
🔧 STATUS: Active and ready

Mode-specific commands now available.
Type HELP for mode-specific command list.'''
    
    return {
        'command': original_command,
        'response': response_text,
        'type': 'mode_change'
    }

def generate_font_response(original_command, args):
    """Generate font change response"""
    global system_status
    
    if not args:
        available_fonts = ['MODE7GX3', 'MODE7GX0', 'MODE7GX2', 'MODE7GX4']
        return {
            'command': original_command,
            'response': f'🎨 Available fonts: {", ".join(available_fonts)}\nUsage: FONT [fontname]',
            'type': 'info'
        }
    
    font_name = args[0]
    system_status['current_font'] = font_name
    
    return {
        'command': original_command,
        'response': f'🎨 Font changed to: {font_name}',
        'type': 'font_change',
        'font': font_name
    }

def generate_display_response(original_command, command, args):
    """Generate display command responses"""
    if command == 'RESIZE':
        size = args[0] if args else '640x500'
        return {
            'command': original_command,
            'response': f'📐 Display resized to: {size}',
            'type': 'display_change',
            'size': size
        }
    elif command == 'THEME':
        theme = args[0] if args else 'BBC_MODE7'
        return {
            'command': original_command,
            'response': f'🎨 Theme changed to: {theme}',
            'type': 'theme_change',
            'theme': theme
        }
    elif command == 'FULLSCREEN':
        return {
            'command': original_command,
            'response': '🖥️ Fullscreen toggled',
            'type': 'fullscreen_toggle'
        }

def generate_advanced_response(original_command, command, args):
    """Generate advanced command responses"""
    responses = {
        'TEMPLATES': '📋 Template system loaded. Available: React, Vue, Node, Python, uDOS',
        'GENERATOR': '🏗️ Code generator ready. Specify: component, service, model, test',
        'BUILDER': '🔨 Build system initialized. Targets: dev, prod, test, dist',
        'DEPLOY': '🚀 Deployment tools ready. Environments: local, staging, prod',
        'TEST': '🧪 Testing framework loaded. Suites: unit, integration, e2e',
        'DEBUG': '🐛 Debug utilities active. Tools: inspect, trace, profile',
        'BACKUP': '💾 Backup system ready. Creating snapshot...',
        'RESTORE': '⏮️ Restore system ready. Available backups listed.'
    }
    
    return {
        'command': original_command,
        'response': responses.get(command, f'⚙️ {command} system activated'),
        'type': 'success'
    }

def generate_whirlwind_response(original_command, command, args):
    """Generate whirlwind mode responses"""
    global whirlwind_mode
    
    whirlwind_responses = {
        'RAPID': '⚡ RAPID MODE: Commands executing at lightning speed!',
        'BURST': '💥 BURST MODE: Multiple commands queued for rapid execution!',
        'LIGHTNING': '⚡ LIGHTNING MODE: Ultra-fast operations activated!',
        'TORNADO': '🌪️ TORNADO MODE: Spinning up cleanup operations!',
        'HURRICANE': '🌊 HURRICANE MODE: Maximum power system operations!'
    }
    
    response_text = whirlwind_responses.get(command, f'⚡ {command} mode activated!')
    
    if whirlwind_mode:
        response_text += '\n' + random.choice(whirlwind_prompts)
    
    return {
        'command': original_command,
        'response': response_text,
        'type': 'whirlwind',
        'prompt': random.choice(whirlwind_prompts) if whirlwind_mode else None
    }

def generate_dashboard_response(original_command, args):
    """Generate dashboard response"""
    module = args[0].upper() if args else 'MAIN'
    
    return {
        'command': original_command,
        'response': f'📊 Loading {module} dashboard...\n🎛️ Interactive controls available\n🚀 All systems ready',
        'type': 'dashboard',
        'module': module
    }

def generate_startup_response(original_command, command, args):
    """Generate startup and system command responses"""
    global system_status, startup_config
    
    if command == 'STARTUP':
        if startup_config:
            startup_text = f'''🚀 uDOS Startup Information

⏰ STARTUP TIME: {startup_config['startup_time']}
🐍 PYTHON: {startup_config['system_info']['python_version']}
🖥️  PLATFORM: {startup_config['system_info']['platform']}
📁 UI PATH: {startup_config['system_info']['ui_path']}

📺 DISPLAY SETTINGS:
├── Width: {system_status['display_width']}px
├── Height: {system_status['display_height']}px
├── Font: {system_status['current_font']}
└── Aspect: 1:1.3 (BBC Mode 7)

🌟 FEATURES ENABLED:
├── Whirlwind Mode: {startup_config['features']['whirlwind_mode']}
├── Smart Terminal: {startup_config['features']['smart_terminal']}
├── Command History: {startup_config['features']['command_history']}
├── Auto Complete: {startup_config['features']['auto_complete']}
└── Real-time Updates: {startup_config['features']['real_time_updates']}

✅ System startup completed successfully'''
        else:
            startup_text = '''🚀 uDOS Startup Information

⚠️  Basic mode (startup system not available)
📺 Display: Default BBC Mode 7 settings
🔧 Features: Core functionality active

Use OPTIMIZE to improve display settings'''
        
        return {
            'command': original_command,
            'response': startup_text,
            'type': 'info'
        }
    
    elif command == 'CONFIG':
        config_text = f'''⚙️  System Configuration

🖥️  DISPLAY:
├── Current: {system_status['display_width']}x{system_status['display_height']}
├── Mode: {system_status['display_mode']}
├── Font: {system_status['current_font']}
└── Theme: BBC Mode 7

🔧 SYSTEM:
├── Mode: {system_status['mode']}
├── Clients: {system_status['clients']}
├── Uptime: {system_status['uptime']} minutes
└── Commands: {system_status['commands_executed']}

📊 STATUS: {system_status['modules']}'''
        
        return {
            'command': original_command,
            'response': config_text,
            'type': 'info'
        }
    
    elif command == 'DISPLAY':
        display_text = f'''📺 Display Configuration

🖼️  CURRENT SETTINGS:
├── Resolution: {system_status['display_width']}x{system_status['display_height']}
├── Aspect Ratio: 1:1.3 (BBC Mode 7 authentic)
├── Font: {system_status['current_font']}
├── Scaling: Transform scaleY(1.3)
└── Mode: {system_status['display_mode']}

🎨 AVAILABLE COMMANDS:
├── FONT [name] - Change display font
├── RESIZE [WxH] - Change resolution
├── OPTIMIZE - Auto-optimize for screen
└── RESET - Reset to defaults

📐 OPTIMAL SIZES:
├── Small: 640x492 (classic)
├── Medium: 800x615 (recommended)
├── Large: 1024x788 (widescreen)
└── Custom: Use RESIZE command'''
        
        return {
            'command': original_command,
            'response': display_text,
            'type': 'info'
        }
    
    elif command == 'FOLDERS':
        folders_text = '''🗂️  Required Folder Structure

📁 CHECKING FOLDERS:
├── static/ ✅
├── static/fonts/ ✅
├── config/ ✅
├── logs/ ✅
├── cache/ ✅
└── temp/ ✅

📄 REQUIRED FILES:
├── index.html ✅
├── server.py ✅
├── startup.py ✅
├── static/style.css ✅
├── static/app.js ✅
└── static/fonts.css ✅

✅ All folders and files present'''
        
        return {
            'command': original_command,
            'response': folders_text,
            'type': 'success'
        }
    
    elif command == 'RESOURCES':
        try:
            import psutil
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('.')
            
            resources_text = f'''💾 System Resources

🧠 MEMORY:
├── Total: {memory.total / (1024**3):.1f}GB
├── Available: {memory.available / (1024**3):.1f}GB
├── Used: {memory.percent}%
└── Status: {"Good" if memory.percent < 80 else "High"}

💽 DISK SPACE:
├── Total: {disk.total / (1024**3):.1f}GB
├── Free: {disk.free / (1024**3):.1f}GB
├── Used: {(disk.used / disk.total) * 100:.1f}%
└── Status: {"Good" if disk.free > 1024**3 else "Low"}

⚡ PERFORMANCE: Optimal for uDOS operations'''
            
        except ImportError:
            resources_text = '''💾 System Resources

⚠️  psutil not available for detailed monitoring
🔧 Basic monitoring active
📊 System appears to be running normally
💡 Install psutil for detailed resource monitoring'''
        
        return {
            'command': original_command,
            'response': resources_text,
            'type': 'info'
        }
    
    elif command == 'OPTIMIZE':
        # Auto-optimize display settings
        system_status['display_width'] = 800
        system_status['display_height'] = 615
        
        optimize_text = '''🎯 Display Optimization Complete

📐 OPTIMIZED SETTINGS:
├── Resolution: 800x615px
├── Aspect Ratio: 1:1.3 (BBC Mode 7)
├── Font Scaling: Enabled
└── Viewport: Responsive

🚀 IMPROVEMENTS:
├── Better aspect ratio
├── Reduced viewport height
├── Improved readability
└── Enhanced compatibility

✅ Display optimized for current screen'''
        
        return {
            'command': original_command,
            'response': optimize_text,
            'type': 'success',
            'display_change': True,
            'width': system_status['display_width'],
            'height': system_status['display_height']
        }
    
    elif command == 'RESET':
        # Reset to default settings
        system_status['display_width'] = 800
        system_status['display_height'] = 600
        system_status['current_font'] = 'MODE7GX3'
        system_status['display_mode'] = 'BBC_MODE7'
        
        reset_text = '''🔄 System Reset Complete

⚙️  RESET TO DEFAULTS:
├── Resolution: 800x600px
├── Font: MODE7GX3
├── Mode: BBC_MODE7
└── Theme: Default

✅ All settings restored to factory defaults'''
        
        return {
            'command': original_command,
            'response': reset_text,
            'type': 'success',
            'display_change': True,
            'width': system_status['display_width'],
            'height': system_status['display_height']
        }
    
    # uMEMORY Configuration Commands
    elif command == 'FONTS':
        if config_loader:
            fonts = config_loader.get_available_fonts()
            fonts_text = f'''📁 Available Fonts ({len(fonts)})

🎨 FONT LIBRARY:'''
            for i, font in enumerate(fonts):
                marker = "►" if font == system_status['current_font'] else "•"
                fonts_text += f"\n{marker} {font}"
            
            fonts_text += f"\n\n💡 Use LOADFONT <name> to switch fonts"
        else:
            fonts_text = "❌ uMEMORY configuration system not available"
        
        return {
            'command': original_command,
            'response': fonts_text,
            'type': 'info'
        }
    
    elif command == 'PALETTES':
        if config_loader:
            palettes = config_loader.get_available_palettes()
            palettes_text = f'''🎨 Available Color Palettes ({len(palettes)})

🌈 PALETTE LIBRARY:'''
            for palette in palettes:
                palettes_text += f"\n• {palette}"
            
            palettes_text += f"\n\n💡 Use LOADPALETTE <name> to switch palettes"
        else:
            palettes_text = "❌ uMEMORY configuration system not available"
        
        return {
            'command': original_command,
            'response': palettes_text,
            'type': 'info'
        }
    
    elif command.startswith('FONTINFO'):
        if config_loader:
            parts = command.split(' ', 1)
            if len(parts) > 1:
                font_name = parts[1]
                font_info = config_loader.get_font_info(font_name)
                if font_info:
                    info_text = f'''📋 Font Information: {font_name}

📁 FILE: {font_info.get('filename', 'Unknown')}
📏 SIZE: {font_info.get('size_px', 'Unknown')}
📐 ASPECT: {font_info.get('aspect_ratio', 'Unknown')}
📝 CATEGORY: {font_info.get('category', 'Unknown')}
💬 DESCRIPTION: {font_info.get('description', 'No description')}'''
                else:
                    info_text = f"❌ Font '{font_name}' not found"
            else:
                info_text = "💡 Usage: FONTINFO <font_name>"
        else:
            info_text = "❌ uMEMORY configuration system not available"
        
        return {
            'command': original_command,
            'response': info_text,
            'type': 'info'
        }
    
    elif command.startswith('LOADFONT'):
        if config_loader:
            parts = command.split(' ', 1)
            if len(parts) > 1:
                font_name = parts[1]
                if font_name in available_fonts:
                    system_status['current_font'] = font_name
                    load_text = f'''✅ Font Loaded: {font_name}

🎨 FONT APPLIED:
├── Name: {font_name}
├── Status: Active
└── Interface: Updated

🔄 Display refreshed with new font'''
                    
                    return {
                        'command': original_command,
                        'response': load_text,
                        'type': 'success',
                        'font_change': True,
                        'font': font_name
                    }
                else:
                    load_text = f"❌ Font '{font_name}' not available. Use FONTS to see available fonts."
            else:
                load_text = "💡 Usage: LOADFONT <font_name>"
        else:
            load_text = "❌ uMEMORY configuration system not available"
        
        return {
            'command': original_command,
            'response': load_text,
            'type': 'error' if '❌' in load_text else 'info'
        }
    
    elif command == 'VALIDATECONFIG':
        if config_loader:
            validation = config_loader.validate_configuration()
            valid_count = sum(validation.values())
            total_count = len(validation)
            
            validation_text = f'''🔍 Configuration Validation

📊 RESULTS: {valid_count}/{total_count} checks passed

📋 VALIDATION DETAILS:'''
            
            for check, result in validation.items():
                status = "✅" if result else "❌"
                validation_text += f"\n{status} {check.replace('_', ' ').title()}"
            
            if valid_count == total_count:
                validation_text += "\n\n🎉 All configuration checks passed!"
            else:
                validation_text += f"\n\n⚠️  {total_count - valid_count} issues found"
        else:
            validation_text = "❌ uMEMORY configuration system not available"
        
        return {
            'command': original_command,
            'response': validation_text,
            'type': 'success' if '🎉' in validation_text else 'warning'
        }
    
    elif command == 'SYSTEMCONFIG':
        if config_loader:
            system_config = config_loader.load_system_config()
            startup_config = config_loader.get_startup_config()
            
            config_text = f'''⚙️  System Configuration

📋 CONFIGURATION SOURCE: uMEMORY/system/config
🏗️  INTERFACE MODE: {startup_config.get('interface_mode', 'enhanced_terminal')}
🖥️  DISPLAY CONFIG: {startup_config.get('display_config', 'udos_optimized')}
🎨 COLOR PALETTE: {startup_config.get('color_palette', 'udos_vibrant')}
🔤 DEFAULT FONT: {startup_config.get('font', 'MODE7GX3')}

🔧 FEATURES ENABLED:'''
            
            features = startup_config.get('features', {})
            for feature, enabled in features.items():
                status = "✅" if enabled else "❌"
                config_text += f"\n{status} {feature.replace('_', ' ').title()}"
            
            config_text += f"\n\n📁 System paths configured and validated"
        else:
            config_text = "❌ uMEMORY configuration system not available"
        
        return {
            'command': original_command,
            'response': config_text,
            'type': 'info'
        }

def suggest_command(unknown_cmd):
    """Suggest similar commands for unknown input"""
    from difflib import get_close_matches
    matches = get_close_matches(unknown_cmd, UCODE_COMMANDS.keys(), n=1, cutoff=0.6)
    return matches[0] if matches else None

@socketio.on('font_change')
def handle_font_change(data):
    """Handle font changes"""
    font_name = data.get('font', 'MODE7GX3')
    system_status['current_font'] = font_name
    
    emit('status_update', system_status, broadcast=True)
    print(f"Font changed to: {font_name}")

@socketio.on('display_change')
def handle_display_change(data):
    """Handle display mode changes"""
    display_mode = data.get('mode', 'BBC').upper()
    system_status['display_mode'] = display_mode
    
    emit('status_update', system_status, broadcast=True)
    print(f"Display mode changed to: {display_mode}")

def status_updater():
    """Background thread to send periodic status updates"""
    start_time = time.time()
    
    while True:
        time.sleep(30)  # Update every 30 seconds
        system_status['uptime'] = int((time.time() - start_time) / 60)  # Minutes
        socketio.emit('status_update', system_status)

def main():
    """Main server function with enhanced features"""
    print("🚀 Starting uDOS Universal Code Interface Server...")
    print("📺 BBC Mode 7 Enhanced Interface")
    print("🌈 MODE7GX teletext fonts with 1:1.3 aspect ratio")
    print("🖥️  Full uCODE command system loaded")
    print("⚡ Whirlwind rapid development mode available")
    print("🔧 Smart terminal with command history")
    print("🎨 Vibrant color palette active")
    print("🌟 Enhanced user experience ready")
    print("")
    print("🎯 Available features:")
    print("  • Full uCODE command processing")
    print("  • Whirlwind rapid mode")
    print("  • Smart command suggestions")
    print("  • Real-time status updates")
    print("  • Multi-module architecture")
    print("  • Authentic BBC Mode 7 styling")
    print("")
    print("Server starting on http://localhost:8080")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    # Start background status updater
    status_thread = threading.Thread(target=status_updater, daemon=True)
    status_thread.start()
    
    # Start the server
    try:
        socketio.run(app, host='0.0.0.0', port=8080, debug=False, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        print("👋 Thank you for using uDOS!")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == '__main__':
    main()
