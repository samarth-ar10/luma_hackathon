#!/usr/bin/env python3
"""
Flask server for construction management system with Worker AI.
"""

import logging
import os
import sqlite3
import sys
from contextlib import contextmanager
from pathlib import Path
from threading import Lock

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import argparse

# Load environment variables
parent_dir = Path(__file__).parent.parent.absolute()
load_dotenv(parent_dir / ".env")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] Worker AI: %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("worker_ai")

# Add the parent directory to the Python path
sys.path.insert(0, str(parent_dir))

# Database configuration
DB_PATH = os.environ.get(
    "WORKER_DB_PATH", str(Path(__file__).parent / "db" / "worker_ai.db")
)

# Ensure database directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Database connection lock for thread safety
db_lock = Lock()

# Import Worker AI module and Portia
try:
    from portia import Config, LLMModel, Portia

    PORTIA_AVAILABLE = True

    # Initialize Portia
    portia_api_key = os.environ.get("PORTIA_API_KEY")
    openai_api_key = os.environ.get("OPENAI_API_KEY")

    if portia_api_key and openai_api_key:
        config = Config.from_default(
            llm_model_name=LLMModel.GPT_4_O,
        )
        portia = Portia(config=config)
        logger.info("Portia initialized successfully with GPT-4o (128K context)")
    else:
        logger.warning("Portia initialization failed: missing API keys")
        PORTIA_AVAILABLE = False
        portia = None

except ImportError as e:
    logger.warning(f"Portia module not available: {e}")
    PORTIA_AVAILABLE = False
    portia = None

# Import and initialize Worker AI Manager
try:
    from flask_server.worker_ai import WorkerAIManager

    worker_ai_manager = WorkerAIManager(
        db_path=str(parent_dir / "construction_data.db")
    )
    logger.info(
        f"Worker AI Manager initialized with {len(worker_ai_manager.workers)} roles"
    )
except ImportError as e:
    logger.error(f"Failed to import worker_ai module: {e}")
    PORTIA_AVAILABLE = False
    worker_ai_manager = None

# Create Flask app
app = Flask(__name__, static_folder="../webui/build")
CORS(app)  # Enable CORS for all routes


@contextmanager
def get_db_connection():
    """Thread-safe context manager for database connections."""
    with db_lock:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()


# Serve static files (React app)
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    """Serve the React application."""
    if path != "" and os.path.exists(app.static_folder + "/" + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")


# API Routes
@app.route("/api/worker/message", methods=["POST"])
def process_message():
    """Process a message from the user to the Worker AI."""
    if worker_ai_manager is None:
        return jsonify({"error": "Worker AI not available"}), 503

    data = request.json
    if not data or "message" not in data or "user_id" not in data:
        return jsonify({"error": "Message and user ID are required"}), 400

    user_id = data.get("user_id")
    message = data.get("message")
    role = data.get("role", "worker")
    context = data.get("context", {})

    result = worker_ai_manager.process_message(user_id, role, message, context)
    return jsonify(result)


@app.route("/api/worker/conversation", methods=["GET"])
def get_conversation():
    """Get conversation history for a user with a specific role."""
    if worker_ai_manager is None:
        return jsonify({"error": "Worker AI not available"}), 503

    user_id = request.args.get("user_id")
    role = request.args.get("role", "worker")

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    limit = request.args.get("limit", 10, type=int)
    result = worker_ai_manager.get_conversation_history(user_id, role, limit)
    return jsonify(result)


@app.route("/api/worker/roles", methods=["GET"])
def get_available_roles():
    """Get list of supported AI roles."""
    if worker_ai_manager is None:
        return jsonify({"roles": []}), 503
    return jsonify({"roles": worker_ai_manager.get_available_roles()})


@app.route("/api/dashboard/layout", methods=["GET"])
def get_dashboard_layout():
    """Get dashboard layout for a user based on role."""
    if worker_ai_manager is None:
        return jsonify({"error": "Worker AI not available"}), 503

    user_id = request.args.get("user_id")
    role = request.args.get("role", "worker")

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    worker = worker_ai_manager.get_worker(role)
    layout = worker.get_dashboard_layout(user_id)
    return jsonify(layout)


@app.route("/api/dashboard/layout", methods=["POST"])
def save_dashboard_layout():
    """Save dashboard layout for a user based on role."""
    if worker_ai_manager is None:
        return jsonify({"error": "Worker AI not available"}), 503

    data = request.json
    if not data or "layout" not in data or "user_id" not in data:
        return jsonify({"error": "Layout and user ID are required"}), 400

    user_id = data.get("user_id")
    role = data.get("role", "worker")
    layout = data.get("layout")

    worker = worker_ai_manager.get_worker(role)
    success = worker.save_dashboard_layout(user_id, layout)

    if success:
        return jsonify({"status": "success"})
    else:
        return jsonify({"error": "Failed to save layout"}), 500


@app.route("/api/ask", methods=["POST"])
def ask_llm():
    """Direct query to the LLM."""
    if not PORTIA_AVAILABLE or worker_ai_manager is None:
        return jsonify({"error": "LLM not available"}), 503

    data = request.json
    if not data or "query" not in data:
        return jsonify({"error": "Query is required"}), 400

    try:
        user_id = data.get("user_id", "anonymous")
        role = data.get("role", "worker")
        query = data.get("query")
        context = data.get("context", {})

        # Use Worker AI to process the query
        response = worker_ai_manager.process_message(user_id, role, query, context)
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error in /api/ask: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Serve data files directly
@app.route("/data/<path:filename>")
def serve_data(filename):
    """Serve data files."""
    webui_data_dir = str(parent_dir / "webui" / "public" / "data")
    if os.path.exists(os.path.join(webui_data_dir, filename)):
        response = send_from_directory(webui_data_dir, filename)
    else:
        return jsonify({"error": f"File {filename} not found"}), 404

    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


# Start the server when run directly
if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Start the Worker AI Flask server")
    parser.add_argument(
        "--port", type=int, default=5003, help="Port to run the server on"
    )
    parser.add_argument(
        "--host", type=str, default="0.0.0.0", help="Host to bind the server to"
    )
    args = parser.parse_args()

    # Ensure database tables are created for each database
    for worker in worker_ai_manager.workers.values():
        worker._init_database()

    # Print startup information
    print(f"Starting Flask server on port {args.port}")
    app.run(debug=True, host=args.host, port=args.port)
