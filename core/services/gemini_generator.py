"""
Gemini Generator Service - v1.6.0
API integration for content and diagram generation with citation tracking

Features:
- Text generation with mandatory citations
- SVG generation (Technical-Kinetic style)
- ASCII/Teletext generation
- Rate limiting and retry logic
- Response validation

Author: uDOS Development Team
Version: 1.6.0
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import google.generativeai as genai
from core.services.citation_manager import get_citation_manager


class GeminiGenerator:
    """Gemini API integration for content generation"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini Generator.

        Args:
            api_key: Gemini API key (defaults to GEMINI_API_KEY env var)
        """
        # Get API key
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment or parameter")

        # Configure Gemini
        genai.configure(api_key=self.api_key)

        # Load prompt templates
        prompts_path = Path("extensions/assistant/gemini_prompts.json")
        if prompts_path.exists():
            with open(prompts_path, 'r') as f:
                self.prompts = json.load(f)
        else:
            raise FileNotFoundError(f"Prompt templates not found: {prompts_path}")

        # Rate limiting
        self.requests_per_minute = 60
        self.request_times: List[float] = []

        # Model configuration
        self.model_name = "gemini-2.5-flash"
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }

    def _check_rate_limit(self) -> None:
        """Enforce rate limiting"""
        now = time.time()

        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if now - t < 60]

        # Check if we've hit the limit
        if len(self.request_times) >= self.requests_per_minute:
            sleep_time = 60 - (now - self.request_times[0])
            if sleep_time > 0:
                time.sleep(sleep_time)

        # Record this request
        self.request_times.append(now)

    def _call_api(self, prompt: str, max_retries: int = 3) -> str:
        """
        Call Gemini API with retry logic.

        Args:
            prompt: Generation prompt
            max_retries: Maximum retry attempts

        Returns:
            Generated content
        """
        self._check_rate_limit()

        model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=self.generation_config
        )

        for attempt in range(max_retries):
            try:
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    time.sleep(wait_time)
                else:
                    raise RuntimeError(f"Gemini API call failed after {max_retries} attempts: {e}")

    def generate_text(self, source_content: str, crawled_content: str = "",
                     topic: str = "") -> Tuple[str, Dict]:
        """
        Generate Markdown content with mandatory citations.

        Args:
            source_content: Source document content
            crawled_content: Web-crawled supplementary content
            topic: Topic/title for the guide

        Returns:
            (generated_markdown, metadata_dict)
        """
        # Get prompt template
        template = self.prompts['prompts']['text_generation']['template']

        # Build prompt
        prompt = template.format(
            source_content=source_content,
            crawled_content=crawled_content if crawled_content else "(no web content)"
        )

        # Generate content
        content = self._call_api(prompt)

        # Validate citations
        cm = get_citation_manager()
        valid, report = cm.validate_citations(content)

        metadata = {
            'topic': topic,
            'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'model': self.model_name,
            'citation_valid': valid,
            'citation_coverage': report['coverage'],
            'word_count': len(content.split()),
            'size_bytes': len(content.encode('utf-8'))
        }

        return content, metadata

    def generate_svg(self, subject: str, diagram_type: str = "flowchart",
                    requirements: List[str] = None) -> Tuple[str, Dict]:
        """
        Generate Technical-Kinetic SVG diagram.

        Args:
            subject: Diagram subject/topic
            diagram_type: Type (flowchart, architecture, organic, schematic)
            requirements: Additional requirements list

        Returns:
            (svg_content, metadata_dict)
        """
        # Get prompt template
        template = self.prompts['prompts']['svg_generation_technical_kinetic']['template']

        # Format requirements
        if requirements:
            req_text = "\n".join(f"- {r}" for r in requirements)
        else:
            req_text = "(standard diagram)"

        # Build prompt
        prompt = template.format(
            diagram_type=diagram_type,
            subject=subject,
            requirements=req_text
        )

        # Generate SVG
        svg_content = self._call_api(prompt)

        # Validate SVG
        is_valid, issues = self._validate_svg(svg_content)

        metadata = {
            'subject': subject,
            'diagram_type': diagram_type,
            'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'model': self.model_name,
            'svg_valid': is_valid,
            'validation_issues': issues,
            'size_bytes': len(svg_content.encode('utf-8'))
        }

        return svg_content, metadata

    def generate_ascii(self, subject: str, max_width: int = 80,
                      max_height: int = 24) -> Tuple[str, Dict]:
        """
        Generate ASCII art diagram.

        Args:
            subject: Diagram subject
            max_width: Maximum width in characters
            max_height: Maximum height in lines

        Returns:
            (ascii_art, metadata_dict)
        """
        template = self.prompts['prompts']['ascii_generation']['template']

        prompt = template.format(subject=subject)
        ascii_art = self._call_api(prompt)

        # Validate dimensions
        lines = ascii_art.split('\n')
        actual_height = len(lines)
        actual_width = max(len(line) for line in lines) if lines else 0

        metadata = {
            'subject': subject,
            'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'width': actual_width,
            'height': actual_height,
            'within_limits': actual_width <= max_width and actual_height <= max_height
        }

        return ascii_art, metadata

    def generate_teletext(self, subject: str) -> Tuple[str, Dict]:
        """
        Generate Teletext HTML graphics.

        Args:
            subject: Graphics subject

        Returns:
            (teletext_html, metadata_dict)
        """
        template = self.prompts['prompts']['teletext_generation']['template']

        prompt = template.format(subject=subject)
        teletext_html = self._call_api(prompt)

        metadata = {
            'subject': subject,
            'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'size_bytes': len(teletext_html.encode('utf-8'))
        }

        return teletext_html, metadata

    def validate_content_quality(self, content: str) -> Dict:
        """
        Validate content quality using Gemini.

        Args:
            content: Content to validate

        Returns:
            Quality report dict
        """
        template = self.prompts['prompts']['quality_validation']['template']

        prompt = template.format(content=content)
        response = self._call_api(prompt)

        # Parse JSON response
        try:
            report = json.loads(response)
        except json.JSONDecodeError:
            # Fallback if response isn't valid JSON
            report = {
                'citation_coverage': 0.0,
                'structure_valid': False,
                'file_size_kb': len(content.encode('utf-8')) / 1024,
                'broken_links': [],
                'readability': 'unknown',
                'issues': ['Failed to parse validation response']
            }

        return report

    def identify_knowledge_gaps(self, source_content: str) -> Dict:
        """
        Identify knowledge gaps for web enrichment.

        Args:
            source_content: Source document content

        Returns:
            Gaps analysis dict
        """
        template = self.prompts['prompts']['web_crawl_enrichment']['template']

        prompt = template.format(source_content=source_content)
        response = self._call_api(prompt)

        # Parse JSON response
        try:
            gaps = json.loads(response)
        except json.JSONDecodeError:
            gaps = {
                'gaps': [],
                'incomplete_sections': [],
                'search_queries': [],
                'suggested_sources': []
            }

        return gaps

    def _validate_svg(self, svg_content: str) -> Tuple[bool, List[str]]:
        """
        Validate SVG Technical-Kinetic compliance.

        Args:
            svg_content: SVG content to validate

        Returns:
            (is_valid, issues_list)
        """
        issues = []

        # Check for SVG tag
        if '<svg' not in svg_content.lower():
            issues.append("Missing <svg> tag")

        # Check for forbidden colors (grays, non-black/white)
        forbidden_patterns = [
            r'fill="(?!#000000|#FFFFFF|black|white|none)',
            r'stroke="(?!#000000|#FFFFFF|black|white|none)',
            r'#[0-9A-Fa-f]{6}(?!000000|FFFFFF)',  # Any hex color except black/white
            'gradient',
            'linearGradient',
            'radialGradient'
        ]

        import re
        for pattern in forbidden_patterns:
            if re.search(pattern, svg_content, re.IGNORECASE):
                issues.append(f"Forbidden color/gradient found: {pattern}")

        # Check size
        size_kb = len(svg_content.encode('utf-8')) / 1024
        if size_kb > 50:
            issues.append(f"SVG too large: {size_kb:.1f}KB (limit: 50KB)")

        # Check for raster images (forbidden)
        if re.search(r'<image|data:image', svg_content, re.IGNORECASE):
            issues.append("Raster images forbidden in Technical-Kinetic style")

        return len(issues) == 0, issues


# Singleton instance
_gemini_generator = None

def get_gemini_generator(api_key: Optional[str] = None) -> GeminiGenerator:
    """Get global Gemini generator instance"""
    global _gemini_generator
    if _gemini_generator is None:
        _gemini_generator = GeminiGenerator(api_key)
    return _gemini_generator


# Example usage
if __name__ == '__main__':
    # Initialize
    try:
        gen = GeminiGenerator()

        # Test text generation
        print("Testing text generation...")
        source = "Water purification is essential for survival. Boiling kills most pathogens."
        content, meta = gen.generate_text(source, topic="Water Purification")
        print(f"Generated {meta['word_count']} words")
        print(f"Citation coverage: {meta['citation_coverage']:.1%}")
        print()

        # Test SVG generation
        print("Testing SVG generation...")
        svg, svg_meta = gen.generate_svg(
            subject="Water filtration system",
            diagram_type="flowchart",
            requirements=["Show water flow", "Label each stage", "Use kinetic conduits"]
        )
        print(f"Generated {svg_meta['size_bytes']} bytes")
        print(f"Valid: {svg_meta['svg_valid']}")
        if svg_meta['validation_issues']:
            print(f"Issues: {svg_meta['validation_issues']}")

    except Exception as e:
        print(f"Error: {e}")
