#!/usr/bin/env python3
"""
Script to upload demo construction data to SQLite database and retrieve it
"""

import sqlite3
import logging
from datetime import datetime, timedelta
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Sample construction data - using existing schema
USERS = [
    {
        "id": 1,
        "name": "John Smith",
        "role": "CEO",
        "email": "john@constructco.com",
        "phone": "555-123-4567",
    },
    {
        "id": 2,
        "name": "Sarah Johnson",
        "role": "Project Manager",
        "email": "sarah@constructco.com",
        "phone": "555-234-5678",
    },
    {
        "id": 3,
        "name": "Mike Chen",
        "role": "Engineer",
        "email": "mike@constructco.com",
        "phone": "555-345-6789",
    },
    {
        "id": 4,
        "name": "Lisa Wong",
        "role": "Safety Manager",
        "email": "lisa@constructco.com",
        "phone": "555-456-7890",
    },
    {
        "id": 5,
        "name": "David Brown",
        "role": "Foreman",
        "email": "david@constructco.com",
        "phone": "555-567-8901",
    },
]

PROJECTS = [
    {
        "id": 1,
        "name": "Downtown Office Tower",
        "status": "In Progress",
        "start_date": "2024-01-15",
        "end_date": "2025-06-30",
        "budget": 25000000.00,
        "manager_id": 2,
    },
    {
        "id": 2,
        "name": "Riverside Apartments",
        "status": "Planning",
        "start_date": "2024-05-01",
        "end_date": "2026-01-15",
        "budget": 18500000.00,
        "manager_id": 2,
    },
    {
        "id": 3,
        "name": "Central Park Renovation",
        "status": "In Progress",
        "start_date": "2024-03-10",
        "end_date": "2024-09-15",
        "budget": 4200000.00,
        "manager_id": 2,
    },
    {
        "id": 4,
        "name": "Harbor Bridge Repairs",
        "status": "Pending Approval",
        "start_date": "2024-06-15",
        "end_date": "2024-12-30",
        "budget": 7500000.00,
        "manager_id": 2,
    },
    {
        "id": 5,
        "name": "School Gymnasium",
        "status": "Completed",
        "start_date": "2023-09-01",
        "end_date": "2024-02-28",
        "budget": 3800000.00,
        "manager_id": 2,
    },
]

TASKS = [
    {
        "id": 1,
        "project_id": 1,
        "name": "Foundation Inspection",
        "description": "Verify foundation meets specifications",
        "status": "Completed",
        "priority": "High",
        "assigned_to": 3,
        "due_date": "2024-02-15",
    },
    {
        "id": 2,
        "project_id": 1,
        "name": "Steel Framework Installation",
        "description": "Install main steel framework for floors 1-10",
        "status": "In Progress",
        "priority": "High",
        "assigned_to": 5,
        "due_date": "2024-05-30",
    },
    {
        "id": 3,
        "project_id": 1,
        "name": "Electrical Wiring - Phase 1",
        "description": "Complete electrical wiring for floors 1-5",
        "status": "Pending",
        "priority": "Medium",
        "assigned_to": 3,
        "due_date": "2024-06-15",
    },
    {
        "id": 4,
        "project_id": 2,
        "name": "Site Preparation",
        "description": "Clear and prepare construction site",
        "status": "Pending",
        "priority": "High",
        "assigned_to": 5,
        "due_date": "2024-05-15",
    },
    {
        "id": 5,
        "project_id": 3,
        "name": "Landscaping",
        "description": "Plant trees and install irrigation",
        "status": "In Progress",
        "priority": "Medium",
        "assigned_to": 3,
        "due_date": "2024-05-30",
    },
    {
        "id": 6,
        "project_id": 1,
        "name": "Glass Facade Installation",
        "description": "Install exterior glass panels on floors 1-5",
        "status": "Pending",
        "priority": "High",
        "assigned_to": 5,
        "due_date": "2024-07-30",
    },
    {
        "id": 7,
        "project_id": 3,
        "name": "Playground Equipment",
        "description": "Install new playground equipment",
        "status": "Pending",
        "priority": "Low",
        "assigned_to": 5,
        "due_date": "2024-06-30",
    },
]

