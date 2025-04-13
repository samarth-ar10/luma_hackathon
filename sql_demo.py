#!/usr/bin/env python3
"""
Demo script to showcase the functionality of the SQL demo
"""

from portia_demo.sql_demo import (
    create_table,
    insert_sample_data,
    execute_sql_query,
)

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_database():
    """
    Setup the database with sample data
    """
    logger.info("Creating table...")
    create_table()
    logger.info("Inserting sample data...")
    insert_sample_data()


def main():
    """
    Main function to showcase the functionality of execute_sql_query
    """
    # Step 1: Setup
    setup_database()

    # Step 2: Simple query
    logger.info("Executing simple query...")
    try:
        result = execute_sql_query("SELECT * FROM customers")
        logger.info("Query result: %s", result)
    except Exception as e:
        logger.error("Error executing query: %s", e)

    # Step 3: More complex query
    logger.info("Executing more complex query...")
    try:
        result = execute_sql_query(
            "SELECT * FROM customers WHERE signup_date LIKE '2024-04-%'"
        )
        logger.info("Query result: %s", result)
    except Exception as e:
        logger.error("Error executing query: %s", e)


if __name__ == "__main__":
    main()
