"""JSON Viewer/Editor Service

Interactive JSON tree navigation, inline editing with validation, and diff view.
Part of uDOS v1.2.22 self-healing system (Task 7).

Features:
- Tree navigation with expand/collapse
- Inline editing with validation
- Diff view for changes
- Syntax highlighting
- Path tracking (e.g., data.users[0].name)
- Undo/redo support
- Export to file

Privacy: All operations local, no external calls.
"""

import json
import os
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import copy


class JSONNode:
    """Represents a node in the JSON tree."""
    
    def __init__(self, key: str, value: Any, parent: Optional['JSONNode'] = None):
        self.key = key
        self.value = value
        self.parent = parent
        self.expanded = False
        self.children: List['JSONNode'] = []
        
        # Build children for dict/list
        if isinstance(value, dict):
            for k, v in value.items():
                child = JSONNode(k, v, parent=self)
                self.children.append(child)
        elif isinstance(value, list):
            for i, v in enumerate(value):
                child = JSONNode(f"[{i}]", v, parent=self)
                self.children.append(child)
    
    def get_path(self) -> str:
        """Get full path to this node (e.g., 'data.users[0].name')."""
        if self.parent is None:
            return self.key
        
        parent_path = self.parent.get_path()
        if self.key.startswith('['):
            return f"{parent_path}{self.key}"
        else:
            return f"{parent_path}.{self.key}" if parent_path else self.key
    
    def get_type_icon(self) -> str:
        """Get icon representing value type."""
        if isinstance(self.value, dict):
            return "📦" if self.expanded else "📁"
        elif isinstance(self.value, list):
            return "📋" if self.expanded else "📄"
        elif isinstance(self.value, str):
            return "📝"
        elif isinstance(self.value, (int, float)):
            return "🔢"
        elif isinstance(self.value, bool):
            return "✓" if self.value else "✗"
        elif self.value is None:
            return "∅"
        else:
            return "?"
    
    def get_display_value(self) -> str:
        """Get formatted display value."""
        if isinstance(self.value, dict):
            return f"{{ {len(self.value)} keys }}"
        elif isinstance(self.value, list):
            return f"[ {len(self.value)} items ]"
        elif isinstance(self.value, str):
            # Truncate long strings
            if len(self.value) > 50:
                return f'"{self.value[:47]}..."'
            return f'"{self.value}"'
        elif isinstance(self.value, bool):
            return str(self.value).lower()
        elif self.value is None:
            return "null"
        else:
            return str(self.value)
    
    def toggle_expand(self):
        """Toggle expansion state."""
        if isinstance(self.value, (dict, list)):
            self.expanded = not self.expanded


