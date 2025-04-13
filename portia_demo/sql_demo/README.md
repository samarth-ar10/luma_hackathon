# SQL Demo Components

This directory contains SQL-related demos and tools for Portia integration.

## Components

### 1. Basic SQL Demo

- **File:** `sql_server_demo.py`
- **Description:** A simple SQLite demonstration that creates a customer database, inserts sample data, and queries it.
- **Usage:** Import directly or run `python sql_server_demo.py`

### 2. Direct SQL Query with LLM

- **File:** `portia_direct.py`
- **Description:** Uses OpenAI's GPT-4o to analyze and suggest SQL queries for a customer database.
- **Usage:** Run `python portia_direct.py`

### 3. MCP Server Implementation (WIP)

- **Directory:** `../sql_mcp_server/`
- **Description:** Model Context Protocol (MCP) server implementation for SQL operations. Currently a work in progress due to dependency issues.
- **Usage:** Not fully functional yet

## Usage Examples

### Basic Database Operations

```python
from sql_demo.sql_server_demo import create_table, insert_sample_data, query_customers

# Create the table schema
create_table()

# Insert sample data
insert_sample_data()

# Query all customers
query_customers()
```

### Using GPT-4o for SQL Analysis

```python
from sql_demo.portia_direct import query_llm

# Define your SQL-related question
sql_prompt = """
I have a customer table with id, name, email, and signup_date.
How can I query customers who signed up in April 2024?
"""

# Get AI-generated SQL suggestions
api_key = os.getenv("OPENAI_API_KEY")
result = query_llm(api_key, sql_prompt)
print(result)
```

## Future Development

The SQL components are designed to be modular and can be integrated with other Portia tools and functionality. The MCP server implementation will allow for more complex SQL operations through a standardized protocol. 