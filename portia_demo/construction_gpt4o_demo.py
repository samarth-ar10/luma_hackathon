#!/usr/bin/env python3
"""
ConstructComm AI Demo - Shows how SQL + GPT-4o could be used for construction company data
"""
import os
import sqlite3
from contextlib import contextmanager
from dotenv import load_dotenv

# Import the direct LLM query function
from sql_demo.portia_direct import query_llm

# Load environment variables
load_dotenv()

# Database setup
DB_PATH = "construction_data.db"


@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def execute_sql_query(query):
    """Execute a SQL query and return the results."""
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


def display_results(data, title=None):
    """Format and display results in a readable table."""
    if not data:
        print("No data to display.")
        return

    if title:
        print(f"\n{title}")
        print("-" * 80)

    # Get all column names from the data
    columns = list(data[0].keys())

    # Calculate column widths based on content
    col_widths = {}
    for col in columns:
        col_width = len(col) + 2  # Minimum width based on column name
        for row in data:
            value_width = len(str(row[col])) + 2
            col_width = max(col_width, value_width)
        col_widths[col] = min(col_width, 40)  # Cap width at 40 chars

    # Print header
    header = "".join(f"{col:<{col_widths[col]}}" for col in columns)
    print(header)
    print("-" * sum(col_widths.values()))

    # Print rows
    for row in data:
        row_str = ""
        for col in columns:
            value = str(row[col])
            # Truncate long values
            if len(value) > col_widths[col] - 2:
                value = value[: col_widths[col] - 5] + "..."
            row_str += f"{value:<{col_widths[col]}}"
        print(row_str)


