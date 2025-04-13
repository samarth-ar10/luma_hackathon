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
    portia = Portia(config=config)

    # Example: Ask for SQL advice directly
    prompt = """
    I need to understand how to work with a SQL database. I have a customer table with the following structure:
    
    CREATE TABLE customers (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT,
        signup_date TEXT
    )
    
    I have the following data:
    - John Doe (john@example.com) signed up on 2024-04-01
    - Jane Smith (jane@example.com) signed up on 2024-04-02
    
    Please help me:
    1. Write a SQL query to find all customers who signed up in April 2024
    2. Suggest other useful queries for this database
    3. Recommend how to enhance this schema if I want to track purchase history
    """

    # Run the agent with our prompt
    print("Asking Portia for SQL advice with GPT-4o...\n")
    print(prompt)
    print("\n" + "-" * 50 + "\n")

    # Use the Ask method which is simpler than Plan
    result = portia.ask(prompt)

    # Display the result
    print("\n=== Portia Result ===")
    print(result)


if __name__ == "__main__":
    main()
