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
    CustomTool,
)

# First, execute our SQL server demo to ensure the database exists
from portia_demo.sql_server_demo import create_table, insert_sample_data

# Load environment variables
load_dotenv()


# Create a SQLite database helper class
class SQLiteDatabase:
    def __init__(self, db_path):
        self.db_path = db_path

    def execute_query(self, query):
        """Execute a SQL query and return the results."""
        conn = sqlite3.connect(self.db_path)
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

    def get_all_customers(self):
        """Get all customers from the database."""
        return self.execute_query("SELECT * FROM customers")


def main():
    # Create the database and sample data
    create_table()
    insert_sample_data()

    # Initialize our database helper
    db = SQLiteDatabase("sql_data.db")

    # Configure Portia with OpenAI GPT-4o
    config = Config.from_default(
        llm_provider=LLMProvider.OPENAI,
        llm_model_name=LLMModel.GPT_4_O,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )

    # Create custom tools for working with SQL
    # SQL Query Tool
    class SqlQueryTool(CustomTool):
        name = "sql_query"
        description = "Execute a SQL query on the customers database"

        def run(self, query: str) -> Dict[str, Any]:
            """Run a SQL query against the database."""
            return db.execute_query(query)

    # Get All Customers Tool
    class GetAllCustomersTool(CustomTool):
        name = "get_all_customers"
        description = "Get all customers from the database"

        def run(self) -> Dict[str, Any]:
            """Get all customers from the database."""
            return db.get_all_customers()

    # Initialize Portia with our custom tools
    portia = Portia(config=config, tools=[SqlQueryTool(), GetAllCustomersTool()])

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
