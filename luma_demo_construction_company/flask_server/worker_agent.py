import os
from dotenv import load_dotenv
import json
import datetime
from typing import Dict, Any, Optional

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


class WorkerAgent:
    """
    Worker Agent class responsible for creating specific visualizations
    Uses Portia with GPT-4 for generating visualization code and specifications
    """

    def __init__(self, tile_id: str, worker_task: Dict[str, Any]):
        """
        Initialize Worker Agent with Portia configuration

        Args:
            tile_id (str): ID of the tile this worker is responsible for
            worker_task (dict): Task specification from the queen agent
        """
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

        # Configure Portia with OpenAI as the LLM provider (GPT-4)
        self.config = Config.from_default(
            storage_class=StorageClass.CLOUD,
            llm_provider=LLMProvider.OPENAI,
            llm_model="gpt-4",
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

        # Store tile ID and worker task
        self.tile_id = tile_id
        self.worker_task = worker_task

        # Store visualization code
        self.visualization_code = None

    def generate_visualization(
        self,
        data: Optional[Dict[str, Any]] = None,
        visualization_preference: str = "balanced",
    ) -> Dict[str, Any]:
        """
        Generate visualization code based on the worker task and data

        Args:
            data (dict, optional): The data for the visualization. If None, will fetch from DB.
            visualization_preference (str): Preferred visualization style ("technical", "balanced", or "non-technical")

        Returns:
            dict: Visualization code and specifications
        """
        # If no data provided, query the database using the worker task specification
        if data is None:
            data_source = self.worker_task.get("dataSource", "projects")
            # Use Portia to fetch data
            with execution_context(
                end_user_id=f"worker_agent_data_fetch_{self.tile_id}"
            ):
                task = f"""
                Fetch data from the database for visualization.
                Use the get_{data_source} tool to retrieve all records from the {data_source} table.
                """
                plan_run = self.portia.run(task)
                data = plan_run.outputs

        # Build prompt for visualization generation with preference
        prompt = self._build_visualization_prompt(data, visualization_preference)

        # Use Portia to run the task
        with execution_context(end_user_id=f"worker_agent_{self.tile_id}"):
            task = f"""
            You are a data visualization expert specializing in React. Your task is to create 
            visualization code based on the requirements.
            
            {prompt}
            """

            # Execute the task
            plan_run = self.portia.run(task)

            # Parse the response
            visualization_response = plan_run.outputs

        # Extract code from the response
        self.visualization_code = self._extract_code(str(visualization_response))

        # Build metadata about the visualization
        metadata = self._build_visualization_metadata(visualization_preference)

        return {
            "tile_id": self.tile_id,
            "code": self.visualization_code,
            "metadata": metadata,
            "data": data,
            "visualization_preference": visualization_preference,
        }

    def update_visualization(
        self,
        data: Optional[Dict[str, Any]] = None,
        feedback: Optional[str] = None,
        visualization_preference: str = "balanced",
    ) -> Dict[str, Any]:
        """
        Update existing visualization based on new data or feedback

        Args:
            data (dict, optional): The updated data for the visualization. If None, will fetch from DB.
            feedback (str, optional): User feedback for the visualization
            visualization_preference (str): Preferred visualization style ("technical", "balanced", or "non-technical")

        Returns:
            dict: Updated visualization code and specifications
        """
        # If no data provided, query the database using the worker task specification
        if data is None:
            data_source = self.worker_task.get("dataSource", "projects")
            # Use Portia to fetch data
            with execution_context(
                end_user_id=f"worker_agent_update_data_fetch_{self.tile_id}"
            ):
                task = f"""
                Fetch updated data from the database for visualization.
                Use the get_{data_source} tool to retrieve all records from the {data_source} table.
                """
                plan_run = self.portia.run(task)
                data = plan_run.outputs

        # Build prompt for visualization update with preference
        prompt = self._build_update_prompt(data, feedback, visualization_preference)

        # Use Portia to run the task
        with execution_context(end_user_id=f"worker_agent_update_{self.tile_id}"):
            task = f"""
            You are a data visualization expert specializing in React. Your task is to update 
            visualization code based on new data or feedback.
            
            {prompt}
            """

            # Execute the task
            plan_run = self.portia.run(task)

            # Parse the response
            visualization_response = plan_run.outputs

        # Extract code from the response
        self.visualization_code = self._extract_code(str(visualization_response))

        # Build metadata about the visualization
        metadata = self._build_visualization_metadata(visualization_preference)

        return {
            "tile_id": self.tile_id,
            "code": self.visualization_code,
            "metadata": metadata,
            "data": data,
            "visualization_preference": visualization_preference,
        }

    def _build_visualization_prompt(
        self, data: Dict[str, Any], visualization_preference: str = "balanced"
    ) -> str:
        """
        Build prompt for visualization generation

        Args:
            data (dict): The data for the visualization
            visualization_preference (str): Preferred visualization style

        Returns:
            str: Prompt for Portia
        """
        # Extract information from worker task
        data_source = self.worker_task.get("dataSource", "")
        vis_specs = self.worker_task.get("visualizationSpecs", {})
        interactivity = self.worker_task.get("interactivity", {})

        # Convert data to a string representation
        data_str = json.dumps(data, indent=2)

        # Adapt style based on visualization preference
        style_guidance = ""
        if visualization_preference == "technical":
            style_guidance = """
            Create a technical visualization that:
            1. Prioritizes detailed information and precise numbers
            2. Uses tables with comprehensive data when appropriate
            3. Includes detailed labels, statistics, and metrics
            4. Shows data in its most complete form
            5. Minimizes decorative elements in favor of information density
            """
        elif visualization_preference == "non-technical":
            style_guidance = """
            Create a non-technical visualization that:
            1. Prioritizes visual clarity and intuitive understanding
            2. Uses charts, graphs, and visual elements instead of detailed tables when possible
            3. Simplifies numerical data into percentages or ratings
            4. Emphasizes color coding and visual patterns
            5. Reduces technical jargon and complex metrics
            """
        else:  # balanced
            style_guidance = """
            Create a balanced visualization that:
            1. Combines visual elements with appropriate level of detail
            2. Uses the most appropriate chart type for the data
            3. Includes key metrics and numbers without overwhelming the view
            4. Maintains a good balance between information density and visual appeal
            5. Works well for both technical and non-technical users
            """

        prompt = f"""
        Create a React component for a visualization with the following specifications:
        
        Tile ID: {self.tile_id}
        Data Source: {data_source}
        Visualization Specifications: {json.dumps(vis_specs, indent=2)}
        Interactivity Features: {json.dumps(interactivity, indent=2)}
        Visualization Preference: {visualization_preference}
        
        {style_guidance}
        
        The data for this visualization is:
        ```json
        {data_str}
        ```
        
        Please create a React functional component that:
        1. Uses an appropriate visualization library (e.g., Recharts, Nivo, Victory, or D3)
        2. Follows React best practices
        3. Includes the interactivity features specified
        4. Is responsive and adapts to different screen sizes
        5. Handles loading states and potential errors
        6. Uses modern React patterns (hooks, etc.)
        
        The component should be named '{self.tile_id.replace("-", "")}Visualization' and should accept props for data and config.
        
        Return only the complete React component code without any explanations or comments.
        """

        return prompt

    def _build_update_prompt(
        self,
        data: Dict[str, Any],
        feedback: Optional[str] = None,
        visualization_preference: str = "balanced",
    ) -> str:
        """
        Build prompt for visualization update

        Args:
            data (dict): The updated data for the visualization
            feedback (str, optional): User feedback for the visualization
            visualization_preference (str): Preferred visualization style

        Returns:
            str: Prompt for Portia
        """
        # Convert data to a string representation
        data_str = json.dumps(data, indent=2)

        # Include style guidance based on visualization preference
        style_guidance = ""
        if visualization_preference == "technical":
            style_guidance = """
            Ensure the updated visualization:
            1. Prioritizes detailed information and precise numbers
            2. Uses tables with comprehensive data when appropriate
            3. Includes detailed labels, statistics, and metrics
            4. Shows data in its most complete form
            5. Minimizes decorative elements in favor of information density
            """
        elif visualization_preference == "non-technical":
            style_guidance = """
            Ensure the updated visualization:
            1. Prioritizes visual clarity and intuitive understanding
            2. Uses charts, graphs, and visual elements instead of detailed tables when possible
            3. Simplifies numerical data into percentages or ratings
            4. Emphasizes color coding and visual patterns
            5. Reduces technical jargon and complex metrics
            """
        else:  # balanced
            style_guidance = """
            Ensure the updated visualization:
            1. Combines visual elements with appropriate level of detail
            2. Uses the most appropriate chart type for the data
            3. Includes key metrics and numbers without overwhelming the view
            4. Maintains a good balance between information density and visual appeal
            5. Works well for both technical and non-technical users
            """

        prompt = f"""
        Update the following React visualization component with new data and address any feedback.
        
        Current visualization code:
        ```jsx
        {self.visualization_code}
        ```
        
        Updated data:
        ```json
        {data_str}
        ```

        Visualization Preference: {visualization_preference}
        
        {style_guidance}
        """

        if feedback:
            prompt += f"""
            User feedback to address:
            {feedback}
            """

        prompt += """
        Please modify the React component to:
        1. Work with the updated data
        2. Address the user feedback (if provided)
        3. Maintain all existing functionality
        4. Ensure the component is optimized for performance
        5. Match the specified visualization preference style
        
        Return only the complete updated React component code without any explanations or comments.
        """

        return prompt

    def _extract_code(self, response: str) -> str:
        """
        Extract code from LLM response

        Args:
            response (str): The response from the LLM

        Returns:
            str: Extracted code
        """
        # Look for code blocks (```jsx or ```)
        if "```jsx" in response:
            code_blocks = response.split("```jsx")
            if len(code_blocks) > 1:
                code = code_blocks[1].split("```")[0].strip()
                return code

        if "```" in response:
            code_blocks = response.split("```")
            if len(code_blocks) > 1:
                code = code_blocks[1].strip()
                return code

        # If no code blocks are found, return the entire response
        return response.strip()

    def _build_visualization_metadata(
        self, visualization_preference: str = "balanced"
    ) -> Dict[str, Any]:
        """
        Build metadata about the visualization

        Args:
            visualization_preference (str): Preferred visualization style

        Returns:
            dict: Visualization metadata
        """
        # Extract information from worker task
        data_source = self.worker_task.get("dataSource", "")
        vis_specs = self.worker_task.get("visualizationSpecs", {})
        vis_type = vis_specs.get("type", "unknown")

        return {
            "type": vis_type,
            "dataSource": data_source,
            "generatedAt": str(datetime.datetime.now()),
            "library": self._infer_visualization_library(),
            "interactivity": self.worker_task.get("interactivity", {}),
            "visualizationPreference": visualization_preference,
        }

    def _infer_visualization_library(self) -> str:
        """
        Infer the visualization library used in the code

        Returns:
            str: Name of the visualization library
        """
        code = self.visualization_code or ""

        libraries = {
            "recharts": ["Recharts", "LineChart", "BarChart", "PieChart", "AreaChart"],
            "nivo": [
                "ResponsiveLine",
                "ResponsiveBar",
                "ResponsivePie",
                "ResponsiveHeatMap",
            ],
            "victory": ["VictoryChart", "VictoryLine", "VictoryBar", "VictoryPie"],
            "d3": ["d3.select", "d3.scale", "d3.axis", "d3.line"],
            "visx": ["BarGroup", "LinePath", "Pie", "Heatmap"],
        }

        for lib, keywords in libraries.items():
            for keyword in keywords:
                if keyword in code:
                    return lib

        return "unknown"
