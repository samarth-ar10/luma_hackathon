#!/usr/bin/env python3
"""
Flask Server - API and data provider for the Construction Management Dashboard
Connects to SQLite database and provides endpoints for data retrieval and LLM interactions
"""
import os
import sys
import json
import sqlite3
from contextlib import contextmanager
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Add the parent directory to the Python path to import Portia and SQL tools
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Load environment variables
load_dotenv()

# Try to import Portia components, with graceful fallback if not available
try:
    from portia import Config, LLMModel, LLMProvider, Portia

    PORTIA_AVAILABLE = True
except ImportError:
    print("Warning: Portia module not available. LLM features will be disabled.")
    PORTIA_AVAILABLE = False

# Import Worker AI functionality
try:
    from portia_demo.flask_server.worker_ai import WorkerAIManager

    WORKER_AI_AVAILABLE = True
    # Initialize Worker AI Manager
    worker_ai_manager = WorkerAIManager(
        os.environ.get("CONSTRUCTION_DB_PATH", "portia_demo/construction_data.db")
    )
    print("Worker AI functionality initialized successfully")
except ImportError:
    print(
        "Warning: Worker AI module not available. Worker AI features will be disabled."
    )
    WORKER_AI_AVAILABLE = False

# Initialize Flask app
app = Flask(__name__, static_folder="portia_demo/webui/build")
CORS(app)  # Enable Cross-Origin Resource Sharing

