#!/usr/bin/env python3
import os
import sys
import sqlite3
from typing import Dict, Any

sys.path.append("/home/samarth/Projects/luma_hackathon")
from dotenv import load_dotenv

from portia import (
    Config,
    LLMModel,
    LLMProvider,
    Portia,
    Tool,
    ToolRegistry,
    ToolRunContext,
)

# First, execute our SQL server demo to ensure the database exists
from portia_demo.sql_server_demo import create_table, insert_sample_data

# Load environment variables
load_dotenv()


def main():
    # Create the database and sample data
    create_table()
    insert_sample_data()

    # Configure Portia with OpenAI GPT-4o
    config = Config.from_default(
        llm_provider=LLMProvider.OPENAI,
        llm_model_name=LLMModel.GPT_4_O,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )

    # ----------------
    # SQL Database Tools
    # ----------------

    def execute_sql_query(query):
        """Execute a SQL query and return the results."""
        conn = sqlite3.connect("sql_data.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute(query)
            conn.commit()

            # If this is a SELECT query, fetch results
            if query.strip().upper().startswith("SELECT"):
                columns = [col[0] for col in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return {"success": True, "results": results}
            else:
                return {"success": True, "message": "Query executed successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    def get_all_customers():
        """Get all customers from the database."""
        return execute_sql_query("SELECT * FROM customers")

    # Create our SQL tools registry
    class SqlToolRegistry(ToolRegistry):
        def __init__(self):
            self.tools = {
                "sql_query": Tool(
                    id="sql_query",
                    name="SQL Query",
                    description="Execute a SQL query on the database",
                    function=lambda params: execute_sql_query(params["query"]),
                ),
                "get_all_customers": Tool(
                    id="get_all_customers",
                    name="Get All Customers",
                    description="Get all customers from the database",
                    function=lambda params: get_all_customers(),
                ),
            }

        def get_tool(self, tool_id: str) -> Tool:
            if tool_id not in self.tools:
                raise Exception(f"Tool {tool_id} not found")
            return self.tools[tool_id]

        def get_tools(self):
            return list(self.tools.values())

        def register_tool(self, tool: Tool) -> None:
            self.tools[tool.id] = tool

    # Create tool registry with our SQL tools
    tool_registry = SqlToolRegistry()

    # Initialize Portia with our tools and GPT-4o
    portia = Portia(config=config, tools=tool_registry)

    # Example: Run Portia with a query about our customer database
    prompt = """
    I have a customer database with a table called 'customers'. 
    The table has columns for id, name, email, and signup_date.
    Please help me:
    1. Get all customers from the database
    2. Write a SQL query to find customers who signed up in April 2024
    3. Explain what other queries might be useful for this customer database
    """

    # Run the agent with our prompt
    print("Running Portia with GPT-4o and SQL tools...\n")
    result = portia.run(prompt)

    # Display the result
    print("\n=== Portia Result ===")
    print(result.explanation)

    # Display actions taken
    print("\n=== Actions Taken ===")
    for action in result.actions:
        print(f"- {action.name}: {action.details}")


if __name__ == "__main__":
    main()
