import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from psycopg2 import sql
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Database connection parameters
DB_NAME = os.getenv("DB_NAME", "construction_company")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# Valid table names for security
VALID_TABLES = [
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


def get_db_connection():
    """
    Establishes a connection to the PostgreSQL database.
    Creates the database if it doesn't exist.

    Returns:
        connection: A psycopg2 connection object
    """
    try:
        # First try to connect to the specific database
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        logger.info(f"Connected to database: {DB_NAME}")
        return conn
    except psycopg2.OperationalError:
        # If database doesn't exist, connect to default postgres database and create it
        logger.info(f"Database {DB_NAME} does not exist. Creating it.")
        conn = psycopg2.connect(
            dbname="postgres",
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Create database if not exists
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
        cursor.close()
        conn.close()

        # Connect to the newly created database
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        logger.info(f"Created and connected to database: {DB_NAME}")
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise


def execute_query(query, params=None, fetch=True):
    """
    Execute a SQL query and return results.

    Args:
        query (str): SQL query to execute
        params (tuple, optional): Parameters for the query. Defaults to None.
        fetch (bool, optional): Whether to fetch and return results. Defaults to True.

    Returns:
        list: Query results if fetch is True, otherwise None
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute the query
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        results = None
        if fetch:
            results = cursor.fetchall()

        conn.commit()
        return results
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Query execution error: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()


def get_table_data(table_name):
    """
    Get all data from a specified table.

    Args:
        table_name (str): Name of the table to query

    Returns:
        list: All rows from the specified table
    """
    if table_name not in VALID_TABLES:
        raise ValueError(f"Invalid table name: {table_name}")

    query = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name))
    return execute_query(query.as_string(conn=get_db_connection()))


def get_column_names(table_name):
    """
    Get column names for a specified table.

    Args:
        table_name (str): Name of the table

    Returns:
        list: Column names for the specified table
    """
    if table_name not in VALID_TABLES:
        raise ValueError(f"Invalid table name: {table_name}")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Query to get column names
    query = """
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name = %s
    ORDER BY ordinal_position
    """

    cursor.execute(query, (table_name,))
    results = cursor.fetchall()

    # Extract column names from results
    column_names = [row[0] for row in results]

    cursor.close()
    conn.close()

    return column_names


def get_role_data(role_type):
    """
    Get data relevant to a specific role.

    Args:
        role_type (str): Type of role ('project_manager', 'safety_officer', or 'site_supervisor')

    Returns:
        dict: Data relevant to the specified role
    """
    role_data = {}

    if role_type == "project_manager":
        # Project managers need project overview and financial data
        role_data["projects"] = execute_query(
            "SELECT * FROM projects ORDER BY end_date"
        )
        role_data["tasks"] = execute_query(
            "SELECT t.* FROM tasks t JOIN projects p ON t.project_id = p.project_id ORDER BY t.end_date"
        )
        role_data["workers"] = execute_query("SELECT * FROM workers ORDER BY name")
        role_data["progress"] = execute_query(
            """
            SELECT pt.*, p.name as project_name 
            FROM progress_tracking pt
            JOIN projects p ON pt.project_id = p.project_id
            ORDER BY pt.date DESC
            """
        )

    elif role_type == "safety_officer":
        # Safety officers need safety incidents and checklist data
        role_data["safety_incidents"] = execute_query(
            """
            SELECT s.*, p.name as project_name 
            FROM safety s
            JOIN projects p ON s.project_id = p.project_id
            ORDER BY s.date DESC
            """
        )
        role_data["safety_checklists"] = execute_query(
            """
            SELECT sc.*, p.name as project_name 
            FROM safety_checklists sc
            JOIN projects p ON sc.project_id = p.project_id
            ORDER BY sc.date DESC
            """
        )
        role_data["equipment"] = execute_query(
            "SELECT * FROM equipment ORDER BY next_maintenance"
        )

    elif role_type == "site_supervisor":
        # Site supervisors need daily tasks, workers, and materials data
        role_data["daily_tasks"] = execute_query(
            """
            SELECT dt.*, p.name as project_name, w.name as worker_name
            FROM daily_tasks dt
            JOIN projects p ON dt.project_id = p.project_id
            JOIN workers w ON dt.worker_id = w.worker_id
            ORDER BY dt.date DESC
            """
        )
        role_data["workers"] = execute_query("SELECT * FROM workers ORDER BY name")
        role_data["materials"] = execute_query(
            "SELECT * FROM materials ORDER BY category, name"
        )
        role_data["equipment"] = execute_query(
            "SELECT * FROM equipment WHERE status = 'Operational' ORDER BY name"
        )
    else:
        raise ValueError(f"Invalid role type: {role_type}")

    return role_data


def get_projects(filters=None):
    """
    Get projects from the database

    Args:
        filters (dict): Optional filters to apply to the query

    Returns:
        list: List of projects
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = "SELECT * FROM projects"

    # Apply filters if provided
    if filters:
        where_clauses = []
        params = []

        if "status" in filters:
            where_clauses.append("status = %s")
            params.append(filters["status"])

        if "location" in filters:
            where_clauses.append("location = %s")
            params.append(filters["location"])

        if "manager" in filters:
            where_clauses.append("manager = %s")
            params.append(filters["manager"])

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        cursor.execute(query, params)
    else:
        cursor.execute(query)

    projects = cursor.fetchall()

    # Convert to dictionaries
    result = []
    for project in projects:
        result.append(dict(project))

    cursor.close()
    conn.close()

    return result


def get_tasks(filters=None):
    """
    Get tasks from the database

    Args:
        filters (dict): Optional filters to apply to the query

    Returns:
        list: List of tasks
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = "SELECT * FROM tasks"

    # Apply filters if provided
    if filters:
        where_clauses = []
        params = []

        if "project_id" in filters:
            where_clauses.append("project_id = %s")
            params.append(filters["project_id"])

        if "status" in filters:
            where_clauses.append("status = %s")
            params.append(filters["status"])

        if "assigned_to" in filters:
            where_clauses.append("assigned_to = %s")
            params.append(filters["assigned_to"])

        if "priority" in filters:
            where_clauses.append("priority = %s")
            params.append(filters["priority"])

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        cursor.execute(query, params)
    else:
        cursor.execute(query)

    tasks = cursor.fetchall()

    # Convert to dictionaries
    result = []
    for task in tasks:
        result.append(dict(task))

    cursor.close()
    conn.close()

    return result


def get_workers(filters=None):
    """
    Get workers from the database

    Args:
        filters (dict): Optional filters to apply to the query

    Returns:
        list: List of workers
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = "SELECT * FROM workers"

    # Apply filters if provided
    if filters:
        where_clauses = []
        params = []

        if "role" in filters:
            where_clauses.append("role = %s")
            params.append(filters["role"])

        if "availability" in filters:
            where_clauses.append("availability = %s")
            params.append(filters["availability"])

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        cursor.execute(query, params)
    else:
        cursor.execute(query)

    workers = cursor.fetchall()

    # Convert to dictionaries
    result = []
    for worker in workers:
        worker_dict = dict(worker)
        # Convert array fields to lists
        if worker_dict["skills"] is not None:
            worker_dict["skills"] = list(worker_dict["skills"])
        if worker_dict["certification"] is not None:
            worker_dict["certification"] = list(worker_dict["certification"])
        result.append(worker_dict)

    cursor.close()
    conn.close()

    return result


def get_materials(filters=None):
    """
    Get materials from the database

    Args:
        filters (dict): Optional filters to apply to the query

    Returns:
        list: List of materials
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = "SELECT * FROM materials"

    # Apply filters if provided
    if filters:
        where_clauses = []
        params = []

        if "category" in filters:
            where_clauses.append("category = %s")
            params.append(filters["category"])

        if "supplier" in filters:
            where_clauses.append("supplier = %s")
            params.append(filters["supplier"])

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        cursor.execute(query, params)
    else:
        cursor.execute(query)

    materials = cursor.fetchall()

    # Convert to dictionaries
    result = []
    for material in materials:
        result.append(dict(material))

    cursor.close()
    conn.close()

    return result


def get_safety_incidents(filters=None):
    """
    Get safety incidents from the database

    Args:
        filters (dict): Optional filters to apply to the query

    Returns:
        list: List of safety incidents
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = "SELECT * FROM safety"

    # Apply filters if provided
    if filters:
        where_clauses = []
        params = []

        if "project_id" in filters:
            where_clauses.append("project_id = %s")
            params.append(filters["project_id"])

        if "type" in filters:
            where_clauses.append("type = %s")
            params.append(filters["type"])

        if "severity" in filters:
            where_clauses.append("severity = %s")
            params.append(filters["severity"])

        if "status" in filters:
            where_clauses.append("status = %s")
            params.append(filters["status"])

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        cursor.execute(query, params)
    else:
        cursor.execute(query)

    incidents = cursor.fetchall()

    # Convert to dictionaries
    result = []
    for incident in incidents:
        result.append(dict(incident))

    cursor.close()
    conn.close()

    return result


def get_equipment(filters=None):
    """
    Get equipment from the database

    Args:
        filters (dict): Optional filters to apply to the query

    Returns:
        list: List of equipment
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = "SELECT * FROM equipment"

    # Apply filters if provided
    if filters:
        where_clauses = []
        params = []

        if "status" in filters:
            where_clauses.append("status = %s")
            params.append(filters["status"])

        if "type" in filters:
            where_clauses.append("type = %s")
            params.append(filters["type"])

        if "location" in filters:
            where_clauses.append("location = %s")
            params.append(filters["location"])

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        cursor.execute(query, params)
    else:
        cursor.execute(query)

    equipment_items = cursor.fetchall()

    # Convert to dictionaries
    result = []
    for item in equipment_items:
        result.append(dict(item))

    cursor.close()
    conn.close()

    return result


def get_safety_checklists(filters=None):
    """
    Get safety checklists from the database

    Args:
        filters (dict): Optional filters to apply to the query

    Returns:
        list: List of safety checklist items
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = "SELECT * FROM safety_checklists"

    # Apply filters if provided
    if filters:
        where_clauses = []
        params = []

        if "priority" in filters:
            where_clauses.append("priority = %s")
            params.append(filters["priority"])

        if "status" in filters:
            where_clauses.append("status = %s")
            params.append(filters["status"])

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        cursor.execute(query, params)
    else:
        cursor.execute(query)

    items = cursor.fetchall()

    # Convert to dictionaries
    result = []
    for item in items:
        result.append(dict(item))

    cursor.close()
    conn.close()

    return result


def get_daily_tasks(filters=None):
    """
    Get daily tasks from the database

    Args:
        filters (dict): Optional filters to apply to the query

    Returns:
        list: List of daily tasks
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = "SELECT * FROM daily_tasks"

    # Apply filters if provided
    if filters:
        where_clauses = []
        params = []

        if "priority" in filters:
            where_clauses.append("priority = %s")
            params.append(filters["priority"])

        if "completed" in filters:
            where_clauses.append("completed = %s")
            params.append(filters["completed"])

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        cursor.execute(query, params)
    else:
        cursor.execute(query)

    tasks = cursor.fetchall()

    # Convert to dictionaries
    result = []
    for task in tasks:
        result.append(dict(task))

    cursor.close()
    conn.close()

    return result


def get_progress_tracking(filters=None):
    """
    Get progress tracking data from the database

    Args:
        filters (dict): Optional filters to apply to the query

    Returns:
        list: List of progress tracking items
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = "SELECT * FROM progress_tracking"

    # Apply filters if provided
    if filters:
        where_clauses = []
        params = []

        if "location" in filters:
            where_clauses.append("location = %s")
            params.append(filters["location"])

        if "date" in filters:
            where_clauses.append("date = %s")
            params.append(filters["date"])

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        cursor.execute(query, params)
    else:
        cursor.execute(query)

    items = cursor.fetchall()

    # Convert to dictionaries
    result = []
    for item in items:
        result.append(dict(item))

    cursor.close()
    conn.close()

    return result