# Configure Portia if available
if PORTIA_AVAILABLE:
    portia_api_key = os.getenv("PORTIA_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if portia_api_key and openai_api_key:
        portia_config = Config.from_default(
            llm_provider=LLMProvider.OPENAI,
            llm_model_name=LLMModel.GPT_4O,
            openai_api_key=openai_api_key,
            portia_api_key=portia_api_key,
        )
        portia = Portia(config=portia_config)
    else:
        print("Warning: API keys for Portia not found in environment variables.")
        PORTIA_AVAILABLE = False

# Database configuration
DB_PATH = os.environ.get("CONSTRUCTION_DB_PATH", "portia_demo/construction_data.db")
print(f"Using database at: {DB_PATH}")


@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def dict_factory(cursor, row):
    """Convert SQLite row to dictionary."""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def execute_query(query, params=None):
    """Execute a SQL query and return the results as a list of dictionaries."""
    with get_db_connection() as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if query.strip().upper().startswith("SELECT"):
                return {"success": True, "results": cursor.fetchall()}
            else:
                conn.commit()
                return {"success": True, "affected_rows": cursor.rowcount}
        except sqlite3.Error as e:
            return {"success": False, "error": str(e)}


# API Routes


@app.route("/api/query", methods=["POST"])
def query_db():
    """Execute a SQL query against the database."""
    data = request.json
    if not data or "sql" not in data:
        return jsonify({"error": "SQL query is required"}), 400

    sql = data["sql"]
    params = data.get("params")

    # For security, prevent certain operations in demo mode
    if any(keyword in sql.upper() for keyword in ["DROP", "DELETE", "TRUNCATE"]):
        return (
            jsonify({"error": "Destructive operations not allowed in demo mode"}),
            403,
        )

    result = execute_query(sql, params)
    return jsonify(result)


@app.route("/api/ask", methods=["POST"])
def ask_llm():
    """Endpoint to query the LLM with a natural language question."""
    if not PORTIA_AVAILABLE:
        return (
            jsonify(
                {"response": "LLM features are disabled. Portia module not available."}
            ),
            503,
        )

    data = request.json
    if not data or "query" not in data:
        return jsonify({"error": "Query is required"}), 400

    try:
        # Use Portia to process the query
        plan_run = portia.run(data["query"])
        response = plan_run.model_dump_json()
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/projects", methods=["GET"])
def get_projects():
    """Get all projects."""
    result = execute_query("SELECT * FROM projects")
    return jsonify(result)


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    """Get all tasks, optionally filtered by project_id."""
    project_id = request.args.get("project_id")

    if project_id:
        result = execute_query(
            "SELECT t.*, p.name as project_name FROM tasks t JOIN projects p ON t.project_id = p.id WHERE t.project_id = ?",
            (project_id,),
        )
    else:
        result = execute_query(
            "SELECT t.*, p.name as project_name FROM tasks t JOIN projects p ON t.project_id = p.id"
        )

    return jsonify(result)


@app.route("/api/materials", methods=["GET"])
def get_materials():
    """Get all materials, optionally filtered by project_id."""
    project_id = request.args.get("project_id")

    if project_id:
        result = execute_query(
            "SELECT m.*, p.name as project_name FROM materials m JOIN projects p ON m.project_id = p.id WHERE m.project_id = ?",
            (project_id,),
        )
    else:
        result = execute_query(
            "SELECT m.*, p.name as project_name FROM materials m JOIN projects p ON m.project_id = p.id"
        )

    return jsonify(result)


@app.route("/api/safety-reports", methods=["GET"])
def get_safety_reports():
    """Get all safety reports, optionally filtered by project_id."""
    project_id = request.args.get("project_id")

    if project_id:
        result = execute_query(
            """
            SELECT s.*, p.name as project_name, u.name as inspector_name 
            FROM safety_reports s 
            JOIN projects p ON s.project_id = p.id
            JOIN users u ON s.inspector_id = u.id
            WHERE s.project_id = ?
            """,
            (project_id,),
        )
    else:
        result = execute_query(
            """
            SELECT s.*, p.name as project_name, u.name as inspector_name 
            FROM safety_reports s 
            JOIN projects p ON s.project_id = p.id
            JOIN users u ON s.inspector_id = u.id
            """
        )

    return jsonify(result)


@app.route("/api/users", methods=["GET"])
def get_users():
    """Get all users."""
    result = execute_query("SELECT * FROM users")
    return jsonify(result)


@app.route("/api/roles/<role>", methods=["GET"])
def get_role_data(role):
    """Get data specific to a role."""
    try:
        # Get all data
        projects = execute_query("SELECT * FROM projects")

        if projects["success"]:
            project_ids = [p["id"] for p in projects["results"]]

            # Filter by role (simplified version)
            if role.lower() == "project-manager":
                # Project managers (Sarah Johnson is ID 2)
                manager_id = 2  # Sarah Johnson
                projects["results"] = [
                    p for p in projects["results"] if p["manager_id"] == manager_id
                ]
                project_ids = [p["id"] for p in projects["results"]]

            # Get related data
            tasks_result = execute_query(
                f"""
                SELECT t.*, p.name as project_name, u.name as assignee_name 
                FROM tasks t 
                JOIN projects p ON t.project_id = p.id
                LEFT JOIN users u ON t.assigned_to = u.id
                WHERE t.project_id IN ({','.join('?' for _ in project_ids)})
                """,
                project_ids,
            )

            materials_result = execute_query(
                f"""
                SELECT m.*, p.name as project_name 
                FROM materials m 
                JOIN projects p ON m.project_id = p.id
                WHERE m.project_id IN ({','.join('?' for _ in project_ids)})
                """,
                project_ids,
            )

            safety_reports_result = execute_query(
                f"""
                SELECT s.*, p.name as project_name, u.name as inspector_name 
                FROM safety_reports s 
                JOIN projects p ON s.project_id = p.id
                JOIN users u ON s.inspector_id = u.id
                WHERE s.project_id IN ({','.join('?' for _ in project_ids)})
                """,
                project_ids,
            )

            return jsonify(
                {
                    "projects": projects["results"],
                    "tasks": tasks_result.get("results", []),
                    "materials": materials_result.get("results", []),
                    "safety_reports": safety_reports_result.get("results", []),
                }
            )
        else:
            return jsonify({"error": "Failed to retrieve project data"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Get statistics for the dashboard."""
    try:
        # Projects
        projects_result = execute_query("SELECT COUNT(*) as total FROM projects")
        projects_in_progress = execute_query(
            "SELECT COUNT(*) as in_progress FROM projects WHERE status = 'In Progress'"
        )

        # Tasks
        tasks_result = execute_query("SELECT COUNT(*) as total FROM tasks")
        tasks_completed = execute_query(
            "SELECT COUNT(*) as completed FROM tasks WHERE status = 'Completed'"
        )

        # Materials
        materials_cost = execute_query(
            "SELECT SUM(quantity * unit_price) as total_cost FROM materials"
        )

        # Safety
        safety_issues = execute_query(
            "SELECT COUNT(*) as issues FROM safety_reports WHERE compliance_status != 'Compliant'"
        )

        # Combine results
        stats = {
            "projects": {
                "total": (
                    projects_result["results"][0]["total"]
                    if projects_result["success"]
                    else 0
                ),
                "in_progress": (
                    projects_in_progress["results"][0]["in_progress"]
                    if projects_in_progress["success"]
                    else 0
                ),
            },
            "tasks": {
                "total": (
                    tasks_result["results"][0]["total"]
                    if tasks_result["success"]
                    else 0
                ),
                "completed": (
                    tasks_completed["results"][0]["completed"]
                    if tasks_completed["success"]
                    else 0
                ),
                "completion_rate": round(
                    (
                        tasks_completed["results"][0]["completed"]
                        / tasks_result["results"][0]["total"]
                    )
                    * 100
                    if tasks_result["success"]
                    and tasks_result["results"][0]["total"] > 0
                    else 0
                ),
            },
            "materials": {
                "total_cost": (
                    materials_cost["results"][0]["total_cost"]
                    if materials_cost["success"]
                    else 0
                )
            },
            "safety": {
                "issues": (
                    safety_issues["results"][0]["issues"]
                    if safety_issues["success"]
                    else 0
                )
            },
        }

        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Tasks CRUD operations
@app.route("/api/tasks", methods=["POST"])
def add_task():
    """Add a new task."""
    data = request.json
    if not data:
        return jsonify({"error": "Task data is required"}), 400

    # Basic validation
    required_fields = [
        "project_id",
        "name",
        "description",
        "status",
        "priority",
        "assigned_to",
        "due_date",
    ]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Field '{field}' is required"}), 400

    # Insert task
    result = execute_query(
        """
        INSERT INTO tasks (project_id, name, description, status, priority, assigned_to, due_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["project_id"],
            data["name"],
            data["description"],
            data["status"],
            data["priority"],
            data["assigned_to"],
            data["due_date"],
        ),
    )

    if result["success"]:
        # Get the newly created task
        new_task_id = execute_query("SELECT last_insert_rowid() as id")["results"][0][
            "id"
        ]
        new_task = execute_query("SELECT * FROM tasks WHERE id = ?", (new_task_id,))[
            "results"
        ][0]
        return jsonify({"success": True, "task": new_task})
    else:
        return jsonify({"error": result["error"]}), 500


@app.route("/api/tasks/<int:task_id>", methods=["PATCH"])
def update_task(task_id):
    """Update a task."""
    data = request.json
    if not data:
        return jsonify({"error": "Task update data is required"}), 400

    # Build update query dynamically based on provided fields
    update_fields = []
    params = []

    for field in [
        "name",
        "description",
        "status",
        "priority",
        "assigned_to",
        "due_date",
    ]:
        if field in data:
            update_fields.append(f"{field} = ?")
            params.append(data[field])

    if not update_fields:
        return jsonify({"error": "No fields to update"}), 400

    # Add task_id to params
    params.append(task_id)

    # Execute update
    result = execute_query(
        f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = ?", params
    )

    if result["success"]:
        # Get the updated task
        updated_task = (
            execute_query("SELECT * FROM tasks WHERE id = ?", (task_id,))["results"][0]
            if execute_query("SELECT * FROM tasks WHERE id = ?", (task_id,))["results"]
            else None
        )

        return jsonify({"success": True, "task": updated_task})
    else:
        return jsonify({"error": result["error"]}), 500


# Worker AI API endpoints
@app.route("/api/worker/roles", methods=["GET"])
def get_worker_ai_roles():
    """Get available Worker AI roles."""
    if not WORKER_AI_AVAILABLE:
        return jsonify({"error": "Worker AI module not available"}), 503

    return jsonify({"roles": worker_ai_manager.get_available_roles()})


@app.route("/api/worker/message", methods=["POST"])
def process_worker_ai_message():
    """Process a message using Worker AI."""
    if not WORKER_AI_AVAILABLE:
        return jsonify({"error": "Worker AI module not available"}), 503

    data = request.json
    if not data or "message" not in data or "role" not in data or "user_id" not in data:
        return jsonify({"error": "Message, role, and user_id are required"}), 400

    # Process the message using Worker AI
    response = worker_ai_manager.process_message(
        user_id=data["user_id"],
        role=data["role"],
        message=data["message"],
        context=data.get("context", {}),
    )

    return jsonify(response)


# Data export routes
@app.route("/api/export/data", methods=["GET"])
def export_data():
    """Export all data as JSON files for frontend use."""
    try:
        data_dir = "portia_demo/webui/public/data"
        os.makedirs(data_dir, exist_ok=True)

        # Get all data
        projects = execute_query(
            "SELECT p.*, u.name as manager_name FROM projects p JOIN users u ON p.manager_id = u.id"
        )
        tasks = execute_query(
            """
            SELECT t.*, p.name as project_name, u.name as assignee_name 
            FROM tasks t 
            JOIN projects p ON t.project_id = p.id
            LEFT JOIN users u ON t.assigned_to = u.id
        """
        )
        materials = execute_query(
            "SELECT m.*, p.name as project_name FROM materials m JOIN projects p ON m.project_id = p.id"
        )
        safety_reports = execute_query(
            """
            SELECT s.*, p.name as project_name, u.name as inspector_name 
            FROM safety_reports s 
            JOIN projects p ON s.project_id = p.id
            JOIN users u ON s.inspector_id = u.id
        """
        )
        users = execute_query("SELECT * FROM users")

        # Write to files
        with open(os.path.join(data_dir, "projects.json"), "w") as f:
            json.dump(projects["results"], f, indent=2)

        with open(os.path.join(data_dir, "tasks.json"), "w") as f:
            json.dump(tasks["results"], f, indent=2)

        with open(os.path.join(data_dir, "materials.json"), "w") as f:
            json.dump(materials["results"], f, indent=2)

        with open(os.path.join(data_dir, "safety_reports.json"), "w") as f:
            json.dump(safety_reports["results"], f, indent=2)

        with open(os.path.join(data_dir, "users.json"), "w") as f:
            json.dump(users["results"], f, indent=2)

        return jsonify(
            {
                "success": True,
                "message": "Data exported successfully",
                "files": [
                    "projects.json",
                    "tasks.json",
                    "materials.json",
                    "safety_reports.json",
                    "users.json",
                ],
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Serve data files directly (with proper CORS headers)
@app.route("/data/<path:filename>")
def serve_data(filename):
    data_dir = os.path.join("portia_demo/webui/public/data")
    response = send_from_directory(data_dir, filename)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


# Serve React frontend (fallback for non-API routes)
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path != "" and os.path.exists(app.static_folder + "/" + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    # Export data on startup
    with app.app_context():
        try:
            print("Exporting data for frontend...")
            export_data_result = export_data()
            print("Data export complete.")
        except Exception as e:
            print(f"Warning: Failed to export data: {e}")

    # Start server
    app.run(debug=True, host="0.0.0.0", port=5002)
