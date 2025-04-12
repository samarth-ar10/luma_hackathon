# Construction Company Flask Server

A Flask server implementing Portia for construction company chat interactions. This server provides a simple API for role-based interactions in a construction company context.

## Setup

1. Clone the repository
2. Navigate to the `flask_server` directory
3. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Create a `.env` file based on `.env.example` and add your API keys:
   ```
   cp .env.example .env
   ```
6. Start the server:
   ```
   python app.py
   ```

## API Endpoints

### Health Check
```
GET /health
```
Returns a simple status to confirm the server is running.

### Chat
```
POST /chat
```
Process a chat message using Portia.

**Request Body:**
```json
{
  "prompt": "What are the safety protocols for high-rise construction?",
  "role": "Safety Officer",
  "context": {
    "company_name": "Elite Builders"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "response": "...",
  "steps": [...]
}
```

### Clear History
```
POST /clear-history
```
Clears the conversation history.

### Get Roles
```
GET /roles
```
Returns a list of available construction company roles.

## Using with React

Example fetch request from React:

```javascript
const sendMessage = async (prompt, role) => {
  try {
    const response = await fetch('http://localhost:5000/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt,
        role,
        context: {
          company_name: 'Elite Builders'
        }
      }),
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error sending message:', error);
    return { status: 'error', message: error.message };
  }
};
``` 

A Flask server implementing Portia for construction company chat interactions. This server provides a simple API for role-based interactions in a construction company context.

## Setup

1. Clone the repository
2. Navigate to the `flask_server` directory
3. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Create a `.env` file based on `.env.example` and add your API keys:
   ```
   cp .env.example .env
   ```
6. Start the server:
   ```
   python app.py
   ```

## API Endpoints

### Health Check
```
GET /health
```
Returns a simple status to confirm the server is running.

### Chat
```
POST /chat
```
Process a chat message using Portia.

**Request Body:**
```json
{
  "prompt": "What are the safety protocols for high-rise construction?",
  "role": "Safety Officer",
  "context": {
    "company_name": "Elite Builders"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "response": "...",
  "steps": [...]
}
```

### Clear History
```
POST /clear-history
```
Clears the conversation history.

### Get Roles
```
GET /roles
```
Returns a list of available construction company roles.

## Using with React

Example fetch request from React:

```javascript
const sendMessage = async (prompt, role) => {
  try {
    const response = await fetch('http://localhost:5000/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt,
        role,
        context: {
          company_name: 'Elite Builders'
        }
      }),
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error sending message:', error);
    return { status: 'error', message: error.message };
  }
};
``` 