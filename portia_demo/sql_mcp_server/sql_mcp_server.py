#!/usr/bin/env python3
import os
import json
import logging
from typing import List, Dict, Any, Optional, Union
import sqlite3
from contextlib import contextmanager

from modelcontextprotocol import (
    MCPServer,
    Tool,
    InputParameter,
    OutputParameter,
    register_tool,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLite database setup
DB_PATH = os.environ.get("SQL_MCP_DB_PATH", "sql_mcp_data.db")


@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# Create MCP server
server = MCPServer()


@register_tool(server)
class CreateTableTool(Tool):
    """Create a new table in the database."""

    name = "sql_create_table"
    description = "Creates a new table in the SQL database with specified columns"

    class Input:
        table_name: str = InputParameter(description="Name of the table to create")
        columns: Dict[str, str] = InputParameter(
            description="Column definitions as name:type pairs (e.g., {'id': 'INTEGER PRIMARY KEY', 'name': 'TEXT'})"
        )

    class Output:
        success: bool = OutputParameter(
            description="Whether the table was created successfully"
        )
        message: str = OutputParameter(
            description="Result message or error information"
        )

    def run(self, input: Input) -> Output:
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()

                # Build the CREATE TABLE statement
                columns_sql = ", ".join(
                    [f"{name} {type_}" for name, type_ in input.columns.items()]
                )
                create_sql = (
                    f"CREATE TABLE IF NOT EXISTS {input.table_name} ({columns_sql})"
                )

                cursor.execute(create_sql)
                conn.commit()

                return self.Output(
                    success=True,
                    message=f"Table '{input.table_name}' created successfully.",
                )
        except Exception as e:
            logger.error(f"Error creating table: {str(e)}")
            return self.Output(
                success=False, message=f"Failed to create table: {str(e)}"
            )


@register_tool(server)
class InsertDataTool(Tool):
    """Insert data into a table."""

    name = "sql_insert_data"
    description = "Inserts one or more rows of data into the specified table"

    class Input:
        table_name: str = InputParameter(
            description="Name of the table to insert data into"
        )
        data: Union[Dict[str, Any], List[Dict[str, Any]]] = InputParameter(
            description="Data to insert, either a single row as dict or multiple rows as list of dicts"
        )

    class Output:
        success: bool = OutputParameter(
            description="Whether the data was inserted successfully"
        )
        message: str = OutputParameter(
            description="Result message or error information"
        )
        rows_affected: int = OutputParameter(description="Number of rows inserted")

    def run(self, input: Input) -> Output:
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()

                # Handle both single row and multiple rows
                data_rows = input.data if isinstance(input.data, list) else [input.data]

                if not data_rows:
                    return self.Output(
                        success=False,
                        message="No data provided for insertion",
                        rows_affected=0,
                    )

                # Get column names from the first row
                columns = list(data_rows[0].keys())
                placeholders = ", ".join(["?"] * len(columns))

                insert_sql = f"INSERT INTO {input.table_name} ({', '.join(columns)}) VALUES ({placeholders})"

                rows_affected = 0
                for row in data_rows:
                    values = [row.get(col) for col in columns]
                    cursor.execute(insert_sql, values)
                    rows_affected += 1

                conn.commit()

                return self.Output(
                    success=True,
                    message=f"Successfully inserted data into '{input.table_name}'",
                    rows_affected=rows_affected,
                )
        except Exception as e:
            logger.error(f"Error inserting data: {str(e)}")
            return self.Output(
                success=False,
                message=f"Failed to insert data: {str(e)}",
                rows_affected=0,
            )


@register_tool(server)
class QueryDataTool(Tool):
    """Query data from a table."""

    name = "sql_query_data"
    description = "Queries data from the database using SQL SELECT statements"

    class Input:
        query: str = InputParameter(
            description="SQL query to execute (SELECT statements only)"
        )
        params: Optional[List[Any]] = InputParameter(
            description="Query parameters (for parameterized queries)", default=None
        )

    class Output:
        success: bool = OutputParameter(
            description="Whether the query was executed successfully"
        )
        data: List[Dict[str, Any]] = OutputParameter(
            description="Query results as a list of dictionaries"
        )
        message: str = OutputParameter(
            description="Result message or error information"
        )

    def run(self, input: Input) -> Output:
        try:
            # Basic security check to prevent non-SELECT queries
            if not input.query.strip().upper().startswith("SELECT"):
                return self.Output(
                    success=False,
                    data=[],
                    message="Only SELECT queries are allowed through this tool.",
                )

            with get_db_connection() as conn:
                cursor = conn.cursor()

                if input.params:
                    cursor.execute(input.query, input.params)
                else:
                    cursor.execute(input.query)

                # Convert results to list of dicts
                columns = [col[0] for col in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append({col: row[idx] for idx, col in enumerate(columns)})

                return self.Output(
                    success=True,
                    data=results,
                    message=f"Query executed successfully, returned {len(results)} rows",
                )
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            return self.Output(
                success=False, data=[], message=f"Failed to execute query: {str(e)}"
            )


@register_tool(server)
class UpdateDataTool(Tool):
    """Update data in a table."""

    name = "sql_update_data"
    description = "Updates data in the specified table based on a condition"

    class Input:
        table_name: str = InputParameter(description="Name of the table to update")
        set_values: Dict[str, Any] = InputParameter(
            description="Column-value pairs to set"
        )
        where_clause: str = InputParameter(
            description="WHERE clause to identify rows to update"
        )
        where_params: Optional[List[Any]] = InputParameter(
            description="Parameters for the WHERE clause", default=None
        )

    class Output:
        success: bool = OutputParameter(description="Whether the update was successful")
        message: str = OutputParameter(
            description="Result message or error information"
        )
        rows_affected: int = OutputParameter(description="Number of rows updated")

    def run(self, input: Input) -> Output:
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()

                # Build the SET clause
                set_clause = ", ".join(
                    [f"{col} = ?" for col in input.set_values.keys()]
                )
                set_values = list(input.set_values.values())

                update_sql = f"UPDATE {input.table_name} SET {set_clause} WHERE {input.where_clause}"

                params = set_values
                if input.where_params:
                    params.extend(input.where_params)

                cursor.execute(update_sql, params)
                conn.commit()

                return self.Output(
                    success=True,
                    message=f"Successfully updated data in '{input.table_name}'",
                    rows_affected=cursor.rowcount,
                )
        except Exception as e:
            logger.error(f"Error updating data: {str(e)}")
            return self.Output(
                success=False,
                message=f"Failed to update data: {str(e)}",
                rows_affected=0,
            )


@register_tool(server)
class DeleteDataTool(Tool):
    """Delete data from a table."""

    name = "sql_delete_data"
    description = "Deletes data from the specified table based on a condition"

    class Input:
        table_name: str = InputParameter(description="Name of the table to delete from")
        where_clause: str = InputParameter(
            description="WHERE clause to identify rows to delete"
        )
        where_params: Optional[List[Any]] = InputParameter(
            description="Parameters for the WHERE clause", default=None
        )

    class Output:
        success: bool = OutputParameter(
            description="Whether the deletion was successful"
        )
        message: str = OutputParameter(
            description="Result message or error information"
        )
        rows_affected: int = OutputParameter(description="Number of rows deleted")

    def run(self, input: Input) -> Output:
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()

                delete_sql = (
                    f"DELETE FROM {input.table_name} WHERE {input.where_clause}"
                )

                if input.where_params:
                    cursor.execute(delete_sql, input.where_params)
                else:
                    cursor.execute(delete_sql)

                conn.commit()

                return self.Output(
                    success=True,
                    message=f"Successfully deleted data from '{input.table_name}'",
                    rows_affected=cursor.rowcount,
                )
        except Exception as e:
            logger.error(f"Error deleting data: {str(e)}")
            return self.Output(
                success=False,
                message=f"Failed to delete data: {str(e)}",
                rows_affected=0,
            )


@register_tool(server)
class ListTablesTool(Tool):
    """List all tables in the database."""

    name = "sql_list_tables"
    description = "Lists all tables in the database"

    class Input:
        pass

    class Output:
        success: bool = OutputParameter(
            description="Whether the operation was successful"
        )
        tables: List[str] = OutputParameter(description="List of table names")
        message: str = OutputParameter(
            description="Result message or error information"
        )

    def run(self, input: Input) -> Output:
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]

                return self.Output(
                    success=True, tables=tables, message=f"Found {len(tables)} tables"
                )
        except Exception as e:
            logger.error(f"Error listing tables: {str(e)}")
            return self.Output(
                success=False, tables=[], message=f"Failed to list tables: {str(e)}"
            )


@register_tool(server)
class GetTableSchemaTool(Tool):
    """Get the schema of a table."""

    name = "sql_get_table_schema"
    description = "Gets the schema (column names and types) of a table"

    class Input:
        table_name: str = InputParameter(
            description="Name of the table to get schema for"
        )

    class Output:
        success: bool = OutputParameter(
            description="Whether the operation was successful"
        )
        schema: Dict[str, str] = OutputParameter(
            description="Column names and their types"
        )
        message: str = OutputParameter(
            description="Result message or error information"
        )

    def run(self, input: Input) -> Output:
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(f"PRAGMA table_info({input.table_name})")
                columns = cursor.fetchall()

                schema = {}
                for col in columns:
                    name = col[1]
                    type_ = col[2]
                    schema[name] = type_

                return self.Output(
                    success=True,
                    schema=schema,
                    message=f"Successfully retrieved schema for '{input.table_name}'",
                )
        except Exception as e:
            logger.error(f"Error getting table schema: {str(e)}")
            return self.Output(
                success=False,
                schema={},
                message=f"Failed to get table schema: {str(e)}",
            )


if __name__ == "__main__":
    # Start the MCP server
    server.start()
