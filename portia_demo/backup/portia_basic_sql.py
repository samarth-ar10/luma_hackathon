#!/usr/bin/env python3
import os
import sys
import sqlite3

sys.path.append("/home/samarth/Projects/luma_hackathon")
from dotenv import load_dotenv

from portia import (
    Config,
    LLMModel,
    LLMProvider,
    Portia,
    example_tool_registry,
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

    # Initialize Portia with example tools
    portia = Portia(config=config, tools=example_tool_registry)

    # Example: Run Portia with a query about our customer database
    prompt = """
    I have a customer database in SQLite with a table called 'customers'.
    The table has columns for id, name, email, and signup_date.
    
    Here's a sample of the data in the database:
    - Customer ID: 1, Name: John Doe, Email: john@example.com, Signup Date: 2024-04-01
    - Customer ID: 2, Name: Jane Smith, Email: jane@example.com, Signup Date: 2024-04-02
    
    Please help me understand:
    1. What types of queries would be useful for analyzing this customer database?
    2. How could I find customers who signed up in April 2024?
    3. If I wanted to add more data like purchase history, how might I structure that data?
    """

    # Run the agent with our prompt
    print("Running Portia with GPT-4o...\n")
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
