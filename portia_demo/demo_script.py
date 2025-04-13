#!/usr/bin/env python3
"""
SQL Demo - Simple script to demonstrate the use of execute_sql_query
"""
from sql_demo import (
    create_table,
    insert_sample_data,
    execute_sql_query,
    display_customers,
)


def main():
    """Run the SQL demo script"""
    print("=" * 50)
    print("SQL Demo")
    print("=" * 50)

    # Step 1: Create the database and add sample data
    print("\n>> Step 1: Setting up the database")
    create_table()
    insert_sample_data()

    # Step 2: Execute a SQL query using execute_sql_query
    print("\n>> Step 2: Using execute_sql_query")
    query = "SELECT * FROM customers"
    result = execute_sql_query(query)

    # Check if query was successful
    if result["success"]:
        if "results" in result:
            # For SELECT queries, show the results
            print(
                f"Query executed successfully. Found {len(result['results'])} "
                f"customers:"
            )
            # Use the display_customers helper to format the output nicely
            display_customers(result["results"])
        else:
            # For non-SELECT queries, show the message
            print(result["message"])
    else:
        # Handle errors
        print(f"Error executing query: {result['error']}")

    # Step 3: Execute a more complex query
    print("\n>> Step 3: More complex query")
    complex_query = "SELECT * FROM customers WHERE signup_date LIKE '2024-04-%'"
    result = execute_sql_query(complex_query)

    if result["success"] and "results" in result:
        print(
            f"Query executed successfully. Found {len(result['results'])} "
            f"customers:"
        )
        display_customers(result["results"])
    else:
        print(f"Error executing query: {result.get('error', 'Unknown error')}")

    print("\nDemo complete!")


if __name__ == "__main__":
    main()
