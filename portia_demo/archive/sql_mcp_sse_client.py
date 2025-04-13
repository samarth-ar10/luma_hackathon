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

    # Set up the SQL MCP tool registry using SSE connection
    # Note: You must start the SSE server first with:
    # python sql_mcp_server/run_sse_server.py
    sql_tool_registry = McpToolRegistry.from_sse_connection(
        server_name="sql_db_sse",
        url="http://localhost:8000",
    )

    # Combine the SQL tools with default Portia tools
    tool_registry = sql_tool_registry + DefaultToolRegistry(config)

    # Initialize Portia with our tools
    portia = Portia(config=config, tools=tool_registry)

    # Example: Run Portia with a query that involves SQL operations
    prompt = """
    I need to create a simple product inventory system:
    1. Create a products table with columns for id, name, price, quantity, and description
    2. Add three products of your choice
    3. Show me all products where quantity is less than 10
    """

    # Run the agent with our prompt
    result = portia.run(prompt)

    # Display the result
    print("\n=== Portia SQL Agent Result (SSE) ===")
    print(result.explanation)

    # You can also access the detailed log of actions taken
    print("\n=== Actions Taken ===")
    for action in result.actions:
        print(f"- {action.name}: {action.details}")


if __name__ == "__main__":
    main()
