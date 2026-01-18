"""
JSON/JSONL Parser for uDOS v1.0.6.0

Parses JSON and JSONL (JSON Lines) files into SQLite tables.

Features:
- Flat JSON objects → direct table mapping
- Nested JSON → flattened columns (dot notation)
- Arrays of objects → multiple rows
- JSONL streaming support
- Automatic type detection
- Configurable flattening strategies

Author: uDOS Core Team
Version: 1.0.6.0
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any, Iterator
from dataclasses import dataclass
from datetime import datetime
import re


@dataclass
class JSONMetadata:
    """Metadata for JSON import operations."""

    filename: str
    format: str  # "json" or "jsonl"
    record_count: int
    schema_detected: Dict[str, str]
    nested_depth: int
    encoding: str = "utf-8"


class JSONParser:
    """Parse JSON and JSONL files into SQLite tables."""

    def __init__(self, max_nesting_depth: int = 3, flatten_strategy: str = "dot"):
        """
        Initialize the JSON parser.

        Args:
            max_nesting_depth: Maximum depth for nested object flattening
            flatten_strategy: "dot" (a.b.c) or "underscore" (a_b_c)
        """
        self.max_nesting_depth = max_nesting_depth
        self.flatten_strategy = flatten_strategy
        self.metadata: Optional[JSONMetadata] = None

    def detect_format(self, file_path: Path) -> str:
        """
        Detect if file is JSON or JSONL format.

        Args:
            file_path: Path to the file

        Returns:
            "json" or "jsonl"
        """
        with open(file_path, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()
            second_line = f.readline().strip()

        # JSONL: each line is valid JSON
        # JSON: single object or array

        if not first_line:
            raise ValueError("Empty file")

        try:
            json.loads(first_line)
            # First line is valid JSON
            if second_line:
                try:
                    json.loads(second_line)
                    # Both lines are valid JSON → JSONL
                    return "jsonl"
                except json.JSONDecodeError:
                    # First line valid, second not → single JSON
                    return "json"
            else:
                # Only one line → single JSON object
                return "json"
        except json.JSONDecodeError:
            # First line not valid JSON → must be multi-line JSON
            return "json"

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
            return "TEXT"  # Store as JSON string
        else:
            return "TEXT"

    def flatten_object(
        self, obj: Dict[str, Any], prefix: str = "", depth: int = 0
    ) -> Dict[str, Any]:
        """
        Flatten nested dictionary to flat structure.

        Args:
            obj: Nested dictionary
            prefix: Current key prefix
            depth: Current nesting depth

        Returns:
            Flattened dictionary
        """
        result = {}
        separator = "." if self.flatten_strategy == "dot" else "_"

        for key, value in obj.items():
            new_key = f"{prefix}{separator}{key}" if prefix else key

            if isinstance(value, dict) and depth < self.max_nesting_depth:
                # Recursively flatten nested object
                result.update(self.flatten_object(value, new_key, depth + 1))
            elif isinstance(value, list):
                # Convert list to JSON string
                result[new_key] = json.dumps(value)
            else:
                result[new_key] = value

        return result

    def parse_json_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Parse standard JSON file.

        Args:
            file_path: Path to JSON file

        Returns:
            List of record dictionaries
        """
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            # Single object → single row
            return [self.flatten_object(data)]
        elif isinstance(data, list):
            # Array of objects → multiple rows
            return [
                self.flatten_object(item) if isinstance(item, dict) else {"value": item}
                for item in data
            ]
        else:
            # Primitive value
            return [{"value": data}]

    def parse_jsonl_file(self, file_path: Path) -> Iterator[Dict[str, Any]]:
        """
        Parse JSONL (JSON Lines) file.

        Args:
            file_path: Path to JSONL file

        Yields:
            Flattened record dictionaries
        """
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    if isinstance(obj, dict):
                        yield self.flatten_object(obj)
                    else:
                        yield {"value": obj}
                except json.JSONDecodeError as e:
                    print(f"Warning: Skipping invalid JSON line: {e}")
                    continue

    def detect_schema(self, records: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Detect schema (column names and types) from records.

        Args:
            records: List of record dictionaries

        Returns:
            Dictionary mapping column names to SQLite types
        """
        schema = {}

        # Collect all keys
        all_keys = set()
        for record in records:
            all_keys.update(record.keys())

        # Infer type for each key
        for key in all_keys:
            # Sample values for this key
            values = [record.get(key) for record in records if key in record]
            values = [v for v in values if v is not None]

            if not values:
                schema[key] = "TEXT"
                continue

            # Determine most common type
            types = [self.infer_type(v) for v in values]
            type_counts = {}
            for t in types:
                type_counts[t] = type_counts.get(t, 0) + 1

            # Use most common type
            schema[key] = max(type_counts, key=type_counts.get)

        return schema

    def parse_file(
        self, file_path: Path, format_hint: Optional[str] = None
    ) -> tuple[JSONMetadata, List[Dict[str, Any]]]:
        """
        Parse JSON or JSONL file.

        Args:
            file_path: Path to the file
            format_hint: Optional format hint ("json" or "jsonl")

        Returns:
            Tuple of (metadata, records)
        """
        # Detect format
        format_type = format_hint if format_hint else self.detect_format(file_path)

        # Parse based on format
        if format_type == "json":
            records = self.parse_json_file(file_path)
        else:
            records = list(self.parse_jsonl_file(file_path))

        # Detect schema
        schema = self.detect_schema(records)

        # Calculate nesting depth
        max_depth = 0
        for key in schema.keys():
            depth = key.count("." if self.flatten_strategy == "dot" else "_")
            max_depth = max(max_depth, depth)

        # Create metadata
        metadata = JSONMetadata(
            filename=file_path.name,
            format=format_type,
            record_count=len(records),
            schema_detected=schema,
            nested_depth=max_depth,
            encoding="utf-8",
        )

        self.metadata = metadata
        return metadata, records

    def create_sqlite_table(
        self,
        db_path: Path,
        table_name: str,
        schema: Dict[str, str],
        records: List[Dict[str, Any]],
        if_exists: str = "fail",
    ) -> None:
        """
        Create SQLite table and insert JSON data.

        Args:
            db_path: Path to SQLite database
            table_name: Name for the new table
            schema: Column names and types
            records: Data records
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

            # Create table if needed
            if not exists or if_exists == "replace":
                column_defs = [
                    f"{col_name} {col_type}" for col_name, col_type in schema.items()
                ]
                create_sql = (
                    f"CREATE TABLE {table_name} (\n  "
                    + ",\n  ".join(column_defs)
                    + "\n)"
                )
                cursor.execute(create_sql)

            # Insert records
            if records:
                # Get all column names
                columns = list(schema.keys())
                placeholders = ",".join(["?"] * len(columns))
                insert_sql = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"

                for record in records:
                    values = [record.get(col) for col in columns]
                    cursor.execute(insert_sql, values)

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
    ) -> JSONMetadata:
        """
        One-step import: parse JSON/JSONL and create SQLite table.

        Args:
            file_path: Path to JSON/JSONL file
            db_path: Path to SQLite database
            table_name: Name for the new table
            format_hint: Optional format hint ("json" or "jsonl")
            if_exists: What to do if table exists ('fail', 'replace', 'append')

        Returns:
            JSON metadata
        """
        metadata, records = self.parse_file(file_path, format_hint)
        self.create_sqlite_table(
            db_path, table_name, metadata.schema_detected, records, if_exists
        )
        return metadata
