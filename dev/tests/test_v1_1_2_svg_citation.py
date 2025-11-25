"""
Test Suite for Feature 1.1.2.8: SVG/Citation Pipeline Integration
v1.1.2 Phase 2: Knowledge Bank & AI Integration

Tests SVG diagram generation, citation extraction, reference management,
bibliography formatting, cross-referencing, diagram versioning, and export formats.

Test Categories:
1. SVG Generation (6 tests)
2. Citation Extraction (6 tests)
3. Reference Management (6 tests)
4. Bibliography Formatting (5 tests)
5. Cross-Referencing (5 tests)
6. Diagram Versioning (5 tests)
7. Export Formats (5 tests)
8. Citation Validation (5 tests)
9. SVG Optimization (4 tests)
10. Reference Linking (5 tests)
11. Citation Styles (4 tests)
12. Integration Scenarios (3 tests)

Total: 59 tests
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import re
from datetime import datetime
from enum import Enum


class CitationStyle(Enum):
    """Citation style enumeration."""
    APA = "apa"
    MLA = "mla"
    CHICAGO = "chicago"
    IEEE = "ieee"


class ExportFormat(Enum):
    """Export format enumeration."""
    SVG = "svg"
    PNG = "png"
    PDF = "pdf"
    JSON = "json"


class SVGCitationPipeline:
    """SVG diagram and citation management pipeline."""

    def __init__(self):
        self.diagrams = {}
        self.citations = {}
        self.references = {}
        self.bibliographies = {}
        self.cross_refs = {}
        self.diagram_versions = {}

    def generate_svg(self, diagram_id, elements, width=800, height=600):
        """Generate SVG diagram from elements."""
        svg_content = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">\n'

        for element in elements:
            if element["type"] == "rect":
                svg_content += f'  <rect x="{element["x"]}" y="{element["y"]}" '
                svg_content += f'width="{element["width"]}" height="{element["height"]}" '
                svg_content += f'fill="{element.get("fill", "black")}" />\n'

            elif element["type"] == "circle":
                svg_content += f'  <circle cx="{element["cx"]}" cy="{element["cy"]}" '
                svg_content += f'r="{element["r"]}" fill="{element.get("fill", "black")}" />\n'

            elif element["type"] == "text":
                svg_content += f'  <text x="{element["x"]}" y="{element["y"]}" '
                svg_content += f'font-size="{element.get("size", 16)}">{element["text"]}</text>\n'

            elif element["type"] == "line":
                svg_content += f'  <line x1="{element["x1"]}" y1="{element["y1"]}" '
                svg_content += f'x2="{element["x2"]}" y2="{element["y2"]}" '
                svg_content += f'stroke="{element.get("stroke", "black")}" />\n'

        svg_content += '</svg>'

        # Check if diagram already exists (updating)
        if diagram_id in self.diagrams:
            # Update existing diagram's content only, preserve version
            diagram = self.diagrams[diagram_id]
            diagram["content"] = svg_content
            diagram["width"] = width
            diagram["height"] = height
        else:
            # Create new diagram
            diagram = {
                "id": diagram_id,
                "content": svg_content,
                "width": width,
                "height": height,
                "elements": elements,
                "created_at": datetime.now().isoformat(),
                "version": 1
            }

            self.diagrams[diagram_id] = diagram
            self._track_diagram_version(diagram_id, 1, "Initial version")

        return diagram_id

    def get_diagram(self, diagram_id):
        """Get SVG diagram."""
        if diagram_id not in self.diagrams:
            raise KeyError(f"Diagram not found: {diagram_id}")

        return self.diagrams[diagram_id].copy()

    def update_diagram(self, diagram_id, elements=None, width=None, height=None):
        """Update SVG diagram."""
        if diagram_id not in self.diagrams:
            raise KeyError(f"Diagram not found: {diagram_id}")

        diagram = self.diagrams[diagram_id]

        # Increment version for any update
        new_version = diagram["version"] + 1
        diagram["version"] = new_version

        if elements is not None:
            diagram["elements"] = elements
            # Regenerate SVG content
            self.generate_svg(diagram_id, elements,
                            width or diagram["width"],
                            height or diagram["height"])

        if width is not None:
            diagram["width"] = width

        if height is not None:
            diagram["height"] = height

        diagram["updated_at"] = datetime.now().isoformat()

        self._track_diagram_version(diagram_id, new_version, "Updated")

        return new_version

    def extract_citations(self, text):
        """Extract citations from text."""
        # Match patterns like [Author, Year] or (Author Year)
        patterns = [
            r'\[([^\]]+),\s*(\d{4})\]',  # [Author, 2024]
            r'\(([^,]+),\s*(\d{4})\)',   # (Author, 2024)
            r'\[(\d+)\]'                  # [1]
        ]

        citations = []

        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple) and len(match) == 2:
                    citations.append({
                        "author": match[0].strip(),
                        "year": match[1],
                        "type": "author-year"
                    })
                elif isinstance(match, str):
                    # Numeric citation [1]
                    citations.append({
                        "number": match,
                            "type": "numeric"
                        })

        return citations

    def add_citation(self, citation_id, author, year, title, source=None, url=None):
        """Add citation to library."""
        citation = {
            "id": citation_id,
            "author": author,
            "year": year,
            "title": title,
            "source": source,
            "url": url,
            "added_at": datetime.now().isoformat()
        }

        self.citations[citation_id] = citation
        return citation_id

    def get_citation(self, citation_id):
        """Get citation by ID."""
        if citation_id not in self.citations:
            raise KeyError(f"Citation not found: {citation_id}")

        return self.citations[citation_id].copy()

    def add_reference(self, ref_id, citation_id, context=None):
        """Add reference to citation."""
        if citation_id not in self.citations:
            raise KeyError(f"Citation not found: {citation_id}")

        reference = {
            "id": ref_id,
            "citation_id": citation_id,
            "context": context,
            "created_at": datetime.now().isoformat()
        }

        self.references[ref_id] = reference
        return ref_id

    def get_references_for_citation(self, citation_id):
        """Get all references for a citation."""
        refs = []
        for ref_id, ref in self.references.items():
            if ref["citation_id"] == citation_id:
                refs.append(ref)

        return refs

    def format_bibliography(self, citation_ids, style=CitationStyle.APA):
        """Format bibliography in specified style."""
        if not isinstance(style, CitationStyle):
            raise ValueError(f"Invalid citation style: {style}")

        entries = []

        for cid in citation_ids:
            if cid not in self.citations:
                continue

            citation = self.citations[cid]

            if style == CitationStyle.APA:
                entry = self._format_apa(citation)
            elif style == CitationStyle.MLA:
                entry = self._format_mla(citation)
            elif style == CitationStyle.CHICAGO:
                entry = self._format_chicago(citation)
            elif style == CitationStyle.IEEE:
                entry = self._format_ieee(citation)
            else:
                entry = str(citation)

            entries.append(entry)

        bibliography = {
            "style": style.value,
            "entries": entries,
            "count": len(entries),
            "generated_at": datetime.now().isoformat()
        }

        return bibliography

    def _format_apa(self, citation):
        """Format citation in APA style."""
        return f"{citation['author']} ({citation['year']}). {citation['title']}."

    def _format_mla(self, citation):
        """Format citation in MLA style."""
        return f"{citation['author']}. \"{citation['title']}.\" {citation['year']}."

    def _format_chicago(self, citation):
        """Format citation in Chicago style."""
        return f"{citation['author']}. {citation['title']}. {citation['year']}."

    def _format_ieee(self, citation):
        """Format citation in IEEE style."""
        return f"{citation['author']}, \"{citation['title']},\" {citation['year']}."

    def create_cross_reference(self, from_id, to_id, ref_type="related"):
        """Create cross-reference between items."""
        if from_id not in self.cross_refs:
            self.cross_refs[from_id] = []

        self.cross_refs[from_id].append({
            "to": to_id,
            "type": ref_type,
            "created_at": datetime.now().isoformat()
        })

        return True

    def get_cross_references(self, item_id):
        """Get cross-references for item."""
        return self.cross_refs.get(item_id, []).copy()

    def _track_diagram_version(self, diagram_id, version, note):
        """Track diagram version."""
        if diagram_id not in self.diagram_versions:
            self.diagram_versions[diagram_id] = []

        self.diagram_versions[diagram_id].append({
            "version": version,
            "note": note,
            "timestamp": datetime.now().isoformat()
        })

    def get_diagram_version_history(self, diagram_id):
        """Get diagram version history."""
        return self.diagram_versions.get(diagram_id, []).copy()

    def export_diagram(self, diagram_id, format=ExportFormat.SVG):
        """Export diagram in specified format."""
        if not isinstance(format, ExportFormat):
            raise ValueError(f"Invalid export format: {format}")

        diagram = self.get_diagram(diagram_id)

        export_data = {
            "id": diagram_id,
            "format": format.value,
            "exported_at": datetime.now().isoformat()
        }

        if format == ExportFormat.SVG:
            export_data["content"] = diagram["content"]
            export_data["mime_type"] = "image/svg+xml"

        elif format == ExportFormat.PNG:
            # Simulate PNG conversion
            export_data["content"] = f"<PNG_DATA:{diagram_id}>"
            export_data["mime_type"] = "image/png"

        elif format == ExportFormat.PDF:
            # Simulate PDF conversion
            export_data["content"] = f"<PDF_DATA:{diagram_id}>"
            export_data["mime_type"] = "application/pdf"

        elif format == ExportFormat.JSON:
            export_data["content"] = json.dumps(diagram, indent=2)
            export_data["mime_type"] = "application/json"

        return export_data

    def validate_citation(self, citation_id):
        """Validate citation completeness."""
        if citation_id not in self.citations:
            raise KeyError(f"Citation not found: {citation_id}")

        citation = self.citations[citation_id]

        validation = {
            "valid": True,
            "errors": [],
            "warnings": []
        }

        # Required fields
        if not citation.get("author"):
            validation["valid"] = False
            validation["errors"].append("Missing author")

        if not citation.get("year"):
            validation["valid"] = False
            validation["errors"].append("Missing year")

        if not citation.get("title"):
            validation["valid"] = False
            validation["errors"].append("Missing title")

        # Optional fields
        if not citation.get("source"):
            validation["warnings"].append("Missing source")

        if not citation.get("url"):
            validation["warnings"].append("Missing URL")

        # Year format
        try:
            year = int(citation.get("year", "0"))
            if year < 1000 or year > 2100:
                validation["warnings"].append("Year seems unusual")
        except ValueError:
            validation["valid"] = False
            validation["errors"].append("Invalid year format")

        return validation

    def optimize_svg(self, diagram_id):
        """Optimize SVG diagram."""
        diagram = self.get_diagram(diagram_id)

        optimizations = {
            "original_size": len(diagram["content"]),
            "optimized_size": 0,
            "savings": 0,
            "optimizations_applied": []
        }

        content = diagram["content"]

        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        optimizations["optimizations_applied"].append("whitespace_removal")

        # Remove unnecessary precision
        content = re.sub(r'(\d+\.\d{3,})', lambda m: f"{float(m.group(1)):.2f}", content)
        optimizations["optimizations_applied"].append("precision_reduction")

        optimizations["optimized_size"] = len(content)
        optimizations["savings"] = optimizations["original_size"] - optimizations["optimized_size"]
        optimizations["savings_percent"] = round(
            (optimizations["savings"] / optimizations["original_size"]) * 100, 2
        ) if optimizations["original_size"] > 0 else 0

        # Update diagram
        diagram["content"] = content
        diagram["optimized"] = True

        return optimizations

    def link_diagram_to_citation(self, diagram_id, citation_id):
        """Link diagram to citation."""
        if diagram_id not in self.diagrams:
            raise KeyError(f"Diagram not found: {diagram_id}")

        if citation_id not in self.citations:
            raise KeyError(f"Citation not found: {citation_id}")

        diagram = self.diagrams[diagram_id]

        if "citations" not in diagram:
            diagram["citations"] = []

        if citation_id not in diagram["citations"]:
            diagram["citations"].append(citation_id)

        return True

    def get_diagram_citations(self, diagram_id):
        """Get citations linked to diagram."""
        if diagram_id not in self.diagrams:
            raise KeyError(f"Diagram not found: {diagram_id}")

        diagram = self.diagrams[diagram_id]
        citation_ids = diagram.get("citations", [])

        citations = []
        for cid in citation_ids:
            if cid in self.citations:
                citations.append(self.citations[cid])

        return citations

    def search_citations(self, query):
        """Search citations by author or title."""
        query_lower = query.lower()
        results = []

        for cid, citation in self.citations.items():
            if (query_lower in citation.get("author", "").lower() or
                query_lower in citation.get("title", "").lower()):
                results.append(cid)

        return results

    def generate_citation_key(self, author, year):
        """Generate citation key."""
        # Format: AuthorLastName2024
        # Handle "LastName, FirstName" or "FirstName LastName" formats
        if "," in author:
            author_key = author.split(",")[0].strip()  # Take last name before comma
        elif " " in author:
            author_key = author.split()[-1]  # Take last word
        else:
            author_key = author

        author_key = re.sub(r'[^a-zA-Z]', '', author_key)
        return f"{author_key}{year}"

    def get_pipeline_stats(self):
        """Get pipeline statistics."""
        return {
            "total_diagrams": len(self.diagrams),
            "total_citations": len(self.citations),
            "total_references": len(self.references),
            "total_cross_refs": sum(len(refs) for refs in self.cross_refs.values())
        }


class TestSVGGeneration(unittest.TestCase):
    """Test SVG diagram generation."""

    def setUp(self):
        self.pipeline = SVGCitationPipeline()

    def test_generate_simple_svg(self):
        """Test generating simple SVG."""
        elements = [
            {"type": "rect", "x": 10, "y": 10, "width": 100, "height": 50, "fill": "blue"}
        ]

        diagram_id = self.pipeline.generate_svg("test1", elements)

        self.assertIn(diagram_id, self.pipeline.diagrams)

        diagram = self.pipeline.get_diagram(diagram_id)
        self.assertIn("<svg", diagram["content"])
        self.assertIn("<rect", diagram["content"])

    def test_svg_with_multiple_elements(self):
        """Test SVG with multiple elements."""
        elements = [
            {"type": "circle", "cx": 50, "cy": 50, "r": 25, "fill": "red"},
            {"type": "text", "x": 30, "y": 55, "text": "Hello", "size": 14}
        ]

        diagram_id = self.pipeline.generate_svg("test2", elements)
        diagram = self.pipeline.get_diagram(diagram_id)

        self.assertIn("<circle", diagram["content"])
        self.assertIn("<text", diagram["content"])
        self.assertIn("Hello", diagram["content"])

    def test_svg_dimensions(self):
        """Test SVG dimensions."""
        diagram_id = self.pipeline.generate_svg("test3", [], width=1000, height=800)
        diagram = self.pipeline.get_diagram(diagram_id)

        self.assertEqual(diagram["width"], 1000)
        self.assertEqual(diagram["height"], 800)
        self.assertIn('width="1000"', diagram["content"])

    def test_svg_with_line(self):
        """Test SVG with line element."""
        elements = [
            {"type": "line", "x1": 0, "y1": 0, "x2": 100, "y2": 100, "stroke": "black"}
        ]

        diagram_id = self.pipeline.generate_svg("test4", elements)
        diagram = self.pipeline.get_diagram(diagram_id)

        self.assertIn("<line", diagram["content"])
        self.assertIn('stroke="black"', diagram["content"])

    def test_svg_element_defaults(self):
        """Test SVG element default values."""
        elements = [
            {"type": "rect", "x": 0, "y": 0, "width": 50, "height": 50}
        ]

        diagram_id = self.pipeline.generate_svg("test5", elements)
        diagram = self.pipeline.get_diagram(diagram_id)

        self.assertIn('fill="black"', diagram["content"])

    def test_svg_version_tracking(self):
        """Test SVG version is tracked."""
        diagram_id = self.pipeline.generate_svg("test6", [])
        diagram = self.pipeline.get_diagram(diagram_id)

        self.assertEqual(diagram["version"], 1)


class TestCitationExtraction(unittest.TestCase):
    """Test citation extraction."""

    def setUp(self):
        self.pipeline = SVGCitationPipeline()

    def test_extract_author_year_citation(self):
        """Test extracting [Author, Year] citations."""
        text = "According to research [Smith, 2024], this is true."

        citations = self.pipeline.extract_citations(text)

        self.assertEqual(len(citations), 1)
        self.assertEqual(citations[0]["author"], "Smith")
        self.assertEqual(citations[0]["year"], "2024")

    def test_extract_parenthetical_citation(self):
        """Test extracting (Author, Year) citations."""
        text = "This finding (Jones, 2023) supports the theory."

        citations = self.pipeline.extract_citations(text)

        self.assertEqual(len(citations), 1)
        self.assertEqual(citations[0]["author"], "Jones")

    def test_extract_numeric_citation(self):
        """Test extracting [1] numeric citations."""
        text = "As shown in previous work [1]."

        citations = self.pipeline.extract_citations(text)

        self.assertEqual(len(citations), 1)
        self.assertEqual(citations[0]["type"], "numeric")

    def test_extract_multiple_citations(self):
        """Test extracting multiple citations."""
        text = "Research [Smith, 2024] and [Jones, 2023] shows this."

        citations = self.pipeline.extract_citations(text)

        self.assertEqual(len(citations), 2)

    def test_no_citations(self):
        """Test text with no citations."""
        text = "This text has no citations."

        citations = self.pipeline.extract_citations(text)

        self.assertEqual(len(citations), 0)

    def test_citation_type_identification(self):
        """Test citation type is identified."""
        text = "[Author, 2024]"

        citations = self.pipeline.extract_citations(text)

        self.assertEqual(citations[0]["type"], "author-year")


class TestReferenceManagement(unittest.TestCase):
    """Test reference management."""

    def setUp(self):
        self.pipeline = SVGCitationPipeline()

    def test_add_citation(self):
        """Test adding citation."""
        citation_id = self.pipeline.add_citation(
            "cite1",
            "Smith, J.",
            "2024",
            "Test Article"
        )

        self.assertIn(citation_id, self.pipeline.citations)

    def test_get_citation(self):
        """Test getting citation."""
        self.pipeline.add_citation(
            "cite2",
            "Jones, A.",
            "2023",
            "Research Paper",
            source="Journal of Testing"
        )

        citation = self.pipeline.get_citation("cite2")

        self.assertEqual(citation["author"], "Jones, A.")
        self.assertEqual(citation["source"], "Journal of Testing")

    def test_add_reference(self):
        """Test adding reference to citation."""
        citation_id = self.pipeline.add_citation(
            "cite3",
            "Author",
            "2024",
            "Title"
        )

        ref_id = self.pipeline.add_reference(
            "ref1",
            citation_id,
            context="Introduction section"
        )

        self.assertIn(ref_id, self.pipeline.references)

    def test_get_references_for_citation(self):
        """Test getting references for citation."""
        citation_id = self.pipeline.add_citation("cite4", "Author", "2024", "Title")

        self.pipeline.add_reference("ref2", citation_id)
        self.pipeline.add_reference("ref3", citation_id)

        refs = self.pipeline.get_references_for_citation(citation_id)

        self.assertEqual(len(refs), 2)

    def test_reference_with_context(self):
        """Test reference includes context."""
        citation_id = self.pipeline.add_citation("cite5", "Author", "2024", "Title")

        self.pipeline.add_reference("ref4", citation_id, context="Methods section")

        ref = self.pipeline.references["ref4"]
        self.assertEqual(ref["context"], "Methods section")

    def test_citation_not_found(self):
        """Test getting non-existent citation."""
        with self.assertRaises(KeyError):
            self.pipeline.get_citation("nonexistent")


class TestBibliographyFormatting(unittest.TestCase):
    """Test bibliography formatting."""

    def setUp(self):
        self.pipeline = SVGCitationPipeline()

        # Add test citations
        self.pipeline.add_citation("cite1", "Smith, J.", "2024", "Test Article")
        self.pipeline.add_citation("cite2", "Jones, A.", "2023", "Research Paper")

    def test_format_apa_bibliography(self):
        """Test APA bibliography formatting."""
        bib = self.pipeline.format_bibliography(["cite1"], CitationStyle.APA)

        self.assertEqual(bib["style"], "apa")
        self.assertIn("Smith, J. (2024)", bib["entries"][0])

    def test_format_mla_bibliography(self):
        """Test MLA bibliography formatting."""
        bib = self.pipeline.format_bibliography(["cite1"], CitationStyle.MLA)

        self.assertEqual(bib["style"], "mla")
        self.assertIn("Smith, J.", bib["entries"][0])

    def test_format_chicago_bibliography(self):
        """Test Chicago bibliography formatting."""
        bib = self.pipeline.format_bibliography(["cite1"], CitationStyle.CHICAGO)

        self.assertEqual(bib["style"], "chicago")
        self.assertGreater(len(bib["entries"]), 0)

    def test_format_ieee_bibliography(self):
        """Test IEEE bibliography formatting."""
        bib = self.pipeline.format_bibliography(["cite1"], CitationStyle.IEEE)

        self.assertEqual(bib["style"], "ieee")
        self.assertGreater(len(bib["entries"]), 0)

    def test_bibliography_multiple_entries(self):
        """Test bibliography with multiple entries."""
        bib = self.pipeline.format_bibliography(["cite1", "cite2"], CitationStyle.APA)

        self.assertEqual(bib["count"], 2)
        self.assertEqual(len(bib["entries"]), 2)


class TestCrossReferencing(unittest.TestCase):
    """Test cross-referencing."""

    def setUp(self):
        self.pipeline = SVGCitationPipeline()

    def test_create_cross_reference(self):
        """Test creating cross-reference."""
        self.pipeline.create_cross_reference("item1", "item2", "related")

        refs = self.pipeline.get_cross_references("item1")

        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0]["to"], "item2")
        self.assertEqual(refs[0]["type"], "related")

    def test_multiple_cross_references(self):
        """Test multiple cross-references."""
        self.pipeline.create_cross_reference("item1", "item2")
        self.pipeline.create_cross_reference("item1", "item3")

        refs = self.pipeline.get_cross_references("item1")

        self.assertEqual(len(refs), 2)

    def test_cross_reference_types(self):
        """Test different cross-reference types."""
        self.pipeline.create_cross_reference("item1", "item2", "prerequisite")

        refs = self.pipeline.get_cross_references("item1")

        self.assertEqual(refs[0]["type"], "prerequisite")

    def test_no_cross_references(self):
        """Test item with no cross-references."""
        refs = self.pipeline.get_cross_references("nonexistent")

        self.assertEqual(len(refs), 0)

    def test_cross_reference_timestamp(self):
        """Test cross-reference has timestamp."""
        self.pipeline.create_cross_reference("item1", "item2")

        refs = self.pipeline.get_cross_references("item1")

        self.assertIn("created_at", refs[0])


class TestDiagramVersioning(unittest.TestCase):
    """Test diagram versioning."""

    def setUp(self):
        self.pipeline = SVGCitationPipeline()

    def test_initial_version(self):
        """Test initial diagram version."""
        diagram_id = self.pipeline.generate_svg("ver1", [])
        diagram = self.pipeline.get_diagram(diagram_id)

        self.assertEqual(diagram["version"], 1)

    def test_version_increment(self):
        """Test version increments on update."""
        diagram_id = self.pipeline.generate_svg("ver2", [])

        new_version = self.pipeline.update_diagram(
            diagram_id,
            elements=[{"type": "rect", "x": 0, "y": 0, "width": 10, "height": 10}]
        )

        self.assertEqual(new_version, 2)

    def test_version_history(self):
        """Test version history tracking."""
        diagram_id = self.pipeline.generate_svg("ver3", [])
        self.pipeline.update_diagram(diagram_id, width=1000)

        history = self.pipeline.get_diagram_version_history(diagram_id)

        self.assertGreater(len(history), 0)

    def test_version_history_metadata(self):
        """Test version history includes metadata."""
        diagram_id = self.pipeline.generate_svg("ver4", [])

        history = self.pipeline.get_diagram_version_history(diagram_id)

        self.assertIn("timestamp", history[0])
        self.assertIn("note", history[0])

    def test_multiple_updates(self):
        """Test multiple updates increment version."""
        diagram_id = self.pipeline.generate_svg("ver5", [])

        self.pipeline.update_diagram(diagram_id, width=800)
        self.pipeline.update_diagram(diagram_id, height=600)

        diagram = self.pipeline.get_diagram(diagram_id)
        self.assertEqual(diagram["version"], 3)


class TestExportFormats(unittest.TestCase):
    """Test export formats."""

    def setUp(self):
        self.pipeline = SVGCitationPipeline()

        elements = [{"type": "rect", "x": 0, "y": 0, "width": 100, "height": 100}]
        self.diagram_id = self.pipeline.generate_svg("export1", elements)

    def test_export_svg(self):
        """Test exporting as SVG."""
        export = self.pipeline.export_diagram(self.diagram_id, ExportFormat.SVG)

        self.assertEqual(export["format"], "svg")
        self.assertEqual(export["mime_type"], "image/svg+xml")
        self.assertIn("<svg", export["content"])

    def test_export_png(self):
        """Test exporting as PNG."""
        export = self.pipeline.export_diagram(self.diagram_id, ExportFormat.PNG)

        self.assertEqual(export["format"], "png")
        self.assertEqual(export["mime_type"], "image/png")

    def test_export_pdf(self):
        """Test exporting as PDF."""
        export = self.pipeline.export_diagram(self.diagram_id, ExportFormat.PDF)

        self.assertEqual(export["format"], "pdf")
        self.assertEqual(export["mime_type"], "application/pdf")

    def test_export_json(self):
        """Test exporting as JSON."""
        export = self.pipeline.export_diagram(self.diagram_id, ExportFormat.JSON)

        self.assertEqual(export["format"], "json")
        self.assertEqual(export["mime_type"], "application/json")

        # Should be valid JSON
        data = json.loads(export["content"])
        self.assertIn("id", data)

    def test_export_includes_metadata(self):
        """Test export includes metadata."""
        export = self.pipeline.export_diagram(self.diagram_id, ExportFormat.SVG)

        self.assertIn("exported_at", export)
        self.assertIn("id", export)


class TestCitationValidation(unittest.TestCase):
    """Test citation validation."""

    def setUp(self):
        self.pipeline = SVGCitationPipeline()

    def test_validate_complete_citation(self):
        """Test validating complete citation."""
        citation_id = self.pipeline.add_citation(
            "val1",
            "Author",
            "2024",
            "Title",
            source="Journal",
            url="http://example.com"
        )

        validation = self.pipeline.validate_citation(citation_id)

        self.assertTrue(validation["valid"])

    def test_validate_missing_author(self):
        """Test validation detects missing author."""
        citation_id = self.pipeline.add_citation(
            "val2",
            "",
            "2024",
            "Title"
        )

        validation = self.pipeline.validate_citation(citation_id)

        self.assertFalse(validation["valid"])
        self.assertIn("Missing author", validation["errors"])

    def test_validate_missing_year(self):
        """Test validation detects missing year."""
        citation_id = self.pipeline.add_citation(
            "val3",
            "Author",
            "",
            "Title"
        )

        validation = self.pipeline.validate_citation(citation_id)

        self.assertFalse(validation["valid"])

    def test_validate_missing_optional_fields(self):
        """Test validation warns about missing optional fields."""
        citation_id = self.pipeline.add_citation(
            "val4",
            "Author",
            "2024",
            "Title"
        )

        validation = self.pipeline.validate_citation(citation_id)

        self.assertGreater(len(validation["warnings"]), 0)

    def test_validate_invalid_year(self):
        """Test validation detects invalid year."""
        citation_id = self.pipeline.add_citation(
            "val5",
            "Author",
            "invalid",
            "Title"
        )

        validation = self.pipeline.validate_citation(citation_id)

        self.assertFalse(validation["valid"])


class TestSVGOptimization(unittest.TestCase):
    """Test SVG optimization."""

    def setUp(self):
        self.pipeline = SVGCitationPipeline()

    def test_optimize_svg(self):
        """Test SVG optimization."""
        elements = [
            {"type": "rect", "x": 10, "y": 10, "width": 100, "height": 50}
        ]
        diagram_id = self.pipeline.generate_svg("opt1", elements)

        result = self.pipeline.optimize_svg(diagram_id)

        self.assertIn("original_size", result)
        self.assertIn("optimized_size", result)

    def test_optimization_reduces_size(self):
        """Test optimization reduces size."""
        # Create diagram with extra whitespace
        elements = [{"type": "rect", "x": 10, "y": 10, "width": 100, "height": 50}]
        diagram_id = self.pipeline.generate_svg("opt2", elements)

        result = self.pipeline.optimize_svg(diagram_id)

        self.assertLessEqual(result["optimized_size"], result["original_size"])

    def test_optimization_tracking(self):
        """Test optimizations are tracked."""
        diagram_id = self.pipeline.generate_svg("opt3", [])

        result = self.pipeline.optimize_svg(diagram_id)

        self.assertIn("optimizations_applied", result)
        self.assertGreater(len(result["optimizations_applied"]), 0)

    def test_optimization_percentage(self):
        """Test optimization percentage calculation."""
        diagram_id = self.pipeline.generate_svg("opt4", [])

        result = self.pipeline.optimize_svg(diagram_id)

        self.assertIn("savings_percent", result)
        self.assertGreaterEqual(result["savings_percent"], 0)


class TestReferenceLinking(unittest.TestCase):
    """Test reference linking."""

    def setUp(self):
        self.pipeline = SVGCitationPipeline()

    def test_link_diagram_to_citation(self):
        """Test linking diagram to citation."""
        diagram_id = self.pipeline.generate_svg("link1", [])
        citation_id = self.pipeline.add_citation("cite1", "Author", "2024", "Title")

        linked = self.pipeline.link_diagram_to_citation(diagram_id, citation_id)

        self.assertTrue(linked)

    def test_get_diagram_citations(self):
        """Test getting citations for diagram."""
        diagram_id = self.pipeline.generate_svg("link2", [])
        citation_id = self.pipeline.add_citation("cite2", "Author", "2024", "Title")

        self.pipeline.link_diagram_to_citation(diagram_id, citation_id)

        citations = self.pipeline.get_diagram_citations(diagram_id)

        self.assertEqual(len(citations), 1)
        self.assertEqual(citations[0]["id"], citation_id)

    def test_multiple_citations_per_diagram(self):
        """Test multiple citations per diagram."""
        diagram_id = self.pipeline.generate_svg("link3", [])
        cite1 = self.pipeline.add_citation("c1", "Author1", "2024", "Title1")
        cite2 = self.pipeline.add_citation("c2", "Author2", "2024", "Title2")

        self.pipeline.link_diagram_to_citation(diagram_id, cite1)
        self.pipeline.link_diagram_to_citation(diagram_id, cite2)

        citations = self.pipeline.get_diagram_citations(diagram_id)

        self.assertEqual(len(citations), 2)

    def test_search_citations(self):
        """Test searching citations."""
        self.pipeline.add_citation("s1", "Smith", "2024", "Research")
        self.pipeline.add_citation("s2", "Jones", "2023", "Study")

        results = self.pipeline.search_citations("Smith")

        self.assertIn("s1", results)
        self.assertNotIn("s2", results)

    def test_generate_citation_key(self):
        """Test generating citation key."""
        key = self.pipeline.generate_citation_key("Smith, John", "2024")

        self.assertEqual(key, "Smith2024")


class TestCitationStyles(unittest.TestCase):
    """Test citation styles."""

    def setUp(self):
        self.pipeline = SVGCitationPipeline()
        self.citation_id = self.pipeline.add_citation(
            "style1",
            "Smith, J.",
            "2024",
            "Test Article"
        )

    def test_apa_style(self):
        """Test APA citation style."""
        citation = self.pipeline.get_citation(self.citation_id)
        formatted = self.pipeline._format_apa(citation)

        self.assertIn("Smith, J. (2024)", formatted)

    def test_mla_style(self):
        """Test MLA citation style."""
        citation = self.pipeline.get_citation(self.citation_id)
        formatted = self.pipeline._format_mla(citation)

        self.assertIn("Smith, J.", formatted)
        self.assertIn("2024", formatted)

    def test_chicago_style(self):
        """Test Chicago citation style."""
        citation = self.pipeline.get_citation(self.citation_id)
        formatted = self.pipeline._format_chicago(citation)

        self.assertIn("Smith, J.", formatted)

    def test_ieee_style(self):
        """Test IEEE citation style."""
        citation = self.pipeline.get_citation(self.citation_id)
        formatted = self.pipeline._format_ieee(citation)

        self.assertIn("Smith, J.", formatted)


class TestIntegrationScenarios(unittest.TestCase):
    """Test end-to-end SVG/citation scenarios."""

    def setUp(self):
        self.pipeline = SVGCitationPipeline()

    def test_complete_diagram_with_citations(self):
        """Test complete diagram with citations workflow."""
        # Create diagram
        elements = [
            {"type": "rect", "x": 10, "y": 10, "width": 200, "height": 100},
            {"type": "text", "x": 50, "y": 60, "text": "Water Purification", "size": 16}
        ]
        diagram_id = self.pipeline.generate_svg("workflow1", elements, 800, 600)

        # Add citations
        cite1 = self.pipeline.add_citation(
            "c1",
            "Smith, J.",
            "2024",
            "Water Treatment Methods",
            source="Water Journal"
        )

        cite2 = self.pipeline.add_citation(
            "c2",
            "Jones, A.",
            "2023",
            "Purification Techniques"
        )

        # Link citations to diagram
        self.pipeline.link_diagram_to_citation(diagram_id, cite1)
        self.pipeline.link_diagram_to_citation(diagram_id, cite2)

        # Generate bibliography
        bib = self.pipeline.format_bibliography([cite1, cite2], CitationStyle.APA)

        # Optimize diagram
        opt_result = self.pipeline.optimize_svg(diagram_id)

        # Export
        export = self.pipeline.export_diagram(diagram_id, ExportFormat.SVG)

        # Verify complete workflow
        self.assertEqual(len(self.pipeline.get_diagram_citations(diagram_id)), 2)
        self.assertEqual(bib["count"], 2)
        self.assertGreater(opt_result["savings"], 0)
        self.assertIn("<svg", export["content"])

    def test_citation_extraction_and_management(self):
        """Test citation extraction and management."""
        # Extract from text
        text = "Research shows [Smith, 2024] and [Jones, 2023] that this works."
        extracted = self.pipeline.extract_citations(text)

        # Add to library
        for i, cite_data in enumerate(extracted):
            self.pipeline.add_citation(
                f"auto{i}",
                cite_data["author"],
                cite_data["year"],
                f"Auto-extracted {i}"
            )

        # Search
        results = self.pipeline.search_citations("Smith")

        # Generate bibliography
        bib = self.pipeline.format_bibliography(
            list(self.pipeline.citations.keys()),
            CitationStyle.MLA
        )

        self.assertEqual(len(extracted), 2)
        self.assertGreater(len(results), 0)
        self.assertGreater(bib["count"], 0)

    def test_multi_version_diagram_workflow(self):
        """Test multi-version diagram workflow."""
        # Initial diagram
        diagram_id = self.pipeline.generate_svg(
            "versions",
            [{"type": "circle", "cx": 50, "cy": 50, "r": 25}]
        )

        # Update multiple times
        self.pipeline.update_diagram(
            diagram_id,
            elements=[{"type": "rect", "x": 0, "y": 0, "width": 100, "height": 100}]
        )

        self.pipeline.update_diagram(diagram_id, width=1000, height=800)

        # Get history
        history = self.pipeline.get_diagram_version_history(diagram_id)

        # Get stats
        stats = self.pipeline.get_pipeline_stats()

        # Verify workflow (initial version 1 + 2 updates = 3 history entries)
        self.assertEqual(len(history), 3)
        diagram = self.pipeline.get_diagram(diagram_id)
        self.assertEqual(diagram["version"], 3)
        self.assertEqual(stats["total_diagrams"], 1)


if __name__ == "__main__":
    unittest.main()
