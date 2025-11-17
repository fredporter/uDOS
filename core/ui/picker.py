"""
Universal Picker Component - v1.0.23
Reusable interactive picker for all multi-option scenarios

Variants:
- SingleSelect: Choose one from list
- MultiSelect: Choose multiple with checkboxes
- SearchPicker: Type-to-filter with results
- RecentPicker: Recent items with quick access

Author: uDOS Development Team
Version: 1.0.23
"""

from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum


class PickerType(Enum):
    """Picker variant types"""
    SINGLE = "single"
    MULTI = "multi"
    SEARCH = "search"
    RECENT = "recent"


@dataclass
class PickerItem:
    """Item in picker list"""
    id: str
    label: str
    description: Optional[str] = None
    icon: Optional[str] = None
    metadata: Optional[Dict] = None
    selected: bool = False


@dataclass
class PickerConfig:
    """Configuration for picker"""
    title: str
    picker_type: PickerType = PickerType.SINGLE
    max_items_display: int = 9  # Max items to show (1-9 for keyboard)
    show_icons: bool = True
    show_descriptions: bool = True
    show_stats: bool = False
    allow_cancel: bool = True
    allow_search: bool = True
    compact_mode: bool = False  # For small viewports


class UniversalPicker:
    """Universal picker component"""

    def __init__(self, config: PickerConfig, viewport=None):
        """Initialize picker"""
        self.config = config
        self.viewport = viewport
        self.items: List[PickerItem] = []
        self.filtered_items: List[PickerItem] = []
        self.search_query: str = ""

    def set_items(self, items: List[PickerItem]):
        """Set picker items"""
        self.items = items
        self.filtered_items = items.copy()

    def add_item(self, item: PickerItem):
        """Add single item"""
        self.items.append(item)
        self.filtered_items.append(item)

    def filter_items(self, query: str):
        """Filter items by query"""
        self.search_query = query
        query_lower = query.lower()

        self.filtered_items = [
            item for item in self.items
            if query_lower in item.label.lower() or
               (item.description and query_lower in item.description.lower())
        ]

    def render(self) -> str:
        """Render picker UI"""
        if self.config.compact_mode:
            return self._render_compact()
        else:
            return self._render_full()

    def _render_full(self) -> str:
        """Render full picker UI"""
        output = [
            "┌─────────────────────────────────────────────────────────────────┐",
            f"│  {self.config.title:<61} │",
            "├─────────────────────────────────────────────────────────────────┤"
        ]

        # Show search query if active
        if self.search_query:
            count = len(self.filtered_items)
            output.append(f"│  Filter: '{self.search_query}' ({count} matches)  │")
            output.append("│                                                                 │")

        # Show items
        items_to_show = self.filtered_items[:self.config.max_items_display]

        if not items_to_show:
            output.append("│  ❌ No items to display                                        │")
        else:
            for i, item in enumerate(items_to_show, 1):
                line = self._format_item_line(i, item)
                output.append(f"│  {line:<61} │")

        # Show "more" indicator
        if len(self.filtered_items) > self.config.max_items_display:
            remaining = len(self.filtered_items) - self.config.max_items_display
            output.append(f"│  ... and {remaining} more items   │")

        output.append("│                                                                 │")

        # Show actions based on picker type
        output.extend(self._render_actions())

        output.extend([
            "├─────────────────────────────────────────────────────────────────┤",
            "│  Type to filter | ESC to cancel                                │",
            "└─────────────────────────────────────────────────────────────────┘",
            "",
            "Enter choice: "
        ])

        return "\n".join(output)

    def _render_compact(self) -> str:
        """Render compact picker for small viewports"""
        output = [
            f"╔═ {self.config.title} ═╗",
            ""
        ]

        items_to_show = self.filtered_items[:self.config.max_items_display]

        for i, item in enumerate(items_to_show, 1):
            icon = item.icon if self.config.show_icons and item.icon else ""

            if self.config.picker_type == PickerType.MULTI:
                checkbox = "[✓]" if item.selected else "[ ]"
                output.append(f"{i}. {checkbox} {icon} {item.label}")
            else:
                output.append(f"{i}. {icon} {item.label}")

        if len(self.filtered_items) > self.config.max_items_display:
            output.append(f"... +{len(self.filtered_items) - self.config.max_items_display}")

        output.append("")
        output.append("[1-9] Select | [ESC] Cancel")
        output.append("")
        output.append("Choice: ")

        return "\n".join(output)

    def _format_item_line(self, number: int, item: PickerItem) -> str:
        """Format single item line"""
        parts = []

        # Number
        parts.append(f"{number}.")

        # Checkbox for multi-select
        if self.config.picker_type == PickerType.MULTI:
            checkbox = "[✓]" if item.selected else "[ ]"
            parts.append(checkbox)

        # Icon
        if self.config.show_icons and item.icon:
            parts.append(item.icon)

        # Label
        parts.append(item.label[:30])  # Truncate long labels

        # Description
        if self.config.show_descriptions and item.description:
            desc = item.description[:20]  # Truncate
            parts.append(f"- {desc}")

        # Stats from metadata
        if self.config.show_stats and item.metadata:
            stats = self._format_stats(item.metadata)
            if stats:
                parts.append(f"({stats})")

        return " ".join(parts)

    def _format_stats(self, metadata: Dict) -> str:
        """Format metadata as stats"""
        stats = []

        if 'count' in metadata:
            stats.append(f"{metadata['count']} items")

        if 'size' in metadata:
            stats.append(f"{metadata['size']}")

        if 'date' in metadata:
            stats.append(f"{metadata['date']}")

        return ", ".join(stats)

    def _render_actions(self) -> List[str]:
        """Render action bar based on picker type"""
        actions = []

        if self.config.picker_type == PickerType.SINGLE:
            actions.append("│  [1-9] Select item                                             │")

        elif self.config.picker_type == PickerType.MULTI:
            actions.extend([
                "│  [1-9] Toggle item    [A] Select all    [N] Select none      │",
                "│  [ENTER] Confirm      [C] Cancel                              │"
            ])

        elif self.config.picker_type == PickerType.SEARCH:
            actions.extend([
                "│  [1-9] Select result  [R] Refine search                      │",
                "│  [A] Show all         [C] Clear filter                       │"
            ])

        elif self.config.picker_type == PickerType.RECENT:
            actions.extend([
                "│  [1-9] Select recent  [A] Show all                           │",
                "│  [C] Clear recent     [S] Search                             │"
            ])

        return actions

    def get_selected_items(self) -> List[PickerItem]:
        """Get selected items (for multi-select)"""
        return [item for item in self.items if item.selected]

    def toggle_item(self, item_id: str):
        """Toggle item selection (for multi-select)"""
        for item in self.items:
            if item.id == item_id:
                item.selected = not item.selected
                break

    def select_all(self):
        """Select all items"""
        for item in self.filtered_items:
            item.selected = True

    def deselect_all(self):
        """Deselect all items"""
        for item in self.items:
            item.selected = False

    def get_item_by_number(self, number: int) -> Optional[PickerItem]:
        """Get item by display number (1-9)"""
        if 1 <= number <= len(self.filtered_items):
            return self.filtered_items[number - 1]
        return None


