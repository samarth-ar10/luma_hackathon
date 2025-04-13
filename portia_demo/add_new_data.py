#!/usr/bin/env python3
"""
Add new data to the SQL databases
"""
import os
import sqlite3
from contextlib import contextmanager

# Database paths
SQL_DATA_DB = "sql_data.db"
CONSTRUCTION_DB = "construction_data.db"


@contextmanager
def get_db_connection(db_path):
    """Context manager for database connections."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def add_customers():
    """Add more customers to the sql_data.db"""
    with get_db_connection(SQL_DATA_DB) as conn:
        cursor = conn.cursor()

        # New customers data
        new_customers = [
            (5, "Michael Wilson", "michael@example.com", "2024-05-01"),
            (6, "Sarah Miller", "sarah@example.com", "2024-05-03"),
            (7, "David Clark", "david@example.com", "2024-03-25"),
            (8, "Emily White", "emily@example.com", "2024-04-15"),
            (9, "Thomas Lee", "thomas@example.com", "2024-04-18"),
            (10, "Jessica Moore", "jessica@example.com", "2024-05-05"),
        ]

        insert_sql = """
        INSERT OR IGNORE INTO customers (id, name, email, signup_date)
        VALUES (?, ?, ?, ?)
        """

        rows_added = 0
        for customer in new_customers:
            cursor.execute(insert_sql, customer)
            rows_added += cursor.rowcount

        conn.commit()
        print(f"Added {rows_added} new customers to sql_data.db")


def create_products_table():
    """Create a new products table in sql_data.db"""
    with get_db_connection(SQL_DATA_DB) as conn:
        cursor = conn.cursor()

        # Create products table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
        """
        )

        # Create orders table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            order_date TEXT NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
        """
        )

        # Create order_items table for the many-to-many relationship
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
        """
        )

        conn.commit()
        print("Created new tables: products, orders, and order_items")


def add_product_data():
    """Add sample product data"""
    with get_db_connection(SQL_DATA_DB) as conn:
        cursor = conn.cursor()

        # Sample products
        products = [
            (1, "Laptop Pro", "Electronics", 1299.99, 15),
            (2, "Smartphone X", "Electronics", 899.99, 25),
            (3, "Bluetooth Headphones", "Audio", 149.99, 30),
            (4, "Wireless Mouse", "Computer Accessories", 49.99, 50),
            (5, "USB-C Cable", "Computer Accessories", 19.99, 100),
            (6, "Smart Watch", "Wearables", 299.99, 20),
            (7, "Desk Lamp", "Home Office", 39.99, 45),
            (8, "Office Chair", "Furniture", 199.99, 10),
            (9, "Webcam HD", "Computer Accessories", 79.99, 35),
            (10, "External SSD 1TB", "Storage", 159.99, 40),
        ]

        # Sample orders
        orders = [
            (1, 2, "2024-04-05", 1449.98, "Delivered"),
            (2, 1, "2024-04-10", 299.99, "Delivered"),
            (3, 4, "2024-04-15", 129.98, "Shipped"),
            (4, 3, "2024-04-20", 199.99, "Processing"),
            (5, 6, "2024-05-01", 949.98, "Pending"),
            (6, 5, "2024-05-03", 379.98, "Processing"),
            (7, 7, "2024-05-04", 1499.97, "Pending"),
        ]

        # Sample order items
        order_items = [
            (1, 1, 1, 1, 1299.99),  # Order 1: 1 Laptop Pro
            (2, 1, 3, 1, 149.99),  # Order 1: 1 Headphones
            (3, 2, 6, 1, 299.99),  # Order 2: 1 Smart Watch
            (4, 3, 4, 1, 49.99),  # Order 3: 1 Wireless Mouse
            (5, 3, 5, 4, 19.99),  # Order 3: 4 USB-C Cables
            (6, 4, 8, 1, 199.99),  # Order 4: 1 Office Chair
            (7, 5, 2, 1, 899.99),  # Order 5: 1 Smartphone X
            (8, 5, 5, 2, 19.99),  # Order 5: 2 USB-C Cables
            (9, 6, 9, 1, 79.99),  # Order 6: 1 Webcam HD
            (10, 6, 10, 1, 159.99),  # Order 6: 1 External SSD
            (11, 6, 7, 1, 39.99),  # Order 6: 1 Desk Lamp
            (12, 7, 1, 1, 1299.99),  # Order 7: 1 Laptop Pro
            (13, 7, 9, 1, 79.99),  # Order 7: 1 Webcam HD
            (14, 7, 4, 1, 49.99),  # Order 7: 1 Wireless Mouse
        ]

        # Insert products
        for product in products:
            cursor.execute(
                """
            INSERT OR IGNORE INTO products (id, name, category, price, stock)
            VALUES (?, ?, ?, ?, ?)
            """,
                product,
            )

        # Insert orders
        for order in orders:
            cursor.execute(
                """
            INSERT OR IGNORE INTO orders (id, customer_id, order_date, total_amount, status)
            VALUES (?, ?, ?, ?, ?)
            """,
                order,
            )

        # Insert order items
        for item in order_items:
            cursor.execute(
                """
            INSERT OR IGNORE INTO order_items (id, order_id, product_id, quantity, price)
            VALUES (?, ?, ?, ?, ?)
            """,
                item,
            )

        conn.commit()
        print(
            f"Added {len(products)} products, {len(orders)} orders, and {len(order_items)} order items"
        )


