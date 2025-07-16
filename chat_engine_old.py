from ufo_messenger import UFOMessenger
import base64

class ChatEngine:
    def __init__(self, prompt_logger=None):
        self.messenger = UFOMessenger()
        self.prompt_logger = prompt_logger

    def log(self, prompt_type, content, metadata=None):
        if self.prompt_logger:
            self.prompt_logger(prompt_type, content, metadata)

    def process_streaming(self, message, project, chat_history):
        project_name = "None"
        system_prompt = ""
        if project:
            project_name = project.get('name', 'Unnamed Project')
            system_prompt = project.get('system_prompt', '')

        self.log('LLM_PROMPT', f'{system_prompt}\n\nProcessing message: {message}')
        yield {'type': 'message', 'content': f"Received: {message}"}

        self.log('LLM_RESPONSE', f"Simulating response for project: {project_name}")
        yield {'type': 'message', 'content': f"Project: {project_name}"}

        if self.messenger.available:
            self.log('UFO2_COMMAND', f'Sending command to UFO2: {message}')
            success, output, error = self.messenger.send_command(message)
            if success:
                self.log('UFO2_OUTPUT', output)
                yield {'type': 'ufo_output', 'content': output}
            else:
                self.log('UFO2_ERROR', error)
                yield {'type': 'debug_output', 'content': f"UFO2 Error: {output}"}
        else:
            self.log('UFO2_UNAVAILABLE', 'UFO2 is not available.')
            yield {'type': 'debug_output', 'content': "UFO2 is not available."}

    def analyze_document_streaming(self, message, file_data, system_prompt):
        self.log('OCR_PROMPT', system_prompt)
        self.log('OCR_MESSAGE', message)
        
        # Simulate OCR processing
        yield {'type': 'message', 'content': "Eva OCR: Analyzing document..."}
        
        # Decode base64 file data (assuming it's a base64 string)
        try:
            # In a real scenario, you'd send this to a vision model
            # For now, we'll just simulate some parsed content
            decoded_content = base64.b64decode(file_data.split(',')[1]).decode('utf-8')
            parsed_content = f"Parsed content from document:\n\n{decoded_content[:200]}...\n\n(Full content truncated for demo)"
            
            self.log('OCR_RESULT', parsed_content)
            yield {'type': 'message', 'content': parsed_content}
            
        except Exception as e:
            self.log('OCR_ERROR', str(e))
            yield {'type': 'error', 'content': f"Error processing document: {str(e)}"}
