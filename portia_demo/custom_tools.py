"""
Custom tools for Portia to interact with the SQL database.
"""

import os
import sqlite3
from contextlib import contextmanager
from typing import Optional, Dict, Any

from portia import Tool


class SQLQueryTool(Tool):
    """Tool for executing SQL SELECT queries on the company database."""

    name: str = "sql_query"
    description: str = (
        "Execute a SQL SELECT query on the company database to retrieve data"
    )
    id: str = "sql_query_tool"
    output_schema: tuple[str, str] = (
        "dict",
        "Dictionary containing query results, count, query string, and "
        "potential error messages",
    )
    db_path: str = os.environ.get("SQL_MCP_DB_PATH", "sql_data.db")

    def __init__(self):
        super().__init__()

    @contextmanager
    def get_db_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def run(self, query: str) -> Dict[str, Any]:
        """
        Execute a SQL query on the database.

        Args:
            query: The SQL query to execute (must be a SELECT query)

        Returns:
            Dict: Contains the query results or error information
        """
        # Validate query is a SELECT query for security
        if not query.strip().upper().startswith("SELECT"):
            return {"error": "Only SELECT queries are allowed for security reasons"}

        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)

                # Convert results to a list of dictionaries
                columns = [col[0] for col in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))

                return {"results": results, "count": len(results), "query": query}
        except Exception as e:
            return {"error": str(e), "query": query}


class GetTableInfoTool(Tool):
    """Tool for getting information about available tables in the database."""

    name: str = "get_table_info"
    description: str = (
        "Get information about a specific table or all tables in the database"
    )
    id: str = "get_table_info_tool"
    output_schema: tuple[str, str] = (
        "dict",
        "Dictionary containing table information, column details, sample data, "
        "or list of all tables",
    )
    db_path: str = os.environ.get("SQL_MCP_DB_PATH", "sql_data.db")

    def __init__(self):
        super().__init__()

    @contextmanager
    def get_db_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def run(self, table_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get table information from the database.

        Args:
            table_name: Optional table name. If provided, returns info about that table.
                        If None, returns a list of all tables.

        Returns:
            Dict: Contains table information or list of tables
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()

                if table_name:
                    # Get information about a specific table
                    try:
                        # Get column information
                        cursor.execute(f"PRAGMA table_info({table_name})")
                        columns = []
                        for row in cursor.fetchall():
                            columns.append(
                                {
                                    "name": row["name"],
                                    "type": row["type"],
                                    "notnull": bool(row["notnull"]),
                                    "primary_key": bool(row["pk"]),
                                }
                            )

                        # Get sample data (first 5 rows)
                        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                        sample_data = []
                        col_names = [col[0] for col in cursor.description]
                        for row in cursor.fetchall():
                            sample_data.append(dict(zip(col_names, row)))

                        return {
                            "table_name": table_name,
                            "columns": columns,
                            "sample_data": sample_data,
                        }
                    except Exception as e:
                        return {
                            "error": (
                                f"Error getting information for table "
                                f"'{table_name}': {str(e)}"
                            )
                        }
                else:
                    # Get list of all tables
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = [row["name"] for row in cursor.fetchall()]

                    return {"tables": tables}
        except Exception as e:
            return {"error": f"Database error: {str(e)}"}


# Create the custom tool registry
custom_tools = [SQLQueryTool(), GetTableInfoTool()]