class PickerBuilder:
    """Builder for creating pickers easily"""

    @staticmethod
    def single_select(title: str, items: List[Dict],
                     icon_key: str = 'icon',
                     label_key: str = 'label',
                     desc_key: str = 'description') -> UniversalPicker:
        """Create single-select picker"""
        config = PickerConfig(title=title, picker_type=PickerType.SINGLE)
        picker = UniversalPicker(config)

        for i, item_data in enumerate(items):
            item = PickerItem(
                id=str(i),
                label=item_data.get(label_key, ''),
                description=item_data.get(desc_key),
                icon=item_data.get(icon_key),
                metadata=item_data
            )
            picker.add_item(item)

        return picker

    @staticmethod
    def multi_select(title: str, items: List[Dict],
                    icon_key: str = 'icon',
                    label_key: str = 'label',
                    desc_key: str = 'description') -> UniversalPicker:
        """Create multi-select picker"""
        config = PickerConfig(title=title, picker_type=PickerType.MULTI)
        picker = UniversalPicker(config)

        for i, item_data in enumerate(items):
            item = PickerItem(
                id=str(i),
                label=item_data.get(label_key, ''),
                description=item_data.get(desc_key),
                icon=item_data.get(icon_key),
                metadata=item_data
            )
            picker.add_item(item)

        return picker

    @staticmethod
    def search_picker(title: str, search_function: Callable[[str], List[Dict]]) -> UniversalPicker:
        """Create search picker with dynamic results"""
        config = PickerConfig(title=title, picker_type=PickerType.SEARCH)
        picker = UniversalPicker(config)
        picker._search_function = search_function  # Store for dynamic updates
        return picker

    @staticmethod
    def recent_picker(title: str, recent_items: List[Dict],
                     max_recent: int = 9) -> UniversalPicker:
        """Create recent items picker"""
        config = PickerConfig(
            title=title,
            picker_type=PickerType.RECENT,
            max_items_display=max_recent
        )
        picker = UniversalPicker(config)

        for i, item_data in enumerate(recent_items[:max_recent]):
            item = PickerItem(
                id=str(i),
                label=item_data.get('label', ''),
                description=item_data.get('description'),
                icon=item_data.get('icon', '📄'),
                metadata=item_data
            )
            picker.add_item(item)

        return picker


