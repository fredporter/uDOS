#!/usr/bin/env python3
"""
uDOS Copilot Summary Module

Provides precise, single-line dev summaries in uDOS log format.
Can be called from Copilot Chat or as a standalone module.

Usage:
    python -m core.copilot_summary "summary message" [duration_ms] [code] [tizo] [zoom]
"""

import sys
import argparse
from pathlib import Path
from .dev_logger import quick_dev_log


def generate_summary(
    summary_msg: str,
    duration_ms: int = 0,
    code: int = 0,
    tizo: str = "AUS-BNE",
    zoom: int = 3
) -> Path:
    """
    Generate a dev summary log entry.

    Args:
        summary_msg: The summary message (keep concise, one line)
        duration_ms: Duration of the work in milliseconds
        code: Return code (0 = success, non-zero = error)
        tizo: Location code (default: AUS-BNE)
        zoom: Zoom level (default: 3)

    Returns:
        Path to the log file created
    """
    # Clean up the summary message
    clean_msg = summary_msg.strip().replace('\n', ' ').replace('\r', ' ')

    # Generate the log entry
    log_path = quick_dev_log(
        tizo=tizo,
        zoom=zoom,
        command="DEV SUMMARY",
        code=code,
        ms=duration_ms,
        message=clean_msg,
        with_user_ctx=True
    )

    return log_path


def main():
    """Command line interface for generating dev summaries."""
    parser = argparse.ArgumentParser(
        description="Generate uDOS dev summary log entry",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python -m core.copilot_summary "core/maps/grid.py: add APAC-centre wrap"
    python -m core.copilot_summary "implemented file search" 450 0 AUS-BNE 3
    python -m core.copilot_summary "fixed parsing bug" 120 1 JPN-TYO 2
        """
    )

    parser.add_argument("summary", help="Summary message (keep concise)")
    parser.add_argument("duration", nargs="?", type=int, default=0,
                       help="Duration in milliseconds (default: 0)")
    parser.add_argument("code", nargs="?", type=int, default=0,
                       help="Return code (default: 0)")
    parser.add_argument("tizo", nargs="?", default="AUS-BNE",
                       help="TIZO location code (default: AUS-BNE)")
    parser.add_argument("zoom", nargs="?", type=int, default=3,
                       help="Zoom level (default: 3)")

    args = parser.parse_args()

    try:
        log_path = generate_summary(
            summary_msg=args.summary,
            duration_ms=args.duration,
            code=args.code,
            tizo=args.tizo,
            zoom=args.zoom
        )

        print(f"Dev summary logged to: {log_path}")

        # Show the last line written
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if lines:
                print(f"Entry: {lines[-1].strip()}")

    except Exception as e:
        print(f"Error generating summary: {e}", file=sys.stderr)
        sys.exit(1)


# Copilot Chat snippet support
COPILOT_SNIPPET = """
To generate a uDOS dev summary, run:

```bash
python -m core.copilot_summary "your summary message here" [duration_ms] [code] [tizo] [zoom]
```

Or use the quick function in Python:
```python
from core.copilot_summary import generate_summary
log_path = generate_summary("implemented feature X", duration_ms=450, code=0)
```

Example summaries:
- "core/maps/grid.py: add APAC-centre wrap; improve cell refs"
- "fixed STATUS command memory leak in uDOS_main.py"
- "added teletext output rendering for MAP WEB command"
- "refactored file handler error paths, improved logging"

Keep summaries:
- One line only
- File-focused when possible (core/module/file.py: what changed)
- Action-oriented (add, fix, refactor, implement)
- Under 80 characters if possible
"""


if __name__ == "__main__":
    main()
