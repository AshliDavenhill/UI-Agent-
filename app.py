from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_agent
from tools import search_tool, wiki_tool, save_tool
import uuid
import json

load_dotenv()

app = Flask(__name__)
CORS(app)

# Store active tasks
active_tasks = {}

class ConstrainedResponse(BaseModel):
    action: str  # "button", "form", "status", "confirm"
    message: str  # Max 120 chars
    confidence: float  # 0.0 to 1.0
    options: list[str] = []  # For buttons/forms
    task_id: str
    step: int
    total_steps: int = 1
    can_correct: bool = False

class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a research assistant with STRICT constraints:
1. EVERY response MUST be 120 characters or less
2. Use simple, clear, concise language
3. Break tasks into clear steps
4. Ask for user input when needed
5. Show progress clearly

When responding:
- Keep messages SHORT and DIRECT
- Use "button" action to offer choices
- Use "form" action to request input
- Use "status" action to show progress
- Always be concise - every character counts!

Example good response (under 120 chars): "Searching web for your topic. Choose: Web, Wikipedia, or Both?"
""",
    ),
    ("human", "{input}"),
])

tools = [search_tool, wiki_tool, save_tool]

# Create agent using the available API for langchain 1.2.3
system_prompt = """You are a research assistant with STRICT constraints:
1. EVERY response MUST be 120 characters or less
2. Use simple, clear, concise language
3. Break tasks into clear steps
4. Ask for user input when needed
5. Show progress clearly

When responding:
- Keep messages SHORT and DIRECT
- Use "button" action to offer choices
- Use "form" action to request input
- Use "status" action to show progress
- Always be concise - every character counts!

Example good response (under 120 chars): "Searching web for your topic. Choose: Web, Wikipedia, or Both?"
"""

rom langchain.agents import create_openai_tools_agent, AgentExecutor

def truncate_message(msg: str, max_len: int = 120) -> str:
    """Ensure message is within character limit"""
    if len(msg) <= max_len:
        return msg
    return msg[:max_len-3] + "..."

def create_constrained_response(
    message: str,
    action: str = "status",
    confidence: float = 0.8,
    options: list = None,
    task_id: str = None,
    step: int = 1,
    total_steps: int = 1,
    can_correct: bool = False
) -> dict:
    """Create a constrained response object"""
    return {
        "action": action,
        "message": truncate_message(message, 120),
        "confidence": min(max(confidence, 0.0), 1.0),
        "options": options or [],
        "task_id": task_id,
        "step": step,
        "total_steps": total_steps,
        "can_correct": can_correct
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify server is running"""
    return jsonify({
        "status": "ok",
        "message": "Server is running",
        "active_tasks": len(active_tasks)
    })

@app.route('/api/query', methods=['POST'])
def handle_query():
    try:
        data = request.json
        if not data:
            return jsonify({
                "action": "status",
                "message": "Invalid request: No JSON data provided",
                "confidence": 0.0,
                "options": [],
                "task_id": "",
                "step": 0,
                "total_steps": 1,
                "can_correct": False
            }), 400
        
        query = data.get('query', '')
        task_id = data.get('task_id')
        correction = data.get('correction')
    except Exception as e:
        return jsonify({
            "action": "status",
            "message": f"Request error: {str(e)}",
            "confidence": 0.0,
            "options": [],
            "task_id": "",
            "step": 0,
            "total_steps": 1,
            "can_correct": False
        }), 400
    
    if not task_id:
        task_id = str(uuid.uuid4())
        active_tasks[task_id] = {
            "query": query,
            "steps": [],
            "current_step": 0,
            "status": "in_progress",
            "corrections": []
        }
    
    task = active_tasks.get(task_id, {})
    
    # Initialize task if new
    if not task:
        task = {
            "query": query,
            "steps": [],
            "current_step": 0,
            "status": "in_progress",
            "corrections": [],
            "chat_history": []
        }
        active_tasks[task_id] = task
    
    # Handle corrections
    if correction:
        task["corrections"].append(correction)
        query = f"Correction requested: {correction}. Please adjust your approach for: {task.get('query', query)}"
    
    try:
        # Execute agent with the new API
        config = {"configurable": {"thread_id": task_id}}
        response = agent_runnable.invoke({"input": query}, config)
              # Execute agent
response = agent_executor.invoke({"input": query})