class JSONViewer:
    """Interactive JSON viewer/editor with tree navigation."""
    
    def __init__(self, config=None):
        """Initialize JSON viewer.
        
        Args:
            config: Optional Config instance for project root
        """
        self.config = config
        self.current_file: Optional[str] = None
        self.root: Optional[JSONNode] = None
        self.original_data: Optional[Dict] = None
        self.current_data: Optional[Dict] = None
        self.history: List[Dict] = []  # Undo stack
        self.redo_stack: List[Dict] = []  # Redo stack
        self.cursor: Optional[JSONNode] = None
        self.scroll_offset = 0
    
    def load_file(self, filepath: str) -> Tuple[bool, str]:
        """Load JSON file.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Resolve path
            if self.config:
                project_root = Path(self.config.project_root)
                filepath = project_root / filepath
            
            # Read file
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Store
            self.current_file = str(filepath)
            self.original_data = copy.deepcopy(data)
            self.current_data = data
            
            # Build tree
            filename = Path(filepath).name
            self.root = JSONNode(filename, data)
            self.root.expanded = True
            self.cursor = self.root
            
            # Clear history
            self.history = []
            self.redo_stack = []
            self.scroll_offset = 0
            
            return True, f"✅ Loaded: {filepath}"
            
        except FileNotFoundError:
            return False, f"❌ File not found: {filepath}"
        except json.JSONDecodeError as e:
            return False, f"❌ Invalid JSON: {e}"
        except Exception as e:
            return False, f"❌ Error loading file: {e}"
    
    def load_string(self, json_string: str, name: str = "data") -> Tuple[bool, str]:
        """Load JSON from string.
        
        Args:
            json_string: JSON string
            name: Name for root node
            
        Returns:
            Tuple of (success, message)
        """
        try:
            data = json.loads(json_string)
            
            self.current_file = None
            self.original_data = copy.deepcopy(data)
            self.current_data = data
            
            self.root = JSONNode(name, data)
            self.root.expanded = True
            self.cursor = self.root
            
            self.history = []
            self.redo_stack = []
            self.scroll_offset = 0
            
            return True, "✅ JSON loaded from string"
            
        except json.JSONDecodeError as e:
            return False, f"❌ Invalid JSON: {e}"
        except Exception as e:
            return False, f"❌ Error parsing JSON: {e}"
    
    def get_tree_view(self, max_lines: int = 20) -> List[str]:
        """Get tree view as list of lines.
        
        Args:
            max_lines: Maximum number of lines to display
            
        Returns:
            List of formatted lines
        """
        if not self.root:
            return ["No JSON loaded"]
        
        lines = []
        self._render_node(self.root, lines, depth=0, prefix="")
        
        # Apply scroll offset
        start = self.scroll_offset
        end = start + max_lines
        return lines[start:end]
    
    def _render_node(self, node: JSONNode, lines: List[str], depth: int, prefix: str):
        """Recursively render node and children.
        
        Args:
            node: Node to render
            lines: List to append lines to
            depth: Current depth
            prefix: Prefix for indentation
        """
        # Highlight cursor
        cursor_marker = "▶ " if node == self.cursor else "  "
        
        # Indent
        indent = "  " * depth
        
        # Format line
        icon = node.get_type_icon()
        key_display = node.key
        value_display = node.get_display_value()
        
        line = f"{cursor_marker}{indent}{icon} {key_display}: {value_display}"
        lines.append(line)
        
        # Render children if expanded
        if node.expanded and node.children:
            for child in node.children:
                self._render_node(child, lines, depth + 1, prefix)
    
    def navigate_down(self) -> bool:
        """Move cursor down one node.
        
        Returns:
            True if moved, False if at bottom
        """
        if not self.root:
            return False
        
        # Get all visible nodes
        visible = self._get_visible_nodes()
        
        # Find current position
        try:
            idx = visible.index(self.cursor)
            if idx < len(visible) - 1:
                self.cursor = visible[idx + 1]
                return True
        except ValueError:
            pass
        
        return False
    
    def navigate_up(self) -> bool:
        """Move cursor up one node.
        
        Returns:
            True if moved, False if at top
        """
        if not self.root:
            return False
        
        # Get all visible nodes
        visible = self._get_visible_nodes()
        
        # Find current position
        try:
            idx = visible.index(self.cursor)
            if idx > 0:
                self.cursor = visible[idx - 1]
                return True
        except ValueError:
            pass
        
        return False
    
    def _get_visible_nodes(self) -> List[JSONNode]:
        """Get list of all visible nodes in tree order.
        
        Returns:
            List of visible nodes
        """
        if not self.root:
            return []
        
        visible = []
        self._collect_visible(self.root, visible)
        return visible
    
    def _collect_visible(self, node: JSONNode, visible: List[JSONNode]):
        """Recursively collect visible nodes.
        
        Args:
            node: Current node
            visible: List to append to
        """
        visible.append(node)
        
        if node.expanded and node.children:
            for child in node.children:
                self._collect_visible(child, visible)
    
    def toggle_expand(self) -> bool:
        """Toggle expansion of cursor node.
        
        Returns:
            True if toggled, False if not expandable
        """
        if not self.cursor:
            return False
        
        if isinstance(self.cursor.value, (dict, list)):
            self.cursor.toggle_expand()
            return True
        
        return False
    
    def edit_value(self, new_value_str: str) -> Tuple[bool, str]:
        """Edit value at cursor.
        
        Args:
            new_value_str: New value as string (will be parsed)
            
        Returns:
            Tuple of (success, message)
        """
        if not self.cursor or self.cursor == self.root:
            return False, "❌ Cannot edit root node"
        
        if isinstance(self.cursor.value, (dict, list)):
            return False, "❌ Cannot edit containers (edit children instead)"
        
        try:
            # Save state for undo
            self._save_state()
            
            # Parse new value
            new_value = self._parse_value(new_value_str)
            
            # Update in tree
            old_value = self.cursor.value
            self.cursor.value = new_value
            
            # Update in data structure
            self._update_data_structure()
            
            return True, f"✅ Updated: {old_value} → {new_value}"
            
        except ValueError as e:
            return False, f"❌ Invalid value: {e}"
        except Exception as e:
            return False, f"❌ Error updating: {e}"
    
    def _parse_value(self, value_str: str) -> Any:
        """Parse string value to appropriate type.
        
        Args:
            value_str: String to parse
            
        Returns:
            Parsed value
            
        Raises:
            ValueError: If parsing fails
        """
        value_str = value_str.strip()
        
        # Try JSON parsing first (handles null, true, false, numbers, strings)
        try:
            return json.loads(value_str)
        except json.JSONDecodeError:
            pass
        
        # If quoted, treat as string
        if (value_str.startswith('"') and value_str.endswith('"')) or \
           (value_str.startswith("'") and value_str.endswith("'")):
            return value_str[1:-1]
        
        # Try number
        try:
            if '.' in value_str:
                return float(value_str)
            return int(value_str)
        except ValueError:
            pass
        
        # Boolean
        if value_str.lower() in ('true', 'yes', 'on'):
            return True
        if value_str.lower() in ('false', 'no', 'off'):
            return False
        
        # Null
        if value_str.lower() in ('null', 'none'):
            return None
        
        # Default to string
        return value_str
    
    def _update_data_structure(self):
        """Update current_data from tree."""
        if not self.root:
            return
        
        self.current_data = self._node_to_dict(self.root)
    
    def _node_to_dict(self, node: JSONNode) -> Any:
        """Convert node tree back to dict/list structure.
        
        Args:
            node: Root node
            
        Returns:
            Dict/list structure
        """
        if isinstance(node.value, dict):
            result = {}
            for child in node.children:
                result[child.key] = self._node_to_dict(child)
            return result
        elif isinstance(node.value, list):
            result = []
            for child in node.children:
                result.append(self._node_to_dict(child))
            return result
        else:
            return node.value
    
    def _save_state(self):
        """Save current state to history."""
        if self.current_data:
            self.history.append(copy.deepcopy(self.current_data))
            self.redo_stack.clear()  # Clear redo on new edit
    
    def undo(self) -> Tuple[bool, str]:
        """Undo last change.
        
        Returns:
            Tuple of (success, message)
        """
        if not self.history:
            return False, "❌ Nothing to undo"
        
        # Save current state to redo
        self.redo_stack.append(copy.deepcopy(self.current_data))
        
        # Restore previous state
        self.current_data = self.history.pop()
        
        # Rebuild tree
        if self.root:
            filename = self.root.key
            self.root = JSONNode(filename, self.current_data)
            self.root.expanded = True
            self.cursor = self.root
        
        return True, "✅ Undo successful"
    
    def redo(self) -> Tuple[bool, str]:
        """Redo last undone change.
        
        Returns:
            Tuple of (success, message)
        """
        if not self.redo_stack:
            return False, "❌ Nothing to redo"
        
        # Save current state to history
        self.history.append(copy.deepcopy(self.current_data))
        
        # Restore redo state
        self.current_data = self.redo_stack.pop()
        
        # Rebuild tree
        if self.root:
            filename = self.root.key
            self.root = JSONNode(filename, self.current_data)
            self.root.expanded = True
            self.cursor = self.root
        
        return True, "✅ Redo successful"
    
    def get_diff(self) -> List[str]:
        """Get diff between original and current data.
        
        Returns:
            List of diff lines
        """
        if not self.original_data or not self.current_data:
            return ["No changes"]
        
        if self.original_data == self.current_data:
            return ["No changes"]
        
        diff_lines = ["Changes:"]
        self._compare_dicts(self.original_data, self.current_data, diff_lines, path="")
        
        return diff_lines
    
    def _compare_dicts(self, old: Any, new: Any, lines: List[str], path: str):
        """Recursively compare old and new data.
        
        Args:
            old: Original value
            new: New value
            lines: List to append diff lines to
            path: Current path
        """
        if old == new:
            return
        
        if type(old) != type(new):
            lines.append(f"  {path}: {old} → {new} (type changed)")
            return
        
        if isinstance(old, dict):
            # Check for added/removed keys
            old_keys = set(old.keys())
            new_keys = set(new.keys())
            
            for key in new_keys - old_keys:
                lines.append(f"  {path}.{key}: ADDED = {new[key]}")
            
            for key in old_keys - new_keys:
                lines.append(f"  {path}.{key}: REMOVED")
            
            # Check for changed values
            for key in old_keys & new_keys:
                new_path = f"{path}.{key}" if path else key
                self._compare_dicts(old[key], new[key], lines, new_path)
        
        elif isinstance(old, list):
            for i, (old_val, new_val) in enumerate(zip(old, new)):
                new_path = f"{path}[{i}]"
                self._compare_dicts(old_val, new_val, lines, new_path)
            
            if len(old) != len(new):
                lines.append(f"  {path}: length changed ({len(old)} → {len(new)})")
        
        else:
            lines.append(f"  {path}: {old} → {new}")
    
    def save(self, filepath: Optional[str] = None) -> Tuple[bool, str]:
        """Save JSON to file.
        
        Args:
            filepath: Optional path (uses current_file if None)
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Determine filepath
            save_path = filepath or self.current_file
            
            if not save_path:
                return False, "❌ No file specified"
            
            # Resolve path
            if self.config:
                project_root = Path(self.config.project_root)
                save_path = project_root / save_path
            
            # Create backup
            if os.path.exists(save_path):
                backup_path = f"{save_path}.backup"
                import shutil
                shutil.copy2(save_path, backup_path)
            
            # Write file
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_data, f, indent=2, ensure_ascii=False)
            
            # Update original
            self.original_data = copy.deepcopy(self.current_data)
            self.current_file = str(save_path)
            
            return True, f"✅ Saved: {save_path}"
            
        except Exception as e:
            return False, f"❌ Error saving: {e}"
    
    def get_info(self) -> Dict[str, Any]:
        """Get viewer info.
        
        Returns:
            Dict with info
        """
        return {
            'file': self.current_file or "N/A",
            'has_changes': self.original_data != self.current_data if self.original_data else False,
            'undo_available': len(self.history) > 0,
            'redo_available': len(self.redo_stack) > 0,
            'cursor_path': self.cursor.get_path() if self.cursor else "N/A",
            'total_nodes': len(self._get_visible_nodes()) if self.root else 0
        }


# Singleton instance
_json_viewer_instance = None


def get_json_viewer(config=None):
    """Get or create JSON viewer singleton.
    
    Args:
        config: Optional Config instance
        
    Returns:
        JSONViewer instance
    """
    global _json_viewer_instance
    
    if _json_viewer_instance is None:
        _json_viewer_instance = JSONViewer(config)
    
    return _json_viewer_instance
