#!/usr/bin/env python3
"""
Database initialization script for the company communication and data flow manager.
Creates tables and populates them with sample data for all roles.
"""
import os
import sqlite3
from contextlib import contextmanager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_PATH = os.environ.get("SQL_MCP_DB_PATH", "../sql_data.db")


@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def create_tables():
    """Create all required tables for the application."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Keep existing customers table (from the original demo)
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            signup_date TEXT
        )
        """
        )

        # Create employees table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            department TEXT,
            role TEXT,
            salary REAL,
            hire_date TEXT,
            manager_id INTEGER,
            FOREIGN KEY (manager_id) REFERENCES employees (id)
        )
        """
        )

        # Create sales table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            product_name TEXT,
            amount REAL,
            date TEXT,
            sales_rep_id INTEGER,
            FOREIGN KEY (customer_id) REFERENCES customers (id),
            FOREIGN KEY (sales_rep_id) REFERENCES employees (id)
        )
        """
        )

        # Create projects table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY,
            name TEXT,
            description TEXT,
            department TEXT,
            start_date TEXT,
            end_date TEXT,
            budget REAL,
            status TEXT,
            manager_id INTEGER,
            FOREIGN KEY (manager_id) REFERENCES employees (id)
        )
        """
        )

        # Create tickets table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY,
            title TEXT,
            description TEXT,
            status TEXT,
            priority INTEGER,
            assigned_to INTEGER,
            created_by INTEGER,
            created_date TEXT,
            resolution TEXT,
            FOREIGN KEY (assigned_to) REFERENCES employees (id),
            FOREIGN KEY (created_by) REFERENCES employees (id)
        )
        """
        )

        # Create tasks table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT,
            description TEXT,
            status TEXT,
            due_date TEXT,
            assigned_to INTEGER,
            project_id INTEGER,
            FOREIGN KEY (assigned_to) REFERENCES employees (id),
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
        """
        )

        # Create marketing_campaigns table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS marketing_campaigns (
            id INTEGER PRIMARY KEY,
            name TEXT,
            start_date TEXT,
            end_date TEXT,
            budget REAL,
            target_audience TEXT,
            channel TEXT,
            status TEXT,
            lead_count INTEGER,
            conversion_rate REAL
        )
        """
        )

        # Create leads table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            phone TEXT,
            source TEXT,
            status TEXT,
            date_acquired TEXT,
            campaign_id INTEGER,
            FOREIGN KEY (campaign_id) REFERENCES marketing_campaigns (id)
        )
        """
        )

        # Create construction_sites table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS construction_sites (
            id INTEGER PRIMARY KEY,
            name TEXT,
            location TEXT,
            project_id INTEGER,
            start_date TEXT,
            status TEXT,
            site_manager_id INTEGER,
            budget REAL,
            FOREIGN KEY (project_id) REFERENCES projects (id),
            FOREIGN KEY (site_manager_id) REFERENCES employees (id)
        )
        """
        )

        # Create materials table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY,
            name TEXT,
            unit TEXT,
            quantity REAL,
            price_per_unit REAL,
            supplier TEXT,
            reorder_level REAL
        )
        """
        )

        # Create KPIs table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS kpis (
            id INTEGER PRIMARY KEY,
            name TEXT,
            value REAL,
            target REAL,
            period TEXT,
            department TEXT
        )
        """
        )

        # Create department_performance table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS department_performance (
            id INTEGER PRIMARY KEY,
            department TEXT,
            performance_score REAL,
            period TEXT,
            details TEXT
        )
        """
        )

        conn.commit()
        print("All tables created successfully!")


def insert_sample_data():
    """Insert sample data into all tables."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Insert sample employees
        employees = [
            (
                1,
                "John Smith",
                "john.smith@company.com",
                "Executive",
                "CEO",
                250000.00,
                "2020-01-01",
                None,
            ),
            (
                2,
                "Sarah Johnson",
                "sarah.j@company.com",
                "Marketing",
                "Marketing Director",
                120000.00,
                "2020-02-15",
                1,
            ),
            (
                3,
                "Michael Lee",
                "michael.l@company.com",
                "Sales",
                "Sales Director",
                115000.00,
                "2020-03-10",
                1,
            ),
            (
                4,
                "Emily Brown",
                "emily.b@company.com",
                "Engineering",
                "CTO",
                145000.00,
                "2020-02-01",
                1,
            ),
            (
                5,
                "Robert Garcia",
                "robert.g@company.com",
                "Construction",
                "Construction Manager",
                105000.00,
                "2020-04-15",
                1,
            ),
            (
                6,
                "Jennifer Wilson",
                "jennifer.w@company.com",
                "Marketing",
                "Marketing Specialist",
                75000.00,
                "2021-01-10",
                2,
            ),
            (
                7,
                "David Thompson",
                "david.t@company.com",
                "Sales",
                "Sales Representative",
                65000.00,
                "2021-02-15",
                3,
            ),
            (
                8,
                "Jessica Martinez",
                "jessica.m@company.com",
                "Engineering",
                "Senior Developer",
                110000.00,
                "2020-06-15",
                4,
            ),
            (
                9,
                "Daniel Rodriguez",
                "daniel.r@company.com",
                "Construction",
                "Site Supervisor",
                80000.00,
                "2021-03-01",
                5,
            ),
            (
                10,
                "Amanda White",
                "amanda.w@company.com",
                "HR",
                "HR Manager",
                95000.00,
                "2020-05-01",
                1,
            ),
        ]
        cursor.executemany(
            """
        INSERT OR IGNORE INTO employees (id, name, email, department, role, salary, hire_date, manager_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            employees,
        )

        # Insert more customers (beyond the 4 in the original demo)
        customers = [
            (5, "Mark Williams", "mark@example.com", "2023-11-15"),
            (6, "Susan Taylor", "susan@example.com", "2023-12-20"),
            (7, "James Anderson", "james@example.com", "2024-01-10"),
            (8, "Patricia Moore", "patricia@example.com", "2024-02-05"),
            (9, "Michael Davis", "michael@example.com", "2024-02-25"),
            (10, "Elizabeth Clark", "elizabeth@example.com", "2024-03-18"),
        ]
        cursor.executemany(
            """
        INSERT OR IGNORE INTO customers (id, name, email, signup_date)
        VALUES (?, ?, ?, ?)
        """,
            customers,
        )

        # Insert sample sales data
        sales = [
            (1, 1, "Product A", 1500.00, "2024-01-15", 7),
            (2, 2, "Product B", 2200.00, "2024-01-22", 7),
            (3, 3, "Product C", 1800.00, "2024-02-05", 7),
            (4, 4, "Product A", 1500.00, "2024-02-12", 7),
            (5, 5, "Product D", 3000.00, "2024-02-20", 7),
            (6, 6, "Product B", 2200.00, "2024-03-05", 7),
            (7, 7, "Product C", 1800.00, "2024-03-15", 7),
            (8, 8, "Product E", 4500.00, "2024-03-22", 7),
            (9, 9, "Product B", 2200.00, "2024-04-02", 7),
            (10, 10, "Product A", 1500.00, "2024-04-10", 7),
        ]
        cursor.executemany(
            """
        INSERT OR IGNORE INTO sales (id, customer_id, product_name, amount, date, sales_rep_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
            sales,
        )

        # Insert sample projects data
        projects = [
            (
                1,
                "Website Redesign",
                "Redesign company website for better UX",
                "Engineering",
                "2024-01-05",
                "2024-03-31",
                25000.00,
                "completed",
                4,
            ),
            (
                2,
                "Mobile App Development",
                "Develop iOS and Android app",
                "Engineering",
                "2024-02-01",
                "2024-06-30",
                50000.00,
                "active",
                4,
            ),
            (
                3,
                "Office Renovation",
                "Renovate the main office building",
                "Construction",
                "2024-01-15",
                "2024-05-15",
                150000.00,
                "active",
                5,
            ),
            (
                4,
                "Q2 Marketing Campaign",
                "Launch Q2 digital marketing campaign",
                "Marketing",
                "2024-04-01",
                "2024-06-30",
                35000.00,
                "active",
                2,
            ),
            (
                5,
                "Sales Training Program",
                "Train sales team on new products",
                "Sales",
                "2024-03-15",
                "2024-04-15",
                10000.00,
                "active",
                3,
            ),
            (
                6,
                "New Warehouse Construction",
                "Build new warehouse facility",
                "Construction",
                "2024-06-01",
                "2024-12-31",
                500000.00,
                "planned",
                5,
            ),
        ]
        cursor.executemany(
            """
        INSERT OR IGNORE INTO projects (id, name, description, department, start_date, end_date, budget, status, manager_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            projects,
        )

        # Insert sample tickets data
        tickets = [
            (
                1,
                "Server Down",
                "Main production server is not responding",
                "critical",
                1,
                8,
                4,
                "2024-04-01",
                None,
            ),
            (
                2,
                "Login Feature Bug",
                "Users cannot login using SSO",
                "high",
                2,
                8,
                6,
                "2024-04-02",
                None,
            ),
            (
                3,
                "Update Documentation",
                "Update API documentation for v2",
                "medium",
                3,
                8,
                2,
                "2024-03-25",
                "Documentation updated",
            ),
            (
                4,
                "Performance Issue",
                "App loading time is too slow",
                "high",
                2,
                8,
                7,
                "2024-03-28",
                None,
            ),
            (
                5,
                "New Feature Request",
                "Add dark mode to mobile app",
                "low",
                4,
                8,
                9,
                "2024-04-05",
                None,
            ),
        ]
        cursor.executemany(
            """
        INSERT OR IGNORE INTO tickets (id, title, description, status, priority, assigned_to, created_by, created_date, resolution)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            tickets,
        )

        # Insert sample tasks data
        tasks = [
            (
                1,
                "Design Homepage",
                "Create design mockups for homepage",
                "in_progress",
                "2024-04-15",
                8,
                1,
            ),
            (
                2,
                "Implement Login",
                "Develop login functionality for app",
                "completed",
                "2024-03-15",
                8,
                2,
            ),
            (
                3,
                "Test Payment System",
                "Test payment gateway integration",
                "not_started",
                "2024-04-30",
                8,
                2,
            ),
            (
                4,
                "Purchase Materials",
                "Order materials for office renovation",
                "in_progress",
                "2024-04-10",
                9,
                3,
            ),
            (
                5,
                "Create Social Media Content",
                "Develop content for Q2 campaign",
                "in_progress",
                "2024-04-20",
                6,
                4,
            ),
            (
                6,
                "Prepare Sales Training Materials",
                "Create training slides and materials",
                "completed",
                "2024-03-25",
                7,
                5,
            ),
        ]
        cursor.executemany(
            """
        INSERT OR IGNORE INTO tasks (id, title, description, status, due_date, assigned_to, project_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            tasks,
        )

        # Insert sample marketing campaigns data
        marketing_campaigns = [
            (
                1,
                "Spring Promotion",
                "2024-03-01",
                "2024-04-15",
                15000.00,
                "New Customers",
                "Email",
                "completed",
                250,
                0.12,
            ),
            (
                2,
                "Social Media Blitz",
                "2024-04-01",
                "2024-05-31",
                25000.00,
                "18-35 Age Group",
                "Social Media",
                "active",
                420,
                0.08,
            ),
            (
                3,
                "Product Launch",
                "2024-05-15",
                "2024-07-15",
                40000.00,
                "Existing Customers",
                "Multi-Channel",
                "planned",
                0,
                0.0,
            ),
            (
                4,
                "Holiday Season",
                "2024-11-01",
                "2024-12-31",
                35000.00,
                "All Segments",
                "Multi-Channel",
                "planned",
                0,
                0.0,
            ),
        ]
        cursor.executemany(
            """
        INSERT OR IGNORE INTO marketing_campaigns (id, name, start_date, end_date, budget, target_audience, channel, status, lead_count, conversion_rate)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            marketing_campaigns,
        )

        # Insert sample leads data
        leads = [
            (
                1,
                "Brian Wilson",
                "brian@example.com",
                "555-123-4567",
                "Website",
                "qualified",
                "2024-03-05",
                1,
            ),
            (
                2,
                "Linda Miller",
                "linda@example.com",
                "555-234-5678",
                "Email",
                "contacted",
                "2024-03-10",
                1,
            ),
            (
                3,
                "Paul Harris",
                "paul@example.com",
                "555-345-6789",
                "Social Media",
                "new",
                "2024-04-02",
                2,
            ),
            (
                4,
                "Nancy Adams",
                "nancy@example.com",
                "555-456-7890",
                "Referral",
                "qualified",
                "2024-03-15",
                1,
            ),
            (
                5,
                "George Clark",
                "george@example.com",
                "555-567-8901",
                "Social Media",
                "contacted",
                "2024-04-05",
                2,
            ),
            (
                6,
                "Olivia Martin",
                "olivia@example.com",
                "555-678-9012",
                "Social Media",
                "new",
                "2024-04-08",
                2,
            ),
        ]
        cursor.executemany(
            """
        INSERT OR IGNORE INTO leads (id, name, email, phone, source, status, date_acquired, campaign_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            leads,
        )

        # Insert sample construction sites data
        construction_sites = [
            (
                1,
                "Main Office Renovation",
                "123 Business St",
                3,
                "2024-01-15",
                "in_progress",
                9,
                150000.00,
            ),
            (
                2,
                "New Warehouse Project",
                "456 Industrial Ave",
                6,
                "2024-06-01",
                "planning",
                5,
                500000.00,
            ),
        ]
        cursor.executemany(
            """
        INSERT OR IGNORE INTO construction_sites (id, name, location, project_id, start_date, status, site_manager_id, budget)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            construction_sites,
        )

        # Insert sample materials data
        materials = [
            (1, "Lumber", "board feet", 500.0, 5.75, "ABC Supplies", 100.0),
            (2, "Concrete", "cubic yards", 75.0, 125.00, "XYZ Materials", 20.0),
            (3, "Steel Beams", "pieces", 40.0, 350.00, "Steel Inc", 15.0),
            (4, "Paint", "gallons", 25.0, 35.00, "Paint Depot", 10.0),
            (5, "Roofing Shingles", "bundles", 90.0, 45.00, "Roofing Supply Co", 30.0),
            (6, "Glass Panels", "panels", 15.0, 275.00, "Glass Works", 5.0),
        ]
        cursor.executemany(
            """
        INSERT OR IGNORE INTO materials (id, name, unit, quantity, price_per_unit, supplier, reorder_level)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            materials,
        )

        # Insert sample KPIs data
        kpis = [
            (1, "Revenue", 22000.00, 25000.00, "Q1 2024", "Company"),
            (2, "Customer Satisfaction", 4.2, 4.5, "Q1 2024", "Company"),
            (3, "New Customers", 25, 30, "Q1 2024", "Sales"),
            (4, "Project Completion Rate", 0.85, 0.9, "Q1 2024", "Engineering"),
            (5, "Marketing ROI", 2.8, 3.0, "Q1 2024", "Marketing"),
            (6, "Construction Safety Rating", 9.5, 9.8, "Q1 2024", "Construction"),
        ]
        cursor.executemany(
            """
        INSERT OR IGNORE INTO kpis (id, name, value, target, period, department)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
            kpis,
        )

        # Insert sample department performance data
        department_performance = [
            (1, "Executive", 4.8, "Q1 2024", "Excellent leadership performance"),
            (
                2,
                "Sales",
                4.2,
                "Q1 2024",
                "Exceeded sales targets, room for improvement in lead conversion",
            ),
            (3, "Marketing", 4.5, "Q1 2024", "Successful campaign launches, good ROI"),
            (
                4,
                "Engineering",
                4.0,
                "Q1 2024",
                "Met deadlines, some quality issues to address",
            ),
            (
                5,
                "Construction",
                4.6,
                "Q1 2024",
                "Projects on budget, good safety record",
            ),
            (
                6,
                "HR",
                4.3,
                "Q1 2024",
                "Improved employee satisfaction, reduced turnover",
            ),
        ]
        cursor.executemany(
            """
        INSERT OR IGNORE INTO department_performance (id, department, performance_score, period, details)
        VALUES (?, ?, ?, ?, ?)
        """,
            department_performance,
        )

        conn.commit()
        print("Sample data inserted successfully!")


def main():
    """Run the database initialization process."""
    print("Database Initialization Script")
    print("=" * 30)

    create_tables()
    insert_sample_data()

    print("\nDatabase initialization complete!")


if __name__ == "__main__":
    main()
