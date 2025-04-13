#!/usr/bin/env python3
"""
SQL Demo Example - Shows how to use the SQL demo components.
"""
import os
from dotenv import load_dotenv

# Import the SQL demo components
from sql_demo import (
    create_table,
    insert_sample_data,
    query_customers,
    display_customers,
    execute_sql_query,
    query_llm,
)

# Load environment variables
load_dotenv()


def main():
    """Run a demonstration of SQL capabilities."""
    print("=" * 50)
    print("SQL Demo Example")
    print("=" * 50)

    # STEP 1: Create the database and add sample data
    print("\n>> Step 1: Setting up the database")
    create_table()
    insert_sample_data()

    # STEP 2: Execute a custom query
    print("\n>> Step 2: Running a custom SQL query")
    april_customers = query_customers(
        "SELECT * FROM customers WHERE signup_date LIKE '2024-04-%'"
    )
    print(f"Found {len(april_customers)} customers who signed up in April:")
    display_customers(april_customers)

    # STEP 3: Use GPT-4o to analyze the database
    print("\n>> Step 3: Using GPT-4o to analyze the database")

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Skipping GPT-4o analysis.")
        return

    # Create a targeted prompt
    prompt = """
    Analyze the following customer database:
    
    CREATE TABLE customers (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT,
        signup_date TEXT
    )
    
    Only 4 customers are in the database:
    - Customer 1: John Doe, signed up on 2024-04-01
    - Customer 2: Jane Smith, signed up on 2024-04-02
    - Customer 3: Alice Johnson, signed up on 2024-03-15
    - Customer 4: Bob Brown, signed up on 2024-04-10
    
    Please provide:
    1. A SQL query to count customers by signup month
    2. How to modify this schema for better performance
    3. One business insight from this data
    """

    print("\nSending prompt to GPT-4o...")
    response = query_llm(openai_api_key, prompt)

    print("\nGPT-4o Response:")
    print("-" * 50)
    print(response)
    print("-" * 50)

    print("\nDemo complete!")


if __name__ == "__main__":
    main()
