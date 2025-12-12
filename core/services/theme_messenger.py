"""
Theme Messenger - Universal Theme-Aware I/O System

Loads theme message templates and provides formatted output for all
uDOS I/O operations with emoji, color, and vocabulary per theme.

Part of v1.2.22 - Self-Healing & Auto-Error-Awareness System
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class ThemeMessenger:
    """
    Universal message formatter using theme-specific templates.
    
    Provides consistent, theme-aware messaging for errors, success,
    warnings, prompts, and status messages across all command handlers.
    """
    
    # Fallback vocabulary maps for when theme doesn't define messages
    DEFAULT_VOCAB = {
        'galaxy': {
            'prefix': '🌌',
            'success_verb': 'TRANSMITTED',
            'error_verb': 'SIGNAL LOST',
            'warning_verb': 'ANOMALY',
            'status_verb': 'SCANNING',
        },
        'dungeon': {
            'prefix': '💀',
            'success_verb': 'ENCHANTED',
            'error_verb': 'CURSED',
            'warning_verb': 'HAUNTED',
            'status_verb': 'DIVINING',
        },
        'ranger': {
            'prefix': '🌲',
            'success_verb': 'TRACKED',
            'error_verb': 'TRAIL BLOCKED',
            'warning_verb': 'DANGER',
            'status_verb': 'SCOUTING',
        },
        'foundation': {
            'prefix': '📋',
            'success_verb': 'COMPLETED',
            'error_verb': 'ERROR',
            'warning_verb': 'WARNING',
            'status_verb': 'PROCESSING',
        },
        'minimal': {
            'prefix': '•',
            'success_verb': 'OK',
            'error_verb': 'ERROR',
            'warning_verb': 'WARN',
            'status_verb': 'INFO',
        },
        'retro': {
            'prefix': '█',
            'success_verb': 'EXEC',
            'error_verb': 'ABORT',
            'warning_verb': 'ALERT',
            'status_verb': 'PROC',
        },
        'cyberpunk': {
            'prefix': '▸',
            'success_verb': 'COMPILED',
            'error_verb': 'SEGFAULT',
            'warning_verb': 'BUFFER OVERFLOW',
            'status_verb': 'EXECUTING',
        }
    }
    
    def __init__(self, config):
        """
        Initialize theme messenger.
        
        Args:
            config: Config instance with get() and workspace_root
        """
        self.config = config
        self.current_theme = config.get('theme', 'foundation')
        self.messages = {}
        self.vocabulary = {}
        self.use_plaintext = self._detect_plaintext_mode()
        
        self._load_theme()
    
    def _detect_plaintext_mode(self) -> bool:
        """Detect if terminal supports color/emoji."""
        term = os.getenv('TERM', '')
        
        # Modern terminals support color
        modern_terms = ['xterm-256color', 'screen-256color', 'tmux-256color']
        if term in modern_terms:
            return False
        
        # Check for CI/CD environments
        if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
            return True
        
        # Default to color support
        return False
    
    def _load_theme(self):
        """Load theme messages from theme JSON file."""
        theme_file = Path(self.config.workspace_root) / "core" / "data" / "themes" / f"{self.current_theme}.json"
        
        if not theme_file.exists():
            # Fallback to foundation theme
            theme_file = Path(self.config.workspace_root) / "core" / "data" / "themes" / "foundation.json"
        
        try:
            with open(theme_file, 'r') as f:
                theme_data = json.load(f)
                self.messages = theme_data.get('messages', {})
                self.vocabulary = theme_data.get('TERMINOLOGY', {})
                
                # If no messages defined, use vocabulary
                if not self.messages and self.vocabulary:
                    self.messages = self.vocabulary
        except Exception:
            # Use default vocabulary
            self.vocabulary = self.DEFAULT_VOCAB.get(self.current_theme, self.DEFAULT_VOCAB['foundation'])
    
    def format_message(self, msg_type: str, key: str, **context) -> str:
        """
        Format message using theme templates.
        
        Args:
            msg_type: Message category (error, success, warning, prompt, status)
            key: Specific message key within category
            **context: Variables to interpolate into template
        
        Returns:
            Formatted message string
        
        Example:
            format_message('error', 'error_not_found', file='test.txt')
            → "💀 CURSED SPELL: File 'test.txt' not found"
        """
        # Build full message key
        full_key = f"{msg_type}_{key}" if not key.startswith(msg_type) else key
        
        # Try to get template
        template = self.messages.get(full_key)
        
        if not template:
            # Fallback to generic template
            template = self._generate_fallback(msg_type, key, context)
        
        # Handle plaintext mode
        if self.use_plaintext:
            template = self._strip_emoji(template)
        
        # Interpolate context variables
        try:
            return template.format(**context)
        except KeyError as e:
            # Missing variable, return with placeholder
            return template.replace(f"{{{e.args[0]}}}", f"<{e.args[0].upper()}>")
        except Exception:
            return template
    
    def _generate_fallback(self, msg_type: str, key: str, context: Dict[str, Any]) -> str:
        """Generate fallback message when template not defined."""
        vocab = self.vocabulary if self.vocabulary else self.DEFAULT_VOCAB.get(self.current_theme, {})
        prefix = vocab.get('prefix', '•')
        
        if msg_type == 'error':
            verb = vocab.get('error_verb', 'ERROR')
            message = context.get('message', context.get('error', 'Unknown error'))
            return f"{prefix} {verb}: {message}"
        
        elif msg_type == 'success':
            verb = vocab.get('success_verb', 'SUCCESS')
            action = context.get('action', 'Operation')
            return f"{prefix} {verb}: {action}"
        
        elif msg_type == 'warning':
            verb = vocab.get('warning_verb', 'WARNING')
            message = context.get('message', 'Warning')
            return f"{prefix} {verb}: {message}"
        
        elif msg_type == 'prompt':
            return f"{prefix} {context.get('message', 'Enter choice')}: "
        
        elif msg_type == 'status':
            verb = vocab.get('status_verb', 'STATUS')
            message = context.get('message', 'Processing')
            return f"{prefix} {verb}: {message}"
        
        else:
            return f"{prefix} {key}: {context.get('message', '')}"
    
    def _strip_emoji(self, text: str) -> str:
        """Remove emoji for plaintext terminals."""
        # Common emoji used in uDOS
        emoji_map = {
            '🌌': '[GALAXY]',
            '💀': '[DUNGEON]',
            '🌲': '[RANGER]',
            '📋': '[INFO]',
            '✅': '[OK]',
            '❌': '[ERROR]',
            '⚠️': '[WARN]',
            '🔧': '[TOOL]',
            '🔐': '[SECURE]',
            '✨': '[WIZARD]',
            '🐛': '[DEBUG]',
            '🧪': '[TEST]',
        }
        
        result = text
        for emoji, replacement in emoji_map.items():
            result = result.replace(emoji, replacement)
        
        return result
    
    def error(self, key: str, **context) -> str:
        """Shorthand for error messages."""
        return self.format_message('error', key, **context)
    
    def success(self, key: str, **context) -> str:
        """Shorthand for success messages."""
        return self.format_message('success', key, **context)
    
    def warning(self, key: str, **context) -> str:
        """Shorthand for warning messages."""
        return self.format_message('warning', key, **context)
    
    def prompt(self, key: str, **context) -> str:
        """Shorthand for prompt messages."""
        return self.format_message('prompt', key, **context)
    
    def status(self, key: str, **context) -> str:
        """Shorthand for status messages."""
        return self.format_message('status', key, **context)
    
    def reload_theme(self, theme_name: Optional[str] = None):
        """Reload theme (e.g., after theme change)."""
        if theme_name:
            self.current_theme = theme_name
            self.config.set('theme', theme_name)
        
        self._load_theme()
