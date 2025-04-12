import os
from dotenv import load_dotenv
from portia import (
    Config,
    Portia,
    PortiaToolRegistry,
    StorageClass,
    LLMProvider,
    open_source_tool_registry,
    execution_context,
)


class PortiaWorker:
    """
    PortiaWorker class for construction company interactions
    Uses Portia to handle chat-based interactions based on role and context
    """

    def __init__(self):
        """Initialize PortiaWorker with OpenAI configuration"""
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

        # Configure Portia with OpenAI
        self.config = Config.from_default(
            storage_class=StorageClass.CLOUD, llm_provider=LLMProvider.OPENAI
        )

        # Initialize Portia
        self.portia = Portia(
            config=self.config,
            tools=PortiaToolRegistry(self.config) + open_source_tool_registry,
        )

        # Store conversation history
        self.conversation_history = []

    def process_message(self, prompt, role, context=None):
        """
        Process a message using Portia

        Args:
            prompt (str): The user's prompt/query
            role (str): The user's role (e.g., "Project Manager", "CEO")
            context (dict, optional): Additional context for the conversation

        Returns:
            dict: The response from Portia
        """
        try:
            # Build the full task with role context
            task = self._build_task(prompt, role, context)

            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": prompt})

            # Process with Portia
            with execution_context(end_user_id=f"construction_user_{role}"):
                # Create a plan
                plan = self.portia.plan(task)

                # Execute the plan
                plan_run = self.portia.run_plan(plan)

                # Get the output
                response = plan_run.outputs

                # Add to conversation history
                self.conversation_history.append(
                    {"role": "assistant", "content": str(response)}
                )

                return {
                    "status": "success",
                    "response": response,
                    "steps": [str(step) for step in plan.steps],
                }

        except Exception as e:
            error_message = f"Error processing message: {str(e)}"
            print(error_message)
            return {"status": "error", "message": error_message}

    def _build_task(self, prompt, role, context=None):
        """
        Build a task string with role and context information

        Args:
            prompt (str): The user's prompt/query
            role (str): The user's role
            context (dict, optional): Additional context

        Returns:
            str: The complete task string
        """
        # Start with role context
        task_prefix = f"As a {role} in a construction company, "

        # Add conversation context if available
        if context and "company_name" in context:
            task_prefix += f"working for {context['company_name']}, "

        # Add historical context if there's a conversation history
        if len(self.conversation_history) > 0:
            task_prefix += "considering our previous conversation, "

        # Combine with the actual prompt
        full_task = task_prefix + prompt

        return full_task

    def clear_history(self):
        """Clear the conversation history"""
        self.conversation_history = []
        return {"status": "success", "message": "Conversation history cleared"}


from dotenv import load_dotenv
from portia import (
    Config,
    Portia,
    PortiaToolRegistry,
    StorageClass,
    LLMProvider,
    open_source_tool_registry,
    execution_context,
)


class PortiaWorker:
    """
    PortiaWorker class for construction company interactions
    Uses Portia to handle chat-based interactions based on role and context
    """

    def __init__(self):
        """Initialize PortiaWorker with OpenAI configuration"""
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

        # Configure Portia with OpenAI
        self.config = Config.from_default(
            storage_class=StorageClass.CLOUD, llm_provider=LLMProvider.OPENAI
        )

        # Initialize Portia
        self.portia = Portia(
            config=self.config,
            tools=PortiaToolRegistry(self.config) + open_source_tool_registry,
        )

        # Store conversation history
        self.conversation_history = []

    def process_message(self, prompt, role, context=None):
        """
        Process a message using Portia

        Args:
            prompt (str): The user's prompt/query
            role (str): The user's role (e.g., "Project Manager", "CEO")
            context (dict, optional): Additional context for the conversation

        Returns:
            dict: The response from Portia
        """
        try:
            # Build the full task with role context
            task = self._build_task(prompt, role, context)

            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": prompt})

            # Process with Portia
            with execution_context(end_user_id=f"construction_user_{role}"):
                # Create a plan
                plan = self.portia.plan(task)

                # Execute the plan
                plan_run = self.portia.run_plan(plan)

                # Get the output
                response = plan_run.outputs

                # Add to conversation history
                self.conversation_history.append(
                    {"role": "assistant", "content": str(response)}
                )

                return {
                    "status": "success",
                    "response": response,
                    "steps": [str(step) for step in plan.steps],
                }

        except Exception as e:
            error_message = f"Error processing message: {str(e)}"
            print(error_message)
            return {"status": "error", "message": error_message}

    def _build_task(self, prompt, role, context=None):
        """
        Build a task string with role and context information

        Args:
            prompt (str): The user's prompt/query
            role (str): The user's role
            context (dict, optional): Additional context

        Returns:
            str: The complete task string
        """
        # Start with role context
        task_prefix = f"As a {role} in a construction company, "

        # Add conversation context if available
        if context and "company_name" in context:
            task_prefix += f"working for {context['company_name']}, "

        # Add historical context if there's a conversation history
        if len(self.conversation_history) > 0:
            task_prefix += "considering our previous conversation, "

        # Combine with the actual prompt
        full_task = task_prefix + prompt

        return full_task

    def clear_history(self):
        """Clear the conversation history"""
        self.conversation_history = []
        return {"status": "success", "message": "Conversation history cleared"}
