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
file:///Users/ashlidavenhill/Desktop/Final-Case-study%20/index.html
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
- 
## System Architecture Explanation
1. UI vs Agent vs Memory State Model
This system is intentionally split into three distinct layers:
UI Layer (Frontend – HTML/JS)
The UI strictly controls how the agent can respond.
The agent cannot free-text chat; responses are rendered only through:
Status messages (≤120 characters)
Buttons (predefined options)
Forms (explicit input requests)
The UI enforces constraints such as:
Character limits
Step-by-step progression
Structured user interaction
This prevents unbounded or irrelevant responses

## Agent  Layer (Backend – LangChain + OpenAI)
The agent is responsible for reasoning and research logic only.
It:
Decides what step comes next
Chooses the interaction type (status, button, form)
Produces concise, task-focused output
The agent does not control rendering or conversation flow.
It only returns structured intent, which the UI interprets.

## Memory / State Layer (Backend – Flask Task Store)
Each research task is tracked using a unique task_id.
Stored state includes:
Original query
Current step number
Previous agent responses
User corrections
This allows:
Step continuity
Corrections without restarting
Recovery from partial failures
The system behaves as a state machine, not a chat log.

## Failure Scenario and Recovery
Failure Scenario
A user submits a query, but the OpenAI API temporarily fails
(e.g. network issue, rate limit, or invalid response).
System Response
The backend catches the exception
A short error status is returned to the UI
The task state remains intact
The user can retry or apply a correction
Recovery
Because task state is stored server-side:
The user does not lose progress
The same task_id continues
The agent resumes from the correct step
This prevents full task resets and improves reliability.

## Why Plain Text Chat Would Break This System
If this were implemented as a normal chat interface:
❌ Loss of UI Control
The agent could exceed character limits
Buttons/forms would not be enforceable
Output would become unpredictable
❌ No Step Enforcement
The agent could skip steps or loop
Progress indicators would be meaningless
The user would not know what action is expected
❌ Memory Becomes Ambiguous
Corrections would rely on context guessing
Task recovery would be unreliable
Multi-step reasoning would degrade over time

## Why UI-Constrained Agents Are Required
This design ensures:
Deterministic behavior
Predictable user actions
Safe, explainable agent flow
The system operates as a guided research workflow, not a chatbot.

## Diagram 

┌───────────────────────────┐
│        User (Browser)     │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│        UI Layer           │
│  (HTML / CSS / JS)        │
│                           │
│ - Text input              │
│ - Buttons                 │
│ - Forms                   │
│ - Progress indicators     │
│ - Confidence display      │
│                           │
│ Enforces response format  │
│ and character limits      │
└─────────────┬─────────────┘
              │ JSON (query, task_id)
              ▼
┌───────────────────────────┐
│     Backend API Layer     │
│        (Flask)            │
│                           │
│ - /api/query              │
│ - /api/correct            │
│ - Task routing            │
│ - Error handling          │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│   Memory / State Layer    │
│   (Active Tasks Store)    │
│                           │
│ - task_id                 │
│ - current_step            │
│ - chat history            │
│ - corrections             │
│ - task status             │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│        Agent Layer        │
│  (LangChain + OpenAI)     │
│                           │
│ - Reasoning               │
│ - Tool selection          │
│ - Step decisions          │
│ - Short constrained output│
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│    External Tools / APIs  │
│                           │
│ - Web Search              │
│ - Wikipedia               │
│ - Save / Storage tool     │
└───────────────────────────┘


## Response Types

The agent can respond with different action types:
- **button**: Shows clickable options
- **form**: Requests text input
##
- ## main.py
- This was my base model to work off of when creating this agent,This provided a framework to work off of . Changes can be made and help towards this would be appericated .

## 🙋‍♀️ Self-Reflection
This project represents my early journey into building agent-based systems. I approached it as a beginner, focusing on understanding the fundamentals rather than trying to build a perfect or overly complex solution.
Throughout the development process, I encountered challenges related to system design, API integration, and state management. Each issue helped me better understand how UI constraints, backend logic, and agent reasoning must work together. While the system is not flawless, it reflects genuine learning and problem-solving rather than rote implementation.
I recognise that there are areas for improvement, particularly in robustness, optimisation, and deeper use of agent tooling. However, this project has given me a strong foundation and increased my confidence in working with modern AI frameworks.
I am committed to continuing to learn, experiment, and improve my skills. This project is not an endpoint, but a starting point in my development as an AI and software engineering practitioner.
- **status**: Displays progress information
- **confirm**: Asks for yes/no confirmation
