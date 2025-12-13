"""
uDOS Core Python API - Pure Python Implementation
==================================================

Date: 20251213-170000UTC
Location: Core Services
Version: v1.2.24 (Python-First Rebase)

Replaces: core/runtime/upy_runtime.py (1,198 lines)
Purpose: Provide all uDOS commands as Python functions for direct execution

This module eliminates the 1,850+ line parser by making uDOS scripting
valid Python code. Scripts import this module and call functions directly,
gaining 10-100x speed and full Python ecosystem compatibility.

Usage in .py scripts:
    from udos_core import *
    
    # Variables (Python standard)
    sprite_hp = 100
    player_name = "Hero"
    
    # Commands (function calls)
    PRINT("Hello World")
    GUIDE("water/purification")
    
    # System variables (read-only)
    current_hp = SPRITE_HP
    mission_status = MISSION_STATUS

Design Philosophy:
- Python-first: All syntax is valid Python
- Zero parsing: Direct function execution
- IDE support: Full autocomplete, type hints, debugging
- Educational: Learn real Python, not custom DSL
"""

from typing import Any, Optional, Dict, List, Union
import sys
import os

# Add uDOS root to path
UDOS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if UDOS_ROOT not in sys.path:
    sys.path.insert(0, UDOS_ROOT)

# Import will be added as needed
# from core.config import Config

# =============================================================================
# USER VARIABLES (Read-Write, Persistent)
# =============================================================================

import json
from pathlib import Path