def setup_database():
    """Create and populate the database with sample construction data."""
    queries = [
        # Create tables
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            status TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT,
            budget REAL NOT NULL,
            manager_id INTEGER,
            FOREIGN KEY (manager_id) REFERENCES users(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            project_id INTEGER,
            name TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL,
            priority TEXT NOT NULL,
            assigned_to INTEGER,
            due_date TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (assigned_to) REFERENCES users(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit TEXT NOT NULL,
            unit_price REAL NOT NULL,
            project_id INTEGER,
            delivery_date TEXT,
            status TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS safety_reports (
            id INTEGER PRIMARY KEY,
            project_id INTEGER,
            report_date TEXT NOT NULL,
            inspector_id INTEGER,
            incident_count INTEGER,
            description TEXT,
            compliance_status TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (inspector_id) REFERENCES users(id)
        )
        """,
        # Insert sample data - Users
        """
        INSERT OR IGNORE INTO users (id, name, role, email, phone) VALUES
        (1, 'John Smith', 'CEO', 'john@constructco.com', '555-123-4567'),
        (2, 'Sarah Johnson', 'Project Manager', 'sarah@constructco.com', '555-234-5678'),
        (3, 'Mike Chen', 'Engineer', 'mike@constructco.com', '555-345-6789'),
        (4, 'Emily Rodriguez', 'Safety Manager', 'emily@constructco.com', '555-456-7890'),
        (5, 'David Lee', 'Foreman', 'david@constructco.com', '555-567-8901')
        """,
        # Projects
        """
        INSERT OR IGNORE INTO projects (id, name, status, start_date, end_date, budget, manager_id) VALUES
        (1, 'Downtown Office Tower', 'In Progress', '2024-01-15', '2025-06-30', 25000000.00, 2),
        (2, 'Riverside Apartments', 'Planning', '2024-05-01', '2026-01-15', 18500000.00, 2),
        (3, 'Central Park Renovation', 'In Progress', '2024-03-10', '2024-09-15', 4200000.00, 2)
        """,
        # Tasks
        """
        INSERT OR IGNORE INTO tasks (id, project_id, name, description, status, priority, assigned_to, due_date) VALUES
        (1, 1, 'Foundation Inspection', 'Verify foundation meets specifications', 'Completed', 'High', 3, '2024-02-15'),
        (2, 1, 'Steel Framework Installation', 'Install main steel framework for floors 1-10', 'In Progress', 'High', 5, '2024-05-30'),
        (3, 1, 'Electrical Wiring - Phase 1', 'Complete electrical wiring for floors 1-5', 'Pending', 'Medium', 3, '2024-06-15'),
        (4, 3, 'Tree Removal', 'Remove designated trees and prepare for replanting', 'In Progress', 'Medium', 5, '2024-04-15'),
        (5, 3, 'Pathway Construction', 'Construct new walking paths according to design', 'Pending', 'Medium', 5, '2024-05-30')
        """,
        # Materials
        """
        INSERT OR IGNORE INTO materials (id, name, quantity, unit, unit_price, project_id, delivery_date, status) VALUES
        (1, 'Cement', 1500, 'bags', 12.50, 1, '2024-01-20', 'Delivered'),
        (2, 'Steel Rebar', 5000, 'rods', 25.75, 1, '2024-02-10', 'Delivered'),
        (3, 'Glass Panels', 300, 'panels', 450.00, 1, '2024-07-15', 'Ordered'),
        (4, 'Electrical Wiring', 25000, 'feet', 0.85, 1, '2024-05-25', 'Ordered'),
        (5, 'Pavers', 5000, 'pieces', 3.25, 3, '2024-04-20', 'Delivered'),
        (6, 'Park Benches', 35, 'units', 750.00, 3, '2024-06-10', 'Ordered')
        """,
        # Safety Reports
        """
        INSERT OR IGNORE INTO safety_reports (id, project_id, report_date, inspector_id, incident_count, description, compliance_status) VALUES
        (1, 1, '2024-02-20', 4, 0, 'All safety protocols properly followed.', 'Compliant'),
        (2, 1, '2024-03-15', 4, 1, 'Minor incident: worker failed to wear proper PPE. Issue addressed on site.', 'Warning Issued'),
        (3, 1, '2024-04-10', 4, 0, 'Improved safety measure implementation since last inspection.', 'Compliant'),
        (4, 3, '2024-03-25', 4, 0, 'All safety measures in place for park renovation.', 'Compliant')
        """,
    ]

    for query in queries:
        result = execute_sql_query(query)
        if not result["success"]:
            print(f"Error executing query: {result['error']}")
            print(f"Query: {query}")

    print("Database setup completed successfully.")


def run_sample_queries():
    """Run sample queries to demonstrate the system."""
    # Role-based queries
    ceo_query = """
    SELECT p.name as project_name, p.status, p.budget, 
           COUNT(DISTINCT t.id) as total_tasks,
           SUM(CASE WHEN t.status = 'Completed' THEN 1 ELSE 0 END) as completed_tasks,
           COUNT(DISTINCT sr.id) as safety_reports,
           SUM(sr.incident_count) as total_incidents
    FROM projects p
    LEFT JOIN tasks t ON p.id = t.project_id
    LEFT JOIN safety_reports sr ON p.id = sr.project_id
    GROUP BY p.id
    """

    pm_query = """
    SELECT t.name as task_name, t.status, t.priority, u.name as assigned_to, t.due_date
    FROM tasks t
    JOIN users u ON t.assigned_to = u.id
    WHERE t.project_id = 1
    ORDER BY 
        CASE t.priority 
            WHEN 'High' THEN 1 
            WHEN 'Medium' THEN 2 
            WHEN 'Low' THEN 3 
        END,
        t.due_date
    """

    safety_query = """
    SELECT sr.report_date, p.name as project_name, sr.incident_count, sr.compliance_status
    FROM safety_reports sr
    JOIN projects p ON sr.project_id = p.id
    ORDER BY sr.report_date DESC
    """

    materials_query = """
    SELECT m.name, m.quantity, m.unit, m.unit_price, m.quantity * m.unit_price as total_cost,
           m.delivery_date, m.status, p.name as project_name
    FROM materials m
    JOIN projects p ON m.project_id = p.id
    ORDER BY m.status, m.delivery_date
    """

    # Run and display query results
    print("\n>> CEO Dashboard:")
    ceo_results = execute_sql_query(ceo_query)
    if ceo_results["success"]:
        display_results(ceo_results["results"], "Project Overview")

    print("\n>> Project Manager View:")
    pm_results = execute_sql_query(pm_query)
    if pm_results["success"]:
        display_results(pm_results["results"], "Tasks for Downtown Office Tower")

    print("\n>> Safety Manager View:")
    safety_results = execute_sql_query(safety_query)
    if safety_results["success"]:
        display_results(safety_results["results"], "Safety Reports")

    print("\n>> Logistics View:")
    materials_results = execute_sql_query(materials_query)
    if materials_results["success"]:
        display_results(materials_results["results"], "Materials Tracking")

    return {
        "ceo": ceo_results["results"] if ceo_results["success"] else None,
        "pm": pm_results["results"] if pm_results["success"] else None,
        "safety": safety_results["results"] if safety_results["success"] else None,
        "materials": (
            materials_results["results"] if materials_results["success"] else None
        ),
    }


def ai_analysis_demo(query_results):
    """Demonstrate how GPT-4o can analyze construction data."""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        return

    # 1. CEO Analysis - Project Overview
    ceo_prompt = f"""
    As the CEO of a construction company, analyze this project overview data:
    
    {query_results['ceo']}
    
    Please provide:
    1. A brief executive summary of our project portfolio
    2. Which project(s) require my attention based on task completion and safety incidents?
    3. What key financial insights can you derive from the budget information?
    """

    print("\n>> CEO Data Analysis with GPT-4o:")
    print("Sending project overview to GPT-4o for executive insights...")
    ceo_response = query_llm(openai_api_key, ceo_prompt)
    print("\nCEO Analysis:")
    print("-" * 80)
    print(ceo_response)
    print("-" * 80)

    # 2. Project Manager Analysis - Task Prioritization
    pm_prompt = f"""
    As a Project Manager for the Downtown Office Tower project, analyze these task data:
    
    {query_results['pm']}
    
    Please provide:
    1. A summary of the current task status
    2. Which tasks should be prioritized based on status, priority, and due date?
    3. Are there any resource allocation concerns based on task assignments?
    """

    print("\n>> Project Manager Task Analysis with GPT-4o:")
    print("Sending task data to GPT-4o for project management insights...")
    pm_response = query_llm(openai_api_key, pm_prompt)
    print("\nProject Manager Analysis:")
    print("-" * 80)
    print(pm_response)
    print("-" * 80)

    # 3. Materials & Budget Analysis
    materials_prompt = f"""
    As a Construction Cost Analyst, review this materials data:
    
    {query_results['materials']}
    
    Please provide:
    1. A breakdown of current material expenses by project
    2. Which materials represent the highest cost items?
    3. Are there any delivery timeline concerns based on the status and dates?
    4. What SQL query would you run to identify all materials that are ordered but not yet delivered?
    """

    print("\n>> Materials & Budget Analysis with GPT-4o:")
    print("Sending materials data to GPT-4o for cost analysis...")
    materials_response = query_llm(openai_api_key, materials_prompt)
    print("\nMaterials Analysis:")
    print("-" * 80)
    print(materials_response)
    print("-" * 80)


def main():
    """Run the ConstructComm AI demonstration."""
    print("=" * 80)
    print("ConstructComm AI Demo - SQL + GPT-4o for Construction Management")
    print("=" * 80)

    # Step 1: Set up the database with sample data
    print("\n>> Step 1: Setting up construction database")
    setup_database()

    # Step 2: Run sample role-based queries
    print("\n>> Step 2: Demonstrating role-based data views")
    query_results = run_sample_queries()

    # Step 3: Use GPT-4o to analyze the construction data
    print("\n>> Step 3: GPT-4o analysis of construction data")
    ai_analysis_demo(query_results)

    print("\nDemo complete!")


if __name__ == "__main__":
    main()
