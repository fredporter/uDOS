"""
uDOS Gemini Service Wrapper
Provides lazy-loaded Gemini integration for OK ASK command
"""

from pathlib import Path
from core.services.gemini_service import GeminiCLI

_gemini_instance = None

def get_gemini():
    """Get or create Gemini CLI instance (singleton pattern)"""
    global _gemini_instance
    if _gemini_instance is None:
        # .env is in the project root, not core/
        env_path = Path(__file__).parent.parent / '.env'
        _gemini_instance = GeminiCLI(env_path=env_path)
    return _gemini_instance
