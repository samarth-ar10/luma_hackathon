#!/usr/bin/env python3
"""
Test script to verify connection to LLM through worker_ai.py
"""

import sys
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] Test: %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("test")

# Add parent directory to python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import worker_ai module
try:
    from flask_server.worker_ai import WorkerAIManager, PORTIA_AVAILABLE

    logger.info(
        f"Worker AI module imported successfully. Portia available: {PORTIA_AVAILABLE}"
    )
except ImportError as e:
    logger.error(f"Failed to import worker_ai module: {e}")
    sys.exit(1)


def test_worker_ai_message():
    """
    Test sending a message through worker_ai to verify LLM connectivity
    """
    # Initialize the WorkerAIManager
    try:
        manager = WorkerAIManager(db_path="construction_data.db")
        logger.info(f"WorkerAIManager initialized with {len(manager.workers)} roles")

        # Test roles available
        roles = manager.get_available_roles()
        logger.info(f"Available roles: {roles}")

        # Test message with each role
        test_user_id = "test_user_123"
        test_message = "Hello, can you give me a quick summary of today's tasks?"

        for role in roles:
            logger.info(f"Testing message with role: {role}")
            response = manager.process_message(
                user_id=test_user_id,
                role=role,
                message=test_message,
                context={"test": True},
            )

            logger.info(f"Response from {role} role: {response}")

        return True
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False


if __name__ == "__main__":
    logger.info("Starting Worker AI test")
    success = test_worker_ai_message()

    if success:
        logger.info("Test completed successfully")
    else:
        logger.error("Test failed")
        sys.exit(1)
