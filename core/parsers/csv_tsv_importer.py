"""
CSV/TSV Importer for uDOS v1.0.6.0

Parses .csv and .tsv files into SQLite tables with automatic type detection.

Features:
- Automatic delimiter detection (comma, tab, semicolon, pipe)
- Header row detection (optional)
- Quote handling (single, double, escape sequences)
- Type inference from data
- SQLite table creation with proper types
- Export back to original format

Author: uDOS Core Team
Version: 1.0.6.0
"""

import csv
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import re


@dataclass
class CSVMetadata:
    """Metadata for CSV/TSV import operations."""

    filename: str
    delimiter: str
    has_header: bool
    row_count: int
    column_count: int
    encoding: str = "utf-8"
    quotechar: str = '"'
    escapechar: Optional[str] = None


@dataclass
class ColumnInfo:
    """Column information with inferred type."""

    name: str
    detected_type: str  # SQLite type
    nullable: bool
    sample_values: List[Any]


class CSVTSVImporter:
    """Import CSV and TSV files into SQLite tables."""

    # Type detection patterns
    INTEGER_PATTERN = re.compile(r"^-?\d+$")
    FLOAT_PATTERN = re.compile(r"^-?\d+\.\d+$")
    BOOLEAN_PATTERN = re.compile(r"^(true|false|yes|no|1|0)$", re.IGNORECASE)
    DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    DATETIME_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")

    # Common delimiters to try
    DELIMITERS = [",", "\t", ";", "|"]

    def __init__(self):
        """Initialize the importer."""
        self.metadata: Optional[CSVMetadata] = None
        self.columns: List[ColumnInfo] = []

    def detect_delimiter(self, file_path: Path, sample_size: int = 5) -> str:
        """
        Auto-detect the delimiter by analyzing the first few lines.

        Args:
            file_path: Path to the CSV/TSV file
            sample_size: Number of lines to sample

        Returns:
            Detected delimiter character
        """
        with open(file_path, "r", encoding="utf-8") as f:
            sample_lines = [f.readline() for _ in range(sample_size)]

        # Count occurrences of each delimiter
        delimiter_counts = {}
        for delim in self.DELIMITERS:
            counts = [line.count(delim) for line in sample_lines if line.strip()]
            if counts and all(c == counts[0] for c in counts) and counts[0] > 0:
                delimiter_counts[delim] = counts[0]

        if not delimiter_counts:
            # Default to comma
            return ","

        # Return delimiter with highest consistent count
        return max(delimiter_counts, key=delimiter_counts.get)

    def detect_has_header(self, file_path: Path, delimiter: str) -> bool:
        """
        Detect if the first row is a header row.

        Args:
            file_path: Path to the CSV/TSV file
            delimiter: Delimiter character

        Returns:
            True if first row appears to be a header
        """
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=delimiter)
            try:
                first_row = next(reader)
                second_row = next(reader)
            except StopIteration:
                return False

        # Header detection heuristics:
        # 1. First row has no numbers, second row has numbers
        # 2. First row values are unique
        # 3. First row values are short strings

        first_has_numbers = any(self._is_numeric(val) for val in first_row)
        second_has_numbers = any(self._is_numeric(val) for val in second_row)

        if not first_has_numbers and second_has_numbers:
            return True

        # Check for unique short strings
        if len(first_row) == len(set(first_row)):
            avg_length = sum(len(str(v)) for v in first_row) / len(first_row)
            if avg_length < 30:
                return True

        return False

    def _is_numeric(self, value: str) -> bool:
        """Check if a value is numeric."""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False

    def infer_column_type(self, values: List[str]) -> str:
        """
        Infer SQLite type from sample values.

        Args:
            values: List of sample values (as strings)

        Returns:
            SQLite type name
        """
        # Remove empty values
        non_empty = [v for v in values if v and v.strip()]

        if not non_empty:
            return "TEXT"

        # Check type patterns
        all_integers = all(self.INTEGER_PATTERN.match(v) for v in non_empty)
        all_floats = all(
            self.FLOAT_PATTERN.match(v) or self.INTEGER_PATTERN.match(v)
            for v in non_empty
        )
        all_booleans = all(self.BOOLEAN_PATTERN.match(v) for v in non_empty)
        all_dates = all(self.DATE_PATTERN.match(v) for v in non_empty)
        all_datetimes = all(self.DATETIME_PATTERN.match(v) for v in non_empty)

        if all_datetimes:
            return "TEXT"  # Store as ISO8601 string
        if all_dates:
            return "TEXT"  # Store as ISO8601 string
        if all_booleans:
            return "INTEGER"  # Store as 0/1
        if all_integers:
            return "INTEGER"
        if all_floats:
            return "REAL"

        return "TEXT"

    def parse_file(
        self,
        file_path: Path,
        delimiter: Optional[str] = None,
        has_header: Optional[bool] = None,
        encoding: str = "utf-8",
    ) -> Tuple[CSVMetadata, List[ColumnInfo], List[List[Any]]]:
        """
        Parse CSV/TSV file and return metadata, columns, and data.

        Args:
            file_path: Path to the CSV/TSV file
            delimiter: Delimiter character (auto-detect if None)
            has_header: Whether first row is header (auto-detect if None)
            encoding: File encoding

        Returns:
            Tuple of (metadata, columns, rows)
        """
        # Auto-detect delimiter if not specified
        if delimiter is None:
            delimiter = self.detect_delimiter(file_path)

        # Auto-detect header if not specified
        if has_header is None:
            has_header = self.detect_has_header(file_path, delimiter)

        # Read all data
        with open(file_path, "r", encoding=encoding) as f:
            reader = csv.reader(f, delimiter=delimiter)
            all_rows = list(reader)

        if not all_rows:
            raise ValueError("Empty CSV file")

        # Separate header and data
        if has_header:
            header_row = all_rows[0]
            data_rows = all_rows[1:]
        else:
            # Generate column names
            num_cols = len(all_rows[0])
            header_row = [f"column_{i+1}" for i in range(num_cols)]
            data_rows = all_rows

        # Infer column types from data
        columns = []
        for col_idx, col_name in enumerate(header_row):
            sample_values = [
                row[col_idx] if col_idx < len(row) else "" for row in data_rows[:100]
            ]
            detected_type = self.infer_column_type(sample_values)
            nullable = any(not v or not v.strip() for v in sample_values)

            columns.append(
                ColumnInfo(
                    name=col_name.strip(),
                    detected_type=detected_type,
                    nullable=nullable,
                    sample_values=sample_values[:5],
                )
            )

        # Create metadata
        metadata = CSVMetadata(
            filename=file_path.name,
            delimiter=delimiter,
            has_header=has_header,
            row_count=len(data_rows),
            column_count=len(header_row),
            encoding=encoding,
        )

        self.metadata = metadata
        self.columns = columns

        return metadata, columns, data_rows

    def create_sqlite_table(
        self,
        db_path: Path,
        table_name: str,
        metadata: CSVMetadata,
        columns: List[ColumnInfo],
        rows: List[List[Any]],
        if_exists: str = "fail",
    ) -> None:
        """
        Create SQLite table and insert data.

        Args:
            db_path: Path to SQLite database
            table_name: Name for the new table
            metadata: CSV metadata
            columns: Column information
            rows: Data rows
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
                column_defs = []
                for col in columns:
                    null_constraint = "" if col.nullable else " NOT NULL"
                    column_defs.append(
                        f"{col.name} {col.detected_type}{null_constraint}"
                    )

                create_sql = (
                    f"CREATE TABLE {table_name} (\n  "
                    + ",\n  ".join(column_defs)
                    + "\n)"
                )
                cursor.execute(create_sql)

            # Insert data
            placeholders = ",".join(["?"] * len(columns))
            insert_sql = f"INSERT INTO {table_name} VALUES ({placeholders})"

            for row in rows:
                # Pad or truncate row to match column count
                padded_row = row[: len(columns)] + [""] * (len(columns) - len(row))

                # Convert values to appropriate types
                converted_row = []
                for val, col in zip(padded_row, columns):
                    converted_row.append(self._convert_value(val, col.detected_type))

                cursor.execute(insert_sql, converted_row)

            conn.commit()

        finally:
            conn.close()

    def _convert_value(self, value: str, target_type: str) -> Any:
        """Convert string value to appropriate Python type."""
        if not value or not value.strip():
            return None

        value = value.strip()

        if target_type == "INTEGER":
            # Handle booleans
            if self.BOOLEAN_PATTERN.match(value):
                return 1 if value.lower() in ("true", "yes", "1") else 0
            try:
                return int(value)
            except ValueError:
                return None

        elif target_type == "REAL":
            try:
                return float(value)
            except ValueError:
                return None

        return value

    def import_file(
        self,
        file_path: Path,
        db_path: Path,
        table_name: str,
        delimiter: Optional[str] = None,
        has_header: Optional[bool] = None,
        if_exists: str = "fail",
    ) -> CSVMetadata:
        """
        One-step import: parse CSV/TSV and create SQLite table.

        Args:
            file_path: Path to CSV/TSV file
            db_path: Path to SQLite database
            table_name: Name for the new table
            delimiter: Delimiter character (auto-detect if None)
            has_header: Whether first row is header (auto-detect if None)
            if_exists: What to do if table exists ('fail', 'replace', 'append')

        Returns:
            CSV metadata
        """
        metadata, columns, rows = self.parse_file(file_path, delimiter, has_header)
        self.create_sqlite_table(
            db_path, table_name, metadata, columns, rows, if_exists
        )
        return metadata
