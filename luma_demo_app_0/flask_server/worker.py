import os
import json
from dotenv import load_dotenv
import openai
import anthropic


class Worker:
    """
    Worker class responsible for generating UI (HTML and CSS) based on
    company data and design restrictions provided by QueenWorker.
    """

    def __init__(self):
        """Initialize the Worker with API keys from environment variables."""
        load_dotenv()
        # Load configuration from environment
        self.use_anthropic = os.getenv("USE_ANTHROPIC", "False").lower() in (
            "true",
            "1",
            "t",
        )

        if self.use_anthropic:
            # Use Anthropic/Claude
            anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
            if not anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
            self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
            self.model = "claude-3-opus-20240229"
        else:
            # Use OpenAI
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            openai.api_key = openai_api_key
            self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    def generate_completion(self, system_prompt, user_prompt):
        """Generate a completion using either Anthropic or OpenAI based on configuration."""
        try:
            if self.use_anthropic:
                # Use Anthropic/Claude
                response = self.anthropic_client.messages.create(
                    model=self.model,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                    max_tokens=4000,
                )
                return response.content[0].text
            else:
                # Use OpenAI
                response = openai.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.7,
                    max_tokens=4000,
                )
                return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating completion: {str(e)}")
            raise

    def generate_ui(self, company_data, design_restrictions):
        """
        Generate HTML and CSS for a construction company website based on provided data and design restrictions.

        Args:
            company_data (dict): Data about the construction company
            design_restrictions (dict): Design guidelines to follow for UI generation

        Returns:
            dict: Contains HTML and CSS for the generated UI
        """
        try:
            # Format the company data and design restrictions as a JSON string
            data_json = json.dumps(
                {
                    "company_data": company_data,
                    "design_restrictions": design_restrictions,
                },
                indent=2,
            )

            system_prompt = "You are a skilled UI/UX designer and front-end developer specializing in construction company websites."

            # Create a prompt for generating the UI
            user_prompt = f"""
            Generate HTML and CSS for a construction company website based on the following data and design restrictions:
            
            {data_json}
            
            Please follow these guidelines:
            1. The HTML should be valid and modern, using semantic tags where appropriate
            2. Use the provided color scheme and fonts from the design restrictions
            3. Include all sections specified in the design restrictions
            4. Make the design responsive and mobile-friendly
            5. Implement any special requirements specified in the design restrictions
            6. The CSS should be clean and well-organized
            7. Focus on creating a professional and visually appealing design for a construction company
            8. Include utility classes where appropriate for maintainability
            9. Make sure the design is complete and ready to use
            
            Return both the HTML and CSS in separate blocks, with the HTML code in a block starting with ```html and ending with ```, and the CSS code in a block starting with ```css and ending with ```.
            """

            # Get response from the chosen API
            content = self.generate_completion(system_prompt, user_prompt)

            # Parse the content to extract HTML and CSS
            html_content = ""
            css_content = ""

            # Check if there are markdown code blocks
            if "```html" in content and "```css" in content:
                # Extract HTML
                html_start = content.find("```html") + 7
                html_end = content.find("```", html_start)
                html_content = content[html_start:html_end].strip()

                # Extract CSS
                css_start = content.find("```css") + 6
                css_end = content.find("```", css_start)
                css_content = content[css_start:css_end].strip()
            else:
                # If no markdown blocks, try to infer from content structure
                parts = content.split("CSS:")
                if len(parts) > 1:
                    html_part = parts[0]
                    if "HTML:" in html_part:
                        html_content = html_part.split("HTML:")[1].strip()
                    else:
                        html_content = html_part.strip()
                    css_content = parts[1].strip()
                else:
                    # If all else fails, return the entire content as HTML
                    html_content = content

            return {"html": html_content, "css": css_content}

        except Exception as e:
            error_message = f"Failed to generate UI: {str(e)}"
            print(f"Error: {error_message}")
            # Return an error response that includes html and css to prevent KeyError
            return {
                "error": error_message,
                "html": "<div class='error'>UI generation failed. Please try again.</div>",
                "css": ".error { color: red; padding: 20px; text-align: center; }",
            }

    def generate_ui_from_prompt(self, prompt):
        """
        Generate HTML and CSS based on a user-provided prompt.

        Args:
            prompt (str): User's description of the desired UI

        Returns:
            dict: Contains HTML and CSS for the generated UI
        """
        try:
            system_prompt = "You are a skilled UI/UX designer and front-end developer specializing in construction company websites."

            # Create a more detailed prompt for generating the UI
            user_prompt = f"""
            Generate HTML and CSS for a construction industry website based on the following user prompt:
            
            "{prompt}"
            
            Please follow these guidelines:
            1. The HTML should be valid and modern, using semantic tags where appropriate
            2. Choose an appropriate color scheme and fonts for a construction company
            3. Include common sections such as header, about, services, projects, and contact
            4. Make the design responsive and mobile-friendly
            5. The CSS should be clean and well-organized
            6. Focus on creating a professional and visually appealing design
            7. Include utility classes where appropriate for maintainability
            8. Make sure the design is complete and ready to use
            
            Return both the HTML and CSS in separate blocks, with the HTML code in a block starting with ```html and ending with ```, and the CSS code in a block starting with ```css and ending with ```.
            """

            # Get response from the chosen API
            content = self.generate_completion(system_prompt, user_prompt)

            # Parse the content to extract HTML and CSS
            html_content = ""
            css_content = ""

            # Check if there are markdown code blocks
            if "```html" in content and "```css" in content:
                # Extract HTML
                html_start = content.find("```html") + 7
                html_end = content.find("```", html_start)
                html_content = content[html_start:html_end].strip()

                # Extract CSS
                css_start = content.find("```css") + 6
                css_end = content.find("```", css_start)
                css_content = content[css_start:css_end].strip()
            else:
                # If no markdown blocks, try to infer from content structure
                parts = content.split("CSS:")
                if len(parts) > 1:
                    html_part = parts[0]
                    if "HTML:" in html_part:
                        html_content = html_part.split("HTML:")[1].strip()
                    else:
                        html_content = html_part.strip()
                    css_content = parts[1].strip()
                else:
                    # If all else fails, return the entire content as HTML
                    html_content = content

            return {"html": html_content, "css": css_content}

        except Exception as e:
            error_message = f"Failed to generate UI from prompt: {str(e)}"
            print(f"Error: {error_message}")
            # Return an error response that includes html and css to prevent KeyError
            return {
                "error": error_message,
                "html": "<div class='error'>UI generation failed. Please try again.</div>",
                "css": ".error { color: red; padding: 20px; text-align: center; }",
            }

    def generate_ui_with_data(self, company_data, prompt):
        """
        Generate HTML and CSS based on company data and a user-provided prompt.

        Args:
            company_data (dict): Data about the construction company
            prompt (str): User's description of the desired UI

        Returns:
            dict: Contains HTML and CSS for the generated UI
        """
        try:
            # Format the company data as a JSON string
            data_json = json.dumps(company_data, indent=2)

            system_prompt = "You are a skilled UI/UX designer and front-end developer specializing in construction company websites."

            # Create a prompt for generating the UI that incorporates both the company data and user prompt
            user_prompt = f"""
            Generate HTML and CSS for a construction company website based on the following company data:
            
            {data_json}
            
            And following the user's requirements:
            
            "{prompt}"
            
            Please follow these guidelines:
            1. The HTML should be valid and modern, using semantic tags where appropriate
            2. Choose an appropriate color scheme and fonts that match the company's brand
            3. Include all necessary sections to showcase the company's services, projects, and team
            4. Make the design responsive and mobile-friendly
            5. The CSS should be clean and well-organized
            6. Focus on creating a professional and visually appealing design
            7. Include utility classes where appropriate for maintainability
            8. Make sure the design is complete and ready to use
            
            Return both the HTML and CSS in separate blocks, with the HTML code in a block starting with ```html and ending with ```, and the CSS code in a block starting with ```css and ending with ```.
            """

            # Get response from the chosen API
            content = self.generate_completion(system_prompt, user_prompt)

            # Parse the content to extract HTML and CSS
            html_content = ""
            css_content = ""

            # Check if there are markdown code blocks
            if "```html" in content and "```css" in content:
                # Extract HTML
                html_start = content.find("```html") + 7
                html_end = content.find("```", html_start)
                html_content = content[html_start:html_end].strip()

                # Extract CSS
                css_start = content.find("```css") + 6
                css_end = content.find("```", css_start)
                css_content = content[css_start:css_end].strip()
            else:
                # If no markdown blocks, try to infer from content structure
                parts = content.split("CSS:")
                if len(parts) > 1:
                    html_part = parts[0]
                    if "HTML:" in html_part:
                        html_content = html_part.split("HTML:")[1].strip()
                    else:
                        html_content = html_part.strip()
                    css_content = parts[1].strip()
                else:
                    # If all else fails, return the entire content as HTML
                    html_content = content

            return {"html": html_content, "css": css_content}

        except Exception as e:
            error_message = f"Failed to generate UI with data from prompt: {str(e)}"
            print(f"Error: {error_message}")
            # Return an error response that includes empty html and css to prevent KeyError
            return {
                "error": error_message,
                "html": "<div class='error'>UI generation failed. Please try again.</div>",
                "css": ".error { color: red; padding: 20px; text-align: center; }",
            }


# Test the class if run directly
if __name__ == "__main__":
    from queen_worker import QueenWorker

    queen = QueenWorker()
    worker = Worker()

    # Generate company data and design restrictions
    data = queen.get_data_and_restrictions()

    # Generate UI based on the data
    ui = worker.generate_ui(data["company_data"], data["design_restrictions"])

    # Print the first 200 characters of HTML and CSS
    print("HTML preview:", ui["html"][:200] + "...")
    print("CSS preview:", ui["css"][:200] + "...")
