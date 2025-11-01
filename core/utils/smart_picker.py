"""
uDOS v1.0.2 - Smart File Picker with Fuzzy Search

Enhanced file picker with:
- Fuzzy search and filtering
- Recently used files
- Workspace bookmarks
- File preview
- Batch operations support

Version: 1.0.2
Author: Fred Porter
"""

import os
import json
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from difflib import SequenceMatcher


class SmartFilePicker:
    """
    Advanced file picker with fuzzy search, recent files, and bookmarks.
    """

    ALLOWED_DIRS = ['sandbox', 'memory', 'data']

    # File type icons and colors
    FILE_TYPES = {
        '.py': {'icon': '🐍', 'color': 'yellow', 'desc': 'Python script'},
        '.uscript': {'icon': '📜', 'color': 'blue', 'desc': 'uCODE script'},
        '.usc': {'icon': '📜', 'color': 'blue', 'desc': 'uCODE script'},
        '.md': {'icon': '📝', 'color': 'green', 'desc': 'Markdown'},
        '.txt': {'icon': '📄', 'color': 'white', 'desc': 'Text file'},
        '.json': {'icon': '⚙️', 'color': 'cyan', 'desc': 'JSON config'},
        '.udo': {'icon': '🔧', 'color': 'magenta', 'desc': 'uDOS config'},
        '.log': {'icon': '📋', 'color': 'gray', 'desc': 'Log file'},
        'directory': {'icon': '📁', 'color': 'blue', 'desc': 'Directory'},
        'default': {'icon': '📄', 'color': 'white', 'desc': 'File'}
    }

    def __init__(self, root_dir=None):
        """Initialize smart file picker."""
        self.root = Path(root_dir) if root_dir else Path.cwd()
        self.recent_files_path = self.root / 'memory' / 'config' / 'recent_files.json'
        self.bookmarks_path = self.root / 'memory' / 'config' / 'bookmarks.json'
        self.settings_path = self.root / 'memory' / 'config' / 'picker_settings.json'

        # Initialize config directories
        self._init_config_dirs()

        # Load configuration
        self.recent_files = self._load_recent_files()
        self.bookmarks = self._load_bookmarks()
        self.settings = self._load_settings()

    def _init_config_dirs(self):
        """Create configuration directories if they don't exist."""
        config_dir = self.root / 'memory' / 'config'
        config_dir.mkdir(parents=True, exist_ok=True)

    def _load_recent_files(self) -> List[Dict]:
        """Load recently used files list."""
        if self.recent_files_path.exists():
            try:
                with open(self.recent_files_path, 'r') as f:
                    data = json.load(f)
                    # Sort by last accessed time, newest first
                    return sorted(data, key=lambda x: x['last_accessed'], reverse=True)
            except (json.JSONDecodeError, KeyError):
                pass
        return []

    def _save_recent_files(self):
        """Save recently used files list."""
        try:
            with open(self.recent_files_path, 'w') as f:
                json.dump(self.recent_files, f, indent=2)
        except Exception:
            pass  # Fail silently

    def _load_bookmarks(self) -> Dict[str, str]:
        """Load workspace bookmarks."""
        if self.bookmarks_path.exists():
            try:
                with open(self.bookmarks_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        return {
            'notes': 'memory/notes.md',
            'config': 'data/system/commands.json',
            'readme': 'README.MD'
        }

    def _save_bookmarks(self):
        """Save workspace bookmarks."""
        try:
            with open(self.bookmarks_path, 'w') as f:
                json.dump(self.bookmarks, f, indent=2)
        except Exception:
            pass

    def _load_settings(self) -> Dict:
        """Load picker settings."""
        default_settings = {
            'max_recent_files': 20,
            'show_hidden_files': False,
            'fuzzy_threshold': 0.3,
            'preview_enabled': True,
            'auto_bookmark_frequent': True
        }

        if self.settings_path.exists():
            try:
                with open(self.settings_path, 'r') as f:
                    settings = json.load(f)
                    # Merge with defaults
                    default_settings.update(settings)
            except json.JSONDecodeError:
                pass

        return default_settings

    def _save_settings(self):
        """Save picker settings."""
        try:
            with open(self.settings_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception:
            pass

    def add_to_recent(self, file_path: str, action: str = 'opened'):
        """Add file to recent files list."""
        abs_path = str(Path(file_path).resolve())
        current_time = time.time()

        # Remove existing entry if present
        self.recent_files = [rf for rf in self.recent_files if rf['path'] != abs_path]

        # Add new entry
        self.recent_files.insert(0, {
            'path': abs_path,
            'relative_path': str(Path(file_path)),
            'last_accessed': current_time,
            'action': action,
            'frequency': 1
        })

        # Update frequency for existing files
        for recent_file in self.recent_files[1:]:
            if recent_file['path'] == abs_path:
                recent_file['frequency'] += 1
                break

        # Limit list size
        max_files = self.settings.get('max_recent_files', 20)
        self.recent_files = self.recent_files[:max_files]

        self._save_recent_files()

    def add_bookmark(self, name: str, file_path: str):
        """Add a bookmark."""
        self.bookmarks[name] = str(file_path)
        self._save_bookmarks()

    def remove_bookmark(self, name: str):
        """Remove a bookmark."""
        if name in self.bookmarks:
            del self.bookmarks[name]
            self._save_bookmarks()

    def fuzzy_search(self, query: str, file_list: List[Path]) -> List[Tuple[Path, float]]:
        """
        Perform fuzzy search on file list.

        Returns list of (file_path, score) tuples sorted by relevance.
        """
        if not query.strip():
            return [(f, 1.0) for f in file_list]

        query = query.lower()
        results = []

        for file_path in file_list:
            filename = file_path.name.lower()

            # Calculate multiple scoring methods
            scores = []

            # Exact match bonus
            if query == filename:
                scores.append(1.0)
            elif query in filename:
                # Substring match score based on position and length
                pos = filename.find(query)
                length_ratio = len(query) / len(filename)
                position_score = 1.0 - (pos / len(filename))
                scores.append(0.8 * length_ratio + 0.2 * position_score)

            # Fuzzy string matching
            similarity = SequenceMatcher(None, query, filename).ratio()
            if similarity > self.settings.get('fuzzy_threshold', 0.3):
                scores.append(similarity * 0.6)

            # Word boundary matching
            words = filename.replace('_', ' ').replace('-', ' ').split()
            for word in words:
                if word.startswith(query):
                    scores.append(0.7)
                    break

            # Acronym matching (first letters)
            if len(query) > 1:
                first_letters = ''.join([word[0] for word in words if word])
                if query == first_letters:
                    scores.append(0.8)

            # Use highest score
            if scores:
                max_score = max(scores)
                results.append((file_path, max_score))

        # Sort by score (descending) and then by name
        results.sort(key=lambda x: (-x[1], x[0].name.lower()))

        return results

    def get_files_in_workspace(self, workspace: str, include_dirs: bool = False) -> List[Path]:
        """Get all files in a workspace directory."""
        if workspace not in self.ALLOWED_DIRS:
            return []

        workspace_path = self.root / workspace
        if not workspace_path.exists():
            return []

        files = []

        # Get all files recursively
        for item in workspace_path.rglob('*'):
            # Skip hidden files unless enabled
            if not self.settings.get('show_hidden_files', False) and item.name.startswith('.'):
                continue

            if item.is_file() or (include_dirs and item.is_dir()):
                files.append(item)

        return sorted(files)

    def format_file_info(self, file_path: Path) -> str:
        """Format file information for display."""
        if not file_path.exists():
            return f"❌ {file_path.name} (missing)"

        # Get file type info
        file_type = self.FILE_TYPES.get(file_path.suffix.lower(), self.FILE_TYPES['default'])
        icon = file_type['icon']
        desc = file_type['desc']

        # Get file size
        if file_path.is_file():
            size = file_path.stat().st_size
            if size < 1024:
                size_str = f"{size}B"
            elif size < 1024 * 1024:
                size_str = f"{size//1024}KB"
            else:
                size_str = f"{size//(1024*1024)}MB"
        else:
            size_str = "DIR"

        # Get relative path
        try:
            rel_path = file_path.relative_to(self.root)
        except ValueError:
            rel_path = file_path

        return f"{icon} {rel_path} ({desc}, {size_str})"

    def get_file_preview(self, file_path: Path, max_lines: int = 5) -> str:
        """Get a preview of file contents."""
        if not file_path.exists() or not file_path.is_file():
            return "No preview available"

        try:
            # Limit preview to text files under 1MB
            if file_path.stat().st_size > 1024 * 1024:
                return "File too large for preview"

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= max_lines:
                        lines.append(f"... ({i} more lines)")
                        break
                    lines.append(line.rstrip())

                return '\n'.join(lines) if lines else "Empty file"

        except Exception:
            return "Cannot preview this file type"

    def pick_file_interactive(self, workspace: str = 'sandbox',
                            title: str = 'Select File',
                            file_patterns: Optional[List[str]] = None,
                            show_recent: bool = True,
                            show_bookmarks: bool = True,
                            allow_multiple: bool = False) -> Optional[List[str]]:
        """
        Interactive file picker with fuzzy search.

        Args:
            workspace: Target workspace
            title: Picker title
            file_patterns: File pattern filters
            show_recent: Show recent files section
            show_bookmarks: Show bookmarks section
            allow_multiple: Allow multiple file selection

        Returns:
            List of selected file paths (or None if cancelled)
        """
        print(f"\n📁 {title}")
        print("=" * 60)

        # Get files in workspace
        all_files = self.get_files_in_workspace(workspace)

        # Apply file pattern filters
        if file_patterns:
            filtered_files = []
            for pattern in file_patterns:
                for file_path in all_files:
                    if file_path.match(pattern):
                        filtered_files.append(file_path)
            all_files = filtered_files

        selected_files = []

        while True:
            print(f"\n📂 Workspace: {workspace} ({len(all_files)} files)")

            # Show sections
            options = []

            # Recent files section
            if show_recent and self.recent_files:
                print("\n🕒 Recent Files:")
                for i, recent in enumerate(self.recent_files[:5], 1):
                    rel_path = recent['relative_path']
                    if Path(rel_path).exists():
                        print(f"  {i}. {self.format_file_info(Path(rel_path))}")
                        options.append(('recent', i-1, rel_path))

            # Bookmarks section
            if show_bookmarks and self.bookmarks:
                print("\n🔖 Bookmarks:")
                for i, (name, path) in enumerate(self.bookmarks.items(), 1):
                    if Path(path).exists():
                        print(f"  b{i}. {name} → {path}")
                        options.append(('bookmark', name, path))

            # Search prompt
            print("\n🔍 Search:")
            query = input("  Enter filename or pattern (empty to browse all): ").strip()

            if query:
                # Fuzzy search
                matches = self.fuzzy_search(query, all_files)
                if matches:
                    print(f"\n📋 Search Results ({len(matches)} matches):")
                    for i, (file_path, score) in enumerate(matches[:20], 1):
                        print(f"  {i}. {self.format_file_info(file_path)} (score: {score:.2f})")

                        # Show preview if enabled
                        if self.settings.get('preview_enabled', True) and i <= 3:
                            preview = self.get_file_preview(file_path, 2)
                            if preview and preview != "No preview available":
                                print(f"      Preview: {preview[:100]}...")

                    # Selection prompt
                    try:
                        choice = input("\n  Select file number (or 'q' to quit, 'b' to browse): ").strip()
                        if choice.lower() == 'q':
                            return None
                        elif choice.lower() == 'b':
                            continue
                        elif choice.isdigit():
                            idx = int(choice) - 1
                            if 0 <= idx < len(matches):
                                selected_file = str(matches[idx][0])
                                selected_files.append(selected_file)
                                self.add_to_recent(selected_file, 'selected')

                                if not allow_multiple:
                                    return [selected_file]

                                print(f"✅ Added: {selected_file}")
                                if input("Add another file? (y/N): ").lower() != 'y':
                                    return selected_files
                    except (ValueError, IndexError):
                        print("❌ Invalid selection")
                else:
                    print("  No matches found")
            else:
                # Browse all files
                print(f"\n📋 All Files in {workspace}:")
                for i, file_path in enumerate(all_files[:50], 1):  # Limit display
                    print(f"  {i}. {self.format_file_info(file_path)}")

                if len(all_files) > 50:
                    print(f"  ... and {len(all_files) - 50} more files")

                try:
                    choice = input("\n  Select file number (or 'q' to quit): ").strip()
                    if choice.lower() == 'q':
                        return None
                    elif choice.isdigit():
                        idx = int(choice) - 1
                        if 0 <= idx < min(50, len(all_files)):
                            selected_file = str(all_files[idx])
                            selected_files.append(selected_file)
                            self.add_to_recent(selected_file, 'selected')

                            if not allow_multiple:
                                return [selected_file]

                            print(f"✅ Added: {selected_file}")
                            if input("Add another file? (y/N): ").lower() != 'y':
                                return selected_files
                except (ValueError, IndexError):
                    print("❌ Invalid selection")

    def quick_pick(self, workspace: str = 'sandbox',
                   query: str = '',
                   pattern: str = '*') -> Optional[str]:
        """
        Quick file picker with minimal interaction.

        Args:
            workspace: Target workspace
            query: Search query
            pattern: File pattern

        Returns:
            Selected file path or None
        """
        files = self.get_files_in_workspace(workspace)

        # Apply pattern filter
        if pattern != '*':
            files = [f for f in files if f.match(pattern)]

        if not files:
            return None

        if query:
            matches = self.fuzzy_search(query, files)
            if matches:
                # Return best match
                return str(matches[0][0])

        # Return first file if no query
        return str(files[0])

    def batch_select(self, workspace: str = 'sandbox',
                    pattern: str = '*',
                    interactive: bool = True) -> List[str]:
        """
        Select multiple files for batch operations.

        Args:
            workspace: Target workspace
            pattern: File pattern filter
            interactive: Whether to use interactive selection

        Returns:
            List of selected file paths
        """
        files = self.get_files_in_workspace(workspace)

        # Apply pattern filter
        if pattern != '*':
            files = [f for f in files if f.match(pattern)]

        if not interactive:
            # Return all matching files
            return [str(f) for f in files]

        # Interactive multi-selection
        return self.pick_file_interactive(
            workspace=workspace,
            title=f"Batch Select Files ({pattern})",
            allow_multiple=True
        ) or []


# Example usage and testing
if __name__ == "__main__":
    picker = SmartFilePicker()

    print("🧪 Smart File Picker Test")
    print("=" * 50)

    # Test fuzzy search
    files = picker.get_files_in_workspace('sandbox')
    if files:
        print(f"\nFound {len(files)} files in sandbox")

        # Test search
        results = picker.fuzzy_search('test', files)
        print(f"Fuzzy search for 'test': {len(results)} results")
        for file_path, score in results[:3]:
            print(f"  {file_path.name} (score: {score:.2f})")

    # Test bookmarks
    print(f"\nBookmarks: {list(picker.bookmarks.keys())}")

    # Test recent files
    print(f"Recent files: {len(picker.recent_files)}")

    print("\n✅ Smart File Picker ready for integration")
