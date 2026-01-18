"""
TUI REPL (Read-Eval-Print Loop)

Main event loop for the lightweight CLI interface.
Integrates dispatcher, renderer, and game state.
"""

from typing import Optional
import sys
import logging
import asyncio
import json
from pathlib import Path

from .dispatcher import CommandDispatcher
from .renderer import GridRenderer
from .state import GameState


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def check_wizard_dashboard():
    """Check if Wizard Server is running and get dashboard info (async)"""
    try:
        # Try to import httpx (optional dependency)
        import httpx

        # Try to connect to Wizard dashboard
        async with httpx.AsyncClient(timeout=2) as client:
            try:
                response = await client.get("http://127.0.0.1:8765/api/v1/index")
                if response.status_code == 200:
                    return response.json()
            except Exception:
                # Wizard not running, that's okay
                pass
    except ImportError:
        # httpx not available
        pass

    return None


class TUIRepl:
    """Main TUI read-eval-print loop"""

    def __init__(self):
        """Initialize REPL"""
        self.dispatcher = CommandDispatcher()
        self.renderer = GridRenderer()
        self.state = GameState()
        self.logger = logging.getLogger("tui-repl")
        self.running = False
        self.wizard_dashboard = None

    def run(self) -> None:
        """
        Start the main REPL loop

        Handles:
        - User input parsing
        - Command dispatch
        - Result rendering
        - State management
        - Error handling
        """
        self.running = True
        self._show_welcome()

        try:
            while self.running:
                try:
                    # Get user input
                    prompt = self.renderer.format_prompt(self.state.current_location)
                    user_input = input(prompt).strip()

                    # Handle empty input
                    if not user_input:
                        continue

                    # Special commands (not routed to handlers)
                    if self._handle_special_commands(user_input):
                        continue

                    # Dispatch to handler
                    result = self.dispatcher.dispatch(user_input)

                    # Update game state
                    self.state.update_from_handler(result)

                    # Log command
                    self.logger.info(f"[COMMAND] {user_input} → {result.get('status')}")
                    self.state.add_to_history(user_input)

                    # Render result
                    output = self.renderer.render(result)
                    print(output)

                except KeyboardInterrupt:
                    print(f"\n{self.renderer.CYAN}→{self.renderer.RESET} Interrupted")
                    self.logger.info("[INTERRUPT] User interrupted")

                except EOFError:
                    print(f"\n{self.renderer.CYAN}→{self.renderer.RESET} End of input")
                    self.running = False

                except Exception as e:
                    self.logger.exception(f"[ERROR] {str(e)}")
                    error_msg = self.renderer.format_error("Unexpected error", str(e))
                    print(error_msg)

        finally:
            self._show_goodbye()

    def _handle_special_commands(self, user_input: str) -> bool:
        """
        Handle special commands that don't route to handlers

        Args:
            user_input: User input string

        Returns:
            True if handled, False otherwise
        """
        cmd = user_input.upper().strip()

        if cmd == "QUIT" or cmd == "EXIT" or cmd == "Q":
            self.running = False
            return True

        elif cmd == "CLEAR" or cmd == "CLS":
            self.renderer.clear_screen()
            return True

        elif cmd == "STATUS":
            self._show_status()
            return True

        elif cmd == "HISTORY":
            self._show_history()
            return True

        return False

    def _show_welcome(self) -> None:
        """Display welcome message"""
        print(
            f"\n{self.renderer.BOLD}🎮 uDOS Lightweight TUI v1.0.0{self.renderer.RESET}"
        )
        print(f"Modern CLI for the refined core")

        # Check Wizard dashboard (non-blocking with timeout)
        try:
            import httpx

            try:
                response = httpx.get("http://127.0.0.1:8765/api/v1/index", timeout=1)
                if response.status_code == 200:
                    dashboard = response.json()
                    apis_configured = sum(
                        1 for v in dashboard.get("configured_apis", {}).values() if v
                    )
                    print(
                        f"{self.renderer.GREEN}✓{self.renderer.RESET} Wizard Server running ({apis_configured}/8 APIs configured)"
                    )
                    print(
                        f"  {self.renderer.CYAN}→ Visit: http://127.0.0.1:8765/{self.renderer.RESET}"
                    )
                    self.wizard_dashboard = dashboard
            except Exception:
                print(
                    f"{self.renderer.YELLOW}⊘{self.renderer.RESET} Wizard Server not running"
                )
        except ImportError:
            pass

        print(f"{self.renderer.CYAN}Type HELP for commands{self.renderer.RESET}\n")
        self.logger.info("[STARTUP] TUI started")

    def _show_goodbye(self) -> None:
        """Display goodbye message"""
        print(f"\n{self.renderer.CYAN}→{self.renderer.RESET} Goodbye!\n")
        self.logger.info("[SHUTDOWN] TUI closed")

    def _show_status(self) -> None:
        """Show current game status"""
        status = self.state.to_dict()
        print(f"\n{self.renderer.BOLD}Status:{self.renderer.RESET}")
        print(f"  Location: {status['current_location']}")
        print(f"  Level: {status['player_stats']['level']}")
        print(f"  Health: {status['player_stats']['health']}")
        print(f"  Inventory: {len(status['inventory'])} items")
        print(f"  Discovered: {len(status['discovered_locations'])} locations\n")

    def _show_history(self) -> None:
        """Show command history"""
        if not self.state.session_history:
            print(f"{self.renderer.CYAN}(no history){self.renderer.RESET}\n")
            return

        print(f"\n{self.renderer.BOLD}Command History:{self.renderer.RESET}")
        for i, cmd in enumerate(self.state.session_history[-10:], 1):
            print(f"  {i}. {cmd}")
        print()


def main() -> int:
    """
    Main entry point for TUI

    Returns:
        Exit code
    """
    try:
        repl = TUIRepl()
        repl.run()
        return 0
    except Exception as e:
        print(f"Fatal error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