def add_construction_data():
    """Add more data to the construction_data.db"""
    with get_db_connection(CONSTRUCTION_DB) as conn:
        cursor = conn.cursor()

        # Add more users (employees)
        new_users = [
            (
                11,
                "Rachel Turner",
                "architect",
                "rachel@constructco.com",
                "555-123-0011",
            ),
            (
                12,
                "Anthony Harris",
                "electrician",
                "anthony@constructco.com",
                "555-123-0012",
            ),
            (
                13,
                "Olivia Parker",
                "procurement",
                "olivia@constructco.com",
                "555-123-0013",
            ),
            (14, "Nathan Lewis", "laborer", "nathan@constructco.com", "555-123-0014"),
            (
                15,
                "Sophia Garcia",
                "environmental-specialist",
                "sophia@constructco.com",
                "555-123-0015",
            ),
        ]

        # Add more projects
        new_projects = [
            (
                6,
                "Green Office Complex",
                "Planning",
                "2024-05-15",
                "2025-08-30",
                4500000.00,
                2,
            ),
            (
                7,
                "Urban Mixed-Use Development",
                "Bidding",
                "2024-06-01",
                "2026-01-15",
                12000000.00,
                2,
            ),
            (
                8,
                "Hospital Renovation Wing B",
                "Approved",
                "2024-07-10",
                "2025-04-25",
                3200000.00,
                2,
            ),
        ]

        # Add more tasks
        new_tasks = [
            (
                21,
                6,
                "Initial Environmental Assessment",
                "Conduct site environmental review",
                "Not Started",
                "High",
                15,
                "2024-05-30",
            ),
            (
                22,
                6,
                "Architectural Drawings",
                "Create preliminary design drafts",
                "Not Started",
                "High",
                11,
                "2024-06-15",
            ),
            (
                23,
                6,
                "Budget Estimation",
                "Detailed cost analysis for green features",
                "Not Started",
                "Medium",
                3,
                "2024-06-10",
            ),
            (
                24,
                7,
                "Zoning Compliance Review",
                "Verify urban zoning requirements",
                "Not Started",
                "High",
                3,
                "2024-06-10",
            ),
            (
                25,
                7,
                "Stakeholder Meeting",
                "Present plans to community stakeholders",
                "Not Started",
                "Medium",
                2,
                "2024-06-20",
            ),
            (
                26,
                8,
                "Medical Equipment Specs",
                "Finalize specialized equipment requirements",
                "Not Started",
                "High",
                3,
                "2024-07-25",
            ),
            (
                27,
                8,
                "Electrical System Upgrade Plan",
                "Design electrical upgrades for medical equipment",
                "Not Started",
                "High",
                12,
                "2024-08-05",
            ),
        ]

        # Add more materials
        new_materials = [
            (
                21,
                "Solar Panels (250W)",
                120,
                "panel",
                350.00,
                6,
                "2024-07-15",
                "Ordered",
            ),
            (
                22,
                "Recycled Concrete Mix",
                500,
                "ton",
                85.00,
                6,
                "2024-07-20",
                "Pending",
            ),
            (
                23,
                "Energy Efficient Windows",
                85,
                "unit",
                450.00,
                6,
                "2024-08-01",
                "Pending",
            ),
            (24, "Steel I-Beams", 50, "unit", 1200.00, 7, "2024-07-10", "Pending"),
            (25, "Electrical Conduit", 2000, "foot", 3.50, 8, "2024-08-15", "Pending"),
            (
                26,
                "Hospital Grade Flooring",
                5000,
                "sq.ft",
                12.50,
                8,
                "2024-09-01",
                "Pending",
            ),
        ]

        # Add more safety reports
        new_safety_reports = [
            (
                8,
                5,
                "2024-05-05",
                4,
                0,
                "All safety protocols properly followed. No incidents.",
                "Compliant",
            ),
            (
                9,
                3,
                "2024-05-03",
                4,
                1,
                "Minor incident with equipment storage. Corrected on-site.",
                "Minor Issues",
            ),
            (
                10,
                4,
                "2024-05-02",
                9,
                0,
                "Regular inspection, all standards met.",
                "Compliant",
            ),
        ]

        # Insert data
        for user in new_users:
            cursor.execute(
                """
            INSERT OR IGNORE INTO users (id, name, role, email, phone)
            VALUES (?, ?, ?, ?, ?)
            """,
                user,
            )

        for project in new_projects:
            cursor.execute(
                """
            INSERT OR IGNORE INTO projects (id, name, status, start_date, end_date, budget, manager_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                project,
            )

        for task in new_tasks:
            cursor.execute(
                """
            INSERT OR IGNORE INTO tasks (id, project_id, name, description, status, priority, assigned_to, due_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                task,
            )

        for material in new_materials:
            cursor.execute(
                """
            INSERT OR IGNORE INTO materials (id, name, quantity, unit, unit_price, project_id, delivery_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                material,
            )

        for report in new_safety_reports:
            cursor.execute(
                """
            INSERT OR IGNORE INTO safety_reports (id, project_id, report_date, inspector_id, incident_count, description, compliance_status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                report,
            )

        conn.commit()
        print(
            f"Added to construction_data.db: {len(new_users)} users, {len(new_projects)} projects, {len(new_tasks)} tasks, {len(new_materials)} materials, {len(new_safety_reports)} safety reports"
        )


def add_equipment_table():
    """Add a new equipment table to construction_data.db"""
    with get_db_connection(CONSTRUCTION_DB) as conn:
        cursor = conn.cursor()

        # Create equipment table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS equipment (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            status TEXT NOT NULL,
            purchase_date TEXT,
            last_maintenance TEXT,
            next_maintenance TEXT,
            assigned_project INTEGER,
            assigned_to INTEGER,
            daily_cost REAL,
            FOREIGN KEY (assigned_project) REFERENCES projects(id),
            FOREIGN KEY (assigned_to) REFERENCES users(id)
        )
        """
        )

        # Create equipment_maintenance_log table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS equipment_maintenance_log (
            id INTEGER PRIMARY KEY,
            equipment_id INTEGER NOT NULL,
            maintenance_date TEXT NOT NULL,
            maintenance_type TEXT NOT NULL,
            description TEXT,
            performed_by INTEGER,
            cost REAL,
            FOREIGN KEY (equipment_id) REFERENCES equipment(id),
            FOREIGN KEY (performed_by) REFERENCES users(id)
        )
        """
        )

        # Sample equipment data
        equipment = [
            (
                1,
                "Excavator CAT 320",
                "Heavy Machinery",
                "Operational",
                "2022-03-15",
                "2024-04-10",
                "2024-07-10",
                4,
                5,
                450.00,
            ),
            (
                2,
                "Concrete Mixer XL",
                "Heavy Machinery",
                "Operational",
                "2023-01-20",
                "2024-03-05",
                "2024-06-05",
                3,
                5,
                200.00,
            ),
            (
                3,
                "Crane RT100",
                "Heavy Machinery",
                "Under Maintenance",
                "2021-05-10",
                "2024-05-02",
                "2024-05-10",
                None,
                None,
                750.00,
            ),
            (
                4,
                "Bulldozer D6",
                "Heavy Machinery",
                "Operational",
                "2022-07-22",
                "2024-02-15",
                "2024-05-15",
                5,
                5,
                375.00,
            ),
            (
                5,
                "Portable Generator 50kW",
                "Power Equipment",
                "Operational",
                "2023-04-18",
                "2024-04-01",
                "2024-07-01",
                3,
                12,
                125.00,
            ),
            (
                6,
                "Scissor Lift 20ft",
                "Access Equipment",
                "Operational",
                "2023-10-05",
                "2024-03-20",
                "2024-06-20",
                3,
                14,
                150.00,
            ),
            (
                7,
                "Jackhammer XHD",
                "Hand Tools",
                "Operational",
                "2023-08-12",
                "2024-04-15",
                "2024-07-15",
                5,
                14,
                75.00,
            ),
            (
                8,
                "Surveying Equipment GPS",
                "Precision Tools",
                "Operational",
                "2024-01-10",
                "2024-04-10",
                "2024-07-10",
                None,
                3,
                100.00,
            ),
            (
                9,
                "Forklift 5-Ton",
                "Material Handling",
                "Operational",
                "2022-11-30",
                "2024-03-01",
                "2024-06-01",
                4,
                5,
                225.00,
            ),
            (
                10,
                "Welding Machine Industrial",
                "Specialty Equipment",
                "Out of Service",
                "2022-05-19",
                "2024-02-28",
                "2024-03-15",
                None,
                None,
                90.00,
            ),
        ]

        # Sample maintenance logs
        maintenance_logs = [
            (
                1,
                1,
                "2024-04-10",
                "Routine",
                "Oil change and filter replacement",
                12,
                350.00,
            ),
            (
                2,
                2,
                "2024-03-05",
                "Routine",
                "General inspection and lubrication",
                5,
                150.00,
            ),
            (
                3,
                3,
                "2024-05-02",
                "Repair",
                "Hydraulic system malfunction repair",
                12,
                1200.00,
            ),
            (
                4,
                4,
                "2024-02-15",
                "Routine",
                "Track tension adjustment and lubrication",
                5,
                275.00,
            ),
            (
                5,
                5,
                "2024-04-01",
                "Routine",
                "Filter replacement and fuel system check",
                12,
                125.00,
            ),
            (
                6,
                6,
                "2024-03-20",
                "Routine",
                "Lift mechanism inspection and lubrication",
                14,
                100.00,
            ),
            (
                7,
                7,
                "2024-04-15",
                "Routine",
                "Bit replacement and mechanism cleaning",
                14,
                75.00,
            ),
            (
                8,
                8,
                "2024-04-10",
                "Calibration",
                "Precision calibration and software update",
                3,
                0.00,
            ),
            (
                9,
                9,
                "2024-03-01",
                "Routine",
                "Fork inspection and hydraulic system check",
                5,
                200.00,
            ),
            (
                10,
                10,
                "2024-02-28",
                "Repair",
                "Power supply board replacement",
                12,
                450.00,
            ),
            (
                11,
                3,
                "2024-05-02",
                "Emergency",
                "Boom arm hydraulic failure",
                12,
                2200.00,
            ),
            (
                12,
                10,
                "2024-03-15",
                "Inspection",
                "Safety inspection failed - electrical issues",
                12,
                0.00,
            ),
        ]

        # Insert equipment data
        for item in equipment:
            cursor.execute(
                """
            INSERT OR IGNORE INTO equipment (id, name, type, status, purchase_date, last_maintenance, next_maintenance, assigned_project, assigned_to, daily_cost)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                item,
            )

        # Insert maintenance logs
        for log in maintenance_logs:
            cursor.execute(
                """
            INSERT OR IGNORE INTO equipment_maintenance_log (id, equipment_id, maintenance_date, maintenance_type, description, performed_by, cost)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                log,
            )

        conn.commit()
        print(
            f"Added to construction_data.db: new equipment table with {len(equipment)} items and {len(maintenance_logs)} maintenance logs"
        )


def main():
    """Main function to add data to databases"""
    # Make sure we're in the right directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    print("Adding new data to databases...")

    # Add data to sql_data.db
    add_customers()
    create_products_table()
    add_product_data()

    # Add data to construction_data.db
    add_construction_data()
    add_equipment_table()

    print("Data addition complete!")


if __name__ == "__main__":
    main()
