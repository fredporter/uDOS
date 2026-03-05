"""
Assistant Extension - Dev Mode Coding Helpers
=============================================

Provides Dev Mode coding assistance via external tools.

Services:
  - DevModeToolCliService: external contributor tool integration for the Dev Mode lane

Usage:
  from extensions.assistant.vibe_cli_service import DevModeToolCliService

  contributor_tool = DevModeToolCliService()
  if contributor_tool.is_available:
      result = contributor_tool.analyze_code("path/to/file.py")
"""

from .vibe_cli_service import (
    DevModeToolCliConfig,
    DevModeToolCliResponse,
    DevModeToolCliService,
    VibeCliService,
    VibeConfig,
    VibeResponse,
)

__all__ = [
    "DevModeToolCliConfig",
    "DevModeToolCliResponse",
    "DevModeToolCliService",
    "VibeCliService",
    "VibeConfig",
    "VibeResponse",
]
