import os
import sys

if "lambda_function" in sys.modules:
    del sys.modules["lambda_function"]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(SCRIPT_DIR) + "/batch_notification_processor")
sys.path.insert(0, os.path.dirname(SCRIPT_DIR) + "/message_status_handler")
sys.path.insert(0, os.path.dirname(SCRIPT_DIR) + "/oracle")
