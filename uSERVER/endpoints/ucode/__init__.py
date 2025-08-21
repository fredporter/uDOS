"""
uCODE REST API endpoints
Provides REST and WebSocket endpoints for the browser-based uDOS interface
"""

from flask import Blueprint, jsonify, request
from flask_socketio import emit
import os
import subprocess
import json
from pathlib import Path

ucode_bp = Blueprint('ucode', __name__, url_prefix='/api/ucode')

@ucode_bp.route('/execute', methods=['POST'])
def execute_command():
    """Execute uDOS command via REST API"""
    data = request.get_json()
    command = data.get('command', '')
    
    # Process the command (integrate with uCORE later)
    result = process_ucode_command(command)
    
    return jsonify(result)

@ucode_bp.route('/modules', methods=['GET'])
def list_modules():
    """List available uDOS modules"""
    udos_root = Path(__file__).parent.parent.parent.parent
    
    modules = []
    module_dirs = ['uCORE', 'uSERVER', 'uSCRIPT', 'uMEMORY', 'imp', 'ghost', 'sorcerer', 'tomb']
    
    for module_dir in module_dirs:
        module_path = udos_root / module_dir
        if module_path.exists():
            modules.append({
                'name': module_dir,
                'path': str(module_path),
                'status': 'available'
            })
    
    return jsonify({'modules': modules})

@ucode_bp.route('/files', methods=['GET'])
def list_files():
    """List files in uDOS directory"""
    path = request.args.get('path', '')
    udos_root = Path(__file__).parent.parent.parent.parent
    
    if path:
        target_path = udos_root / path
    else:
        target_path = udos_root
    
    try:
        if target_path.exists() and target_path.is_dir():
            files = []
            for item in sorted(target_path.iterdir()):
                files.append({
                    'name': item.name,
                    'type': 'directory' if item.is_dir() else 'file',
                    'path': str(item.relative_to(udos_root))
                })
            return jsonify({'files': files, 'current_path': str(target_path.relative_to(udos_root))})
        else:
            return jsonify({'error': 'Path not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ucode_bp.route('/file/<path:filepath>', methods=['GET'])
def get_file_content(filepath):
    """Get content of a specific file"""
    udos_root = Path(__file__).parent.parent.parent.parent
    file_path = udos_root / filepath
    
    try:
        if file_path.exists() and file_path.is_file():
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return jsonify({
                'content': content,
                'path': filepath,
                'size': file_path.stat().st_size
            })
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def process_ucode_command(command):
    """Process uCODE command - to be integrated with uCORE"""
    command = command.strip()
    
    if command.startswith('help'):
        return {
            'output': '''🌈 uCODE Rainbow Commands:
help                 - Show this help
status              - System status  
modules             - List uDOS modules
rainbow             - Activate rainbow block graphics
whirlwind           - Engage whirlwind prompt system
ascii               - Display ASCII art
mode <MODE>         - Change prompt mode (DEV, USER, ADMIN, GHOST, etc.)
files [path]        - List files
cat <file>          - Show file content
ls [path]           - List directory
cd <path>           - Change directory
clear               - Clear terminal
version             - Show uDOS version

🎨 Visual Commands:
rainbow             - Enable prismatic visual effects
whirlwind           - Dynamic prompt rotation
ascii               - Random ASCII art display
fonts               - Show font information
font <name>         - Change font (primary, terminal, display, retro)
font effects        - Toggle font effects
font reset          - Reset to default font
theme <name>        - Change theme (dark, light, mono, rainbow)
theme info          - Show theme information
mode RAINBOW        - Rainbow prompt mode
mode GHOST          - Spectral prompt mode
mode SORCERER       - Magical prompt mode''',
            'success': True
        }
    
    elif command.startswith('status'):
        return {
            'output': 'uDOS Status: Running in DEV mode via Browser UI\nInterface: Omni-device uCODE Window',
            'success': True
        }
    
    elif command.startswith('version'):
        return {
            'output': 'uDOS v1.3 - Universal Development Operating System\nOmni-device uCODE Window v1.0',
            'success': True
        }
    
    elif command.startswith('clear'):
        return {
            'output': '\033[2J\033[H',  # ANSI clear screen
            'success': True,
            'clear': True
        }
    
    elif command.startswith('modules'):
        modules = [
            '📦 uCORE - Core system functions',
            '🌐 uSERVER - Web server & API',
            '📜 uSCRIPT - Script execution engine', 
            '🧠 uMEMORY - Memory management',
            '👻 ghost - Ethereal error handling',
            '🔮 sorcerer - Advanced magic tools',
            '😈 imp - Script editing & templates',
            '⚰️ tomb - Archive & backup manager',
            '🚁 drone - Task automation',
            '🧙‍♂️ wizard - Development framework',
            '🗑️ trash - Deprecated components',
            '📖 uKNOWLEDGE - Knowledge base'
        ]
        return {
            'output': '🌈 Available uDOS modules:\n' + '\n'.join(f'  {mod}' for mod in modules),
            'success': True
        }
    
    elif command.startswith('files') or command.startswith('ls'):
        # Simple file listing
        try:
            udos_root = Path(__file__).parent.parent.parent.parent
            parts = command.split()
            if len(parts) > 1:
                path = udos_root / parts[1]
            else:
                path = udos_root
                
            if path.exists() and path.is_dir():
                items = []
                for item in sorted(path.iterdir()):
                    icon = '📁' if item.is_dir() else '📄'
                    items.append(f'  {icon} {item.name}')
                return {
                    'output': f'Contents of {path.name}:\n' + '\n'.join(items),
                    'success': True
                }
            else:
                return {
                    'output': f'Directory not found: {parts[1] if len(parts) > 1 else ""}',
                    'success': False
                }
        except Exception as e:
            return {
                'output': f'Error listing files: {str(e)}',
                'success': False
            }
    
    elif command.startswith('cat '):
        # Show file content
        try:
            udos_root = Path(__file__).parent.parent.parent.parent
            filename = command[4:].strip()
            file_path = udos_root / filename
            
            if file_path.exists() and file_path.is_file():
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if len(content) > 2000:  # Limit output
                        content = content[:2000] + '\n... (truncated)'
                return {
                    'output': f'Content of {filename}:\n{content}',
                    'success': True
                }
            else:
                return {
                    'output': f'File not found: {filename}',
                    'success': False
                }
        except Exception as e:
            return {
                'output': f'Error reading file: {str(e)}',
                'success': False
            }
    
    else:
        return {
            'output': f'Unknown command: {command}\nType "help" for available commands.',
            'success': False
        }
