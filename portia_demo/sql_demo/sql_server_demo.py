#!/usr/bin/env python3
"""
SQL Server Demo - A simple SQLite database implementation.
Creates a customers table, inserts sample data, and provides query functionality.
"""
import os
import sqlite3
from contextlib import contextmanager

# Create a simple SQLite database
DB_PATH = os.environ.get("SQL_MCP_DB_PATH", "sql_data.db")


@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def create_table():
    """Create a customers table."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        create_sql = """
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            signup_date TEXT
        )
        """
        cursor.execute(create_sql)
        conn.commit()
        print(f"Table 'customers' created successfully.")


def insert_sample_data():
    """Insert sample data into the customers table."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Sample customers
        customers = [
            (1, "John Doe", "john@example.com", "2024-04-01"),
            (2, "Jane Smith", "jane@example.com", "2024-04-02"),
            (3, "Alice Johnson", "alice@example.com", "2024-03-15"),
            (4, "Bob Brown", "bob@example.com", "2024-04-10"),
        ]

        insert_sql = """
        INSERT OR IGNORE INTO customers (id, name, email, signup_date)
        VALUES (?, ?, ?, ?)
        """

        rows_added = 0
        for customer in customers:
            cursor.execute(insert_sql, customer)
            rows_added += cursor.rowcount

        conn.commit()
        if rows_added > 0:
            print(f"Added {rows_added} sample customers.")
        else:
            print(f"Sample customers already exist.")


def query_customers(query=None):
    """Query customers from the database.

    Args:
        query (str, optional): Custom SQL query. If None, returns all customers.

    Returns:
        list: List of dictionaries with customer data
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        if query is None:
            query = "SELECT * FROM customers"

        cursor.execute(query)

        # Convert to list of dicts
        columns = [col[0] for col in cursor.description]
        result = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return result


def display_customers(customers=None):
    """Display customers in a formatted table.

    Args:
        customers (list, optional): List of customer dictionaries. If None, all customers are displayed.
    """
    if customers is None:
        customers = query_customers()

    if not customers:
        print("No customers found.")
        return

    print("\nAll Customers:")
    print("-" * 80)
    print(f"{'ID':<5} {'Name':<20} {'Email':<30} {'Signup Date':<15}")
    print("-" * 80)

    for customer in customers:
        print(
            f"{customer['id']:<5} {customer['name']:<20} {customer['email']:<30} {customer['signup_date']:<15}"
        )


def execute_sql_query(query):
    """Execute a SQL query and return the results.

    Args:
        query (str): SQL query to execute

    Returns:
        dict: Result dictionary with success status and data/message
    """
    with get_db_connection() as conn:
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


def main():
    """Run demo script to create and query the database."""
    print("SQL Database Demo")
    print("=" * 30)

    # Create tables
    create_table()

    # Insert sample data
    insert_sample_data()

    # Display all customers
    display_customers()

    # Example custom query - finding customers who signed up in April
    print("\nCustomers who signed up in April 2024:")
    april_customers = query_customers(
        "SELECT * FROM customers WHERE signup_date LIKE '2024-04-%'"
    )
    display_customers(april_customers)


if __name__ == "__main__":
    main()