# Extract LLM output correctly
output_text = response.get("output", "")

        
        
        # Update chat history
        task["chat_history"].append(("human", query))
        task["chat_history"].append(("assistant", output_text))
        
        # Truncate to 120 characters immediately
        output_text = truncate_message(output_text, 120)
        
        # Estimate confidence based on response quality and tool usage
        confidence = 0.7
        if len(output_text) > 30 and "error" not in output_text.lower():
            confidence = 0.85
        if "error" in output_text.lower() or "unable" in output_text.lower() or "sorry" in output_text.lower():
            confidence = 0.4
        if len(output_text) < 20:
            confidence = 0.5
        
        # Determine action type based on response content
        action = "status"
        options = []
        
        # Check for questions or choices
        if "?" in output_text or "choose" in output_text.lower() or "select" in output_text.lower():
            action = "button"
            # Extract potential options based on context
            if "search" in output_text.lower():
                options = ["Web Search", "Wikipedia", "Both"]
            elif "save" in output_text.lower() or "store" in output_text.lower():
                options = ["Yes, Save", "No, Skip"]
            elif "continue" in output_text.lower():
                options = ["Continue", "Stop"]
            else:
                # Generic yes/no if question detected
                options = ["Yes", "No"]
        
        # Check for input requests
        elif "enter" in output_text.lower() or "provide" in output_text.lower() or "input" in output_text.lower():
            action = "form"
        
        # Check for confirmation requests
        elif "confirm" in output_text.lower() or "proceed" in output_text.lower():
            action = "button"
            options = ["Confirm", "Cancel"]
        
        # Update task state
        task["current_step"] += 1
        task["steps"].append({
            "step": task["current_step"],
            "response": output_text,
            "confidence": confidence
        })
        
        if task["current_step"] >= 3:  # Assume 3 steps for research task
            task["status"] = "completed"
        
        # Create constrained response
        constrained = create_constrained_response(
            message=truncate_message(output_text, 120),
            action=action,
            confidence=confidence,
            options=options,
            task_id=task_id,
            step=task["current_step"],
            total_steps=3,
            can_correct=True
        )
        
        active_tasks[task_id] = task
        
        return jsonify(constrained)
        
    except Exception as e:
        return jsonify({
            "action": "status",
            "message": truncate_message(f"Error: {str(e)}", 120),
            "confidence": 0.3,
            "options": [],
            "task_id": task_id,
            "step": task.get("current_step", 0),
            "total_steps": 1,
            "can_correct": True
        }), 500

@app.route('/api/task/<task_id>', methods=['GET'])
def get_task(task_id):
    task = active_tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task)

@app.route('/api/correct', methods=['POST'])
def handle_correction():
    """Handle user corrections by forwarding to query endpoint"""
    try:
        data = request.json
        if not data:
            return jsonify({
                "action": "status",
                "message": "Invalid request: No JSON data provided",
                "confidence": 0.0,
                "options": [],
                "task_id": "",
                "step": 0,
                "total_steps": 1,
                "can_correct": False
            }), 400
        
        task_id = data.get('task_id')
        correction = data.get('correction')
        
        if not task_id or not correction:
            return jsonify({
                "action": "status",
                "message": "Missing task_id or correction",
                "confidence": 0.0,
                "options": [],
                "task_id": task_id or "",
                "step": 0,
                "total_steps": 1,
                "can_correct": False
            }), 400
    except Exception as e:
        return jsonify({
            "action": "status",
            "message": f"Request error: {str(e)}",
            "confidence": 0.0,
            "options": [],
            "task_id": "",
            "step": 0,
            "total_steps": 1,
            "can_correct": False
        }), 400
    
    # Process correction as a query with correction flag
    # We'll manually process it since we can't easily modify request.json
    task = active_tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    task["corrections"].append(correction)
    query = f"Correction requested: {correction}. Please adjust your approach for: {task.get('query', '')}"
    
    try:
        # Execute agent with the new API
        config = {"configurable": {"thread_id": task_id}}
        response = agent_runnable.invoke({"input": query}, config)
                # Execute agent
response = agent_executor.invoke({"input": query})

# Extract LLM output correctly
output_text = response.get("output", "")
        
    
        output_text = truncate_message(output_text, 120)
        
        task["chat_history"].append(("human", query))
        task["chat_history"].append(("assistant", output_text))
        
        confidence = 0.7
        if len(output_text) > 30 and "error" not in output_text.lower():
            confidence = 0.85
        if "error" in output_text.lower() or "unable" in output_text.lower():
            confidence = 0.4
        
        action = "status"
        options = []
        
        if "?" in output_text or "choose" in output_text.lower():
            action = "button"
            if "search" in output_text.lower():
                options = ["Web Search", "Wikipedia", "Both"]
            else:
                options = ["Yes", "No"]
        elif "enter" in output_text.lower() or "provide" in output_text.lower():
            action = "form"
        
        constrained = create_constrained_response(
            message=output_text,
            action=action,
            confidence=confidence,
            options=options,
            task_id=task_id,
            step=task["current_step"],
            total_steps=3,
            can_correct=True
        )
        
        return jsonify(constrained)
        
    except Exception as e:
        return jsonify({
            "action": "status",
            "message": truncate_message(f"Error: {str(e)}", 120),
            "confidence": 0.3,
            "options": [],
            "task_id": task_id,
            "step": task.get("current_step", 0),
            "total_steps": 1,
            "can_correct": True
        }), 500

if __name__ == '__main__':
    print("Starting Flask server on http://localhost:5000")
    print("Make sure you have set OPENAI_API_KEY in your .env file")
    app.run(debug=True, port=5000, host='0.0.0.0')