class PickerExamples:
    """Example pickers for common use cases"""

    @staticmethod
    def theme_picker(themes: List[Dict]) -> str:
        """Example: Theme selection picker"""
        picker = PickerBuilder.single_select(
            title="SELECT THEME",
            items=themes
        )
        return picker.render()

    @staticmethod
    def file_type_picker(file_types: List[Dict]) -> str:
        """Example: File type filter picker"""
        picker = PickerBuilder.multi_select(
            title="SELECT FILE TYPES TO SHOW",
            items=file_types
        )
        return picker.render()

    @staticmethod
    def tier_picker() -> str:
        """Example: Memory tier picker"""
        tiers = [
            {'icon': '🔒', 'label': 'PRIVATE', 'description': 'Encrypted, you only'},
            {'icon': '🔐', 'label': 'SHARED', 'description': 'Team members'},
            {'icon': '👥', 'label': 'COMMUNITY', 'description': 'Group access'},
            {'icon': '🌍', 'label': 'PUBLIC', 'description': 'Everyone'},
        ]

        picker = PickerBuilder.single_select(
            title="MEMORY - Select tier",
            items=tiers
        )
        return picker.render()

    @staticmethod
    def extension_picker(extensions: List[Dict]) -> str:
        """Example: Extension selection picker"""
        picker = PickerBuilder.multi_select(
            title="SELECT EXTENSIONS TO ENABLE",
            items=extensions
        )
        picker.config.show_stats = True
        return picker.render()


# Convenience functions
def create_single_picker(title: str, items: List[Dict]) -> UniversalPicker:
    """Quick single-select picker"""
    return PickerBuilder.single_select(title, items)


def create_multi_picker(title: str, items: List[Dict]) -> UniversalPicker:
    """Quick multi-select picker"""
    return PickerBuilder.multi_select(title, items)


def create_compact_picker(title: str, items: List[Dict]) -> UniversalPicker:
    """Quick compact picker for small screens"""
    config = PickerConfig(title=title, compact_mode=True)
    picker = UniversalPicker(config)

    for i, item_data in enumerate(items):
        item = PickerItem(
            id=str(i),
            label=item_data.get('label', ''),
            icon=item_data.get('icon'),
            metadata=item_data
        )
        picker.add_item(item)

    return picker
