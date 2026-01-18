"""
Groovebox Extension - Core Module
=================================

Text-based music production with MML sequencing,
808 drums, 303 bass, and 80s synth aesthetics.

Version: v1.0.0.0
"""

from pathlib import Path

# Extension root
GROOVEBOX_ROOT = Path(__file__).parent


# Version
def get_version() -> str:
    """Get groovebox extension version."""
    import json

    version_file = GROOVEBOX_ROOT / "version.json"
    if version_file.exists():
        with open(version_file) as f:
            data = json.load(f)
            return data.get("version", "v0.0.0")
    return "v0.0.0"


__version__ = get_version()
__all__ = ["engine", "instruments"]
