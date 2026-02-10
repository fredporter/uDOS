"""
Grid Renderer

Formats command handler results for display in the TUI.
Handles:
- Success responses
- Error responses
- Warnings
- Different result types (descriptions, lists, etc.)
"""

from typing import Dict, Any, List, Sequence, Iterable, Tuple, Set, Optional
import os
import sys
import time
import json
import re
from pathlib import Path

from core.tui.ui_elements import format_table
from core.tui.output import OutputToolkit


class GridRenderer:
    """Format and display command results"""

    # Terminal colors (ANSI)
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    MOODS = {
        "idle": ["·", "•", "○", "●"],
        "think": ["?", "¿"],
        "busy": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴"],
        "success": ["✓"],
        "warn": ["!"],
        "error": ["x"],
    }

    def __init__(self):
        self._mood = "idle"
        self._pace = 0.6  # seconds per frame
        self._blink = True
        self._emoji_set: Set[str] = set()
        self._emoji_loaded = False

    def render(self, result: Dict[str, Any]) -> str:
        """
        Format handler result for display

        Args:
            result: Dict returned from handler

        Returns:
            Formatted string for display
        """
        status = result.get("status", "unknown")

        if status == "success":
            output = self._render_success(result)
        elif status == "error":
            output = self._render_error(result)
        elif status == "warning":
            output = self._render_warning(result)
        else:
            output = self._render_generic(result)

        return self._apply_emoji(output)

    def _render_success(self, result: Dict[str, Any]) -> str:
        """Format successful response"""
        output = f"{self.GREEN}✓{self.RESET} {result.get('message', 'Success')}\n"

        # Add command-specific output
        if "help" in result:
            output += "\n" + result["help"] + "\n"
        elif "description" in result:
            output += result["description"]
        elif "table" in result:
            headers, rows = self._normalize_table(result["table"])
            output += self.render_table(headers, rows) + "\n"
        elif "output" in result:
            output += result["output"] + "\n"
        elif "items" in result:
            output += self._format_items(result["items"])
        elif "results" in result:
            output += self._format_results(result["results"])
        elif "text" in result:
            output += result["text"] + "\n"

        return output

    def _render_error(self, result: Dict[str, Any]) -> str:
        """Format error response"""
        output = (
            f"{self.RED}✗{self.RESET} Error: {result.get('message', 'Unknown error')}\n"
        )

        if "output" in result:
            output += result["output"] + "\n"

        if "suggestion" in result:
            output += f"{self.CYAN}->{self.RESET} {result['suggestion']}\n"

        if "details" in result:
            output += f"  Details: {result['details']}\n"

        return output

    def _render_warning(self, result: Dict[str, Any]) -> str:
        """Format warning response"""
        output = f"{self.YELLOW}!{self.RESET} {result.get('message', 'Warning')}\n"
        if "output" in result:
            output += result["output"] + "\n"
        return output

    def _render_generic(self, result: Dict[str, Any]) -> str:
        """Format generic response"""
        output = f"{self.CYAN}->{self.RESET} Response:\n"
        for key, value in result.items():
            if key not in ["status"]:
                output += f"  {key}: {value}\n"
        return output

    def _format_items(self, items: List[Dict[str, Any]]) -> str:
        """Format item list"""
        if not items:
            return "  (no items)\n"

        output = ""
        for item in items:
            name = item.get("name", "Unknown")
            qty = item.get("quantity", 1)
            equipped = " [equipped]" if item.get("equipped") else ""
            output += f"  - {name} (qty: {qty}){equipped}\n"
        return output

    def _format_results(self, results: List[Dict[str, Any]]) -> str:
        """Format search results"""
        if not results:
            return "  (no results)\n"

        output = ""
        for i, result in enumerate(results[:10], 1):  # Show first 10
            name = result.get("name", "Unknown")
            loc_id = result.get("id", "")
            output += f"  {i}. {name}\n     {loc_id}\n"
        return output

    def render_table(self, headers: Sequence[str], rows: Iterable[Sequence[Any]]) -> str:
        """Render a basic table for command outputs."""
        return format_table(headers, rows)

    @staticmethod
    def _normalize_table(
        table_data: Any,
    ) -> Tuple[Sequence[str], Iterable[Sequence[Any]]]:
        if isinstance(table_data, dict):
            headers = table_data.get("headers", [])
            rows = table_data.get("rows", [])
            return headers, rows
        if isinstance(table_data, (list, tuple)) and len(table_data) == 2:
            return table_data[0], table_data[1]
        return [], []

    def format_error(self, message: str, details: str = "") -> str:
        """Format an error message"""
        output = f"{self.RED}✗{self.RESET} {message}\n"
        if details:
            output += f"  {details}\n"
        return output

    def format_prompt(self, location: str) -> str:
        """Format the REPL prompt"""
        indicator = self.get_prompt_indicator()
        return f"{indicator} {self.BOLD}[{location}]{self.RESET} > "

    def set_mood(self, mood: str, pace: float = 0.6, blink: bool = True) -> None:
        """Set the mood and animation pace for the prompt indicator."""
        if mood not in self.MOODS:
            mood = "idle"
        self._mood = mood
        self._pace = max(0.1, float(pace))
        self._blink = bool(blink)

    def get_mood(self) -> str:
        """Return the current mood name."""
        return self._mood

    def get_prompt_indicator(self) -> str:
        """Return the animated prompt indicator emoji."""
        return self.get_mood_frame(self._mood, self._pace, self._blink)

    def get_prompt_indicator_plain(self) -> str:
        """Return prompt indicator without ANSI styling."""
        from core.utils.text_width import strip_ansi

        return strip_ansi(self.get_prompt_indicator())

    def get_mood_frame(self, mood: str, pace: float, blink: bool) -> str:
        """Return a single emoji frame for the given mood."""
        frames = self.MOODS.get(mood) or self.MOODS["idle"]
        now = time.time()
        idx = int(now / pace) % len(frames)
        if blink and int(now / (pace * 2)) % 2 == 1:
            return " "
        if not self._supports_ansi():
            return frames[idx]
        return f"{self.DIM}{frames[idx]}{self.RESET}"

    @staticmethod
    def _supports_ansi() -> bool:
        if os.getenv("UDOS_NO_ANSI") == "1" or os.getenv("NO_COLOR"):
            return False
        term = os.getenv("TERM", "").strip().lower()
        if term in {"dumb", "unknown"}:
            return False
        return sys.stdout.isatty()

    def stream_text(self, text: str, prefix: str = "vibe> ") -> None:
        """Stream text line-by-line with a prefix (used for Vibe-style output)."""
        delay_ms = int(os.getenv("VIBE_STREAM_DELAY_MS", "0") or "0")
        lines = text.splitlines() if text else [""]
        for line in lines:
            rendered = self._apply_emoji(line)
            sys.stdout.write(f"{self.CYAN}{prefix}{self.RESET}{rendered}\n")
            sys.stdout.flush()
            if delay_ms > 0:
                time.sleep(delay_ms / 1000.0)

    def _apply_emoji(self, text: str) -> str:
        """Apply emoji shortcode rendering policy to text."""
        if not text:
            return text
        self._load_emoji_set()
        if not self._emoji_set:
            return text
        mode = os.getenv("UDOS_EMOJI_TUI_RENDER", "plain").strip().lower()
        pattern = re.compile(r":[a-z0-9_+\-]+:", re.IGNORECASE)

        def replace(match: re.Match) -> str:
            token = match.group(0)
            token_key = token.lower()
            if token_key not in self._emoji_set:
                return token
            if mode in {"plain", "passthrough", "keep"}:
                return token
            if mode in {"strip", "remove"}:
                return ""
            if mode in {"label", "tag"}:
                return f"[{token}]"
            return token

        return pattern.sub(replace, text)

    def _load_emoji_set(self) -> None:
        """Load emoji shortcode set from vendor data (once)."""
        if self._emoji_loaded:
            return
        self._emoji_loaded = True
        try:
            repo_root = self._find_repo_root()
            if not repo_root:
                return
            path = repo_root / "vendor" / "emoji" / "github-emoji-shortcodes.json"
            if not path.exists():
                return
            data = json.loads(path.read_text(encoding="utf-8"))
            shortcodes = data.get("shortcodes") or []
            if isinstance(shortcodes, list):
                self._emoji_set = {
                    s.lower() for s in shortcodes if isinstance(s, str)
                }
        except Exception:
            self._emoji_set = set()

    def _find_repo_root(self) -> Optional[Path]:
        """Locate repo root by searching for fonts/emoji."""
        current = Path(__file__).resolve()
        for parent in [current] + list(current.parents):
            candidate = parent / "fonts" / "emoji" / "github-emoji-shortcodes.json"
            if candidate.exists():
                return parent
        cwd = Path.cwd()
        for parent in [cwd] + list(cwd.parents):
            candidate = parent / "fonts" / "emoji" / "github-emoji-shortcodes.json"
            if candidate.exists():
                return parent
        return None

    @staticmethod
    def clear_screen() -> None:
        """Clear terminal screen"""
        print("\033[2J\033[H", end="")

    def present_frames(self, frames: Sequence[str], interval: float = 0.8, repeat: int = 1, clear: bool = True) -> None:
        """Present full-screen frames with clears between (presentation-style)."""
        OutputToolkit.present_frames(frames, interval=interval, repeat=repeat, clear=clear)

    @staticmethod
    def separator(char: str = "-", width: int = 60) -> str:
        """Create a separator line"""
        return char * width


# Legacy alias for older imports/tests
Renderer = GridRenderer
