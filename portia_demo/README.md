# Portia Demo Project - Company Data Flow Manager

This project demonstrates a company data flow manager with AI integration using Portia and a React frontend.

## Project Structure

- **`flask_server/`**: Flask server connecting the web UI with LLM functionality
  - Serves API endpoints for data and AI queries
  - Integrates with Portia for AI capabilities
  - Contains database access logic

- **`webui/`**: React-based web UI
  - Dashboard for company statistics
  - Role-specific views for different departments
  - AI-powered assistant for natural language queries

- **`sql_demo/`**: SQL database tools and utilities
  - Basic SQLite implementation with company data
  - SQL query execution functions

- **`custom_tools.py`**: Custom Portia tools for SQL database access
  - Enables the AI to query and understand the database schema
  - Provides secure database access capabilities

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js and npm
- OpenAI API key
- Portia API key

### Installation

1. Set up your environment variables in `.env`:
```
PORTIA_API_KEY=your-portia-api-key
OPENAI_API_KEY=your-openai-api-key
SQL_MCP_DB_PATH=portia_demo/sql_data.db
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install React dependencies:
```bash
cd webui
npm install
```

### Starting the App with AI Functionality

1. Initialize the database (first time only):
```bash
cd /path/to/portia_demo
python flask_server/init_db.py
```

2. Start the Flask server:
```bash
cd /path/to/portia_demo
python flask_server/simple_app.py
```
This will start the Flask server on http://localhost:9000

3. In a separate terminal, start the React frontend:
```bash
cd /path/to/portia_demo/webui
npm start
```
This will launch the React app on http://localhost:3000

4. Open your browser to http://localhost:3000 to use the application

## Using the AI Assistant

The AI Assistant tab provides a natural language interface to query your company data. Some example questions you can ask:

- "How is the marketing department performing?"
- "Show me our current revenue statistics"
- "What projects are currently active in the engineering department?"
- "Show me all employees in the sales department"

The AI is powered by Portia, which enables:
- Structured planning for natural language queries
- Transparent execution of database queries
- Contextual understanding of your company data

## API Endpoints

- **GET /api/stats**: Company-wide statistics for the dashboard
- **GET /api/roles/{role}**: Data specific to a given role (ceo, marketing, sales, etc.)
- **POST /api/ask**: Natural language query endpoint for the AI assistant 
- **POST /api/query**: Execute SQL queries directly

## Troubleshooting

If you encounter issues:

1. Ensure your API keys are correctly set in `.env`
2. Check that the database exists at the specified path
3. Verify the Flask server is running on port 9000
4. Check browser console for any frontend errors

## License

See the LICENSE file for details. 