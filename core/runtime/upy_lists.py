"""
uPY List Operations (v2.0.2)

Provides list manipulation functions for uPY runtime.

Supports:
- List literals: [item1, item2, item3]
- LIST APPEND, REMOVE, INSERT operations
- LIST GET, SET operations
- LIST SIZE, SLICE operations
- List indexing with negative indices

Examples:
- (LIST|CREATE|items|apple|banana|cherry)
- (LIST|APPEND|items|orange)
- (LIST|REMOVE|items|banana)
- (LIST|GET|items|0) → "apple"
- (LIST|SIZE|items) → 3
- (LIST|SLICE|items|0|2) → ["apple", "cherry"]
"""

from typing import Any, List, Optional, Union


class ListOperations:
    """
    List manipulation utilities for uPY runtime.
    """

    @staticmethod
    def parse_list_literal(literal: str) -> List[Any]:
        """
        Parse list literal: [item1, item2, item3]

        Args:
            literal: String representation like "[apple, banana, cherry]"

        Returns:
            List of items
        """
        literal = literal.strip()
        if not literal.startswith('[') or not literal.endswith(']'):
            raise ValueError(f"Invalid list literal: {literal}")

        # Remove brackets
        inner = literal[1:-1].strip()

        if not inner:
            return []

        # Split on comma but respect nested brackets and quotes
        items = []
        current = []
        bracket_depth = 0
        in_quotes = False
        quote_char = None

        for char in inner:
            if char in ('"', "'") and (not in_quotes or char == quote_char):
                in_quotes = not in_quotes
                quote_char = char if in_quotes else None
                current.append(char)
            elif char == '[' and not in_quotes:
                bracket_depth += 1
                current.append(char)
            elif char == ']' and not in_quotes:
                bracket_depth -= 1
                current.append(char)
            elif char == ',' and bracket_depth == 0 and not in_quotes:
                # Split here
                items.append(''.join(current).strip())
                current = []
            else:
                current.append(char)

        # Add last item
        if current:
            items.append(''.join(current).strip())

        # Clean up items (remove quotes if present)
        cleaned = []
        for item in items:
            item = item.strip()
            # Remove surrounding quotes
            if (item.startswith('"') and item.endswith('"')) or \
               (item.startswith("'") and item.endswith("'")):
                item = item[1:-1]
            cleaned.append(item)

        return cleaned

    @staticmethod
    def create_list(items: List[Any] = None) -> List[Any]:
        """
        Create a new list.

        Args:
            items: Initial items (optional)

        Returns:
            New list
        """
        return list(items) if items else []

    @staticmethod
    def append(lst: List[Any], item: Any) -> List[Any]:
        """
        Append item to list.

        Args:
            lst: List to modify
            item: Item to append

        Returns:
            Modified list
        """
        if not isinstance(lst, list):
            raise TypeError(f"Expected list, got {type(lst).__name__}")

        lst.append(item)
        return lst

    @staticmethod
    def remove(lst: List[Any], item: Any) -> List[Any]:
        """
        Remove first occurrence of item from list.

        Args:
            lst: List to modify
            item: Item to remove

        Returns:
            Modified list

        Raises:
            ValueError: If item not in list
        """
        if not isinstance(lst, list):
            raise TypeError(f"Expected list, got {type(lst).__name__}")

        lst.remove(item)
        return lst

    @staticmethod
    def insert(lst: List[Any], index: int, item: Any) -> List[Any]:
        """
        Insert item at index.

        Args:
            lst: List to modify
            index: Position to insert at (supports negative indices)
            item: Item to insert

        Returns:
            Modified list
        """
        if not isinstance(lst, list):
            raise TypeError(f"Expected list, got {type(lst).__name__}")

        lst.insert(index, item)
        return lst

    @staticmethod
    def get(lst: List[Any], index: int) -> Any:
        """
        Get item at index.

        Args:
            lst: List to access
            index: Position to get (supports negative indices)

        Returns:
            Item at index

        Raises:
            IndexError: If index out of range
        """
        if not isinstance(lst, list):
            raise TypeError(f"Expected list, got {type(lst).__name__}")

        return lst[index]

    @staticmethod
    def set(lst: List[Any], index: int, value: Any) -> List[Any]:
        """
        Set item at index.

        Args:
            lst: List to modify
            index: Position to set (supports negative indices)
            value: New value

        Returns:
            Modified list

        Raises:
            IndexError: If index out of range
        """
        if not isinstance(lst, list):
            raise TypeError(f"Expected list, got {type(lst).__name__}")

        lst[index] = value
        return lst

    @staticmethod
    def size(lst: List[Any]) -> int:
        """
        Get list size.

        Args:
            lst: List to measure

        Returns:
            Number of items
        """
        if not isinstance(lst, list):
            raise TypeError(f"Expected list, got {type(lst).__name__}")

        return len(lst)

    @staticmethod
    def slice(lst: List[Any], start: int, end: Optional[int] = None) -> List[Any]:
        """
        Get list slice.

        Args:
            lst: List to slice
            start: Start index (inclusive)
            end: End index (exclusive, optional)

        Returns:
            Sliced list
        """
        if not isinstance(lst, list):
            raise TypeError(f"Expected list, got {type(lst).__name__}")

        if end is None:
            return lst[start:]
        else:
            return lst[start:end]

    @staticmethod
    def contains(lst: List[Any], item: Any) -> bool:
        """
        Check if list contains item.

        Args:
            lst: List to search
            item: Item to find

        Returns:
            True if item in list
        """
        if not isinstance(lst, list):
            raise TypeError(f"Expected list, got {type(lst).__name__}")

        return item in lst

    @staticmethod
    def index_of(lst: List[Any], item: Any) -> int:
        """
        Get index of first occurrence of item.

        Args:
            lst: List to search
            item: Item to find

        Returns:
            Index of item

        Raises:
            ValueError: If item not in list
        """
        if not isinstance(lst, list):
            raise TypeError(f"Expected list, got {type(lst).__name__}")

        return lst.index(item)

    @staticmethod
    def clear(lst: List[Any]) -> List[Any]:
        """
        Clear all items from list.

        Args:
            lst: List to clear

        Returns:
            Empty list (same reference)
        """
        if not isinstance(lst, list):
            raise TypeError(f"Expected list, got {type(lst).__name__}")

        lst.clear()
        return lst

    @staticmethod
    def join(lst: List[Any], separator: str = ',') -> str:
        """
        Join list items into string.

        Args:
            lst: List to join
            separator: String to insert between items

        Returns:
            Joined string
        """
        if not isinstance(lst, list):
            raise TypeError(f"Expected list, got {type(lst).__name__}")

        return separator.join(str(item) for item in lst)

    @staticmethod
    def split(text: str, separator: str = ',') -> List[str]:
        """
        Split string into list.

        Args:
            text: String to split
            separator: Delimiter

        Returns:
            List of strings
        """
        return text.split(separator)
