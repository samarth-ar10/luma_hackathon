#!/usr/bin/env python3
import os
import logging
import argparse
import uvicorn
from dotenv import load_dotenv

from modelcontextprotocol import MCPServer, SSEServer
from sql_mcp_server import server

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run SQL MCP Server as SSE service")
    parser.add_argument(
        "--host", type=str, default="localhost", help="Host to bind the server to"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to bind the server to"
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default=os.environ.get("SQL_MCP_DB_PATH", "sql_mcp_data.db"),
        help="Path to SQLite database file",
    )
    args = parser.parse_args()

    # Set database path environment variable
    os.environ["SQL_MCP_DB_PATH"] = args.db_path

    # Create FastAPI app with SSE server
    app = SSEServer(server).app

    logger.info(f"Starting SQL MCP SSE server at http://{args.host}:{args.port}")
    logger.info(f"Using database: {args.db_path}")

    # Run the server
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
