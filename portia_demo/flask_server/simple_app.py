#!/usr/bin/env python3
"""
Simplified Flask Server - Main application file for the company communication and data flow manager.
"""
import os
import sqlite3
import sys
from contextlib import contextmanager
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import Portia components
from portia import (
    Config,
    LLMModel,
    LLMProvider,
    Portia,
    example_tool_registry,
)

# Import custom tools
from custom_tools import custom_tools

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder="../webui/build")
CORS(app)  # Enable Cross-Origin Resource Sharing

# Configure Portia
portia_api_key = os.getenv("PORTIA_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Create a Portia config with OpenAI
portia_config = Config.from_default(
    llm_provider=LLMProvider.OPENAI,
    llm_model_name=LLMModel.GPT_4_O,
    openai_api_key=openai_api_key,
    portia_api_key=portia_api_key,
)

# Combine standard tools with our custom SQL tools
all_tools = list(example_tool_registry) + custom_tools

# Initialize Portia with standard and custom tools
portia = Portia(config=portia_config, tools=all_tools)

# Database configuration
DB_PATH = os.path.abspath(os.environ.get("SQL_MCP_DB_PATH", "../sql_data.db"))
print(f"Using database at: {DB_PATH}")


@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    print(f"Attempting to connect to DB at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def execute_sql_query(query):
    """Execute a SQL query and return the results."""
    print(f"Executing SQL query: {query}")
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
                print(f"Query returned {len(results)} results")
                return {"success": True, "results": results}
            else:
                return {"success": True, "message": "Query executed successfully"}
        except Exception as e:
            print(f"SQL Error: {str(e)}")
            return {"success": False, "error": str(e)}


# API Routes
@app.route("/api/ask", methods=["POST"])
def ask_llm():
    """Endpoint to query the LLM with a natural language question using Portia."""
    print("Received request to /api/ask")
    data = request.json
    if not data or "query" not in data:
        return jsonify({"error": "Query is required"}), 400

    try:
        query = data["query"]
        print(f"Processing query with Portia: {query}")

        # Use Portia to process the query
        plan_run = portia.run(query)

        # Extract the relevant information from the plan run
        response = {
            "answer": plan_run.final_output.get("response", plan_run.final_output),
            "plan_id": plan_run.plan_id,
            "state": plan_run.state,
        }

        print(f"Portia response: {response}")
        return jsonify(response)
    except Exception as e:
        print(f"Error in /api/ask: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/query", methods=["POST"])
def sql_query():
    """Endpoint to execute SQL queries from the React app."""
    print("Received request to /api/query")
    data = request.json
    if not data or "sql" not in data:
        return jsonify({"error": "SQL query is required"}), 400

    try:
        # Validate query type for security (only allow SELECT)
        query = data["sql"].strip()
        if not query.upper().startswith("SELECT"):
            return (
                jsonify({"success": False, "error": "Only SELECT queries are allowed"}),
                403,
            )

        # Execute the query
        result = execute_sql_query(query)
        return jsonify(result)
    except Exception as e:
        print(f"Error in /api/query: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/customers", methods=["GET"])
def get_customers():
    """Get all customers - for maintaining backward compatibility."""
    print("Received request to /api/customers")
    try:
        result = execute_sql_query("SELECT * FROM customers")
        return jsonify(result)
    except Exception as e:
        print(f"Error in /api/customers: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Get company statistics for the dashboard."""
    print("Received request to /api/stats")
    try:
        # Execute queries to get relevant statistics
        employee_stats = execute_sql_query(
            "SELECT COUNT(*) as employee_count FROM employees"
        )
        revenue_stats = execute_sql_query(
            "SELECT SUM(amount) as total_revenue FROM sales"
        )
        project_stats = execute_sql_query(
            "SELECT COUNT(*) as project_count FROM projects WHERE status = 'active'"
        )

        stats = {
            "employees": employee_stats.get("results", [{"employee_count": 0}])[0].get(
                "employee_count", 0
            ),
            "revenue": revenue_stats.get("results", [{"total_revenue": 0}])[0].get(
                "total_revenue", 0
            ),
            "active_projects": project_stats.get("results", [{"project_count": 0}])[
                0
            ].get("project_count", 0),
        }

        print(f"Returning stats: {stats}")
        return jsonify(stats)
    except Exception as e:
        print(f"Error in /api/stats: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/roles/<role>", methods=["GET"])
def get_role_data(role):
    """Get data specific to a role."""
    print(f"Received request to /api/roles/{role}")
    valid_roles = [
        "ceo",
        "marketing",
        "sales",
        "engineering",
        "construction",
        "manager",
    ]

    if role.lower() not in valid_roles:
        return jsonify({"error": "Invalid role"}), 400

    try:
        if role.lower() == "ceo":
            # CEO sees high-level KPIs
            data = {
                "kpis": execute_sql_query("SELECT * FROM kpis"),
                "department_performance": execute_sql_query(
                    "SELECT department, performance_score FROM department_performance"
                ),
                "team": execute_sql_query("SELECT * FROM employees"),
            }
        elif role.lower() == "marketing":
            # Marketing sees campaign data
            data = {
                "campaigns": execute_sql_query("SELECT * FROM marketing_campaigns"),
                "leads": execute_sql_query(
                    "SELECT COUNT(*) as lead_count, source FROM leads GROUP BY source"
                ),
            }
        elif role.lower() == "sales":
            # Sales sees customer and revenue data
            data = {
                "customers": execute_sql_query("SELECT * FROM customers LIMIT 10"),
                "revenue": execute_sql_query(
                    "SELECT SUM(amount) as revenue, date FROM sales GROUP BY date ORDER BY date DESC LIMIT 30"
                ),
            }
        elif role.lower() == "engineering":
            # Engineering sees project and ticket data
            data = {
                "projects": execute_sql_query(
                    "SELECT * FROM projects WHERE department = 'engineering'"
                ),
                "tickets": execute_sql_query(
                    "SELECT * FROM tickets WHERE status != 'closed' ORDER BY priority DESC"
                ),
            }
        elif role.lower() == "construction":
            # Construction sees site and material data
            data = {
                "sites": execute_sql_query("SELECT * FROM construction_sites"),
                "materials": execute_sql_query(
                    "SELECT * FROM materials WHERE quantity < reorder_level"
                ),
            }
        elif role.lower() == "manager":
            # Managers see team and task data
            data = {
                "team": execute_sql_query(
                    "SELECT * FROM employees WHERE manager_id = 1"
                ),
                "tasks": execute_sql_query(
                    "SELECT * FROM tasks WHERE assigned_to IN (SELECT id FROM employees WHERE manager_id = 1)"
                ),
            }

        print(f"Returning role data for {role}")
        return jsonify(data)
    except Exception as e:
        print(f"Error in /api/roles/{role}: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Debug route
@app.route("/api/debug", methods=["GET"])
def debug():
    """Get debug information about the server."""
    info = {
        "db_path": DB_PATH,
        "db_exists": os.path.exists(DB_PATH),
        "app_root": os.path.abspath(os.path.dirname(__file__)),
        "static_folder": app.static_folder,
        "portia_configured": portia_api_key is not None and openai_api_key is not None,
        "portia_provider": "OpenAI",
        "custom_tools": [tool.name for tool in custom_tools],
    }
    return jsonify(info)


# Serve React frontend
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    print(f"Received request for path: {path}")
    if path != "" and os.path.exists(app.static_folder + "/" + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    print(f"Starting Flask server on port 9000 with database at {DB_PATH}")
    print(
        f"Portia configured with OpenAI: {portia_api_key is not None and openai_api_key is not None}"
    )
    print(f"Custom tools available: {[tool.name for tool in custom_tools]}")
    app.run(debug=True, host="0.0.0.0", port=9000)
