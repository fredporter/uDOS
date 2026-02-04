"""
Grid Renderer

Formats command handler results for display in the TUI.
Handles:
- Success responses
- Error responses
- Warnings
- Different result types (descriptions, lists, etc.)
"""

from typing import Dict, Any, List
import os
import sys
import time


class GridRenderer:
    """Format and display command results"""

    # Terminal colors (ANSI)
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

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
            return self._render_success(result)
        elif status == "error":
            return self._render_error(result)
        elif status == "warning":
            return self._render_warning(result)
        else:
            return self._render_generic(result)

    def _render_success(self, result: Dict[str, Any]) -> str:
        """Format successful response"""
        output = f"{self.GREEN}✓{self.RESET} {result.get('message', 'Success')}\n"

        # Add command-specific output
        if "help" in result:
            output += "\n" + result["help"] + "\n"
        elif "description" in result:
            output += result["description"]
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
        output = f"{self.YELLOW}⚠{self.RESET} {result.get('message', 'Warning')}\n"
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

    def format_error(self, message: str, details: str = "") -> str:
        """Format an error message"""
        output = f"{self.RED}✗{self.RESET} {message}\n"
        if details:
            output += f"  {details}\n"
        return output

    def format_prompt(self, location: str) -> str:
        """Format the REPL prompt"""
        return f"{self.BOLD}[{location}]{self.RESET} > "

    def stream_text(self, text: str, prefix: str = "vibe> ") -> None:
        """Stream text line-by-line with a prefix (used for Vibe-style output)."""
        delay_ms = int(os.getenv("VIBE_STREAM_DELAY_MS", "0") or "0")
        lines = text.splitlines() if text else [""]
        for line in lines:
            sys.stdout.write(f"{self.CYAN}{prefix}{self.RESET}{line}\n")
            sys.stdout.flush()
            if delay_ms > 0:
                time.sleep(delay_ms / 1000.0)

    @staticmethod
    def clear_screen() -> None:
        """Clear terminal screen"""
        print("\033[2J\033[H", end="")

    @staticmethod
    def separator(char: str = "-", width: int = 60) -> str:
        """Create a separator line"""
        return char * width


# Legacy alias for older imports/tests
Renderer = GridRenderer
