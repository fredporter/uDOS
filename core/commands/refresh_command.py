"""
REFRESH Command - Content Update and Migration System
v1.4.0 Phase 3.4 - Content Refresh System

Updates existing guides and diagrams to new design standards and quality levels.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import hashlib


class ContentVersion:
    """Track content versions and changes."""

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.metadata_file = filepath.parent / f".{filepath.name}.metadata.json"
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> Dict:
        """Load version metadata from file."""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {
            "version": "1.0.0",
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            "generator": "manual",
            "checksum": self._calculate_checksum(),
            "quality_score": None,
            "history": []
        }

    def _save_metadata(self):
        """Save version metadata to file."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)

    def _calculate_checksum(self) -> str:
        """Calculate SHA256 checksum of file content."""
        if not self.filepath.exists():
            return ""

        sha256 = hashlib.sha256()
        with open(self.filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def bump_version(self, change_type: str = "minor") -> str:
        """
        Increment version number.

        Args:
            change_type: "major" (breaking), "minor" (features), "patch" (fixes)

        Returns:
            New version string
        """
        major, minor, patch = map(int, self.metadata["version"].split("."))

        if change_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif change_type == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1

        new_version = f"{major}.{minor}.{patch}"

        # Record history
        self.metadata["history"].append({
            "version": self.metadata["version"],
            "updated": self.metadata["updated"],
            "checksum": self.metadata["checksum"]
        })

        # Update metadata
        self.metadata["version"] = new_version
        self.metadata["updated"] = datetime.now().isoformat()
        self.metadata["checksum"] = self._calculate_checksum()

        self._save_metadata()
        return new_version

    def set_quality_score(self, score: float):
        """Set quality score (0.0-1.0)."""
        self.metadata["quality_score"] = max(0.0, min(1.0, score))
        self._save_metadata()

    def set_generator(self, generator: str):
        """Set generator type (manual, ok-assist, template, etc.)."""
        self.metadata["generator"] = generator
        self._save_metadata()

    def get_version(self) -> str:
        """Get current version string."""
        return self.metadata["version"]

    def needs_update(self, min_version: str = "1.0.0") -> bool:
        """Check if content needs updating based on version."""
        current = tuple(map(int, self.metadata["version"].split(".")))
        minimum = tuple(map(int, min_version.split(".")))
        return current < minimum


class QualityChecker:
    """Automated quality checks for content."""

    @staticmethod
    def check_guide(filepath: Path) -> Tuple[float, List[str]]:
        """
        Check quality of a guide file.

        Returns:
            (quality_score, issues_list)
        """
        issues = []
        score = 1.0

        if not filepath.exists():
            return 0.0, ["File does not exist"]

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check file size
        size_kb = len(content.encode('utf-8')) / 1024
        if size_kb < 1:
            issues.append(f"File very small ({size_kb:.1f}KB) - may be incomplete")
            score -= 0.2
        elif size_kb > 100:
            issues.append(f"File very large ({size_kb:.1f}KB) - consider splitting")
            score -= 0.1

        # Check structure
        if not content.startswith('#'):
            issues.append("Missing main heading (should start with #)")
            score -= 0.1

        # Check for key sections
        required_sections = ['##', 'Description', 'Steps', 'Safety']
        for section in required_sections:
            if section not in content:
                issues.append(f"Missing recommended section: {section}")
                score -= 0.05

        # Check metadata
        if 'OK Assist Generated:' not in content and 'Author:' not in content:
            issues.append("Missing attribution/author metadata")
            score -= 0.05

        # Check links
        internal_links = content.count('[[')
        external_links = content.count('http')
        if internal_links == 0 and external_links == 0:
            issues.append("No cross-references or external links")
            score -= 0.05

        return max(0.0, score), issues

    @staticmethod
    def check_diagram(filepath: Path) -> Tuple[float, List[str]]:
        """
        Check quality of a diagram file.

        Returns:
            (quality_score, issues_list)
        """
        issues = []
        score = 1.0

        if not filepath.exists():
            return 0.0, ["File does not exist"]

        file_ext = filepath.suffix.lower()
        size_bytes = filepath.stat().st_size
        size_kb = size_bytes / 1024

        # Check file size based on format
        if file_ext == '.txt':  # ASCII
            if size_kb > 25:
                issues.append(f"ASCII diagram too large ({size_kb:.1f}KB, target <10KB)")
                score -= 0.2
        elif file_ext == '.html':  # Teletext
            if size_kb > 40:
                issues.append(f"Teletext diagram too large ({size_kb:.1f}KB, target <30KB)")
                score -= 0.2
        elif file_ext == '.svg':  # SVG
            if size_kb > 75:
                issues.append(f"SVG diagram too large ({size_kb:.1f}KB, target <50KB)")
                score -= 0.2

            # Check SVG structure
            with open(filepath, 'r') as f:
                content = f.read()

            if '<svg' not in content:
                issues.append("Not a valid SVG file")
                score -= 0.5

            # Check for optimization opportunities
            if content.count('<path') > 100:
                issues.append("Many paths - consider optimization")
                score -= 0.05

            if 'viewBox' not in content:
                issues.append("Missing viewBox attribute (not scalable)")
                score -= 0.1

        return max(0.0, score), issues


class RefreshCommand:
    """Main REFRESH command implementation."""

    def __init__(self, workspace_root: Path):
        self.workspace_root = Path(workspace_root)
        self.knowledge_dir = self.workspace_root / "knowledge"
        self.diagrams_dir = self.knowledge_dir / "diagrams"
        self.checker = QualityChecker()

    def refresh_file(self, filepath: Path, force: bool = False,
                    check_only: bool = False) -> Dict:
        """
        Refresh a single file.

        Args:
            filepath: Path to file to refresh
            force: Force refresh even if version is current
            check_only: Only check quality, don't update

        Returns:
            Dictionary with refresh results
        """
        result = {
            "file": str(filepath.relative_to(self.workspace_root)),
            "success": False,
            "action": "none",
            "old_version": None,
            "new_version": None,
            "quality_score": None,
            "issues": [],
            "message": ""
        }

        if not filepath.exists():
            result["message"] = "File does not exist"
            return result

        # Initialize version tracking
        version = ContentVersion(filepath)
        result["old_version"] = version.get_version()

        # Run quality check
        if filepath.suffix in ['.md', '.txt'] and filepath.parent.name != 'diagrams':
            # It's a guide
            quality_score, issues = self.checker.check_guide(filepath)
            content_type = "guide"
        else:
            # It's a diagram
            quality_score, issues = self.checker.check_diagram(filepath)
            content_type = "diagram"

        result["quality_score"] = quality_score
        result["issues"] = issues

        if check_only:
            result["action"] = "check"
            result["message"] = f"Quality check complete: {quality_score:.2f}/1.0"
            result["success"] = True
            return result

        # Determine if refresh needed
        needs_update = force or quality_score < 0.8 or version.needs_update("2.0.0")

        if not needs_update:
            result["action"] = "skip"
            result["message"] = f"File up to date (v{version.get_version()}, quality: {quality_score:.2f})"
            result["success"] = True
            return result

        # Update version and metadata
        if quality_score < 0.6:
            # Major issues - major version bump
            new_version = version.bump_version("major")
            result["action"] = "major_update"
        elif quality_score < 0.8:
            # Minor issues - minor version bump
            new_version = version.bump_version("minor")
            result["action"] = "minor_update"
        else:
            # Forced refresh or standards update - patch bump
            new_version = version.bump_version("patch")
            result["action"] = "refresh"

        version.set_quality_score(quality_score)

        result["new_version"] = new_version
        result["message"] = f"Updated to v{new_version} (quality: {quality_score:.2f})"
        result["success"] = True

        return result

    def refresh_category(self, category: str, force: bool = False,
                        check_only: bool = False) -> List[Dict]:
        """
        Refresh all files in a category.

        Args:
            category: Category name (water, fire, shelter, etc.)
            force: Force refresh all files
            check_only: Only check quality, don't update

        Returns:
            List of refresh results
        """
        category_dir = self.knowledge_dir / category
        if not category_dir.exists():
            return [{
                "success": False,
                "message": f"Category '{category}' not found"
            }]

        results = []

        # Refresh guides
        for guide_file in category_dir.glob("*.md"):
            if guide_file.name != "README.md":
                result = self.refresh_file(guide_file, force, check_only)
                results.append(result)

        # Refresh diagrams
        diagram_category_dir = self.diagrams_dir / category
        if diagram_category_dir.exists():
            for diagram_file in diagram_category_dir.glob("*"):
                if diagram_file.is_file() and not diagram_file.name.startswith('.'):
                    result = self.refresh_file(diagram_file, force, check_only)
                    results.append(result)

        return results

    def refresh_all(self, force: bool = False, check_only: bool = False) -> Dict:
        """
        Refresh all content in knowledge bank.

        Args:
            force: Force refresh all files
            check_only: Only check quality, don't update

        Returns:
            Summary dictionary
        """
        categories = ['water', 'fire', 'shelter', 'food', 'medical',
                     'navigation', 'tools', 'communication']

        all_results = []
        for category in categories:
            results = self.refresh_category(category, force, check_only)
            all_results.extend(results)

        # Generate summary
        summary = {
            "total_files": len(all_results),
            "updated": sum(1 for r in all_results if r.get("action") not in ["none", "skip", "check"]),
            "skipped": sum(1 for r in all_results if r.get("action") == "skip"),
            "failed": sum(1 for r in all_results if not r.get("success")),
            "avg_quality": sum(r.get("quality_score", 0) for r in all_results) / len(all_results) if all_results else 0,
            "results": all_results
        }

        return summary

    def generate_report(self, summary: Dict) -> str:
        """Generate human-readable report."""
        report = ["=" * 80]
        report.append("REFRESH COMMAND REPORT")
        report.append("=" * 80)
        report.append("")
        report.append(f"Total Files Processed: {summary['total_files']}")
        report.append(f"Files Updated: {summary['updated']}")
        report.append(f"Files Skipped: {summary['skipped']}")
        report.append(f"Failed: {summary['failed']}")
        report.append(f"Average Quality Score: {summary['avg_quality']:.2f}/1.0")
        report.append("")

        # Group by action
        by_action = {}
        for result in summary['results']:
            action = result.get('action', 'unknown')
            if action not in by_action:
                by_action[action] = []
            by_action[action].append(result)

        for action, results in sorted(by_action.items()):
            if results:
                report.append(f"{action.upper().replace('_', ' ')}: {len(results)} files")
                for r in results[:5]:  # Show first 5
                    report.append(f"  - {r['file']}: {r.get('message', 'N/A')}")
                if len(results) > 5:
                    report.append(f"  ... and {len(results) - 5} more")
                report.append("")

        report.append("=" * 80)
        return "\n".join(report)


# CLI interface
def main():
    """Command-line interface for REFRESH command."""
    import argparse

    parser = argparse.ArgumentParser(
        description="REFRESH - Update content to new design standards"
    )
    parser.add_argument(
        'target',
        nargs='?',
        help='File, category, or "all" to refresh'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force refresh even if quality is good'
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check quality only, do not update'
    )
    parser.add_argument(
        '--workspace',
        default='.',
        help='Workspace root directory (default: current directory)'
    )

    args = parser.parse_args()

    # Initialize command
    workspace = Path(args.workspace).resolve()
    refresh = RefreshCommand(workspace)

    # Execute refresh
    if args.target == 'all' or args.target is None:
        print("Refreshing all content...")
        summary = refresh.refresh_all(force=args.force, check_only=args.check)
        print(refresh.generate_report(summary))
    elif Path(args.target).exists():
        # Single file
        filepath = Path(args.target).resolve()
        result = refresh.refresh_file(filepath, force=args.force, check_only=args.check)
        print(f"\nFile: {result['file']}")
        print(f"Action: {result['action']}")
        print(f"Quality: {result['quality_score']:.2f}/1.0")
        if result['issues']:
            print("\nIssues:")
            for issue in result['issues']:
                print(f"  - {issue}")
        print(f"\nResult: {result['message']}")
    else:
        # Category
        print(f"Refreshing category: {args.target}...")
        results = refresh.refresh_category(args.target, force=args.force, check_only=args.check)
        summary = {
            "total_files": len(results),
            "updated": sum(1 for r in results if r.get("action") not in ["none", "skip", "check"]),
            "skipped": sum(1 for r in results if r.get("action") == "skip"),
            "failed": sum(1 for r in results if not r.get("success")),
            "avg_quality": sum(r.get("quality_score", 0) for r in results) / len(results) if results else 0,
            "results": results
        }
        print(refresh.generate_report(summary))


if __name__ == "__main__":
    main()
