#!/usr/bin/env python3
"""
Script to check the database schema of construction_data.db
"""

import sqlite3
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_database_schema(db_path):
    """Check the database schema and print table information"""
    if not os.path.exists(db_path):
        logger.info(f"Database file doesn't exist: {db_path}")
        return

    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        if not tables:
            logger.info("No tables found in the database.")
        else:
            logger.info(f"Found {len(tables)} tables:")

            # For each table, get its schema and row count
            for table in tables:
                table_name = table[0]

                # Get schema
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()

                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]

                logger.info(f"\nTable: {table_name} ({row_count} rows)")
                logger.info("Columns:")
                for col in columns:
                    col_id, name, type_, not_null, default_val, pk = col
                    logger.info(
                        f"  - {name} ({type_}){' PRIMARY KEY' if pk else ''}{' NOT NULL' if not_null else ''}"
                    )

                # Show sample data (first 3 rows)
                if row_count > 0:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                    rows = cursor.fetchall()

                    logger.info(f"Sample data (up to 3 rows):")
                    for row in rows:
                        logger.info(f"  {row}")

        # Close connection
        conn.close()

    except sqlite3.Error as e:
        logger.error(f"SQLite error: {e}")
    except Exception as e:
        logger.error(f"Error: {e}")


def main():
    """Main function to check database schema"""
    db_path = "portia_demo/construction_data.db"

    logger.info(f"Checking database: {db_path}")
    check_database_schema(db_path)

    # Also check sql_data.db
    alt_db_path = "portia_demo/sql_data.db"
    logger.info(f"\nChecking alternative database: {alt_db_path}")
    check_database_schema(alt_db_path)


if __name__ == "__main__":
    main()
