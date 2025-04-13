#!/usr/bin/env python3
"""
Portia Direct - Provides direct integration with OpenAI for SQL analysis.
Bypasses the normal MCP server route for simplicity.
"""
import os
import openai

# Import from the same package
from .sql_server_demo import create_table, insert_sample_data


def query_llm(api_key, prompt, model="gpt-4o"):
    """Query the LLM with a prompt.

    Args:
        api_key (str): OpenAI API key
        prompt (str): Prompt to send to the LLM
        model (str, optional): Model to use. Defaults to "gpt-4o".

    Returns:
        str: Response from the LLM
    """
    client = openai.OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful SQL expert who can analyze databases and provide insights.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=2000,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error querying OpenAI: {str(e)}"


def main():
    """Run a test of the GPT-4o integration."""
    print("Portia Direct - GPT-4o Integration Test")
    print("=" * 40)

    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        return

    # Create a test database
    create_table()
    insert_sample_data()

    # Create a sample prompt
    prompt = """
    Analyze a customer database with these fields:
    - id: Primary key
    - name: Customer name
    - email: Customer email
    - signup_date: Date when the customer signed up

    What kind of SQL queries would be useful for business analytics?
    Give me 3 example queries.
    """

    print("\nSending prompt to GPT-4o...")
    response = query_llm(api_key, prompt)

    print("\nGPT-4o Response:")
    print("-" * 40)
    print(response)
    print("-" * 40)


if __name__ == "__main__":
    main()
