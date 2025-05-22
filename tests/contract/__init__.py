import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(SCRIPT_DIR) + "/../batch_notification_processor")
sys.path.insert(0, os.path.dirname(SCRIPT_DIR) + "/../message_status_handler")
sys.path.insert(0, os.path.dirname(SCRIPT_DIR) + "/../shared")
