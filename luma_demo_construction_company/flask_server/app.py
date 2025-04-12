from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from dotenv import load_dotenv

from queen_agent import QueenAgent
from worker_agent import WorkerAgent
from db_setup import setup_database
from db_utils import get_db_connection

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Initialize database during startup
try:
    setup_database()
    print("Database setup complete")
except Exception as e:
    print(f"Error setting up database: {e}")

# Initialize Queen Agent
queen = QueenAgent()

# Dictionary to store worker agents
worker_agents = {}


@app.route("/api/design-layout", methods=["POST"])
def design_layout():
    """
    API endpoint to design a layout for a specific company and role
    """
    data = request.json
    company_type = data.get("company_type", "construction")
    role_type = data.get("role_type", "project_manager")
    constraints = data.get("constraints", {})

    layout_design = queen.design_layout(company_type, role_type, constraints)
    return jsonify(layout_design)


@app.route("/api/assign-workers", methods=["POST"])
def assign_workers():
    """
    API endpoint to assign worker agents to the layout tiles
    """
    data = request.json
    layout_design = data.get("layout_design", {})

    # Use database schema instead of passing data_source directly
    worker_tasks = queen.assign_worker_tasks(layout_design)

    # Create worker agents for each tile
    for tile_id, worker_task in worker_tasks.items():
        worker_agents[tile_id] = WorkerAgent(tile_id, worker_task)

    return jsonify(worker_tasks)


@app.route("/api/generate-visualizations", methods=["POST"])
def generate_visualizations():
    """
    API endpoint to generate all visualizations for the dashboard
    """
    data = request.json
    layout_design = data.get("layout_design", {})
    visualization_preference = data.get("visualization_preference", "balanced")

    visualizations = {}

    for tile_id, worker in worker_agents.items():
        # Worker agents will fetch data from the database
        # Pass visualization preference to worker agent
        visualization = worker.generate_visualization(
            visualization_preference=visualization_preference
        )
        visualizations[tile_id] = visualization

    return jsonify(visualizations)


@app.route("/api/update-visualization", methods=["POST"])
def update_visualization():
    """
    API endpoint to update a specific visualization
    """
    data = request.json
    tile_id = data.get("tile_id")
    feedback = data.get("feedback")
    visualization_preference = data.get("visualization_preference", "balanced")

    if tile_id not in worker_agents:
        return jsonify({"error": f"Worker agent for tile {tile_id} not found"}), 404

    # Worker agent will fetch updated data from the database
    visualization = worker_agents[tile_id].update_visualization(
        feedback=feedback, visualization_preference=visualization_preference
    )

    return jsonify(visualization)


