"""
SQL Script Executor for uDOS v1.0.6.0

Execute SQL scripts for data transformation with safety constraints.

Features:
- Multi-statement SQL execution
- Transaction support
- Common Table Expressions (CTEs)
- Temporary tables
- Safety constraints (read-only mode, no DROP on protected tables)
- Script validation

Author: uDOS Core Team
Version: 1.0.6.0
"""

import sqlite3
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class ExecutionMode(Enum):
    """SQL execution modes."""

    READ_ONLY = "read_only"  # Only SELECT allowed
    READ_WRITE = "read_write"  # SELECT, INSERT, UPDATE allowed
    FULL = "full"  # All operations allowed


@dataclass
class SQLExecutionResult:
    """Result of SQL script execution."""

    statements_executed: int
    rows_affected: int
    error: Optional[str]
    results: List[List[Any]]  # Results from SELECT statements


class SQLExecutor:
    """Execute SQL scripts with safety constraints."""

    # Dangerous keywords
    DANGEROUS_PATTERNS = [
        r"\bDROP\s+DATABASE\b",
        r"\bDROP\s+SCHEMA\b",
        r"\bTRUNCATE\s+TABLE\b",
        r"\bDELETE\s+FROM\s+\w+\s*$",  # DELETE without WHERE
    ]

    # Write operations
    WRITE_PATTERNS = [
        r"\bINSERT\b",
        r"\bUPDATE\b",
        r"\bDELETE\b",
        r"\bCREATE\b",
        r"\bDROP\b",
        r"\bALTER\b",
    ]

    def __init__(
        self,
        mode: ExecutionMode = ExecutionMode.READ_WRITE,
        protected_tables: Optional[List[str]] = None,
    ):
        """
        Initialize SQL executor.

        Args:
            mode: Execution mode (read_only, read_write, full)
            protected_tables: Tables that cannot be dropped or truncated
        """
        self.mode = mode
        self.protected_tables = protected_tables or []

    def split_statements(self, sql: str) -> List[str]:
        """
        Split SQL script into individual statements.

        Args:
            sql: SQL script text

        Returns:
            List of SQL statements
        """
        # Remove comments
        sql = re.sub(r"--[^\n]*", "", sql)
        sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)

        # Split on semicolons (simple approach)
        statements = [s.strip() for s in sql.split(";") if s.strip()]

        return statements

    def validate_statement(self, statement: str) -> tuple[bool, Optional[str]]:
        """
        Validate SQL statement against safety constraints.

        Args:
            statement: SQL statement to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        statement_upper = statement.upper()

        # Check for dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, statement_upper):
                return False, f"Dangerous operation detected: {pattern}"

        # Check execution mode constraints
        if self.mode == ExecutionMode.READ_ONLY:
            for pattern in self.WRITE_PATTERNS:
                if re.search(pattern, statement_upper):
                    return (
                        False,
                        f"Write operation not allowed in read-only mode: {pattern}",
                    )

        # Check protected tables
        if self.protected_tables:
            for table in self.protected_tables:
                # Check for DROP TABLE
                if re.search(rf"\bDROP\s+TABLE\s+{table}\b", statement_upper):
                    return False, f"Cannot drop protected table: {table}"
                # Check for TRUNCATE
                if re.search(rf"\bTRUNCATE\s+TABLE\s+{table}\b", statement_upper):
                    return False, f"Cannot truncate protected table: {table}"

        return True, None

    def execute_statement(
        self, cursor: sqlite3.Cursor, statement: str
    ) -> tuple[int, List[Any]]:
        """
        Execute a single SQL statement.

        Args:
            cursor: SQLite cursor
            statement: SQL statement

        Returns:
            Tuple of (rows_affected, results)
        """
        cursor.execute(statement)

        # Check if statement returns results
        if statement.strip().upper().startswith("SELECT"):
            results = cursor.fetchall()
            return 0, results
        else:
            return cursor.rowcount, []

    def execute_script(
        self, db_path: Path, sql: str, use_transaction: bool = True
    ) -> SQLExecutionResult:
        """
        Execute SQL script.

        Args:
            db_path: Path to SQLite database
            sql: SQL script text
            use_transaction: Whether to wrap in transaction

        Returns:
            Execution result
        """
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        statements_executed = 0
        total_rows_affected = 0
        all_results = []
        error = None

        try:
            if use_transaction:
                cursor.execute("BEGIN TRANSACTION")

            # Split and execute statements
            statements = self.split_statements(sql)

            for statement in statements:
                # Validate statement
                is_valid, error_msg = self.validate_statement(statement)
                if not is_valid:
                    error = error_msg
                    if use_transaction:
                        conn.rollback()
                    break

                # Execute statement
                rows_affected, results = self.execute_statement(cursor, statement)
                statements_executed += 1
                total_rows_affected += rows_affected

                if results:
                    all_results.extend(results)

            if use_transaction and error is None:
                conn.commit()

        except Exception as e:
            error = str(e)
            if use_transaction:
                conn.rollback()

        finally:
            conn.close()

        return SQLExecutionResult(
            statements_executed=statements_executed,
            rows_affected=total_rows_affected,
            error=error,
            results=all_results,
        )

    def execute_file(
        self, db_path: Path, sql_file: Path, use_transaction: bool = True
    ) -> SQLExecutionResult:
        """
        Execute SQL script from file.

        Args:
            db_path: Path to SQLite database
            sql_file: Path to SQL script file
            use_transaction: Whether to wrap in transaction

        Returns:
            Execution result
        """
        with open(sql_file, "r", encoding="utf-8") as f:
            sql = f.read()

        return self.execute_script(db_path, sql, use_transaction)

    def execute_query(self, db_path: Path, query: str) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results as dictionaries.

        Args:
            db_path: Path to SQLite database
            query: SELECT query

        Returns:
            List of result dictionaries
        """
        # Ensure read-only
        if not query.strip().upper().startswith("SELECT"):
            raise ValueError("Only SELECT queries allowed in execute_query")

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            # Convert Row objects to dicts
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def create_temp_table(
        self, db_path: Path, table_name: str, columns: Dict[str, str], data: List[tuple]
    ) -> None:
        """
        Create temporary table for data transformation.

        Args:
            db_path: Path to SQLite database
            table_name: Name for temp table
            columns: Column definitions {name: type}
            data: Data rows as tuples
        """
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            # Create temp table
            column_defs = [f"{name} {dtype}" for name, dtype in columns.items()]
            create_sql = f"CREATE TEMP TABLE {table_name} ({', '.join(column_defs)})"
            cursor.execute(create_sql)

            # Insert data
            placeholders = ",".join(["?"] * len(columns))
            insert_sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
            cursor.executemany(insert_sql, data)

            conn.commit()
        finally:
            conn.close()
