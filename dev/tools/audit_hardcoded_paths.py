#!/usr/bin/env python3
"""
Path Audit Tool for uDOS v1.2.15

Scans setup/config files for hardcoded paths and generates a comprehensive audit report.
Credits v1.2.12 path refactoring work and identifies remaining issues.

Target files:
- setup.py
- core/config.py
- extensions/setup/setup_manager.py
- extensions/play/story_manager.py

Usage:
    python dev/tools/audit_hardcoded_paths.py [--verbose] [--output <file>]
"""

import os
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# ANSI color codes
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'


class PathAuditor:
    """Audits Python files for hardcoded paths."""
    
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.issues: Dict[str, List[Tuple[int, str, str]]] = {}
        
        # Patterns to detect hardcoded paths
        self.path_patterns = [
            # Direct string paths
            (r'["\'](?:\.{0,2}/)?(?:core|extensions|knowledge|memory|wiki|data|sandbox)/', 
             'Direct path string'),
            # os.path.join without PATHS
            (r'os\.path\.join\(["\'][^"\']+["\']', 'os.path.join with hardcoded string'),
            # Path() constructor with hardcoded string
            (r'Path\(["\'](?!\/)[^"\']+["\']', 'Path() with hardcoded string'),
            # Relative paths
            (r'["\']\.\.?/[^"\']+["\']', 'Relative path'),
        ]
        
        # Exceptions (allowed patterns)
        self.allowed_patterns = [
            r'PATHS\.',  # Using PATHS constants
            r'get_path\(',  # Using path helper
            r'#.*',  # Comments
            r'""".*"""',  # Docstrings
            r"'''.*'''",
        ]
        
    def scan_file(self, filepath: Path) -> List[Tuple[int, str, str]]:
        """Scan a single file for hardcoded paths.
        
        Returns:
            List of (line_number, line_content, issue_type) tuples
        """
        issues = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"{RED}Error reading {filepath}: {e}{RESET}")
            return issues
        
        for line_num, line in enumerate(lines, 1):
            # Skip comments and docstrings
            if any(re.search(pattern, line) for pattern in self.allowed_patterns):
                continue
            
            # Check for hardcoded path patterns
            for pattern, issue_type in self.path_patterns:
                if re.search(pattern, line):
                    issues.append((line_num, line.strip(), issue_type))
        
        return issues
    
    def audit_files(self, target_files: List[str]) -> Dict[str, List[Tuple[int, str, str]]]:
        """Audit multiple files for hardcoded paths.
        
        Args:
            target_files: List of file paths relative to workspace root
            
        Returns:
            Dictionary mapping filepath to list of issues
        """
        for filepath in target_files:
            full_path = self.workspace_root / filepath
            
            if not full_path.exists():
                print(f"{YELLOW}Warning: {filepath} not found, skipping{RESET}")
                continue
            
            print(f"Scanning {BLUE}{filepath}{RESET}...", end=' ')
            issues = self.scan_file(full_path)
            
            if issues:
                self.issues[filepath] = issues
                print(f"{RED}{len(issues)} issues found{RESET}")
            else:
                print(f"{GREEN}✓ Clean{RESET}")
        
        return self.issues
    
    def generate_report(self, output_file: str = None, verbose: bool = False) -> str:
        """Generate markdown audit report.
        
        Args:
            output_file: Optional file to write report to
            verbose: Include all issue details
            
        Returns:
            Report content as string
        """
        report_lines = [
            "# uDOS v1.2.15 Path Audit Report",
            "",
            f"**Generated:** {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}",
            f"**Workspace:** {self.workspace_root}",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
        ]
        
        total_issues = sum(len(issues) for issues in self.issues.values())
        total_files = len(self.issues)
        
        if total_issues == 0:
            report_lines.extend([
                f"✅ **No hardcoded paths detected** across {len(self.issues)} files scanned.",
                "",
                "All files are using PATHS constants or approved path helpers.",
            ])
        else:
            report_lines.extend([
                f"⚠️  **{total_issues} potential hardcoded paths** found across {total_files} files.",
                "",
                f"- Files with issues: {total_files}",
                f"- Total issues: {total_issues}",
                f"- Average per file: {total_issues / total_files:.1f}",
            ])
        
        # Credit v1.2.12 refactoring
        report_lines.extend([
            "",
            "---",
            "",
            "## Credit: v1.2.12 Path Refactoring",
            "",
            "**Foundation Work (December 2025):**",
            "- Introduced centralized `core/utils/paths.py` PATHS constants",
            "- Migrated scattered path definitions to single source of truth",
            "- Established `PATHS.MEMORY`, `PATHS.KNOWLEDGE`, `PATHS.CORE`, etc.",
            "- Updated .gitignore patterns for v1.2.x structure",
            "- Created TREE and CONFIG commands for structure validation",
            "",
            "**Impact:**",
            "- 95.9% SHAKEDOWN test coverage (142/148 tests passing)",
            "- Standardized memory/ucode/ folder structure",
            "- Clean separation: tracked code vs user workspace",
            "",
            "**v1.2.15 Builds On:**",
            "This audit identifies remaining hardcoded paths in setup/config files that were outside",
            "the scope of v1.2.12's core/commands refactoring. The goal is to achieve 100% PATHS",
            "constant usage across the entire codebase.",
        ])
        
        # Detailed findings
        if total_issues > 0:
            report_lines.extend([
                "",
                "---",
                "",
                "## Detailed Findings",
                "",
            ])
            
            for filepath, issues in sorted(self.issues.items()):
                report_lines.extend([
                    f"### {filepath}",
                    "",
                    f"**Issues Found:** {len(issues)}",
                    "",
                ])
                
                if verbose:
                    # Group by issue type
                    by_type: Dict[str, List[Tuple[int, str]]] = {}
                    for line_num, line_content, issue_type in issues:
                        if issue_type not in by_type:
                            by_type[issue_type] = []
                        by_type[issue_type].append((line_num, line_content))
                    
                    for issue_type, items in sorted(by_type.items()):
                        report_lines.extend([
                            f"**{issue_type}:** {len(items)} occurrences",
                            "",
                        ])
                        for line_num, line_content in items:
                            report_lines.append(f"- Line {line_num}: `{line_content}`")
                        report_lines.append("")
                else:
                    # Summary only
                    issue_types = {}
                    for _, _, issue_type in issues:
                        issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
                    
                    for issue_type, count in sorted(issue_types.items()):
                        report_lines.append(f"- {issue_type}: {count}")
                    report_lines.append("")
        
        # Recommendations
        report_lines.extend([
            "---",
            "",
            "## Recommendations",
            "",
            "### 1. Migrate to PATHS Constants",
            "```python",
            "# ❌ Before:",
            'config_path = "core/data/config.json"',
            "",
            "# ✅ After:",
            "from core.utils.paths import PATHS",
            "config_path = PATHS.CORE_DATA / 'config.json'",
            "```",
            "",
            "### 2. Use Path Helpers",
            "```python",
            "# For dynamic paths:",
            "from core.utils.path_utils import get_memory_path, get_knowledge_path",
            "",
            'user_data = get_memory_path("system/user/config.json")',
            'guide = get_knowledge_path("water/purification.md")',
            "```",
            "",
            "### 3. Update Setup/Config Files",
            "- setup.py: Use PATHS.WORKSPACE_ROOT for all file operations",
            "- config.py: Reference PATHS constants in default config",
            "- setup_manager.py: Migrate hardcoded extension paths",
            "- story_manager.py: Use PATHS.MEMORY for story files",
            "",
            "### 4. Testing",
            "After migration, run:",
            "```bash",
            "./start_udos.sh memory/tests/shakedown.uscript",
            "python memory/ucode/tests/test_path_integrity.py",
            "```",
        ])
        
        # Footer
        report_lines.extend([
            "",
            "---",
            "",
            f"**Audit completed:** {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}",
            "",
            f"**Next Steps:** Migrate identified paths to PATHS constants for v1.2.15 config rebuild.",
        ])
        
        report = '\n'.join(report_lines)
        
        if output_file:
            output_path = self.workspace_root / output_file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\n{GREEN}Report written to: {output_file}{RESET}")
        
        return report


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Audit uDOS files for hardcoded paths')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Include detailed line-by-line findings')
    parser.add_argument('--output', '-o', default='dev/sessions/v1.2.15-path-audit.md',
                       help='Output file for report (default: dev/sessions/v1.2.15-path-audit.md)')
    parser.add_argument('--workspace', '-w', default='.',
                       help='Workspace root directory (default: current directory)')
    
    args = parser.parse_args()
    
    # Target files to audit
    target_files = [
        'setup.py',
        'core/config.py',
        'extensions/setup/setup_manager.py',
        'extensions/play/story_manager.py',
    ]
    
    print(f"{BLUE}uDOS v1.2.15 Path Audit Tool{RESET}")
    print(f"Workspace: {args.workspace}")
    print(f"Scanning {len(target_files)} files...\n")
    
    # Run audit
    auditor = PathAuditor(args.workspace)
    auditor.audit_files(target_files)
    
    # Generate report
    print(f"\n{BLUE}Generating report...{RESET}")
    report = auditor.generate_report(output_file=args.output, verbose=args.verbose)
    
    # Print summary
    total_issues = sum(len(issues) for issues in auditor.issues.values())
    if total_issues == 0:
        print(f"\n{GREEN}✓ All files clean! No hardcoded paths detected.{RESET}")
    else:
        print(f"\n{YELLOW}⚠️  {total_issues} potential issues found{RESET}")
        print(f"See report: {args.output}")
    
    return 0 if total_issues == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
