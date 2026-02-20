"""
Handles reading and writing data for Vibe services to persistent storage.
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from core.services.logging_manager import get_logger

_logger = get_logger(__name__)

_persistence_service_instance = None

class PersistenceService:
    """
    A singleton service for managing persistent data for Vibe services.
    Handles file I/O operations for JSON-based data stores.
    """
    def __init__(self, base_path: str = "memory/vibe"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        _logger.info(f"PersistenceService initialized with base path: {self.base_path.resolve()}")

    def _get_file_path(self, file_name: str) -> Path:
        """Constructs the full path for a given file name."""
        return self.base_path / f"{file_name}.json"

    def read_data(self, file_name: str) -> Optional[Dict[str, Any]]:
        """
        Reads and parses JSON data from a file.

        Args:
            file_name: The name of the data file (without extension).

        Returns:
            A dictionary containing the loaded data, or None if the file
            does not exist or is empty.
        """
        file_path = self._get_file_path(file_name)
        if not file_path.exists() or os.path.getsize(file_path) == 0:
            _logger.warning(f"Data file not found or empty: {file_path}")
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                _logger.debug(f"Successfully read data from {file_path}")
                return data
        except (json.JSONDecodeError, IOError) as e:
            _logger.error(f"Error reading data from {file_path}: {e}", exc_info=True)
            return None

    def write_data(self, file_name: str, data: Dict[str, Any]) -> bool:
        """
        Writes a dictionary to a JSON file.

        Args:
            file_name: The name of the data file (without extension).
            data: The dictionary to write.

        Returns:
            True if the write was successful, False otherwise.
        """
        file_path = self._get_file_path(file_name)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            _logger.debug(f"Successfully wrote data to {file_path}")
            return True
        except IOError as e:
            _logger.error(f"Error writing data to {file_path}: {e}", exc_info=True)
            return False

def get_persistence_service() -> PersistenceService:
    """
    Returns the singleton instance of the PersistenceService.
    """
    global _persistence_service_instance
    if _persistence_service_instance is None:
        _persistence_service_instance = PersistenceService()
    return _persistence_service_instance
