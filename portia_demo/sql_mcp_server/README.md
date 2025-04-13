# SQL MCP Server for Portia

This is a Model Context Protocol (MCP) server that provides SQL database operations for Portia AI agents. It allows AI agents to create tables, insert data, query data, update data, delete data, and inspect database schema.

## Features

- Create tables with custom schemas
- Insert data (single row or batch)
- Query data with SQL SELECT statements
- Update existing data
- Delete data based on conditions
- List all tables in the database
- Get table schema information

## Installation

1. Make sure you have Python 3.11+ installed
2. Install dependencies using Poetry:

```bash
cd sql_mcp_server
poetry install
```

Or with pip:

```bash
pip install modelcontextprotocol sqlalchemy pydantic python-dotenv
```

## Running the server directly

You can run the server directly:

```bash
python sql_mcp_server.py
```

The server uses SQLite by default and will create a database file called `sql_mcp_data.db` in the current directory. You can change the database path by setting the `SQL_MCP_DB_PATH` environment variable.

## Using with Portia

To use this SQL MCP server with Portia, you can connect it using either the stdio or SSE method. See the example client script `portia_demo/sql_mcp_client.py` for a full example.

Basic usage:

```python
from portia import Config, Portia, DefaultToolRegistry, McpToolRegistry

# Connect to the SQL MCP server using stdio
sql_tools = McpToolRegistry.from_stdio_connection(
    server_name="sql_db",
    command="python",
    args=["sql_mcp_server/sql_mcp_server.py"],
    env={"SQL_MCP_DB_PATH": "my_database.db"},
)

# Initialize Portia with SQL tools
config = Config.from_default()
tool_registry = sql_tools + DefaultToolRegistry(config)
portia = Portia(config=config, tools=tool_registry)

# Run Portia with SQL capabilities
result = portia.run("Create a table called 'users' with columns for id, name, and email")
```

## Available SQL Tools

The server provides the following tools:

1. `sql_create_table` - Create a new table with custom columns
2. `sql_insert_data` - Insert data into a table
3. `sql_query_data` - Query data using SELECT statements
4. `sql_update_data` - Update data in a table
5. `sql_delete_data` - Delete data from a table
6. `sql_list_tables` - List all tables in the database
7. `sql_get_table_schema` - Get the schema of a table

## Security Considerations

- The SQL MCP server restricts `sql_query_data` to only allow SELECT statements for security.
- For production use, consider additional security measures like input validation and query analysis.
- This implementation uses SQLite for simplicity. For production, consider using a more robust database system.

## License

MIT 