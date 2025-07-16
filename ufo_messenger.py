# Eva Eva2 Messenger - Lean Windows Implementation
import subprocess
import os
import time
import threading
from config import PATHS

class UFOMessenger:
    def __init__(self):
        self.ufo_path = PATHS.get('ufo2')
        self.available = self.ufo_path and os.path.exists(self.ufo_path)

    def send_command(self, command):
        if not self.available:
            yield "UFO2 not available"
            return

        try:
            sanitized_command = command.replace('\n', ' ').replace('\r', ' ')
            env = os.environ.copy()
            env['PYTHONUTF8'] = '1'
            env['PYTHONIOENCODING'] = 'utf-8'

            cmd_list = [
                "python", "-m", "ufo",
                "--task", "eva_task",
                "-r", sanitized_command
            ]

            process = subprocess.Popen(
                cmd_list,
                cwd=self.ufo_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                env=env,
                bufsize=0  # Unbuffered for real-time output
            )

            # Set up timeout monitoring
            timeout = 300  # 5 minutes timeout
            start_time = time.time()

            # Read output line by line for real-time streaming
            for line in iter(process.stdout.readline, ''):
                # Check for timeout
                if time.time() - start_time > timeout:
                    process.terminate()
                    yield "\n\nUFO2 command timed out after 5 minutes.\n"
                    break

                if "snapshot capture failed" not in line.lower():
                    yield line
                
                # Reset timeout on new output
                start_time = time.time()
            
            process.stdout.close()
            return_code = process.wait() if process.poll() is None else process.returncode

            if return_code != 0:
                yield f"\n\nUFO2 Error (Code {return_code})\n"

        except subprocess.TimeoutExpired:
            process.kill()
            yield "\n\nUFO2 command timed out and was terminated.\n"
        except Exception as e:
            yield f"\n\nAn unexpected error occurred: {e}\n"
