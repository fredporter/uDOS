"""
Fuzzy File Matcher - v1.0.23
Intelligent file matching with typo tolerance and relevance ranking

Features:
- Levenshtein distance for typo tolerance
- Partial matching (substrings)
- Recent files prioritization
- Smart abbreviations (readme → README.md)
- Path-aware matching

Author: uDOS Development Team
Version: 1.0.23
"""

from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import os
import json


class FuzzyMatcher:
    """Smart file matching with typo tolerance"""

    def __init__(self, workspace_root: str = "/Users/fredbook/Code/uDOS", logger=None):
        """Initialize fuzzy matcher"""
        self.workspace_root = Path(workspace_root)
        self.logger = logger
        self.recent_files_cache = []
        self.max_recent = 20

        # Common abbreviations
        self.abbreviations = {
            'readme': 'README.md',
            'rm': 'README.md',
            'change': 'CHANGELOG.md',
            'contrib': 'CONTRIBUTING.md',
            'road': 'ROADMAP.MD',
            'license': 'LICENSE.txt',
            'req': 'requirements.txt',
        }

    def find_matches(self, query: str, search_paths: Optional[List[str]] = None,
                     max_results: int = 10) -> List[Dict]:
        """
        Find files matching query with fuzzy logic

        Args:
            query: Search string
            search_paths: Optional list of paths to search (default: workspace root)
            max_results: Maximum number of results

        Returns:
            List of matches with scores and metadata
        """
        if not query:
            return []

        # Check abbreviations first
        if query.lower() in self.abbreviations:
            expanded = self.abbreviations[query.lower()]
            if self._file_exists(expanded):
                return [{
                    'path': expanded,
                    'score': 1000,
                    'reason': 'Abbreviation match',
                    'type': 'exact'
                }]

        # Collect all candidate files
        candidates = self._collect_candidates(search_paths)

        # Score each candidate
        scored = []
        for candidate in candidates:
            score = self._calculate_score(query, candidate)
            if score > 0:
                scored.append({
                    'path': candidate,
                    'score': score,
                    'reason': self._get_match_reason(query, candidate, score),
                    'type': self._get_match_type(score)
                })

        # Sort by score and return top N
        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored[:max_results]

    def find_best_match(self, query: str, search_paths: Optional[List[str]] = None) -> Optional[str]:
        """Find single best match for query"""
        matches = self.find_matches(query, search_paths, max_results=1)
        return matches[0]['path'] if matches else None

    def _collect_candidates(self, search_paths: Optional[List[str]] = None) -> List[str]:
        """Collect all files to search"""
        candidates = []

        if search_paths:
            # Search specific paths
            for path_str in search_paths:
                path = Path(path_str)
                if path.is_file():
                    candidates.append(str(path))
                elif path.is_dir():
                    candidates.extend(self._scan_directory(path))
        else:
            # Search workspace root
            candidates = self._scan_directory(self.workspace_root)

        return candidates

    def _scan_directory(self, directory: Path, max_depth: int = 5) -> List[str]:
        """Recursively scan directory for files"""
        files = []

        try:
            for item in directory.rglob("*"):
                # Skip hidden and cache directories
                if any(part.startswith('.') for part in item.parts):
                    continue
                if '__pycache__' in item.parts:
                    continue
                if 'node_modules' in item.parts:
                    continue

                if item.is_file():
                    # Store relative path
                    rel_path = item.relative_to(self.workspace_root)
                    files.append(str(rel_path))
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Error scanning {directory}: {e}")

        return files

    def _calculate_score(self, query: str, candidate: str) -> int:
        """Calculate match score for candidate"""
        query_lower = query.lower()
        candidate_lower = candidate.lower()
        filename = Path(candidate).name.lower()

        score = 0

        # Exact filename match (highest priority)
        if query_lower == filename:
            score += 1000

        # Exact path match
        elif query_lower == candidate_lower:
            score += 900

        # Filename starts with query
        elif filename.startswith(query_lower):
            score += 800

        # Path starts with query
        elif candidate_lower.startswith(query_lower):
            score += 700

        # Filename contains query
        elif query_lower in filename:
            score += 600

        # Path contains query
        elif query_lower in candidate_lower:
            score += 500

        # Fuzzy match (Levenshtein distance)
        else:
            distance = self._levenshtein_distance(query_lower, filename)
            # Closer match = higher score
            if distance <= 3:  # Allow up to 3 character differences
                score += max(0, 400 - (distance * 100))

        # Bonus for recent files
        if candidate in self.recent_files_cache:
            recent_index = self.recent_files_cache.index(candidate)
            score += max(0, 200 - (recent_index * 10))

        # Bonus for common file types
        if filename.endswith(('.md', '.py', '.txt', '.json')):
            score += 50

        # Bonus for root-level files
        if '/' not in candidate:
            score += 30

        return score

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # Cost of insertions, deletions, or substitutions
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def _get_match_reason(self, query: str, candidate: str, score: int) -> str:
        """Get human-readable reason for match"""
        query_lower = query.lower()
        candidate_lower = candidate.lower()
        filename = Path(candidate).name.lower()

        if score >= 1000:
            return "Exact filename match"
        elif score >= 900:
            return "Exact path match"
        elif score >= 800:
            return "Filename starts with query"
        elif score >= 700:
            return "Path starts with query"
        elif score >= 600:
            return "Filename contains query"
        elif score >= 500:
            return "Path contains query"
        elif score >= 300:
            return "Fuzzy match (typo tolerance)"
        elif score >= 200:
            return "Recent file"
        else:
            return "Weak match"

    def _get_match_type(self, score: int) -> str:
        """Get match type category"""
        if score >= 800:
            return "exact"
        elif score >= 500:
            return "partial"
        elif score >= 300:
            return "fuzzy"
        else:
            return "weak"

    def _file_exists(self, path: str) -> bool:
        """Check if file exists (workspace-relative)"""
        full_path = self.workspace_root / path
        return full_path.exists() and full_path.is_file()

    def add_recent_file(self, file_path: str):
        """Add file to recent cache"""
        # Remove if already exists
        if file_path in self.recent_files_cache:
            self.recent_files_cache.remove(file_path)

        # Add to front
        self.recent_files_cache.insert(0, file_path)

        # Trim to max size
        if len(self.recent_files_cache) > self.max_recent:
            self.recent_files_cache = self.recent_files_cache[:self.max_recent]

    def get_recent_files(self, limit: int = 10) -> List[str]:
        """Get recent files"""
        return self.recent_files_cache[:limit]

    def clear_recent_files(self):
        """Clear recent files cache"""
        self.recent_files_cache = []


