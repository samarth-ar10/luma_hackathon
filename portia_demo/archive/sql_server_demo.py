#!/usr/bin/env python3
import sqlite3
import os
from contextlib import contextmanager

# Create a simple SQLite database
DB_PATH = "sql_data.db"


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
        ]

        insert_sql = """
        INSERT INTO customers (id, name, email, signup_date)
        VALUES (?, ?, ?, ?)
        """

        for customer in customers:
            try:
                cursor.execute(insert_sql, customer)
            except sqlite3.IntegrityError:
                print(f"Customer with ID {customer[0]} already exists.")

        conn.commit()
        print(f"Sample customers inserted successfully.")


def query_customers():
    """Query all customers from the database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers")
        customers = cursor.fetchall()

        print("\nAll Customers:")
        print("-" * 60)
        print(f"{'ID':<5} {'Name':<20} {'Email':<25} {'Signup Date':<15}")
        print("-" * 60)

        for customer in customers:
            print(
                f"{customer['id']:<5} {customer['name']:<20} {customer['email']:<25} {customer['signup_date']:<15}"
            )


def main():
    print("SQL Database Demo")
    print("=" * 30)

    # Create tables
    create_table()

    # Insert sample data
    insert_sample_data()

    # Query data
    query_customers()


if __name__ == "__main__":
    main()
