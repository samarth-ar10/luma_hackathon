#!/usr/bin/env python3
"""
Worker AI - Flask server acting as a personal agent that manages the dashboard
and provides conversational AI capabilities using Portia LLM integration.
"""

import json
import logging
import os
import sqlite3
import sys
from contextlib import contextmanager
from datetime import datetime
import openai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] Worker AI: %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("worker_ai")

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import Portia components
try:
    from portia import Portia

    PORTIA_AVAILABLE = True
except ImportError:
    logger.warning("Portia module not available. LLM features will be disabled.")
    PORTIA_AVAILABLE = False

# Worker AI capability levels
AI_CAPABILITY_LEVELS = {
    "BASIC": "basic",  # Simple predefined responses
    "ENHANCED": "enhanced",  # Using LLM for specific tasks
    "AUTONOMOUS": "autonomous",  # Can make decisions without explicit requests
}

# Available roles
SUPPORTED_ROLES = [
    "ceo",
    "project-manager",
    "safety-officer",
    "equipment-manager",
    "worker",
    "engineer",
]

# Database configuration
DB_PATH = os.environ.get(
    "WORKER_DB_PATH", os.path.join(os.path.dirname(__file__), "db/worker_ai.db")
)


@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    # Ensure the directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Initialize the database with required tables."""
    with get_db_connection() as conn:
        conn.execute(
            """
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            role TEXT NOT NULL
        )
        """
        )

        conn.execute(
            """
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id TEXT PRIMARY KEY,
            role TEXT NOT NULL,
            dashboard_layout TEXT NOT NULL,
            visualization_preferences TEXT,
            theme TEXT,
            last_updated TEXT NOT NULL
        )
        """
        )

        conn.execute(
            """
        CREATE TABLE IF NOT EXISTS dashboard_items (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            role TEXT NOT NULL,
            item_type TEXT NOT NULL,
            priority INTEGER NOT NULL,
            config TEXT NOT NULL,
            last_updated TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES user_preferences (user_id)
        )
        """
        )

        conn.commit()
        logger.info("Database initialized")


