#!/usr/bin/env python3
"""
Script to list all tables in the database and their row counts
"""
import sqlite3
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def list_tables(db_path):
    """List all tables in the database and their row counts"""
    if not os.path.exists(db_path):
        logger.error(f"Database file not found: {db_path}")
        return

    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        if not tables:
            logger.info(f"No tables found in {db_path}")
            return

        logger.info(f"Found {len(tables)} tables in {db_path}:")

        # For each table, get row count and schema
        for table in tables:
            table_name = table[0]

            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]

            # Get schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            # Get sample data (first row only)
            if row_count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
                sample = cursor.fetchone()
            else:
                sample = None

            # Print info
            logger.info(f"- Table: {table_name} ({row_count} rows)")
            logger.info(f"  Columns: {', '.join(col[1] for col in columns)}")

            # Check for dynamic data indicators in column names
            dynamic_indicators = [
                "timestamp",
                "date",
                "time",
                "log",
                "history",
                "session",
                "cache",
                "temp",
                "activity",
            ]

            dynamic_columns = [
                col[1]
                for col in columns
                if any(ind in col[1].lower() for ind in dynamic_indicators)
            ]

            if dynamic_columns:
                logger.info(f"  Dynamic data columns: {', '.join(dynamic_columns)}")

            # If there's sample data, show a snippet
            if sample:
                sample_str = str(sample)
                if len(sample_str) > 100:
                    sample_str = sample_str[:97] + "..."
                logger.info(f"  Sample: {sample_str}")

            logger.info("")

        conn.close()

    except sqlite3.Error as e:
        logger.error(f"Error accessing database {db_path}: {e}")


def main():
    # Check both databases
    list_tables("portia_demo/construction_data.db")
    list_tables("portia_demo/sql_data.db")


if __name__ == "__main__":
    main()