class SmartFilePicker:
    """Interactive file picker with fuzzy matching"""

    def __init__(self, fuzzy_matcher: FuzzyMatcher, viewport=None):
        """Initialize picker"""
        self.matcher = fuzzy_matcher
        self.viewport = viewport

    def show_picker(self, query: str = "", search_paths: Optional[List[str]] = None) -> str:
        """Show interactive file picker"""

        if query:
            matches = self.matcher.find_matches(query, search_paths, max_results=20)
        else:
            # Show recent files
            matches = [{'path': path, 'score': 100, 'reason': 'Recent file', 'type': 'recent'}
                      for path in self.matcher.get_recent_files()]

        if not matches:
            return self._show_no_matches(query)

        return self._format_picker(query, matches)

    def _format_picker(self, query: str, matches: List[Dict]) -> str:
        """Format picker UI"""
        output = [
            "┌─────────────────────────────────────────────────────────────────┐",
            "│  FILE PICKER - Select file:                                    │",
            "├─────────────────────────────────────────────────────────────────┤"
        ]

        if query:
            output.append(f"│  Query: '{query}'  ({len(matches)} matches)                    │")
        else:
            output.append(f"│  Recent Files ({len(matches)} items)                           │")

        output.append("│                                                                 │")

        # Show matches (max 9 for number selection)
        for i, match in enumerate(matches[:9], 1):
            icon = self._get_file_icon(match['path'])
            reason = match['reason'][:25]  # Truncate long reasons

            # Format: number, icon, filename, reason
            filename = Path(match['path']).name[:30]
            output.append(f"│  {i}. {icon} {filename:<30} [{reason:<25}] │")

        if len(matches) > 9:
            output.append(f"│     ... and {len(matches) - 9} more matches                    │")

        output.extend([
            "│                                                                 │",
            "│  Actions:                                                       │",
            "│    [1-9] Select file      [R] Refine search                    │",
            "│    [A] Show all matches   [C] Clear recent                     │",
            "│                                                                 │",
            "├─────────────────────────────────────────────────────────────────┤",
            "│  Type to filter | ESC to cancel                                │",
            "└─────────────────────────────────────────────────────────────────┘",
            "",
            "Enter choice: "
        ])

        return "\n".join(output)

    def _show_no_matches(self, query: str) -> str:
        """Show no matches message"""
        return f"""
┌─────────────────────────────────────────────────────────────────┐
│  FILE PICKER - No matches found                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Query: '{query}'                                              │
│                                                                 │
│  ❌ No files match your search                                 │
│                                                                 │
│  Suggestions:                                                   │
│    • Check spelling                                             │
│    • Try shorter query                                          │
│    • Use file extension (.md, .py, .txt)                       │
│    • Try abbreviations (readme, road, change)                  │
│                                                                 │
│  Recent files: {len(self.matcher.get_recent_files())} available │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
"""

    def _get_file_icon(self, path: str) -> str:
        """Get icon for file type"""
        ext = Path(path).suffix.lower()

        icons = {
            '.md': '📝',
            '.py': '🐍',
            '.txt': '📄',
            '.json': '🔧',
            '.upy': '⚙️',
            '.sh': '🔨',
            '.js': '💛',
            '.css': '🎨',
            '.html': '🌐',
        }

        return icons.get(ext, '📄')


# Convenience function
def create_fuzzy_matcher(workspace_root: str = "/Users/fredbook/Code/uDOS", logger=None):
    """Create fuzzy matcher instance"""
    return FuzzyMatcher(workspace_root=workspace_root, logger=logger)
