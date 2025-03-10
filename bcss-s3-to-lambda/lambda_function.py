"""Lambda function to process and send batch notifications via NHS Notify service."""

import json
import logging
import os
import uuid
import boto3

from bcss_notify_batch_processor import (
    BCSSNotifyBatchProcessor,
)  # pylint: disable=import-error
from bcss_notify_request_handler import (
    BCSSNotifyRequestHandler,
)  # pylint: disable=import-error

# Set up logger
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

# Set up log format
FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Create a stream handler to output logs to CloudWatch
CONSOLE_HANDLER = logging.StreamHandler()
CONSOLE_HANDLER.setFormatter(FORMATTER)
LOGGER.addHandler(CONSOLE_HANDLER)

# Environment variables
HOST = os.getenv("host")  # Oracle database host
PORT = os.getenv("port")  # Oracle database port
SID = os.getenv("sid")  # Oracle database SID
TABLESPACE_NAME = os.getenv("tablespace")  # Oracle tablespace name
SNS_ARN = os.getenv("sns_arn")  # AWS SNS topic ARN
SECRET_NAME = os.getenv("secret_arn")  # AWS Secrets Manager secret name
REGION_NAME = os.getenv("region_name")  # AWS region
NHS_NOTIFY_BASE_URL = os.getenv("nhs_notify_base_url")  # NHS Notify API base URL
TOKEN_URL = os.getenv("token_url")  # OAuth token URL

# Initialize AWS clients
SECRETS_CLIENT = boto3.client(service_name="secretsmanager", region_name=REGION_NAME)


def get_secret(secret_name: str) -> dict:
    """
    Retrieve a secret value from AWS Secrets Manager.

    Args:
        secret_name: Name of the secret to retrieve

    Returns:
        dict: Parsed secret value
    """
    response = SECRETS_CLIENT.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])


def lambda_handler(_event: dict, _context: object) -> None:
    """
    AWS Lambda handler to process and send batch notifications.

    Args:
        event: AWS Lambda event
        context: AWS Lambda context
    """
    LOGGER.info("Lambda function has started.")

    # Fetch required secrets
    db_secret = get_secret(SECRET_NAME)
    notify_secrets = get_secret("bcss-notify-nonprod-pem-key")

    # Configure database connection
    db_config = {
        "user": db_secret["username"],
        "password": db_secret["password"],
        "dsn": f"{HOST}:{PORT}/{SID}",
    }

    # Initialize processors
    batch_processor = BCSSNotifyBatchProcessor(db_config)
    request_handler = BCSSNotifyRequestHandler(
        TOKEN_URL, notify_secrets["private-key"], NHS_NOTIFY_BASE_URL, db_config
    )

    # Generate unique batch ID
    batch_id = str(uuid.uuid4())
    LOGGER.debug("Generated batch ID: %s", batch_id)

    # Process participants
    LOGGER.info("Getting participants...")
    participants, routing_config_id = batch_processor.get_participants(batch_id)
    LOGGER.info("Retrieved participants successfully.")

    LOGGER.debug(
        "Participants data: \n%s\nRouting config ID: %s",
        participants,
        routing_config_id,
    )

    # Send batch message
    LOGGER.info("Sending batch message...")
    message_response = request_handler.send_message(
        batch_id, routing_config_id, participants
    )
    LOGGER.info("Batch message sent successfully.")

    LOGGER.debug("Message response: \n%s", message_response)
    LOGGER.info("Lambda function has completed.")


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