class WorkerAI:
    """
    Simplified Worker AI that acts as a middleman between the user and LLM.
    Handles role-based interactions and visualization generation.
    """

    def __init__(self, role="worker", db_path="construction_data.db"):
        self.role = role
        self.db_path = db_path
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

        if not self.openai_api_key:
            logger.warning("OpenAI API key not found in environment variables.")

        # Initialize database tables if needed
        self._init_database()

        logger.info(f"Worker AI for role {role} initialized")

    def _init_database(self):
        """Initialize database tables if they don't exist."""
        try:
            # Create conversation history and preferences tables
            with self._get_db_connection() as conn:
                # Create conversation history table
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS conversation_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        user_message TEXT NOT NULL,
                        ai_response TEXT NOT NULL,
                        timestamp TEXT NOT NULL
                    )
                    """
                )

                # Create user preferences table
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        user_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        dashboard_layout TEXT,
                        visualization_preferences TEXT,
                        theme TEXT,
                        last_updated TEXT NOT NULL,
                        PRIMARY KEY (user_id, role)
                    )
                    """
                )

                # Create dashboard items table
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS dashboard_items (
                        id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        item_type TEXT NOT NULL,
                        priority INTEGER NOT NULL,
                        config TEXT NOT NULL,
                        last_updated TEXT NOT NULL,
                        FOREIGN KEY (user_id, role) REFERENCES user_preferences (user_id, role)
                    )
                    """
                )

                conn.commit()
            logger.info("Database initialized")
        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}")
            raise

    def _get_db_connection(self):
        """Get a fresh database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_available_tables(self):
        """Get a list of tables in the database."""
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                return [
                    table["name"]
                    for table in tables
                    if table["name"] != "conversation_history"
                ]
        except Exception as e:
            logger.error(f"Error fetching tables: {str(e)}")
            return []

    def get_table_schema(self, table_name):
        """Get the schema for a specific table."""
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                return [{"name": col["name"], "type": col["type"]} for col in columns]
        except Exception as e:
            logger.error(f"Error fetching schema for {table_name}: {str(e)}")
            return []

    def sample_table_data(self, table_name, limit=5):
        """Get sample data from a table."""
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit};")
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching data from {table_name}: {str(e)}")
            return []

    def _get_role_system_prompt(self):
        """Generate role-specific system prompt."""
        base_prompt = """You are an AI assistant for a construction management system. 
Your primary responsibility is to help {role} users organize and understand their data.
Always provide professional, concise advice that is relevant to the {role}'s responsibilities.

When generating visualizations or UI components:
1. Always use React and provide complete, ready-to-use component code
2. Make UI components that can be easily swapped into the existing React dashboard
3. Follow a clean, modern design style with Bootstrap 5 classes
4. Include proper data handling and error states

Available database tables and their schemas:
{db_schema}

Here are some sample records from the database:
{db_samples}
"""

        # Role-specific additions
        role_additions = {
            "ceo": """
As a CEO assistant, prioritize high-level metrics, financial data, and project statuses.
Focus on executive-level insights and company-wide performance.
Organize dashboard tiles to highlight KPIs, financial health, and strategic information.
""",
            "project-manager": """
As a Project Manager assistant, focus on project timelines, task completion, resource allocation, and bottlenecks.
Provide detailed task breakdowns, milestone tracking, and resource utilization metrics.
Organize dashboard tiles to emphasize project progress, team performance, and upcoming deadlines.
""",
            "safety-officer": """
As a Safety Officer assistant, concentrate on safety incidents, compliance metrics, and risk assessments.
Highlight safety protocols, inspection results, and training needs.
Organize dashboard tiles to showcase safety performance, incident tracking, and regulatory compliance.
""",
            "equipment-manager": """
As an Equipment Manager assistant, focus on equipment utilization, maintenance schedules, and inventory.
Track equipment status, repair history, and availability.
Organize dashboard tiles to display equipment allocation, maintenance alerts, and utilization rates.
""",
            "worker": """
As a Worker assistant, emphasize assigned tasks, safety procedures, and required materials.
Provide clear instructions, deadlines, and task priorities.
Organize dashboard tiles to show daily assignments, task details, and relevant safety information.
""",
        }

        # Get database schema and samples
        tables = self.get_available_tables()
        db_schema_text = ""
        db_samples_text = ""

        for table in tables:
            schema = self.get_table_schema(table)
            db_schema_text += f"Table: {table}\n"
            db_schema_text += (
                "Columns: "
                + ", ".join([f"{col['name']} ({col['type']})" for col in schema])
                + "\n\n"
            )

            samples = self.sample_table_data(table)
            if samples:
                db_samples_text += f"Table: {table}\n"
                db_samples_text += json.dumps(samples, indent=2) + "\n\n"

        # Combine base prompt with role-specific additions
        role_prompt = base_prompt.format(
            role=self.role, db_schema=db_schema_text, db_samples=db_samples_text
        )

        if self.role in role_additions:
            role_prompt += role_additions[self.role]

        return role_prompt

    def process_message(self, user_id, message, context=None):
        """
        Process a message from the user and return an AI response.

        Args:
            user_id (str): Unique identifier for the user
            message (str): User's message
            context (dict, optional): Additional context for the message

        Returns:
            dict: Response containing the AI message and any additional data
        """
        try:
            if not self.openai_api_key:
                return {
                    "message": "OpenAI API key is not configured. Please set the OPENAI_API_KEY environment variable.",
                    "error": True,
                }

            # Set up the OpenAI client with the API key
            client = openai.OpenAI(api_key=self.openai_api_key)

            # Get conversation history for this user
            history = self.get_conversation_history(user_id)

            # Build the messages array for the API call
            messages = [
                {"role": "system", "content": self._get_role_system_prompt()},
            ]

            # Add conversation history (up to 5 most recent exchanges)
            for i, entry in enumerate(history[-5:]):
                messages.append({"role": "user", "content": entry["user_message"]})
                messages.append({"role": "assistant", "content": entry["ai_response"]})

            # Add the current user message
            context_str = ""
            if context:
                context_str = f"\nContext: {json.dumps(context)}"

            messages.append({"role": "user", "content": message + context_str})

            # Make the API call to OpenAI
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",  # Using gpt-4o with 128K token context limit
                    messages=messages,
                    temperature=0.7,
                    max_tokens=2048,
                )

                ai_response = response.choices[0].message.content

                # Save to conversation history
                self.save_conversation(user_id, message, ai_response)

                # Extract any code blocks for easier frontend handling
                visualization_code = self._extract_code_blocks(ai_response)

                return {
                    "message": ai_response,
                    "visualization": visualization_code if visualization_code else None,
                    "timestamp": datetime.now().isoformat(),
                }

            except Exception as e:
                logger.error(f"OpenAI API error: {str(e)}")
                return {
                    "message": f"I encountered an error while processing your request: {str(e)}",
                    "error": True,
                }

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                "message": "Sorry, I encountered an unexpected error while processing your request.",
                "error": True,
            }

    def _extract_code_blocks(self, text):
        """Extract code blocks from the AI response for easier frontend use."""
        import re

        # Look for code blocks (```jsx or ```javascript or just ```)
        code_blocks = re.findall(r"```(?:jsx|javascript|react)?\s*([\s\S]*?)```", text)

        if code_blocks:
            # Return the first code block that appears to be a React component
            for block in code_blocks:
                if "import React" in block or "function" in block or "const" in block:
                    return block.strip()

        return None

    def save_conversation(self, user_id, user_message, ai_response):
        """Save a conversation exchange to the database."""
        try:
            with self._get_db_connection() as conn:
                conn.execute(
                    "INSERT INTO conversation_history (user_id, role, user_message, ai_response, timestamp) VALUES (?, ?, ?, ?, ?)",
                    (
                        user_id,
                        self.role,
                        user_message,
                        ai_response,
                        datetime.now().isoformat(),
                    ),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving conversation: {str(e)}")

    def get_conversation_history(self, user_id, limit=10):
        """Get conversation history for a specific user."""
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM conversation_history WHERE user_id = ? AND role = ? ORDER BY timestamp DESC LIMIT ?",
                    (user_id, self.role, limit),
                )
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching conversation history: {str(e)}")
            return []

    def get_dashboard_layout(self, user_id):
        """
        Get dashboard layout preferences for a specific user and role.
        If no preferences exist, creates default layout based on role.

        Args:
            user_id (str): Unique identifier for the user

        Returns:
            dict: Dashboard layout configuration with prioritized tiles
        """
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT dashboard_layout FROM user_preferences 
                    WHERE user_id = ? AND role = ?
                    """,
                    (user_id, self.role),
                )
                result = cursor.fetchone()

                if result:
                    # Return existing layout preferences
                    return json.loads(result["dashboard_layout"])
                else:
                    # Create default layout based on role
                    layout = self._create_default_dashboard_layout()
                    self.save_dashboard_layout(user_id, layout)
                    return layout

        except Exception as e:
            logger.error(f"Error fetching dashboard layout: {str(e)}")
            # Return fallback layout in case of error
            return self._create_default_dashboard_layout()

    def _create_default_dashboard_layout(self):
        """Create default dashboard layout based on role."""
        # Common tiles with default priority (lower number = higher priority)
        tiles = [
            {
                "id": "projects",
                "title": "Project Overview",
                "size": "medium",
                "priority": 10,
            }
        ]

        # Role-specific tiles with priorities
        if self.role == "ceo":
            tiles.extend(
                [
                    {
                        "id": "finances",
                        "title": "Financial Overview",
                        "size": "large",
                        "priority": 1,
                    },
                    {
                        "id": "safety",
                        "title": "Safety Statistics",
                        "size": "small",
                        "priority": 5,
                    },
                    {
                        "id": "tasks",
                        "title": "Task Completion",
                        "size": "small",
                        "priority": 8,
                    },
                ]
            )
        elif self.role == "project-manager":
            tiles.extend(
                [
                    {"id": "tasks", "title": "Tasks", "size": "large", "priority": 1},
                    {
                        "id": "materials",
                        "title": "Materials Tracking",
                        "size": "medium",
                        "priority": 3,
                    },
                    {
                        "id": "timeline",
                        "title": "Project Timeline",
                        "size": "medium",
                        "priority": 2,
                    },
                ]
            )
        elif self.role == "safety-officer":
            tiles.extend(
                [
                    {
                        "id": "safety",
                        "title": "Safety Reports",
                        "size": "large",
                        "priority": 1,
                    },
                    {
                        "id": "safetyTasks",
                        "title": "Safety Tasks",
                        "size": "medium",
                        "priority": 2,
                    },
                    {
                        "id": "incidents",
                        "title": "Incident Tracking",
                        "size": "medium",
                        "priority": 3,
                    },
                ]
            )
        elif self.role == "equipment-manager":
            tiles.extend(
                [
                    {
                        "id": "equipment",
                        "title": "Equipment Status",
                        "size": "large",
                        "priority": 1,
                    },
                    {
                        "id": "maintenance",
                        "title": "Maintenance Schedule",
                        "size": "medium",
                        "priority": 2,
                    },
                    {
                        "id": "inventory",
                        "title": "Inventory",
                        "size": "medium",
                        "priority": 3,
                    },
                ]
            )
        elif self.role == "engineer":
            tiles.extend(
                [
                    {
                        "id": "tasks",
                        "title": "Engineering Tasks",
                        "size": "large",
                        "priority": 1,
                    },
                    {
                        "id": "materials",
                        "title": "Materials Specifications",
                        "size": "medium",
                        "priority": 2,
                    },
                    {
                        "id": "projects",
                        "title": "Project Details",
                        "size": "medium",
                        "priority": 3,
                    },
                ]
            )
        else:  # default worker role
            tiles.extend(
                [
                    {
                        "id": "tasks",
                        "title": "My Tasks",
                        "size": "large",
                        "priority": 1,
                    },
                    {
                        "id": "safety",
                        "title": "Safety Reminders",
                        "size": "medium",
                        "priority": 2,
                    },
                    {
                        "id": "materials",
                        "title": "Materials Needed",
                        "size": "medium",
                        "priority": 3,
                    },
                ]
            )

        # Add mail tile for all roles
        tiles.append({"id": "mail", "title": "Mail", "size": "small", "priority": 15})

        # Sort tiles by priority
        tiles.sort(key=lambda x: x["priority"])

        return {"tiles": tiles}

    def save_dashboard_layout(self, user_id, layout):
        """
        Save dashboard layout preferences for a specific user and role.

        Args:
            user_id (str): Unique identifier for the user
            layout (dict): Dashboard layout configuration

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            layout_json = json.dumps(layout)
            timestamp = datetime.now().isoformat()

            with self._get_db_connection() as conn:
                cursor = conn.cursor()

                # Check if user preferences exist
                cursor.execute(
                    "SELECT user_id FROM user_preferences WHERE user_id = ? AND role = ?",
                    (user_id, self.role),
                )

                if cursor.fetchone():
                    # Update existing preferences
                    cursor.execute(
                        """
                        UPDATE user_preferences 
                        SET dashboard_layout = ?, last_updated = ? 
                        WHERE user_id = ? AND role = ?
                        """,
                        (layout_json, timestamp, user_id, self.role),
                    )
                else:
                    # Insert new preferences
                    cursor.execute(
                        """
                        INSERT INTO user_preferences 
                        (user_id, role, dashboard_layout, visualization_preferences, theme, last_updated) 
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (user_id, self.role, layout_json, "{}", "light", timestamp),
                    )

            conn.commit()
            return True

        except Exception as e:
            logger.error(f"Error saving dashboard layout: {str(e)}")
            return False


class WorkerAIManager:
    """
    Manages multiple WorkerAI instances for different roles.
    """

    def __init__(self, db_path="construction_data.db"):
        self.db_path = db_path
        self.workers = {}

        # Initialize workers for different roles
        self.available_roles = [
            "ceo",
            "project-manager",
            "safety-officer",
            "equipment-manager",
            "worker",
            "engineer",
        ]
        for role in self.available_roles:
            try:
                self.workers[role] = WorkerAI(role=role, db_path=db_path)
                logger.info(f"Initialized Worker AI for role {role}")
            except Exception as e:
                logger.error(f"Error initializing Worker AI for role {role}: {str(e)}")

    def get_worker(self, role):
        """Get a worker AI for a specific role."""
        if role in self.workers:
            return self.workers[role]
        else:
            # Default to worker role if requested role doesn't exist
            logger.warning(f"Requested role {role} not found, defaulting to 'worker'")
            return self.workers.get("worker")

    def get_available_roles(self):
        """Get list of available roles."""
        return self.available_roles

    def process_message(self, user_id, role, message, context=None):
        """Process a message using the appropriate worker for the specified role."""
        worker = self.get_worker(role)
        return worker.process_message(user_id, message, context)

    def get_conversation_history(self, user_id, role, limit=10):
        """Get conversation history for a specific user and role."""
        worker = self.get_worker(role)
        return worker.get_conversation_history(user_id, limit)


# Create Worker AI Manager instance
worker_ai_manager = WorkerAIManager()
# Expose the manager as worker_ai for backward compatibility
worker_ai = worker_ai_manager

# If this file is run directly, print information about the Worker AI
if __name__ == "__main__":
    print("Worker AI Manager initialized")
    print(f"Database path: {DB_PATH}")

    # Initialize all role-specific AI instances
    worker_ai_manager.initialize()

    # Print all available roles
    print(f"Available roles: {', '.join(SUPPORTED_ROLES)}")

    # Example interaction
    role = "project-manager"
    response = worker_ai_manager.process_user_message(
        "test_user",
        role,
        "Show me the status of all projects",
        {"source": "console_test"},
    )

    print("\nExample interaction:")
    print(f"User ({role}): Show me the status of all projects")
    print(f"Worker AI: {response.get('message', '')}")
