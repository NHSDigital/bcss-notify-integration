import json
import os

import boto3
import uuid

import logging

# Set up logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # You can change this to DEBUG, ERROR, etc.

# Set up log format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create a stream handler to output logs to CloudWatch
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(console_handler)

from BCSSNotifyBatchProcessor import BCSSNotifyBatchProcessor
from BCSSNotifyRequestHandler import BCSSNotifyRequestHandler

HOST = os.getenv("host")
PORT = os.getenv("port")
SID = os.getenv("sid")
TABLESPACE_NAME = os.getenv("tablespace")
SNS_ARN = os.getenv("sns_arn")
SECRET_NAME = os.getenv("secret_arn")
REGION_NAME = os.getenv("region_name")
NHS_NOTIFY_BASE_URL = os.getenv("nhs_notify_base_url")
ROUTING_CONFIG_ID = os.getenv("routing_config_id")
TOKEN_URL = os.getenv("token_url")

# Initialize AWS clients
secrets_client = boto3.client(service_name="secretsmanager", region_name=REGION_NAME)


def get_secret(secret_name):
    """Retrieve a secret value from AWS Secrets Manager."""
    response = secrets_client.get_secret_value(SecretId=secret_name)
    secret = json.loads(response["SecretString"])
    return secret


def lambda_handler(event, context):
    logger.info("Lambda function has started.")

    db_secret = get_secret(SECRET_NAME)
    notify_secrets = get_secret("bcss-notify-nonprod-pem-key")

    db_user = db_secret["username"]
    db_password = db_secret["password"]

    PRIVATE_KEY = notify_secrets["private-key"]

    db_config = {
        "user": db_user,
        "password": db_password,
        "dsn": f"{HOST}:{PORT}/{SID}",
    }

    bcss_notify_batch_processor = BCSSNotifyBatchProcessor(db_config)
    bcss_notify_request_handler = BCSSNotifyRequestHandler(
        TOKEN_URL, PRIVATE_KEY, NHS_NOTIFY_BASE_URL, db_config
    )

    BATCH_ID = str(uuid.uuid4())
    logger.debug(f"DEBUG: BATCH_ID - {BATCH_ID}")

    logger.info(f"Getting participants...")
    participants, ROUTING_CONFIG_ID = bcss_notify_batch_processor.get_participants(
        BATCH_ID
    )
    logger.info(f"Got participants.")

    logger.debug(f"DEBUG: PARTICIPANTS - \n {participants}\n ROUTING_CONFIG_ID - {ROUTING_CONFIG_ID}")

    logger.info(f"Sending batch message...")
    bcss_notify_message_response = bcss_notify_request_handler.send_message(
        BATCH_ID, ROUTING_CONFIG_ID, participants
    )
    logger.info(f"Bacth message sent.")

    logger.debug(f"DEBUG: BCSS_NOTIFY_MESSAGE_RESPONSE - \n {bcss_notify_message_response}")
    logger.info("Lambda function has completed.")


"""
    # BCSSNotifyBatchProcessor

    # Generate Batch ID

    # Call PKG_NOTIFY_WRAP.f_get_next_batch with Batch ID, should Return Routing Config

    # Check presence of Routing Config

    # If not present, no records to process

    # If present, Call SELECT * FROM v_notify_message_queue WHERE batch_id = your batch UUID

    # Return list of participants

    # BCSSNotifyRequestHandler

    # Using participants list param, check length of participants list

    # If 0 stop,

    # If > 0, send message

    # 
"""
