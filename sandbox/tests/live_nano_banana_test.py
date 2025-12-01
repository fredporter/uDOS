"""
Live Nano Banana API Tests - v1.1.7

Requires valid GEMINI_API_KEY in environment.
Tests complete PNG→SVG pipeline with real API calls.

Run: pytest sandbox/tests/live_nano_banana_test.py -v -s
Skip: Add --skipif to skip live tests

Author: uDOS Development Team
Version: 1.1.7
"""

import pytest
import os
from pathlib import Path
import sys

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.services.gemini_generator import GeminiGenerator
from core.services.vectorizer import Vectorizer

# Skip all tests if no API key
pytestmark = pytest.mark.skipif(
    not os.getenv('GEMINI_API_KEY'),
    reason="Requires GEMINI_API_KEY in environment"
)


class TestLiveNanoBananaPNGGeneration:
    """Test PNG generation via Gemini 2.5 Flash Image (Nano Banana)."""

    def test_generate_simple_png_standard_mode(self):
        """Test basic PNG generation with standard Nano Banana."""
        gen = GeminiGenerator()

        png_bytes, metadata = gen.generate_image_svg(
            description="simple water filter diagram",
            style="technical-kinetic",
            diagram_type="flowchart",
            use_pro=False
        )

        assert png_bytes is not None, "PNG bytes should not be None"
        assert len(png_bytes) > 0, "PNG should have content"
        assert metadata['model'] in ['gemini-2.0-flash-exp', 'gemini-2.5-flash'], \
            f"Expected standard model, got {metadata['model']}"
        print(f"\n✅ Generated PNG: {len(png_bytes)} bytes using {metadata['model']}")

    def test_generate_png_pro_mode(self):
        """Test PNG generation with Nano Banana Pro (higher quality, slower)."""
        gen = GeminiGenerator()

        png_bytes, metadata = gen.generate_image_svg(
            description="fire triangle chemistry diagram",
            style="technical-kinetic",
            diagram_type="schematic",
            use_pro=True
        )

        assert png_bytes is not None
        assert len(png_bytes) > 0
        assert metadata['model'] in ['gemini-exp-1206', 'gemini-2.0-flash-thinking-exp'], \
            f"Expected Pro model, got {metadata['model']}"
        print(f"\n✅ Generated PNG (Pro): {len(png_bytes)} bytes using {metadata['model']}")

    def test_generate_with_style_guide_references(self):
        """Test PNG generation with style guide reference images."""
        gen = GeminiGenerator()

        # Load style guide (may be empty if no PNGs exist)
        references = gen.load_style_guide('technical-kinetic')
        print(f"\n📚 Loaded {len(references)} style guide references")

        png_bytes, metadata = gen.generate_image_svg(
            description="shelter construction diagram",
            style="technical-kinetic",
            diagram_type="architecture",
            use_pro=False
        )

        assert png_bytes is not None
        assert len(png_bytes) > 0
        print(f"✅ Generated with {len(references)} references: {len(png_bytes)} bytes")


class TestLiveVectorization:
    """Test PNG → SVG vectorization with real images."""

    @pytest.fixture
    def sample_png(self):
        """Generate a sample PNG for testing."""
        gen = GeminiGenerator()
        png_bytes, _ = gen.generate_image_svg(
            description="simple fire triangle",
            style="technical-kinetic",
            diagram_type="schematic",
            use_pro=False
        )
        return png_bytes

    def test_vectorize_with_potrace(self, sample_png):
        """Test vectorization using potrace method."""
        vec = Vectorizer()

        result = vec.vectorize_png(sample_png, method='potrace')

        assert result.svg_content is not None, "SVG content should not be None"
        assert '<svg' in result.svg_content, "Should contain SVG tag"
        assert result.method == 'potrace', f"Expected potrace, got {result.method}"
        assert result.validation is not None, "Should have validation results"

        print(f"\n✅ Vectorized with potrace:")
        print(f"   SVG size: {len(result.svg_content)} chars")
        print(f"   Valid: {result.validation.is_valid}")
        print(f"   Issues: {len(result.validation.issues)} found")

    def test_vectorize_with_vtracer_fallback(self, sample_png):
        """Test vectorization using vtracer fallback method."""
        vec = Vectorizer()

        result = vec.vectorize_png(sample_png, method='vtracer')

        assert result.svg_content is not None
        assert '<svg' in result.svg_content
        assert result.method == 'vtracer', f"Expected vtracer, got {result.method}"

        print(f"\n✅ Vectorized with vtracer:")
        print(f"   SVG size: {len(result.svg_content)} chars")
        print(f"   Valid: {result.validation.is_valid}")

    def test_technical_kinetic_validation(self, sample_png):
        """Test Technical-Kinetic validation on vectorized SVG."""
        vec = Vectorizer()

        result = vec.vectorize_png(sample_png, method='potrace')
        validation = result.validation

        print(f"\n🔍 Technical-Kinetic Validation:")
        print(f"   Is valid: {validation.is_valid}")
        print(f"   Monochrome: {validation.is_monochrome}")
        print(f"   Issues found: {len(validation.issues)}")

        for issue in validation.issues:
            print(f"   ⚠️  {issue}")

        # Validation may have issues but SVG should still be generated
        assert validation is not None


