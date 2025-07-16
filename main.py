# Eva - Lean Async Flask Implementation
import json
import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify, Response
from chat_engine import ChatEngine
from workflow_manager import WorkflowManager

app = Flask(__name__)
workflow_mgr = WorkflowManager()

# Global prompt logging storage
prompt_logs = []
MAX_PROMPT_LOGS = 1000

PROMPTS_FILE = 'prompts.json'

def get_prompts():
    if not os.path.exists(PROMPTS_FILE):
        return {
            "system_prompt": "",
            "ocr_prompt": "Analyze this image using your vision and OCR and parse the contents and provide them in a neat and structured fashion as per sections."
        }
    with open(PROMPTS_FILE, 'r') as f:
        return json.load(f)

def save_prompts(prompts):
    with open(PROMPTS_FILE, 'w') as f:
        json.dump(prompts, f, indent=4)

def log_prompt(prompt_type, content, metadata=None):
    """Log prompts with timestamp and type"""
    global prompt_logs
    
    log_entry = {
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'type': prompt_type,
        'content': content[:66000] if len(content) > 66000 else content,  # Truncate very long content
        'metadata': metadata or {}
    }
    
    prompt_logs.append(log_entry)
    
    if len(prompt_logs) > MAX_PROMPT_LOGS:
        prompt_logs = prompt_logs[-MAX_PROMPT_LOGS:]

# Pass the logger to the chat engine
chat_engine = ChatEngine(prompt_logger=log_prompt)

@app.route('/')
def index():
    return render_template('index.html', projects=workflow_mgr.get_projects())

@app.route('/api/projects', methods=['GET'])
def get_projects():
    return jsonify(workflow_mgr.get_projects())

@app.route('/api/projects', methods=['POST'])
def save_project():
    data = request.json
    if not data or not data.get('name'):
        return jsonify({'error': 'Invalid data'}), 400

    existing_projects = workflow_mgr.get_projects()
    is_new = not any(p['name'] == data['name'] for p in existing_projects)

    if is_new and data.get('use_custom_prompt') is False:
        prompts = get_prompts()
        data['system_prompt'] = prompts.get('system_prompt', '')
    
    # If a custom prompt is present, ensure the flag is set to true.
    if data.get('system_prompt'):
        data['use_custom_prompt'] = True
        
    success = workflow_mgr.save_project(data)
    return jsonify({'success': success})

@app.route('/api/chat_stream', methods=['POST'])
def chat_stream():
    data = request.json
    if not data:
        return jsonify({'error': 'Invalid data'}), 400
    message = data.get('message', '')
    project = data.get('project')
    chat_history = data.get('chat_history', [])

    if not message:
        return jsonify({'error': 'No message'}), 400

    global prompt_logs
    prompt_logs = []
    log_prompt('SYSTEM', 'New request received, logs cleared.')

    def generate():
        try:
            log_prompt('USER_MESSAGE', message, {'project': project.get('name') if project else 'None'})
            for response_chunk in chat_engine.process_streaming(message, project, chat_history):
                yield f"data: {json.dumps(response_chunk)}\n\n"
        except Exception as e:
            log_prompt('ERROR', str(e))
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return Response(
        generate(), 
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'X-Accel-Buffering': 'no',  # Disable Nginx buffering
            'Connection': 'keep-alive'
        }
    )

@app.route('/api/analyze_document', methods=['POST'])
def analyze_document():
    try:
        data = request.json
        message = data.get('message', '')
        file_data = data.get('file')
        system_prompt = data.get('systemPrompt', '')
        
        if not file_data:
            return jsonify({'error': 'No file data provided'}), 400
        
        def generate():
            try:
                for update in chat_engine.analyze_document_streaming(message, file_data, system_prompt):
                    response_data = f"data: {json.dumps(update)}\n\n"
                    yield response_data
                
                yield f"data: [DONE]\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
        
        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/prompt_logs', methods=['GET'])
def get_prompt_logs():
    return jsonify({'logs': prompt_logs})

@app.route('/api/prompts', methods=['GET'])
def api_get_prompts():
    return jsonify(get_prompts())

@app.route('/api/prompts', methods=['POST'])
def api_save_prompts():
    prompts = request.json
    if not prompts:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    save_prompts(prompts)

    general_system_prompt = prompts.get('system_prompt', '')
    projects = workflow_mgr.get_projects()
    for p in projects:
        if not p.get('use_custom_prompt'):
            p['system_prompt'] = general_system_prompt
            workflow_mgr.save_project(p)

    return jsonify({'success': True})

@app.route('/api/clear_screenshot', methods=['POST'])
def clear_screenshot():
    chat_engine.clear_screenshot()
    return jsonify({'success': True})

if __name__ == '__main__':
    # Disabled reloader to prevent infinite restart loop caused by watchdog
    # monitoring site-packages. Set use_reloader=False.
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
