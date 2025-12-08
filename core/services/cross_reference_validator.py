"""
Cross-Reference Validator
Validates links between knowledge guides and ensures bidirectional references.

Part of v1.2.11 - Knowledge Quality & Automation
"""

import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, asdict
import json


@dataclass
class LinkIssue:
    """Represents a link validation issue."""
    source_file: str
    issue_type: str  # broken, unidirectional, missing_backlink, orphaned
    details: str
    suggested_fix: str
    severity: str  # error, warning, info


class CrossReferenceValidator:
    """Validator for cross-references between knowledge guides."""

    def __init__(self, knowledge_path: str = "knowledge"):
        self.knowledge_path = Path(knowledge_path)
        from core.utils.paths import PATHS
        self.issues_report_path = PATHS.MEMORY_SYSTEM / "xref-validation-report.json"

        # Regex patterns
        self.link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        self.frontmatter_pattern = re.compile(r'^---\n(.*?)\n---', re.DOTALL)

    def validate_all(self) -> List[LinkIssue]:
        """
        Validate all cross-references in knowledge bank.

        Returns:
            List of LinkIssue objects
        """
        print("🔗 Validating cross-references...")

        issues = []

        # Step 1: Build link graph
        link_graph = self._build_link_graph()

        # Step 2: Validate links
        for source, targets in link_graph.items():
            for target, link_text in targets:
                # Check if target exists
                if not self._file_exists(target):
                    issues.append(LinkIssue(
                        source_file=source,
                        issue_type='broken',
                        details=f"Link to '{link_text}' → {target} (file not found)",
                        suggested_fix=f"Remove broken link or create {target}",
                        severity='error'
                    ))
                    continue

                # Check bidirectional reference
                if not self._has_backlink(target, source, link_graph):
                    issues.append(LinkIssue(
                        source_file=source,
                        issue_type='unidirectional',
                        details=f"Link to {target} has no backlink",
                        suggested_fix=f"Add link in {target} back to {source}",
                        severity='warning'
                    ))

        # Step 3: Find orphaned guides (no incoming links)
        all_files = self._get_all_guides()
        referenced_files = set()
        for targets in link_graph.values():
            referenced_files.update(t[0] for t in targets)

        orphaned = all_files - referenced_files - set(link_graph.keys())
        for orphan in orphaned:
            # Skip index/README files
            if orphan.name.lower() in ['readme.md', 'index.md', 'structure.txt']:
                continue

            issues.append(LinkIssue(
                source_file=str(orphan),
                issue_type='orphaned',
                details="Guide has no incoming links (not referenced by any other guide)",
                suggested_fix="Add links to this guide from related guides",
                severity='info'
            ))

        # Save report
        self._save_validation_report(issues)

        return issues

    def _build_link_graph(self) -> Dict[str, List[Tuple[str, str]]]:
        """
        Build graph of all links between guides.

        Returns:
            Dict mapping source file → [(target_path, link_text), ...]
        """
        graph = {}

        for guide_path in self._get_all_guides():
            # Skip non-markdown files
            if guide_path.suffix != '.md':
                continue

            content = guide_path.read_text(encoding='utf-8', errors='ignore')

            # Extract all markdown links
            links = self.link_pattern.findall(content)

            if links:
                # Normalize source path (relative to knowledge/)
                source = str(guide_path.relative_to(self.knowledge_path))
                graph[source] = []

                for link_text, link_path in links:
                    # Only process relative links (skip URLs)
                    if link_path.startswith(('http://', 'https://', '#')):
                        continue

                    # Resolve relative path
                    target = self._resolve_link_path(guide_path, link_path)
                    graph[source].append((target, link_text))

        return graph

    def _resolve_link_path(self, source_file: Path, link_path: str) -> str:
        """Resolve relative link path to absolute path within knowledge/."""
        # Remove anchors
        link_path = link_path.split('#')[0]

        # Resolve relative to source file's directory
        if link_path.startswith('/'):
            # Absolute path from knowledge root
            target = Path('knowledge') / link_path.lstrip('/')
        else:
            # Relative path
            target = (source_file.parent / link_path).resolve()

        # Normalize to relative path from knowledge/
        try:
            return str(target.relative_to(self.knowledge_path))
        except ValueError:
            # Path is outside knowledge/ (e.g., ../other)
            return link_path

    def _file_exists(self, path: str) -> bool:
        """Check if linked file exists."""
        full_path = self.knowledge_path / path
        return full_path.exists()

    def _has_backlink(self, target: str, source: str,
                     link_graph: Dict[str, List[Tuple[str, str]]]) -> bool:
        """Check if target file links back to source."""
        target_links = link_graph.get(target, [])
        return any(link_target == source for link_target, _ in target_links)

    def _get_all_guides(self) -> Set[Path]:
        """Get all guide files in knowledge bank."""
        guides = set()

        for category_path in self.knowledge_path.iterdir():
            if not category_path.is_dir():
                continue

            guides.update(category_path.glob('*.md'))

        return guides

    def _save_validation_report(self, issues: List[LinkIssue]):
        """Save validation report to JSON."""
        self.issues_report_path.parent.mkdir(parents=True, exist_ok=True)

        report = {
            'validation_date': str(Path().cwd().joinpath('.').stat().st_mtime),
            'total_issues': len(issues),
            'by_type': {
                'broken': len([i for i in issues if i.issue_type == 'broken']),
                'unidirectional': len([i for i in issues if i.issue_type == 'unidirectional']),
                'orphaned': len([i for i in issues if i.issue_type == 'orphaned'])
            },
            'by_severity': {
                'error': len([i for i in issues if i.severity == 'error']),
                'warning': len([i for i in issues if i.severity == 'warning']),
                'info': len([i for i in issues if i.severity == 'info'])
            },
            'issues': [asdict(i) for i in issues]
        }

        self.issues_report_path.write_text(json.dumps(report, indent=2))

    def generate_fix_workflow(self, issues: List[LinkIssue]) -> str:
        """Generate .upy workflow to fix validation issues."""
        workflow_path = PATHS.MEMORY_WORKFLOWS / "fix-xref-issues.upy"

        # Only auto-fix broken and unidirectional links (not orphans)
        fixable_issues = [i for i in issues
                         if i.issue_type in ['broken', 'unidirectional']]

        workflow = f"""#!/usr/bin/env udos
# Fix Cross-Reference Issues Workflow
# Auto-generated from validation report
# Total issues: {len(issues)}
# Auto-fixable: {len(fixable_issues)}

MISSION CREATE "Fix Cross-Reference Issues"
SET $objective "Repair broken and unidirectional links"

"""

        # Group by source file for efficiency
        by_file = {}
        for issue in fixable_issues:
            if issue.source_file not in by_file:
                by_file[issue.source_file] = []
            by_file[issue.source_file].append(issue)

        for i, (source_file, file_issues) in enumerate(by_file.items(), 1):
            workflow += f"""
# File {i}/{len(by_file)}: {source_file}
ECHO "[{i}/{len(by_file)}] Checking {source_file}..."

"""
            for j, issue in enumerate(file_issues, 1):
                if issue.issue_type == 'broken':
                    workflow += f"""  ECHO "  ⚠️  Issue {j}: Broken link"
  ECHO "      {issue.details}"
  ECHO "      Fix: {issue.suggested_fix}"
  # Manual review required

"""
                elif issue.issue_type == 'unidirectional':
                    workflow += f"""  ECHO "  🔗 Issue {j}: Missing backlink"
  ECHO "      {issue.details}"
  ECHO "      {issue.suggested_fix}"
  # Manual review required - add backlink to target file

"""

        workflow += """
ECHO ""
ECHO "⚠️  Cross-reference issues require manual review"
ECHO "    Review suggestions above and update guides accordingly"
ECHO ""

MISSION COMPLETE
"""

        workflow_path.write_text(workflow)
        return str(workflow_path)


# CLI interface
if __name__ == "__main__":
    import sys

    validator = CrossReferenceValidator()

    if '--validate' in sys.argv:
        issues = validator.validate_all()

        print(f"\n🔗 Cross-Reference Validation:")
        print(f"   Total issues: {len(issues)}")
        print(f"\n📊 By Type:")
        for issue_type in ['broken', 'unidirectional', 'orphaned']:
            count = len([i for i in issues if i.issue_type == issue_type])
            print(f"   {issue_type.title()}: {count}")

        print(f"\n⚠️  By Severity:")
        for severity in ['error', 'warning', 'info']:
            count = len([i for i in issues if i.severity == severity])
            emoji = {'error': '🔴', 'warning': '🟡', 'info': '⚪'}[severity]
            print(f"   {emoji} {severity.title()}: {count}")

        print(f"\n💾 Validation report saved to: {validator.issues_report_path}")

        if '--generate-workflow' in sys.argv:
            workflow_path = validator.generate_fix_workflow(issues)
            print(f"📝 Fix workflow generated: {workflow_path}")

    else:
        print("Usage: python cross_reference_validator.py --validate [--generate-workflow]")
