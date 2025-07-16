# TabletGPT - Single Source of Truth Configuration

# Core LLM Configuration - Google Gemini 2.5 Flash Lite
LLM = {
    "api_key": "AIzaSyBC4m0pBy8t6D1Q0OAdzPGJ0m8ZAdXr7o0",
    "base_url": "https://generativelanguage.googleapis.com/v1beta/models",
    "model": "models/gemini-2.5-flash-lite-preview-06-17",  # Official model name from Google docs
    "temperature": 0.1,
    "max_tokens": 66000,  # Max output tokens for Gemini 2.5 Flash Lite
    "max_input_tokens": 1000000,  # 1M max input context
    "timeout": 30,
    "thinking_budget": 2048  # Thinking tokens for enhanced reasoning (allocated from output)
}

# System Paths (Windows Only)
PATHS = {
    "ufo2": "D:/UFO",
    "projects": "projects.json",
    "images": "workflow_images",
    "temp": "temp"
}

# Flask Configuration
FLASK = {
    "host": "127.0.0.1",
    "port": 5000,
    "debug": False
}

# System Prompt for Eva2 Orchestration
SYSTEM_PROMPT = """You are Eva's Eva2 orchestrator. Transform user requests into clear Eva2 commands.

PROJECT CONTEXT:
{project_context}

CURRENT SCREENSHOT: [Provided for analysis]

Your job: Generate ONE clear Eva2 command based on the user's request and current screen.

Response format:
{
  "intent": "execute_step|direct_command|status",
  "command": "clear Eva2 instruction",
  "reasoning": "why this command"
}

Keep commands simple and precise for Windows automation."""
