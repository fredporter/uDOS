"""
uDOS Assistant Extension - Gemini Integration
AI-powered assistance (optional extension)

Version: 1.0.0
Moved from core to extensions in v1.2.0
"""

from .gemini_service import GeminiService, get_gemini_service

__all__ = ['GeminiService', 'get_gemini_service']
__version__ = '1.0.0'
