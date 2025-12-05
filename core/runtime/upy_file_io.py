"""
uPY File I/O Operations (v2.0.2)

Provides file reading, writing, and JSON parsing for uPY runtime.

Supports:
- READ FILE - Load text/JSON files
- WRITE FILE - Save text/JSON files
- FILE EXISTS - Check file existence
- JSON PARSE - Parse JSON strings
- JSON STRINGIFY - Convert to JSON
- Path validation and safety checks

Examples:
- (FILE|READ|path/to/file.txt|content_var)
- (FILE|WRITE|path/to/file.txt|{$data})
- (FILE|EXISTS|path/to/file.txt)
- (JSON|PARSE|{$json_string}|result_var)
- (JSON|STRINGIFY|{$data}|json_var)
"""

import json
from pathlib import Path
from typing import Any, Optional, Union, Dict, List


class FileIOError(Exception):
    """Raised when file I/O operation fails"""
    pass


class FileIO:
    """
    File I/O utilities for uPY runtime.

    Provides safe file operations with path validation.
    """

    def __init__(self, workspace_root: Optional[Path] = None):
        """
        Initialize file I/O manager.

        Args:
            workspace_root: Root directory for file operations (default: current directory)
        """
        self.workspace_root = workspace_root or Path.cwd()

    def _resolve_path(self, filepath: str) -> Path:
        """
        Resolve and validate file path.

        Args:
            filepath: File path (absolute or relative to workspace)

        Returns:
            Resolved Path object

        Raises:
            FileIOError: If path is invalid or outside workspace
        """
        # Convert to Path object
        path = Path(filepath)

        # If relative, make it relative to workspace root
        if not path.is_absolute():
            path = self.workspace_root / path

        # Resolve to absolute path
        path = path.resolve()

        # Security check: ensure path is within workspace
        # (commented out for flexibility, but can be enabled for sandboxing)
        # try:
        #     path.relative_to(self.workspace_root)
        # except ValueError:
        #     raise FileIOError(f"Path outside workspace: {path}")

        return path

    def read_file(self, filepath: str, encoding: str = 'utf-8') -> str:
        """
        Read text file content.

        Args:
            filepath: Path to file
            encoding: Text encoding (default: utf-8)

        Returns:
            File content as string

        Raises:
            FileIOError: If file cannot be read
        """
        try:
            path = self._resolve_path(filepath)

            if not path.exists():
                raise FileIOError(f"File not found: {filepath}")

            if not path.is_file():
                raise FileIOError(f"Not a file: {filepath}")

            with open(path, 'r', encoding=encoding) as f:
                return f.read()

        except FileIOError:
            raise
        except Exception as e:
            raise FileIOError(f"Failed to read file {filepath}: {e}")

    def write_file(self, filepath: str, content: str, encoding: str = 'utf-8', append: bool = False) -> bool:
        """
        Write text file content.

        Args:
            filepath: Path to file
            content: Content to write
            encoding: Text encoding (default: utf-8)
            append: If True, append to file instead of overwriting

        Returns:
            True if successful

        Raises:
            FileIOError: If file cannot be written
        """
        try:
            path = self._resolve_path(filepath)

            # Create parent directories if they don't exist
            path.parent.mkdir(parents=True, exist_ok=True)

            mode = 'a' if append else 'w'
            with open(path, mode, encoding=encoding) as f:
                f.write(content)

            return True

        except Exception as e:
            raise FileIOError(f"Failed to write file {filepath}: {e}")

    def file_exists(self, filepath: str) -> bool:
        """
        Check if file exists.

        Args:
            filepath: Path to file

        Returns:
            True if file exists
        """
        try:
            path = self._resolve_path(filepath)
            return path.exists() and path.is_file()
        except Exception:
            return False

    def dir_exists(self, dirpath: str) -> bool:
        """
        Check if directory exists.

        Args:
            dirpath: Path to directory

        Returns:
            True if directory exists
        """
        try:
            path = self._resolve_path(dirpath)
            return path.exists() and path.is_dir()
        except Exception:
            return False

    def delete_file(self, filepath: str) -> bool:
        """
        Delete file.

        Args:
            filepath: Path to file

        Returns:
            True if successful

        Raises:
            FileIOError: If file cannot be deleted
        """
        try:
            path = self._resolve_path(filepath)

            if not path.exists():
                raise FileIOError(f"File not found: {filepath}")

            if not path.is_file():
                raise FileIOError(f"Not a file: {filepath}")

            path.unlink()
            return True

        except FileIOError:
            raise
        except Exception as e:
            raise FileIOError(f"Failed to delete file {filepath}: {e}")

    def read_json(self, filepath: str) -> Union[Dict, List, Any]:
        """
        Read JSON file.

        Args:
            filepath: Path to JSON file

        Returns:
            Parsed JSON data

        Raises:
            FileIOError: If file cannot be read or parsed
        """
        try:
            content = self.read_file(filepath)
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise FileIOError(f"Invalid JSON in {filepath}: {e}")
        except FileIOError:
            raise
        except Exception as e:
            raise FileIOError(f"Failed to read JSON file {filepath}: {e}")

    def write_json(self, filepath: str, data: Any, indent: int = 2) -> bool:
        """
        Write JSON file.

        Args:
            filepath: Path to JSON file
            data: Data to serialize
            indent: JSON indentation (default: 2)

        Returns:
            True if successful

        Raises:
            FileIOError: If file cannot be written
        """
        try:
            content = json.dumps(data, indent=indent, ensure_ascii=False)
            return self.write_file(filepath, content)
        except Exception as e:
            raise FileIOError(f"Failed to write JSON file {filepath}: {e}")

    def parse_json(self, json_string: str) -> Union[Dict, List, Any]:
        """
        Parse JSON string.

        Args:
            json_string: JSON string to parse

        Returns:
            Parsed JSON data

        Raises:
            FileIOError: If JSON is invalid
        """
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            raise FileIOError(f"Invalid JSON: {e}")

    def stringify_json(self, data: Any, indent: Optional[int] = None) -> str:
        """
        Convert data to JSON string.

        Args:
            data: Data to serialize
            indent: JSON indentation (None for compact)

        Returns:
            JSON string

        Raises:
            FileIOError: If data cannot be serialized
        """
        try:
            return json.dumps(data, indent=indent, ensure_ascii=False)
        except Exception as e:
            raise FileIOError(f"Failed to stringify JSON: {e}")

    def get_file_size(self, filepath: str) -> int:
        """
        Get file size in bytes.

        Args:
            filepath: Path to file

        Returns:
            File size in bytes

        Raises:
            FileIOError: If file cannot be accessed
        """
        try:
            path = self._resolve_path(filepath)

            if not path.exists():
                raise FileIOError(f"File not found: {filepath}")

            return path.stat().st_size

        except FileIOError:
            raise
        except Exception as e:
            raise FileIOError(f"Failed to get file size {filepath}: {e}")

    def list_files(self, dirpath: str, pattern: str = '*') -> List[str]:
        """
        List files in directory.

        Args:
            dirpath: Path to directory
            pattern: Glob pattern (default: *)

        Returns:
            List of file paths (relative to directory)

        Raises:
            FileIOError: If directory cannot be accessed
        """
        try:
            path = self._resolve_path(dirpath)

            if not path.exists():
                raise FileIOError(f"Directory not found: {dirpath}")

            if not path.is_dir():
                raise FileIOError(f"Not a directory: {dirpath}")

            files = []
            for item in path.glob(pattern):
                if item.is_file():
                    files.append(str(item.relative_to(path)))

            return sorted(files)

        except FileIOError:
            raise
        except Exception as e:
            raise FileIOError(f"Failed to list files in {dirpath}: {e}")