class TestLiveEndToEndPipeline:
    """Test complete PNG → SVG pipeline end-to-end."""

    def test_complete_pipeline_standard_mode(self):
        """Test full pipeline: prompt → PNG → SVG → validate."""
        gen = GeminiGenerator()
        vec = Vectorizer()

        # Step 1: Generate PNG
        print("\n📸 Step 1: Generating PNG...")
        png_bytes, png_metadata = gen.generate_image_svg(
            description="water purification process flowchart",
            style="technical-kinetic",
            diagram_type="flowchart",
            use_pro=False
        )

        assert png_bytes is not None
        print(f"   ✅ PNG generated: {len(png_bytes)} bytes")

        # Step 2: Vectorize to SVG
        print("\n🔄 Step 2: Vectorizing to SVG...")
        result = vec.vectorize_png(png_bytes, method='potrace')

        assert result.svg_content is not None
        assert '<svg' in result.svg_content
        print(f"   ✅ SVG generated: {len(result.svg_content)} chars")

        # Step 3: Validate
        print("\n🔍 Step 3: Validating Technical-Kinetic compliance...")
        validation = result.validation

        print(f"   Is valid: {validation.is_valid}")
        print(f"   Monochrome: {validation.is_monochrome}")
        print(f"   Issues: {len(validation.issues)}")

        assert validation is not None
        print("\n🎉 Pipeline complete!")

    def test_pipeline_with_pro_mode(self):
        """Test pipeline with Pro mode (higher quality, slower)."""
        gen = GeminiGenerator()
        vec = Vectorizer()

        import time
        start_time = time.time()

        # Generate with Pro mode
        print("\n📸 Generating PNG (Pro mode)...")
        png_bytes, metadata = gen.generate_image_svg(
            description="solar water heater diagram",
            style="technical-kinetic",
            diagram_type="architecture",
            use_pro=True
        )

        png_time = time.time() - start_time
        print(f"   ✅ PNG generated in {png_time:.1f}s")

        # Vectorize
        print("\n🔄 Vectorizing...")
        vec_start = time.time()
        result = vec.vectorize_png(png_bytes, method='potrace')
        vec_time = time.time() - vec_start

        print(f"   ✅ SVG generated in {vec_time:.1f}s")

        total_time = time.time() - start_time
        print(f"\n⏱️  Total pipeline time: {total_time:.1f}s")

        # Pro mode should be slower but still reasonable (<90s)
        assert total_time < 90, f"Pipeline too slow: {total_time}s"
        assert result.svg_content is not None


class TestLivePerformance:
    """Test performance metrics and timeouts."""

    def test_standard_mode_performance(self):
        """Verify standard mode completes within 30s."""
        gen = GeminiGenerator()

        import time
        start_time = time.time()

        png_bytes, metadata = gen.generate_image_svg(
            description="simple diagram",
            style="technical-kinetic",
            diagram_type="flowchart",
            use_pro=False
        )

        elapsed = time.time() - start_time
        print(f"\n⏱️  Generation time: {elapsed:.1f}s (target: <30s)")

        assert png_bytes is not None
        assert elapsed < 30, f"Standard mode too slow: {elapsed}s (expected <30s)"

    def test_pro_mode_performance(self):
        """Verify Pro mode completes within 60s."""
        gen = GeminiGenerator()

        import time
        start_time = time.time()

        png_bytes, metadata = gen.generate_image_svg(
            description="complex technical diagram",
            style="technical-kinetic",
            diagram_type="architecture",
            use_pro=True
        )

        elapsed = time.time() - start_time
        print(f"\n⏱️  Pro generation time: {elapsed:.1f}s (target: <60s)")

        assert png_bytes is not None
        # Pro mode can be slower, allow up to 60s
        assert elapsed < 60, f"Pro mode too slow: {elapsed}s (expected <60s)"


# Test runner convenience
if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
