#!/usr/bin/env python3
import os
from dotenv import load_dotenv

from portia import (
    Config,
    Portia,
    DefaultToolRegistry,
    McpToolRegistry,
)

# Load environment variables
load_dotenv()


def main():
    # Configure Portia
    config = Config.from_default()

    # Set up the SQL MCP tool registry
    # The server is started as a subprocess using stdio connection
    sql_tool_registry = McpToolRegistry.from_stdio_connection(
        server_name="sql_db",
        command="python",
        args=["portia_demo/sql_mcp_server/sql_mcp_server.py"],
        # You can set environment variables for the subprocess if needed
        env={
            "SQL_MCP_DB_PATH": "sql_data.db",  # Path where SQLite database will be stored
            "PATH": os.environ.get("PATH", ""),
        },
    )

    # Combine the SQL tools with default Portia tools
    tool_registry = sql_tool_registry + DefaultToolRegistry(config)

    # Initialize Portia with our tools
    portia = Portia(config=config, tools=tool_registry)

    # Example: Run Portia with a query that involves SQL operations
    prompt = """
    Please help me manage a customer database:
    1. Create a 'customers' table with columns: id (integer primary key), name (text), email (text), signup_date (text)
    2. Insert two sample customers
    3. Query all customers and show the results
    """

    # Run the agent with our prompt
    result = portia.run(prompt)

    # Display the result
    print("\n=== Portia SQL Agent Result ===")
    print(result.explanation)

    # You can also access the detailed log of actions taken
    print("\n=== Actions Taken ===")
    for action in result.actions:
        print(f"- {action.name}: {action.details}")


if __name__ == "__main__":
    main()
