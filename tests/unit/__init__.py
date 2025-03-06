import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(SCRIPT_DIR) + "/../bcss_s3_to_lambda")
sys.path.insert(0, os.path.dirname(SCRIPT_DIR) + "/../bcss_notify_callback")
