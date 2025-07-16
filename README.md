# TabletGPT - AI-Powered Pharmacy Automation System

## Quick Start

### Running with Admin Privileges
Double-click `run_tabletgpt.bat` - it will automatically request admin privileges via Windows UAC and start the server.

### Manual Start
```bash
python main.py
```

Server will be available at: `http://localhost:5000`

## Core Features

- **AI-Powered Workflow Automation**: Guide UFO2 step-by-step through pharmacy tasks
- **Real-time Streaming Interface**: Super responsive UI with immediate feedback
- **Complete Chat History**: Full conversation context sent to LLM (no truncation)
- **Smart Error Recovery**: Automatic retry logic with enhanced guidance
- **End Workflow Management**: Clean project completion with auto-clear

## Architecture

```
User → Flask + Chat LLM → Simple Messenger → UFO2
```

### Data Flow
1. **Input**: System Prompt + Current Screenshot + Complete Chat History
2. **Output**: Thinking → Step Number → Instructions → System Message → UFO2 Result
3. **Feedback Loop**: UFO2 responses appended to chat history for next iteration

## Project Structure

```
tabletgpt/
├── run_tabletgpt.bat          # Admin launcher
├── main.py                    # Flask server with async streaming
├── chat_engine.py             # Core AI orchestration
├── ufo_messenger.py           # UFO2 integration
├── workflow_manager.py        # Project management
├── config.py                  # Configuration
├── static/                    # Frontend assets
├── templates/                 # HTML templates
└── #*                        # Documentation (preserved)
```

## Key Components

### Chat Engine (`chat_engine.py`)
- **System Prompt**: Exact user specification with Tablet GPT branding
- **Intent Analysis**: Handles regular steps, error recovery (#), thinker analyze (nA), and End
- **Streaming**: Real-time response generation with complete context preservation
- **No Truncation**: Entire chat history and UFO outputs preserved

### UFO Messenger (`ufo_messenger.py`)
- **# Scenario**: No images, instructions as-is
- **nA Scenario**: Pass images + stream descriptions
- **Reference Images**: Automatic enhancement with step context

### Frontend (`static/js/app.js`)
- **Real-time Streaming**: Server-Sent Events for immediate updates
- **Auto-clear**: Chat window refresh on End/completion
- **Responsive UI**: Optimized for pharmacy workflow efficiency

## Workflow Types

1. **Regular Steps (1-n)**: Sequential project execution
2. **Error Recovery (#)**: Custom error handling with direct commands
3. **Thinker Analyze (nA)**: Dynamic analysis with screenshot interpretation
4. **End**: Project completion with automatic chat clear

## Performance Optimizations

- **Threading**: Concurrent request handling
- **Streaming**: Immediate response chunks
- **No Buffering**: Direct client updates
- **CORS Headers**: Cross-origin responsiveness
- **Admin Privileges**: Full system access for automation

## Security & Ethics

- **Admin UAC**: Proper Windows privilege escalation
- **Clean Codebase**: All test scripts removed
- **Defensive Focus**: Pharmacy automation and workflow optimization
- **No Malicious Code**: Pure automation assistance

Built for reliable, responsive pharmacy workflow automation with complete audit trails and intelligent error recovery.