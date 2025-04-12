import datetime
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
from portia import Tool
import db_utils


class ProjectsToolSchema(BaseModel):
    """Input for ProjectsTool."""

    status: Optional[str] = Field(
        None, description="Filter by project status (e.g., 'In Progress', 'Completed')"
    )
    location: Optional[str] = Field(None, description="Filter by project location")
    manager: Optional[str] = Field(None, description="Filter by project manager name")


class ProjectsTool(Tool[List[Dict[str, Any]]]):
    """Tool to retrieve projects data from the database."""

    id: str = "get_projects_tool"
    name: str = "get_projects"
    description: str = "Retrieve projects data from the construction company database"
    args_schema: type[BaseModel] = ProjectsToolSchema
    output_schema: tuple[str, str] = (
        "list[dict]",
        "List of project records from the database",
    )

    def run(
        self,
        _: Any,
        status: Optional[str] = None,
        location: Optional[str] = None,
        manager: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Run the tool to get projects data."""
        filters = {}
        if status:
            filters["status"] = status
        if location:
            filters["location"] = location
        if manager:
            filters["manager"] = manager

        projects = db_utils.get_projects(filters)

        # Convert date objects to strings for JSON serialization
        for project in projects:
            for key, value in project.items():
                if isinstance(value, datetime.date):
                    project[key] = value.isoformat()

        return projects


class TasksToolSchema(BaseModel):
    """Input for TasksTool."""

    project_id: Optional[str] = Field(None, description="Filter by project ID")
    status: Optional[str] = Field(
        None,
        description="Filter by task status (e.g., 'In Progress', 'Completed', 'Not Started')",
    )
    assigned_to: Optional[str] = Field(
        None, description="Filter by team/person assignment"
    )
    priority: Optional[str] = Field(
        None, description="Filter by priority level (e.g., 'High', 'Medium', 'Low')"
    )


class TasksTool(Tool[List[Dict[str, Any]]]):
    """Tool to retrieve tasks data from the database."""

    id: str = "get_tasks_tool"
    name: str = "get_tasks"
    description: str = "Retrieve tasks data from the construction company database"
    args_schema: type[BaseModel] = TasksToolSchema
    output_schema: tuple[str, str] = (
        "list[dict]",
        "List of task records from the database",
    )

    def run(
        self,
        _: Any,
        project_id: Optional[str] = None,
        status: Optional[str] = None,
        assigned_to: Optional[str] = None,
        priority: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Run the tool to get tasks data."""
        filters = {}
        if project_id:
            filters["project_id"] = project_id
        if status:
            filters["status"] = status
        if assigned_to:
            filters["assigned_to"] = assigned_to
        if priority:
            filters["priority"] = priority

        tasks = db_utils.get_tasks(filters)

        # Convert date objects to strings for JSON serialization
        for task in tasks:
            for key, value in task.items():
                if isinstance(value, datetime.date):
                    task[key] = value.isoformat()

        return tasks


class WorkersToolSchema(BaseModel):
    """Input for WorkersTool."""

    role: Optional[str] = Field(None, description="Filter by worker role")
    availability: Optional[str] = Field(
        None, description="Filter by worker availability"
    )


class WorkersTool(Tool[List[Dict[str, Any]]]):
    """Tool to retrieve workers data from the database."""

    id: str = "get_workers_tool"
    name: str = "get_workers"
    description: str = "Retrieve workers data from the construction company database"
    args_schema: type[BaseModel] = WorkersToolSchema
    output_schema: tuple[str, str] = (
        "list[dict]",
        "List of worker records from the database",
    )

    def run(
        self, _: Any, role: Optional[str] = None, availability: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Run the tool to get workers data."""
        filters = {}
        if role:
            filters["role"] = role
        if availability:
            filters["availability"] = availability

        workers = db_utils.get_workers(filters)
        return workers


class MaterialsToolSchema(BaseModel):
    """Input for MaterialsTool."""

    category: Optional[str] = Field(None, description="Filter by material category")
    supplier: Optional[str] = Field(None, description="Filter by supplier name")


class MaterialsTool(Tool[List[Dict[str, Any]]]):
    """Tool to retrieve materials data from the database."""

    id: str = "get_materials_tool"
    name: str = "get_materials"
    description: str = "Retrieve materials data from the construction company database"
    args_schema: type[BaseModel] = MaterialsToolSchema
    output_schema: tuple[str, str] = (
        "list[dict]",
        "List of material records from the database",
    )

    def run(
        self, _: Any, category: Optional[str] = None, supplier: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Run the tool to get materials data."""
        filters = {}
        if category:
            filters["category"] = category
        if supplier:
            filters["supplier"] = supplier

        materials = db_utils.get_materials(filters)

        # Convert date objects to strings for JSON serialization
        for material in materials:
            for key, value in material.items():
                if isinstance(value, datetime.date):
                    material[key] = value.isoformat()

        return materials


class SafetyIncidentsToolSchema(BaseModel):
    """Input for SafetyIncidentsTool."""

    project_id: Optional[str] = Field(None, description="Filter by project ID")
    type: Optional[str] = Field(None, description="Filter by incident type")
    severity: Optional[str] = Field(
        None, description="Filter by severity level (e.g., 'High', 'Medium', 'Low')"
    )
    status: Optional[str] = Field(None, description="Filter by incident status")


class SafetyIncidentsTool(Tool[List[Dict[str, Any]]]):
    """Tool to retrieve safety incidents data from the database."""

    id: str = "get_safety_incidents_tool"
    name: str = "get_safety_incidents"
    description: str = (
        "Retrieve safety incidents data from the construction company database"
    )
    args_schema: type[BaseModel] = SafetyIncidentsToolSchema
    output_schema: tuple[str, str] = (
        "list[dict]",
        "List of safety incident records from the database",
    )

    def run(
        self,
        _: Any,
        project_id: Optional[str] = None,
        type: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Run the tool to get safety incidents data."""
        filters = {}
        if project_id:
            filters["project_id"] = project_id
        if type:
            filters["type"] = type
        if severity:
            filters["severity"] = severity
        if status:
            filters["status"] = status

        incidents = db_utils.get_safety_incidents(filters)

        # Convert date objects to strings for JSON serialization
        for incident in incidents:
            for key, value in incident.items():
                if isinstance(value, datetime.date):
                    incident[key] = value.isoformat()

        return incidents


class EquipmentToolSchema(BaseModel):
    """Input for EquipmentTool."""

    status: Optional[str] = Field(
        None, description="Filter by equipment status (e.g., 'In Use', 'Available')"
    )
    type: Optional[str] = Field(None, description="Filter by equipment type")
    location: Optional[str] = Field(None, description="Filter by equipment location")


class EquipmentTool(Tool[List[Dict[str, Any]]]):
    """Tool to retrieve equipment data from the database."""

    id: str = "get_equipment_tool"
    name: str = "get_equipment"
    description: str = "Retrieve equipment data from the construction company database"
    args_schema: type[BaseModel] = EquipmentToolSchema
    output_schema: tuple[str, str] = (
        "list[dict]",
        "List of equipment records from the database",
    )

    def run(
        self,
        _: Any,
        status: Optional[str] = None,
        type: Optional[str] = None,
        location: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Run the tool to get equipment data."""
        filters = {}
        if status:
            filters["status"] = status
        if type:
            filters["type"] = type
        if location:
            filters["location"] = location

        equipment = db_utils.get_equipment(filters)

        # Convert date objects to strings for JSON serialization
        for item in equipment:
            for key, value in item.items():
                if isinstance(value, datetime.date):
                    item[key] = value.isoformat()

        return equipment


class SafetyChecklistsToolSchema(BaseModel):
    """Input for SafetyChecklistsTool."""

    priority: Optional[str] = Field(
        None,
        description="Filter by priority level (e.g., 'Critical', 'Warning', 'Normal')",
    )
    status: Optional[str] = Field(
        None, description="Filter by status (e.g., 'Pending', 'Completed')"
    )


class SafetyChecklistsTool(Tool[List[Dict[str, Any]]]):
    """Tool to retrieve safety checklists data from the database."""

    id: str = "get_safety_checklists_tool"
    name: str = "get_safety_checklists"
    description: str = (
        "Retrieve safety checklists data from the construction company database"
    )
    args_schema: type[BaseModel] = SafetyChecklistsToolSchema
    output_schema: tuple[str, str] = (
        "list[dict]",
        "List of safety checklist records from the database",
    )

    def run(
        self, _: Any, priority: Optional[str] = None, status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Run the tool to get safety checklists data."""
        filters = {}
        if priority:
            filters["priority"] = priority
        if status:
            filters["status"] = status

        checklists = db_utils.get_safety_checklists(filters)
        return checklists


class DailyTasksToolSchema(BaseModel):
    """Input for DailyTasksTool."""

    priority: Optional[str] = Field(
        None, description="Filter by priority level (e.g., 'High', 'Medium', 'Low')"
    )
    completed: Optional[bool] = Field(
        None, description="Filter by completion status (true/false)"
    )


class DailyTasksTool(Tool[List[Dict[str, Any]]]):
    """Tool to retrieve daily tasks data from the database."""

    id: str = "get_daily_tasks_tool"
    name: str = "get_daily_tasks"
    description: str = (
        "Retrieve daily tasks data from the construction company database"
    )
    args_schema: type[BaseModel] = DailyTasksToolSchema
    output_schema: tuple[str, str] = (
        "list[dict]",
        "List of daily task records from the database",
    )

    def run(
        self, _: Any, priority: Optional[str] = None, completed: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """Run the tool to get daily tasks data."""
        filters = {}
        if priority:
            filters["priority"] = priority
        if completed is not None:
            filters["completed"] = completed

        tasks = db_utils.get_daily_tasks(filters)
        return tasks


class ProgressTrackingToolSchema(BaseModel):
    """Input for ProgressTrackingTool."""

    location: Optional[str] = Field(None, description="Filter by location")
    date: Optional[str] = Field(None, description="Filter by date (YYYY-MM-DD)")


class ProgressTrackingTool(Tool[List[Dict[str, Any]]]):
    """Tool to retrieve progress tracking data from the database."""

    id: str = "get_progress_tracking_tool"
    name: str = "get_progress_tracking"
    description: str = (
        "Retrieve progress tracking data from the construction company database"
    )
    args_schema: type[BaseModel] = ProgressTrackingToolSchema
    output_schema: tuple[str, str] = (
        "list[dict]",
        "List of progress tracking records from the database",
    )

    def run(
        self, _: Any, location: Optional[str] = None, date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Run the tool to get progress tracking data."""
        filters = {}
        if location:
            filters["location"] = location
        if date:
            try:
                filters["date"] = datetime.date.fromisoformat(date)
            except ValueError:
                return {"error": f"Invalid date format: {date}. Expected YYYY-MM-DD"}

        progress = db_utils.get_progress_tracking(filters)

        # Convert date objects to strings for JSON serialization
        for item in progress:
            for key, value in item.items():
                if isinstance(value, datetime.date):
                    item[key] = value.isoformat()

        return progress


class CustomQueryToolSchema(BaseModel):
    """Input for CustomQueryTool."""

    query: str = Field(
        ..., description="SQL query to execute (SELECT queries only for security)"
    )


class CustomQueryTool(Tool[List[Dict[str, Any]]]):
    """Tool to execute a custom SQL query on the database."""

    id: str = "execute_custom_query_tool"
    name: str = "execute_custom_query"
    description: str = "Execute a custom SQL query on the construction company database"
    args_schema: type[BaseModel] = CustomQueryToolSchema
    output_schema: tuple[str, str] = (
        "list[dict]",
        "Query results from the database",
    )

    def run(self, _: Any, query: str) -> Union[List[Dict[str, Any]], Dict[str, str]]:
        """Run the tool to execute a custom query."""
        # Security check: Only allow SELECT queries
        query_upper = query.strip().upper()
        if not query_upper.startswith("SELECT"):
            return {"error": "Only SELECT queries are allowed for security reasons"}

        try:
            result = db_utils.execute_query(query)

            # Convert date objects to strings for JSON serialization
            for item in result:
                if isinstance(item, dict):
                    for key, value in item.items():
                        if isinstance(value, datetime.date):
                            item[key] = value.isoformat()

            return result
        except Exception as e:
            return {"error": f"Query execution failed: {str(e)}"}


# Tool registry for construction company database
construction_db_tool_registry = [
    ProjectsTool(),
    TasksTool(),
    WorkersTool(),
    MaterialsTool(),
    SafetyIncidentsTool(),
    EquipmentTool(),
    SafetyChecklistsTool(),
    DailyTasksTool(),
    ProgressTrackingTool(),
    CustomQueryTool(),
]
