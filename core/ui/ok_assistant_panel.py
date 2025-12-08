"""
OK Assistant Panel for uDOS TUI

O-key opens OK assistant with context-aware AI assistance and quick prompts.
Integrates with Gemini service for intelligent workflow, code, and documentation generation.

Features:
- Quick prompts for common tasks (MAKE workflow, SVG, doc, tests)
- Conversation history (last 10 exchanges)
- Context display (current file, workspace, TILE location)
- Command suggestions based on workspace state
- Integration with OK MAKE commands

Usage:
    Press O-key to open OK assistant
    Navigate with arrow keys (or numpad 8/2)
    Press ENTER to select prompt
    Press ESC to close panel
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from prompt_toolkit.formatted_text import HTML, FormattedText

from core.utils.paths import PATHS
from core.services.ok_context_manager import get_ok_context_manager
from extensions.assistant.context_builder import get_context_builder
from core.services.ok_context_manager import get_ok_context_manager
from extensions.assistant.context_builder import get_context_builder


class ConversationEntry:
    """Single conversation exchange."""
    
    def __init__(self, data: Dict):
        self.timestamp = data.get("timestamp", datetime.now().isoformat())
        self.prompt = data.get("prompt", "")
        self.response = data.get("response", "")
        self.success = data.get("success", True)
        self.tokens_used = data.get("tokens_used", 0)
    
    def format_timestamp(self) -> str:
        """Format timestamp for display."""
        try:
            dt = datetime.fromisoformat(self.timestamp)
            return dt.strftime("%H:%M:%S")
        except:
            return "00:00:00"
    
    def get_status_emoji(self) -> str:
        """Get emoji indicator for conversation status."""
        return "✓" if self.success else "✗"


class QuickPrompt:
    """Predefined quick prompt template."""
    
    def __init__(self, name: str, category: str, template: str, command: Optional[str] = None):
        self.name = name
        self.category = category  # workflow, svg, code, doc, mission
        self.template = template  # Template with {placeholder} variables
        self.command = command  # Optional uDOS command to execute
    
    def get_category_emoji(self) -> str:
        """Get emoji for prompt category."""
        return {
            "workflow": "🔄",
            "svg": "🎨",
            "code": "💻",
            "doc": "📝",
            "mission": "🎯",
            "explain": "💡",
            "optimize": "⚡"
        }.get(self.category, "❓")
    
    def format(self, **kwargs) -> str:
        """Format template with provided variables."""
        try:
            return self.template.format(**kwargs)
        except KeyError:
            return self.template


class OKAssistantPanel:
    """OK Assistant Panel for TUI."""
    
    # Predefined quick prompts
    QUICK_PROMPTS = [
        QuickPrompt(
            "MAKE Workflow Script",
            "workflow",
            "OK MAKE WORKFLOW \"{description}\" for TILE {tile}",
            "OK MAKE WORKFLOW"
        ),
        QuickPrompt(
            "MAKE SVG Graphic",
            "svg",
            "OK MAKE SVG \"{description}\"",
            "OK MAKE SVG"
        ),
        QuickPrompt(
            "MAKE Documentation",
            "doc",
            "OK MAKE DOC \"{topic}\"",
            "OK MAKE DOC"
        ),
        QuickPrompt(
            "MAKE Unit Tests",
            "code",
            "OK MAKE TEST {file_path}",
            "OK MAKE TEST"
        ),
        QuickPrompt(
            "MAKE Mission Script",
            "mission",
            "OK MAKE MISSION {category} {tile}",
            "OK MAKE MISSION"
        ),
        QuickPrompt(
            "Explain Error",
            "explain",
            "OK ASK Explain this error: {error_message}",
            "OK ASK"
        ),
        QuickPrompt(
            "Optimize Code",
            "optimize",
            "OK ASK How can I optimize this code in {file_path}?",
            "OK ASK"
        ),
        QuickPrompt(
            "Custom Question",
            "explain",
            "OK ASK {question}",
            "OK ASK"
        ),
    ]
    
    def __init__(self, context_manager=None):
        """
        Initialize OK Assistant Panel.
        
        Args:
            context_manager: Optional context manager for workspace awareness
        """
        self.selected_index = 0
        self.view_mode = "prompts"  # prompts, history, input
        self.history: List[ConversationEntry] = []
        
        # Context awareness (use provided or get singleton)
        self.context_manager = context_manager or get_ok_context_manager()
        self.context_builder = get_context_builder()
        
        # Current context
        self.current_file = None
        self.current_workspace = None
        self.tile_location = None
        self.last_error = None
        
        # Paths
        self.history_dir = PATHS.MEMORY / "system" / "user"
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.history_dir / "ok_history.json"
        
        # Load history
        self._load_history()
        
        # Update context
        self._update_context()
    
    def _load_history(self):
        """Load conversation history from file."""
        self.history = []
        
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    # Load last 10 conversations
                    for entry_data in data.get("history", [])[-10:]:
                        self.history.append(ConversationEntry(entry_data))
            except Exception as e:
                # Fail silently - start with empty history
                pass
    
    def _save_history(self):
        """Save conversation history to file."""
        try:
            data = {
                "history": [
                    {
                        "timestamp": entry.timestamp,
                        "prompt": entry.prompt,
                        "response": entry.response,
                        "success": entry.success,
                        "tokens_used": entry.tokens_used
                    }
                    for entry in self.history
                ]
            }
            
            with open(self.history_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            # Fail silently
            pass
    
    def _update_context(self):
        """Update current context from workspace state."""
        # Update context manager with current workspace
        import os
        cwd = Path(os.getcwd())
        self.context_manager.update_workspace(cwd)
        
        # Get context data
        context_data = self.context_manager.get_context()
        
        # Update panel context
        workspace_info = context_data.get("workspace", {})
        self.current_file = workspace_info.get("current_file")
        self.tile_location = workspace_info.get("tile_location") or "AA340"
        
        # Format workspace path
        try:
            if "memory" in str(cwd):
                self.current_workspace = str(cwd.relative_to(PATHS.ROOT))
            else:
                self.current_workspace = str(cwd)
        except:
            self.current_workspace = "/"
        
        # Get last error from history
        errors = context_data.get("history", {}).get("errors", [])
        self.last_error = errors[-1] if errors else None
    
    def add_conversation(self, prompt: str, response: str, success: bool = True, tokens: int = 0):
        """
        Add a conversation entry to history.
        
        Args:
            prompt: User prompt
            response: OK assistant response
            success: Whether response was successful
            tokens: Number of tokens used
        """
        entry = ConversationEntry({
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "response": response,
            "success": success,
            "tokens_used": tokens
        })
        
        self.history.append(entry)
        
        # Keep only last 10
        if len(self.history) > 10:
            self.history = self.history[-10:]
        
        self._save_history()
    
    def clear_history(self):
        """Clear conversation history."""
        self.history = []
        self._save_history()
    
    def get_selected_prompt(self) -> Optional[QuickPrompt]:
        """Get currently selected quick prompt."""
        if 0 <= self.selected_index < len(self.QUICK_PROMPTS):
            return self.QUICK_PROMPTS[self.selected_index]
        return None
    
    def move_selection(self, delta: int):
        """Move selection up/down."""
        if self.view_mode == "prompts":
            self.selected_index = (self.selected_index + delta) % len(self.QUICK_PROMPTS)
        elif self.view_mode == "history":
            if self.history:
                self.selected_index = (self.selected_index + delta) % len(self.history)
    
    def render(self) -> str:
        """
        Render OK Assistant Panel.
        
        Returns:
            Formatted text for display
        """
        lines = []
        
        # Header
        lines.append("╔══════════════════════════════════════════════════════════════╗")
        lines.append("║                      OK ASSISTANT                            ║")
        lines.append("╠══════════════════════════════════════════════════════════════╣")
        
        # Context display
        context_line = f"║ Context: {self.current_workspace:<50} ║"
        lines.append(context_line[:64] + "║")
        
        tile_file = f"TILE: {self.tile_location}"
        if self.current_file:
            tile_file += f"  File: {Path(self.current_file).name}"
        context_line2 = f"║ {tile_file:<58} ║"
        lines.append(context_line2[:64] + "║")
        
        lines.append("╠══════════════════════════════════════════════════════════════╣")
        
        # View tabs
        prompts_tab = "[PROMPTS]" if self.view_mode == "prompts" else " PROMPTS "
        history_tab = "[HISTORY]" if self.view_mode == "history" else " HISTORY "
        tabs_line = f"║ {prompts_tab}  {history_tab}                                 ║"
        lines.append(tabs_line[:64] + "║")
        
        lines.append("╠══════════════════════════════════════════════════════════════╣")
        
        # Content area (12 lines)
        if self.view_mode == "prompts":
            lines.extend(self._render_prompts())
        elif self.view_mode == "history":
            lines.extend(self._render_history())
        
        # Footer
        lines.append("╠══════════════════════════════════════════════════════════════╣")
        footer = "║ [O]Ask [P]Prompts [H]History [C]Clear [ESC]Close           ║"
        lines.append(footer)
        lines.append("╚══════════════════════════════════════════════════════════════╝")
        
        return "\n".join(lines)
    
    def _render_prompts(self) -> List[str]:
        """Render quick prompts view (12 lines)."""
        lines = []
        
        for i, prompt in enumerate(self.QUICK_PROMPTS):
            emoji = prompt.get_category_emoji()
            name = prompt.name
            
            # Highlight selected
            if i == self.selected_index:
                line = f"║ ► {emoji} {name:<54} ║"
            else:
                line = f"║   {emoji} {name:<54} ║"
            
            lines.append(line[:64] + "║")
        
        # Fill remaining lines
        while len(lines) < 12:
            lines.append("║" + " " * 62 + "║")
        
        return lines[:12]
    
    def _render_history(self) -> List[str]:
        """Render conversation history view (12 lines)."""
        lines = []
        
        if not self.history:
            lines.append("║   No conversation history yet.                               ║")
            lines.append("║                                                              ║")
            lines.append("║   Use quick prompts or press O to ask a question.           ║")
            
            # Fill remaining lines
            while len(lines) < 12:
                lines.append("║" + " " * 62 + "║")
            
            return lines[:12]
        
        # Show last 6 conversations (2 lines each)
        recent = list(reversed(self.history[-6:]))
        
        for entry in recent:
            time = entry.format_timestamp()
            status = entry.get_status_emoji()
            
            # Prompt line
            prompt_text = entry.prompt[:50]
            line1 = f"║ {status} {time} > {prompt_text:<46} ║"
            lines.append(line1[:64] + "║")
            
            # Response line (truncated)
            response_text = entry.response[:56] if entry.response else "..."
            line2 = f"║          {response_text:<52} ║"
            lines.append(line2[:64] + "║")
        
        # Fill remaining lines
        while len(lines) < 12:
            lines.append("║" + " " * 62 + "║")
        
        return lines[:12]
    
    def handle_key(self, key: str) -> Optional[str]:
        """
        Handle key input for panel.
        
        Args:
            key: Key character
            
        Returns:
            Action string or None
        """
        # Navigation
        if key in ('8', 'w', 'up'):  # Up
            self.move_selection(-1)
            return "navigate_up"
        
        elif key in ('2', 's', 'down'):  # Down
            self.move_selection(1)
            return "navigate_down"
        
        # View switching
        elif key.lower() == 'p':
            self.view_mode = "prompts"
            return "view_prompts"
        
        elif key.lower() == 'h':
            self.view_mode = "history"
            return "view_history"
        
        # Actions
        elif key.lower() == 'c':
            self.clear_history()
            return "clear_history"
        
        elif key in ('\r', '\n'):  # Enter
            if self.view_mode == "prompts":
                prompt = self.get_selected_prompt()
                if prompt:
                    return f"select_prompt:{prompt.name}"
            return "select"
        
        elif key in ('\x1b', 'escape'):  # ESC
            return "close"
        
        return None


def get_ok_assistant_panel(context_manager=None) -> OKAssistantPanel:
    """
    Factory function to get OK Assistant Panel instance.
    
    Args:
        context_manager: Optional context manager for workspace awareness
        
    Returns:
        OKAssistantPanel instance
    """
    return OKAssistantPanel(context_manager=context_manager)
