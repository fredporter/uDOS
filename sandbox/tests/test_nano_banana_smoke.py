"""
Smoke Test for Nano Banana System - v1.1.7

Minimal test to verify basic functionality without mocking complexity.

Run: pytest sandbox/tests/test_nano_banana_smoke.py -v

Author: uDOS Development Team
Version: 1.1.7
"""

import pytest
from pathlib import Path
import sys

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.commands.generate_handler import GenerateHandler, handle_generate_command


class TestNanoBananaSmoke:
    """Smoke tests for Nano Banana - verify basic structure."""
    
    def test_generate_handler_initialization(self):
        """Test that GenerateHandler can be instantiated."""
        handler = GenerateHandler()
        
        assert handler is not None
        assert hasattr(handler, 'handle_command')
        assert hasattr(handler, 'svg_output')
        # Note: Don't access .gemini_generator property as it triggers loading
        assert hasattr(GenerateHandler, 'gemini_generator')  # Property exists
        assert hasattr(GenerateHandler, 'vectorizer')  # Property exists
    
    def test_output_directories_created(self):
        """Test that output directories are created on init."""
        handler = GenerateHandler()
        
        assert handler.svg_output.exists()
        assert handler.ascii_output.exists()
        assert handler.teletext_output.exists()
    
    def test_handle_generate_command_callable(self):
        """Test that handle_generate_command function exists."""
        assert callable(handle_generate_command)
    
    def test_function_signature(self):
        """Test handle_generate_command has correct signature."""
        import inspect
        sig = inspect.signature(handle_generate_command)
        
        assert 'params' in sig.parameters
        assert 'viewport' in sig.parameters
        assert 'logger' in sig.parameters
        
        # Check defaults
        assert sig.parameters['viewport'].default is None
        assert sig.parameters['logger'].default is None
    
    def test_lazy_loading_properties(self):
        """Test that services use lazy loading."""
        handler = GenerateHandler()
        
        # Properties should exist but services shouldn't be loaded yet
        assert handler._gemini_generator is None
        assert handler._vectorizer is None
        assert handler._ascii_generator is None
    
    @pytest.mark.skip("Requires Gemini API key - use live tests instead")
    def test_svg_generation_requires_api_key(self):
        """Test that SVG generation fails gracefully without API key."""
        # This test would require mocking or live API
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
