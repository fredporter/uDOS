"""
Vectorization Service - v1.1.6
Convert PNG line art to clean SVG vectors for Technical-Kinetic compliance

Features:
- Potrace integration (primary vectorizer)
- vtracer fallback (Rust-based)
- Technical-Kinetic validation
- Stroke width normalization
- XML well-formedness checking

Author: uDOS Core Team
Version: 1.1.6
"""

import subprocess
import tempfile
import shutil
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, Dict, Tuple
from dataclasses import dataclass


@dataclass
class VectorizationResult:
    """Result of vectorization operation"""
    svg_content: str
    method: str  # 'potrace' or 'vtracer'
    validation: Dict[str, bool]
    metadata: Dict[str, any]


class VectorizerService:
    """Convert PNG line art to SVG using potrace/vtracer"""

    def __init__(self, logger=None):
        """
        Initialize vectorizer service.

        Args:
            logger: Optional logger instance
        """
        self.logger = logger
        self.potrace_path = self._find_potrace()
        self.vtracer_available = self._check_vtracer()

        if self.logger:
            if self.potrace_path:
                self.logger.info(f"Vectorizer: potrace found at {self.potrace_path}")
            if self.vtracer_available:
                self.logger.info("Vectorizer: vtracer available")
            if not self.potrace_path and not self.vtracer_available:
                self.logger.warning(
                    "No vectorizer found. Install potrace or vtracer for PNG→SVG conversion"
                )

    def vectorize(
        self,
        png_bytes: bytes,
        stroke_width: float = 2.5,
        simplify: bool = True,
        validate_compliance: bool = True
    ) -> VectorizationResult:
        """
        Convert PNG to SVG.

        Args:
            png_bytes: Input PNG image data
            stroke_width: Target stroke width (2-3px for Technical-Kinetic)
            simplify: Simplify paths for cleaner output
            validate_compliance: Check Technical-Kinetic compliance

        Returns:
            VectorizationResult with SVG content and metadata

        Raises:
            RuntimeError: No vectorizer available
            ValueError: Invalid PNG input
        """
        if not png_bytes:
            raise ValueError("Empty PNG data provided")

        # Try potrace first (best quality)
        if self.potrace_path:
            svg_content, metadata = self._vectorize_potrace(
                png_bytes,
                stroke_width,
                simplify
            )
            method = "potrace"

        # Fallback to vtracer
        elif self.vtracer_available:
            svg_content, metadata = self._vectorize_vtracer(
                png_bytes,
                stroke_width
            )
            method = "vtracer"

        else:
            raise RuntimeError(
                "No vectorizer available. Install potrace or vtracer:\n"
                "  macOS:  brew install potrace\n"
                "  Linux:  sudo apt-get install potrace\n"
                "  Python: pip install vtracer"
            )

        # Validate if requested
        validation = {}
        if validate_compliance:
            validation = self.validate_technical_kinetic(svg_content)

        return VectorizationResult(
            svg_content=svg_content,
            method=method,
            validation=validation,
            metadata=metadata
        )

    def _vectorize_potrace(
        self,
        png_bytes: bytes,
        stroke_width: float,
        simplify: bool
    ) -> Tuple[str, Dict]:
        """
        Use potrace for vectorization (highest quality).

        Args:
            png_bytes: PNG image data
            stroke_width: Target stroke width
            simplify: Enable path simplification

        Returns:
            Tuple of (SVG content, metadata dict)
        """
        # Create temp files
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as png_file:
            png_file.write(png_bytes)
            png_path = png_file.name

        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as svg_file:
            svg_path = svg_file.name

        try:
            # Build potrace command
            cmd = [
                str(self.potrace_path),
                "--svg",                 # SVG output
                "--turdsize", "2",       # Remove small artifacts (2px)
                "--alphamax", "1.0" if simplify else "0.0",  # Corner rounding
                "--opttolerance", "0.2", # Path optimization
                "--output", svg_path,
                png_path
            ]

            # Run potrace
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                raise RuntimeError(f"potrace failed: {result.stderr}")

            # Read SVG output
            with open(svg_path, 'r', encoding='utf-8') as f:
                svg_content = f.read()

            # Post-process: set stroke width and clean attributes
            svg_content = self._post_process_svg(svg_content, stroke_width)

            metadata = {
                "vectorizer": "potrace",
                "simplified": simplify,
                "stroke_width": stroke_width,
                "file_size_bytes": len(svg_content)
            }

            return svg_content, metadata

        finally:
            # Cleanup temp files
            Path(png_path).unlink(missing_ok=True)
            Path(svg_path).unlink(missing_ok=True)

    def _vectorize_vtracer(
        self,
        png_bytes: bytes,
        stroke_width: float
    ) -> Tuple[str, Dict]:
        """
        Use vtracer for vectorization (fallback).

        Args:
            png_bytes: PNG image data
            stroke_width: Target stroke width

        Returns:
            Tuple of (SVG content, metadata dict)
        """
        try:
            import vtracer
        except ImportError:
            raise RuntimeError("vtracer not available. Install with: pip install vtracer")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as png_file:
            png_file.write(png_bytes)
            png_path = png_file.name

        try:
            # Convert using vtracer
            svg_str = vtracer.convert_raw_image_to_svg(
                png_path,
                colormode='binary',   # Black & white only
                filter_speckle=4,     # Remove small artifacts
                corner_threshold=60,  # Preserve sharp corners
                mode='spline'         # Smooth curves
            )

            # Post-process
            svg_str = self._post_process_svg(svg_str, stroke_width)

            metadata = {
                "vectorizer": "vtracer",
                "simplified": True,
                "stroke_width": stroke_width,
                "file_size_bytes": len(svg_str)
            }

            return svg_str, metadata

        finally:
            Path(png_path).unlink(missing_ok=True)

    def _post_process_svg(self, svg_content: str, stroke_width: float) -> str:
        """
        Post-process SVG for Technical-Kinetic compliance.

        Args:
            svg_content: Raw SVG content
            stroke_width: Target stroke width

        Returns:
            Cleaned SVG content
        """
        # Parse SVG
        try:
            root = ET.fromstring(svg_content)
        except ET.ParseError:
            # If parsing fails, return as-is with warning
            if self.logger:
                self.logger.warning("SVG parsing failed during post-processing")
            return svg_content

        # Get SVG namespace
        ns = {'svg': 'http://www.w3.org/2000/svg'}
        if root.tag.startswith('{'):
            ns_url = root.tag.split('}')[0][1:]
            ns = {'svg': ns_url}

        # Set stroke properties on all paths
        for path in root.iter():
            if 'path' in path.tag.lower():
                # Set stroke
                path.set('stroke', '#000000')
                path.set('stroke-width', str(stroke_width))

                # Remove fill (Technical-Kinetic uses stroke only)
                current_fill = path.get('fill', '')
                if current_fill and current_fill != 'none':
                    path.set('fill', 'none')

                # Ensure proper stroke properties
                path.set('stroke-linecap', 'round')
                path.set('stroke-linejoin', 'round')

        # Add viewBox if missing
        if 'viewBox' not in root.attrib and 'width' in root.attrib and 'height' in root.attrib:
            width = root.get('width', '800').replace('pt', '').replace('px', '')
            height = root.get('height', '600').replace('pt', '').replace('px', '')
            root.set('viewBox', f"0 0 {width} {height}")

        # Convert back to string
        svg_content = ET.tostring(root, encoding='unicode')

        # Clean up XML declaration if present
        svg_content = svg_content.replace('<?xml version="1.0" encoding="unicode"?>', '')

        # Add proper XML declaration
        if not svg_content.startswith('<?xml'):
            svg_content = '<?xml version="1.0" encoding="UTF-8"?>\n' + svg_content

        return svg_content

    def validate_technical_kinetic(self, svg_content: str) -> Dict[str, any]:
        """
        Validate Technical-Kinetic compliance.

        Checks:
        - Valid XML
        - No forbidden elements (gradient, filter, pattern, image, raster)
        - Monochrome only (black/white)
        - No gray fills or gradients

        Args:
            svg_content: SVG content to validate

        Returns:
            Dict with validation results
        """
        validation = {
            "valid_xml": False,
            "no_forbidden_elements": False,
            "monochrome_only": False,
            "no_gradients": False,
            "compliant": False,
            "errors": []
        }

        # Check XML well-formedness
        try:
            root = ET.fromstring(svg_content)
            validation["valid_xml"] = True
        except ET.ParseError as e:
            validation["errors"].append(f"XML parse error: {str(e)}")
            return validation

        # Check for forbidden elements
        forbidden = ["linearGradient", "radialGradient", "filter", "pattern", "image"]
        ns = root.tag.split('}')[0][1:] if root.tag.startswith('{') else ''

        forbidden_found = []
        for elem_name in forbidden:
            # Check both with and without namespace
            found = root.findall(f".//{elem_name}") or \
                    root.findall(f".//{{{ns}}}{elem_name}")
            if found:
                forbidden_found.append(elem_name)

        validation["no_forbidden_elements"] = len(forbidden_found) == 0
        if forbidden_found:
            validation["errors"].append(f"Forbidden elements: {', '.join(forbidden_found)}")

        # Check colors (should only be #000000, #FFFFFF, or 'none')
        allowed_colors = [
            "#000000", "#000", "black",
            "#FFFFFF", "#FFF", "white",
            "none", ""
        ]

        invalid_colors = []
        for elem in root.iter():
            for attr in ["stroke", "fill", "stop-color"]:
                color = elem.get(attr, "").lower()
                if color and color not in allowed_colors:
                    invalid_colors.append(f"{elem.tag}[@{attr}='{color}']")

        validation["monochrome_only"] = len(invalid_colors) == 0
        if invalid_colors:
            validation["errors"].append(
                f"Invalid colors: {', '.join(set(invalid_colors[:5]))}"
            )

        # Check for gradients (should already be caught above)
        validation["no_gradients"] = "gradient" not in forbidden_found

        # Overall compliance
        validation["compliant"] = (
            validation["valid_xml"] and
            validation["no_forbidden_elements"] and
            validation["monochrome_only"] and
            validation["no_gradients"]
        )

        return validation

    def _find_potrace(self) -> Optional[Path]:
        """
        Locate potrace binary.

        Returns:
            Path to potrace or None
        """
        potrace = shutil.which("potrace")
        return Path(potrace) if potrace else None

    def _check_vtracer(self) -> bool:
        """
        Check if vtracer is available.

        Returns:
            True if vtracer can be imported
        """
        try:
            import vtracer
            return True
        except ImportError:
            return False

    def get_capabilities(self) -> Dict[str, bool]:
        """
        Get vectorizer capabilities.

        Returns:
            Dict with available vectorizers
        """
        return {
            "potrace": self.potrace_path is not None,
            "vtracer": self.vtracer_available,
            "any_available": self.potrace_path is not None or self.vtracer_available
        }


def get_vectorizer_service(logger=None) -> VectorizerService:
    """
    Get singleton vectorizer service instance.

    Args:
        logger: Optional logger instance

    Returns:
        VectorizerService instance
    """
    if not hasattr(get_vectorizer_service, '_instance'):
        get_vectorizer_service._instance = VectorizerService(logger=logger)
    return get_vectorizer_service._instance