MATERIALS = [
    {
        "id": 1,
        "name": "Cement",
        "quantity": 1500,
        "unit": "bags",
        "unit_price": 12.50,
        "project_id": 1,
        "delivery_date": "2024-01-20",
        "status": "Delivered",
    },
    {
        "id": 2,
        "name": "Steel Rebar",
        "quantity": 5000,
        "unit": "rods",
        "unit_price": 25.75,
        "project_id": 1,
        "delivery_date": "2024-02-10",
        "status": "Delivered",
    },
    {
        "id": 3,
        "name": "Glass Panels",
        "quantity": 300,
        "unit": "panels",
        "unit_price": 450.00,
        "project_id": 1,
        "delivery_date": "2024-07-15",
        "status": "Ordered",
    },
    {
        "id": 4,
        "name": "Copper Wiring",
        "quantity": 10000,
        "unit": "feet",
        "unit_price": 2.25,
        "project_id": 1,
        "delivery_date": "2024-05-01",
        "status": "Delivered",
    },
    {
        "id": 5,
        "name": "Lumber",
        "quantity": 7500,
        "unit": "board feet",
        "unit_price": 3.50,
        "project_id": 2,
        "delivery_date": "2024-05-10",
        "status": "Ordered",
    },
    {
        "id": 6,
        "name": "HVAC Systems",
        "quantity": 15,
        "unit": "units",
        "unit_price": 4250.00,
        "project_id": 1,
        "delivery_date": "2024-08-15",
        "status": "Pending",
    },
    {
        "id": 7,
        "name": "Concrete Mix",
        "quantity": 500,
        "unit": "yards",
        "unit_price": 125.00,
        "project_id": 3,
        "delivery_date": "2024-03-20",
        "status": "Delivered",
    },
]

SAFETY_REPORTS = [
    {
        "id": 1,
        "project_id": 1,
        "report_date": "2024-02-20",
        "inspector_id": 4,
        "incident_count": 0,
        "description": "All safety protocols properly followed.",
        "compliance_status": "Compliant",
    },
    {
        "id": 2,
        "project_id": 1,
        "report_date": "2024-03-15",
        "inspector_id": 4,
        "incident_count": 1,
        "description": "Minor incident: worker failed to wear proper PPE. Issue addressed on site.",
        "compliance_status": "Warning Issued",
    },
    {
        "id": 3,
        "project_id": 1,
        "report_date": "2024-04-10",
        "inspector_id": 4,
        "incident_count": 0,
        "description": "Improved safety measure implementation since last inspection.",
        "compliance_status": "Compliant",
    },
    {
        "id": 4,
        "project_id": 3,
        "report_date": "2024-04-05",
        "inspector_id": 4,
        "incident_count": 0,
        "description": "All safety requirements met for public park renovation.",
        "compliance_status": "Compliant",
    },
    {
        "id": 5,
        "project_id": 2,
        "report_date": "2024-05-03",
        "inspector_id": 4,
        "incident_count": 2,
        "description": "Two issues found: inadequate fencing and missing signage. To be fixed by next week.",
        "compliance_status": "Warning Issued",
    },
]


def insert_data(conn):
    """Insert sample data into the database"""
    cursor = conn.cursor()

    # Clear existing data
    tables = ["safety_reports", "materials", "tasks", "projects", "users"]
    for table in tables:
        cursor.execute(f"DELETE FROM {table}")

    # Insert users
    for user in USERS:
        cursor.execute(
            """
        INSERT INTO users
        (id, name, role, email, phone)
        VALUES (?, ?, ?, ?, ?)
        """,
            (user["id"], user["name"], user["role"], user["email"], user["phone"]),
        )

    # Insert projects
    for project in PROJECTS:
        cursor.execute(
            """
        INSERT INTO projects
        (id, name, status, start_date, end_date, budget, manager_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                project["id"],
                project["name"],
                project["status"],
                project["start_date"],
                project["end_date"],
                project["budget"],
                project["manager_id"],
            ),
        )

    # Insert tasks
    for task in TASKS:
        cursor.execute(
            """
        INSERT INTO tasks
        (id, project_id, name, description, status, priority, assigned_to, due_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                task["id"],
                task["project_id"],
                task["name"],
                task["description"],
                task["status"],
                task["priority"],
                task["assigned_to"],
                task["due_date"],
            ),
        )

    # Insert materials
    for material in MATERIALS:
        cursor.execute(
            """
        INSERT INTO materials
        (id, name, quantity, unit, unit_price, project_id, delivery_date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                material["id"],
                material["name"],
                material["quantity"],
                material["unit"],
                material["unit_price"],
                material["project_id"],
                material["delivery_date"],
                material["status"],
            ),
        )

    # Insert safety reports
    for report in SAFETY_REPORTS:
        cursor.execute(
            """
        INSERT INTO safety_reports
        (id, project_id, report_date, inspector_id, incident_count, description, compliance_status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                report["id"],
                report["project_id"],
                report["report_date"],
                report["inspector_id"],
                report["incident_count"],
                report["description"],
                report["compliance_status"],
            ),
        )

    conn.commit()
    logger.info("Sample data inserted successfully")


