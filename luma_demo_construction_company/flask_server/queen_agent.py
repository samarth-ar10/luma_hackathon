import os
from dotenv import load_dotenv
from typing import Dict, Any
import json

from portia import (
    Config,
    Portia,
    PortiaToolRegistry,
    StorageClass,
    LLMProvider,
    open_source_tool_registry,
    execution_context,
)

from db_tools import construction_db_tool_registry

# Load environment variables
load_dotenv()


class QueenAgent:
    """
    Queen Agent class responsible for overall website design and coordination
    Uses Portia with GPT-4o for high-level decision making and design
    """

    def __init__(self):
        """Initialize Queen Agent with Portia configuration"""
        # Load environment variables
        load_dotenv()

        # Ensure OPENAI_API_KEY is set
        if not os.getenv("OPENAI_API_KEY"):
            # For development, use shared key if not set
            os.environ["OPENAI_API_KEY"] = "luma_hackathon_shared_key"
            print("Using shared OpenAI API key")

        # Ensure PORTIA_API_KEY is set
        if not os.getenv("PORTIA_API_KEY"):
            os.environ["PORTIA_API_KEY"] = "luma_hackathon_shared_key"
            print("Using shared Portia API key")

        # Configure Portia with OpenAI as the LLM provider (GPT-4o)
        self.config = Config.from_default(
            storage_class=StorageClass.CLOUD,
            llm_provider=LLMProvider.OPENAI,
            llm_model="gpt-4o",
        )

        # Set up the tools registry with database tools
        self.tools_registry = (
            PortiaToolRegistry(self.config)
            + open_source_tool_registry
            + construction_db_tool_registry
        )

        # Initialize Portia with tools
        self.portia = Portia(
            config=self.config,
            tools=self.tools_registry,
        )

        # Store design decisions
        self.design_decisions = {}

        # Store worker agents
        self.worker_agents = {}

    def design_layout(
        self, company_type: str, role_type: str, constraints: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Design the overall layout for a specific company type and role

        Args:
            company_type (str): Type of company (e.g., "construction")
            role_type (str): Role within the company (e.g., "project_manager")
            constraints (dict, optional): Design constraints/requirements

        Returns:
            dict: Layout design including tiles, components, and styling
        """
        # Build prompt for layout design
        prompt = self._build_layout_prompt(company_type, role_type, constraints)

        # Use Portia to run the task with GPT-4o and database tools
        with execution_context(end_user_id=f"queen_agent_{company_type}_{role_type}"):
            task = f"""
            You are a UI/UX expert specializing in dashboard design. 
            Your task is to create a professional, intuitive layout for a business dashboard based on the requirements.
            
            First, use the provided database tools to understand the available data about {company_type} for the {role_type} role.
            Then design an appropriate dashboard layout based on that data.
            
            {prompt}
            
            Return the result as a valid JSON object.
            """

            # Execute the task
            plan_run = self.portia.run(task)

            # Parse the response
            result = plan_run.outputs

            try:
                # Try to parse the result as JSON
                if isinstance(result, str):
                    layout_design = json.loads(result)
                else:
                    layout_design = result
            except json.JSONDecodeError:
                # If parsing fails, extract JSON from the text response
                try:
                    json_str = self._extract_json(result)
                    layout_design = json.loads(json_str)
                except:
                    # Fallback to string representation
                    layout_design = {
                        "error": "Failed to parse JSON",
                        "raw_response": str(result),
                    }

        # Store design decision
        key = f"{company_type}_{role_type}"
        self.design_decisions[key] = layout_design

        return layout_design

    def assign_worker_tasks(
        self, layout_design: Dict[str, Any], data_source: Dict[str, Any] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Assign visualization tasks to worker agents based on layout design

        Args:
            layout_design (dict): Layout design from design_layout
            data_source (dict, optional): Information about available data sources
                                          If None, will use database tools to get the information

        Returns:
            dict: Dictionary mapping tile IDs to worker tasks
        """
        worker_tasks = {}

        # If no data_source provided, create one based on database schema
        if data_source is None:
            data_source = {
                "projects": {
                    "description": "Construction project information",
                    "fields": [
                        {"name": "project_id", "type": "string"},
                        {"name": "name", "type": "string"},
                        {"name": "start_date", "type": "date"},
                        {"name": "end_date", "type": "date"},
                        {"name": "status", "type": "string"},
                        {"name": "budget", "type": "number"},
                        {"name": "spent", "type": "number"},
                        {"name": "location", "type": "string"},
                        {"name": "manager", "type": "string"},
                    ],
                },
                "tasks": {
                    "description": "Construction tasks and activities",
                    "fields": [
                        {"name": "task_id", "type": "string"},
                        {"name": "project_id", "type": "string"},
                        {"name": "name", "type": "string"},
                        {"name": "start_date", "type": "date"},
                        {"name": "end_date", "type": "date"},
                        {"name": "status", "type": "string"},
                        {"name": "assigned_to", "type": "string"},
                        {"name": "priority", "type": "string"},
                        {"name": "completion_percentage", "type": "number"},
                    ],
                },
                "workers": {
                    "description": "Construction workers information",
                    "fields": [
                        {"name": "worker_id", "type": "string"},
                        {"name": "name", "type": "string"},
                        {"name": "role", "type": "string"},
                        {"name": "skills", "type": "array"},
                        {"name": "certification", "type": "array"},
                        {"name": "hourly_rate", "type": "number"},
                        {"name": "availability", "type": "string"},
                    ],
                },
                "materials": {
                    "description": "Construction materials inventory",
                    "fields": [
                        {"name": "material_id", "type": "string"},
                        {"name": "name", "type": "string"},
                        {"name": "category", "type": "string"},
                        {"name": "unit", "type": "string"},
                        {"name": "quantity", "type": "number"},
                        {"name": "price_per_unit", "type": "number"},
                        {"name": "supplier", "type": "string"},
                        {"name": "last_ordered", "type": "date"},
                    ],
                },
                "safety": {
                    "description": "Safety incidents and reports",
                    "fields": [
                        {"name": "incident_id", "type": "string"},
                        {"name": "project_id", "type": "string"},
                        {"name": "date", "type": "date"},
                        {"name": "type", "type": "string"},
                        {"name": "severity", "type": "string"},
                        {"name": "description", "type": "string"},
                        {"name": "reported_by", "type": "string"},
                        {"name": "status", "type": "string"},
                    ],
                },
                "equipment": {
                    "description": "Construction equipment tracking",
                    "fields": [
                        {"name": "equipment_id", "type": "string"},
                        {"name": "name", "type": "string"},
                        {"name": "type", "type": "string"},
                        {"name": "status", "type": "string"},
                        {"name": "location", "type": "string"},
                        {"name": "last_maintenance", "type": "date"},
                        {"name": "next_maintenance", "type": "date"},
                        {"name": "assigned_to", "type": "string"},
                    ],
                },
            }

        for tile_id, tile_config in layout_design.get("tiles", {}).items():
            # Build prompt for worker assignment
            prompt = self._build_worker_prompt(tile_id, tile_config, data_source)

            # Use Portia to run the task
            with execution_context(
                end_user_id=f"queen_agent_task_assignment_{tile_id}"
            ):
                task = f"""
                You are a data visualization expert. Your task is to assign the 
                appropriate visualization type and data requirements to a worker agent.
                
                First, use the database tools to see what data is available that would be 
                relevant for a visualization described as: {tile_config.get('title', '')}
                
                {prompt}
                
                Return the result as a valid JSON object.
                """

                # Execute the task
                plan_run = self.portia.run(task)

                # Parse the response
                result = plan_run.outputs

                try:
                    # Try to parse the result as JSON
                    if isinstance(result, str):
                        worker_task = json.loads(result)
                    else:
                        worker_task = result
                except json.JSONDecodeError:
                    # If parsing fails, extract JSON from the text response
                    try:
                        json_str = self._extract_json(result)
                        worker_task = json.loads(json_str)
                    except:
                        # Fallback to string representation
                        worker_task = {
                            "error": "Failed to parse JSON",
                            "dataSource": "projects",
                            "requiredFields": ["name", "status", "budget", "spent"],
                            "raw_response": str(result),
                        }

            # Store worker task
            worker_tasks[tile_id] = worker_task

        return worker_tasks

    def _build_layout_prompt(
        self, company_type: str, role_type: str, constraints: Dict[str, Any] = None
    ) -> str:
        """
        Build prompt for layout design

        Args:
            company_type (str): Type of company
            role_type (str): Role within the company
            constraints (dict, optional): Design constraints/requirements

        Returns:
            str: Prompt for Portia
        """
        prompt = f"""
        Design a professional dashboard layout for a {company_type} company, specifically for a {role_type} role.
        
        The layout should include:
        1. An appropriate number of tiles/cards for key metrics and visualizations
        2. A logical arrangement of these tiles based on their importance and relationship
        3. A color scheme appropriate for a {company_type} company
        4. Responsive design considerations
        
        Each tile should have:
        - A unique ID
        - A title
        - A description of what data should be displayed
        - The type of visualization (chart, table, list, etc.)
        - Size (small, medium, large) and positioning information
        """

        if constraints:
            prompt += "\n\nAdditional constraints/requirements:"
            for key, value in constraints.items():
                prompt += f"\n- {key}: {value}"

        prompt += """
        
        Return a JSON object with the following structure:
        {
            "layout": {
                "columns": <number of columns>,
                "maxWidth": <max width in px>,
                "background": <background color>,
                "fontFamily": <primary font family>
            },
            "colorScheme": {
                "primary": <primary color>,
                "secondary": <secondary color>,
                "accent": <accent color>,
                "text": <text color>,
                "background": <background color>
            },
            "tiles": {
                "<tile_id>": {
                    "title": "<title>",
                    "description": "<description>",
                    "visualizationType": "<chart_type>",
                    "size": "<size>",
                    "position": {
                        "row": <row_start>,
                        "column": <column_start>,
                        "rowSpan": <row_span>,
                        "columnSpan": <column_span>
                    },
                    "dataRequirements": [
                        {"field": "<field_name>", "type": "<data_type>", "required": <boolean>}
                    ]
                }
            }
        }
        """

        return prompt

    def _build_worker_prompt(
        self, tile_id: str, tile_config: Dict[str, Any], data_source: Dict[str, Any]
    ) -> str:
        """
        Build prompt for worker assignment

        Args:
            tile_id (str): ID of the tile
            tile_config (dict): Configuration for the tile
            data_source (dict): Information about available data sources

        Returns:
            str: Prompt for Portia
        """
        visualization_type = tile_config.get("visualizationType", "chart")
        title = tile_config.get("title", "")
        description = tile_config.get("description", "")

        prompt = f"""
        As a data visualization expert, assign appropriate specifications for a worker agent to create a {visualization_type} visualization for a tile with ID "{tile_id}".
        
        Tile information:
        - Title: {title}
        - Description: {description}
        - Visualization Type: {visualization_type}
        
        Available data sources:
        """

        for source_name, source_info in data_source.items():
            prompt += f"\n- {source_name}: {source_info.get('description', '')}"
            if "fields" in source_info:
                prompt += "\n  Fields:"
                for field in source_info["fields"]:
                    prompt += f"\n  - {field.get('name', '')}: {field.get('type', '')}"

        prompt += """
        
        Return a JSON object with:
        1. The data source(s) to use
        2. Specific fields required from the data source(s)
        3. Any transformations needed on the data
        4. Detailed visualization specifications (chart type, axes, colors, etc.)
        5. Any interactive features to implement
        
        JSON format:
        {
            "dataSource": "<source_name>",
            "requiredFields": ["<field1>", "<field2>", ...],
            "dataTransformations": [
                {"type": "<transformation_type>", "parameters": {...}}
            ],
            "visualizationSpecs": {
                "type": "<specific_chart_type>",
                "xAxis": {"field": "<field_name>", "label": "<label>"},
                "yAxis": {"field": "<field_name>", "label": "<label>"},
                "colors": ["<color1>", "<color2>", ...],
                "legend": <boolean>,
                "tooltip": <boolean>
            },
            "interactivity": {
                "filtering": <boolean>,
                "sorting": <boolean>,
                "drilling": <boolean>,
                "tooltips": <boolean>
            }
        }
        """

        return prompt

    def _extract_json(self, text):
        """Extract JSON from a text string that may contain other content"""
        if not isinstance(text, str):
            return "{}"

        # Try to find JSON between curly braces
        start_idx = text.find("{")
        if start_idx == -1:
            return "{}"

        # Find the matching closing brace
        brace_count = 0
        for i in range(start_idx, len(text)):
            if text[i] == "{":
                brace_count += 1
            elif text[i] == "}":
                brace_count -= 1
                if brace_count == 0:
                    return text[start_idx : i + 1]

        return "{}"
