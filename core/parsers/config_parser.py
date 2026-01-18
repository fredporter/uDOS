"""
YAML/TOML Config Parser for uDOS v1.0.6.0

Parses YAML and TOML configuration files into SQLite tables.

Features:
- YAML document parsing
- TOML section parsing
- Nested structure flattening
- List/array handling
- Type detection
- Configuration validation

Author: uDOS Core Team
Version: 1.0.6.0
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import re

try:
    import yaml
except ImportError:
    yaml = None

try:
    import tomli  # For Python < 3.11
except ImportError:
    try:
        import tomllib as tomli  # Python 3.11+
    except ImportError:
        tomli = None


@dataclass
class ConfigMetadata:
    """Metadata for config file import operations."""

    filename: str
    format: str  # "yaml" or "toml"
    section_count: int
    key_count: int
    nested_depth: int
    encoding: str = "utf-8"


class ConfigParser:
    """Parse YAML and TOML configuration files into SQLite tables."""

    def __init__(self, flatten_strategy: str = "dot", max_depth: int = 5):
        """
        Initialize the config parser.

        Args:
            flatten_strategy: "dot" (a.b.c) or "underscore" (a_b_c)
            max_depth: Maximum nesting depth for flattening
        """
        self.flatten_strategy = flatten_strategy
        self.max_depth = max_depth
        self.metadata: Optional[ConfigMetadata] = None

    def detect_format(self, file_path: Path) -> str:
        """
        Detect if file is YAML or TOML based on extension.

        Args:
            file_path: Path to the file

        Returns:
            "yaml" or "toml"
        """
        suffix = file_path.suffix.lower()
        if suffix in (".yaml", ".yml"):
            return "yaml"
        elif suffix in (".toml",):
            return "toml"
        else:
            raise ValueError(f"Unknown config format: {suffix}")

    def infer_type(self, value: Any) -> str:
        """
        Infer SQLite type from Python value.

        Args:
            value: Python value

        Returns:
            SQLite type name
        """
        if value is None:
            return "TEXT"
        elif isinstance(value, bool):
            return "INTEGER"
        elif isinstance(value, int):
            return "INTEGER"
        elif isinstance(value, float):
            return "REAL"
        elif isinstance(value, (list, dict)):
            return "TEXT"  # Store as string representation
        else:
            return "TEXT"

    def flatten_dict(
        self, d: Dict[str, Any], prefix: str = "", depth: int = 0
    ) -> Dict[str, Any]:
        """
        Flatten nested dictionary.

        Args:
            d: Nested dictionary
            prefix: Current key prefix
            depth: Current nesting depth

        Returns:
            Flattened dictionary
        """
        result = {}
        separator = "." if self.flatten_strategy == "dot" else "_"

        for key, value in d.items():
            new_key = f"{prefix}{separator}{key}" if prefix else key

            if isinstance(value, dict) and depth < self.max_depth:
                # Recursively flatten nested dict
                result.update(self.flatten_dict(value, new_key, depth + 1))
            elif isinstance(value, list):
                # Store lists as comma-separated strings
                if all(isinstance(item, (str, int, float, bool)) for item in value):
                    result[new_key] = ",".join(str(item) for item in value)
                else:
                    result[new_key] = str(value)
            else:
                result[new_key] = value

        return result

    def parse_yaml_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse YAML file.

        Args:
            file_path: Path to YAML file

        Returns:
            Parsed configuration dictionary
        """
        if yaml is None:
            raise ImportError("PyYAML not installed. Install with: pip install pyyaml")

        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            # Wrap non-dict data
            data = {"value": data}

        return self.flatten_dict(data)

    def parse_toml_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse TOML file.

        Args:
            file_path: Path to TOML file

        Returns:
            Parsed configuration dictionary
        """
        if tomli is None:
            raise ImportError("tomli not installed. Install with: pip install tomli")

        with open(file_path, "rb") as f:
            data = tomli.load(f)

        return self.flatten_dict(data)

    def parse_file(
        self, file_path: Path, format_hint: Optional[str] = None
    ) -> tuple[ConfigMetadata, Dict[str, Any]]:
        """
        Parse YAML or TOML file.

        Args:
            file_path: Path to the file
            format_hint: Optional format hint ("yaml" or "toml")

        Returns:
            Tuple of (metadata, flattened_config)
        """
        # Detect format
        format_type = format_hint if format_hint else self.detect_format(file_path)

        # Parse based on format
        if format_type == "yaml":
            config = self.parse_yaml_file(file_path)
        elif format_type == "toml":
            config = self.parse_toml_file(file_path)
        else:
            raise ValueError(f"Unknown format: {format_type}")

        # Calculate nesting depth
        max_depth = 0
        for key in config.keys():
            depth = key.count("." if self.flatten_strategy == "dot" else "_")
            max_depth = max(max_depth, depth)

        # Count sections (top-level keys before first separator)
        sections = set()
        for key in config.keys():
            sep = "." if self.flatten_strategy == "dot" else "_"
            if sep in key:
                sections.add(key.split(sep)[0])
            else:
                sections.add(key)

        # Create metadata
        metadata = ConfigMetadata(
            filename=file_path.name,
            format=format_type,
            section_count=len(sections),
            key_count=len(config),
            nested_depth=max_depth,
            encoding="utf-8",
        )

        self.metadata = metadata
        return metadata, config

    def create_sqlite_table(
        self,
        db_path: Path,
        table_name: str,
        config: Dict[str, Any],
        if_exists: str = "fail",
    ) -> None:
        """
        Create SQLite table with key-value structure for config data.

        Args:
            db_path: Path to SQLite database
            table_name: Name for the new table
            config: Flattened configuration dictionary
            if_exists: What to do if table exists ('fail', 'replace', 'append')
        """
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            # Check if table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,),
            )
            exists = cursor.fetchone() is not None

            if exists:
                if if_exists == "fail":
                    raise ValueError(f"Table {table_name} already exists")
                elif if_exists == "replace":
                    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                elif if_exists != "append":
                    raise ValueError(f"Invalid if_exists value: {if_exists}")

            # Create key-value table
            if not exists or if_exists == "replace":
                create_sql = f"""
                CREATE TABLE {table_name} (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    type TEXT
                )
                """
                cursor.execute(create_sql)

            # Insert config entries
            for key, value in config.items():
                value_type = self.infer_type(value)
                value_str = str(value) if value is not None else None

                if if_exists == "append":
                    # Use INSERT OR REPLACE for append mode
                    cursor.execute(
                        f"INSERT OR REPLACE INTO {table_name} (key, value, type) VALUES (?, ?, ?)",
                        (key, value_str, value_type),
                    )
                else:
                    cursor.execute(
                        f"INSERT INTO {table_name} (key, value, type) VALUES (?, ?, ?)",
                        (key, value_str, value_type),
                    )

            conn.commit()

        finally:
            conn.close()

    def import_file(
        self,
        file_path: Path,
        db_path: Path,
        table_name: str,
        format_hint: Optional[str] = None,
        if_exists: str = "fail",
    ) -> ConfigMetadata:
        """
        One-step import: parse config file and create SQLite table.

        Args:
            file_path: Path to YAML/TOML file
            db_path: Path to SQLite database
            table_name: Name for the new table
            format_hint: Optional format hint ("yaml" or "toml")
            if_exists: What to do if table exists ('fail', 'replace', 'append')

        Returns:
            Config metadata
        """
        metadata, config = self.parse_file(file_path, format_hint)
        self.create_sqlite_table(db_path, table_name, config, if_exists)
        return metadata
