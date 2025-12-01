"""
Integration Tests for Nano Banana System - v1.1.7

Tests GENERATE handler with mocked services to verify integration
without requiring live API calls.

Run: pytest sandbox/tests/integration_nano_banana_test.py -v

Author: uDOS Development Team
Version: 1.1.7
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.commands.generate_handler import GenerateHandler, handle_generate_command


class TestGenerateHandlerIntegration:
    """Integration tests for GENERATE command handler with mocked services."""

    @patch('core.commands.generate_handler.GeminiGenerator')
    @patch('core.commands.generate_handler.Vectorizer')
    def test_full_svg_generation_workflow(self, mock_vec_class, mock_gen_class):
        """Test complete SVG generation workflow with mocked services."""
        # Setup mocks
        mock_gen = mock_gen_class.return_value
        mock_vec = mock_vec_class.return_value

        # Mock PNG generation
        mock_gen.generate_image_svg.return_value = (
            b'fake_png_data_content',
            {
                'model': 'gemini-2.0-flash-exp',
                'size': (1200, 900),
                'style': 'technical-kinetic'
            }
        )

        # Mock vectorization result
        mock_result = Mock()
        mock_result.svg_content = '<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>'
        mock_result.method = 'potrace'
        mock_result.validation = Mock()
        mock_result.validation.is_valid = True
        mock_result.validation.is_monochrome = True
        mock_result.validation.issues = []

        mock_vec.vectorize_png.return_value = mock_result

        # Execute command
        result = handle_generate_command(
            ['SVG', 'test diagram', '--style', 'technical-kinetic'],
            grid=None,
            parser=None
        )

        # Verify workflow
        assert mock_gen.generate_image_svg.called, "Should call PNG generation"
        assert mock_vec.vectorize_png.called, "Should call vectorization"
        assert 'success' in result.lower() or 'generated' in result.lower() or '✅' in result

    @patch('core.commands.generate_handler.GeminiGenerator')
    @patch('core.commands.generate_handler.Vectorizer')
    def test_svg_generation_with_all_options(self, mock_vec_class, mock_gen_class):
        """Test SVG generation with all command-line options."""
        mock_gen = mock_gen_class.return_value
        mock_vec = mock_vec_class.return_value

        # Setup mocks
        mock_gen.generate_image_svg.return_value = (b'png_data', {'model': 'test'})

        mock_result = Mock()
        mock_result.svg_content = '<svg>test</svg>'
        mock_result.validation = Mock()
        mock_result.validation.is_valid = True
        mock_vec.vectorize_png.return_value = mock_result

        # Execute with all options
        result = handle_generate_command(
            [
                'SVG',
                'complex diagram',
                '--style', 'hand-illustrative',
                '--type', 'architecture',
                '--save', 'custom.svg',
                '--pro',
                '--strict'
            ],
            grid=None,
            parser=None
        )

        # Verify options were parsed
        call_args = mock_gen.generate_image_svg.call_args
        assert call_args is not None
        assert call_args[1]['style'] == 'hand-illustrative'
        assert call_args[1]['diagram_type'] == 'architecture'
        assert call_args[1]['use_pro'] == True

    @patch('core.commands.generate_handler.GeminiGenerator')
    @patch('core.commands.generate_handler.Vectorizer')
    def test_validation_failure_handling(self, mock_vec_class, mock_gen_class):
        """Test handling of validation failures in strict mode."""
        mock_gen = mock_gen_class.return_value
        mock_vec = mock_vec_class.return_value

        # Setup mocks
        mock_gen.generate_image_svg.return_value = (b'png_data', {'model': 'test'})

        # Mock failed validation
        mock_result = Mock()
        mock_result.svg_content = '<svg>test</svg>'
        mock_result.validation = Mock()
        mock_result.validation.is_valid = False
        mock_result.validation.issues = ['Gradients detected', 'Not monochrome']
        mock_vec.vectorize_png.return_value = mock_result

        # Execute with strict validation
        result = handle_generate_command(
            ['SVG', 'test', '--strict'],
            grid=None,
            parser=None
        )

        # Should report validation issues
        assert 'validation' in result.lower() or 'issue' in result.lower() or '⚠️' in result

    @patch('core.commands.generate_handler.GeminiGenerator')
    def test_png_generation_error_handling(self, mock_gen_class):
        """Test error handling when PNG generation fails."""
        mock_gen = mock_gen_class.return_value

        # Simulate PNG generation error
        mock_gen.generate_image_svg.side_effect = Exception("API error")

        # Execute command
        result = handle_generate_command(
            ['SVG', 'test diagram'],
            grid=None,
            parser=None
        )

        # Should return error message
        assert 'error' in result.lower() or '❌' in result or 'failed' in result.lower()

    @patch('core.commands.generate_handler.GeminiGenerator')
    @patch('core.commands.generate_handler.Vectorizer')
    def test_vectorization_error_handling(self, mock_vec_class, mock_gen_class):
        """Test error handling when vectorization fails."""
        mock_gen = mock_gen_class.return_value
        mock_vec = mock_vec_class.return_value

        # PNG generation succeeds
        mock_gen.generate_image_svg.return_value = (b'png_data', {'model': 'test'})

        # Vectorization fails
        mock_vec.vectorize_png.side_effect = Exception("Vectorization error")

        # Execute command
        result = handle_generate_command(
            ['SVG', 'test diagram'],
            grid=None,
            parser=None
        )

        # Should return error message
        assert 'error' in result.lower() or '❌' in result or 'failed' in result.lower()


class TestCommandAliases:
    """Test that command aliases work correctly."""

    @patch('core.commands.generate_handler.GeminiGenerator')
    @patch('core.commands.generate_handler.Vectorizer')
    def test_diagram_alias(self, mock_vec_class, mock_gen_class):
        """Test that GENERATE DIAGRAM works as alias for SVG."""
        mock_gen = mock_gen_class.return_value
        mock_vec = mock_vec_class.return_value

        # Setup mocks
        mock_gen.generate_image_svg.return_value = (b'png', {'model': 'test'})

        mock_result = Mock()
        mock_result.svg_content = '<svg>test</svg>'
        mock_result.validation = Mock()
        mock_result.validation.is_valid = True
        mock_vec.vectorize_png.return_value = mock_result

        # Execute DIAGRAM command (alias)
        result = handle_generate_command(
            ['DIAGRAM', 'test'],
            grid=None,
            parser=None
        )

        # Should call SVG generation
        assert mock_gen.generate_image_svg.called
        assert 'success' in result.lower() or '✅' in result


class TestOutputFileHandling:
    """Test SVG file saving and naming."""

    @patch('core.commands.generate_handler.GeminiGenerator')
    @patch('core.commands.generate_handler.Vectorizer')
    @patch('pathlib.Path.write_text')
    def test_custom_filename(self, mock_write, mock_vec_class, mock_gen_class):
        """Test saving SVG with custom filename."""
        mock_gen = mock_gen_class.return_value
        mock_vec = mock_vec_class.return_value

        # Setup mocks
        mock_gen.generate_image_svg.return_value = (b'png', {'model': 'test'})

        mock_result = Mock()
        mock_result.svg_content = '<svg>test</svg>'
        mock_result.validation = Mock()
        mock_result.validation.is_valid = True
        mock_vec.vectorize_png.return_value = mock_result

        # Execute with custom filename
        result = handle_generate_command(
            ['SVG', 'test', '--save', 'custom-name.svg'],
            grid=None,
            parser=None
        )

        # Verify file was written
        assert mock_write.called or 'custom-name.svg' in result

    @patch('core.commands.generate_handler.GeminiGenerator')
    @patch('core.commands.generate_handler.Vectorizer')
    def test_auto_generated_filename(self, mock_vec_class, mock_gen_class):
        """Test automatic filename generation with timestamp."""
        mock_gen = mock_gen_class.return_value
        mock_vec = mock_vec_class.return_value

        # Setup mocks
        mock_gen.generate_image_svg.return_value = (b'png', {'model': 'test'})

        mock_result = Mock()
        mock_result.svg_content = '<svg>test</svg>'
        mock_result.validation = Mock()
        mock_result.validation.is_valid = True
        mock_vec.vectorize_png.return_value = mock_result

        # Execute without custom filename
        result = handle_generate_command(
            ['SVG', 'water filter'],
            grid=None,
            parser=None
        )

        # Should mention filename or location
        assert 'svg' in result.lower() or 'saved' in result.lower() or '💾' in result


class TestStyleAndTypeValidation:
    """Test validation of style and diagram type parameters."""

    def test_invalid_style(self):
        """Test handling of invalid style parameter."""
        result = handle_generate_command(
            ['SVG', 'test', '--style', 'invalid-style'],
            grid=None,
            parser=None
        )

        # Should return error or warning
        assert 'error' in result.lower() or 'invalid' in result.lower() or '❌' in result

    def test_invalid_type(self):
        """Test handling of invalid diagram type parameter."""
        result = handle_generate_command(
            ['SVG', 'test', '--type', 'invalid-type'],
            grid=None,
            parser=None
        )

        # Should return error or warning
        assert 'error' in result.lower() or 'invalid' in result.lower() or '❌' in result

    @patch('core.commands.generate_handler.GeminiGenerator')
    @patch('core.commands.generate_handler.Vectorizer')
    def test_valid_styles(self, mock_vec_class, mock_gen_class):
        """Test all valid style options."""
        mock_gen = mock_gen_class.return_value
        mock_vec = mock_vec_class.return_value

        # Setup mocks
        mock_gen.generate_image_svg.return_value = (b'png', {'model': 'test'})

        mock_result = Mock()
        mock_result.svg_content = '<svg>test</svg>'
        mock_result.validation = Mock()
        mock_result.validation.is_valid = True
        mock_vec.vectorize_png.return_value = mock_result

        valid_styles = ['technical-kinetic', 'hand-illustrative', 'hybrid']

        for style in valid_styles:
            result = handle_generate_command(
                ['SVG', 'test', '--style', style],
                grid=None,
                parser=None
            )

            # Should succeed for valid styles
            assert 'error' not in result.lower() or '✅' in result

    @patch('core.commands.generate_handler.GeminiGenerator')
    @patch('core.commands.generate_handler.Vectorizer')
    def test_valid_types(self, mock_vec_class, mock_gen_class):
        """Test all valid diagram type options."""
        mock_gen = mock_gen_class.return_value
        mock_vec = mock_vec_class.return_value

        # Setup mocks
        mock_gen.generate_image_svg.return_value = (b'png', {'model': 'test'})

        mock_result = Mock()
        mock_result.svg_content = '<svg>test</svg>'
        mock_result.validation = Mock()
        mock_result.validation.is_valid = True
        mock_vec.vectorize_png.return_value = mock_result

        valid_types = [
            'flowchart', 'architecture', 'schematic',
            'kinetic-flow', 'hatching-pattern', 'typography',
            'curved-conduits', 'gears-cogs'
        ]

        for diagram_type in valid_types:
            result = handle_generate_command(
                ['SVG', 'test', '--type', diagram_type],
                grid=None,
                parser=None
            )

            # Should succeed for valid types
            assert 'error' not in result.lower() or '✅' in result


# Test runner convenience
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
