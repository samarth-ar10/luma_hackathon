#!/usr/bin/env python3
import os
import sys

sys.path.append("/home/samarth/Projects/luma_hackathon")
from dotenv import load_dotenv

from portia import (
    Config,
    LLMModel,
    LLMProvider,
    Portia,
)

# First, execute our SQL server demo to ensure the database exists
from portia_demo.sql_server_demo import create_table, insert_sample_data

# Load environment variables
load_dotenv()


# Create a direct query to the LLM
def query_llm(api_key, prompt):
    import openai

    client = openai.OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful SQL expert."},
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content


def main():
    # Create the database and sample data
    create_table()
    insert_sample_data()

    # Get OpenAI API key
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not openai_api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        return

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

    # Run the query directly to the LLM
    print("Querying GPT-4o for SQL advice...\n")
    print(prompt)
    print("\n" + "-" * 50 + "\n")

    result = query_llm(openai_api_key, prompt)

    # Display the result
    print("\n=== GPT-4o Result ===")
    print(result)


if __name__ == "__main__":
    main()