def retrieve_data(conn):
    """Retrieve and display data from the database with formatting for better readability"""
    cursor = conn.cursor()

    # Projects summary with manager name
    logger.info(
        "\n══════════════════════════════ PROJECTS SUMMARY ══════════════════════════════"
    )
    cursor.execute(
        """
    SELECT p.id, p.name, p.status, p.start_date, p.end_date, p.budget, u.name
    FROM projects p
    JOIN users u ON p.manager_id = u.id
    ORDER BY p.start_date
    """
    )
    projects = cursor.fetchall()

    for project in projects:
        logger.info(f"PROJECT #{project[0]}: {project[1]}")
        logger.info(f"  Status: {project[2]}")
        logger.info(f"  Timeline: {project[3]} to {project[4]}")
        logger.info(f"  Budget: ${project[5]:,.2f}")
        logger.info(f"  Manager: {project[6]}")
        logger.info("  " + "─" * 70)

    # Tasks by project status
    logger.info(
        "\n══════════════════════════════ TASK STATUS ══════════════════════════════"
    )
    cursor.execute(
        """
    SELECT 
        p.name as project_name,
        SUM(CASE WHEN t.status = 'Completed' THEN 1 ELSE 0 END) as completed,
        SUM(CASE WHEN t.status = 'In Progress' THEN 1 ELSE 0 END) as in_progress,
        SUM(CASE WHEN t.status = 'Pending' THEN 1 ELSE 0 END) as pending,
        COUNT(*) as total
    FROM tasks t
    JOIN projects p ON t.project_id = p.id
    GROUP BY p.name
    ORDER BY p.name
    """
    )
    task_stats = cursor.fetchall()

    for stat in task_stats:
        project, completed, in_progress, pending, total = stat
        logger.info(f"Project: {project}")
        logger.info(
            f"  Tasks: {total} total ({completed} completed, {in_progress} in progress, {pending} pending)"
        )

        # Calculate completion percentage
        completion = (completed / total) * 100 if total > 0 else 0
        logger.info(f"  Completion: {completion:.1f}%")
        logger.info("  " + "─" * 70)

    # Materials cost by project
    logger.info(
        "\n══════════════════════════════ MATERIALS COST ══════════════════════════════"
    )
    cursor.execute(
        """
    SELECT 
        p.name as project_name,
        SUM(m.quantity * m.unit_price) as total_cost,
        COUNT(*) as material_count
    FROM materials m
    JOIN projects p ON m.project_id = p.id
    GROUP BY p.name
    ORDER BY total_cost DESC
    """
    )
    material_costs = cursor.fetchall()

    for cost_data in material_costs:
        project, total_cost, count = cost_data
        logger.info(f"Project: {project}")
        logger.info(f"  Materials: {count} items")
        logger.info(f"  Total Cost: ${total_cost:,.2f}")
        logger.info("  " + "─" * 70)

    # Most recent safety reports
    logger.info(
        "\n══════════════════════════════ RECENT SAFETY REPORTS ══════════════════════════════"
    )
    cursor.execute(
        """
    SELECT 
        s.report_date, 
        p.name, 
        u.name,
        s.incident_count, 
        s.compliance_status,
        s.description
    FROM safety_reports s
    JOIN projects p ON s.project_id = p.id
    JOIN users u ON s.inspector_id = u.id
    ORDER BY s.report_date DESC
    LIMIT 5
    """
    )
    reports = cursor.fetchall()

    for report in reports:
        date, project, inspector, incidents, status, desc = report
        logger.info(f"Date: {date} - Project: {project}")
        logger.info(f"  Inspector: {inspector}")
        logger.info(f"  Status: {status} ({incidents} incidents)")
        if desc:
            logger.info(f"  Notes: {desc}")
        logger.info("  " + "─" * 70)


