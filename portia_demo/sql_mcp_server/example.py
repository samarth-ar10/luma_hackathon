#!/usr/bin/env python3
import asyncio
import os
from typing import Dict, Any, List

from modelcontextprotocol import SSEClientConfig, ClientSession


async def main():
    """Example of how to use the SQL MCP server directly without Portia."""
    print("SQL MCP Server Direct Example")
    print("----------------------------")

    # Configure connection to a running MCP server
    # Assumes you've started the server separately with: python sql_mcp_server.py
    config = SSEClientConfig(url="http://localhost:8000")

    async with ClientSession(config) as session:
        # List available tools
        tools = await session.list_tools()
        print(f"Available tools: {', '.join([tool.name for tool in tools])}")

        # Create a table
        print("\n1. Creating a table 'products'...")
        create_result = await session.call_tool(
            "sql_create_table",
            {
                "table_name": "products",
                "columns": {
                    "id": "INTEGER PRIMARY KEY",
                    "name": "TEXT",
                    "price": "REAL",
                    "category": "TEXT",
                },
            },
        )
        print(f"Result: {create_result['message']}")

        # Insert data
        print("\n2. Inserting product data...")
        products = [
            {"id": 1, "name": "Laptop", "price": 1299.99, "category": "Electronics"},
            {"id": 2, "name": "Headphones", "price": 149.99, "category": "Electronics"},
            {"id": 3, "name": "Coffee Mug", "price": 12.99, "category": "Kitchen"},
        ]
        insert_result = await session.call_tool(
            "sql_insert_data", {"table_name": "products", "data": products}
        )
        print(
            f"Result: {insert_result['message']} ({insert_result['rows_affected']} rows)"
        )

        # Query data
        print("\n3. Querying all products...")
        query_result = await session.call_tool(
            "sql_query_data", {"query": "SELECT * FROM products"}
        )
        print(f"Result: {query_result['message']}")

        # Display products
        print("\nProducts:")
        for product in query_result["data"]:
            print(
                f"  ID: {product['id']}, Name: {product['name']}, "
                f"Price: ${product['price']}, Category: {product['category']}"
            )

        # Query with filtering
        print("\n4. Querying electronics products...")
        electronics_result = await session.call_tool(
            "sql_query_data",
            {
                "query": "SELECT * FROM products WHERE category = ?",
                "params": ["Electronics"],
            },
        )

        # Display electronics
        print("\nElectronics Products:")
        for product in electronics_result["data"]:
            print(
                f"  ID: {product['id']}, Name: {product['name']}, "
                f"Price: ${product['price']}"
            )

        # Update a product
        print("\n5. Updating a product price...")
        update_result = await session.call_tool(
            "sql_update_data",
            {
                "table_name": "products",
                "set_values": {"price": 1199.99},
                "where_clause": "id = ?",
                "where_params": [1],
            },
        )
        print(
            f"Result: {update_result['message']} ({update_result['rows_affected']} rows)"
        )

        # Query updated product
        updated_product = await session.call_tool(
            "sql_query_data", {"query": "SELECT * FROM products WHERE id = 1"}
        )
        print(f"\nUpdated product: {updated_product['data'][0]}")

        # Get table schema
        print("\n6. Getting table schema...")
        schema_result = await session.call_tool(
            "sql_get_table_schema", {"table_name": "products"}
        )
        print("\nProducts Schema:")
        for column, type_ in schema_result["schema"].items():
            print(f"  {column}: {type_}")


if __name__ == "__main__":
    asyncio.run(main())
