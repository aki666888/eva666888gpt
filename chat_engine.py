import google.generativeai as genai
from ufo_messenger import UFOMessenger
import base64
import json
from config import LLM, SYSTEM_PROMPT
import pyautogui
from PIL import Image
import io
import os

class ChatEngine:
    def __init__(self, prompt_logger=None):
        self.messenger = UFOMessenger()
        self.prompt_logger = prompt_logger
        self.screenshot_history = []  # Keep track of multiple screenshots
        self.clear_all_screenshots() # Clear any old screenshots on startup
        
        # Configure Gemini
        genai.configure(api_key=LLM['api_key'])
        self.model = genai.GenerativeModel(
            model_name=LLM['model'],  # Use model from config.py as single source of truth
            generation_config={
                'temperature': LLM['temperature'],
                'max_output_tokens': LLM['max_tokens'],
            }
        )

    def log(self, prompt_type, content, metadata=None):
        if self.prompt_logger:
            self.prompt_logger(prompt_type, content, metadata)

    def take_screenshot(self):
        """Take a screenshot and return as PIL Image"""
        # Keep only the last 2 screenshots to avoid accumulation
        # Delete the second-to-last screenshot if we have 2 or more
        if len(self.screenshot_history) >= 2:
            second_to_last = self.screenshot_history[-2]
            if os.path.exists(second_to_last):
                try:
                    os.remove(second_to_last)
                    self.log('SCREENSHOT_CLEANUP', f'Removed old screenshot: {second_to_last}')
                except Exception as e:
                    self.log('SCREENSHOT_CLEANUP_ERROR', f'Failed to remove {second_to_last}: {e}')
            
        try:
            screenshot = pyautogui.screenshot()
            # Use timestamp to make filenames unique
            import time
            temp_path = f"temp_screenshot_{int(time.time())}.png"
            screenshot.save(temp_path)
            self.screenshot_history.append(temp_path)
            # Keep only last 2 screenshots in history
            if len(self.screenshot_history) > 2:
                self.screenshot_history = self.screenshot_history[-2:]
            return screenshot
        except Exception as e:
            self.log('SCREENSHOT_ERROR', str(e))
            return None

    def clear_screenshot(self):
        """Clear only the oldest screenshot, keeping the most recent for experience saver"""
        if len(self.screenshot_history) > 1:
            # Remove oldest screenshot, keep the most recent
            oldest = self.screenshot_history[0]
            if os.path.exists(oldest):
                try:
                    os.remove(oldest)
                    self.screenshot_history.remove(oldest)
                    self.log('SCREENSHOT_CLEANUP', f'Cleared oldest screenshot: {oldest}')
                except Exception as e:
                    self.log('SCREENSHOT_CLEANUP_ERROR', f'Failed to clear {oldest}: {e}')
    
    def clear_all_screenshots(self):
        """Clear all screenshots (used on startup)"""
        for screenshot_path in self.screenshot_history:
            if os.path.exists(screenshot_path):
                try:
                    os.remove(screenshot_path)
                except:
                    pass
        self.screenshot_history = []
        # Also clean up any orphaned temp screenshots
        import glob
        for temp_file in glob.glob("temp_screenshot*.png"):
            try:
                os.remove(temp_file)
            except:
                pass

    def _extract_command_from_response(self, data):
        if isinstance(data, str):
            return data
        if isinstance(data, list) and data:
            return self._extract_command_from_response(data[0])
        if isinstance(data, dict):
            return self._extract_command_from_response(data.get('command', ''))
        return ""

    def process_streaming(self, message, project, chat_history):
        # --- Direct Project Reload (Debugging Step) ---
        project_name_from_frontend = project.get('name') if project else None
        reloaded_project = None
        if project_name_from_frontend:
            with open('projects.json', 'r') as f:
                all_projects = json.load(f)
            for p in all_projects:
                if p.get('name') == project_name_from_frontend:
                    reloaded_project = p
                    break
        current_project_data = reloaded_project or project
        # --- End of Direct Project Reload ---

        if not current_project_data or not current_project_data.get('steps'):
            yield {'type': 'error', 'content': 'No project or steps found.'}
            return

        steps = current_project_data.get('steps', [])

        for i, step in enumerate(steps):
            command = step.get('instructions')
            if not command:
                continue

            yield {'type': 'assistant_response', 'content': {'thinking': f'Executing step {i+1}', 'working_on_step': f'Step {i+1}', 'instructions_to_eva2': command}}

            if self.messenger.available:
                self.log('UFO2_COMMAND', command)
                yield {'type': 'debug_output', 'content': f"Sending to EVA2: {command}"}
                
                full_output = ""
                line_buffer = ""
                for char in self.messenger.send_command(command):
                    yield {'type': 'ufo_output', 'content': char}
                    full_output += char
                    line_buffer += char
                    # Check for newline to process line-based status checks
                    if char == '\n':
                        line_buffer = ""

                if "EVALUATION_AGENT" in full_output:
                    if "succeeded" in full_output.lower():
                        yield {'type': 'eva2_conclusion', 'content': f"Step {i+1} evaluated as successful."}
                    else:
                        yield {'type': 'error', 'content': f"Step {i+1} evaluated as failed."}
                        break
                elif "UFO2 Error" in full_output:
                    self.log('UFO2_ERROR', full_output)
                else:
                    observations = ""
                    status = ""
                    if "Observations👀:" in full_output:
                        observations = full_output.split("Observations👀:")[-1].split("\n")[0].strip()
                    if "Status📊:" in full_output:
                        status = full_output.split("Status📊:")[-1].split("\n")[0].strip()
                    
                    context_message = f"EVA2 Observation: {observations}\nEVA2 Status: {status}"
                    yield {'type': 'eva2_context', 'content': context_message}
            else:
                self.log('UFO2_UNAVAILABLE', 'UFO2 is not available.')

    def analyze_document_streaming(self, message, file_data, system_prompt):
        self.log('OCR_PROMPT', system_prompt)
        self.log('OCR_MESSAGE', message)
        
        try:
            # Extract base64 image data
            image_data = file_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Use Gemini to analyze the document
            prompt = f"{system_prompt}\n\n{message}"
            response = self.model.generate_content([prompt, image])
            
            self.log('OCR_RESULT', response.text)
            yield {'type': 'message', 'content': response.text}
            
        except Exception as e:
            self.log('OCR_ERROR', str(e))
            yield {'type': 'error', 'content': f"Error processing document: {str(e)}"}
