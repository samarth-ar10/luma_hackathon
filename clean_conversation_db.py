#!/usr/bin/env python3
"""
Script to clean up the conversation database by deleting older conversations
"""
import sqlite3
import os
import argparse
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def connect_to_database(db_path):
    """Connect to the SQLite database"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Error connecting to database: {e}")
        return None


def get_conversation_tables(conn):
    """Find tables in the database that might contain conversation data"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    conversation_tables = []
    for table in tables:
        table_name = table["name"]
        # Check if this looks like a conversation table
        try:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col["name"].lower() for col in cursor.fetchall()]

            # Look for tables that have message/timestamp/user columns
            if (
                any("message" in col for col in columns)
                or any("timestamp" in col for col in columns)
                or any("user" in col for col in columns)
                or "conversation" in table_name.lower()
            ):
                conversation_tables.append(table_name)
        except sqlite3.Error:
            pass

    return conversation_tables


def get_conversation_count(conn, table_name):
    """Get the total number of conversations in the table"""
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
        result = cursor.fetchone()
        return result["count"] if result else 0
    except sqlite3.Error as e:
        logger.error(f"Error counting conversations in {table_name}: {e}")
        return 0


def clean_conversations(conn, table_name, keep_count=50, dry_run=True):
    """Clean up conversations by deleting all but the most recent ones"""
    try:
        cursor = conn.cursor()

        # First, try to find the timestamp column
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        timestamp_col = None
        id_col = None

        for col in columns:
            col_name = col["name"].lower()
            # Find the timestamp column
            if "timestamp" in col_name or "date" in col_name or "time" in col_name:
                timestamp_col = col["name"]
            # Find the ID column
            if col_name == "id" or col_name.endswith("_id"):
                id_col = col["name"]

        if not id_col:
            logger.warning(f"Could not find ID column in {table_name}, using rowid")
            id_col = "rowid"

        # Get the total count
        total_count = get_conversation_count(conn, table_name)
        if total_count <= keep_count:
            logger.info(
                f"Table {table_name} has {total_count} records, which is less than or equal to {keep_count}. No cleanup needed."
            )
            return 0

        # Determine how many to delete
        delete_count = total_count - keep_count

        # Construct the query based on available columns
        if timestamp_col:
            query = f"""
            DELETE FROM {table_name} 
            WHERE {id_col} NOT IN (
                SELECT {id_col} FROM {table_name} 
                ORDER BY {timestamp_col} DESC 
                LIMIT {keep_count}
            )
            """
        else:
            query = f"""
            DELETE FROM {table_name} 
            WHERE {id_col} NOT IN (
                SELECT {id_col} FROM {table_name} 
                ORDER BY {id_col} DESC 
                LIMIT {keep_count}
            )
            """

        if dry_run:
            logger.info(f"DRY RUN: Would execute: {query}")
            logger.info(
                f"This would delete approximately {delete_count} records from {table_name}"
            )
            return delete_count
        else:
            logger.info(f"Executing: {query}")
            cursor.execute(query)
            deleted = cursor.rowcount
            conn.commit()
            logger.info(f"Deleted {deleted} records from {table_name}")
            return deleted

    except sqlite3.Error as e:
        logger.error(f"Error cleaning conversations in {table_name}: {e}")
        return 0


def main():
    parser = argparse.ArgumentParser(
        description="Clean up conversation database by removing old records"
    )
    parser.add_argument(
        "--db",
        default="portia_demo/construction_data.db",
        help="Path to the database file",
    )
    parser.add_argument(
        "--keep",
        type=int,
        default=50,
        help="Number of most recent conversations to keep",
    )
    parser.add_argument(
        "--table", help="Specific table to clean (optional, will auto-detect otherwise)"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually perform the deletion (default is dry run)",
    )

    args = parser.parse_args()

    db_path = args.db
    keep_count = args.keep
    specific_table = args.table
    dry_run = not args.execute

    if not os.path.exists(db_path):
        logger.error(f"Database file not found: {db_path}")
        return 1

    conn = connect_to_database(db_path)
    if not conn:
        return 1

    try:
        if specific_table:
            tables = [specific_table]
        else:
            tables = get_conversation_tables(conn)

        if not tables:
            logger.warning("No conversation tables found in the database")
            return 0

        logger.info(
            f"Found {len(tables)} potential conversation tables: {', '.join(tables)}"
        )

        total_deleted = 0
        for table in tables:
            deleted = clean_conversations(conn, table, keep_count, dry_run)
            total_deleted += deleted

        mode = "DRY RUN" if dry_run else "EXECUTED"
        logger.info(
            f"{mode}: Would delete/Deleted a total of {total_deleted} records from {len(tables)} tables"
        )

        if dry_run:
            logger.info(
                "This was a dry run. Use --execute to actually perform the deletion."
            )

    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    exit(main())