@app.route("/api/data/<table_name>", methods=["GET"])
def get_data(table_name):
    """
    API endpoint to get data directly from a specific table
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {table_name}")
        columns = [desc[0] for desc in cur.description]
        data = [dict(zip(columns, row)) for row in cur.fetchall()]
        cur.close()
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/role-data/<role_type>", methods=["GET"])
def get_role_data(role_type):
    """
    API endpoint to get all relevant data for a specific role
    """
    relevant_data = {}

    # Define what data is relevant for each role
    role_data_mapping = {
        "project_manager": ["projects", "tasks", "workers"],
        "construction_worker": ["tasks", "materials", "safety_checklists"],
        "safety_officer": ["safety", "safety_checklists", "projects"],
        "site_supervisor": [
            "projects",
            "equipment",
            "workers",
            "daily_tasks",
            "progress_tracking",
        ],
        "inventory_manager": ["materials", "equipment"],
    }

    # Get data for each relevant table
    tables = role_data_mapping.get(role_type, ["projects"])

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        for table in tables:
            cur.execute(f"SELECT * FROM {table}")
            columns = [desc[0] for desc in cur.description]
            relevant_data[table] = [dict(zip(columns, row)) for row in cur.fetchall()]

        cur.close()
        conn.close()
        return jsonify(relevant_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/all-data", methods=["GET"])
def get_all_data():
    """
    API endpoint to get data from all tables
    """
    all_data = {}
    tables = [
        "projects",
        "tasks",
        "workers",
        "materials",
        "safety",
        "equipment",
        "safety_checklists",
        "daily_tasks",
        "progress_tracking",
    ]

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        for table in tables:
            try:
                cur.execute(f"SELECT * FROM {table}")
                columns = [desc[0] for desc in cur.description]
                all_data[table] = [dict(zip(columns, row)) for row in cur.fetchall()]
            except Exception as e:
                all_data[table] = {
                    "error": f"Error retrieving data from {table}: {str(e)}"
                }

        cur.close()
        conn.close()
        return jsonify(all_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/dashboard-config", methods=["POST"])
def dashboard_config():
    """
    API endpoint to get dashboard layout and tile prioritization based on role
    """
    data = request.json
    role = data.get("role", "project_manager").lower().replace(" ", "_")
    visualization_preference = data.get("visualization_preference", "balanced")

    # Define the prioritization logic for different roles
    role_priorities = {
        "project_manager": {
            "project_overview": 1,
            "task_progress": 2,
            "team_members": 3,
            "project_timeline": 3,
            "progress_tracking": 4,
            "material_inventory": 5,
            "safety_incidents": 4,
            "equipment_status": 6,
            "daily_tasks": 7,
        },
        "ceo": {
            "project_overview": 1,
            "project_timeline": 2,
            "progress_tracking": 3,
            "team_members": 4,
            "safety_incidents": 5,
            "material_inventory": 6,
            "equipment_status": 7,
            "task_progress": 3,
            "daily_tasks": 8,
        },
        "site_supervisor": {
            "task_progress": 1,
            "project_overview": 2,
            "team_members": 3,
            "daily_tasks": 3,
            "progress_tracking": 4,
            "material_inventory": 5,
            "equipment_status": 6,
            "project_timeline": 7,
            "safety_incidents": 4,
        },
        "safety_officer": {
            "safety_incidents": 1,
            "progress_tracking": 2,
            "daily_tasks": 3,
            "project_timeline": 4,
            "project_overview": 5,
            "task_progress": 6,
            "team_members": 7,
            "equipment_status": 8,
            "material_inventory": 9,
        },
        "construction_worker": {
            "task_progress": 1,
            "daily_tasks": 2,
            "material_inventory": 2,
            "safety_incidents": 3,
            "team_members": 4,
            "progress_tracking": 5,
            "equipment_status": 5,
            "project_overview": 6,
            "project_timeline": 7,
        },
        "inventory_manager": {
            "material_inventory": 1,
            "equipment_status": 2,
            "progress_tracking": 4,
            "daily_tasks": 5,
            "project_timeline": 6,
            "project_overview": 7,
            "team_members": 9,
            "task_progress": 8,
            "safety_incidents": 10,
        },
    }

    # Define visualization formats for different preferences
    visualization_formats = {
        "technical": {
            "project_overview": "detailed_table",
            "task_progress": "detailed_table",
            "team_members": "detailed_table",
            "material_inventory": "detailed_table",
            "safety_incidents": "detailed_table",
            "equipment_status": "detailed_table",
            "project_timeline": "timeline_with_details",
            "daily_tasks": "detailed_table",
            "progress_tracking": "detailed_table",
        },
        "balanced": {
            "project_overview": "summary_table",
            "task_progress": "bar_chart",
            "team_members": "summary_table",
            "material_inventory": "summary_table",
            "safety_incidents": "summary_table",
            "equipment_status": "summary_table",
            "project_timeline": "timeline",
            "daily_tasks": "summary_table",
            "progress_tracking": "bar_chart",
        },
        "non_technical": {
            "project_overview": "simplified_bar_chart",
            "task_progress": "simplified_bar_chart",
            "team_members": "simplified_table",
            "material_inventory": "simplified_table",
            "safety_incidents": "simplified_table",
            "equipment_status": "simplified_table",
            "project_timeline": "simplified_timeline",
            "daily_tasks": "simplified_table",
            "progress_tracking": "simplified_bar_chart",
        },
    }

    # Get the priorities for the specified role (with fallback to project_manager)
    priorities = role_priorities.get(role, role_priorities["project_manager"])
    formats = visualization_formats.get(
        visualization_preference, visualization_formats["balanced"]
    )

    response = {
        "role": role,
        "visualization_preference": visualization_preference,
        "tile_configuration": [],
    }

    # Build the response with tile configurations
    for tile_id, priority in priorities.items():
        response["tile_configuration"].append(
            {
                "tile_id": tile_id,
                "priority": priority,
                "visualization_format": formats.get(tile_id, "summary_table"),
            }
        )

    # Sort tiles by priority
    response["tile_configuration"].sort(key=lambda x: x["priority"])

    return jsonify(response)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
