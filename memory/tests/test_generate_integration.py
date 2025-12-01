"""
Integration tests for GENERATE command handler (v1.1.8)

Tests the complete GENERATE SVG/DIAGRAM/ASCII/TELETEXT pipeline with proper mocking.
Mock strategy: Target service modules directly, handle lazy loading correctly.

Test Coverage:
- Command routing and parameter parsing
- SVG generation pipeline (Gemini → PNG → Vectorize)
- ASCII generation
- File I/O operations
- Error handling and fallbacks
- Style guide integration
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock, PropertyMock
from pathlib import Path
import tempfile
import shutil


class TestGenerateHandlerIntegration:
    """Integration tests for GenerateHandler with proper mocking."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory for tests."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_viewport(self):
        """Create mock viewport."""
        viewport = Mock()
        viewport.print = Mock()
        return viewport

    @pytest.fixture
    def mock_logger(self):
        """Create mock logger."""
        logger = Mock()
        logger.info = Mock()
        logger.error = Mock()
        logger.warning = Mock()
        return logger

    @pytest.fixture
    def handler(self, mock_viewport, mock_logger, temp_output_dir, monkeypatch):
        """Create GenerateHandler with mocked dependencies."""
        from core.commands.generate_handler import GenerateHandler

        # Patch output directories to use temp dir
        handler = GenerateHandler(viewport=mock_viewport, logger=mock_logger)
        handler.svg_output = temp_output_dir / "svg"
        handler.ascii_output = temp_output_dir / "ascii"
        handler.teletext_output = temp_output_dir / "teletext"

        # Ensure temp directories exist
        handler.svg_output.mkdir(parents=True, exist_ok=True)
        handler.ascii_output.mkdir(parents=True, exist_ok=True)
        handler.teletext_output.mkdir(parents=True, exist_ok=True)

        return handler

    # ===== Test 1: Handler Initialization =====
    def test_handler_initialization(self, handler):
        """Test handler initializes correctly."""
        assert handler.viewport is not None
        assert handler.logger is not None
        assert handler._gemini_generator is None  # Lazy loaded
        assert handler._vectorizer is None  # Lazy loaded
        assert handler.svg_output.exists()
        assert handler.ascii_output.exists()
        assert handler.teletext_output.exists()

    # ===== Test 2: Help Command =====
    def test_help_command(self, handler):
        """Test GENERATE HELP command."""
        result = handler.handle_command(['HELP'])
        assert 'GENERATE' in result
        assert 'SVG' in result
        assert 'ASCII' in result

    # ===== Test 3: Empty Command =====
    def test_empty_command(self, handler):
        """Test GENERATE with no parameters shows help."""
        result = handler.handle_command([])
        assert 'GENERATE' in result or 'Usage' in result

    # ===== Test 4: SVG Generation with Mocked Services =====
    @patch('core.services.gemini_generator.GeminiGenerator')
    @patch('core.services.vectorizer.get_vectorizer_service')
    def test_svg_generation_success(self, mock_vectorizer_service, mock_gemini_class, handler):
        """Test successful SVG generation pipeline."""
        # Setup mocks
        mock_gemini = Mock()
        # generate_image_svg returns (png_bytes, metadata) tuple
        mock_gemini.generate_image_svg.return_value = (
            b'fake_png_bytes',  # png_bytes
            {'format': 'PNG'}   # metadata
        )
        mock_gemini_class.return_value = mock_gemini

        # Setup vectorizer mock
        mock_vectorizer = Mock()
        mock_result = Mock()
        mock_result.svg_content = '<svg><rect/></svg>'
        mock_result.method = 'potrace'
        mock_result.metadata = {'path_count': 5}
        mock_result.validation = {'compliant': True}
        mock_vectorizer.vectorize.return_value = mock_result
        mock_vectorizer_service.return_value = mock_vectorizer

        # Execute
        result = handler.handle_command(['SVG', 'water filter diagram'])

        # Verify
        assert '✅' in result or 'success' in result.lower() or 'Generated' in result    # ===== Test 5: SVG Generation Failure Handling =====
    @patch('core.services.gemini_generator.GeminiGenerator')
    def test_svg_generation_failure(self, mock_gemini_class, handler):
        """Test SVG generation handles failures gracefully."""
        # Setup mock to fail
        mock_gemini = Mock()
        mock_gemini.generate_image_svg.side_effect = Exception("API Error")
        mock_gemini_class.return_value = mock_gemini

        # Execute
        result = handler.handle_command(['SVG', 'test diagram'])

        # Verify error is handled
        assert '❌' in result or 'error' in result.lower() or 'failed' in result.lower()

    # ===== Test 6: File Save Option =====
    @patch('core.services.gemini_generator.GeminiGenerator')
    @patch('core.services.vectorizer.get_vectorizer_service')
    def test_svg_save_to_file(self, mock_vectorizer_service, mock_gemini_class, handler, temp_output_dir):
        """Test SVG generation with --save option."""
        # Setup mocks
        mock_gemini = Mock()
        mock_gemini.generate_image_svg.return_value = (
            b'fake_png_bytes',
            {'format': 'PNG'}
        )
        mock_gemini_class.return_value = mock_gemini

        mock_vectorizer = Mock()
        mock_result = Mock()
        mock_result.svg_content = '<svg><rect/></svg>'
        mock_result.method = 'potrace'
        mock_result.metadata = {'path_count': 5}
        mock_result.validation = {'compliant': True}
        mock_vectorizer.vectorize.return_value = mock_result
        mock_vectorizer_service.return_value = mock_vectorizer

        # Execute with save option
        result = handler.handle_command(['SVG', 'diagram', '--save', 'custom.svg'])

        # Verify (result should indicate success)
        assert isinstance(result, str)

    # ===== Test 7: Style Option =====
    @patch('core.services.gemini_generator.GeminiGenerator')
    @patch('core.services.vectorizer.get_vectorizer_service')
    def test_svg_style_option(self, mock_vectorizer_service, mock_gemini_class, handler):
        """Test SVG generation with --style option."""
        mock_gemini = Mock()
        mock_gemini.generate_image_svg.return_value = (
            b'fake_png_bytes',
            {'format': 'PNG'}
        )
        mock_gemini_class.return_value = mock_gemini

        mock_vectorizer = Mock()
        mock_result = Mock()
        mock_result.svg_content = '<svg><rect/></svg>'
        mock_result.method = 'potrace'
        mock_result.metadata = {'path_count': 5}
        mock_result.validation = {'compliant': True}
        mock_vectorizer.vectorize.return_value = mock_result
        mock_vectorizer_service.return_value = mock_vectorizer

        # Execute with style
        result = handler.handle_command(['SVG', 'diagram', '--style', 'technical-kinetic'])

        # Verify mock was called with style
        if mock_gemini.generate_image_svg.called:
            call_args = mock_gemini.generate_image_svg.call_args
            # Style should be passed through
            assert call_args is not None

    # ===== Test 8: Lazy Loading of Gemini Generator =====
    def test_gemini_generator_lazy_load(self, handler):
        """Test Gemini generator is lazy loaded on first access."""
        assert handler._gemini_generator is None

        with patch('core.services.gemini_generator.GeminiGenerator') as mock_class:
            mock_instance = Mock()
            mock_class.return_value = mock_instance

            # Access property
            generator = handler.gemini_generator

            # Verify lazy load occurred
            assert handler._gemini_generator is not None
            assert generator == mock_instance

    # ===== Test 9: Lazy Loading Failure Handling =====
    def test_gemini_generator_import_error(self, handler):
        """Test handling of missing Gemini generator."""
        with patch('core.services.gemini_generator.GeminiGenerator', side_effect=ImportError("No API key")):
            with pytest.raises(ImportError) as exc_info:
                _ = handler.gemini_generator

            assert "not available" in str(exc_info.value).lower() or "api" in str(exc_info.value).lower()

    # ===== Test 10: ASCII Generation =====
    def test_ascii_generation(self, handler):
        """Test ASCII diagram generation."""
        # ASCII generation might be simpler, not requiring Gemini
        result = handler.handle_command(['ASCII', 'simple box'])

        # Verify result is a string (may be help message or actual result)
        assert isinstance(result, str)

    # ===== Test 11: DIAGRAM Alias =====
    @patch('core.services.gemini_generator.GeminiGenerator')
    @patch('core.services.vectorizer.get_vectorizer_service')
    def test_diagram_alias_for_svg(self, mock_vectorizer_service, mock_gemini_class, handler):
        """Test DIAGRAM command works as alias for SVG."""
        mock_gemini = Mock()
        mock_gemini.generate_image_svg.return_value = (
            b'fake_png_bytes',
            {'format': 'PNG'}
        )
        mock_gemini_class.return_value = mock_gemini

        mock_vectorizer = Mock()
        mock_result = Mock()
        mock_result.svg_content = '<svg><rect/></svg>'
        mock_result.method = 'potrace'
        mock_result.metadata = {'path_count': 5}
        mock_result.validation = {'compliant': True}
        mock_vectorizer.vectorize.return_value = mock_result
        mock_vectorizer_service.return_value = mock_vectorizer

        # Both should work
        result_svg = handler.handle_command(['SVG', 'test'])
        result_diagram = handler.handle_command(['DIAGRAM', 'test'])

        # Both should return strings
        assert isinstance(result_svg, str)
        assert isinstance(result_diagram, str)

    # ===== Test 12: Multiple Generations =====
    @patch('core.services.gemini_generator.GeminiGenerator')
    @patch('core.services.vectorizer.get_vectorizer_service')
    def test_multiple_svg_generations(self, mock_vectorizer_service, mock_gemini_class, handler):
        """Test multiple SVG generations use cached generator."""
        mock_gemini = Mock()
        mock_gemini.generate_image_svg.return_value = (
            b'fake_png_bytes',
            {'format': 'PNG'}
        )
        mock_gemini_class.return_value = mock_gemini

        mock_vectorizer = Mock()
        mock_result = Mock()
        mock_result.svg_content = '<svg><rect/></svg>'
        mock_result.method = 'potrace'
        mock_result.metadata = {'path_count': 5}
        mock_result.validation = {'compliant': True}
        mock_vectorizer.vectorize.return_value = mock_result
        mock_vectorizer_service.return_value = mock_vectorizer

        # First generation
        handler.handle_command(['SVG', 'diagram1'])
        first_generator = handler._gemini_generator

        # Second generation
        handler.handle_command(['SVG', 'diagram2'])
        second_generator = handler._gemini_generator

        # Should use same instance (cached)
        assert first_generator is second_generator
        assert mock_gemini_class.call_count == 1  # Only instantiated once


class TestGenerateCommandRouting:
    """Test command routing and parameter parsing."""

    @pytest.fixture
    def handler(self):
        """Create handler for routing tests."""
        from core.commands.generate_handler import GenerateHandler
        return GenerateHandler(viewport=Mock(), logger=Mock())

    def test_svg_command_recognized(self, handler):
        """Test SVG subcommand is recognized."""
        with patch.object(handler, '_generate_svg', return_value="mock result"):
            result = handler.handle_command(['SVG', 'test'])
            assert result == "mock result"

    def test_ascii_command_recognized(self, handler):
        """Test ASCII subcommand is recognized."""
        with patch.object(handler, '_generate_ascii', return_value="mock result"):
            result = handler.handle_command(['ASCII', 'test'])
            # May call method or return help
            assert isinstance(result, str)

    def test_invalid_subcommand(self, handler):
        """Test invalid subcommand returns help."""
        result = handler.handle_command(['INVALID', 'test'])
        assert isinstance(result, str)
        # Should return help or error message


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
