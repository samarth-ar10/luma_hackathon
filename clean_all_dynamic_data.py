#!/usr/bin/env python3
"""
Script to clean up all dynamic data in the databases
Keeps only the most recent records to reduce context size
"""
import sqlite3
import os
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Tables with dynamic data that we can clean up
DYNAMIC_TABLES = {
    "portia_demo/construction_data.db": [
        {
            "name": "conversation_history",
            "time_col": "timestamp",
            "id_col": "id",
            "keep_count": 10,
        },
        {
            "name": "equipment_maintenance_log",
            "time_col": "maintenance_date",
            "id_col": "id",
            "keep_count": 5,
        },
        {
            "name": "user_preferences",
            "time_col": "last_updated",
            "id_col": "user_id",
            "keep_count": 3,  # Keep only most recent preferences per user
        },
    ],
    "portia_demo/sql_data.db": [
        {"name": "orders", "time_col": "order_date", "id_col": "id", "keep_count": 5}
    ],
}


def connect_to_database(db_path):
    """Connect to the SQLite database"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Error connecting to database: {e}")
        return None


def clean_table(conn, table_info, dry_run=True):
    """Clean up a table by deleting older records"""
    table_name = table_info["name"]
    time_col = table_info["time_col"]
    id_col = table_info["id_col"]
    keep_count = table_info["keep_count"]

    try:
        cursor = conn.cursor()

        # Check if table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
        )
        if not cursor.fetchone():
            logger.warning(
                f"Table {table_name} does not exist in this database. Skipping."
            )
            return 0

        # Get total records
        cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
        total_count = cursor.fetchone()["count"]

        if total_count <= keep_count:
            logger.info(
                f"Table {table_name} has {total_count} records, which is <= {keep_count}. No cleanup needed."
            )
            return 0

        # Determine how many to delete
        delete_count = total_count - keep_count

        # Construct the query
        query = f"""
        DELETE FROM {table_name} 
        WHERE {id_col} NOT IN (
            SELECT {id_col} FROM {table_name} 
            ORDER BY {time_col} DESC 
            LIMIT {keep_count}
        )
        """

        if dry_run:
            logger.info(f"DRY RUN for {table_name}: Would execute: {query}")
            logger.info(
                f"This would delete {delete_count} records, keeping {keep_count}"
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
        logger.error(f"Error cleaning table {table_name}: {e}")
        return 0


def clean_related_items(conn, dry_run=True):
    """Clean up related items (like order_items after cleaning orders)"""
    try:
        cursor = conn.cursor()

        # Check if order_items exists when orders table is present
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='order_items'"
        )
        if cursor.fetchone():
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='orders'"
            )
            if cursor.fetchone():
                # Get remaining order IDs
                cursor.execute("SELECT id FROM orders")
                remaining_orders = [row["id"] for row in cursor.fetchall()]

                if not remaining_orders:
                    logger.warning("No orders found. Skipping order_items cleanup.")
                    return 0

                # Get orphaned order items
                placeholders = ",".join(["?"] * len(remaining_orders))
                cursor.execute(
                    f"SELECT COUNT(*) as count FROM order_items WHERE order_id NOT IN ({placeholders})",
                    remaining_orders,
                )
                orphan_count = cursor.fetchone()["count"]

                if orphan_count == 0:
                    logger.info("No orphaned order_items found. Skipping cleanup.")
                    return 0

                # Delete orphaned order items
                query = (
                    f"DELETE FROM order_items WHERE order_id NOT IN ({placeholders})"
                )

                if dry_run:
                    logger.info(f"DRY RUN: Would execute: {query}")
                    logger.info(
                        f"This would delete {orphan_count} orphaned order_items"
                    )
                    return orphan_count
                else:
                    logger.info(f"Executing: {query}")
                    cursor.execute(query, remaining_orders)
                    deleted = cursor.rowcount
                    conn.commit()
                    logger.info(f"Deleted {deleted} orphaned records from order_items")
                    return deleted

        return 0
    except sqlite3.Error as e:
        logger.error(f"Error cleaning related items: {e}")
        return 0


def delete_empty_preferences(conn, dry_run=True):
    """Delete empty dashboard_items which may be taking up space"""
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='dashboard_items'"
        )
        if cursor.fetchone():
            cursor.execute("SELECT COUNT(*) as count FROM dashboard_items")
            count = cursor.fetchone()["count"]

            if count == 0:
                # Table exists but is empty - we can use VACUUM to reclaim space
                if not dry_run:
                    logger.info("Running VACUUM to reclaim space from empty tables")
                    cursor.execute("VACUUM")
                    conn.commit()
                    logger.info("VACUUM completed successfully")
                else:
                    logger.info("DRY RUN: Would run VACUUM to reclaim space")

        return 0
    except sqlite3.Error as e:
        logger.error(f"Error handling empty tables: {e}")
        return 0


def main():
    parser = argparse.ArgumentParser(
        description="Clean up all dynamic data in the databases"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually perform the deletion (default is dry run)",
    )

    args = parser.parse_args()
    dry_run = not args.execute

    mode = "DRY RUN" if dry_run else "EXECUTE"
    logger.info(f"Running in {mode} mode")

    total_deleted = 0

    # Process each database
    for db_path, tables in DYNAMIC_TABLES.items():
        if not os.path.exists(db_path):
            logger.error(f"Database file not found: {db_path}")
            continue

        logger.info(f"Processing database: {db_path}")
        conn = connect_to_database(db_path)
        if not conn:
            continue

        try:
            # Clean each table
            for table_info in tables:
                deleted = clean_table(conn, table_info, dry_run)
                total_deleted += deleted

            # Clean related items
            if db_path == "portia_demo/sql_data.db":
                deleted = clean_related_items(conn, dry_run)
                total_deleted += deleted

            # Handle empty preferences
            if db_path == "portia_demo/construction_data.db":
                delete_empty_preferences(conn, dry_run)

        finally:
            conn.close()

    logger.info(f"{mode}: Would delete/Deleted a total of {total_deleted} records")

    if dry_run:
        logger.info(
            "This was a dry run. Use --execute to actually perform the deletion."
        )


if __name__ == "__main__":
    main()
