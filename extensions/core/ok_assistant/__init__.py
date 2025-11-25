"""
uDOS OK Assistant Extension
Gemini API integration for AI-powered assistance
Moved from core/services to extensions/core as it's an API-based service
"""

from .gemini_service import GeminiCLI, get_gemini

__all__ = ['GeminiCLI', 'get_gemini']
