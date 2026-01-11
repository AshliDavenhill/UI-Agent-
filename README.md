# Constrained Research Agent Web Application

A web-based research assistant agent with constrained responses, step-by-step progress tracking, and user correction capabilities.

## Features

- **120 Character Response Limit**: All agent responses are constrained to a maximum of 120 characters
- **Predefined UI Components**: Responses rendered via buttons, forms, and status indicators
- **Partial Task Completion**: Visual progress indicators showing step-by-step task completion
- **User Corrections**: Ability to correct agent behavior without restarting the task
- **Confidence Indicators**: Visual representation of agent confidence/uncertainty levels

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your environment variables:
Create a `.env` file in the root directory with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

1. Enter your research query in the input field
2. The agent will respond with constrained messages (max 120 chars)
3. Use the provided buttons or forms to interact with the agent
4. Monitor progress through the step indicators
5. Check confidence levels via the confidence bars
6. Use the correction feature to adjust agent behavior mid-task

## Troubleshooting

### "Failed to fetch" Error

If you see "Failed to fetch" errors:

1. **Check if the Flask server is running:**
   ```bash
   python app.py
   ```
   You should see: "Starting Flask server on http://localhost:5000"

2. **Verify the server is accessible:**
   Open `http://localhost:5000/api/health` in your browser. You should see:
   ```json
   {"status": "ok", "message": "Server is running", "active_tasks": 0}
   ```

3. **Check your .env file:**
   Make sure you have `OPENAI_API_KEY=your_key_here` in a `.env` file

4. **Check the browser console:**
   Open Developer Tools (F12) and check the Console tab for detailed error messages

5. **Verify port 5000 is not in use:**
   If port 5000 is occupied, change the port in `app.py`:
   ```python
   app.run(debug=True, port=5001)  # Change to different port
   ```
   Then update the frontend fetch URLs accordingly

## Architecture

- **Backend**: Flask REST API (`app.py`)
- **Frontend**: Modern HTML/CSS/JavaScript (`templates/index.html`)
- **Agent**: LangChain-based research assistant with tool calling capabilities
- **Tools**: Web search, Wikipedia, and file saving

## Response Types

The agent can respond with different action types:
- **button**: Shows clickable options
- **form**: Requests text input
- **status**: Displays progress information
- **confirm**: Asks for yes/no confirmation
