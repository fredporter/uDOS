"""
Citation Manager Service - v1.6.0
Tracks sources, embeds citations, validates attribution compliance

Features:
- Source tracking (<cite>, <web>, <meta> tags)
- Citation coverage calculation (≥95% target)
- Bibliography generation
- Validation and compliance checking

Author: uDOS Development Team
Version: 1.6.0
"""

from pathlib import Path
from typing import List, Dict, Tuple, Optional
import re
import json
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Source:
    """Citation source metadata"""
    id: int
    type: str  # 'document', 'web', 'metadata'
    title: str
    author: Optional[str] = None
    url: Optional[str] = None
    date: Optional[str] = None
    page: Optional[int] = None

    def to_bibliography_entry(self) -> str:
        """Format as bibliography entry"""
        parts = [f"{self.id}."]

        if self.title:
            parts.append(f'"{self.title}"')
        if self.author:
            parts.append(f"by {self.author}")
        if self.url:
            parts.append(f"<{self.url}>")
        if self.date:
            parts.append(f"({self.date})")
        if self.page:
            parts.append(f"p. {self.page}")

        return " ".join(parts)


class CitationManager:
    """Manages citation tracking and validation"""

    def __init__(self):
        """Initialize Citation Manager"""
        self.sources: Dict[int, Source] = {}
        self.next_cite_id = 1
        self.next_web_id = 1
        self.next_meta_id = 1

    def add_source(self, source_type: str, title: str, **kwargs) -> int:
        """
        Add a citation source.

        Args:
            source_type: 'document', 'web', or 'metadata'
            title: Source title or description
            **kwargs: Additional metadata (author, url, date, page)

        Returns:
            Citation ID
        """
        if source_type == 'document':
            source_id = self.next_cite_id
            self.next_cite_id += 1
        elif source_type == 'web':
            source_id = self.next_web_id
            self.next_web_id += 1
        elif source_type == 'metadata':
            source_id = self.next_meta_id
            self.next_meta_id += 1
        else:
            raise ValueError(f"Invalid source type: {source_type}")

        source = Source(
            id=source_id,
            type=source_type,
            title=title,
            **kwargs
        )

        self.sources[source_id] = source
        return source_id

    def embed_citation(self, text: str, source_id: int, source_type: str) -> str:
        """
        Embed citation tag in text.

        Args:
            text: Text to cite
            source_id: Citation ID
            source_type: 'document', 'web', or 'metadata'

        Returns:
            Text with embedded citation tag
        """
        # Determine tag type
        if source_type == 'document':
            tag = f"<cite>{source_id}</cite>"
        elif source_type == 'web':
            tag = f"<web>{source_id}</web>"
        elif source_type == 'metadata':
            tag = f"<meta>{source_id}</meta>"
        else:
            raise ValueError(f"Invalid source type: {source_type}")

        # Add tag at end of sentence (before period if present)
        if text.rstrip().endswith('.'):
            text = text.rstrip()[:-1] + tag + '.'
        else:
            text = text.rstrip() + tag

        return text

    def extract_citations(self, content: str) -> Dict[str, List[int]]:
        """
        Extract all citation tags from content.

        Args:
            content: Markdown content with citation tags

        Returns:
            Dict with citation IDs by type: {'cite': [1,2,3], 'web': [1,2], 'meta': [1]}
        """
        citations = {
            'cite': [],
            'web': [],
            'meta': []
        }

        # Find all citation tags
        for tag_type in ['cite', 'web', 'meta']:
            pattern = f'<{tag_type}>(\\d+)</{tag_type}>'
            matches = re.findall(pattern, content)
            citations[tag_type] = [int(m) for m in matches]

        return citations

    def calculate_coverage(self, content: str) -> float:
        """
        Calculate citation coverage percentage.

        Args:
            content: Markdown content

        Returns:
            Coverage score (0.0 - 1.0)
        """
        # Count sentences
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        total_sentences = len(sentences)

        if total_sentences == 0:
            return 0.0

        # Count sentences with citations
        cited_sentences = 0
        for sentence in sentences:
            if re.search(r'<(cite|web|meta)>\d+</(cite|web|meta)>', sentence):
                cited_sentences += 1

        return cited_sentences / total_sentences

    def validate_citations(self, content: str, min_coverage: float = 0.95) -> Tuple[bool, Dict]:
        """
        Validate citation compliance.

        Args:
            content: Markdown content with citations
            min_coverage: Minimum required coverage (default: 0.95)

        Returns:
            (is_valid, report_dict)
        """
        coverage = self.calculate_coverage(content)
        citations = self.extract_citations(content)

        # Count paragraphs and citations
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        total_paragraphs = len(paragraphs)
        cited_paragraphs = sum(1 for p in paragraphs
                              if re.search(r'<(cite|web|meta)>\d+</(cite|web|meta)>', p))

        # Check for uncited paragraphs
        uncited_paragraphs = []
        for i, para in enumerate(paragraphs, 1):
            if not re.search(r'<(cite|web|meta)>\d+</(cite|web|meta)>', para):
                # Skip headers, code blocks, empty lines
                if not para.startswith('#') and not para.startswith('```'):
                    uncited_paragraphs.append(i)

        # Validation report
        report = {
            'valid': coverage >= min_coverage and cited_paragraphs == total_paragraphs,
            'coverage': round(coverage, 3),
            'min_coverage': min_coverage,
            'total_sentences': len(re.split(r'[.!?]+', content)),
            'total_paragraphs': total_paragraphs,
            'cited_paragraphs': cited_paragraphs,
            'uncited_paragraphs': uncited_paragraphs,
            'citations': {
                'document': len(citations['cite']),
                'web': len(citations['web']),
                'metadata': len(citations['meta']),
                'total': sum(len(v) for v in citations.values())
            },
            'issues': []
        }

        # Add issues
        if coverage < min_coverage:
            report['issues'].append(
                f"Coverage {coverage:.1%} below minimum {min_coverage:.1%}"
            )
        if uncited_paragraphs:
            report['issues'].append(
                f"{len(uncited_paragraphs)} paragraphs without citations: {uncited_paragraphs[:5]}"
            )

        return report['valid'], report

    def generate_bibliography(self) -> str:
        """
        Generate bibliography from all sources.

        Returns:
            Formatted bibliography markdown
        """
        if not self.sources:
            return ""

        # Group by type
        doc_sources = [s for s in self.sources.values() if s.type == 'document']
        web_sources = [s for s in self.sources.values() if s.type == 'web']
        meta_sources = [s for s in self.sources.values() if s.type == 'metadata']

        bib = ["## References\n"]

        if doc_sources:
            bib.append("### Source Document\n")
            for source in sorted(doc_sources, key=lambda s: s.id):
                bib.append(source.to_bibliography_entry())
            bib.append("")

        if web_sources:
            bib.append("### Web Sources\n")
            for source in sorted(web_sources, key=lambda s: s.id):
                bib.append(source.to_bibliography_entry())
            bib.append("")

        if meta_sources:
            bib.append("### Document Metadata\n")
            for source in sorted(meta_sources, key=lambda s: s.id):
                bib.append(source.to_bibliography_entry())
            bib.append("")

        return "\n".join(bib)

    def strip_citations(self, content: str) -> str:
        """
        Remove all citation tags from content.

        Args:
            content: Content with citation tags

        Returns:
            Clean content without citation tags
        """
        # Remove all citation tags
        content = re.sub(r'<cite>\d+</cite>', '', content)
        content = re.sub(r'<web>\d+</web>', '', content)
        content = re.sub(r'<meta>\d+</meta>', '', content)

        # Clean up double spaces
        content = re.sub(r'  +', ' ', content)

        return content

    def export_metadata(self, output_path: Path) -> None:
        """
        Export citation metadata to JSON.

        Args:
            output_path: Path to save metadata JSON
        """
        metadata = {
            'generated': datetime.now().isoformat(),
            'sources': {
                str(sid): asdict(source)
                for sid, source in self.sources.items()
            },
            'statistics': {
                'total_sources': len(self.sources),
                'document_sources': len([s for s in self.sources.values() if s.type == 'document']),
                'web_sources': len([s for s in self.sources.values() if s.type == 'web']),
                'metadata_sources': len([s for s in self.sources.values() if s.type == 'metadata'])
            }
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

    def import_metadata(self, metadata_path: Path) -> None:
        """
        Import citation metadata from JSON.

        Args:
            metadata_path: Path to metadata JSON file
        """
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        # Rebuild sources
        self.sources = {}
        for sid_str, source_dict in metadata['sources'].items():
            sid = int(sid_str)
            source = Source(**source_dict)
            self.sources[sid] = source

        # Update ID counters
        doc_ids = [s.id for s in self.sources.values() if s.type == 'document']
        web_ids = [s.id for s in self.sources.values() if s.type == 'web']
        meta_ids = [s.id for s in self.sources.values() if s.type == 'metadata']

        self.next_cite_id = max(doc_ids) + 1 if doc_ids else 1
        self.next_web_id = max(web_ids) + 1 if web_ids else 1
        self.next_meta_id = max(meta_ids) + 1 if meta_ids else 1


# Singleton instance
_citation_manager = None

def get_citation_manager() -> CitationManager:
    """Get global citation manager instance"""
    global _citation_manager
    if _citation_manager is None:
        _citation_manager = CitationManager()
    return _citation_manager


# Example usage
if __name__ == '__main__':
    cm = CitationManager()

    # Add sources
    doc_id = cm.add_source('document', 'Survival Manual 2025', author='Jane Doe', page=42)
    web_id = cm.add_source('web', 'Water Purification Methods',
                          url='https://example.com/water', date='2025-11-26')
    meta_id = cm.add_source('metadata', 'Document author information')

    # Create cited content
    content = cm.embed_citation("Water should be boiled for at least 1 minute", doc_id, 'document')
    content += " " + cm.embed_citation("At higher altitudes, boil for 3 minutes", web_id, 'web')

    print("Content with citations:")
    print(content)
    print()

    # Validate
    valid, report = cm.validate_citations(content)
    print(f"Valid: {valid}")
    print(f"Coverage: {report['coverage']:.1%}")
    print(f"Citations: {report['citations']}")
    print()

    # Generate bibliography
    print(cm.generate_bibliography())
