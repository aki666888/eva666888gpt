import os

last_screenshot_path = "temp_screenshot.png"
if os.path.exists(last_screenshot_path):
    os.remove(last_screenshot_path)