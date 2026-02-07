"""
Markdown Table Parser - v1.0.6.0

Parses .table.md files with frontmatter metadata into SQLite tables.

Format:
--------
---
table_name: records
columns:
  - name: id
    type: integer
    primary_key: true
  - name: label
    type: text
---

| id | label | created_at |
|----|-------|-----------|
| 1 | Alpha | 2026-01-01 |
| 2 | Beta | 2026-01-02 |
"""

import re
import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class ColumnDef:
    """Column definition from frontmatter."""

    name: str
    type: str
    primary_key: bool = False
    not_null: bool = False
    unique: bool = False
    default: Optional[Any] = None


@dataclass
class TableMetadata:
    """Table metadata from frontmatter."""

    name: str
    columns: List[ColumnDef]
    description: Optional[str] = None
    source: Optional[str] = None
    exported_at: Optional[str] = None
    row_count: Optional[int] = None


class MarkdownTableParser:
    """Parse .table.md files with frontmatter into SQLite."""

    # Type mapping from Markdown → SQLite
    TYPE_MAPPING = {
        "integer": "INTEGER",
        "int": "INTEGER",
        "text": "TEXT",
        "string": "TEXT",
        "real": "REAL",
        "float": "REAL",
        "decimal": "REAL",
        "boolean": "BOOLEAN",
        "bool": "BOOLEAN",
        "datetime": "TEXT",
        "date": "TEXT",
        "time": "TEXT",
        "blob": "BLOB",
        "json": "TEXT",
    }

    def __init__(self):
        self.metadata: Optional[TableMetadata] = None
        self.rows: List[Dict[str, Any]] = []

    def parse_file(self, filepath: str) -> Tuple[TableMetadata, List[Dict[str, Any]]]:
        """Parse .table.md file and return metadata and rows."""
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        return self.parse_content(content)

    def parse_content(self, content: str) -> Tuple[TableMetadata, List[Dict[str, Any]]]:
        """Parse .table.md content string."""
        # Split frontmatter and markdown
        frontmatter, markdown_table = self._extract_frontmatter(content)

        # Parse metadata
        self.metadata = self._parse_metadata(frontmatter)

        # Parse table
        self.rows = self._parse_table(markdown_table)

        return self.metadata, self.rows

    def _extract_frontmatter(self, content: str) -> Tuple[str, str]:
        """Extract frontmatter (YAML) and table content."""
        lines = content.split("\n")

        if not lines[0].startswith("---"):
            raise ValueError("Content must start with '---' for frontmatter")

        # Find closing ---
        end_idx = None
        for i in range(1, len(lines)):
            if lines[i].startswith("---"):
                end_idx = i
                break

        if end_idx is None:
            raise ValueError("Missing closing '---' for frontmatter")

        frontmatter = "\n".join(lines[1:end_idx])
        markdown_table = "\n".join(lines[end_idx + 1 :])

        return frontmatter, markdown_table

    def _parse_metadata(self, frontmatter: str) -> TableMetadata:
        """Parse YAML frontmatter into TableMetadata."""
        metadata = {}
        columns = []

        for line in frontmatter.split("\n"):
            line = line.strip()
            if not line:
                continue

            # Parse top-level keys
            if ": " in line:
                key, value = line.split(": ", 1)
                key = key.strip()
                value = value.strip()

                if key == "table_name":
                    metadata["name"] = value
                elif key == "description":
                    metadata["description"] = value
                elif key == "source_db":
                    metadata["source"] = value
                elif key == "exported_at":
                    metadata["exported_at"] = value
                elif key == "row_count":
                    try:
                        metadata["row_count"] = int(value)
                    except ValueError:
                        pass
                elif key == "columns":
                    # Start of columns list
                    pass

        # Parse columns (YAML list)
        columns = self._parse_columns(frontmatter)

        if "name" not in metadata:
            raise ValueError("Missing 'table_name' in frontmatter")

        if not columns:
            raise ValueError("Missing 'columns' definition in frontmatter")

        metadata["columns"] = columns
        return TableMetadata(**metadata)

    def _parse_columns(self, frontmatter: str) -> List[ColumnDef]:
        """Parse columns list from YAML frontmatter."""
        columns = []
        lines = frontmatter.split("\n")

        in_columns = False
        current_column = {}

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("columns:"):
                in_columns = True
                continue

            if in_columns:
                if stripped.startswith("- name:"):
                    # Start new column
                    if current_column:
                        columns.append(self._build_column_def(current_column))
                    current_column = {"name": stripped.split(": ", 1)[1].strip()}

                elif stripped.startswith("name:") and current_column:
                    current_column["name"] = stripped.split(": ", 1)[1].strip()

                elif stripped.startswith("type:") and current_column:
                    current_column["type"] = stripped.split(": ", 1)[1].strip()

                elif stripped.startswith("primary_key:") and current_column:
                    current_column["primary_key"] = (
                        stripped.split(": ", 1)[1].strip().lower() == "true"
                    )

                elif stripped.startswith("not_null:") and current_column:
                    current_column["not_null"] = (
                        stripped.split(": ", 1)[1].strip().lower() == "true"
                    )

                elif stripped.startswith("unique:") and current_column:
                    current_column["unique"] = (
                        stripped.split(": ", 1)[1].strip().lower() == "true"
                    )

                elif stripped.startswith("default:") and current_column:
                    current_column["default"] = stripped.split(": ", 1)[1].strip()

                # Stop parsing columns when we hit another top-level key
                elif (
                    stripped
                    and not stripped.startswith("-")
                    and not stripped.startswith("  ")
                ):
                    in_columns = False
                    if current_column:
                        columns.append(self._build_column_def(current_column))
                    break

        # Don't forget the last column
        if current_column:
            columns.append(self._build_column_def(current_column))

        return columns

    def _build_column_def(self, col_dict: Dict[str, Any]) -> ColumnDef:
        """Build ColumnDef from parsed dictionary."""
        if "name" not in col_dict or "type" not in col_dict:
            raise ValueError(f"Column missing 'name' or 'type': {col_dict}")

        return ColumnDef(
            name=col_dict["name"],
            type=col_dict["type"],
            primary_key=col_dict.get("primary_key", False),
            not_null=col_dict.get("not_null", False),
            unique=col_dict.get("unique", False),
            default=col_dict.get("default"),
        )

    def _parse_table(self, markdown_content: str) -> List[Dict[str, Any]]:
        """Parse Markdown table format into rows."""
        rows = []
        lines = [line.strip() for line in markdown_content.split("\n") if line.strip()]

        if not lines:
            return rows

        # Find the table (starts with |)
        table_lines = [line for line in lines if line.startswith("|")]

        if len(table_lines) < 3:
            return rows  # Need header, separator, at least one data row

        # Parse header
        header_line = table_lines[0]
        headers = self._parse_table_row(header_line)

        # Parse separator (skip)
        # separator = table_lines[1]

        # Parse data rows
        for data_line in table_lines[2:]:
            values = self._parse_table_row(data_line)

            # Match values to column names
            row = {}
            for i, header in enumerate(headers):
                if i < len(values):
                    # Convert value based on column type
                    col_def = next(
                        (c for c in self.metadata.columns if c.name == header), None
                    )
                    if col_def:
                        row[header] = self._convert_value(values[i], col_def.type)
                    else:
                        row[header] = values[i]

            rows.append(row)

        return rows

    def _parse_table_row(self, row_line: str) -> List[str]:
        """Parse a single table row (pipe-delimited)."""
        # Remove leading/trailing pipes and split
        cleaned = row_line.strip("|").strip()
        cells = cleaned.split("|")
        return [cell.strip() for cell in cells]

    def _convert_value(self, value: str, col_type: str) -> Any:
        """Convert string value to appropriate Python type."""
        if not value or value.lower() in ("null", "none", "n/a", ""):
            return None

        col_type_lower = col_type.lower()

        if col_type_lower in ("integer", "int"):
            try:
                return int(value)
            except ValueError:
                return value

        elif col_type_lower in ("real", "float", "decimal"):
            try:
                return float(value)
            except ValueError:
                return value

        elif col_type_lower in ("boolean", "bool"):
            return value.lower() in ("true", "1", "yes", "on")

        elif col_type_lower == "json":
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value

        else:
            return value

    def create_sqlite_table(self, db_path: str, overwrite: bool = False) -> bool:
        """Create SQLite table from parsed metadata and insert rows."""
        if not self.metadata or not self.rows:
            raise ValueError("No metadata or rows parsed")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            # Drop table if exists and overwrite=True
            if overwrite:
                cursor.execute(f"DROP TABLE IF EXISTS [{self.metadata.name}]")

            # Build CREATE TABLE statement
            create_sql = self._build_create_table_sql()
            cursor.execute(create_sql)

            # Insert rows
            col_names = [col.name for col in self.metadata.columns]
            placeholders = ",".join(["?" for _ in col_names])
            insert_sql = f"INSERT INTO [{self.metadata.name}] ({','.join(col_names)}) VALUES ({placeholders})"

            for row in self.rows:
                values = [row.get(col_name) for col_name in col_names]
                cursor.execute(insert_sql, values)

            conn.commit()
            return True

        except sqlite3.Error as e:
            conn.rollback()
            raise RuntimeError(f"SQLite error: {e}")

        finally:
            conn.close()

    def _build_create_table_sql(self) -> str:
        """Build CREATE TABLE SQL statement."""
        col_defs = []

        for col in self.metadata.columns:
            sql_type = self.TYPE_MAPPING.get(col.type.lower(), col.type)
            col_def = f"[{col.name}] {sql_type}"

            if col.primary_key:
                col_def += " PRIMARY KEY"
            if col.not_null:
                col_def += " NOT NULL"
            if col.unique:
                col_def += " UNIQUE"
            if col.default:
                col_def += f" DEFAULT {col.default}"

            col_defs.append(col_def)

        sql = f"CREATE TABLE [{self.metadata.name}] ({', '.join(col_defs)})"
        return sql

    def export_to_markdown(
        self, db_path: str, table_name: str, output_path: str
    ) -> bool:
        """Export SQLite table to .table.md format."""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            # Get table schema
            cursor.execute(f"PRAGMA table_info([{table_name}])")
            schema = cursor.fetchall()

            if not schema:
                raise ValueError(f"Table '{table_name}' not found")

            columns = [{"name": col[1], "type": col[2]} for col in schema]

            # Get data
            cursor.execute(f"SELECT * FROM [{table_name}]")
            rows = cursor.fetchall()

            # Build frontmatter
            frontmatter = f"---\ntable_name: {table_name}\n"
            frontmatter += f"exported_at: {datetime.now().isoformat()}Z\n"
            frontmatter += f"row_count: {len(rows)}\n"
            frontmatter += "columns:\n"

            for col in columns:
                frontmatter += f"  - name: {col['name']}\n"
                frontmatter += f"    type: {col['type']}\n"

            frontmatter += "---\n"

            # Build table
            col_names = [col["name"] for col in columns]
            header = "| " + " | ".join(col_names) + " |"
            separator = "|-" + "-|-" * (len(col_names) - 1) + "-|"

            data_rows = []
            for row in rows:
                data_rows.append(
                    "| "
                    + " | ".join(str(v) if v is not None else "" for v in row)
                    + " |"
                )

            # Write file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(frontmatter)
                f.write("\n" + header + "\n")
                f.write(separator + "\n")
                for data_row in data_rows:
                    f.write(data_row + "\n")

            return True

        finally:
            conn.close()
