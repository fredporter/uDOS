"""
uCLI entrypoint module.

uCODE remains the command surface; uCLI is the terminal interface.
"""

from core.tui.ucode import UCLI


def main():
    """Main entry point for uCLI."""
    tui = UCLI()
    tui.run()


if __name__ == "__main__":
    main()
