import os
import sys

# The bcss-notify-integration repo contains several modules called lambda_function.py
# This is a pattern enforced by AWS Lambda, but it makes it difficult to import the 
# correct module in tests as import order is not guaranteed.
# To work around this, we remove any existing modules from the sys.modules cache
# named "lambda_function" before importing the module we want to test.
if "lambda_function" in sys.modules:
    del sys.modules["lambda_function"]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(SCRIPT_DIR) + "/../batch_notification_processor")
