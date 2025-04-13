#!/usr/bin/env python3
"""
Test script to verify direct connection to LLM through both Portia and the Flask API
"""

import os
import logging
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] Test: %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("test_llm")


def test_portia_direct():
    """Test direct connection to Portia/OpenAI"""
    try:
        # Import Portia components
        from portia import Config, LLMModel, LLMProvider, Portia

        # Check if API keys are available
        portia_api_key = os.environ.get("PORTIA_API_KEY")
        openai_api_key = os.environ.get("OPENAI_API_KEY")

        if not portia_api_key:
            logger.error("PORTIA_API_KEY not found in environment variables")
            return False

        if not openai_api_key:
            logger.error("OPENAI_API_KEY not found in environment variables")
            return False

        logger.info(f"PORTIA_API_KEY found: {portia_api_key[:5]}...")
        logger.info(f"OPENAI_API_KEY found: {openai_api_key[:5]}...")

        # Initialize Portia with OpenAI model
        config = Config.from_default(llm_model_name=LLMModel.GPT_4_O)
        llm_provider = LLMProvider.OPENAI

        portia = Portia(config=config)

        # Test query
        query = "What is the tallest building in the world?"

        logger.info(f"Sending direct query to LLM: {query}")
        response = portia.query(query=query, llm_provider=llm_provider)

        logger.info(f"Response from LLM: {response}")
        return True

    except ImportError as e:
        logger.error(f"Failed to import Portia module: {e}")
        return False
    except Exception as e:
        logger.error(f"Error in direct Portia test: {e}")
        return False


def test_flask_api():
    """Test connection to LLM through Flask API"""
    try:
        # Flask API endpoint
        api_url = "http://localhost:5003/api/ask"

        # Test query
        payload = {
            "user_id": "test_user_direct",
            "role": "worker",
            "query": "What time is it in New York right now?",
        }

        logger.info(f"Sending API request to Flask: {api_url}")
        logger.info(f"Payload: {payload}")

        response = requests.post(api_url, json=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            logger.info(f"API Response: {result}")
            return True
        else:
            logger.error(f"API Error: {response.status_code} - {response.text}")
            return False

    except requests.RequestException as e:
        logger.error(f"Request error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in API test: {e}")
        return False


if __name__ == "__main__":
    logger.info("Running LLM connection tests")

    # Test direct Portia connection
    logger.info("Testing direct Portia connection...")
    portia_success = test_portia_direct()

    # Test Flask API connection
    logger.info("Testing Flask API connection...")
    api_success = test_flask_api()

    # Summary
    if portia_success:
        logger.info("✅ Direct Portia connection test PASSED")
    else:
        logger.error("❌ Direct Portia connection test FAILED")

    if api_success:
        logger.info("✅ Flask API connection test PASSED")
    else:
        logger.error("❌ Flask API connection test FAILED")
