"""
Assistant Extension - AI Coding Helpers
=======================================

Provides AI-powered coding assistance via external tools.

Services:
  - VibeCliService: Mistral Vibe CLI integration (WIZARD ONLY)

Usage:
  from extensions.assistant.vibe_cli_service import VibeCliService

  vibe = VibeCliService()
  if vibe.is_available:
      result = vibe.analyze_code("path/to/file.py")
"""

from .vibe_cli_service import VibeCliService, VibeConfig, VibeResponse

__all__ = ["VibeCliService", "VibeConfig", "VibeResponse"]