def export_data_for_frontend(conn, export_dir="portia_demo/webui/src/data"):
    """Export data as JSON files for the frontend"""
    import json

    # Create directory if it doesn't exist
    os.makedirs(export_dir, exist_ok=True)

    cursor = conn.cursor()

    # Export projects
    cursor.execute(
        """
    SELECT p.*, u.name as manager_name
    FROM projects p
    JOIN users u ON p.manager_id = u.id
    """
    )

    # Get column names
    columns = [description[0] for description in cursor.description]

    # Fetch results and convert to dictionary
    projects_data = []
    for row in cursor.fetchall():
        projects_data.append(dict(zip(columns, row)))

    # Write to JSON file
    with open(os.path.join(export_dir, "projects.json"), "w") as f:
        json.dump(projects_data, f, indent=2)

    # Export tasks with associated project and assignee information
    cursor.execute(
        """
    SELECT 
        t.*,
        p.name as project_name,
        u.name as assignee_name
    FROM tasks t
    JOIN projects p ON t.project_id = p.id
    LEFT JOIN users u ON t.assigned_to = u.id
    """
    )

    columns = [description[0] for description in cursor.description]
    tasks_data = []
    for row in cursor.fetchall():
        tasks_data.append(dict(zip(columns, row)))

    with open(os.path.join(export_dir, "tasks.json"), "w") as f:
        json.dump(tasks_data, f, indent=2)

    # Export materials with project info
    cursor.execute(
        """
    SELECT 
        m.*,
        p.name as project_name
    FROM materials m
    JOIN projects p ON m.project_id = p.id
    """
    )

    columns = [description[0] for description in cursor.description]
    materials_data = []
    for row in cursor.fetchall():
        materials_data.append(dict(zip(columns, row)))

    with open(os.path.join(export_dir, "materials.json"), "w") as f:
        json.dump(materials_data, f, indent=2)

    # Export safety reports with project and inspector info
    cursor.execute(
        """
    SELECT 
        s.*,
        p.name as project_name,
        u.name as inspector_name
    FROM safety_reports s
    JOIN projects p ON s.project_id = p.id
    JOIN users u ON s.inspector_id = u.id
    """
    )

    columns = [description[0] for description in cursor.description]
    safety_data = []
    for row in cursor.fetchall():
        safety_data.append(dict(zip(columns, row)))

    with open(os.path.join(export_dir, "safety_reports.json"), "w") as f:
        json.dump(safety_data, f, indent=2)

    # Export users
    cursor.execute("SELECT * FROM users")

    columns = [description[0] for description in cursor.description]
    users_data = []
    for row in cursor.fetchall():
        users_data.append(dict(zip(columns, row)))

    with open(os.path.join(export_dir, "users.json"), "w") as f:
        json.dump(users_data, f, indent=2)

    logger.info(f"Data exported to JSON files in {export_dir}")


def main():
    """Main function to upload data, retrieve it, and export for frontend"""
    db_path = "portia_demo/construction_data.db"

    try:
        # Make sure the database exists before connecting
        if not os.path.exists(db_path):
            logger.error(f"Database file doesn't exist: {db_path}")
            return

        # Connect to database
        conn = sqlite3.connect(db_path)
        logger.info(f"Connected to database: {db_path}")

        # Insert data
        insert_data(conn)

        # Retrieve and display data
        retrieve_data(conn)

        # Export data for frontend
        export_data_for_frontend(conn)

        # Close connection
        conn.close()
        logger.info("Database connection closed")

    except sqlite3.Error as e:
        logger.error(f"SQLite error: {e}")
    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == "__main__":
    main()
