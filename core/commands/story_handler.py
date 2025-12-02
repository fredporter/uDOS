"""
Story Command Handler - Interactive Adventure System

Provides commands for playing interactive text-based adventures with state
management, choice tracking, and integration with SPRITE/OBJECT systems.

Commands:
- STORY START <adventure> - Begin a new adventure
- STORY PAUSE - Pause current adventure and save state
- STORY RESUME - Resume paused adventure from checkpoint
- STORY QUIT - Quit current adventure (with confirmation)
- STORY STATUS - Display current adventure state and progress
- STORY LIST - List available adventures

Version: 1.1.19
Author: uDOS Development Team
Date: 2025-12-03
"""

import json
import os
from datetime import datetime, UTC
from pathlib import Path
from typing import Dict, List, Optional, Any


class StoryHandler:
    """Handler for interactive story/adventure commands."""
    
    def __init__(self, components: Dict[str, Any]):
        """Initialize story handler with system components.
        
        Args:
            components: Dictionary with config, logger, variable_manager, etc.
        """
        self.config = components.get('config')
        self.logger = components.get('logger')
        self.var_manager = components.get('variable_manager')
        
        # Story system paths
        self.adventures_dir = Path("memory/workflows/missions")
        self.state_dir = Path("memory/workflows/state")
        self.checkpoints_dir = Path("memory/workflows/checkpoints")
        
        # Ensure directories exist
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        
        # Current story state
        self.current_story = None
        self.story_state = {
            "adventure_id": None,
            "adventure_name": None,
            "status": "NOT_STARTED",  # NOT_STARTED, ACTIVE, PAUSED, COMPLETED, FAILED
            "start_time": None,
            "pause_time": None,
            "resume_time": None,
            "current_chapter": 0,
            "current_scene": 0,
            "choices_made": [],
            "flags": {},
            "variables": {},
            "inventory": [],
            "hp": 100,
            "xp": 0,
            "endings_unlocked": []
        }
    
    def handle(self, command: str, params: List[str]) -> str:
        """Main handler for STORY commands.
        
        Args:
            command: The STORY command (ignored, but required for interface)
            params: Command arguments [subcommand, ...]
            
        Returns:
            Command output string
        """
        if not params:
            return self._show_help()
        
        subcommand = params[0].upper()
        
        if subcommand == "START":
            return self._start_adventure(params[1:])
        elif subcommand == "PAUSE":
            return self._pause_adventure()
        elif subcommand == "RESUME":
            return self._resume_adventure()
        elif subcommand == "QUIT":
            return self._quit_adventure()
        elif subcommand == "STATUS":
            return self._show_status()
        elif subcommand == "LIST":
            return self._list_adventures()
        elif subcommand == "HELP":
            return self._show_help()
        else:
            return f"❌ Unknown STORY subcommand: {subcommand}\n\nUse 'STORY HELP' for available commands."
    
    def _start_adventure(self, args: List[str]) -> str:
        """Start a new adventure.
        
        Args:
            args: [adventure_name]
            
        Returns:
            Success message or error
        """
        if not args:
            return "❌ Usage: STORY START <adventure>\n\nUse 'STORY LIST' to see available adventures."
        
        adventure_name = args[0]
        
        # Check if adventure already active
        if self.story_state["status"] == "ACTIVE":
            return f"⚠️  Adventure already active: {self.story_state['adventure_name']}\n\nUse 'STORY PAUSE' first, then 'STORY START {adventure_name}'"
        
        # Find adventure file
        adventure_file = self.adventures_dir / f"{adventure_name}.upy"
        
        if not adventure_file.exists():
            return f"❌ Adventure not found: {adventure_name}\n\nUse 'STORY LIST' to see available adventures."
        
        # Initialize new story state
        self.story_state = {
            "adventure_id": adventure_name,
            "adventure_name": adventure_name.replace('_', ' ').title(),
            "status": "ACTIVE",
            "start_time": datetime.now(UTC).isoformat(),
            "pause_time": None,
            "resume_time": None,
            "current_chapter": 0,
            "current_scene": 0,
            "choices_made": [],
            "flags": {},
            "variables": {},
            "inventory": [],
            "hp": 100,
            "xp": 0,
            "endings_unlocked": []
        }
        
        # Save initial state
        self._save_state()
        
        # Create checkpoint
        self._create_checkpoint("adventure_start")
        
        output = []
        output.append("═══════════════════════════════════════════════════════════════")
        output.append(f"  {self.story_state['adventure_name']}")
        output.append("═══════════════════════════════════════════════════════════════")
        output.append("")
        output.append("🎮 Adventure started!")
        output.append("")
        output.append("Controls:")
        output.append("  - STORY PAUSE - Save progress and pause")
        output.append("  - STORY STATUS - Check stats and progress")
        output.append("  - STORY QUIT - Exit adventure (with confirmation)")
        output.append("")
        output.append(f"📖 Adventure file: {adventure_file}")
        output.append(f"💾 State saved: {self._get_state_file()}")
        output.append("")
        output.append("Ready to begin your adventure!")
        output.append("")
        
        return "\n".join(output)
    
    def _pause_adventure(self) -> str:
        """Pause current adventure and save state.
        
        Returns:
            Success message or error
        """
        if self.story_state["status"] != "ACTIVE":
            return "⚠️  No active adventure to pause."
        
        # Update state
        self.story_state["status"] = "PAUSED"
        self.story_state["pause_time"] = datetime.now(UTC).isoformat()
        
        # Save state
        self._save_state()
        
        # Create checkpoint
        self._create_checkpoint("adventure_pause")
        
        output = []
        output.append("⏸️  Adventure paused")
        output.append("")
        output.append(f"Adventure: {self.story_state['adventure_name']}")
        output.append(f"Progress: Chapter {self.story_state['current_chapter']}, Scene {self.story_state['current_scene']}")
        output.append(f"HP: {self.story_state['hp']}/100")
        output.append(f"XP: {self.story_state['xp']}")
        output.append("")
        output.append("💾 Progress saved")
        output.append("")
        output.append("Use 'STORY RESUME' to continue your adventure.")
        output.append("")
        
        return "\n".join(output)
    
    def _resume_adventure(self) -> str:
        """Resume paused adventure from checkpoint.
        
        Returns:
            Success message or error
        """
        if self.story_state["status"] == "ACTIVE":
            return f"⚠️  Adventure already active: {self.story_state['adventure_name']}"
        
        if self.story_state["status"] != "PAUSED":
            return "⚠️  No paused adventure to resume.\n\nUse 'STORY START <adventure>' to begin a new adventure."
        
        # Load saved state
        loaded = self._load_state()
        if not loaded:
            return "❌ Failed to load saved state."
        
        # Update state
        self.story_state["status"] = "ACTIVE"
        self.story_state["resume_time"] = datetime.now(UTC).isoformat()
        
        # Save updated state
        self._save_state()
        
        output = []
        output.append("▶️  Adventure resumed")
        output.append("")
        output.append(f"Adventure: {self.story_state['adventure_name']}")
        output.append(f"Progress: Chapter {self.story_state['current_chapter']}, Scene {self.story_state['current_scene']}")
        output.append(f"HP: {self.story_state['hp']}/100")
        output.append(f"XP: {self.story_state['xp']}")
        output.append("")
        output.append("Continuing your adventure...")
        output.append("")
        
        return "\n".join(output)
    
    def _quit_adventure(self) -> str:
        """Quit current adventure with confirmation.
        
        Returns:
            Success message or error
        """
        if self.story_state["status"] not in ["ACTIVE", "PAUSED"]:
            return "⚠️  No adventure to quit."
        
        # TODO: Add confirmation prompt when interactive mode available
        # For now, save final state before quitting
        
        adventure_name = self.story_state["adventure_name"]
        
        # Update state
        self.story_state["status"] = "QUIT"
        
        # Save final state
        self._save_state()
        
        # Create final checkpoint
        self._create_checkpoint("adventure_quit")
        
        # Reset current story
        self.current_story = None
        
        output = []
        output.append("🚪 Adventure quit")
        output.append("")
        output.append(f"Adventure: {adventure_name}")
        output.append("")
        output.append("💾 Final state saved")
        output.append("")
        output.append("Thank you for playing!")
        output.append("")
        
        return "\n".join(output)
    
    def _show_status(self) -> str:
        """Display current adventure state and progress.
        
        Returns:
            Status display
        """
        if self.story_state["status"] == "NOT_STARTED":
            return "📖 No adventure started.\n\nUse 'STORY START <adventure>' to begin."
        
        output = []
        output.append("═══════════════════════════════════════════════════════════════")
        output.append("  Adventure Status")
        output.append("═══════════════════════════════════════════════════════════════")
        output.append("")
        output.append(f"Adventure: {self.story_state['adventure_name']}")
        output.append(f"Status: {self.story_state['status']}")
        output.append(f"Started: {self._format_timestamp(self.story_state['start_time'])}")
        
        if self.story_state['pause_time']:
            output.append(f"Paused: {self._format_timestamp(self.story_state['pause_time'])}")
        
        if self.story_state['resume_time']:
            output.append(f"Resumed: {self._format_timestamp(self.story_state['resume_time'])}")
        
        output.append("")
        output.append("Progress:")
        output.append(f"  Chapter: {self.story_state['current_chapter']}")
        output.append(f"  Scene: {self.story_state['current_scene']}")
        output.append(f"  Choices made: {len(self.story_state['choices_made'])}")
        output.append("")
        output.append("Stats:")
        output.append(f"  HP: {self.story_state['hp']}/100")
        output.append(f"  XP: {self.story_state['xp']}")
        output.append(f"  Inventory items: {len(self.story_state['inventory'])}")
        output.append("")
        
        if self.story_state['endings_unlocked']:
            output.append(f"Endings unlocked: {', '.join(self.story_state['endings_unlocked'])}")
            output.append("")
        
        output.append(f"State file: {self._get_state_file()}")
        output.append("")
        
        return "\n".join(output)
    
    def _list_adventures(self) -> str:
        """List available adventures.
        
        Returns:
            List of adventures
        """
        # Find all .upy files in adventures directory
        adventure_files = list(self.adventures_dir.glob("*.upy"))
        
        if not adventure_files:
            return "📖 No adventures available.\n\nAdventures should be placed in: memory/workflows/missions/"
        
        output = []
        output.append("═══════════════════════════════════════════════════════════════")
        output.append("  Available Adventures")
        output.append("═══════════════════════════════════════════════════════════════")
        output.append("")
        
        for i, adventure_file in enumerate(sorted(adventure_files), 1):
            adventure_id = adventure_file.stem
            adventure_name = adventure_id.replace('_', ' ').title()
            
            # Try to read metadata from file (first few lines)
            try:
                with open(adventure_file, 'r') as f:
                    lines = [f.readline().strip() for _ in range(10)]
                    
                # Look for description in comments
                description = "No description available"
                for line in lines:
                    if "Purpose:" in line or "Description:" in line:
                        description = line.split(':', 1)[1].strip()
                        break
                
                output.append(f"{i}. {adventure_name}")
                output.append(f"   ID: {adventure_id}")
                output.append(f"   {description}")
                output.append("")
                
            except Exception as e:
                output.append(f"{i}. {adventure_name}")
                output.append(f"   ID: {adventure_id}")
                output.append(f"   Error reading metadata: {e}")
                output.append("")
        
        output.append("Usage: STORY START <adventure_id>")
        output.append("")
        
        return "\n".join(output)
    
    def _show_help(self) -> str:
        """Display STORY command help.
        
        Returns:
            Help text
        """
        output = []
        output.append("═══════════════════════════════════════════════════════════════")
        output.append("  STORY - Interactive Adventure System")
        output.append("═══════════════════════════════════════════════════════════════")
        output.append("")
        output.append("Commands:")
        output.append("")
        output.append("  STORY START <adventure>")
        output.append("    Begin a new adventure")
        output.append("    Example: STORY START water_quest")
        output.append("")
        output.append("  STORY PAUSE")
        output.append("    Pause current adventure and save progress")
        output.append("")
        output.append("  STORY RESUME")
        output.append("    Resume paused adventure from checkpoint")
        output.append("")
        output.append("  STORY QUIT")
        output.append("    Quit current adventure (saves final state)")
        output.append("")
        output.append("  STORY STATUS")
        output.append("    Display current adventure state and progress")
        output.append("")
        output.append("  STORY LIST")
        output.append("    List all available adventures")
        output.append("")
        output.append("Features:")
        output.append("  - State management with JSON checkpoints")
        output.append("  - Progress tracking (chapters, scenes, choices)")
        output.append("  - HP/XP system")
        output.append("  - Inventory management")
        output.append("  - Multiple endings support")
        output.append("  - SPRITE/OBJECT integration")
        output.append("")
        output.append("Adventures are stored in: memory/workflows/missions/")
        output.append("State files saved to: memory/workflows/state/")
        output.append("")
        
        return "\n".join(output)
    
    # Helper methods
    
    def _get_state_file(self) -> Path:
        """Get current story state file path."""
        if self.story_state["adventure_id"]:
            return self.state_dir / f"story_{self.story_state['adventure_id']}.json"
        return self.state_dir / "story_current.json"
    
    def _save_state(self) -> bool:
        """Save current story state to JSON file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            state_file = self._get_state_file()
            
            with open(state_file, 'w') as f:
                json.dump(self.story_state, f, indent=2)
            
            if self.logger:
                self.logger.debug(f"Story state saved: {state_file}")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to save story state: {e}")
            return False
    
    def _load_state(self) -> bool:
        """Load story state from JSON file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            state_file = self._get_state_file()
            
            if not state_file.exists():
                return False
            
            with open(state_file, 'r') as f:
                self.story_state = json.load(f)
            
            if self.logger:
                self.logger.debug(f"Story state loaded: {state_file}")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to load story state: {e}")
            return False
    
    def _create_checkpoint(self, checkpoint_name: str) -> bool:
        """Create story checkpoint.
        
        Args:
            checkpoint_name: Name for this checkpoint
            
        Returns:
            True if successful, False otherwise
        """
        try:
            timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            checkpoint_file = self.checkpoints_dir / f"story_{self.story_state['adventure_id']}_{checkpoint_name}_{timestamp}.json"
            
            checkpoint_data = {
                "checkpoint_name": checkpoint_name,
                "timestamp": datetime.now(UTC).isoformat(),
                "story_state": self.story_state.copy()
            }
            
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
            
            if self.logger:
                self.logger.debug(f"Checkpoint created: {checkpoint_file}")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to create checkpoint: {e}")
            return False
    
    def _format_timestamp(self, timestamp_str: Optional[str]) -> str:
        """Format ISO timestamp for display.
        
        Args:
            timestamp_str: ISO format timestamp
            
        Returns:
            Formatted timestamp string
        """
        if not timestamp_str:
            return "N/A"
        
        try:
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        except Exception:
            return timestamp_str


# Handler registration function
def get_handler(components: Dict[str, Any]) -> StoryHandler:
    """Get story handler instance.
    
    Args:
        components: System components dictionary
        
    Returns:
        StoryHandler instance
    """
    return StoryHandler(components)