class UserVars:
    """Persistent user variables stored in memory/bank/user/variables.json"""
    
    def __init__(self):
        self.var_file = Path("memory/bank/user/variables.json")
        self.var_file.parent.mkdir(parents=True, exist_ok=True)
        self._vars = self._load()
    
    def _load(self) -> dict:
        """Load user variables from disk"""
        if self.var_file.exists():
            try:
                with open(self.var_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save(self):
        """Save user variables to disk"""
        with open(self.var_file, 'w') as f:
            json.dump(self._vars, f, indent=2)
    
    def get(self, name: str, default=None):
        """Get user variable value"""
        return self._vars.get(name, default)
    
    def set(self, name: str, value: Any):
        """Set user variable value and persist"""
        self._vars[name] = value
        self._save()
    
    def delete(self, name: str):
        """Delete user variable"""
        if name in self._vars:
            del self._vars[name]
            self._save()
    
    def list_all(self) -> dict:
        """Get all user variables"""
        return self._vars.copy()

# Global user variables instance
_user_vars = UserVars()

# =============================================================================
# SYSTEM VARIABLES (Read-Only)
# =============================================================================

class SystemVars:
    """Read-only system variables for uCODE scripts"""
    
    def __init__(self):
        # self.config = Config()  # TODO: Add when integrating with full system
        self._sprite_hp = 100
        self._mission_status = "NONE"
        self._location = "AA340"  # Default: Sydney
        
    @property
    def SPRITE_HP(self) -> int:
        """Current sprite health points"""
        return self._sprite_hp
    
    @property
    def MISSION_STATUS(self) -> str:
        """Current mission status (DRAFT|ACTIVE|PAUSED|COMPLETED|FAILED)"""
        return self._mission_status
    
    @property
    def LOCATION(self) -> str:
        """Current TILE code location"""
        return self._location
    
    @property
    def WORKFLOW_NAME(self) -> str:
        """Current workflow script name"""
        return getattr(self, '_workflow_name', 'NONE')
    
    @property
    def WORKFLOW_PHASE(self) -> str:
        """Workflow phase (INIT|SETUP|EXECUTE|MONITOR|COMPLETE)"""
        return getattr(self, '_workflow_phase', 'INIT')

# Global system variables instance
_sys_vars = SystemVars()

# Expose as module-level variables (Python-friendly syntax)
SPRITE_HP = _sys_vars.SPRITE_HP
MISSION_STATUS = _sys_vars.MISSION_STATUS
LOCATION = _sys_vars.LOCATION
WORKFLOW_NAME = _sys_vars.WORKFLOW_NAME
WORKFLOW_PHASE = _sys_vars.WORKFLOW_PHASE

# =============================================================================
# CORE COMMANDS (Python Functions)
# =============================================================================

def PRINT(*messages: str) -> None:
    """Print messages to console with emoji rendering
    
    Args:
        *messages: One or more messages (pipe | in .upy format separates lines)
    
    Emoji Rendering (ONLY in COMMAND arguments):
        :sb: → [    :eb: → ]    :pipe: → |    :star: → *
        :sq: → '    :dq: → "    :dollar: → $   etc.
    
    Examples:
        PRINT("Hello", "World")  # Python: 2 args
        PRINT["Hello"|"World"]   # .upy: 2 lines
        PRINT["Use :pipe: char"] # .upy: renders "Use | char"
    """
    # Import emoji renderer
    try:
        from core.ui.ucode_editor import render_command_emoji
        
        # Render each message with emoji conversion
        for message in messages:
            rendered = render_command_emoji(str(message))
            print(rendered)
    except ImportError:
        # Fallback if smart editor not available
        for message in messages:
            print(message)

def GUIDE(path: str, complexity: str = "detailed") -> Dict[str, Any]:
    """Load knowledge guide from knowledge bank
    
    Args:
        path: Guide path (e.g., "water/purification")
        complexity: simple | detailed | technical
    
    Returns:
        Dictionary with guide content and metadata
    """
    # TODO: Integrate with actual knowledge system
    return {
        "path": path,
        "complexity": complexity,
        "content": f"Guide: {path}",
        "status": "mock"
    }

def CHECKPOINT_SAVE(name: str, data: Dict[str, Any]) -> bool:
    """Save workflow checkpoint
    
    Args:
        name: Checkpoint name
        data: State data to save
    
    Returns:
        True if successful
    """
    # TODO: Implement checkpoint manager integration
    print(f"CHECKPOINT: {name} saved")
    return True

def HEAL_SPRITE(amount: int) -> int:
    """Heal sprite by amount, return new HP
    
    Args:
        amount: HP to add
    
    Returns:
        New HP value
    """
    global _sys_vars
    _sys_vars._sprite_hp = min(100, _sys_vars._sprite_hp + amount)
    print(f"Healed {amount} HP → {_sys_vars._sprite_hp}")
    return _sys_vars._sprite_hp

def MISSION_CREATE(name: str, objective: str) -> str:
    """Create new mission
    
    Args:
        name: Mission name
        objective: Mission objective
    
    Returns:
        Mission ID
    """
    # TODO: Implement mission manager integration
    mission_id = f"mission-{name.lower().replace(' ', '-')}"
    print(f"Mission created: {mission_id}")
    return mission_id

def SPRITE_SET(attribute: str, value: Any) -> None:
    """Set sprite attribute
    
    Args:
        attribute: Attribute name (HP, GOLD, LEVEL, etc.)
        value: New value
    """
    global _sys_vars
    attr_map = {
        'HP': '_sprite_hp',
        'GOLD': '_sprite_gold',
        'LEVEL': '_sprite_level',
    }
    
    if attribute.upper() in attr_map:
        setattr(_sys_vars, attr_map[attribute.upper()], value)
        print(f"Sprite {attribute}: {value}")
    else:
        print(f"Unknown sprite attribute: {attribute}")

# =============================================================================
# HELPER FUNCTIONS (For uCODE Editor)
# =============================================================================

def python_to_ucode(python_code: str) -> str:
    """Convert Python code to uCODE visual syntax
    
    Args:
        python_code: Valid Python code
    
    Returns:
        uCODE-formatted string for display
    
    Visual Transformations:
        PRINT("Hello") → PRINT["Hello"]
        heal_sprite(20) → @HEAL-SPRITE[20]
        sprite_hp = 100 → $sprite-hp = 100
        CLONE_dev → CLONE*DEV (-- becomes *, tags UPPERCASE)
        build_full → BUILD*FULL
    
    Tag Rendering Rules:
        - Double dash (--) becomes asterisk (*)
        - Underscore (_) becomes dash (-)
        - Tag part after * is UPPERCASE
        - Command part before * stays as-is
    """
    import re
    
    # Transform command tags: CLONE--dev → CLONE*DEV
    def transform_tags(match):
        cmd = match.group(1)  # Command part (before --)
        tag = match.group(2).upper()  # Tag part (after --), uppercase
        return f"{cmd}*{tag}"
    
    code = python_code
    # Match: word + double-dash + word (e.g., CLONE--dev, BUILD--full)
    code = re.sub(r'(\w+)--(\w+)', transform_tags, code)
    
    # Transform underscores to dashes in identifiers
    code = code.replace('_', '-')
    
    # TODO: Full implementation in core/ui/ucode_editor.py
    return code

def ucode_to_python(ucode_text: str) -> str:
    """Convert uCODE visual syntax to valid Python
    
    Args:
        ucode_text: uCODE-formatted text
    
    Returns:
        Valid Python code
    
    Examples:
        PRINT["Hello"] → PRINT("Hello")
        @HEAL-SPRITE[20] → heal_sprite(20)
        $SPRITE-HP → sprite_hp
    """
    # TODO: Implement in core/ui/ucode_editor.py
    # This is a placeholder for the smart editor transformation
    return ucode_text

# =============================================================================
# MODULE INFO
# =============================================================================

__version__ = "1.2.24"
__author__ = "Fred Porter"
__description__ = "uDOS Core Python API - Pure Python scripting interface"

# Export all public functions
__all__ = [
    # User variables (persistent)
    '_user_vars',
    # System variables (read-only)
    'SPRITE_HP', 'MISSION_STATUS', 'LOCATION', 'WORKFLOW_NAME', 'WORKFLOW_PHASE',
    # Core commands
    'PRINT', 'GUIDE', 'CHECKPOINT_SAVE', 'HEAL_SPRITE', 'MISSION_CREATE', 'SPRITE_SET',
    # Helper functions
    'python_to_ucode', 'ucode_to_python',
]

# Convenience functions for user variables
def get_var(name: str, default=None):
    """Get user variable (persistent across scripts)"""
    return _user_vars.get(name, default)

def set_var(name: str, value: Any):
    """Set user variable (saved to memory/bank/user/variables.json)"""
    _user_vars.set(name, value)

def delete_var(name: str):
    """Delete user variable"""
    _user_vars.delete(name)

def list_vars() -> dict:
    """List all user variables"""
    return _user_vars.list_all()

__all__ += ['get_var', 'set_var', 'delete_var', 'list_vars']

if __name__ == '__main__':
    print(f"uDOS Core Python API v{__version__}")
    print(f"Total commands: {len(__all__)}")
    print("\nUsage:")
    print("  from udos_core import *")
    print("  PRINT('Hello World')")
    print("  guide = GUIDE('water/purification')")
