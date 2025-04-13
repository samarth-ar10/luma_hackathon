#!/usr/bin/env python3
"""
SQL + GPT-4o Demo - Shows how to use OpenAI's GPT-4o to analyze SQL data
"""
import os
from dotenv import load_dotenv

# Import SQL demo components
from sql_demo import (
    create_table,
    insert_sample_data,
    execute_sql_query,
    display_customers,
)

# Import the direct LLM query function
from sql_demo.portia_direct import query_llm

# Load environment variables
load_dotenv()


def main():
    """Run the SQL + GPT-4o demo"""
    print("=" * 50)
    print("SQL + GPT-4o Demo")
    print("=" * 50)

    # Step 1: Set up the database
    print("\n>> Step 1: Setting up the database")
    create_table()
    insert_sample_data()

    # Step 2: Run a SQL query to get the data
    print("\n>> Step 2: Querying the database")
    query = "SELECT * FROM customers"
    result = execute_sql_query(query)

    if result["success"] and "results" in result:
        customers = result["results"]
        print(f"Found {len(customers)} customers:")
        display_customers(customers)
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
        return

    # Step 3: Use GPT-4o directly for analysis
    print("\n>> Step 3: Using GPT-4o for analysis")

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        return

    # Create a prompt for analysis
    prompt = """
    I have a customers table with the following data:
    
    - John Doe (john@example.com), signed up on 2024-04-01
    - Jane Smith (jane@example.com), signed up on 2024-04-02
    - Alice Johnson (alice@example.com), signed up on 2024-03-15
    - Bob Brown (bob@example.com), signed up on 2024-04-10
    
    Please analyze this data and provide:
    1. Which month has the most signups?
    2. What SQL query would you use to find customers who signed up in April 2024?
    3. Suggest an additional field that would be useful to add to this table.
    """

    print("Sending prompt to GPT-4o...")
    response = query_llm(openai_api_key, prompt)

    print("\nGPT-4o Analysis:")
    print("-" * 50)
    print(response)
    print("-" * 50)

    # Step 4: Run another GPT-4o analysis with actual SQL query results
    print("\n>> Step 4: Advanced SQL analysis with GPT-4o")

    # Execute the query to find April signups
    april_query = "SELECT * FROM customers WHERE signup_date LIKE '2024-04-%'"
    result = execute_sql_query(april_query)

    if result["success"] and "results" in result:
        april_customers = result["results"]
        print(f"Found {len(april_customers)} customers who signed up in April:")
        display_customers(april_customers)

        # Create a new prompt with the actual query results
        advanced_prompt = f"""
        I executed this SQL query: "{april_query}" 
        
        And got these results:
        {april_customers}
        
        Can you provide:
        1. A summary of these findings
        2. What percentage of our total customer base signed up in April?
        3. Suggest a follow-up query I could run to get more insights
        """

        print("\nSending advanced prompt to GPT-4o...")
        advanced_response = query_llm(openai_api_key, advanced_prompt)

        print("\nAdvanced GPT-4o Analysis:")
        print("-" * 50)
        print(advanced_response)
        print("-" * 50)

    print("\nDemo complete!")


if __name__ == "__main__":
    main()
